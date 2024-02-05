 
<!--BEGIN_DATA
{
    "create_date": "2019-09-14 17:44", 
    "modify_date": "2019-09-14 17:44", 
    "is_top": "0", 
    "summary": "NAT穿透技术原理", 
    "tags": "WebRTC、C/C++、网络", 
    "file_name": "NAT穿透技术原理.md"
}
END_DATA-->

####<p>原文出处：<a href='https://www.cnblogs.com/markqian/articles/3378693.html' target='blank'>NAT穿透技术原理浅谈</a></p>

今天我们来看看NAT方面的技术，提起NAT技术，我们大家可能并不陌生，就真实的存在我们身边，只不过我们很少关注它．NAT是一种网络地址翻译技术，将内部私有IP地址改变成可以在公网上使用的:公网IP.其出现背景就是因为我们国家公网IP地址太少了不够用，才使NAT技术兴起．这里我就不具体和大家细说NAT是怎么转换IP地址了，技术原理不太难．NAT技术的使用从技术角度讲是有利也有弊的．我们可以同时让多个计算机同时联网，同时也隐藏了内部地址，NAT对来自外部的数据查看其NAT映射记录，对没有相应记录的数据包进行拒绝，无非提高了网络的安全性．从另一个方面来看，NAT设备对数据包进行编辑修改操作，降低了发送数据的数率．由于技术的复杂性，排错也变的困难了，我们在内部对外发布一个服务器，还得考虑这个端口映射问题等．这也到罢了，网络盛行的今天，各种应用不断，其协议应用也各有不同，有的根本无法通过NAT．这是最为头疼的事．目前为了解决这些问题，已多现多种穿透技术．一会我们细谈．

NAT三种实现方式

静态地址转换： 一个公网IP对应一个内部IP,一对一转换

动态地址转换： N个公网IP对应M个内部Ip,不固定的一对一IP转换关系．同一时间，有M-N个主机无法联网．

端口多路复用： 对外只有一个公网IP,通过端口来区别不同内部IP主机的数据．

IP转换策略

对于静态与动态地址转换；其数据包出站的时候，进行源地址转换．我们称之为 SNAT［SOURCE
ADDRESS］.其内部源IP变公网源IP.数据包入站的时候，进行目标地址转DNAT[DESTINATION
ADDRESS],其外部公网宿IP变内部宿IP.静态与动态不进行端口转换．而端口多路复用技术．不但要转换其IP地址，还要进行其传输层的端口转换．通过这唯一的端口号来区别不同的内部数据［在通信过程中会建立一张内部到外部映射表］．我们称之NATP［NAT PORT］技术.在我们家用网络中，大部分用的是端口多路复用技术．在端口多路复用技术中，对数据的处理还分这么两类：锥形NAT与对称型NAT.锥形NAT又分完全锥形NAT[FULL CONE]|受限锥形NAT[RESTRICTED CONE]|端口受限锥形NAT[PORT RESTRICTED CONE].

全完锥形NAT： 将来自内部同一个IP地址同一个端口号的主机监听/请求，映射到公网IP某个端口的监听．任意外部IP地址与端口对其自己公网的IP这个映射后的端口访问，都将重新定位到内部这个主机．个人认为在内部发布服务器到外网，此技术原理完全否合该技术原理，当然某些
P2P中也可能利用该技术．该技术中，基于C/S架构的应用可以在任何一端发起连接．

受限锥形NAT:与完全NAT不同的是，在公网映射端口后，并不允许所有IP进行对于该端口的访问，要想通信必需内部主机对某个外部IP主机发起过连接，然后这个外部IP主机就可以与该内部主机通信了．但端口不做限制.如出站源IP为A端口为B,对于外部IP回复，宿IP为A宿端口可以是任意．NAPT设备都将成功转发到内部主机．NAPT设备根据映射记录做出判断．该技术中只能内部主机先发起连接通信才可成功．

