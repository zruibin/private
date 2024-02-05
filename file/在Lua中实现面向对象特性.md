 
<!--BEGIN_DATA
{
    "create_date": "2021-12-24 19:20", 
    "modify_date": "2021-12-24 19:20", 
    "is_top": "0", 
    "summary": "在Lua中实现面向对象特性——模拟类、继承、多态<br/>Lua中实现面向对象的一种漂亮解决方案<br/>在Lua中以面向对象的方式使用C++注册的类<br/>如何创建一个安全的Lua沙盒", 
    "tags": "Lua", 
    "file_name": "在Lua中实现面向对象特性.md"
}
END_DATA-->

#### <p>原文出处：<a href='https://www.cnblogs.com/msxh/p/8469340.html' target='blank'>在Lua中实现面向对象特性——模拟类、继承、多态</a></p>

## 一、简介

Lua是一门非常强大、非常灵活的脚本语言，自它从发明以来，无数的游戏使用了Lua作为开发语言。但是作为一款脚本语言，Lua也有着自己的不足，那就是它本身并没有提供面向对象的特性，而游戏开发是一项庞大复杂的工程，如果没有面向对象功能势必会为开发带来一定的不便。不过幸好Lua中有table这样强大的数据结构，利用它再结合元表(metatable)，我们便可以很方便地在Lua中模拟出类、继承和多态等面向对象编程具有的特性。

## 二、前提知识

按照惯例，我们还是先来熟悉一下必要的前提知识，以便方便我们理解后续的代码。

### 1.表(table)

(1)table 是 Lua 的一种数据结构，用于帮助我们创建不同的数据类型，如：数组、字典等；

(2)table 是一个关联型数组，你可以用任意类型的值来作数组的索引，但这个值不能是 nil，所有索引值都需要用 "["和"]"括起来；如果是字符串，还可以去掉引号和中括号； 即如果没有[]括起，则认为是字符串索引，Lua table 是不固定大小的，你可以根据自己需要进行扩容；

(3)table 的默认初始索引一般以 1 开始，如果不写索引，则索引就会被认为是数字，并按顺序自动从1往后编；

(4)table 的变量只是一个地址引用，对 table 的操作不会产生数据影响；

(5)table 不会固定长度大小，有新数据插入时长度会自动增长；

(6)table 里保存数据可以是任何类型，包括function和table；

(7)table所有元素之间，总是用逗号 "，" 隔开；

### 2.元表(metatable)

