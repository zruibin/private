 
<!--BEGIN_DATA
{
    "create_date": "2023-12-02 13:24", 
    "modify_date": "2023-12-02 13:24", 
    "is_top": "0", 
    "summary": "skynet引导服务bootstrap的启动<br/>如何在lua服务中启动另一个lua服务<br/>lua服务间是如何交互的", 
    "tags": "C/C++、Lua、架构、网络", 
    "file_name": "skynet源码阅读笔记02.md"
}
END_DATA-->

#### <p>原文出处：<a href='https://www.jianshu.com/p/1eb22d418087' target='blank'>skynet引导服务bootstrap的启动 </a></p>

## skynet 源码阅读笔记 —— 引导服务 bootstrap 的启动

### 引导服务 bootstrap 的启动

skynet 在启动的初期，在 `skynet_start` 函数中创建了两个服务 `logger` 和 `bootstrap`。其中 `bootstrap` 是一个 snlua 类型的服务，主要通过 `bootstrap` 函数来实现：

```c
//syknet_start.c
void skynet_start(struct skynet_config * config) {
    ...
    skynet_handle_namehandle(skynet_context_handle(ctx), "logger");
    //config->bootstrap = "snlua bootstrap"
    bootstrap(ctx, config->bootstrap);
    ...
}

static void bootstrap(struct skynet_context * logger, const char * cmdline) {
    int sz = strlen(cmdline);
    char name[sz+1];
    char args[sz+1];
    sscanf(cmdline, "%s %s", name, args);
    //name = snlua, args = "bootstrap"
    struct skynet_context *ctx = skynet_context_new(name, args);
    if (ctx == NULL) {
        skynet_error(NULL, "Bootstrap error : %s\n", cmdline);
        skynet_context_dispatchall(logger);
        exit(1);
    }
}
```

可以看到，在上述代码中 `bootstrap` 主要的工作便是调用 `skynet_context_new` 创建了一个名为 `snlua`的服务。我们来看下 `skynet_context_new` 的代码实现：

```c
struct skynet_context*  skynet_context_new(const char * name, const char *param) {
    //查询模块名称，查询到则直接返回模块指针，否则将其加载到全局的模块列表中
    struct skynet_module * mod = skynet_module_query(name);
    if (mod == NULL)
        return NULL;

    void *inst = skynet_module_instance_create(mod);
    if (inst == NULL)
        return NULL;

    struct skynet_context * ctx = skynet_malloc(sizeof(*ctx));

    ...     //为避免粘帖过多代码，此处省略部分 ctx 的赋值操作

    struct message_queue * queue = ctx->queue = skynet_mq_create(ctx->handle);

    // init function maybe use ctx->handle, so it must init at last
    context_inc();
    CHECKCALLING_BEGIN(ctx)
    int r = skynet_module_instance_init(mod, inst, ctx, param);
    CHECKCALLING_END(ctx)

    if (r == 0) {
        //ctx 的引用计数减 1，skynet_context_release 会在 ctx->ref == 0 时回收这个 context
        struct skynet_context * ret = skynet_context_release(ctx);
        if (ret) {
            ctx->init = true;
        }
        //将次级消息队列放入全局消息队列中
        skynet_globalmq_push(queue);
        if (ret) {
            skynet_error(ret, "LAUNCH %s %s", name, param ? param : "");
        }
        return ret;
    } else {
        ... //错误处理，包括释放已分配的ctx、次级消息队列等
        return NULL;
    }
}
```

### snlua 的加载及初始化