端口受限锥形NAT:该技术与受限锥形NAT相比更为严格．除具有受限锥形NAT特性．对于回复主机的源端口也有要求．哪我用端口B访问你，对于外部主机的回复信宿端口也只能是B.否折通信失败．该技术中只能内部主机先发起连接通信才可成功．

对称型NAT：内部主机用同一IP与同一端口与外部多IP通信．NAPT设备为每个会话转换了不同的源端口．不在转换成相同的源端口．对于回复的数据包，只有信宿IP地址与端口完全吻合才可进入．当然源IP也是要检测的，不可能随意外部IP都能进入的．

NAT穿透技术

为何会出现NAT穿透技术？我们知道在NAPT技术应用中，要想实现通信，端口是必需的．IP地址修改是必需的．现在是残酷的．FTP应用协议分控制端口与数据端口，悲剧的是数据端口不是固定的，协商成功后告知对方数据端口内容是承载于应用层之中．NAT设备无法对其进行分析，做出相应的映射，从而导致通信失败．VPN协议中的PPTP协议，在数据连接中协议部分根本没有端口这一概念．要NAT如何做出决策？ipsec安全协议本身就是保证数据的安全并认证通信源而发明，对
其网络层进行IP效验，对传输入层进行加密，对数据进行加密．对于NAT来说让其通信这更是无稽之谈．当然无法穿过NAT的还有很多，如语音VOIP中的H.323与SIP协议．为了能让这些协议成功应用，出现了五花八门的穿透NAT技术．其技术有UPNP技术．ALG［应用层网关识别技术］SBC[会话边界控制]ICE[交互式连接建立]MIDCOM［中间盒技术］TURN［中继NAT穿越］STUN技术．TCP/UDP hole punching［TCP/UDP打洞技术］NAT-T技术…总之很多，原理各不相同，我也没有时间一个一个学习和分析．在此说几个应用比较多点的例子．

ALG技术：传统的NAT技术只能检测网络层与传输层地址，你FTP不是在应用层传送端口地址吗？所以ALG技术就是一种应用层地址识别技术，根据不同的协议进行检测，然后将发现的地址时行修改并通知NAT做相应的映射记录，从而实现成功通信．对于该技术，对于互联网每一种新的协议支持都要更新其设备要不无法识别．扩展性差．对于个别协议该技术无法解决问题，如IPSEC协议．

STUN技术：通过STUN协议与第三方服务器建立连接，推测出客户端的NAT类型．进而通信．
RFC3489/STUN协议过程［摘自cr0_3百度空间］．STUN协议定义了三类测试过程来检测NAT类型，如下所述：

Test1：STUN Client通过端口{IP-c1:Port-c1}向STUN Server{IP-s1:Port-s1}发送一个Binding Request（没有设置任何属性）。STUN Server收到该请求后，通过端口{IP-s1:Port-s1}把它所看到的STUN Client的IP和端口{IP-m1,Port-m1}作为Binding Response的内容回送给STUN Client。

Test1#2：STUN Client通过端口{IP-c1:Port-c1}向STUN Server{IP-s2:Port-s2}发送一个Binding Request（没有设置任何属性）。STUN Server收到该请求后，通过端口{IP-s2:Port-s2}把它所看到的STUN Client的IP和端口{IP-m1#2,Port-m1#2}作为Binding Response的内容回送给STUN Client。

Test2：STUN Client通过端口{IP-c1:Port-c1}向STUN Server{IP-s1:Port-s1}发送一个Binding Request（设置了Change IP和Change Port属性）。STUN Server收到该请求后，通过端口{IP-s2:Port-s2}把它所看到的STUN Client的IP和端口{IP-m2,Port-m2}作为Binding Response的内容回送给STUN Client。