关于元表的概念以及它的要点，我们已经在《[【游戏开发】小白学Lua——从Lua查找表元素的过程看元表、元方法](http://www.cnblogs.com/msxh/p/7745553.html)》这篇博客中做了深入地探讨，在此就不再赘述了，忘记了或者不熟悉的小伙伴可以去看一下。

## 三、Lua中实现类、继承、多态

### 1.利用Lua实现类

在面向对象的特性中，类一般都有类名，构造方法，成员方法，属性等。下面我们就用Lua中的table和元表实现一下模拟类中的这些特性，Class.lua代码如下：

```lua
--类的声明，这里声明了类名还有属性，并且给出了属性的初始值
Class = {x=0,y=0}
--设置元表的索引，想模拟类的话，这步操作很关键
Class.__index = Class
--构造方法，构造方法的名字是随便起的，习惯性命名为new()
function Class:new(x,y)
     local t = {}  --初始化t，如果没有这句，那么类所建立的对象如果有一个改变，其他对象都会改变
     setmetatable(t, Class)  --将t的元表设定为Class
     t.x = x   --属性值初始化
     t.y = y
     return t  --返回自身
end

--这里定义类的其他方法
function Class:test()
 print(self.x,self.y)
end

function Class:plus()
 self.x = self.x + 1
 self.y = self.y + 1
end
```

简单解释一下，在Lua中的类，其实都是table，因为table既可以存储普通变量又可以存储函数或者另一个table，利用这个特性，我们实现了面向对象的类中的方法、属性(字段)和构造方法。而设置元表和__index元方法这一步也是必不可少的，我们需要借助它的查找机制来实现类的继承和多态等。

### 2.利用Lua实现继承

在上面我们实现了Lua中的类，那么实现继承也就不是什么难事了，SubClass.lua 代码如下：

```lua
require 'Class'

--声明了新的属性Z
SubClass = {z = 0}
--设置类型是Class
setmetatable(SubClass, Class)
--还是和类定义一样，表索引设定为自身
SubClass.__index = SubClass
--这里是构造方法
function SubClass:new(x,y,z)
   local t = {}             --初始化对象自身
   t = Class:new(x,y)       --将对象自身设定为父类，这个语句相当于其他语言的super 或者 base
   setmetatable(t, SubClass)    --将对象自身元表设定为SubClass类
   t.z= z                   --新的属性初始化，如果没有将会按照声明=0
   return t
end

--定义一个新的方法
function SubClass:go()
   self.x = self.x + 10
end

--重定义父类的方法，相当于override
function SubClass:test()
     print(self.x,self.y,self.z)
end
```

代码里面的注释已经很全了，关键点是通过设置SubClass的元表为它的父类Class，从而很方便地实现了继承，这还是要归功于table的查找机制。在子类SubClass中，我们可以自由地新增字段和子类独有的新方法。而且还可以重定义或者说覆盖/重写父类的方法，类似于Java中的override，子类覆盖父类的虚方法。有了这些我们就可以模拟面向对象中的多态了。

### 3.利用Lua实现多态

这里我们新建一个 Main.lua 将它作为我们程序的入口，在里面测试一下我们上面的代码是否如我们所期待的那样，Main.lua 代码如下：

```lua
require 'Class'
require 'SubClass'

local a = Class:new() -- 首先实例化父类的对象，并调用父类中的方法
a:plus()
a:test()

a = SubClass:new()    -- 然后实例化子类对象
a:plus()            -- 子类对象可以访问到父类中的成员和方法
a:go()                -- 子类对象调用子类中的新增方法
a:test()            -- 子类对象调用重写的方法
```

程序运行的输出结果如下：

```lua
1       1
11      1       0
```

首先我们实例化父类对象并调用父类中的方法，结果输出了1 1，符合预期。接着我们再实例化了子类的对象，然后成功地访问到了父类中的成员变量和方法，并且还可以访问子类中的新增方法，最后我们再执行了重写过父类中虚函数的方法，结果输出 11 1 0，也是正确的。

## 四、总结

通过简单地几步，我们就在Lua中成功地模拟了类、继承和多态的特性，这可以给我们程序开发带来了不少的方便。以Unity游戏开发举例，tolua/ulua是Unity游戏开发热更新方案中的一种，他们功能很强大，但是美中不足的一点就是它们没有提供面向对象的特性，所以在开发的时候，很多直接就是全局函数、全局变量和过程式的开发流程，影响了开发的效率，更对之后的维护带来诸多不便。因此我们就可以通过与本篇中类似的方法，改进tolua/ulua，让它们也可以实现面向对象开发。

当然本篇中的代码只是作为抛砖引玉，它其实是十分简陋的，想用在商业项目中还需要做很多的改良与完善。至于如何改进tolua/ulua，让他们支持面向对象特性，我们将在以后的篇章中继续探讨。

本篇博客中的代码已经同步到Github:<https://github.com/XINCGer/Unity3DTraining/tree/master/SomeTest/Lua_Class>欢迎fork!

<hr>

#### <p>原文出处：<a href='https://www.jb51.net/article/59723.htm' target='blank'>Lua中实现面向对象的一种漂亮解决方案</a></p>

这篇文章主要介绍了Lua中实现面向对象的一种漂亮解决方案,本文给出实现代码、使用方法及代码分析,需要的朋友可以参考下

在 pil 中，lua 的作者推荐了[一种方案来实现OO](http://www.lua.org/pil/16.html)，比较简洁，但是我依然觉得有些繁琐。

这里给出一种更漂亮一点的解决方案，见下文：

这里提供 Lua 中实现 OO 的一种方案：  

代码如下:

```lua
local _class={}
 
function class(super)
 local class_type={}
 class_type.ctor=false
 class_type.super=super
 class_type.new=function(...)
   local obj={}
   do
    local create
    create = function(c,...)
     if c.super then
      create(c.super,...)
     end
     if c.ctor then
      c.ctor(obj,...)
     end
    end
 
    create(class_type,...)
   end
   setmetatable(obj,{ __index=_class[class_type] })
   return obj
  end
 local vtbl={}
 _class[class_type]=vtbl
 
 setmetatable(class_type,{__newindex=
  function(t,k,v)
   vtbl[k]=v
  end
 })
 
 if super then
  setmetatable(vtbl,{__index=
   function(t,k)
    local ret=_class[super][k]
    vtbl[k]=ret
    return ret
   end
  })
 end
 
 return class_type
end
```


现在，我们来看看怎么使用：  

```lua
base_type=class()  -- 定义一个基类 base_type  
```

代码如下:

```lua
function base_type:ctor(x) -- 定义 base_type 的构造函数  
 print("base_type ctor")  
 self.x=x  
end  
  
function base_type:print_x() -- 定义一个成员函数 base_type:print_x  
 print(self.x)  
end  
  
function base_type:hello() -- 定义另一个成员函数 base_type:hello  
 print("hello base_type")  
end  
```
  
以上是基本的 class 定义的语法，完全兼容 lua 的编程习惯。我增加了一个叫做 ctor 的词，作为构造函数的名字。  

下面看看怎样继承：  

代码如下:

```lua
test=class(base_type) -- 定义一个类 test 继承于 base_type  
  
function test:ctor() -- 定义 test 的构造函数  
 print("test ctor")  
end  
  
function test:hello() -- 重载 base_type:hello 为 test:hello  
 print("hello test")  
end  
```
  
现在可以试一下了：  

代码如下:

```lua
a=test.new(1) -- 输出两行，base_type ctor 和 test ctor 。这个对象被正确的构造了。  
a:print_x() -- 输出 1 ，这个是基类 base_type 中的成员函数。  
a:hello() -- 输出 hello test ，这个函数被重载了。  
```

在这个方案中，只定义了一个函数 class(super) ，用这个函数，我们就可以方便的在 lua 中定义类：  

代码如下:

```lua
base_type=class()       -- 定义一个基类 base_type

function base_type:ctor(x)  -- 定义 base_type 的构造函数  
    print("base_type ctor")  
    self.x=x  
end

function base_type:print_x()    -- 定义一个成员函数 base_type:print_x  
    print(self.x)  
end

function base_type:hello()  -- 定义另一个成员函数 base_type:hello  
    print("hello base_type")  
end
```

以上是基本的 class 定义的语法，完全兼容 lua 的编程习惯。我增加了一个叫做 ctor 的词，作为构造函数的名字。

下面看看怎样继承： 

```lua
test=class(basetype) -- 定义一个类 test 继承于 basetype  
```

代码如下:

```lua
function test:ctor()    \-- 定义 test 的构造函数  
    print("test ctor")  
end

function test:hello()   \-- 重载 base_type:hello 为 test:hello  
    print("hello test")  
end  
```
  
现在可以试一下了：  

代码如下:

```lua
a=test.new(1)   \-- 输出两行，base_type ctor 和 test ctor 。这个对象被正确的构造了。  
a:print_x() -- 输出 1 ，这个是基类 base_type 中的成员函数。  
a:hello()   \-- 输出 hello test ，这个函数被重载了。  
```
  
其实，实现多重继承也并不复杂，这里就不再展开了。更有意义的扩展可能是增加一个 dtor :)

ps. 这里用了点小技巧，将 self 绑定到 closure 上，所以并不使用 a:hello 而是直接用 a.hello 调用成员函数。这个技巧并不非常有用，从效率角度上说，还是不用为好。

**您可能感兴趣的文章:**

  * [Lua面向对象之类和继承](https://www.jb51.net/article/55168.htm)
  * [Lua面向对象之多重继承、私密性详解](https://www.jb51.net/article/55171.htm)
  * [Lua面向对象之类和继承浅析](https://www.jb51.net/article/55724.htm)
  * [Lua中的面向对象编程详解](https://www.jb51.net/article/55823.htm)
  * [Lua 极简入门指南（七）：面向对象编程](https://www.jb51.net/article/57015.htm)
  * [Lua面向对象编程学习笔记](https://www.jb51.net/article/58384.htm)
  * [Lua模拟面向对象示例分享](https://www.jb51.net/article/61926.htm)
  * [Lua](http://common.jb51.net/tag/Lua/1.htm)
  * [面向对象](http://common.jb51.net/tag/%E9%9D%A2%E5%90%91%E5%AF%B9%E8%B1%A1/1.htm)
  * [Lua极简入门指南（六）：模块](https://www.jb51.net/article/56935.htm)
  * [Lua教程（十七）：C API简介](https://www.jb51.net/article/65224.htm)
  * [Lua中的loadfile、dofile、require详解](https://www.jb51.net//article/55125.htm)
  * [Lua的table库函数insert、remove、concat、sort详细介绍](https://www.jb51.net/article/64711.htm)
  * [Lua中调用函数使用点号和冒号的区别](https://www.jb51.net/article/55163.htm)
  * [Lua中的table学习笔记](https://www.jb51.net/article/58478.htm)
  * [Lua中table的几种构造方式详解](https://www.jb51.net/article/55115.htm)

<hr>
#### <p>原文出处：<a href='https://www.cnblogs.com/chevin/p/5897220.html' target='blank'>在Lua中以面向对象的方式使用C++注册的类</a></p>

在上一节《[Lua和C++交互 学习记录之八：注册C++类为Lua模块](http://www.cnblogs.com/chevin/p/5896858.html)》里介绍了在Lua中以模块的方式使用C++注册的类。

下面将其修改为熟悉的面向对象调用方式。

## 1.Lua中面向对象的方式

1. 在Lua中使用`student_obj:get_age()`其实相当于`student_obj.get_age(student_obj)`

2. 给`student_obj`增加一个元表metatable，并设置元表里key为`"__index"`的值的为metatable本身，然后将成员操作方法添加到元表metatable里，这样通过:操作符就可以找到对应的方法了。

3. 这个增加的元表会放在Lua的全局表中用一个自定义的字符串，比如"StudentClass"，为key值进行保存(为了避免冲突，最好能起比较特殊的key值)。

## 2.Lua的全局表

1. 这个全局表可以使用`LUA_REGISTRYINDEX`索引从Lua中得到。

```lua
//lua->stack
lua_getfield(L, LUA_REGISTRYINDEX, "StudentClass");

////-------等价于下面两个函数------
//lua_pushstring("StudentClass");
//lua_gettable(L, LUA_REGISTRYINDEX);
```

2. 可以使用相应的`lua_setfield`函数设置table,下面的-1使用`LUA_REGISTRYINDEX`，就是设置全局表中Key为"StudentClass"的值（后面的代码就是将元表作为值）

```lua
lua_pushinteger(L, 66); //val
lua_setfield(L, -1, "StudentClass");

////-------等价于下面函数------
//lua_pushstring("StudentClass"); //key
//lua_pushinteger(L, 66); //val
//lua_settable(L, -1);
```

3. 将所有函数分为两部分进行注册

①第一部分：构造函数，和原来一样注册到Lua使用

```c
//构造函数
static const luaL_Reg lua_reg_student_constructor_funcs[] = {
     { "create", lua_create_new_student },
     { NULL, NULL }
;
```

②第二部分：成员操作函数，需要注册到元表里

```c
//成员操作函数
static const luaL_Reg lua_reg_student_member_funcs[] = {
    { "get_name", lua_get_name },
    { "set_name", lua_set_name },
    { "get_age", lua_get_age },
    { "set_age", lua_set_age },
    { "print", lua_print },
    { NULL, NULL },
};
```

4. 修改注册函数：创建元表，设置元表的`__index`为元表本身，注册成员操作函数到元表中

```c
int luaopen_student_libs(lua_State* L)
{
    //创建全局元表（里面包含了对LUA_REGISTRYINDEX的操作），元表的位置为-1
    luaL_newmetatable(L, "StudentClass");

    //将元表作为一个副本压栈到位置-1，原元表位置-2
    lua_pushvalue(L, -1);

    //设置-2位置元表的__index索引的值为位置-1的元表，并弹出位置-1的元表，原元表的位置为-1
    lua_setfield(L, -2, "__index");

    //将成员函数注册到元表中（到这里，全局元表的设置就全部完成了）
    luaL_setfuncs(L, lua_reg_student_member_funcs, 0);

    //注册构造函数到新表中，并返回给Lua
    luaL_newlib(L, lua_reg_student_constructor_funcs);

    return 1;
}
```

5. 修改创建对象函数：创建对象的userdata，将全局元表设置到userdata上

```c
int lua_create_new_student(lua_State* L)
{
    //创建一个对象指针放到stack里，返回给Lua中使用，userdata的位置-1
    Student** s = (Student**)lua_newuserdata(L, sizeof(Student*));
    *s = new Student();

    //Lua->stack，得到全局元表位置-1,userdata位置-2
    luaL_getmetatable(L, "StudentClass");

    //将元表赋值给位置-2的userdata，并弹出-1的元表
    lua_setmetatable(L, -2);

    return 1;
}
```

6. 修改Lua中的调用方式为面向对象方式

```c
local student_obj = Student.create()
student_obj:set_name("Jack")
student_obj:print()

--下面的代码也是可行的
--student_obj.set_name(student_obj,"Jack")
--student_obj.print(student_obj)
```

以上，就完成了面向对象的内容了。

7. 使用`luaL_checkudata`宏替换`lua_touserdata`函数

```c
Student** s = (Student**)luaL_checkudata(L, 1, "StudentClass");
```

除了可以转换userdata之外，还可以检查是否有"StudentClass"的元表，增加程序健壮性。

8. 自动GC

①当Lua进行自动内存回收GC时，会调用内部的`__gc`函数，所以定义一个函数和其进行注册对应

②函数实现

```c
int lua_auto_gc(lua_State* L)
{
    Student** s = (Student**)luaL_checkudata(L, 1, "StudentClass");
    luaL_argcheck(L, s != NULL, 1, "invalid user data");

    if (s){
        delete *s;
    }

    return 0;
}
```

③在注册成员函数`lua_reg_student_member_funcs`中增加对应的函数

```c
{ "__gc", lua_auto_gc }, //注册Lua内部函数__gc
```

④修改对应的Lua代码，增加对象回收的代码

```lua
--让其进行自动gc
student_obj = nil

--手动强制gc
--collectgarbage("collect")
```

⑤还有比较常用的内部函数是`__tostring`

下面列出整个项目的所有文件：

一.main.cpp文件

```c
#include <iostream>

//这个头文件包含了所需的其它头文件
#include "lua.hpp"

#include "Student.h"
#include "StudentRegFuncs.h"

static const luaL_Reg lua_reg_libs[] = {
    { "base", luaopen_base }, //系统模块
    { "Student", luaopen_student_libs}, //模块名字Student，注册函数luaopen_student_libs
    { NULL, NULL }
};

int main(int argc, char* argv[])
{
    if (lua_State* L = luaL_newstate()){

        //注册让lua使用的库
        const luaL_Reg* lua_reg = lua_reg_libs;
        for (; lua_reg->func; ++lua_reg){
            luaL_requiref(L, lua_reg->name, lua_reg->func, 1);
            lua_pop(L, 1);
        }
        //加载脚本，如果出错，则打印错误
        if (luaL_dofile(L, "hello.lua")){
            std::cout << lua_tostring(L, -1) << std::endl;
        }

        lua_close(L);
    }
    else{
        std::cout << "luaL_newstate error !" << std::endl;
    }

    system("pause");

    return 0;
}
```

二.Student.h文件

```c
#pragma once

#include <iostream>
#include <string>

class Student
{
public:
    //构造/析构函数
    Student();
    ~Student();

    //get/set函数
    std::string get_name();
    void set_name(std::string name);
    unsigned get_age();
    void set_age(unsigned age);

    //打印函数
    void print();

private:
    std::string _name;
    unsigned _age;
};
```

三.Student.cpp文件

```c
#include "Student.h"

Student::Student()
    :_name("Empty"),
    _age(0)
{
    std::cout << "Student Constructor" << std::endl;
}

Student::~Student()
{
    std::cout << "Student Destructor" << std::endl;
}

std::string Student::get_name()
{
    return _name;
}

void Student::set_name(std::string name)
{
    _name = name;
}

unsigned Student::get_age()
{
    return _age;
}

void Student::set_age(unsigned age)
{
    _age = age;
}

void Student::print()
{
    std::cout << "name :" << _name << " age : " << _age << std::endl;
}
```

四.StudentRegFuncs.h文件

```c
#pragma once

#include "Student.h"
#include "lua.hpp"

//------定义相关的全局函数------
//创建对象
int lua_create_new_student(lua_State* L);

//get/set函数
int lua_get_name(lua_State* L);
int lua_set_name(lua_State* L);
int lua_get_age(lua_State* L);
int lua_set_age(lua_State* L);

//打印函数
int lua_print(lua_State* L);

//转换为字符串函数
int lua_student2string(lua_State* L);

//自动GC
int lua_auto_gc(lua_State* L);

//------注册全局函数供Lua使用------
//构造函数
static const luaL_Reg lua_reg_student_constructor_funcs[] = {
    { "create", lua_create_new_student },
    { NULL, NULL }
};

//成员操作函数
static const luaL_Reg lua_reg_student_member_funcs[] = {
    { "get_name", lua_get_name },
    { "set_name", lua_set_name },
    { "get_age", lua_get_age },
    { "set_age", lua_set_age },
    { "print", lua_print },
    { "__gc", lua_auto_gc }, //注册Lua内部函数__gc
    { "__tostring", lua_student2string },
    { NULL, NULL },
};

int luaopen_student_libs(lua_State* L);
```

五.StudentRegFuncs.cpp文件

```c
#include "StudentRegFuncs.h"

int lua_create_new_student(lua_State* L)
{
    //创建一个对象指针放到stack里，返回给Lua中使用，userdata的位置-1
    Student** s = (Student**)lua_newuserdata(L, sizeof(Student*));
    *s = new Student();

    //Lua->stack，得到全局元表位置-1,userdata位置-2
    luaL_getmetatable(L, "StudentClass");

    //将元表赋值给位置-2的userdata，并弹出-1的元表
    lua_setmetatable(L, -2);

    return 1;
}

int lua_get_name(lua_State* L)
{
    //得到第一个传入的对象参数（在stack最底部）
    Student** s = (Student**)luaL_checkudata(L, 1, "StudentClass");
    luaL_argcheck(L, s != NULL, 1, "invalid user data");

    //清空stack
    lua_settop(L, 0);

    //将数据放入stack中，供Lua使用
    lua_pushstring(L, (*s)->get_name().c_str());

    return 1;
}

int lua_set_name(lua_State* L)
{
    //得到第一个传入的对象参数
    Student** s = (Student**)luaL_checkudata(L, 1, "StudentClass");
    luaL_argcheck(L, s != NULL, 1, "invalid user data");

    luaL_checktype(L, -1, LUA_TSTRING);

    std::string name = lua_tostring(L, -1);
    (*s)->set_name(name);

    return 0;
}

int lua_get_age(lua_State* L)
{
    Student** s = (Student**)luaL_checkudata(L, 1, "StudentClass");
    luaL_argcheck(L, s != NULL, 1, "invalid user data");

    lua_pushinteger(L, (*s)->get_age());

    return 1;
}

int lua_set_age(lua_State* L)
{
    Student** s = (Student**)luaL_checkudata(L, 1, "StudentClass");
    luaL_argcheck(L, s != NULL, 1, "invalid user data");

    luaL_checktype(L, -1, LUA_TNUMBER);

    (*s)->set_age((unsigned)lua_tointeger(L, -1));

    return 0;
}

int lua_print(lua_State* L)
{
    Student** s = (Student**)luaL_checkudata(L, 1, "StudentClass");
    luaL_argcheck(L, s != NULL, 1, "invalid user data");

    (*s)->print();

    return 0;
}

int lua_student2string(lua_State* L)
{
    Student** s = (Student**)luaL_checkudata(L, 1, "StudentClass");
    luaL_argcheck(L, s != NULL, 1, "invalid user data");

    lua_pushfstring(L, "This is student name : %s age : %d !", (*s)->get_name().c_str(), (*s)->get_age());

    return 1;
}

int lua_auto_gc(lua_State* L)
{
    Student** s = (Student**)luaL_checkudata(L, 1, "StudentClass");
    luaL_argcheck(L, s != NULL, 1, "invalid user data");

    if (s){
        delete *s;
    }

    return 0;
}

int luaopen_student_libs(lua_State* L)
{
    //创建全局元表（里面包含了对LUA_REGISTRYINDEX的操作），元表的位置为-1
    luaL_newmetatable(L, "StudentClass");

    //将元表作为一个副本压栈到位置-1，原元表位置-2
    lua_pushvalue(L, -1);

    //设置-2位置元表的__index索引的值为位置-1的元表，并弹出位置-1的元表，原元表的位置为-1
    lua_setfield(L, -2, "__index");

    //将成员函数注册到元表中（到这里，全局元表的设置就全部完成了）
    luaL_setfuncs(L, lua_reg_student_member_funcs, 0);

    //注册构造函数到新表中，并返回给Lua
    luaL_newlib(L, lua_reg_student_constructor_funcs);

    return 1;
}
```

六.hello.lua文件

```lua
local student_obj = Student.create()
student_obj:set_name("Jack")
student_obj:print()

--使用内部的__tostring函数进行打印
print(student_obj)

--下面的代码也是可行的
--student_obj.set_name(student_obj,"Jack")
--student_obj.print(student_obj)

--让其进行自动gc
student_obj = nil

--手动强制gc
--collectgarbage("collect")
```

<hr>

#### <p>原文出处：<a href='https://cloud.tencent.com/developer/ask/122232' target='blank'>如何创建一个安全的Lua沙盒</a></p>

```lua
-- save a pointer to globals that would be unreachable in sandbox
local e = _ENV

-- sample sandbox environment
sandbox_env = {
  ipairs = ipairs,
  next = next,
  pairs = pairs,
  pcall = pcall,
  tonumber = tonumber,
  tostring = tostring,
  type = type,
  unpack = unpack,
  coroutine = { create = coroutine.create, resume = coroutine.resume, 
      running = coroutine.running, status = coroutine.status, 
      wrap = coroutine.wrap },
  string = { byte = string.byte, char = string.char, find = string.find, 
      format = string.format, gmatch = string.gmatch, gsub = string.gsub, 
      len = string.len, lower = string.lower, match = string.match, 
      rep = string.rep, reverse = string.reverse, sub = string.sub, 
      upper = string.upper },
  table = { insert = table.insert, maxn = table.maxn, remove = table.remove, 
      sort = table.sort },
  math = { abs = math.abs, acos = math.acos, asin = math.asin, 
      atan = math.atan, atan2 = math.atan2, ceil = math.ceil, cos = math.cos, 
      cosh = math.cosh, deg = math.deg, exp = math.exp, floor = math.floor, 
      fmod = math.fmod, frexp = math.frexp, huge = math.huge, 
      ldexp = math.ldexp, log = math.log, log10 = math.log10, max = math.max, 
      min = math.min, modf = math.modf, pi = math.pi, pow = math.pow, 
      rad = math.rad, random = math.random, sin = math.sin, sinh = math.sinh, 
      sqrt = math.sqrt, tan = math.tan, tanh = math.tanh },
  os = { clock = os.clock, difftime = os.difftime, time = os.time },
}

function run_sandbox(sb_env, sb_func, ...)
  local sb_orig_env = _ENV
  if (not sb_func) then return nil end
  _ENV = sb_env
  local sb_ret = {e.pcall(sb_func, ...)}
  _ENV = sb_orig_env
  return e.table.unpack(sb_ret)
end


--[[
pcall_rc, result_or_err_msg = run_sandbox(sandbox_env, my_func, arg1, arg2)
--]]
```