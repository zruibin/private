 
<!--BEGIN_DATA
{
    "create_date": "2020-03-21 15:19", 
    "modify_date": "2020-03-21 15:19", 
    "is_top": "0", 
    "summary": "App extension实战-Personal VPN连接并捕获packet", 
    "tags": "iOS、网络", 
    "file_name": "App extension实战-Personal VPN连接并捕获packet.md"
}
END_DATA-->

####<p>原文出处：<a href='https://juejin.im/post/5b2de89be51d4558a426ee45' target='blank'>App extension实战-Personal VPN连接并捕获packet</a></p>

####本例需求 : iOS建立简单的VPN连接并成功拦截IP数据包pakcet.

####建议：建议阅读本文前先仔细阅读并理解下App extension原理，有助于在项目中解决很多问题。[App extension总结]()

####注意：Personal-VPN功能是苹果开发者账号才有权限开启，所以如果没有开发者账号次Demo无法运行

本Demo中已经测试可以通过，只需要下载Demo并按照Demo中所说提供两个合法的bundle id即可运行。


#####GitHub地址(附代码) :[XDXVPNExtensionDemo](https://github.com/ChengyangLi/XDXVPNExtensionDemo)
#####简书地址 : [XDXVPNExtensionDemo](https://www.jianshu.com/p/bbdb439ab5e2)
#####博客地址 : [XDXVPNExtensionDemo](https://xiaodongxie1024.github.io/2018/06/23/20180623_vpn_extension/)
#####掘金地址 :[XDXVPNExtensionDemo](https://juejin.im/user/58ec343861ff4b00691b4f26/posts)

###一. App extension 定义及工作原理

#####1. App extension, 更多请了解[Appextension总结](https://juejin.im/post/5acefc0e6fb9a028e1205688)

  * 定义：App Extension 可以让开发者们拓展自定义的功能和内容到应用程序之外，并在用户与其他应用程序或系统交互时提供给用户。

  * 苹果定义了很多种app extension, 每一种不同功能的app extension 称为extension point,其中我们要学习的VPN Extension就是一种extension point。

###二. VPN extension 简介

#####1. 背景

我们先来简单了解一下国内墙的原理

![](./image/20200321-151937.webp)

![](./image/20200321-151938.webp)

#####2. 定义

苹果提供的VPN Extension可以帮助我们配置VPN通道，自定义和拓展核心网络功能。

苹果官方文档中定义如下

![](./image/20200321-151939.webp)

#####3.使用框架

NetworkExtension ：包含在iOS和macOS中用于自定义和拓展核心网络功能的API集合。

其中我们要讲的是NetworkExtension框架中的Personal VPN服务。

  * Personal VPN

NEVPNManager API提供给我们去创建和管理个人VPN的配置。它通常用来向用户提供服务确保用户安全的上网，例如使用公共场所的wifi。

#####4. 核心API

  * NETunnelProviderManager 和 NEPacketTunnelProvider

在 iOS 9 中，开发者可以用 NETunnelProvider 扩展核心网络层，从而实现非标准化的私密VPN技术。最重要的两个类是
NETunnelProviderManager 和 NEPacketTunnelProvider。

###二. VPN extension 创建步骤

#####1. 新建Target

在已经创建好的项目中新建Target

  * Target : 指定了应用程序中构建product的设置信息和文件,即包含App extension point的代码集合。

> Xcode会为每一种extension point提供一个模板，每种模板里会提供特定的源文件(源文件中会包含一些示例代码)和设置信息，build这个target将会生成一个指定的二进制文件被添加到app’s bundle中。

![](./image/20200321-151940.webp)

在弹出列表中选择Packet Tunnel Provider,注意在最新的Xcode中该模板已经被取消，需要我们手动下载，安装好后重启Xcode即可，这里提供下载链接链接:

    
    https://pan.baidu.com/s/1V3xIljdRedmqGyp5QSwbTA
    密码: ne8x

![](./image/20200321-151941.webp)