Test3：STUN Client通过端口{IP-c1:Port-c1}向STUN Server{IP-s1:Port-s1}发送一个Binding Request（设置了Change Port属性）。STUN Server收到该请求后，通过端口{IP-s1:Port-s2}把它所看到的STUN Client的IP和端口{IP-m3,Port-m3}作为Binding Response的内容回送给STUN Client。

NAT类型检测过程如下

1\. 进行Test1。如果STUN Client不能够收到STUN Server的应答（重复多次确认），那么说明该STUN Client是UDP Blocked类型（也有可能是STUN Server不可到达，这里不考虑这种情形）；否则，STUN Client把返回的{IP-m1,Port-m1}和本地的{IP-c1:Port-c1}进行比较（只需要比较IP即可），如果相同，说明本机直接连接于公网，否则本机位于NAT之后，但还需要进一步判断具体类型。

1.1. 如果本机直接连接于公网，进行Test2。如果STUN Client不能够收到STUN Server的应答（重复多次确认），那么说明该STUN Client是Symmetric Firewall类型；否则，该STUN Client是Open Internet类型。

1.2. 如果本机位于NAT之后，进行Test2。如果STUN Client能够收到STUN Server的应答，那么说明该STUN Client是Full Cone NAT；否则，需要进一步进行测试。

1.2.1. 进行Test1#2。STUN Client比较IP-m1和IP-m1#2是否相同，如果不相同，那么说明该STUN Client是Symmetric NAT类型；否则，需要进一步进行测试。

1.2.1.1 进行Test3。如果STUN Client能够收到STUN Server的应答，那么说明该STUN Client是Restricted Cone NAT类型；否则，该STUN Client是Port Restricted Cone NAT类型。

该技术大部分是针对P2P应用环境中．

NAT-T技术：其思想就是在ESP隧道模式下，在外IP包头与ESP报头中间加入8个字节的UDP报关，使其NAT成功映射．

IPSec提供了端到端的IP通信的安全性，但在NAT环境下对IPSec的支持有限，AH协议是肯定不能进行NAT的了，这和AH设计的理念是相违背的；ESP协议在NAT环境下最多只能有一个VPN主机能建立VPN通道，无法实现多台机器同时在NAT环境下进行ESP通信。

NAT穿越(NAT Traversal，NAT -T)就是为解决这 个问题而提出的，RFC3947，3948中定义，在RFC4306中也加入了NAT-T的说明，但并没废除RFC3947，3948，只是不区分阶段1
和阶段2。该方法将ESP协议包封装到UDP包中（在原ESP协议的IP包头外添加新的IP头和UDP头），使之可以在NAT环境下使用的一种方法，这样在NAT的内部网中可以有多个IPSec主机建立VPN通道进行通信。

AH封装：AH封装的校验从IP头开始，如果NAT将IP的头部改动，AH的校验就会失败，因此我们得出结论，AH是无法与NAT共存的。ESP封装的传输模式：对于NAT来说，ESP封装比AH的优势在于，无论是加密还是完整性的校验，IP头部都没有被包括进去。但是还是有新的问题，对于ESP
的传输模式，NAT 无法更新上层校验和。TCP 和 UDP 报头包含一个校验和，它整合了源和目标 IP 地址和端口号的值。当 NAT 改变了某个包的 IP 地址和（或）端口号时，它通常要更新 TCP 或 UDP 校验和。当 TCP 或 UDP 校验和使用了 ESP 来加密时，它就无法更新这个校验和。由于地址或端口已经被 NAT 更改，目的地的校验和检验就会失败。虽然 UDP 校验和是可选的，但是 TCP 校验和却是必需的。

ESP封装的隧道模式：从ESP隧道模式的封装中，我们可以发现，ESP隧道模式将整个原始的IP包整个进行了加密，且在ESP的头部外面新加了一层IP 头部，所以NAT如果只改变最前面的IP地址对后面受到保护的部分是不会有影响的。因此，IPsec只有采用ESP的隧道模式来封装数据时才能与NAT共存。ESP的传输模式，因为TCP部分被加密，NAT无法对TCP校验和进行修改，不兼容。ESP的隧道模式，由于NAT改动外部的IP而不能改动被加密的原始IP，使得只有这种情况下才能与NAT共存。


