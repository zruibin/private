 
<!--BEGIN_DATA
{
    "create_date": "2019-12-21 15:45", 
    "modify_date": "2019-12-21 15:45", 
    "is_top": "0", 
    "summary": "微软VSCode IDE源码分析揭秘", 
    "tags": "工具", 
    "file_name": "微软VSCode_IDE源码分析揭秘.md"
}
END_DATA-->

####<p>原文出处：<a href='' target='blank'>微软 VSCode IDE 源码分析揭秘</a></p>

![](./image/20191221-154600.webp)

###目录

  * (1)简介
  * (2)技术架构
  * (3)启动主进程
  * (4)实例化服务
  * (5)事件分发
  * (6)进程通信
  * (7)主要窗口
  * (8)开发调试

###1.简介

Visual Studio Code(简称 VSCode) 是开源免费的 IDE 编辑器，原本是微软内部使用的云编辑器(Monaco)。

git 仓库地址：https://github.com/microsoft/vscode

通过 Eletron 集成了桌面应用，可以跨平台使用，开发语言主要采用微软自家的 TypeScript。  
整个项目结构比较清晰，方便阅读代码理解。成为了最流行跨平台的桌面 IDE 应用

微软希望 VSCode 在保持核心轻量级的基础上，增加项目支持，智能感知，编译调试。

![](./image/20191221-154601.webp)

###编译安装