选择好后我们可以看到我们项目中的变化如下：

![](./image/20200321-151942.webp)

我们的项目中增加了对Target的配置，左侧项目工程文件中增加了系统为我们自动生成的模板，注意如果在新建Target时选择的是Ojective-C语言模板中有一处错误信息，因为与我们要实现的并无关联，模板中代码我们均不使用，忽略即可。

#####2. 删除模板中多余代码

由于我们这里只演示简单的建立连接的过程，所以模板中生成的很多代码使用不到，我们只需要留下如下代码。

    
    
    - (void)startTunnelWithOptions:(NSDictionary *)options completionHandler:(void (^)(NSError *))completionHandler
    {
    }

    - (void)stopTunnelWithReason:(NEProviderStopReason)reason completionHandler:(void (^)(void))completionHandler
    {
    	// Add code here to start the process of stopping the tunnel
    	[self.connection cancel];
    	completionHandler();
    }


在这里我们需要建立和断开连接的回调即可。此时Build通过。

#####3. 配置VPN所需信息

######3-1. 配置签名信息，开启权限

  * Personal-VPN功能是苹果开发者账号才有权限开启，所以如果没有开发者账号此Demo无法运行。

  ![](./image/20200321-151943.webp)

  * Bundle Identifier不可随意写，需要按照规范com.xxx.xxx形式来书写，否则Build会出错

  * 因为vpn extension并不是一个独立的app,所以创建target时前缀必须为主app的前缀再.extensionName.
    
    
    主app  Bundle Identifier : com.xdx.XDXRouterDemo.XDXVPNExtensionDemo
    extension Bundle Identifier : com.xdx.XDXRouterDemo.XDXVPNExtensionDemo.XDXVPNTunnelDemo