<hr>



####<p>原文出处：<a href='https://www.jianshu.com/p/84e8c78ca61d' target='blank'>ICE协议下NAT穿越的实现（STUN&TURN）</a></p>

####前言：

之前写了篇关于WebRTC的文章：[iOS下音视频通信-基于WebRTC  ](https://www.jianshu.com/p/c49da1d93df4)，由于它是基于点对点连接的，自然而然需要NAT穿越的技术，否则消息将无法传递。

在WebRTC使用了ICE协议框架，里面提到了`STUN`和`TURN`两个协议，而NAT穿越实现就是由这两个协议共同协调完成的。

####正文：

#####一. 首先来简单讲讲什么是NAT？

原来这是因为IPV4引起的，我们上网很可能会处在一个NAT设备（无线路由器之类）之后。  
NAT设备会在IP封包通过设备时修改源/目的IP地址. 对于家用路由器来说, 使用的是网络地址端口转换(NAPT), 它不仅改IP,还修改TCP和UDP协议的端口号, 这样就能让内网中的设备共用同一个外网IP. 举个例子, NAPT维护一个类似下表的NAT表：  

NAT映射

![](./image/20190914-181513.webp)

  
NAT设备会根据NAT表对出去和进来的数据做修改, 比如将`192.168.0.3:8888`发出去的封包改成`120.132.92.21:9202`,外部就认为他们是在和`120.132.92.21:9202`通信.
同时NAT设备会将`120.132.92.21:9202`收到的封包的IP和端口改成`192.168.0.3:8888`, 再发给内网的主机,这样内部和外部就能双向通信了, 但如果其中`192.168.0.3:8888` == `120.132.92.21:9202`这一映射因为某些原因被NAT设备淘汰了, 那么外部设备就无法直接与`192.168.0.3:8888`通信了。

我们的设备经常是处在NAT设备的后面, 比如在大学里的校园网, 查一下自己分配到的IP, 其实是内网IP, 表明我们在NAT设备后面,如果我们在寝室再接个路由器, 那么我们发出的数据包会多经过一次NAT.

#####二. NAT的副作用以及解决方案

国内移动无线网络运营商在链路上一段时间内没有数据通讯后, 会淘汰NAT表中的对应项, 造成链路中断。

######这是NAT带来的第一个副作用：NAT超时:

而国内的运营商一般NAT超时的时间为5分钟，所以通常我们TCP长连接的心跳设置的时间间隔为3-5分钟。**

######而第二个副作用就是：我们这边文章要提到的NAT墙。

NAT会有一个机制，所有外界对内网的请求，到达NAT的时候，都会被NAT所丢弃，这样如果我们处于一个NAT设备后面，我们将无法得到任何外界的数据。

但是这种机制有一个解决方案：就是如果我们A主动往B发送一条信息，这样A就在自己的NAT上打了一个B的洞。这样A的这条消息到达B的NAT的时候，虽然被丢掉了，但是如果B这个时候在给A发信息，到达A的NAT的时候，就可以从A之前打的那个洞中，发送给到A手上了。

简单来讲，就是**如果A和B要进行通信，那么得事先A发一条信息给B，B发一条信息给A。这样提前在各自的NAT上打了对方的洞，这样下一次A和B之间就可以进行通信了。**

#####三. 四种NAT类型：

RFC3489 中将 NAT 的实现分为四大类：

  1. Full Cone NAT （完全锥形 NAT）

  2. Restricted Cone NAT （限制锥形 NAT ，可以理解为 IP 限制，Port不限制）

  3. Port Restricted Cone NAT （端口限制锥形 NAT，IP+Port 限制）

  4. Symmetric NAT （对称 NAT）

其中完全最上层的完全锥形NAT的穿透性最好，而最下层的对称形NAT的安全性最高。

简单来讲讲这4种类型的NAT代表什么：

  * 如果一个NAT是Full Cone NAT，那么无论什么IP地址访问，都不会被NAT墙掉（这种基本很少）。
  * Restricted Cone NAT，仅仅是经过打洞的IP能穿越NAT，但是不限于Port。
  * Port Restricted Cone NAT，仅仅是经过打洞的IP+端口号能穿越NAT。
  * Symmetric NAT 这种也是仅仅是经过打洞的IP+端口号能穿越NAT，但是它有一个最大的和Cone类型的NAT的区别，它对外的公网Port是不停的变化的：  
比如A是一个对称NAT，那么A给B发信息，经过NAT映射到一个Port:10000，A给C发信息，经过NAT映射到一个Port:10001，这样会导致一个问题，我们服务器根本无法协调进行NAT打洞。

至于为什么无法协调打洞，下面我们会从STUN和TURN的工作原理来讲。

#####四. STUN和TURN的实现：

######1.STUN Server主要做了两件事：

  * 接受客户端的请求，并且把客户端的公网IP、Port封装到ICE Candidate中。
  2. 通过一个复杂的机制，得到客户端的NAT类型。

完成了这些STUN Server就会这些基本信息发送回客户端，然后根据NAT类型，来判断是否需要TURN服务器协调进行下一步工作。

我们来讲讲这两步具体做了什么吧：  
第一件事就不用说了，其实就是得到客户端的请求，把源IP和Port拿到，添加到ICE Candidate中。

#######来讲讲第二件事，STUN是如何判断NAT的类型的：

假设B是客户端，C是STUN服务器，C有两个IP分别为IP1和IP2（至于为什么要两个IP，接着往下看）：

#######STEP1.判断客户端是否在NAT后：

B向C的IP1的pot1端口发送一个UDP包。C收到这个包后，会把它收到包的源IP和port写到UDP包中，然后把此包通过IP1和port1发还给B。这个IP和port也就是NAT的外网IP和port（如果你不理解，那么请你去看我的BLOG里面的NAT的原理和分类），也就是说你在STEP1中就得到了NAT的外网IP。

熟悉NAT工作原理的朋友可以知道，C返回给B的这个UDP包B一定收到。如果在你的应用中，向一个STUN服务器发送数据包后，你没有收到STUN的任何回应包，那只有两种可能：1、STUN服务器不存在，或者你弄错了port。2、你的NAT拒绝一切UDP包从外部向内部通过。

当B收到此UDP后，把此UDP中的IP和自己的IP做比较，如果是一样的，就说明自己是在公网，下步NAT将去探测防火墙类型，我不想多说。如果不一样，说明有NAT的存在，系统进行STEP2的操作。

#######STEP2.判断是否处于Full Cone Nat下：

B向C的IP1发送一个UDP包，请求C通过另外一个IP2和PORT（不同与SETP1的IP1）向B返回一个UDP数据包（现在知道为什么C要有两个IP了吧，虽然还不理解为什么，呵呵）。

我们来分析一下，如果B收到了这个数据包，那说明什么？说明NAT来着不拒，不对数据包进行任何过滤，这也就是STUN标准中的full coneNAT。遗憾的是，Full Cone Nat太少了，这也意味着你能收到这个数据包的可能性不大。如果没收到，那么系统进行STEP3的操作。

#######STEP3.判断是否处于对称NAT下：

B向C的IP2的port2发送一个数据包，C收到数据包后，把它收到包的源IP和port写到UDP包中，然后通过自己的IP2和port2把此包发还给B。

和step1一样，B肯定能收到这个回应UDP包。此包中的port是我们最关心的数据，下面我们来分析：  
如果这个port和step1中的port一样，那么可以肯定这个NAT是个CONE NAT，否则是对称NAT。道理很简单：根据对称NAT的规则，当目的地址的IP和port有任何一个改变，那么NAT都会重新分配一个port使用，而在step3中，和step1对应，我们改变了IP和port。因此，如果是对称NAT,那这两个port肯定是不同的。

如果在你的应用中，到此步的时候PORT是不同的，那么这个它就是处在一个对称NAT下了。如果相同，那么只剩下了restrict cone 和portrestrict cone。系统用step4探测是是那一种。

#######STEP4.判断是处于Restrict Cone NAT还是Port Restrict NAT之下：

B向C的IP2的一个端口PD发送一个数据请求包，要求C用IP2和不同于PD的port返回一个数据包给B。

我们来分析结果：如果B收到了，那也就意味着只要IP相同，即使port不同，NAT也允许UDP包通过。显然这是Restrict Cone NAT。如果没收到，没别的好说，Port Restrict NAT.

#######到这里STUN Server一共通过这4步，判断出客户端处于什么类型的NAT下，然后去做后续的处理：

这4步都会返回给客户端它的公网IP、Port和NAT类型，除此之外：

  1. 如果A处于公网或者Full Cone Nat下，STUN不做其他的了，因为其他客户端可以直接和A进行通信。

  
![](./image/20190914-181514.webp)

  2. 如果A处于Restrict Cone或者Port Restrict NAT下，STUN还会协调TURN进行NAT打洞。

  
![](./image/20190914-181515.webp)

  3. 如果A处于对称NAT下，那么点对点连接下，NAT是无法进行打洞的。所以为了通信，只能采取最后的手段了，就是转成C/S架构了，STUN会协调TURN进行消息转发。

  
![](./image/20190914-181516.webp)

######2.TURN Server也主要做了两件事：

  * #######为NAT打洞：

如果A和B要互相通信，那么TURN Server，会命令A和B互相发一条信息，这样各自的NAT就留下了对方的洞，下次他们就可以之间进行通信了。

  * #######为对称NAT提供消息转发：

当A或者B其中一方是对称NAT时，那么给这一方发信息，就只能通过TURN Server来转发了。

#####最后补充一下，为什么对称NAT无法打洞：

假如A、B进行通信，而B处于对称NAT之下，那么A与B通信，STUN拿到A，B的公网地址和端口号都为10000，然后去协调TURN打洞，那么TURN去命令A发信息给B，则A就在NAT打了个B的洞，但是这个B的洞是端口号为10000的洞，但是下次B如果给A发信息，因为B是对称NAT，它给每个新的IP发送信息时，都重新对应一个公网端口，所以给A发送请求可能是公网10001端口，但是A只有B的10000端口被打洞过，所以B的请求就被丢弃了。  
显然Server是无法协调客户端打洞的，因为协调客户端打得洞仅仅是上次对端为Server发送端口的洞，并不适用于另一个请求。

######最后的最后再补充一点，就是NAT打的洞也是具有时效性的，如果NAT超时了，那么还是需要重新打洞的。



<hr>




####<p>原文出处：<a href='https://blog.csdn.net/yinshuhai/article/details/464661' target='blank'>P2P:UDP穿透NAT防火墙</a></p>

**现在大部分网络使用NAT，或者像我们学校，虽然IP是公网的，但是网关防火墙都不允许外面的访问我们内部，这样的情况就得用p2p技术了。因为这次做的东西需要用到p2p传输，就找了一些资料，整理了一下。**


**对于UDP：**一种是Cone NAT，简单说就是NAT每次分配给内网的端口是一样的，即使连接不同的主机，NAT上的端口还是不变（除非过期）。类似这样的NAT或防火墙，已经有比较可靠的解决方法：[Peer-to-Peer (P2P) communication across middleboxes](http://blogs.impx.net/dragonimp/articles/484.aspx)

另外一种是Symmetric NAT，对于这种NAT，内网连接不同的其他主机，NAT分配给它的是不同的端口。这种情况下，使用上面的方法就已经无效了。可能的办法就是猜测NAT下次将要分配的端口，也有算法可以比较准确得猜测到端口：[Symmetric NAT Traversal using
STUN](http://blogs.impx.net/dragonimp/articles/485.aspx)

虽然还是没有办法完全猜对，但也是一种办法。我已经用实现Cone NAT，因为考虑到现在大部分的NAT不是Symmetric的，因此，就不去考虑Symmetric的实现了，也许日后有时间可以考虑。

**对于TCP**，也有办法：[Establishing TCP Connections Between Hosts Behind NATs](http://www.andrew.cmu.edu/user/ggw/natblaster.pdf)

TCP现在还没用上，估计很快就要用到了。

**这里总结一下UDP穿透NAT：**


**   对于Cone NAT，是这样的情况：**

           Server S1                                     Server S2

        18.181.0.31:1235                             138.76.29.7:1235

               |                                             |

               |                                             |

               +----------------------+----------------------+

                                      |

          ^  Session 1 (A-S1)  ^      |      ^  Session 2 (A-S2)  ^

          |  18.181.0.31:1235  |      |      |  138.76.29.7:1235  |

          v 155.99.25.11:62000 v      |      v 155.99.25.11:62000 v

                                      |

                                   Cone NAT

                                 155.99.25.11

                                      |

          ^  Session 1 (A-S1)  ^      |      ^  Session 2 (A-S2)  ^

          |  18.181.0.31:1235  |      |      |  138.76.29.7:1235  |

          v   10.0.0.1:1234    v      |      v   10.0.0.1:1234    v

                                      |

                                   Client A

                                10.0.0.1:1234

****

** **

****



**下面是Symmetric NAT**



           Server S1                                     Server S2

        18.181.0.31:1235                             138.76.29.7:1235

               |                                             |

               |                                             |

               +----------------------+----------------------+

                                      |

          ^  Session 1 (A-S1)  ^      |      ^  Session 2 (A-S2)  ^

          |  18.181.0.31:1235  |      |      |  138.76.29.7:1235  |

          v 155.99.25.11:62000 v      |      v 155.99.25.11:62001 v

                                      |

                                 Symmetric NAT

                                 155.99.25.11

                                      |

          ^  Session 1 (A-S1)  ^      |      ^  Session 2 (A-S2)  ^

          |  18.181.0.31:1235  |      |      |  138.76.29.7:1235  |

          v   10.0.0.1:1234    v      |      v   10.0.0.1:1234    v

                                      |

                                   Client A

                                10.0.0.1:1234



我实现的是Cone NAT，所有就说说Cone NAT：



                                Server S

                                   |

                                   |

            +----------------------+----------------------+

            |                                             |

          NAT A（NAip:NAport)                       NAT B(NBip:NBport)

            |                                             |

            |                                             |

         Client A                                      Client B







   假设上图中的NATA和NATB都是Cone NAT。

现在ClientA要向ClientB发送数据（比如文件），首先ClientA和B分别通过他们的NATA和B在ServerS上登记，ServerS记录他们NAT的IP和端口号（因为是NAT和ServerS通信的，所以ServerS能也只能得到NAT的地址和端口号）。现在ClientA通过NATA告诉ServerS说要传文件给Client，ServerS就把ClientA的NATA的IP和端口号发送给NATB（因为B的NAT端口已经在ServerS上有记录了），ClientB收到后发送连接数据给NATA，这个时候NATA是不会接受ClientB发过来的包的，因为ClientA没有连接过B，NATA就不会接受B的数据了。虽然B连接A不成功，但是B已经连接过A了，NATB记住了，这时B告诉ServerS叫A过来连，A收到命令后连接B就成功了，于是建立连接，后面的传输就成功了！

整个过程如下：

ClientA-->NATA-->ServerS(A在S登记NAip:NAport)  
ClientB-->NATB-->ServerS (B在S登记NBip:NBport)

ClientA-->NATA-->ServerS(A告诉S，要发数据给B)  
ServerS-->NATB-->ClinetB(S把NAip:NAport发给B，并告诉B，A要发数据给你了)

ClientB-->NATB-->NATA(NAip:NAport)-->Dropped-->ClientA (B发的包别NATA丢掉了，A是收不到了)  
ClientB-->NATB-->ServerS(B等不到A的回应，就告诉S，叫A过来连我吧)

ServerS-->NATA-->ClinetA(S把NBip:NBport发给A，并告诉A，B连不到你，你连B吧)  
ClientA-->NATA-->NATB(NBip:NBport)-->ClinetB(B收到A的连接请求，要发送应答给A)  
ClientB-->NATB-->NATA-->ClientA(A收到B的应答，后面可以发送数据给NBip:NBport了)

ClientA-->NATA-->NATB-->ClientB(现在开始就从这条路发数据了)



一般防火墙原理：

防火墙的设置分未界内根界外，就像以前使用的AtGuard，如果设置界内，就是对从外面发起的连接进行检测，如果规则设置阻挡，那么从外面访问进来的连接就被阻挡。
但是，这不是说这样单方面的通信，很多人对这个不清楚，以为防火墙都不让外面进来了，那文件是怎么传的？其实，如果从里面发起连接，然后外面就可以连接进来了。虽然我没有关于防火墙确切的资料，但根据我的掌握的理论，我想我的推理是正确的。先由里面发起连接对方的请求，防火墙就会记住这个信息（也许是建立了一个session，一定时间内会释放或过期），对方收到请求，反过来连接防火墙是允许的。所以，对于上面的NAT原理，当然是可以用于一般的防火墙，而且更简单，因为得到的“NAT”的IP和端口都是本机的。


实现：


NAT信息的获取和发送：


理论上解决了，实现这个就简单了。本来做这个就是因为自己的客户端JBQ的需要，因此直接在JBQ客户端上面做。而服务器（用于p2p的服务器另外写）。原来的JBQ消息和文件都是通过服务器中转，现在就是把文件这部分改成p2p。

按照上面的原理，发送方需要把自己在NAT上的地址信息发送给接受方，然后由接受方向发送方连接，这样就可以在接受方的防火墙上面开个session，以让发送方进行后面的连接。但接受方连接不成功的时候，把自己的NAT信息再通过服务器发送给发送发送方，然后发送方再次连接接受方，于是建立连接。这里用到的服务器有两个，一个用来发送NAT信息，还有一个用来获取NAT信息。

本来这个两个应该是用同一个服务器，但是我们有原来的聊天服务器，因此，发送NAT信息的任务就交给聊天服务器，现在只要完成获取NAT信息的服务器就可以了。不管是Tcp还是UDP，连接双方都可以直接得到对方得IP和端口，因为只要由需要自己的NAT信息的客户端向p2p服务器发一个消息，p2p把跟它连接的客户端使用的NAT信息发回给客户端就可以。客户端收到p2p服务器发回来的消息以后，就可以把这个消息通过聊天服务器发给对方。

其他的握手和连接通过上面的理论都可以比较容易的写出来。

存在的问题：这种方法只适用于Cone NAT，对于**Symmetric NAT还需要通过猜测端口。**

另外，同样不适用于TCP，因为TCP的三次握手在这样的连接中必定失败。但也可以通过一点的办法解决，这个上面提到过。

总结：总的来说，上面用的方法可以解决的这一类NAT（防火墙的问题），可以让都处于NAT或防火墙后面的双方直接连接。上面的实现解决了我的JBQ客户端里面的一系
列问题，视频等都已经在这个基础上实现p2p了。