下载最新版本,目前我用的是 1.37.1 版本  
官方的 wiki 中有编译安装的说明 [How to Contribute](https://github.com/microsoft/vscode/wiki/How-to-Contribute?_blank)

Linux, Window, MacOS 三个系统编译时有些差别，参考官方文档，在编译安装依赖时如果遇到 connect timeout, 需要进行科学上网。

> 需要注意的一点 运行环境依赖版本 Nodejs x64 version >= 10.16.0, < 11.0.0, python 2.7(3.0不能正常执行)

###2.技术架构

![](./image/20191221-154602.webp)

####Electron

> [Electron](https://electronjs.org/?_blank) 是一个使用 JavaScript, HTML 和 CSS 等Web 技术创建原生程序的框架，它负责比较难搞的部分，你只需把精力放在你的应用的核心上即可 (Electron = Node.js + Chromium + Native API)

####Monaco Editor

> [Monaco Editor](https://github.com/microsoft/monaco-editor?_blank)是微软开源项目, 为VS Code 提供支持的代码编辑器，运行在浏览器环境中。编辑器提供代码提示，智能建议等功能。供开发人员远程更方便的编写代码，可独立运行。

####TypeScript

> [TypeScript](http://www.typescriptlang.org/)是一种由微软开发的自由和开源的编程语言。它是JavaScript 的一个超集，而且本质上向这个语言添加了可选的静态类型和基于类的面向对象编程

###目录结构

    
    
    ├── build         ##gulp编译构建脚本  
    ├── extensions    ##内置插件  
    ├── product.json  ##App meta信息  
    ├── resources     ##平台相关静态资源  
    ├── scripts       ##工具脚本，开发/测试  
    ├── src           ##源码目录  
    └── typings       ##函数语法补全定义  
    └── vs  
        ├── base        ##通用工具/协议和UI库  
        │   ├── browser ##基础UI组件，DOM操作  
        │   ├── common  ##diff描述，markdown解析器，worker协议，各种工具函数  
        │   ├── node    ##Node工具函数  
        │   ├── parts   ##IPC协议（Electron、Node），quickopen、tree组件  
        │   ├── test    ##base单测用例  
        │   └── worker  ##Worker factory和main Worker（运行IDE Core：Monaco）  
        ├── code        ##VSCode主运行窗口  
        ├── editor        ##IDE代码编辑器  
        |   ├── browser     ##代码编辑器核心  
        |   ├── common      ##代码编辑器核心  
        |   ├── contrib     ##vscode 与独立 IDE共享的代码  
        |   └── standalone  ##独立 IDE 独有的代码  
        ├── platform      ##支持注入服务和平台相关基础服务（文件、剪切板、窗体、状态栏）  
        ├── workbench     ##工作区UI布局，功能主界面  
        │   ├── api              ####
        │   ├── browser          ####
        │   ├── common           ####
        │   ├── contrib          ####
        │   ├── electron-browser ####
        │   ├── services         ####
        │   └── test             ####
        ├── css.build.js  ##用于插件构建的CSS loader  
        ├── css.js        ##CSS loader  
        ├── editor        ##对接IDE Core（读取编辑/交互状态），提供命令、上下文菜单、hover、snippet等支持  
        ├── loader.js     ##AMD loader（用于异步加载AMD模块）  
        ├── nls.build.js  ##用于插件构建的NLS loader  
        └── nls.js        ##NLS（National Language Support）多语言loader  
    

####核心层

  * base: 提供通用服务和构建用户界面

  * platform: 注入服务和基础服务代码

  * editor: 微软 Monaco 编辑器，也可独立运行使用

  * wrokbench: 配合 Monaco 并且给 viewlets 提供框架：如：浏览器状态栏，菜单栏利用 electron 实现桌面程序

####核心环境

整个项目完全使用 typescript 实现，electron 中运行主进程和渲染进程，使用的 api 有所不同，所以在 core 中每个目录组织也是按照使用的 api 来安排，运行的环境分为几类：

  * common: 只使用 javascritp api 的代码，能在任何环境下运行
  * browser: 浏览器 api, 如操作 dom; 可以调用 common
  * node: 需要使用 node 的 api,比如文件 io 操作
  * electron-brower: 渲染进程 api, 可以调用 common, brower, node, 依赖[electron renderer-process API](https://github.com/electron/electron/tree/master/docs#modules-for-the-renderer-process-web-page)
  * electron-main: 主进程 api, 可以调用: common, node 依赖于[electron main-process AP](https://github.com/electron/electron/tree/master/docs#modules-for-the-main-process)

![](./image/20191221-154603.webp)

###3.启动主进程

####Electron 通过 package.json 中的 main 字段来定义应用入口。

main.js 是 vscode 的入口。

  * src/main.js  
_ vs/code/electron-main/main.ts  
_ vs/code/electron-main/app.ts  
_ vs/code/electron-main/windows.ts  
_ vs/workbench/electron-browser/desktop.main.ts *
vs/workbench/browser/workbench.ts


```
{app.once('ready', function () {  
          //启动追踪，后面会讲到，跟性能检测优化相关。  
          if (args['trace']) {  
              // @ts-ignore  
              const contentTracing = require('electron').contentTracing;  
        
              const traceOptions = {  
                  categoryFilter: args['trace-category-filter'] || '*',  
                  traceOptions: args['trace-options'] || 'record-until-full,enable-sampling'  
              };  
        
              contentTracing.startRecording(traceOptions, () => onReady());  
          } else {  
              onReady();  
          }  
      });  
      function onReady() {  
          perf.mark('main:appReady');  
        
          Promise.all([nodeCachedDataDir.ensureExists(), userDefinedLocale]).then(([cachedDataDir, locale]) => {  
              //1. 这里尝试获取本地配置信息，如果有的话会传递到startup  
              if (locale && !nlsConfiguration) {  
                  nlsConfiguration = lp.getNLSConfiguration(product.commit, userDataPath, metaDataFile, locale);  
              }  
        
              if (!nlsConfiguration) {  
                  nlsConfiguration = Promise.resolve(undefined);  
              }  
        
        
              nlsConfiguration.then(nlsConfig => {  
        
                  //4. 首先会检查用户语言环境配置，如果没有设置默认使用英语  
                  const startup = nlsConfig => {  
                      nlsConfig._languagePackSupport = true;  
                      process.env['VSCODE_NLS_CONFIG'] = JSON.stringify(nlsConfig);  
                      process.env['VSCODE_NODE_CACHED_DATA_DIR'] = cachedDataDir || '';  
        
                      perf.mark('willLoadMainBundle');  
                      //使用微软的loader组件加载electron-main/main文件  
                      require('./bootstrap-amd').load('vs/code/electron-main/main', () => {  
                          perf.mark('didLoadMainBundle');  
                      });  
                  };  
        
                  // 2. 接收到有效的配置传入是其生效，调用startup  
                  if (nlsConfig) {  
                      startup(nlsConfig);  
                  }  
        
                  // 3. 这里尝试使用本地的应用程序  
                  // 应用程序设置区域在ready事件后才有效  
                  else {  
                      let appLocale = app.getLocale();  
                      if (!appLocale) {  
                          startup({ locale: 'en', availableLanguages: {} });  
                      } else {  
        
                          // 配置兼容大小写敏感，所以统一转换成小写  
                          appLocale = appLocale.toLowerCase();  
                          // 这里就会调用config服务，把本地配置加载进来再调用startup  
                          lp.getNLSConfiguration(product.commit, userDataPath, metaDataFile, appLocale).then(nlsConfig => {  
                              if (!nlsConfig) {  
                                  nlsConfig = { locale: appLocale, availableLanguages: {} };  
                              }  
        
                              startup(nlsConfig);  
                          });  
                      }  
                  }  
              });  
          }, console.error);  
      }
  }
```  

####vs/code/electron-main/main.ts

electron-main/main 是程序真正启动的入口,进入 main process 初始化流程.

#####这里主要做了两件事情：

  1. 初始化 Service

  2. 启动主实例

直接看 startup 方法的实现,基础服务初始化完成后会加载 CodeApplication, mainIpcServer, instanceEnvironment，调用 startup 方法启动 APP

    
    
    private async startup(args: ParsedArgs): Promise<void> {  
      
            //spdlog 日志服务  
            const bufferLogService = new BufferLogService();  
      
            // 1. 调用 createServices  
            const [instantiationService, instanceEnvironment] = this.createServices(args, bufferLogService);  
            try {  
      
                // 1.1 初始化Service服务  
                await instantiationService.invokeFunction(async accessor => {  
                    // 基础服务，包括一些用户数据，缓存目录  
                    const environmentService = accessor.get(IEnvironmentService);  
                    // 配置服务  
                    const configurationService = accessor.get(IConfigurationService);  
                    // 持久化数据  
                    const stateService = accessor.get(IStateService);  
      
                    try {  
                        await this.initServices(environmentService, configurationService as ConfigurationService, stateService as StateService);  
                    } catch (error) {  
      
                        // 抛出错误对话框  
                        this.handleStartupDataDirError(environmentService, error);  
      
                        throw error;  
                    }  
                });  
      
                // 1.2 启动实例  
                await instantiationService.invokeFunction(async accessor => {  
                    const environmentService = accessor.get(IEnvironmentService);  
                    const logService = accessor.get(ILogService);  
                    const lifecycleService = accessor.get(ILifecycleService);  
                    const configurationService = accessor.get(IConfigurationService);  
      
                    const mainIpcServer = await this.doStartup(logService, environmentService, lifecycleService, instantiationService, true);  
      
                    bufferLogService.logger = new SpdLogService('main', environmentService.logsPath, bufferLogService.getLevel());  
                    once(lifecycleService.onWillShutdown)(() => (configurationService as ConfigurationService).dispose());  
      
                    return instantiationService.createInstance(CodeApplication, mainIpcServer, instanceEnvironment).startup();  
                });  
            } catch (error) {  
                instantiationService.invokeFunction(this.quit, error);  
            }  
        }  


####Service

这里通过 createService 创建一些基础的 Service

####运行环境服务 EnvironmentService

src/vs/platform/environment/node/environmentService.ts

通过这个服务获取当前启动目录，日志目录，操作系统信息，配置文件目录，用户目录等。

####日志服务 MultiplexLogService

src/vs/platform/log/common/log.ts

默认使用控制台日志 ConsoleLogMainService其中包含性能追踪和释放信息，日志输出级别

####配置服务 ConfigurationService

src/vs/platform/configuration/node/configurationService.ts

从运行环境服务获取内容

####生命周期服务 LifecycleService

src/vs/platform/lifecycle/common/lifecycleService.ts

监听事件，electron app 模块 比如：ready， window-all-closed，before-quit

可以参考官方[electron app 文档](https://www.w3cschool.cn/electronmanual/electronmanual-electronapp.html)

####状态服务 StateService

src/vs/platform/state/node/stateService.ts

通过 FileStorage 读写 storage.json 存储，里记录一些与程序运行状态有关的键值对

####请求服务 RequestService

src/vs/platform/request/browser/requestService.ts

这里使用的是原生 ajax 请求，实现了 request 方法

####主题服务 ThemeMainService

src/vs/platform/theme/electron-main/themeMainService.ts

这里只设置背景颜色，通过 getBackgroundColor 方法 IStateService 存储

####签名服务 SignService

src/vs/platform/sign/node/signService.ts

    
    
    private createServices(args: ParsedArgs, bufferLogService: BufferLogService): [IInstantiationService, typeof process.env] {  
      
        //服务注册容器  
        const services = new ServiceCollection();  
      
        const environmentService = new EnvironmentService(args, process.execPath);  
        const instanceEnvironment = this.patchEnvironment(environmentService); // Patch `process.env` with the instance's environment  
        services.set(IEnvironmentService, environmentService);  
      
        const logService = new MultiplexLogService([new ConsoleLogMainService(getLogLevel(environmentService)), bufferLogService]);  
        process.once('exit', () => logService.dispose());  
        //日志服务  
        services.set(ILogService, logService);  
        //配置服务  
        services.set(IConfigurationService, new ConfigurationService(environmentService.settingsResource));  
        //生命周期  
        services.set(ILifecycleService, new SyncDescriptor(LifecycleService));  
        //状态存储  
        services.set(IStateService, new SyncDescriptor(StateService));  
        //网络请求  
        services.set(IRequestService, new SyncDescriptor(RequestService));  
        //主题设定  
        services.set(IThemeMainService, new SyncDescriptor(ThemeMainService));  
        //签名服务  
        services.set(ISignService, new SyncDescriptor(SignService));  
      
        return [new InstantiationService(services, true), instanceEnvironment];  
    }  


###4.实例化服务

SyncDescriptor 负责注册这些服务，当用到该服务时进程实例化使用

src/vs/platform/instantiation/common/descriptors.ts

    
    export class SyncDescriptor<T> {  
        readonly ctor: any;  
        readonly staticArguments: any[];  
        readonly supportsDelayedInstantiation: boolean;  
        constructor(ctor: new (...args: any[]) => T, staticArguments: any[] = [], supportsDelayedInstantiation: boolean = false) {  
            this.ctor = ctor;  
            this.staticArguments = staticArguments;  
            this.supportsDelayedInstantiation = supportsDelayedInstantiation;  
        }  
    }  
    

main.ts 中 startup 方法调用 invokeFunction.get 实例化服务
    
    
    await instantiationService.invokeFunction(async accessor => {  
        const environmentService = accessor.get(IEnvironmentService);  
        const configurationService = accessor.get(IConfigurationService);  
        const stateService = accessor.get(IStateService);  
        try {  
            await this.initServices(environmentService, configurationService as ConfigurationService, stateService as StateService);  
        } catch (error) {  
      
            // Show a dialog for errors that can be resolved by the user  
            this.handleStartupDataDirError(environmentService, error);  
      
            throw error;  
        }  
    });  
    

get 方法调用_getOrCreateServiceInstance，这里第一次创建会存入缓存中下次实例化对象时会优先从缓存中获取对象。

src/vs/platform/instantiation/common/instantiationService.ts

    
    
    invokeFunction<R, TS extends any[] = []>(fn: (accessor: ServicesAccessor, ...args: TS) => R, ...args: TS): R {  
        let _trace = Trace.traceInvocation(fn);  
        let _done = false;  
        try {  
            const accessor: ServicesAccessor = {  
                get: <T>(id: ServiceIdentifier<T>, isOptional?: typeof optional) => {  
      
                    if (_done) {  
                        throw illegalState('service accessor is only valid during the invocation of its target method');  
                    }  
      
                    const result = this._getOrCreateServiceInstance(id, _trace);  
                    if (!result && isOptional !== optional) {  
                        throw new Error(`[invokeFunction] unknown service '${id}'`);  
                    }  
                    return result;  
                }  
            };  
            return fn.apply(undefined, [accessor, ...args]);  
        } finally {  
            _done = true;  
            _trace.stop();  
        }  
    }  
    private _getOrCreateServiceInstance<T>(id: ServiceIdentifier<T>, _trace: Trace): T {  
        let thing = this._getServiceInstanceOrDescriptor(id);  
        if (thing instanceof SyncDescriptor) {  
            return this._createAndCacheServiceInstance(id, thing, _trace.branch(id, true));  
        } else {  
            _trace.branch(id, false);  
            return thing;  
        }  
    }  
    

#####vs/code/electron-main/app.ts

这里首先触发 CodeApplication.startup()方法， 在第一个窗口打开 3 秒后成为共享进程，

    
    
    async startup(): Promise<void> {  
        ...  
      
        // 1. 第一个窗口创建共享进程  
        const sharedProcess = this.instantiationService.createInstance(SharedProcess, machineId, this.userEnv);  
        const sharedProcessClient = sharedProcess.whenReady().then(() => connect(this.environmentService.sharedIPCHandle, 'main'));  
        this.lifecycleService.when(LifecycleMainPhase.AfterWindowOpen).then(() => {  
            this._register(new RunOnceScheduler(async () => {  
                const userEnv = await getShellEnvironment(this.logService, this.environmentService);  
      
                sharedProcess.spawn(userEnv);  
            }, 3000)).schedule();  
        });  
        // 2. 创建app实例  
        const appInstantiationService = await this.createServices(machineId, trueMachineId, sharedProcess, sharedProcessClient);  
      
      
        // 3. 打开一个窗口 调用  
      
        const windows = appInstantiationService.invokeFunction(accessor => this.openFirstWindow(accessor, electronIpcServer, sharedProcessClient));  
      
        // 4. 窗口打开后执行生命周期和授权操作  
        this.afterWindowOpen();  
        ...  
      
        //vscode结束了性能问题的追踪  
        if (this.environmentService.args.trace) {  
            this.stopTracingEventually(windows);  
        }  
    }  
    

openFirstWindow 主要实现CodeApplication.openFirstWindow 首次开启窗口时，创建 Electron 的 IPC，使主进程和渲染进程间通信。  

window 会被注册到 sharedProcessClient，主进程和共享进程通信根据 environmentService 提供的参数(path,uri)调用 windowsMainService.open 方法打开窗口

    
    
    private openFirstWindow(accessor: ServicesAccessor, electronIpcServer: ElectronIPCServer, sharedProcessClient: Promise<Client<string>>): ICodeWindow[] {  
      
            ...  
            // 1. 注入Electron IPC Service, windows窗口管理，菜单栏等服务  
      
            // 2. 根据environmentService进行参数配置  
            const macOpenFiles: string[] = (<any>global).macOpenFiles;  
            const context = !!process.env['VSCODE_CLI'] ? OpenContext.CLI : OpenContext.DESKTOP;  
            const hasCliArgs = hasArgs(args._);  
            const hasFolderURIs = hasArgs(args['folder-uri']);  
            const hasFileURIs = hasArgs(args['file-uri']);  
            const noRecentEntry = args['skip-add-to-recently-opened'] === true;  
            const waitMarkerFileURI = args.wait && args.waitMarkerFilePath ? URI.file(args.waitMarkerFilePath) : undefined;  
      
            ...  
      
            // 打开主窗口，默认从执行命令行中读取参数  
            return windowsMainService.open({  
                context,  
                cli: args,  
                forceNewWindow: args['new-window'] || (!hasCliArgs && args['unity-launch']),  
                diffMode: args.diff,  
                noRecentEntry,  
                waitMarkerFileURI,  
                gotoLineMode: args.goto,  
                initialStartup: true  
            });  
        }  
    

#####vs/code/electron-main/windows.ts

接下来到了 electron 的 windows 窗口，open 方法在 doOpen 中执行窗口配置初始化，最终调用openInBrowserWindow -> 执行 doOpenInBrowserWindow 是其打开 window,主要步骤如下：

    
    private openInBrowserWindow(options: IOpenBrowserWindowOptions): ICodeWindow {  
      
        ...  
        // New window  
        if (!window) {  
            //1.判断是否全屏创建窗口  
             ...  
            // 2. 创建实例窗口  
            window = this.instantiationService.createInstance(CodeWindow, {  
                state,  
                extensionDevelopmentPath: configuration.extensionDevelopmentPath,  
                isExtensionTestHost: !!configuration.extensionTestsPath  
            });  
      
            // 3.添加到当前窗口控制器  
            WindowsManager.WINDOWS.push(window);  
      
            // 4.窗口监听器  
            window.win.webContents.removeAllListeners('devtools-reload-page'); // remove built in listener so we can handle this on our own  
            window.win.webContents.on('devtools-reload-page', () => this.reload(window!));  
            window.win.webContents.on('crashed', () => this.onWindowError(window!, WindowError.CRASHED));  
            window.win.on('unresponsive', () => this.onWindowError(window!, WindowError.UNRESPONSIVE));  
            window.win.on('closed', () => this.onWindowClosed(window!));  
      
            // 5.注册窗口生命周期  
            (this.lifecycleService as LifecycleService).registerWindow(window);  
        }  
      
        ...  
      
        return window;  
    }  
    

doOpenInBrowserWindow 会调用 window.load 方法 在 window.ts 中实现
    
    
    load(config: IWindowConfiguration, isReload?: boolean, disableExtensions?: boolean): void {  
      
        ...  
      
        // Load URL  
        perf.mark('main:loadWindow');  
        this._win.loadURL(this.getUrl(configuration));  
      
        ...  
    }  
      
    private getUrl(windowConfiguration: IWindowConfiguration): string {  
      
        ...  
        //加载欢迎屏幕的html  
        let configUrl = this.doGetUrl(config);  
        ...  
        return configUrl;  
    }  
      
    //默认加载 vs/code/electron-browser/workbench/workbench.html  
    private doGetUrl(config: object): string {  
        return `${require.toUrl('vs/code/electron-browser/workbench/workbench.html')}?config=${encodeURIComponent(JSON.stringify(config))}`;  
    }  
    

main process 的使命完成, 主界面进行构建布局。

在 workbench.html 中加载了 workbench.js，这里调用 return require('vs/workbench/electron-browser/desktop.main').main(configuration);实现对主界面的展示

#####vs/workbench/electron-browser/desktop.main.ts

创建工作区，调用 workbench.startup()方法，构建主界面展示布局
    
    
    ...  
    async open(): Promise<void> {  
        const services = await this.initServices();  
        await domContentLoaded();  
        mark('willStartWorkbench');  
      
        // 1.创建工作区  
        const workbench = new Workbench(document.body, services.serviceCollection, services.logService);  
      
        // 2.监听窗口变化  
        this._register(addDisposableListener(window, EventType.RESIZE, e => this.onWindowResize(e, true, workbench)));  
      
        // 3.工作台生命周期  
        this._register(workbench.onShutdown(() => this.dispose()));  
        this._register(workbench.onWillShutdown(event => event.join(services.storageService.close())));  
      
        // 3.启动工作区  
        const instantiationService = workbench.startup();  
      
        ...  
    }  
    ...  

#####vs/workbench/browser/workbench.ts

工作区继承自 layout 类，主要作用是构建工作区，创建界面布局。
    
    
    export class Workbench extends Layout {  
        ...  
        startup(): IInstantiationService {  
            try {  
                ...  
      
                // Services  
                const instantiationService = this.initServices(this.serviceCollection);  
      
                instantiationService.invokeFunction(async accessor => {  
                    const lifecycleService = accessor.get(ILifecycleService);  
                    const storageService = accessor.get(IStorageService);  
                    const configurationService = accessor.get(IConfigurationService);  
      
                    // Layout  
                    this.initLayout(accessor);  
      
                    // Registries  
                    this.startRegistries(accessor);  
      
                    // Context Keys  
                    this._register(instantiationService.createInstance(WorkbenchContextKeysHandler));  
      
                    // 注册监听事件  
                    this.registerListeners(lifecycleService, storageService, configurationService);  
      
                    // 渲染工作区  
                    this.renderWorkbench(instantiationService, accessor.get(INotificationService) as NotificationService, storageService, configurationService);  
      
                    // 创建工作区布局  
                    this.createWorkbenchLayout(instantiationService);  
      
                    // 布局构建  
                    this.layout();  
      
                    // Restore  
                    try {  
                        await this.restoreWorkbench(accessor.get(IEditorService), accessor.get(IEditorGroupsService), accessor.get(IViewletService), accessor.get(IPanelService), accessor.get(ILogService), lifecycleService);  
                    } catch (error) {  
                        onUnexpectedError(error);  
                    }  
                });  
      
                return instantiationService;  
            } catch (error) {  
                onUnexpectedError(error);  
      
                throw error; // rethrow because this is a critical issue we cannot handle properly here  
            }  
        }  
        ...  
    }  
    

###5.事件分发

####event

src/vs/base/common/event.ts

程序中常见使用 once 方法进行事件绑定, 给定一个事件，返回一个只触发一次的事件，放在匿名函数返回
    
    
    export function once<T>(event: Event<T>): Event<T> {  
        return (listener, thisArgs = null, disposables?) => {  
            // 设置次变量，防止事件重复触发造成事件污染  
            let didFire = false;  
            let result: IDisposable;  
            result = event(e => {  
                if (didFire) {  
                    return;  
                } else if (result) {  
                    result.dispose();  
                } else {  
                    didFire = true;  
                }  
      
                return listener.call(thisArgs, e);  
            }, null, disposables);  
      
            if (didFire) {  
                result.dispose();  
            }  
      
            return result;  
        };  
    }  
    

循环派发了所有注册的事件， 事件会存储到一个事件队列，通过 fire 方法触发事件

private _deliveryQueue?: LinkedList<[Listener, T]>;//事件存储队列
    
    
    fire(event: T): void {  
        if (this._listeners) {  
            // 将所有事件传入 delivery queue  
            // 内部/嵌套方式通过emit发出.  
            // this调用事件驱动  
      
            if (!this._deliveryQueue) {  
                this._deliveryQueue = new LinkedList();  
            }  
      
            for (let iter = this._listeners.iterator(), e = iter.next(); !e.done; e = iter.next()) {  
                this._deliveryQueue.push([e.value, event]);  
            }  
      
            while (this._deliveryQueue.size > 0) {  
                const [listener, event] = this._deliveryQueue.shift()!;  
                try {  
                    if (typeof listener === 'function') {  
                        listener.call(undefined, event);  
                    } else {  
                        listener[0].call(listener[1], event);  
                    }  
                } catch (e) {  
                    onUnexpectedError(e);  
                }  
            }  
        }  
    }  
    

###6.进程通信

####主进程

src/vs/code/electron-main/main.ts

main.ts 在启动应用后就创建了一个主进程 main process，它可以通过 electron 中的一些模块直接与原生 GUI 交互。

    
    server = await serve(environmentService.mainIPCHandle);  
    once(lifecycleService.onWillShutdown)(() => server.dispose());  
    

####渲染进程

仅启动主进程并不能给你的应用创建应用窗口。窗口是通过 main 文件里的主进程调用叫 BrowserWindow 的模块创建的。

####主进程与渲染进程之间的通信

在 electron 中，主进程与渲染进程有很多通信的方法。比如 ipcRenderer 和 ipcMain，还可以在渲染进程使用 remote 模块。

####ipcMain & ipcRenderer

  * 主进程：ipcMain

  * 渲染进程：ipcRenderer

ipcMain 模块和 ipcRenderer 是类 EventEmitter 的实例。

在主进程中使用 ipcMain 接收渲染线程发送过来的异步或同步消息，发送过来的消息将触发事件。

在渲染进程中使用 ipcRenderer 向主进程发送同步或异步消息，也可以接收到主进程的消息。

  * 发送消息，事件名为 channel .

  * 回应同步消息, 你可以设置 event.returnValue .

  * 回应异步消息, 你可以使用 event.sender.send(…)

创建 IPC 服务  
src/vs/base/parts/ipc/node/ipc.net.ts

这里返回一个 promise 对象，成功则 createServer

    
    
    export function serve(hook: any): Promise<Server> {  
        return new Promise<Server>((c, e) => {  
            const server = createServer();  
      
            server.on('error', e);  
            server.listen(hook, () => {  
                server.removeListener('error', e);  
                c(new Server(server));  
            });  
        });  
    }  
    

#####创建信道

src/vs/code/electron-main/app.ts

  * mainIpcServer * launchChannel

  * electronIpcServer  
_ updateChannel  
_ issueChannel  
_ workspacesChannel  
_ windowsChannel  
_ menubarChannel  
_ urlChannel  
_ storageChannel  
_ logLevelChannel

    
```
private openFirstWindow(accessor: ServicesAccessor, electronIpcServer: ElectronIPCServer, sharedProcessClient: Promise<Client<string>>): ICodeWindow[] {  
  
        // Register more Main IPC services  
        const launchService = accessor.get(ILaunchService);  
        const launchChannel = new LaunchChannel(launchService);  
        this.mainIpcServer.registerChannel('launch', launchChannel);  
  
        // Register more Electron IPC services  
        const updateService = accessor.get(IUpdateService);  
        const updateChannel = new UpdateChannel(updateService);  
        electronIpcServer.registerChannel('update', updateChannel);  
  
        const issueService = accessor.get(IIssueService);  
        const issueChannel = new IssueChannel(issueService);  
        electronIpcServer.registerChannel('issue', issueChannel);  
  
        const workspacesService = accessor.get(IWorkspacesMainService);  
        const workspacesChannel = new WorkspacesChannel(workspacesService);  
        electronIpcServer.registerChannel('workspaces', workspacesChannel);  
  
        const windowsService = accessor.get(IWindowsService);  
        const windowsChannel = new WindowsChannel(windowsService);  
        electronIpcServer.registerChannel('windows', windowsChannel);  
        sharedProcessClient.then(client => client.registerChannel('windows', windowsChannel));  
  
        const menubarService = accessor.get(IMenubarService);  
        const menubarChannel = new MenubarChannel(menubarService);  
        electronIpcServer.registerChannel('menubar', menubarChannel);  
  
        const urlService = accessor.get(IURLService);  
        const urlChannel = new URLServiceChannel(urlService);  
        electronIpcServer.registerChannel('url', urlChannel);  
  
        const storageMainService = accessor.get(IStorageMainService);  
        const storageChannel = this._register(new GlobalStorageDatabaseChannel(this.logService, storageMainService));  
        electronIpcServer.registerChannel('storage', storageChannel);  
  
        // Log level management  
        const logLevelChannel = new LogLevelSetterChannel(accessor.get(ILogService));  
        electronIpcServer.registerChannel('loglevel', logLevelChannel);  
        sharedProcessClient.then(client => client.registerChannel('loglevel', logLevelChannel));  
  
        ...  
  
        // default: read paths from cli  
        return windowsMainService.open({  
            context,  
            cli: args,  
            forceNewWindow: args['new-window'] || (!hasCliArgs && args['unity-launch']),  
            diffMode: args.diff,  
            noRecentEntry,  
            waitMarkerFileURI,  
            gotoLineMode: args.goto,  
            initialStartup: true  
        });  
}  
```  

每一个信道，内部实现两个方法 listen 和 call

例如：src/vs/platform/localizations/node/localizationsIpc.ts

构造函数绑定事件

    
    
    export class LocalizationsChannel implements IServerChannel {  
      
        onDidLanguagesChange: Event<void>;  
      
        constructor(private service: ILocalizationsService) {  
            this.onDidLanguagesChange = Event.buffer(service.onDidLanguagesChange, true);  
        }  
      
        listen(_: unknown, event: string): Event<any> {  
            switch (event) {  
                case 'onDidLanguagesChange': return this.onDidLanguagesChange;  
            }  
      
            throw new Error(`Event not found: ${event}`);  
        }  
      
        call(_: unknown, command: string, arg?: any): Promise<any> {  
            switch (command) {  
                case 'getLanguageIds': return this.service.getLanguageIds(arg);  
            }  
      
            throw new Error(`Call not found: ${command}`);  
        }  
    }  
    

###7.主要窗口

workbench.ts 中 startup 里面 Workbench 负责创建主界面  
src/vs/workbench/browser/workbench.ts

    
    
    startup(): IInstantiationService {  
        try {  
      
            ...  
      
            instantiationService.invokeFunction(async accessor => {  
      
                // 渲染主工作界面  
                this.renderWorkbench(instantiationService, accessor.get(INotificationService) as NotificationService, storageService, configurationService);  
      
                // 界面布局  
                this.createWorkbenchLayout(instantiationService);  
      
                // Layout  
                this.layout();  
      
                // Restore  
                try {  
                    await this.restoreWorkbench(accessor.get(IEditorService), accessor.get(IEditorGroupsService), accessor.get(IViewletService), accessor.get(IPanelService), accessor.get(ILogService), lifecycleService);  
                } catch (error) {  
                    onUnexpectedError(error);  
                }  
            });  
      
            return instantiationService;  
        } catch (error) {  
            onUnexpectedError(error);  
      
            throw error; // rethrow because this is a critical issue we cannot handle properly here  
        }  
    }  
    

渲染主工作台，渲染完之后加入到 container 中，container 加入到 parent, parent 就是 body 了。

this.parent.appendChild(this.container);
    
    
    private renderWorkbench(instantiationService: IInstantiationService, notificationService: NotificationService, storageService: IStorageService, configurationService: IConfigurationService): void {  
      
            ...  
      
            //TITLEBAR_PART 顶部操作栏  
            //ACTIVITYBAR_PART 最左侧菜单选项卡  
            //SIDEBAR_PART 左侧边栏，显示文件，结果展示等  
            //EDITOR_PART 右侧窗口，代码编写,欢迎界面等  
            //STATUSBAR_PART 底部状态栏  
            [  
                { id: Parts.TITLEBAR_PART, role: 'contentinfo', classes: ['titlebar'] },  
                { id: Parts.ACTIVITYBAR_PART, role: 'navigation', classes: ['activitybar', this.state.sideBar.position === Position.LEFT ? 'left' : 'right'] },  
                { id: Parts.SIDEBAR_PART, role: 'complementary', classes: ['sidebar', this.state.sideBar.position === Position.LEFT ? 'left' : 'right'] },  
                { id: Parts.EDITOR_PART, role: 'main', classes: ['editor'], options: { restorePreviousState: this.state.editor.restoreEditors } },  
                { id: Parts.PANEL_PART, role: 'complementary', classes: ['panel', this.state.panel.position === Position.BOTTOM ? 'bottom' : 'right'] },  
                { id: Parts.STATUSBAR_PART, role: 'contentinfo', classes: ['statusbar'] }  
            ].forEach(({ id, role, classes, options }) => {  
                const partContainer = this.createPart(id, role, classes);  
      
                if (!configurationService.getValue('workbench.useExperimentalGridLayout')) {  
                    // TODO@Ben cleanup once moved to grid  
                    // Insert all workbench parts at the beginning. Issue #52531  
                    // This is primarily for the title bar to allow overriding -webkit-app-region  
                    this.container.insertBefore(partContainer, this.container.lastChild);  
                }  
      
                this.getPart(id).create(partContainer, options);  
            });  
      
            // 将工作台添加至container dom渲染  
            this.parent.appendChild(this.container);  
        }  
    

workbench 最后调用 this.layout()方法，将窗口占据整个界面，渲染完成

    
    
    layout(options?: ILayoutOptions): void {  
            if (!this.disposed) {  
                this._dimension = getClientArea(this.parent);  
      
                if (this.workbenchGrid instanceof Grid) {  
                    position(this.container, 0, 0, 0, 0, 'relative');  
                    size(this.container, this._dimension.width, this._dimension.height);  
      
                    // Layout the grid widget  
                    this.workbenchGrid.layout(this._dimension.width, this._dimension.height);  
                } else {  
                    this.workbenchGrid.layout(options);  
                }  
      
                // Emit as event  
                this._onLayout.fire(this._dimension);  
            }  
        }  
    

###8.开发调试

    
    
    app.once('ready', function () {  
        //启动追踪  
        if (args['trace']) {  
            // @ts-ignore  
            const contentTracing = require('electron').contentTracing;  
      
            const traceOptions = {  
                categoryFilter: args['trace-category-filter'] || '*',  
                traceOptions: args['trace-options'] || 'record-until-full,enable-sampling'  
            };  
      
            contentTracing.startRecording(traceOptions, () => onReady());  
        } else {  
            onReady();  
        }  
    });  
    

####启动追踪

这里如果传入 trace 参数，在 onReady 启动之前会调用 chromium 的收集跟踪数据，提供的底层的追踪工具允许我们深度了解 V8 的解析以及其他时间消耗情况，

一旦收到可以开始记录的请求，记录将会立马启动并且在子进程是异步记录听的. 当所有的子进程都收到 startRecording 请求的时候，callback 将会被调用.

categoryFilter 是一个过滤器，它用来控制那些分类组应该被用来查找.过滤器应当有一个可选的 -前缀来排除匹配的分类组.不允许同一个列表既是包含又是排斥.

#####contentTracing.startRecording(options, callback)

  * options Object  
_ categoryFilter String  
_ traceOptions String

  * callback Function

[关于 trace 的详细介绍](https://www.w3cschool.cn/electronmanual/electronmanual-content-tracing.html)
  

####结束追踪

#####contentTracing.stopRecording(resultFilePath, callback)

  * resultFilePath String

  * callback Function  
在成功启动窗口后，程序结束性能追踪，停止对所有子进程的记录.

子进程通常缓存查找数据，并且仅仅将数据截取和发送给主进程.这有利于在通过 IPC 发送查找数据之前减小查找时的运行开销，这样做很有价值.因此，发送查找数据，我们应当异步通知所有子进程来截取任何待查找的数据.

一旦所有子进程接收到了 stopRecording 请求，将调用 callback ，并且返回一个包含查找数据的文件.

如果 resultFilePath 不为空，那么将把查找数据写入其中，否则写入一个临时文件.实际文件路径如果不为空，则将调用 callback .

####debug

调试界面在菜单栏找到 Help->Toggle Developers Tools

调出 Chrome 开发者调试工具进行调试

![](./image/20191221-154604.webp)

###参考

[https://electronjs.org/docs](https://electronjs.org/docs)

[https://github.com/microsoft/vscode/wiki/How-to-Contribute](https://github.com/microsoft/vscode/wiki/How-to-Contribute)

[https://github.com/Microsoft/vscode/wiki/Code-Organization](https://github.com/Microsoft/vscode/wiki/Code-Organization)

[http://xzper.com/2016/04/17/vscode%E6%BA%90%E7%A0%81%E5%89%96%E6%9E%90/](http://xzper.com/2016/04/17/vscode%E6%BA%90%E7%A0%81%E5%89%96%E6%9E%90/)

[http://www.ayqy.net/blog/vs-code%E6%BA%90%E7%A0%81%E7%AE%80%E6%9E%90/](http://www.ayqy.net/blog/vs-code%E6%BA%90%E7%A0%81%E7%AE%80%E6%9E%90/)

  