######3-2 开启权限

  * 因为personal vpn权限较高，不能直接在Xcode中打开，所以我们需要先登录[苹果开发者中心](https://developer.apple.com/)

  * 需要手动为主工程的target和vpn的target创建父子App ID。创建APP ID的方法网上较多，不再说明。

  * 在创建APP ID时打开Service 中的 Network Extensions 和 Personal VPN两个功能。对于已经创建好的APP ID需要在编辑中增加这两个Service。

> 注意：主target和extension target 对应的app id中都需要打开这两个权限。

  * 创建好APP ID后需要继续创建Profile文件，如果是已经存在的app id中增加了这两项服务后需要重新激活配置文件Profile。

######3-3 在Xcode中配置VPN

  * 在两个Target中选择正确的Profile。（前提是在3-2中正确配置了APP ID并开启了对应两项服务）由于我们只是测试，所以这里只配置了开发证书.
  * 在Capabilities中开启Personal VPN 和 Network Extension（同时如图勾选前三项），然后你的两个Target项目文件中会新增两个.entitlements结尾的配置文件。

  ![](./image/20200321-151944.webp)

#####4. 实现步骤

######4-1 导入必需框架

在项目中导入NetworkExtension.framework框架

![](./image/20200321-151945.webp)

之后在主控制器导入`#import <NetworkExtension/NetworkExtension.h>`

######4-1 初始化并配置NETunnelProviderManager对象

  * NETunnelProviderManager ：配置并控制由Tunnel Provider app extension提供的VPN 连接。

> 可以理解为建立VPN连接前负责配置基本参数信息保存设置到系统(即一般vpn app中都会在第一次打开时授权并保存到系统的VPN设置中)

  * 包含Packet Tunnel Provider extension的containing app使用NETunnelProviderManager去创建和管理使用自定义协议配置VPN。

#####注意：配置好的NETunnelProviderManager对象仅在系统设置中起展示作用，或者说这里的设置并不真正生效，真正生效的设置在app extension target中，如果为了保持一致，如果仅仅测试，配置信息可以随便填写（但target bundle id必须为项目target真实的ID），如果为了与vpn真正配置保持一致，可填写正确地址。

####知识点，了解可跳过

######知识点 1. 区别

######NETunnelProviderManager类继承了 NEVPNManager大多数基本的功能，主要的区别如下：

  * protocolConfiguration 属性只有 NETunnelProviderProtocol类才能设置
  * connection这个只读属性只能通过 NETunnelProviderSession这个类设置。

每个NETunnelProviderManager实例对应一个VPN配置被存储在 Network Extension偏好设置中。可以创建多个NETunnelProviderManager实例来管理多个VPN配置的。

使用NETunnelProviderManager创建的VPN配置被归属为常规企业VPN配置(而不是由NEVPNManager创建的个人VPN)。一次只能在系统启用一个VPN配置。如果同时在系统中激活个人VPN和企业VPN,企业VPN优先使用。

######知识点 2. 将网络数据路由到VPN两种方式

  * IP 地址

这是默认的路由方式。IP通道通过Packet Tunnel Provider extension被标记在VPN通道完全被建立。

  * By source application (Per-App VPN)

Per-App VPN 应用程序规则同时用于路由规则和VPN需求规则。这与基于路由的IP地址形成鲜明的对比，当onDemandEnabled属性被设置成true并且app匹配he Per-App VPN规则试图通过网络进行通信，VPN将自动开始。

######4-2 初始化NETunnelProviderManager对象

  * 设置NETunnelProviderManager所需的各个参数的值

在本例中利用各个参数的值均用模型实现，在主控制器直接调用以下即可

> 注意

  * TunnelBundleId 需要传入VPN Extension Target 的BundleID
  * serverAddress:即在手机设置的VPN中显示的VPN地址
  * 其余参数根据真实情况填写，如果只是测试即可直接用以下参数(或设置其他参数也可)
  * 以下参数只是在系统设置中VPN设置里显示的参数，真正设置网络参数在VPN Target项目中重新设置。
    
    
        [model configureInfoWithTunnelBundleId:@"com.xxx.xxx.xxxx"
                                 serverAddress:@"10.10.10.1"
                                    serverPort:@"54345"
                                           mtu:@"1400"
                                            ip:@"10.8.0.2"
                                        subnet:@"255.255.255.0"
                                           dns:@"8.8.8.8,8.4.4.4"];

而在封装管理NETunnelProviderManager对象真正起作用的是如下代码

    
    
    - (void)applyVpnConfiguration {
        [NETunnelProviderManager loadAllFromPreferencesWithCompletionHandler:^(NSArray<NETunnelProviderManager *> * _Nullable managers, NSError * _Nullable error) {
            if (managers.count > 0) {
                self.vpnManager = managers[0];
                log4cplus_error("XDXVPNManager", "The vpn already configured. We will use it.");
                return;
            }else {
                log4cplus_error("XDXVPNManager", "The vpn config is NULL, we will config it later.");
            }
            [self.vpnManager loadFromPreferencesWithCompletionHandler:^(NSError * _Nullable error) {
                if (error != 0) {
                    const char *errorInfo = [NSString stringWithFormat:@"%@",error].UTF8String;
                    log4cplus_error("XDXVPNManager", "applyVpnConfiguration loadFromPreferencesWithCompletionHandler Failed - %s !",errorInfo);
                    return;
                }
                NETunnelProviderProtocol *protocol = [[NETunnelProviderProtocol alloc] init];
                protocol.providerBundleIdentifier  = self.vpnConfigurationModel.tunnelBundleId;
                NSMutableDictionary *configInfo = [NSMutableDictionary dictionary];
                [configInfo safeSetObject:self.vpnConfigurationModel.serverPort       forKey:@"port"];
                [configInfo safeSetObject:self.vpnConfigurationModel.serverAddress    forKey:@"server"];
                [configInfo safeSetObject:self.vpnConfigurationModel.ip               forKey:@"ip"];
                [configInfo safeSetObject:self.vpnConfigurationModel.subnet           forKey:@"subnet"];
                [configInfo safeSetObject:self.vpnConfigurationModel.mtu              forKey:@"mtu"];
                [configInfo safeSetObject:self.vpnConfigurationModel.dns              forKey:@"dns"];
                protocol.providerConfiguration        = configInfo;
                protocol.serverAddress                = self.vpnConfigurationModel.serverAddress;
                self.vpnManager.protocolConfiguration = protocol;
                self.vpnManager.localizedDescription  = @"NEPacketTunnelVPNDemoConfig";
                [self.vpnManager setEnabled:YES];
                [self.vpnManager saveToPreferencesWithCompletionHandler:^(NSError * _Nullable error) {
                    if (error != 0) {
                        const char *errorInfo = [NSString stringWithFormat:@"%@",error].UTF8String;
                        log4cplus_error("XDXVPNManager", "applyVpnConfiguration saveToPreferencesWithCompletionHandler Failed - %s !",errorInfo);
                    }else {
                        [self applyVpnConfiguration];
                        log4cplus_info("XDXVPNManager", "Save vpn configuration successfully !");
                    }
                }];
            }];
        }];
    }


以上代码通过NETunnelProviderManager的类方法`+(void)loadAllFromPreferencesWithCompletionHandler:(void (^)(NSArray<NETunnelProviderManager *> * __nullable managers, NSError *__nullable error))completionHandler`实现

  * 如果是第一次配置VPN,VPN的设置未保存在系统中，所以上述代码managers.count读取结果应该为0，需要我们做如上设置，第一次设置成功后，VPN的配置信息会保存在设置信息里，所以以后无需重复设置，只需要读取到就好。
  * 注意，第一次配置时需要手机授权，如果拒绝则无法继续进行。
    
    
    //此函数异步读取调用所有app创建且先前保存在本地的NETunnelProvider配置信息，并将它们在回调中以一个存放NETunnelProvider对象的数组的形式返回。
    + (void)loadAllFromPreferencesWithCompletionHandler:(void (^)(NSArray<NETunnelProviderManager *> * __nullable managers, NSError * __nullable error))completionHandler

    //该函数从调用者的VPN设置中加载当前VPN配置
    - (void)loadFromPreferencesWithCompletionHandler:(void (^)(NSError * __nullable error))completionHandler；


然后将存入模型的所有参数放入一个字典，并存入NETunnelProviderProtocol对象的providerConfiguration中，该字典在tunnel建立成功后会传递给NETunnelProviders对象。最后将配置好的NETunnelProviderProtocol对象赋值给NETunnelProviderManager对象的protocolConfiguration即可。

    
    
    //调用此方法用来保存上述配置好的VPN到本机设备的VPN设置中。
    - (void)saveToPreferencesWithCompletionHandler:(nullable void (^)(NSError * __nullable error))completionHandler;
    
    //调用此函数会使用NEVPNConnection对象当前VPN配置来建立VPN连接。返回YES表示成功。
    [self.vpnManager.connection startVPNTunnelAndReturnError:&error];
    - (BOOL)startVPNTunnelAndReturnError:(NSError **)error;

    //调用此函数会关闭当前建立的VPN连接。
    [self.vpnManager.connection stopVPNTunnel];
    - (void)stopVPNTunnel;


######4-3. 主控制器启动VPN

  * 在viewDidLoad中完成初始化操作

    * 初始化模型即根据实际情况对各个网络参数赋值(注意TunnelBundleId为本项目VPN Extension的BundleID)
    * 对XDXVPNManager进行初始化配置模型，设置代理。
    * 注册通知(NEVPNStatusDidChangeNotification)，监听VPN状态变化
  * 在`- (void)vpnDidChange:(NSNotification *)notification`方法中根据VPN的状态动态改变按钮状态

  * 点击按钮实现开启/关闭VPN连接

######4-4.在PacketTunnelProvider回调中完成剩余工作

  * 当我们在主控器调用开启VPN连接后，会进入VPN Target项目中PacketTunnelProvider文件的下述方法中

    
    //当一个新的通道被建立会会调用此函数。我们必须通过重写该类来完成建立连接。
    @param : options - 在主控制调用开启VPN连接时传入的字典，可空。
    @param : completionHandler - 在该方法彻底完成时必须调用这个Block。如果不能建立连接要将错误信息传给该block,如果成功建立连接则只需将nil传给该Block.
    - (void)startTunnelWithOptions:(nullable NSDictionary<NSString *,NSObject *> *)options completionHandler:(void (^)(NSError * __nullable error))completionHandler

注意：因为此时是处于另一个Target中，在手机相当于另一条进程，因此我们无法直接在控制台看到任何我们打印的log信息，这里我使用log4cplus则可以在我们的终端中来截获debug信息。如果你的本机装有log4cplus直接使用下面的命令即可获取信息，若未装则可以在github里直接搜索log4cplusmac版直接运行，也可以在log4cplus mac版的控制台里过滤关键字得到debug信息。

    
    $ deviceconsole |grep XDXVPNManager

    
    #define XDX_NET_MTU                        1400
    #define XDX_NET_REMOTEADDRESS              "192.168.3.14"
    #define XDX_NET_SUBNETMASKS                "255.255.255.255"
    #define XDX_NET_DNS                        "223.5.5.5"
    #define XDX_LOCAL_ADDRESS                  "127.0.0.1"
    #define XDX_NET_TUNNEL_IPADDRESS           "10.10.10.10"

    - (void)startTunnelWithOptions:(NSDictionary *)options completionHandler:(void (^)(NSError *))completionHandler
    {
        log4cplus_info("XDXVPNManager", "XDXPacketTunnelManager - Start Tunel !");
        NEPacketTunnelNetworkSettings *tunnelNetworkSettings = [[NEPacketTunnelNetworkSettings alloc] initWithTunnelRemoteAddress:@XDX_NET_REMOTEADDRESS];
        tunnelNetworkSettings.MTU = [NSNumber numberWithInteger:XDX_NET_MTU];
        tunnelNetworkSettings.IPv4Settings = [[NEIPv4Settings alloc] initWithAddresses:[NSArray arrayWithObjects:@XDX_NET_TUNNEL_IPADDRESS, nil]  subnetMasks:[NSArray arrayWithObjects:@XDX_NET_SUBNETMASKS, nil]];
        tunnelNetworkSettings.IPv4Settings.includedRoutes = @[[NEIPv4Route defaultRoute]];
        NEIPv4Settings *excludeRoute = [[NEIPv4Settings alloc] initWithAddresses:[NSArray arrayWithObjects:@"10.10.10.11", nil] subnetMasks:[NSArray arrayWithObjects:@XDX_NET_SUBNETMASKS, nil]];
        tunnelNetworkSettings.IPv4Settings.excludedRoutes = @[excludeRoute];
        [self setTunnelNetworkSettings:tunnelNetworkSettings completionHandler:^(NSError * _Nullable error) {
            if (error == nil) {
                log4cplus_info("XDXVPNManager", "XDXPacketTunnelManager - Start Tunel Success !");
                completionHandler(nil);
            }else {
                log4cplus_error("XDXVPNManager", "XDXPacketTunnelManager - Start Tunel Failed - %s !",error.debugDescription.UTF8String);
                completionHandler(error);
                return;
            }
        }];
        [self.packetFlow readPacketsWithCompletionHandler:^(NSArray<NSData *> * _Nonnull packets, NSArray<NSNumber *> * _Nonnull protocols) {
            log4cplus_debug("XDXVPNManager", "XDXPacketTunnelManager - Read Packet !");
            [packets enumerateObjectsUsingBlock:^(NSData * _Nonnull obj, NSUInteger idx, BOOL * _Nonnull stop) {
                NSString *packetStr = [NSString stringWithFormat:@"%@",obj];
                log4cplus_debug("XDXVPNManager", "XDXPacketTunnelManager - Read Packet - %s !",packetStr.UTF8String);
            }];
        }];
    }


当你上述的每一步都正确配置，并在主控器中调用-startVPNTunnelAndReturnError方法时，紧接着会在vpntarget中调用以上回调，我们需要在此回调中建立tunnel并配置我们需要的各种网络设置，最后在调用`-(void)setTunnelNetworkSettings`回调中调用`completionHandler(nil);`来建立vpn连接。

> 注意，在设置网络参数成功后必须显式调用completionHandler(nil)才能正常建立连接(官方API要求)，如果设置网络参数出错则将错误信息传入completionHandler(error),否则无法正常建立连接。

#####这里是真正设置vpn tunnel 网络参数的地方，主控制器中设置的仅为系统vpn设置中的展示名称

  * 首先新建一个NEPacketTunnelNetworkSettings对象，此对象是用来设置并建立vpn tunnel初始化对象时提供的RemoteAddress即为我们要建立连接的远程服务器的地址，注意如果是域名需要手动解析为IP地址再传入。下面提供了方法可转换。
  * MTU:最大传输单元,即每个packet最大的容量
  * includedRoutes：即vpn tunnel需要拦截包的地址，如果全部拦截则设置[NEIPv4Route defaultRoute]，也可以指定部分需要拦截的地址
  * excludeRoute ： 设置不拦截哪些包的地址，默认不会拦截tunnel本身地址发出去的包。
  * 最后调用`- (void)setTunnelNetworkSettings`，在回调若成功直接调用`completionHandler(nil);`来建立vpn连接。
    
    
    #include <netinet/in.h>
    #include <netdb.h>
    #include <arpa/inet.h>
    // 域名转换IP
    - (NSString *)queryIpWithDomain:(NSString *)domain {
        struct hostent *hs;
        struct sockaddr_in server;
        if ((hs = gethostbyname([domain UTF8String])) != NULL) {
            server.sin_addr = *((struct in_addr*)hs->h_addr_list[0]);
            return [NSString stringWithUTF8String:inet_ntoa(server.sin_addr)];
        }
        return nil;
    }
    复制代码

在调用完setTunnelNetworkSettings后如果回调返回error且我们按照上述所说完成completionHandler(nil);的配置后，vpn成功建立连接，此时我们的app状态栏里也会相应出现vpn的标识，如下图。

![](./image/20200321-151946.webp)

  * 附加步骤：在VPN Tunndel 中持续读取packet包 因为我们已经成功建立了vpn连接，所以网络数据包我们可以在此回调中截取到

利用NEPacketTunnelProvider对象的packetFlow 完成下面的方法即可。

    
    
    //从流中读入可用的IP包
    - (void)readPakcets {
        __weak PacketTunnelProvider *weakSelf = self;
        [self.packetFlow readPacketsWithCompletionHandler:^(NSArray<NSData *> * _Nonnull packets, NSArray<NSNumber *> * _Nonnull protocols) {
            for (NSData *packet in packets) {
                // log4cplus_debug("XDXVPNManager", "Read Packet - %s",[NSString stringWithFormat:@"%@",packet].UTF8String);
                __typeof__(self) strongSelf = weakSelf;
                // TODO ...
                NSLog(@"XDX : read packet - %@",packet);
            }
            [weakSelf readPakcets];
        }];
    }


以下为我读到的包

![](./image/20200321-151947.webp)

另外如需Debug app extension target可以通过Xcode如下方法

![](./image/20200321-151948.webp)

![](./image/20200321-151949.webp)

  * 停止方法较为简单，不再叙述，详细可在Demo中查阅

####总结：此Demo为利用苹果官方提供的VPN Extension在一个项目中通过新建Target来完成一个简单建立VPN的过程。其中涉及到App extension的知识可在本文所附的另一篇文章中查阅，主要涉及App extension在项目中的配置，以及建立VPN连接时一些参数的设置及方法的调用时机,以及成功建立连接后可拦截手机中的网络Packet。