从前面 `skynet_context_new` 函数中，我们可以看出 `snlua` 服务的启动需要利用到 `skynet_module_instance_create`函数进行实例的创建，利用`skynet_module_instance_init`函数进行初始化，这两个函数最终会调用到对应模块中的 `*_create` 和 `*_init` 函数。对于 snlua 模块而言，其对应代码保存在 `service-src/service_snlua.c` 文件中，最终会编译成为 snlua.so 文件。由于在前面的文章 [skynet 源码阅读笔记 —— skynet的模块与服务](https://www.jianshu.com/p/de2d10867aa6)中已经说明了模块加载的详细方式，因此这里不多着笔墨说明。我们先来看看 snlua 的基本数据结构，然后直接看相关的模块函数

```c
//service-src/service_snlua.c
//内存阈值，当 snlua 占用的内存超过阈值则触发警报
#define MEMORY_WARNING_REPORT (1024 * 1024 * 32)

//snlua 的基本数据结构
struct snlua {
    lua_State * L;                  //每个 snlua 模块都配备了专属的 lua 环境
                                    //不同的 snlua 服务将不同的 lua 脚本运行在自己的 lua 环境中，彼此之间互不影响
    struct skynet_context * ctx;    //模块所属的服务
    size_t mem;
    size_t mem_report;              //内存阈值
    size_t mem_limit;
};

struct snlua* snlua_create(void) {
    struct snlua * l = skynet_malloc(sizeof(*l));
    memset(l,0,sizeof(*l));
    l->mem_report = MEMORY_WARNING_REPORT;
    l->mem_limit = 0;
    l->L = lua_newstate(lalloc, l);
    return l;
}

int snlua_init(struct snlua *l, struct skynet_context *ctx, const char * args) {
    int sz = strlen(args);
    char * tmp = skynet_malloc(sz);
    memcpy(tmp, args, sz);
    //将 launch_cb 设置为 snlua 服务的回调函数，参数为 l
    skynet_callback(ctx, l , launch_cb);
    const char * self = skynet_command(ctx, "REG", NULL);
    //self 的值为 :handle
    uint32_t handle_id = strtoul(self+1, NULL, 16);
    // it must be first message
    //向自己发送第一条消息，这条消息将由 launch_cb 进行处理，消息内容为 "bootstrap"
    skynet_send(ctx, 0, handle_id, PTYPE_TAG_DONTCOPY,0, tmp, sz);
    return 0;
}
```

从上述代码中可知，`snlua_create` 会负责初始化 `snlua` 结构体，并将其返回，而 `snlua_init` 函数则负责将创建好的snlua 服务的回调函数设置为 `launch_cb` 函数，并对其发送一个注册命令，完成后向 snlua 服务的次级消息队列发送一条消息。  

skynet 为每个模块都提供了一组相应的命令，其对应的数据类型为 `command_func`，skynet 为模块所提供的所有命令都存放在了
`cmd_funcs` 数组当中

```c
//skynet_service.c
struct command_func {
    const char *name;   //命令名称
    const char * (*func)(struct skynet_context * context, const char * param);  //命令对应的回调函数
};

static struct command_func cmd_funcs[] = {
    { "TIMEOUT", cmd_timeout },
    { "REG", cmd_reg },
    { "QUERY", cmd_query },
    { "NAME", cmd_name },
    { "EXIT", cmd_exit },
    { "KILL", cmd_kill },
    { "LAUNCH", cmd_launch },
    { "GETENV", cmd_getenv },
    { "SETENV", cmd_setenv },
    { "STARTTIME", cmd_starttime },
    { "ABORT", cmd_abort },
    { "MONITOR", cmd_monitor },
    { "STAT", cmd_stat },
    { "LOGON", cmd_logon },
    { "LOGOFF", cmd_logoff },
    { "SIGNAL", cmd_signal },
    { NULL, NULL },
};
```

在了解了 `command_func` 的定义后，我们来看看 `skynet_command` 函数的实现

```c
//查找相应的命令，并返回命令函数的执行结果
//snlua 对 skynet_command 的调用形式为 skynet_command(ctx, "REG", NULL)
const char* skynet_command(struct skynet_context * context, const char * cmd , const char * param) {
    struct command_func * method = &cmd_funcs[0];
    while(method->name) {
        if (strcmp(cmd, method->name) == 0) {
            return method->func(context, param);
        }
        ++method;
    }
    return NULL;
}

//cmd_reg(ctx, NULL)
static const char* cmd_reg(struct skynet_context * context, const char * param) {
    if (param == NULL || param[0] == '\0') {
        //将回调函数的执行结果和 handle 拼接在一起，并返回
        sprintf(context->result, ":%x", context->handle);
        //context->result 是用来存放 context->cb 的执行结果的
        return context->result;
    } else if (param[0] == '.') {
        return skynet_handle_namehandle(context->handle, param + 1);
    } else {
        skynet_error(context, "Can't register global name %s in C", param);
        return NULL;
    }
}
```

从上述代码中，我们可以简单地总结一下 snlua 的启动流程：

>   1. skynet 调用 bootstrap 函数创建了一个 snlua 服务
>
>   2. 在 bootstrap 创建服务的过程中，会先从全局的 modules 中查找 snlua 模块是否已加载，如果没有则加载到内存当中。
>
>   3. 加载完毕后，先调用 `snlua_create` 函数分配一个 snlua 结构体，该结构体中包含了一个独立的 lua 运行状态，用于执行相应的lua 脚本
>
>   4. 创建好对应的 snlua 模块实例后，执行 `snlua_init` 函数为其进行初始化。初始化的过程中负责设置服务的回调函数，并向 snlua 服务发送一个注册命令，随后向 snlua 服务发送一条消息
>
>   5. 将 snlua 的消息队列压入全局的消息队列当中  

完成上述的 5 个步骤后，一个 snlua 服务就算是启动起来了。

### bootstrap 服务的主要工作

在前面的内容当中，我们看到了 snlua 模块在初始化的过程当中会向自己发送一条消息，这样做的目的是为了自身的服务启动起来。因为在 skynet当中，服务要依靠消息来驱动。snlua 在初始化过程当中向自身发送了一条消息，当 snlua 服务创建完毕后，worker 线程便会消息队列当中取出消息并执行相应的回调函数 `launch_cb` 函数进行消费，这样就能够将 snlua 服务运转起来。我们来看一下`launch_cb` 的实现：

```c
//msg 的值为 bootstrap
static int launch_cb(struct skynet_context * context, void *ud, int type, int session, uint32_t source , const void * msg, size_t sz) {
    assert(type == 0 && session == 0);
    struct snlua *l = ud;
    //重设回调函数
    skynet_callback(context, NULL, NULL);
    int err = init_cb(l, context, msg, sz);
    if (err) {
        skynet_command(context, "EXIT", NULL);
    }
    return 0;
}

static int init_cb(struct snlua *l, struct skynet_context *ctx, const char * args, size_t sz) {
    lua_State *L = l->L;
    l->ctx = ctx;

    //暂停 lua 的 GC 机制
    lua_gc(L, LUA_GCSTOP, 0);
    lua_pushboolean(L, 1);  /* signal for libraries to ignore env. vars. */
    lua_setfield(L, LUA_REGISTRYINDEX, "LUA_NOENV");
    luaL_openlibs(L);
    lua_pushlightuserdata(L, ctx);
    lua_setfield(L, LUA_REGISTRYINDEX, "skynet_context");

    //判断 skynet.codecache 是否为与 package.loaded 当中。如果不在则调用 codecache 进行加载
    luaL_requiref(L, "skynet.codecache", codecache , 0);
    lua_pop(L,1);

    //设置相关的全局变量
    const char *path = optstring(ctx, "lua_path","./lualib/?.lua;./lualib/?/init.lua");
    lua_pushstring(L, path);
    lua_setglobal(L, "LUA_PATH");

    const char *cpath = optstring(ctx, "lua_cpath","./luaclib/?.so");
    lua_pushstring(L, cpath);
    lua_setglobal(L, "LUA_CPATH");

    const char *service = optstring(ctx, "luaservice", "./service/?.lua");
    lua_pushstring(L, service);
    lua_setglobal(L, "LUA_SERVICE");

    const char *preload = skynet_command(ctx, "GETENV", "preload");
    lua_pushstring(L, preload);
    lua_setglobal(L, "LUA_PRELOAD");

    //traceback 将 L 栈的回溯信息压入栈
    lua_pushcfunction(L, traceback);
    assert(lua_gettop(L) == 1);

    //lua 服务的加载器为 loader.lua
    const char * loader = optstring(ctx, "lualoader", "./lualib/loader.lua");
    int r = luaL_loadfile(L,loader);
    if (r != LUA_OK) {
        skynet_error(ctx, "Can't load %s : %s", loader, lua_tostring(L, -1));
        report_launcher_error(ctx);
        return 1;
    }

    //args = bootstrap
    lua_pushlstring(L, args, sz);

    //利用 loader 将 bootstrap.lua 脚本执行起来。
    r = lua_pcall(L,1,0,1);
    if (r != LUA_OK) {
        skynet_error(ctx, "lua loader error : %s", lua_tostring(L, -1));
        report_launcher_error(ctx);
        return 1;
    }

    lua_settop(L,0);
    if (lua_getfield(L, LUA_REGISTRYINDEX, "memlimit") == LUA_TNUMBER) {
        size_t limit = lua_tointeger(L, -1);
        l->mem_limit = limit;
        skynet_error(ctx, "Set memory limit to %.2f M", (float)limit / (1024 * 1024));
        lua_pushnil(L);
        lua_setfield(L, LUA_REGISTRYINDEX, "memlimit");
    }

    lua_pop(L, 1);

    //重启 lua 的 GC 机制
    lua_gc(L, LUA_GCRESTART, 0);

    return 0;
}

static int codecache(lua_State *L) {
    luaL_Reg l[] = {
        { "clear", cleardummy },
        { "mode", cleardummy },
        { NULL, NULL },
    };

    luaL_newlib(L,l);
    lua_getglobal(L, "loadfile");
    lua_setfield(L, -2, "loadfile");

    return 1;
}
```

从上述代码中可以看出，bootstrap服务(即前面的 snlua 服务)在触发时，会调用 `init_cb` 来代替 `lauch_cb`函数。简单地来说，`init_cb` 中最主要的部分便是设置相应的环境变量以及加载器loader。其中，环境变量的意义如下：

> `LUA_PATH`：Lua搜索路径，在`config.lua_path`指定。  
> `LUA_CPATH`：C模块的搜索路径，在`config.lua_cpath`指定。  
> `LUA_SERVICE`：Lua服务的搜索路径，在`config.luaservice`指定。  
> `LUA_PRELOAD`：预加载脚本，这些脚本会在所有服务开始之前执行，可以用它来初始化一些全局的设置。

在设置好相应的环境变量后，`init_cb` 会执行 loader.lua，并将 bootstrap.lua 传进去。loader.lua的主要作用是对环境变量以及传入的参数进行一些文本处理，然后找到对应的文件去执行，这里的参数主要是指 `bootstrap`，最终会执行/service/bootstrap.lua 文件。其中 bootstrap.lua 的源码如下：

```lua
--将 skynet.lua 中定义的函数引用到当前文件
local skynet = require "skynet"
local harbor = require "skynet.harbor"

require "skynet.manager"    -- import skynet.launch, ...

skynet.start(function()
    local standalone = skynet.getenv "standalone"

    --利用 skynet.launch 启动一个 launcher
    local launcher = assert(skynet.launch("snlua","launcher"))

    skynet.name(".launcher", launcher)

    --确认当前的 skynet 节点是主节点还是从节点
    local harbor_id = tonumber(skynet.getenv "harbor" or 0)
    if harbor_id == 0 then
        assert(standalone ==  nil)
        standalone = true
        skynet.setenv("standalone", "true")

        local ok, slave = pcall(skynet.newservice, "cdummy")
        if not ok then
            skynet.abort()
        end
        skynet.name(".cslave", slave)
    else
        if standalone then
            if not pcall(skynet.newservice,"cmaster") then
                skynet.abort()
            end
        end

        local ok, slave = pcall(skynet.newservice, "cslave")
        if not ok then
            skynet.abort()
        end
        skynet.name(".cslave", slave)
    end

    if standalone then
        local datacenter = skynet.newservice "datacenterd"
        skynet.name("DATACENTER", datacenter)
    end

    skynet.newservice "service_mgr"
    pcall(skynet.newservice,skynet.getenv "start" or "main")
    skynet.exit()
end)
```

从上述 lua 代码中，我们可以看出 bootstrap.lua 的主要工作如下：

>   1. 启动`launcher`服务，这个服务是一个通用的服务启动器，如果我们需要在lua创建一个 C 服务就需要用到它
>
>   2. 启动`datacenterd`服务
>
>   3. 启动`service_mgr`服务
>
>   4. 根据 config 中的 start 字段，指定相应的 lua 脚本，在 bootstrap 服务中启动的是 main.lua 脚本

到目前为止，bootstrap 服务的基本内容大概就说完了，而相关的一些其他一部分未说明清楚的部分(如main.lua, skynet.newservice, `skynet_launch` 等)则留在其他文章中讨论

<hr>

#### <p>原文出处：<a href='https://www.jianshu.com/p/bc37152b6413' target='blank'>如何在lua服务中启动另一个lua服务</a></p>

## skynet 源码阅读笔记 —— 如何在 lua 服务中启动另一个 lua 服务

在上一篇文章中[《skynet 源码阅读笔记 —— 引导服务 bootstrap的启动》](https://www.jianshu.com/p/1eb22d418087)，我们探讨了 bootstrap 服务的启动细节，其中bootstrap 服务的核心在于 bootstrap.lua 脚本的执行。而这篇博客会借助 bootstrap.lua 脚本中的部分内容来说明如何在一个lua 服务内启动其他的 lua 服务

```lua
--引用 skynet.lua 中的接口
local skynet = require "skynet"
local harbor = require "skynet.harbor"

require "skynet.manager"    -- import skynet.launch, ...

skynet.start(function()
    local standalone = skynet.getenv "standalone"
    local launcher = assert(skynet.launch("snlua","launcher"))
    skynet.name(".launcher", launcher)
    local harbor_id = tonumber(skynet.getenv "harbor" or 0)

    if harbor_id == 0 then
        assert(standalone ==  nil)
        standalone = true
        skynet.setenv("standalone", "true")

        local ok, slave = pcall(skynet.newservice, "cdummy")
        if not ok then
            skynet.abort()
        end

        skynet.name(".cslave", slave)
    else
        if standalone then
            if not pcall(skynet.newservice,"cmaster") then
                skynet.abort()
            end
        end

        local ok, slave = pcall(skynet.newservice, "cslave")

        if not ok then
            skynet.abort()
        end

        skynet.name(".cslave", slave)
    end

    if standalone then
        local datacenter = skynet.newservice "datacenterd"
        skynet.name("DATACENTER", datacenter)
    end

    skynet.newservice "service_mgr"
    pcall(skynet.newservice,skynet.getenv "start" or "main")
    skynet.exit()
end)
```

在上述代码中，我们可以看到 bootstrap.lua 在文件的最开始处，执行了 `local skynet = require "skynet"` 以及 `require "skynet.manager"`, 这都是为了要在 bootstrap.lua 文件中，引用 skynet 为 lua 服务所设计的api，对应文件及 api 如下：

> lualib/skynet.lua: `skynet.start` 和 `skynet.newservice`  
> 
> lualib/skynet/manager.lua: `skynet.launch` 和 `skynet.name`

### skynet.launch 及 skynet.name 的作用

对于 `skynet.start`函数我们放到后面讨论，这里先分析 `skynet.launch` 以及 `skynet.name` 两个函数，这两个函数定义如下：

```lua
--manager.lua
--bootstrap 中是这样调用 skynet.launch 函数的：skynet.launch("snlua","launcher")
function skynet.launch(...)
    --相当于执行 c.comand("LAUNCH", "snlua laucher")，
    local addr = c.command("LAUNCH", table.concat({...}," "))
    if addr then
        return tonumber("0x" .. string.sub(addr , 2))
    end
end
```

这里简单地说明一下 c 的意义，c 是定义在 skynet.lua 中的一个变量，其中保存了一张表。这张表可以由函数`luaopen_skynet_core` 创建。在这张表中定义了一个命令接口 command，对应的实现如下：

```c
//lua-skynet.c
static int lcommand(lua_State *L) {
    struct skynet_context * context = lua_touserdata(L, lua_upvalueindex(1));
    const char * cmd = luaL_checkstring(L,1);
    const char * result;
    const char * parm = NULL;
    if (lua_gettop(L) == 2) {
        parm = luaL_checkstring(L,2);
    }
    result = skynet_command(context, cmd, parm);
    if (result) {
        lua_pushstring(L, result);
        return 1;
    }
    return 0;
}

//skynet_service.c
static const char * cmd_launch(struct skynet_context * context, const char * param) {
    size_t sz = strlen(param);
    char tmp[sz+1];
    strcpy(tmp,param);
    char * args = tmp;
    char * mod = strsep(&args, " \t\r\n");
    args = strsep(&args, "\r\n");
    struct skynet_context * inst = skynet_context_new(mod,args);
    if (inst == NULL) {
        return NULL;
    } else {
        id_to_hex(context->result, inst->handle);
        return context->result;
    }
}
```

`lcommand` 函数的主要工作便是将对应的命令和参数转发回 C 层的 `cmd_launch` 函数中，这个函数最终会创建一个新的 snlua 类型的 C 服务 inst。而在创建这个 snlua 服务的过程中也会对其进行初始化，这个过程可见前一篇文章中所提到的 bootstrap 服务的创建及初始化，这里就不再赘述。

```lua
function skynet.name(name, handle)
    if not globalname(name, handle) then
        c.command("NAME", name .. " " .. skynet.address(handle))
    end
end
```

`skynet.name` 函数也会调用 `c.command` 接口来向对应的服务发送命令，只不过这次发送的是 NAME 命令，并且最终会调用`cmd_name`函数来为服务进行命名。

### 如何在 lua 服务中创建一个新的 lua 服务

在说完上面两个 api 后，我们再来看看 `skynet.newservice` 的作用。skynet 在 lua 层一共有两种不同的创建服务的方式：一种是`skynet.launch` 创建用 C 编写的服务，而另一种方式则是调用 `skynet.newservice` 创建 lua 服务。以上述的bootstrap 服务和 `service_mgr` 服务为例，创建 lua 服务的流程大致如下：

> 1. 在 bootstrap 的 `start_func` 中执行 `skynet.newservice "service_mgr"`,此时 bootstrap 服务陷入阻塞状态;  
> 2. 在 `service_mgr` 服务被创建出来以后，执行 `service_mgr.lua` 这个脚本，在这个脚本中会执行 `skynet.start` 函数，表示 `service_mgr` 服务正式启动，能够正常地接收消息;  
> 3. `service_mgr` 的 `skynet.start` 返回，bootstrap 服务的`skynet.newservice`函数返回，并获得了 `service_mgr` 服务的句柄

了解了这个基本过程后，让我们来看看 `skynet.newservice` 是如何定义的：

```lua
function skynet.newservice(name, ...)
    return skynet.call(".launcher", "lua" , "LAUNCH", "snlua", name, ...)
end
```

在上述代码中，bootstrap服务的`skynet.newservice`向launcher服务发送了一条命令，并阻塞等待launcher的返回执行结果。这条命令会传递到 launcher.lua中，并最终调用command.LAUNCH，进而调用`launch_service`：

```lua
function command.LAUNCH(_, service, ...)
    launch_service(service, ...)
    return NORET
end

local function launch_service(service, ...)
    local param = table.concat({...}, " ")
    --创建一个 lua 服务并获得该服务的句柄
    local inst = skynet.launch(service, param)
    local session = skynet.context()
    --调用 skynet.response() 获得一个 response 闭包
    local response = skynet.response()
    if inst then
        --将服务句柄和服务的命令形式以键值对的形式保存
        services[inst] = service .. " " .. param
        --保存闭包，这个 response 闭包最终会等 skynet.start 返回后再调用
        instance[inst] = response
        launch_session[inst] = session
    else
        response(false)
        return
    end
    return inst
end
```

在上述代码中，`launch_service` 在创建 `service_mgr` 服务后会调用相应的 `service_mgr.lua` 脚本。在对应的脚本中有一个 skynet.start 函数，其对应实现如下：

```lua
--skynet.lua
function skynet.start(start_func)
    --将对应服务的回调函数设置为 skynet.dispatch_message
    c.callback(skynet.dispatch_message)
    --执行服务脚本中传入的 start_func 函数
    init_thread = skynet.timeout(0, function()
        skynet.init_service(start_func)
        init_thread = nil
    end)
end

function skynet.init_service(start)
    local ok, err = skynet.pcall(start)
    if not ok then
        skynet.error("init service failed: " .. tostring(err))
        skynet.send(".launcher","lua", "ERROR")
        skynet.exit()
    else
        skynet.send(".launcher","lua", "LAUNCHOK")
    end
end
```

在上一篇文章中，我们提到了 snlua 模块在调用 `launch_cb` 函数时会执行 `skynet_callback(context, NULL, NULL);` 将回调函数置为 NULL，而在 skynet.start 函数中才将对应服务的回调函数置为`skynet.dispatch_message`,然后调用 `skynet.init_service(start_func)`对服务进行初始化。而`skynet.init_service(start_func)` 则会调用 `start_func` 函数完成对服务真正意义上的初始化，并根据初始化的结果向 launcher 发送成功或失败的消息。以下分别讨论：

  * 当初始化结果成功时，服务会向 launcher 发送 LAUNCHOK 的命令，这会触发 `comand.LAUNCHOK` 的执行,其中 `command.LAUNCHOK` 的定义如下：

```lua
--launcher.lua
function command.LAUNCHOK(address)
    -- init notice
    local response = instance[address]
    if response then
        response(true, address)
        instance[address] = nil
        launch_session[address] = nil
    end
    return NORET
end
```

从上述代码中可以看出，在执行初始化成功后，launcher会将之前调用 `launch_service` 时保存的闭包取出来执行，传入的第一个参数为 true 表示初始化成功。

  * 当初始化结果失败时，服务会向 launcher 发送 ERROR 的命令。

```lua
--launcher.lua
function command.ERROR(address)
    -- see serivce-src/service_lua.c
    -- init failed
    local response = instance[address]
    if response then
        response(false)
        launch_session[address] = nil
        instance[address] = nil
    end
    services[address] = nil
    return NORET
end
```

与前面 `command.LAUNCHOK`类似，`command.ERROR`会取出对应的 response 闭包并执行，传入参数为 false 表示初始化失败。随后当`skynet.send`返回后，调用 `skynet.exit` 函数移除初始化失败的服务。

```lua
--skynet.lua
function skynet.exit()
    fork_queue = {} -- no fork coroutine can be execute after skynet.exit
    skynet.send(".launcher","lua","REMOVE",skynet.self(), false)

    -- report the sources that call me
    for co, session in pairs(session_coroutine_id) do
        local address = session_coroutine_address[co]
        if session~=0 and address then
            c.send(address, skynet.PTYPE_ERROR, session, "")
        end
    end
    for resp in pairs(unresponse) do
        resp(false)
    end

    -- report the sources I call but haven't return
    local tmp = {}
    for session, address in pairs(watching_session) do
        tmp[address] = true
    end

    for address in pairs(tmp) do
        c.send(address, skynet.PTYPE_ERROR, 0, "")
    end

    c.command("EXIT")

    -- 退出服务后让出处理机权限
    coroutine_yield "QUIT"
end

--launcher.lua
function command.REMOVE(_, handle, kill)
    services[handle] = nil
    local response = instance[handle]
    if response then
        -- instance is dead
        response(not kill)  -- return nil to caller of newservice, when kill == false
        instance[handle] = nil
        launch_session[handle] = nil
    end

    -- don't return (skynet.ret) because the handle may exit
    return NORET
end
```

在执行 `skynet.exit`的过程中，会向 launcher 发送 REMOVE 命令，而这个命令最终会调用 `command.REMOVE` 函数。`command.REMOVE`会取出相应闭包，并判断该闭包是否已经被执行过。这代表了两种情况：一种是因为初始化出错而导致触发了 `command.ERROR`,这个过程中执行了 response 闭包；另一种就是服务自己调用了 `skynet.exit()` 自行退出，此时 response 闭包还没有被执行过。

当 `service_mgr` 服务的`skynet.start` 函数返回后，bootstrap 服务也重新进入运行状态，继续启动其他的服务(比如 main 服务)，整体的过程与启动 `service_mgr` 是相同的。

<hr>

#### <p>原文出处：<a href='https://www.jianshu.com/p/843b0c61cda8' target='blank'>lua服务间是如何交互的</a></p>

## skynet 源码阅读笔记 —— lua 服务间是如何交互的

skynet 中的服务都是由消息来负责驱动的，即便是 lua 服务也不例外。本文讨论的主题为 skynet 框架下，同一 skynet 节点内不同的lua 服务之间是如何通过消息来进行交互的。  

框架概览：

>   * lua 服务的消息协议
>   * lua 服务如何注册自己的消息及对应的回调函数
>   * lua 服务是如何接受消息的？
>   * lua 服务是如何发送消息的？

### lua 服务的消息协议

skynet 使用 proto 来描述不同的消息协议。在最开始的时候，proto 是一个空表，需要由 `skynet.register_protocol` 进行消息协议的注册。skynet 在启动 lua 服务的初期会默认注册 lua，response 以及 error 类型的消息协议，这个过程通常在 `require "skynet"`语句中执行。`skynet.register_protocol`函数如下：

```lua
function skynet.register_protocol(class)
    local name = class.name
    local id = class.id
    assert(proto[name] == nil and proto[id] == nil)
    assert(type(name) == "string" and type(id) == "number" and id >=0 and id <=255)
    proto[name] = class
    proto[id] = class
end

do
    local REG = skynet.register_protocol

    --注册不同的消息类型，有普通的 lua 消息，响应消息以及错误消息
    REG {
        name = "lua",
        id = skynet.PTYPE_LUA,
        pack = skynet.pack,
        unpack = skynet.unpack,
    }
    REG {
        name = "response",
        id = skynet.PTYPE_RESPONSE,
    }
    REG {
        name = "error",
        id = skynet.PTYPE_ERROR,
        unpack = function(...) return ... end,
        dispatch = _error_dispatch,
    }
end
```

从 skynet 默认注册的消息类型来推断，我们知道一个消息协议应当包含有以下的一些字段：

  * name:表明了该消息协议的类型名称
  * id:表明该消息协议的类型编号，包括了以下几种不同的类型 

```lua
local skynet = {
    -- read skynet.h
    PTYPE_TEXT = 0,     --文本类型
    PTYPE_RESPONSE = 1, --响应消息
    PTYPE_MULTICAST = 2,--组播消息
    PTYPE_CLIENT = 3,
    PTYPE_SYSTEM = 4,
    PTYPE_HARBOR = 5,
    PTYPE_SOCKET = 6,
    PTYPE_ERROR = 7,    --错误消息
    PTYPE_QUEUE = 8,    -- used in deprecated mqueue, use skynet.queue instead
    PTYPE_DEBUG = 9,
    PTYPE_LUA = 10,     --lua 服务类型的消息
    PTYPE_SNAX = 11,
    PTYPE_TRACE = 12,   -- use for debug trace
}
```

  * pack:发送消息时所用到的打包函数
  * unpack:接收消息时调用的解包函数
  * dispatch:由消息提供方指定对应类型消息的处理函数，如果没有指定，则最终会调用 `skynet.dispatch(typename, func)`  
函数来处理

说完基本的消息协议，我们来看看 skynet 定义的三种不同类型的消息都有什么作用：

>   1. lua 型消息：采用 skynet.pack 和 skynet.unpack 进行消息的打包和解包, 默认调用`skynet.dispatch(typename, func)`进行消息的派发
>
>   2. response 型消息：response 消息主要用于处理skynet.call调用和定时器的返回。当源服务向目的服务发送请求，会附带一个 session，目的服务在处理完请求后，会将 session 加入 response 消息中一起通过 `skynet.ret` 返回给源服务
>
>   3. error 型消息：当调用 `skynet.call` 发送错误消息时，源服务可以接收到一个 error 类型的消息

### lua 服务如何注册自己的消息及对应的回调函数

讲完了 lua 服务的消息服务的定义，我们以 example/simplemonitor.lua 中的服务来说明一下，lua 服务之间是如何相互收发信息的。而在这之前，我们需要看看 simplemonitor.lua 定义：

```lua
local skynet = require "skynet"

-- It's a simple service exit monitor, you can do something more when a service exit.
local service_map = {}

skynet.register_protocol {
    name = "client",
    id = skynet.PTYPE_CLIENT,   -- PTYPE_CLIENT = 3
    unpack = function() end,
    dispatch = function(_, address)
        local w = service_map[address]
        if w then
            for watcher in pairs(w) do
                skynet.redirect(watcher, address, "error", 0, "")
            end
            service_map[address] = false
        end
    end
}

local function monitor(session, watcher, command, service)
    assert(command, "WATCH")
    local w = service_map[service]
    if not w then
        if w == false then
            skynet.ret(skynet.pack(false))
            return
        end
        w = {}
        service_map[service] = w
    end
    w[watcher] = true
    skynet.ret(skynet.pack(true))
end

skynet.start(function()
    skynet.dispatch("lua", monitor)
end)
```

如以往的文章所提到的那样，当使用 `skynet.newservice` 函数启动一个新的 lua 服务时，会执行相应的脚本来完成服务的初始化。在 simplemonitor.lua 脚本中，先执行了 `require "skynet"`，这不仅会将相应的函数导入到当前 lua 脚本当中，还会执行`skynet.register_protocol`为 simplemonitor 注册三种默认消息协议。随后，simplemonitor.lua 又调用了 `skynet.register_protocol` 注册了一个 client 类型的 lua 消息协议，并指定了对应的 dispatch 函数。随后调用 `skynet.start` 来启动 simplemonitor 服务。在上一篇文章[《skynet 源码阅读笔记 —— 如何在 lua 服务中启动另一个 lua 服务》](https://www.jianshu.com/p/bc37152b6413) 中提到了 `skynet.start` 会将 simplemonitor 服务的消息回调函数设置为 `skynet.dispatch_message`,然后执行 `skynet.dipatch("lua", monitor)`进行服务的初始化。

### lua 服务是如何接受消息的？

讨论完 lua 服务是如何注册自己的消息类型及定义消息对应的回调函数后，我们来看看 lua 服务是如何接受消息的。我们先来看看`skynet.dispatch` 函数的实现：

```lua
--skynet.lua
--simplemonitor 的调用形式为 skynet.dispatch("lua", monitor)
function skynet.dispatch(typename, func)
    --取出 lua 型消息对应的协议
    local p = proto[typename]
    if func then
        local ret = p.dispatch
        --将对应的 dispatch 函数设置为 monitor
        p.dispatch = func
        --返回原来的 dispatch 函数
        return ret
    else
        return p and p.dispatch
    end
end
```

从上述代码可以看出，当 simplemonitor 服务启动完毕后，对应的 lua 消息协议的 dispatch 函数实际上就是 `monitor`函数。接着，我们再来看看 `skynet.dispatch_message`

```lua
function skynet.dispatch_message(...)
    --调用 raw_dispatch_message 进行消息的转发
    local succ, err = pcall(raw_dispatch_message,...)

    while true do
        local co = tremove(fork_queue,1)
        if co == nil then
            break
        end

        local fork_succ, fork_err = pcall(suspend,co,coroutine_resume(co))

        if not fork_succ then
            if succ then
                succ = false
                err = tostring(fork_err)
            else
                err = tostring(err) .. "\n" .. tostring(fork_err)
            end
        end
    end

    assert(succ, tostring(err))
end

local function raw_dispatch_message(prototype, msg, sz, session, source)
    if prototype == 1 then
        ... --prototype == 1代表响应消息类型
    else
        --取出相应的消息协议
        local p = proto[prototype]
        if p == nil then
            ...    --若 p == nil 则调用 c.send 发送一个 ERROR 型消息
        end

        local f = p.dispatch

        if f then
            -- co_create 会从协程池中获取一个空的协程，如果没有则创建一个新的协程，并将 dispatch 函数交给这个协程去执行。
            local co = co_create(f)
            session_coroutine_id[co] = session
            session_coroutine_address[co] = source
            local traceflag = p.trace

            if traceflag == false then
                -- force off
                trace_source[source] = nil
                session_coroutine_tracetag[co] = false
            else
                local tag = trace_source[source]
                if tag then
                    trace_source[source] = nil
                    c.trace(tag, "request")
                    session_coroutine_tracetag[co] = tag
                elseif traceflag then
                    -- set running_thread for trace
                    running_thread = co
                    skynet.trace()
                end
            end

            --启动并执行协程，将协程执行的结果返回给suspend函数，suspend 会根据这个结果执行相应的操作
            suspend(co, coroutine_resume(co, session,source, p.unpack(msg,sz)))
        else
            trace_source[source] = nil

            if session ~= 0 then
                c.send(source, skynet.PTYPE_ERROR, session, "")
            else
                unknown_request(session, source, msg, sz, proto[prototype].name)
            end
        end
    end
end
```

结合上述带注释的代码，我们描述一下整体的过程：当服务 A 向 simplemonitor 发送一条消息时，会将这条消息放入到 simplemonitor 对应的 snlua 服务所属的次级消息队列当中(skynet当中有多个 snlua 类型的服务，分别对应不同的 lua 服务)。worker 线程会将其取出并消费，在消费的过程当中会调用该消息所指定的 callback 函数。而 `skynet.start` 已经通过 `c.callback(skynet.dispatch_message)` 将 simplemonitor 的消息的回调函数设置为 `skynet.dispatch_message`。此时，worker线程最终就会调用到 `raw_dispatch_message`函数。这个函数会获得一个新的空的协程来执行消息协议中指定的 dispatch 函数。对应协程一旦执行起来完毕，会调用 `coroutine_yield` 函数将自身挂起，并返回挂起的原因。`suspend`会根据这个原因做不同的处理

### lua 服务是如何发送消息的？

讲完了当 simplemonitor 收到消息的行为，我们再来看看发送消息的行为。假设现在有一个服务 A 需要向另一个服务 B 发送一条消息，那么他需要调用 `skynet.send` 函数。我们来看看 `skynet.send` 函数的定义：

```lua
function skynet.send(addr, typename, ...)
    local p = proto[typename]
    return c.send(addr, p.id, 0 , p.pack(...))
end
```

`skynet.send`会调用 `c.send(addr, p.id, 0 , p.pack(...))` 函数来发送消息，其中 `c.send` 函数的参数从左至右分别是目标地址，消息协议类型，session ID，自定义参数列表。   

我们再来看看 `c.send` 所对应的函数 `lsend` 是如何实现的：

```c
//lua-skynet.c
static int lsend(lua_State *L) {
    return send_message(L, 0, 2);
}

static int send_message(lua_State *L, int source, int idx_type) {
    struct skynet_context * context = lua_touserdata(L, lua_upvalueindex(1));

    //获得目的地址 addr
    uint32_t dest = (uint32_t)lua_tointeger(L, 1);
    const char * dest_string = NULL;

    if (dest == 0) {
        if (lua_type(L,1) == LUA_TNUMBER) {
            return luaL_error(L, "Invalid service address 0");
        }
        dest_string = get_dest_string(L, 1);
    }

    int type = luaL_checkinteger(L, idx_type+0);
    int session = 0;

    //如果没有设置 session，则最后分配一个 ssession
    if (lua_isnil(L,idx_type+1)) {
        type |= PTYPE_TAG_ALLOCSESSION;
    } else {
        session = luaL_checkinteger(L,idx_type+1);
    }

    int mtype = lua_type(L,idx_type+2);
    
    switch (mtype) {
      case LUA_TSTRING: {
          size_t len = 0;
          void * msg = (void *)lua_tolstring(L,idx_type+2,&len);
          if (len == 0) {
              msg = NULL;
          }
          //调用 skynet_send 将对应的消息发送到指定服务的次级消息队列当中。
          if (dest_string) {
              session = skynet_sendname(context, source, dest_string, type, session , msg, len);
          } else {
              session = skynet_send(context, source, dest, type, session , msg, len);
          }
          break;
      }
      case LUA_TLIGHTUSERDATA: {
          void * msg = lua_touserdata(L,idx_type+2);
          int size = luaL_checkinteger(L,idx_type+3);
          if (dest_string) {
              session = skynet_sendname(context, source, dest_string, type | PTYPE_TAG_DONTCOPY, session, msg, size);
          } else {
              session = skynet_send(context, source, dest, type | PTYPE_TAG_DONTCOPY, session, msg, size);
          }
          break;
      }
      default:
          luaL_error(L, "invalid param %s", lua_typename(L, lua_type(L,idx_type+2)));
    }
    if (session < 0) {
        if (session == -2) {
            // package is too large
            lua_pushboolean(L, 0);
            return 1;
        }
        // send to invalid address
        // todo: maybe throw an error would be better
        return 0;
    }

    lua_pushinteger(L,session);
    return 1;
}
```

结合上述代码及注释，当一个 lua 服务向另一个 lua 服务发送消息时，会调用`skynet.send` 函数，这个函数最终会调用 C 层的`send_message`函数，通过对调用参数的解析，为消息添加上 type 和 session 字段，并最终调用 `skynet_send` 函数，这个函数在之前的[skynet 源码阅读笔记 —— 消息调度机制](https://www.jianshu.com/p/6aa32e53856a)说明了它的作用，这里就不多做说明。`skynet_send`函数将消息压入到指定服务的次级消息队列中，发送的过程就结束了。接下来只需要等待 worker 线程从全局消息队列中取出对应的次级消息队列，并消费相应的消息即可。

