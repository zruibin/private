 
<!--BEGIN_DATA
{
    "create_date": "2019-09-20 11:00", 
    "modify_date": "2019-09-20 11:00", 
    "is_top": "0", 
    "summary": "Bittorrent Protocol Specification", 
    "tags": "C/C++", 
    "file_name": "Bittorrent Protocol Specification.md"
}
END_DATA-->

####<p>原文出处：<a href='http://blog.chinaunix.net/uid-11572501-id-2868613.html' target='blank'>Bittorrent Protocol Specification v1.0 中文</a></p>

翻译：小马哥  
日期：2004-5-22  
BitTorrent 是一种分发文件的协议。它通过URL来识别内容，并且可以无缝的和web进行交互。它基于HTTP协议，它的优势是：如果有多个下载者并发的下载同一个文件，那么，每个下载者也同时为其它下载者上传文件，这样，文件源可以支持大量的用户进行下载，而只带来适当的负载的增长。（译注：因为大量的负载被均衡到整个系统中，所以提供源文件的机器的负载只有少量增长）  
  
一个BT文件分布系统由下列实体组成：  
一个普通的web服务器  
一个静态的“元信息”文件  
一个跟踪（tracker）服务器  
终端用户的web浏览器  
终端下载者  
  
理想的情况是多个终端用户在下载同一个文件。  
要提供文件共享，那么一台主机需要执行以下步骤：  
Ø运行一个 tracker服务器（或者，已经有一个tracker服务器在运行了也可以）  
Ø运行一个web服务器，例如apache，或者已经有一个web服务器在运行了。  
Ø在web服务器上，将文件扩展名.torrent 和MIME类型 application/x-bittorrent关联起来（或者已经关联了）  
Ø根据 tracker服务器的 URL 和要共享的文件来创建一个“元信息”文件（.torrent）。  
Ø将“元信息”文件发布到web服务器上  
Ø在某个web页面上，添加一个到“元信息”文件的链接。  
Ø运行一个已经拥有完整文件的下载者（被成为’origin’，或者’seed’，种子）  
  
要开始下载文件，那么终端用户执行以下步骤：  
Ø安装 BT（或者已经安装）  
Ø访问提供 .torrent 文件的web服务器  
Ø点击到 .torrent 文件的链接（译注：这时候，bt会弹出一个对话框）  
Ø选择要把下载的文件保存到哪里？或者是一次断点续传  
Ø等待下载的完成。  
Ø结束bt程序的运行（如果不主动结束，那么bt会一直为其它人提供文件上传）  
  
各个部分之间的连通性如下：  
网站负责提供一个静态的文件，而把BT辅助程序（客户端）放在客户端机器上。  
Trackers从所有下载者处接收信息，并返回给它们一个随机的peers的列表。这种交互是通过HTTP或HTTPS协议来完成的。  
下载者周期性的向tracker登记，使得tracker能了解它们的进度；下载者之间通过直接连接进行数据的上传和下载。这种连接使用的是BitTorrent对等协议，它基于TCP。  
Origin只负责上传，从不下载，因为它已经拥有了完整的文件。Origin是必须的。  
  
元文件和tracker的响应都采用的是一种简单、有效、可扩展的格式，被称为bencoding，它可以包含字符串和整数。由于对不需要的字典关键字可以忽略，所以这种格式具有可扩展性，其它选项以后可以方便的加进来。  
  
Bencoding格式如下：  
对于字符串，首先是一个字符串的长度，然后是冒号，后面跟着实际的字符串，例如：4:spam，就是“ spam”  整数编码如下，以 ‘i’ 开始，然后10进制的整数值，最后以’e’结尾。例如，i3e表示3，I-3e表示-3。整数没有大小限制。I-0e是无效的。除了i0e外，所以以0起始的整数都无效。I0e当然表示0。  
列表编码如下，以’l’开始，接下来是列表值的编码（也采用bencoded编码），最后以’e’结束。例如：l4:spam4:eggse 表示 [‘spam’,
‘eggs’]。  
字典编码如下，以’d’开始，接下来是可选的keys和它对应的值，最户以’e’结束。例如：d3:cow3:moo4:spam4:eggse，表示{‘cow’:’moo’,’spam’:’eggs’}，而d4:spaml1:al:bee 表示
{‘spam’:[‘a’,’b’]}。键值必须是字符串，而且已经排序（并非是按照字母顺序排序，而是根据原始的字符串进行排序）。  
  
元文件是采用bencoded编码的字典，包括以下关键字：  
  
announce tracker的服务器  
  
info 它实际上是一个字典，包括以下关键字：  
  
Name：  
一个字符串，在保存文件的时候，作为一个建议值。仅仅是个建议而已，你可以用别的名字保存文件。  
Piece length：  
为了更好的传输，文件被分隔成等长的片断，除了最后一个片断以外，这个值就是片断的大小。片断大小几乎一直都是2的幂，最常用的是256k（BT的前一个版本3.2，用的是1M作为默认大小）  
Pieces：  
一个长度为20的整数倍的字符串。它将再被分隔为20字节长的字符串，每个子串都是相应片断的hash值。  
  
此外，还有一个length或files的关键字，这两个关键字只能出现一个。如果是length，那么表示要下载的仅仅是单个文件，如果是files那么要下载的是一个目录中的多个文件。  
如果是单个文件，那么length是该文件的长度。  
  
为了能支持其它关键字，对于多个文件的情况，也把它当作一个文件来看，也就是按照文件出现的顺序，把每个文件的信息连接起来，形成一个字符串。每个文件的信息实际上也是一个字典，包括以下关键字：  
Length：文件长度  
Path：子目录名称的列表，列表最后一项是文件的实际名称。（不允许出现列表为空的情况）。  
Name：在单文件情况下，name是文件的名称，而在多文件情况下，name是目录的名称。  
  
Tracker查询。Trakcer通过HTTP的GET命令的参数来接收信息，而响应给对方（也就是下载者）的是经过bencoded编码的消息。注意，尽管当前的tracker的实现需要一个web服务器，它实际上可以运行的更轻便一些，例如，作为apache的一个模块。  
Tracker GET requests have the following keys:  
  
发送给Tracker的GET请求，包含以下关键字：  
  
Info_hash：  
元文件中info部分的sha hash，20字节长。这个字符创几乎肯定需要被转义（译注：在URL中，有些字符不能出现，必须通过unicode进行编码）  
  
Peer_id：  
下载者的id，一个20字节长的字符串。每个下载者在开始一次新的下载之前，需要随机创建这个id。这个字符串通常也需要被转义。  
  
Ip：  
一个可选的参数，给出了peer的ip地址（或者dns名称？）。通常用在origin身上，如果它和tracker在同一个机器上。  
  
Port：  
peer所监听的端口。下载者通常在在 6881 端口上监听，如果该端口被占用，那么会一直尝试到 6889，如果都被占用，那么就放弃监听。  
  
Uploaded：  
已经上载的数据大小，十进制表示。  
  
Downloaded：  
已经下载的数据大小，十进制表示

Left：  
该peer还有多少数据没有下载完，十进制表示。注意，这个值不能根据文件长度和已下载数据大小计算出来，因为很可能是断点续传，如果因为检查文件完整性失败而必须重新下载的时候，这也提供了一个机会。  
  
Event：  
一个可选的关键字，值是started、compted或者stopped之一（也可以为空，不做处理）。如果不出现该关键字，。在一次下载刚开始的时候，该值被设置为started，在下载完成之后，设置为completed。如果下载者停止了下载，那么该值设置为stopped。  
  
Tracker的响应是用bencoded编码的字典。如果tracker的响应中有一个关键字failure reason，那么它对应的是一个字符串，用来解释查询失败的原因，其它关键字都不再需要了。否则，它必须有两个关键字：Interval：下载者在两次发送请求之间的时间间隔。Peers:一个字典的列表，每个字典包括以下关键字：Peer id，Ip，Port，分别对应peer所选择的id、ip地址或者dns名称、端口号。注意，如果某些事件发生，或者需要更多的peers，那么下载者可能不定期的发送请求，  
  
（downloader 通过 HTTP 的GET 命令来向 tracker 发送查询请求，tracker 响应一个peers 的列表）  
  
如果你想对元信息文件或者tracker查询进行扩展，那么需要同Bram Cohen协调，以确保所有的扩展都是兼容的。  
  
BT对等协议基于TCP，它很有效率，并不需要设置任何socket选项。（译注：BT对等协议指的是peer与peer之间交换信息的协议）  
对等的两个连接是对称的，消息在两个方向上同样的传递，数据也可以在任何一个方向上流动。  
一旦某个peer下载完了一个片断，并且也检查了它的完整性，那么它就向它所有的peers宣布它拥有了这个片断。  
连接的任何一端都包含两比特的状态信息：是否choked，是否感兴趣。Choking是通知对方，没有数据可以发送，除非unchoking发生。Choking的原因以及技术后文解释。  
  
一旦一端状态变为interested，而另一端变为非choking，那么数据传输就开始了。（也就是说，一个peer，如果想从它的某个peer那里得到数据，那么，它首先必须将它两之间的连接设置为 interested，其实就是发一个消息过去，而另一个peer，要检查它是否应该给这个家伙发送数据，如果它对这个家伙是unchoke，那么就可以给它发数据，否则还是不能给它数据）Interested状态必须一直被设置――任何时候。要用点技巧才能比较好的实现这个目的，但它使得下载者能够立刻知道哪些peers将开始下载。  
  
对等协议由一个握手开始，后面是循环的消息流，每个消息的前面，都有一个数字来表示消息的长度。握手的过程首先是先发送19，然后发送“BitTorrent protocol”。19就是“BitTorrent protocol”的长度。  
后续的所有的整数，都采用big-endian 来编码为4个字节  
在协议名称之后，是8个保留的字节，这些字节当前都设置为0。  
接下来对元文件中的 info 信息，通过 sha1 计算后得到的 hash值，20个字节长。接收消息方，也会对 info 进行一个 hash 运算，如果这两个结果不一样，那么说明对方要的文件，并不是自己所要提供的，所以切断连接。  
  
接下来是20个字节的 peer id。  
这就是握手过程  
  
接下来就是以消息长度开始的消息流，这是可选的。长度为0 的消息，用于保持连接的活动状态，被忽略。通常每隔2分钟发送一个这样的消息。  
  
其它类型的消息，都有一个字节长的消息类型，可能的值如下：  
  
‘choke’, ‘unchoe’, ‘interested’, not interested’类型的消息不再含有其它数据了。  
  
‘bitfield’永远也仅仅是第一个被发送的消息。它的数据实际是一个位图，如果downloader已经发送了某个片断，那么对应的位置1，否则置0。Downloaders如果一个片断也没有，可以忽略这个消息。（通过这个消息，能知道什么了？）  
  
‘have’类型的消息，后面的数据是一个简单的数字，它是下载者刚刚下载完并检查过完整性的片断的索引。（由此，可以看到，peer通过这种消息，很快就相互了解了谁都有什么片断）  
  
‘request’类型的消息，后面包含索引、开始位置和长度)长度是2的幂。当前的实现都用的是215 ，而关闭连接的时候，请求一个超过217的长度。(这种类型的消息，就是当一个peer希望另一个peer给它提供片断的时候，发出的请求)  
  
‘cancel’类型的消息，它的数据和’request’消息一样。它们通常只在下载趋向完成的时候发送，也就是在‘结束模式“阶段发送。在一次下载接近完成的时候，最后的几个片断需要很长时间才能下载完。为了确保最后几个片断尽快下载完，它向所有的peers发送下载请求。为了保证这不带来可怕的低效，一旦某个片断下载完成，它就其它peers发送’cancel’消息。（意思就是说，我不要这个片断了，你要是准备好了，也不用给我发了，可以想象，如果对方还是把数据发送过来了，那么这边必须忽略这些重复的数据）。  
  
‘piece’类型的消息，后面保护索引号、开始位置和实际的数据。注意，这种类型的消息和 ‘request’消息之间有潜在的联系（译注：因为通常有了request消息之后，才会响应‘piece’消息）。如果choke和unchoke消息发送的过于迅速，或者，传输速度变的很慢，那么可能会读到一些并不是所期望的片断。
（ 也就是说，有时候读到了一些片断，但这些片断并不是所想要的）

**BitTorrent协议标准之算法和策略**

BitTorrent将资源分成很多个piece，BitTorrent如何选择piece的下载次序，一个良好的块下载的调度策略可以增强网络的健壮性。  

1. **随机的第一个片断** 最简单，你可以采用随机的选择。在p2p中，当需要一个调度策略的时候，有时候随机直接采用随机，达到的效果也还不错，而且随机实现很简单。  
2. **最少的优先** 一个比较好的策略是，在网络中越是稀有的Piece越是优先下载，当然，如果计算得出的稀有程度相同，这时候就随机就可以了。这种办法可以提高整个系统的性能，因为如果全部随机的话，那万一大家一段时间都没有随机到某个piece，而这时候种子又下线了，那么所有人都下不到完整资源了。而且BT客户端下载了一个稀有piece后，就可以马上为其他人提供这个稀有的piece了。那么我们怎样计算一个piece的稀有程度呢，最理想的是整个网络全局的稀有程度，那最好了，但是在p2p网络中，单个peer是很难知道全局信息的，所以BitTorrent的下载策略计算稀有程度是在peer的它连接的所有其他peers中计算的，也就
是一个局部的信息。即便这样，这种方法仍然比随机选择要好的多。  
3. **严格的优先级** 由于piece又被分成多个block，请求和传输的最小单位是block，所以当某个piece的一个block获得了或者发出去了请求，那么剩下的block的优先级将最高。这样做是为了尽可能快获取一个完整的piece。  
4. **最后阶段模式**  下载的最后阶段。BT客户端应当向它连接的所有peers都发出请求，也就是冗余的请求，以便尽快完成下载。如果某个block接收到了，BT客户端应当立即向其他peers发出cancel包，取消请求。那这里也存在一个关键问题，如何来界定是否到达最后阶段了？这个问题也一直被很多人讨论，用百分比?用剩余block个数?等等。个人认为，用剩余block个数来界定是比较合理的。有一种就是取剩余block个数小于正在传输的block个数并且不超过20个的情况作为判断条件。  
5. **BT阻塞算法**（下面这些内容来自互联网）  
BT提倡peer之间尽可能多的相互共享。对于合作者，提供上传服务，对于不合作的，就阻塞对方。所以说，阻塞是一种临时的拒绝上传策略，虽然上传停止了，但是下载仍
然继续。在阻塞停止的时候，连接并不需要重新建立。阻塞算法并不属于BT对等协议（指peers 之间交互的协议）的技术部分，但是对提高性能是必要的。一个好的阻塞
算法应该利用所有可用的资源，为所有下载者提供一致可靠的下载速率，并适当惩罚那些只下载而不上传的peers。  
从技术层面上说，BT的每个peer一直与固定数量的其它 peers 保持疏通（通常是4个，(这个也太少了吧)），所以问题就变成了哪些peers应该保持疏通？
这种方法使得TCP的拥塞控制性能能够可靠的饱和上传容量。（也就是说，尽量让整个系统的上传能力达到最大）。  
严格的根据当前的下载速率来决定哪些peers应该保持疏通。令人惊讶的是，计算当前下载速率是个大难题。当前的实现实质上是一个每隔20秒的轮询。而原来的算法是对一个长时间的网络传输进行总计，但这种方法很差劲，因为由于资源可用或者不可用，带宽会变化的很快。  
为了避免因为频繁的阻塞和疏通peers造成的资源浪费，BT每隔10秒计算一次哪个peer需要被阻塞，然后将这种状态保持到下一个10秒。10秒已经足够使得TCP来调整它的传输性能到最大。  
optimistic unchoking  
如果只是简单的为提供最好的下载速率的peers们提供上载，那么就没有办法来发现那些空闲的连接是否比当前正使用的连接更好。为了解决这个问题，在任何时候，每个p
eer都拥有一个称为“optimistic
unchoking”的连接，这个连接总是保持疏通状态，而不管它的下载速率是怎样。每隔30秒，重新计算一次哪个连接应该是“optimistic
unchoking”。30秒足以让上载能力达到最大，下载能力也相应的达到最大。这种和针锋相对类似的思想非常的伟大。“optimistic
unchoking”非常和谐的与“囚徒困境”合作。  
反对歧视  
某些情况下，一个peer可能被它所有的peers都阻塞了，这种情况下，它将会保持较低的下载速率直到通过“optimistic unchoking”找到更好peers。为了减轻这种问题，如果一段时间过后，从某个peer那里一个片断也没有得到，那么这个peer认为自己被对方“怠慢”了，于是不再为对方提供上传，除非对方是“optimistic unchoking”。这种情况频繁发生，会导致多于一个的并发的“optimistic unchoking”。  
仅仅上传  
一旦某个peer完成了下载，它不能再通过下载速率（因为下载速率已经为0了）来决定为哪些 peers 提供上载了。目前采用的解决办法是，优先选择那些从它这里得到更好的上载速率的peers。这样的理由是可以尽可能的利用上载带宽。

**BitTorrent协议标准之Peer状态**

BT的Peer之间通过TCP进行通讯，相互交换piece（实际上交换的最小单位是block），最终达到下载整个资源的目的。  
一个BT的客户端（本地节点）对于每个与它连接上的节点都维护两种状态信息，choked（阻塞）和interested（关注），它们的含义分别是：  
choked（阻塞）:当一个远端节点把BT客户端（本地节点）阻塞住的时候，BT客户端向远端节点发送的所有请求block的请求包将不会被回应，当BT客户端发现自己被远端节点阻塞的时候，就不应当向该节点发送请求。  
interested（关注）:当BT客户端（本地节点）被远端节点关注时，远端节点会向BT客户端发送请求（当然如果BT客户端把远端节点阻塞住的话，就不会），这说明BT客户端（本地节点）有远端节点所需要的数据。  
上面的解释中都只说了一方主动，另一方被动的情况，其实“作用”是相互的，对于本地节点和远端节点其实是这样的情况：  
am_choking:本地节点把远端节点阻塞  
am_interested:本地节点关注远端节点  
peer_choking:本地节点被远端节点阻塞  
peer_interested:本地节点被远端节点关注  
在连接初始建立的时候，状态是双方互相被阻塞，互相不关注。  
对于这些状态的表示，我们可以用每个Bit表示一个状态，用&操作取出状态值。  
只有在本地节点关注远端节点并且远端节点没有阻塞本地节点的时候，本地节点才能从远端节点下载block，同样，只有在本地节点被远端节点关注并且本地节点没有把远端节点阻塞的时候，本地节点才会向远端节点上传数据。  
需要注意的是，尽管节点被阻塞或者不关注，连接还是不关闭，而是要保持更新状态，除非客户端（本地节点）在一些调度算法上把没用的节点给淘汰关闭。至于多少个Peer后才需要淘汰，那是属于调度策略的事情，各个客户端实现可能不一样，一般30个peer已经够用，建议不要超过55个peer，节点再增多，不见得能把速度提高多少。

BitTorrent**协议标准之数据包格式**

BT中Peer和Peer之间交互的数据包的格式除了握手包之外都是:包长度(Int)+包体。  
当两个Peer连接后，要首先向对方发送握手包，如果握手失败，连接将关闭。握手包的格式是：  
字符串长度+字符串+保留字段+info_hash+peer_id  
字符串长度:后面的字符串长度，1个Byte  
字符串：标识协议的字符串。在1.0的bt协议中为"BitTorrent protocol"  
保留字段：8个字节，用于协议扩展，无扩展的时候全为0，使用的时候从后向前开始使用。  
info_hash:20个字节，就是用于向tracker请求的那个info_hash  
peer_id:20个字节，各个BT软件对peer_id的命名方法不一样，大致有几种类型，这个以后再说。  
当本地节点主动连接到远端节点后，就应当立即向远端节点发送握手包，远端节点接收连接后等等握手包的到来，当握手包接收后立即回应握手包。当远端节点接收到握手包后，它会首先看info_hash字段所代表的任务是否存在，若不存在，那就应该关闭连接。当远端节点回应握手包后，本地节点应当判断该节点的peer_id，如果它有从tracker那里得知远端节点的peer_id，若发现pere_id不符合，本地节点应当关闭连接。

剩下的Peer之间的所有交互数据包格式是：包长度(Int，4个Byte长度)+包类型(1个Byte)+消息体，前面的包长度和包类型是定的，后面的消息体因包类型不同而具体格式不同。主要的包有下面几种：  
keep-alive:  
keep-alive包（保活/心跳包）就是一个包长度设置为0的包，也没有包类型字段，其内容就是0000，它的时间间隔是2分钟。  
choke:  
把接收方阻塞  
unchoke:  
把接收方取消阻塞  
interested:  
关注接收方  
not interested:  
取消关注接收方  
have:  
告诉接收方的Peer，发送方拥有某一个piece的数据，piece的index是以0开始的  
这个包是非常频繁的包，BT客户端的实现应该设计一些技巧在不减少信息发布的情况下减少这个包的传输。比如某个Peer已经有该piece了，显然就不应该向它发送了。或者某个Peer它选择性下载，根本不需要下载这个piece，那也不要给它发送了。或者已经告诉过它一次了，就不要再告诉它了，等等。  
bitfield:  
bitfield包一般在两个节点完成握手之后就要发送，当然，如果节点一个piece都没有，就没有必要发送了。这个包是变长的，取决于有多少个 piece，X就是bitfield的长度，bitfield里第一个字节的高位bit就对应着第一个piece(index=0)。由于piece的个数不一定能被8整除，所以最后可能有没有用到的bit，那些bit全设为0就行了。peer在接收到该包后，要判断bitfield是否合法，即 piece个数是否合法，不合法则要关闭连接。  
request:  
数据请求包，index:整型，表示piece index，begin:整型，表示offset in the piece。length:整型，表示请求的数据的
长度。关于这个block的长度，众说纷纭，有的说16K，有的32K，有的说只要不超过128K就好，等等，我觉得，这个得看实现BT协议的人，如果它的客户端做的就只支持16K，它有很多用户了，你再做BT客户端，你要跟它兼容，你就得支持16K，所以我觉得，自己在程序中控制只要小于128K的请求都回应，向其他人发送request的时候，就根据它是什么客户端，默认就给它发个16K的这种就可以了，整这么复杂干啥~  
piece:  
回应的Block数据，X便是block的长度，index是piece
index，begin是block在piece中的offset，block便是二进制数据了。  
cancel:  
这个包跟request包一样，就是type不一样，它就表示把对应的那个request给取消掉。  
port:  
port包，是用来告诉接收方节点，发送方节点支持DHT，并且DHT监听的端口是listen port。

**从tracker上获取peer列表**  
 从torrent文件中得到了tracker列表后,接下来的工作就是获取peer列表.  
tracker使用http协议.客户端向服务器发送标准的GET请求,就可以得到这个列表.tracker返回的信息是bencode编码.  
向tracker发送的GET请求有如下一些参数:  
info_hash(必须):  
    torrent文件中info字段的sha1.torrent文件解析器中已经计算此值,保存在CTorrentParser的m_Infohash成员中.  
peer_id(必须):  
    节点ID,长20字节.通常每一个下载产生一个相应的ID.通过peer_id可以识别大多数客户端类型.  
ip(可选):  
    客户端指定的期望其他节点与本地交互时连接的IP.一般来说不用指定此参数,除非客户端使用了代理或者端口映射.  
port(可选):  
    本地侦听的端口.  
uploaded:  
    已经上传的字节数.  
download:  
    已经下载的字节数.  
left:  
    未下载的字节数.  
event(可选):  
    此参数可以是如下的值:  
        started:下载开始  
        completed:下载完毕  
        stopped:下载停止  
compact(可选):  
    此参数值为1,表示期望得到紧凑模式的节点列表.  
    否则表示期望得到普通模式的节点列表.      
no_peer_id(可选):  
        其值为1,表示不需要节点id信息.

通常tracker会返回错误代码200.  
如果返回的bencode编码中包含failure reason字段,则表示处理请求失败,此字段的值即为失败原因.  
如果请求成功,则有两个字段是必须出现的:  
    peers:节点列表  
    interval:服务器期望的下次查询间隔时间,单位为秒  
通常还会有如下一些字段出现:  
    done peers:下载完毕的节点个数  
    num peers或者incomplete: 当前下载的节点个数

普通模式的回复其peers字段包括ip,port两个字段,如果未指定no_peer_id参数还将包括peer id字段.  
下面是普通模式的回复例子:  
        d8:intervali3600e5:peersld2:ip13:192.168.24.527:peer id20:{peer_id}4:porti2001eed2:ip11:192.168.0.37:peer id20:{peer_id}4:porti6889eeee

d8:intervali3600e5:peersld2:ip13:192.168.24.524:porti2001eed2:ip11:192.168.0.34:porti6889eeee

紧凑模式的回复其peers字段是一个如下结构的数组:  

	struct PEER  
	{  
	     DWORD  IP;//节点IP  
	     WORD  Port;//节点端口  
	};   
	例如:192.168.24.52:2001 => 0xC0 0xA8 0x18 0x34 0xD1 0x07

下面是紧凑模式的回复例子:  
         
	d8:intervali3600e5:peers12:{12 characters of binary data}e


BT协议分析 收藏  
一 BT系统的组成结构

  1 普通的Web服务器：   例如Apache或IIS服务器

2 一个静态的种子文件：   即.Torrent文件，采用Bencoding编码

3  Tracker服务器：        追踪下载同一文件的用户

4 终端用户的Web浏览器：用于下载种子文件

5  BT客户端：            例如BitCommet，BitSpirit



二 种子文件

1 格式介绍

  种子文件采用bencoding编码，整个文件包含以下关键字：

	announce：               Tracke服务器的UR以字符串)。
	announce-list(可选):  备用Tracker服务器列表(列表)。
	creation date(可选):  种子创建的时I司。
	comment(可选):        备注(字符串)。
	created by(可选):      创建人或创建程序的信息(字符串)。
	Info:                          一个字典结构，包含文件的主要信息，分二种情况:单文件结构或多文件结构

单文件结构如下:

    length:                 文件长度，单位字节(整数)。
    md5sum(可选):  长32个字符的文件的MD5校验和，BT不使用这个值，只是为了兼容一些程序所保留!(字符串)。
    Name:                 文件名(字符串)。
    Piece length:        每个块的大小，单位字节(整数)。
    Pieces:                每个块的20个字节的SHAT Hash的值(二进制格式)。

多文件结构如下:

    files:                    一个字典结构。
    Length:                文件长度，单位字节(整数)。
    md5sum(可选):   同单文件结构中相同。
	Path:                   文件的路径和名字，是一个列表结构，如test\test.txt列表 为 14:test8test.txte 
    Name:                 最上层的目录名字(字符串))o
    Piece length:        同单文件结构中相同。
    Pieces:                同单文件结构中相同。


2 Bencoding编码规则：

  （1）字符串编码：<字符串长度>:<字符串>

       例如字符串spam被编码为4:spam

   （2）整数编码：  i<整数>e

       例如数字23表示为i23e，-23表示为i-23e，0为i0e

   （3）列表编码：  1e

       例如l4:spam4:eggse表示两个字符串“spam”，“eggs”

 （4）字典编码： de

       例如d3:cow3:moo4:spam4:eggse表示{“cow“=“moo“, “spam“=“eggs“}
          d4:path3:C:\8:filename8:test.txte表示{"path"="C:\","filename"="test.txt"}



3 文件举例（以下是用记事本打开.torrent文件）

```
d8:announce40:udp://tracker.bitcomet.net:8080/announce13:creation datei1175422
660e8:encoding3:GBK4:infod6:lengthi7080818e4:name18:gettingoveryou.mp310:name.
utf-818:gettingoveryou.mp312:piece
lengthi1048576e6:pieces140:琚瀲⒂!堯??M挷咲i?屩轩@鏋EU轒50-?鷰靀F?@憸%l?Iy~
??R?襉軦d[1]f岤\>@陗罏?樯燐#o?翟木懣槾"霡­瓼W?棈Dk?鰛殴鴞?チY庖}0!$苶7:privatei1ee13
:publisher-url7:http://19:publisher-url.utf-87:http://e
```

三 BT系统的通信过程（没有采用DHT时）

BT客户端通过种子文件获得相关信息，在下载过程中定期与Tracker服务器交互（通过http协议或者https协议）。Tracker定期从下载者处接受信息，并返回一个Peers列表。

下载者周期性的向Tracker登记，Tracker根据各个下载者的登记信息不断更新Peers列表。因此BT客户端定时的向Tracker发出获取Peers列表
的请求，以便客户端能获得更快、更多的Peers，使得它的下载速度更快。

BT客户端之间根据Peers列表的信息，向相应的BT客户端发起连接，下载需要的部分，从而实现了各个客户端之间的相互通信。这种连接是基于TCP的BT对等协议。

四 Tracker查询

	Tracker通过HTTP的GET命令的参数来接收信息BT客户单发送给Tracker服务器GET请求，包含一下关键字：

  Info_ hash:     种子文件中info部分的SHA-1 (Secure Hash Algorithm 1) ,  20

	字节长。每一个片断都采用SHA-I，当BT客户端每下载完一个片断，都需要验证数据的正确性。

  PeerId:          下载者的ID，一个20字节长的字符串。每个下载者在开始一次新的下载之前，随机创建一个ID 。

  IP（可选):    给出了peer的IP地址。

  Port:               peer所监听的端口。下载者通常在在6881端口上监听，如果该端口

被占用，就会尝试6882，如果还被占用，那么会一直尝试到6889，如果都被占用，那么就放弃监听。

  Uploaded:     已经上载的数据大小。

  Downloaded: 已经下载的数据大小。

  Left:              该Peer还有多少数据没有下载完。

  Event(可选)：值可以为started, completed或stopped之一

  
五 Tracker响应

  BT客户端向Tracker查询后，Track会发出响应。响应是用Bencoding编码的字典。

   1 如果响应中有关键字failure reason，则表示查询失败，其值为一个字符串，解释失败原因。不再有其它关键字。

   2 否则有两个关键字：

     Interval:   两次发送请求的时间间隔

     Peers:      一个字典的列表，每个字典包括一下关键字Peer Id ， IP ,  Port，分别对应Peer所选择的ID, IP地址。



六 BT对等协议

是基于TCP的应用层协议，用于Peer之间交换信息。连接后两个Peer之间是对称的，数据可以双向传送。当一个Peer下载完一个片段后，就会向所有Peer宣布它拥有了这个片段。包括一下几个消息：

1 Handshake消息

2 Bitfield消息

3 Have消息

4 Request消息

5 Cancel消息

6 Choke消息

7 Interested消息

8 keep-alive消息



注：在没有采用DHT（Distributed Hash Table或Dynamic Hash Table）技术时，对等体之间的互相发现需要通过Tracker
服务器，因此如果没有Tracker服务器，BT客户端就不会获得新加入的用户的信息，速度会受很大影响甚至根本无法下载。现在很多BT软件采用DHT技术的Kad算法，可以不通过服务器实现对等体之间的相互定位与发现，例如电驴就采用了kad网络。

  
本文来自CSDN博客，转载请标明出处：<http://blog.csdn.net/zhh157/archive/2008/10/14/3072508.aspx>



BitTorrent 协议规范：  
  
BitTorrent 是一种分发文件的协议。它通过URL来识别内容，并且可以无缝的和web进行交互。它基于HTTP协议，它的优势是：如果有多个下载者并发的下载同一个文件，那么，每个下载者也同时为其它下载者上传文件，这样，文件源可以支持大量的用户进行下载，而只带来适当的负载的增长。（译注：因为大量的负载被均衡到整个系统中，所以提供源文件的机器的负载只有少量增长）

一个BT文件分布系统由下列实体组成：  
  
一个普通的web服务器  
  
一个静态的“元信息”文件  
  
一个跟踪（tracker）服务器  
  
终端用户的web浏览器  
  
终端下载者

理想的情况是多个终端用户在下载同一个文件。  
  
要提供文件共享，那么一台主机需要执行以下步骤：  
  
?运行一个 tracker服务器（或者，已经有一个tracker服务器在运行了也可以）  
  
?运行一个web服务器，例如apache，或者已经有一个web服务器在运行了。  
  
?在web服务器上，将文件扩展名.torrent 和MIME类型 application/x-bittorrent关联起来（或者已经关联了）  
  
?根据 tracker服务器的 URL 和要共享的文件来创建一个“元信息”文件（.torrent）。  
  
?将“元信息”文件发布到web服务器上  
  
?在某个web页面上，添加一个到“元信息”文件的链接。  
  
?运行一个已经拥有完整文件的下载者（被成为’origin’，或者’seed’，种子）

要开始下载文件，那么终端用户执行以下步骤：  
  
?安装 BT（或者已经安装）  
  
?访问提供 .torrent 文件的web服务器  
  
?点击到 .torrent 文件的链接（译注：这时候，bt会弹出一个对话框）  
  
?选择要把下载的文件保存到哪里？或者是一次断点续传  
  
?等待下载的完成。  
  
?结束bt程序的运行（如果不主动结束，那么bt会一直为其它人提供文件上传）

各个部分之间的连通性如下：  
  
网站负责提供一个静态的文件，而把BT辅助程序（客户端）放在客户端机器上。  
  
Trackers从所有下载者处接收信息，并返回给它们一个随机的peers的列表。这种交互是通过HTTP或HTTPS协议来完成的。  
  
下载者周期性的向tracker登记，使得tracker能了解它们的进度；下载者之间通过直接连接进行数据的上传和下载。这种连接使用的是BitTorrent对等协议，它基于TCP。  
  
Origin只负责上传，从不下载，因为它已经拥有了完整的文件。Origin是必须的。

元文件和tracker的响应都采用的是一种简单、有效、可扩展的格式，被称为bencoding，它可以包含字符串和整数。由于对不需要的字典关键字可以忽略，所以这种格式具有可扩展性，其它选项以后可以方便的加进来。

Bencoding格式如下：  
  
对于字符串，首先是一个字符串的长度，然后是冒号，后面跟着实际的字符串，例如：4:spam，就是“ spam”  
  
整数编码如下，以 ‘i’ 开始，然后10进制的整数值，最后以’e’结尾。例如，i3e表示3，I-3e表示-3。整数没有大小限制。I-0e是无效的。除了
i0e外，所以以0起始的整数都无效。I0e当然表示0。  
  
列表编码如下，以’l’开始，接下来是列表值的编码（也采用bencoded编码），最后以’e’结束。例如：l4:spam4:eggse 表示 [‘spam’, ‘eggs’]。  
  
字典编码如下，以’d’开始，接下来是可选的keys和它对应的值，最户以’e’结束。例如：d3:cow3:moo4:spam4:eggse，表示{‘cow’:
’moo’,’spam’:’eggs’}，而d4:spaml1:al:bee 表示{‘spam’:[‘a’,’b’]}。键值必须是字符串，而且已经排序（并非是按照字母顺序排序，而是根据原始的字符串进行排序）。

元文件是采用bencoded编码的字典，包括以下关键字：

announce tracker的服务器

info 它实际上是一个字典，包括以下关键字：

Name：  
  
一个字符串，在保存文件的时候，作为一个建议值。仅仅是个建议而已，你可以用别的名字保存文件。  
  
Piece length：  
  
为了更好的传输，文件被分隔成等长的片断，除了最后一个片断以外，这个值就是片断的大小。片断大小几乎一直都是2的幂，最常用的是 256k  
  
Pieces：  
  
一个长度为20的整数倍的字符串。它将再被分隔为20字节长的字符串，每个子串都是相应片断的hash值。

此外，还有一个length或files的关键字，这两个关键字只能出现一个。如果是length，那么表示要下载的仅仅是单个文件，如果是files那么要下载的是一个目录中的多个文件。  
  
如果是单个文件，那么length是该文件的长度。

为了能支持其它关键字，对于多个文件的情况，也把它当作一个文件来看，也就是按照文件出现的顺序，把每个文件的信息连接起来，形成一个字符串。每个文件的信息实际上也是一个字典，包括以下关键字：  
  
Length：文件长度  
  
Path：子目录名称的列表，列表最后一项是文件的实际名称。（不允许出现列表为空的情况）。  
  
Name：在单文件情况下，name是文件的名称，而在多文件情况下，name是目录的名称。

Tracker查询。Trakcer通过HTTP的GET命令的参数来接收信息，而响应给对方（也就是下载者）的是经过bencoded编码的消息。注意，尽管当前的tracker的实现需要一个web服务器，它实际上可以运行的更轻便一些，例如，作为apache的一个模块。  
  
Tracker GET requests have the following keys:

发送给Tracker的GET请求，包含以下关键字：

Info_hash：  
  
元文件中info部分的sha hash，20字节长。这个字符创几乎肯定需要被转义（译注：在URL中，有些字符不能出现，必须通过unicode进行编码）

Peer_id：  
  
下载者的id，一个20字节长的字符串。每个下载者在开始一次新的下载之前，需要随机创建这个id。这个字符串通常也需要被转义。

Ip：  
  
一个可选的参数，给出了peer的ip地址（或者dns名称？）。通常用在origin身上，如果它和tracker在同一个机器上。

Port：  
  
peer所监听的端口。下载者通常在在 6881 端口上监听，如果该端口被占用，那么会一直尝试到 6889，如果都被占用，那么就放弃监听。

Uploaded：  
  
已经上载的数据大小，十进制表示。

Downloaded：  
  
已经下载的数据大小，十进制表示

Left：  
  
该peer还有多少数据没有下载完，十进制表示。注意，这个值不能根据文件长度和已下载数据大小计算出来，因为很可能是断点续传，如果因为检查文件完整性失败而必须重新下载的时候，这也提供了一个机会。

Event：  
  
一个可选的关键字，值是started、compted或者stopped之一（也可以为空，不做处理）。如果不出现该关键字，。在一次下载刚开始的时候，该值被设置为started，在下载完成之后，设置为completed。如果下载者停止了下载，那么该值设置为stopped。

Tracker的响应是用bencoded编码的字典。如果tracker的响应中有一个关键字failure reason，那么它对应的是一个字符串，用来解释查询失败的原因，其它关键字都不再需要了。否则，它必须有两个关键字：Interval：下载者在两次发送请求之间的时间间隔。Peers:一个字典的列表，每个字典包括以下关键字：Peer id，Ip，Port，分别对应peer所选择的id、ip地址或者dns名称、端口号。注意，如果某些事件发生，或者需要更多的peers，那么下载者可能不定期的发送请求，

（downloader 通过 HTTP 的GET 命令来向 tracker 发送查询请求，tracker 响应一个peers 的列表）

如果你想对元信息文件或者tracker查询进行扩展，那么需要同Bram Cohen协调，以确保所有的扩展都是兼容的。

BT对等协议基于TCP，它很有效率，并不需要设置任何socket选项。（BT对等协议指的是peer与peer之间交换信息的协议）  
  
对等的两个连接是对称的，消息在两个方向上同样的传递，数据也可以在任何一个方向上流动。  
  
一旦某个peer下载完了一个片断，并且也检查了它的完整性，那么它就向它所有的peers宣布它拥有了这个片断。  
  
连接的任何一端都包含两比特的状态信息：是否choked，是否感兴趣。Choking是通知对方，没有数据可以发送，除非unchoking发生。Choking的原因以及技术后文解释。

一旦一端状态变为interested，而另一端变为非choking，那么数据传输就开始了。（也就是说，一个peer，如果想从它的某个peer那里得到数据，那么，它首先必须将它两之间的连接设置为 interested，其实就是发一个消息过去，而另一个peer，要检查它是否应该给这个家伙发送数据，如果它对这个家伙是unchoke，那么就可以给它发数据，否则还是不能给它数据）Interested状态必须一直被设置――任何时候。要用点技巧才能比较好的实现这个目的，但它使得下载者能够立刻知道哪些peers将开始下载。

对等协议由一个握手开始，后面是循环的消息流，每个消息的前面，都有一个数字来表示消息的长度。握手的过程首先是先发送19，然后发送“BitTorrent protocol”。19就是“BitTorrent protocol”的长度。  
  
后续的所有的整数，都采用big-endian 来编码为4个字节  
  
在协议名称之后，是8个保留的字节，这些字节当前都设置为0。  
  
接下来对元文件中的 info 信息，通过 sha1 计算后得到的 hash值，20个字节长。接收消息方，也会对 info 进行一个 hash 运算，如果这两个结果不一样，那么说明对方要的文件，并不是自己所要提供的，所以切断连接。

接下来是20个字节的 peer id。  
  
这就是握手过程

接下来就是以消息长度开始的消息流，这是可选的。长度为0 的消息，用于保持连接的活动状态，被忽略。通常每隔2分钟发送一个这样的消息。

其它类型的消息，都有一个字节长的消息类型，可能的值如下：

‘choke’, ‘unchoe’, ‘interested’, not interested’类型的消息不再含有其它数据了。

‘bitfield’永远也仅仅是第一个被发送的消息。它的数据实际是一个位图，如果downloader已经发送了某个片断，那么对应的位置1，否则置0。Downloaders如果一个片断也没有，可以忽略这个消息。（通过这个消息，能知道什么了？）

‘have’类型的消息，后面的数据是一个简单的数字，它是下载者刚刚下载完并检查过完整性的片断的索引。（由此，可以看到，peer通过这种消息，很快就相互了解了谁都有什么片断）

‘request’类型的消息，后面包含索引、开始位置和长度)长度是2的幂。当前的实现都用的是215 ，而关闭连接的时候，请求一个超过217的长度。(这种类型的消息，就是当一个peer希望另一个peer给它提供片断的时候，发出的请求)

‘cancel’类型的消息，它的数据和’request’消息一样。它们通常只在下载趋向完成的时候发送，也就是在‘结束模式“阶段发送。在一次下载接近完成的时候，最后的几个片断需要很长时间才能下载完。为了确保最后几个片断尽快下载完，它向所有的peers发送下载请求。为了保证这不带来可怕的低效，一旦某个片断下载完成，它就其它peers发送’cancel’消息。（意思就是说，我不要这个片断了，你要是准备好了，也不用给我发了，可以想象，如果对方还是把数据发送过来了，那么这边必须忽略这些重复的数据）。

‘piece’类型的消息，后面保护索引号、开始位置和实际的数据。注意，这种类型的消息和 ‘request’消息之间有潜在的联系（译注：因为通常有了request消息之后，才会响应‘piece’消息）。如果choke和unchoke消息发送的过于迅速，或者，传输速度变的很慢，那么可能会读到一些并不是所期望的片断。
（ 也就是说，有时候读到了一些片断，但这些片断并不是所想要的）


Torrent文件解析

2009-05-11 11:37

BT种子文件使用了一种叫bencoding的编码方法来保存数据。

bencoding有四种类型的数据：srings(字符串)，integers(整数)，lists(列表)，dictionaries(字典)  
编码规则如下：  
(1)strings(字符串)编码为：<字符串长度>：<字符串>  
例如： 4:test 表示为字符串"test"  
4:例子 表示为字符串“例子”  
字符串长度单位为字节  
没开始或结束标记

(2)integers(整数)编码为：i<整数>e  
开始标记i，结束标记为e  
例如： i1234e 表示为整数1234  
i-1234e 表示为整数-1234  
整数没有大小限制  
i0e 表示为整数0  
i-0e 为非法  
以0开头的为非法如： i01234e 为非法

(3)lists(列表)编码为：l>e  
开始标记为l,结束标记为e  
列表里可以包含任何bencoding编码类型，包括整数，字符串，列表，字典。  
例如： l4:test5:abcdee 表示为二个字符串["test","abcde"]

(4)dictionaries(字典)编码为d>e  
开始标记为d,结束标记为e  
关键字必须为bencoding字符串  
值可以为任何bencoding编码类型  
例如： d3:agei20ee 表示为{"age"=20}  
d4:path3:C:"8:filename8:test.txte

表示为{"path"="C:"","filename"="test.txt"}

(5)具体文件结构如下：  
全部内容必须都为bencoding编码类型。  
整个文件为一个字典结构,包含如下关键字  
announce:tracker服务器的URL(字符串)  
announce-list(可选):备用tracker服务器列表(列表)  
creation date(可选):种子创建的时间，Unix标准时间格式，从1970 1月1日 00:00:00到创建时间的秒数(整数)  
comment(可选):备注(字符串)  
created by(可选):创建人或创建程序的信息(字符串)  
info:一个字典结构，包含文件的主要信息，为分二种情况：单文件结构或多文件结构  
单文件结构如下：  
          length:文件长度，单位字节(整数)  
          md5sum(可选)：长32个字符的文件的MD5校验和，BT不使用这个值，只是为了兼容一些程序所保留!(字符串)  
          name:文件名(字符串)  
          piece length:每个块的大小，单位字节(整数)  
          pieces:每个块的20个字节的SHA1 Hash的值(二进制格式)  
多文件结构如下：  
           files:一个字典结构  
                 length:文件长度，单位字节(整数)  
                  md5sum(可选):同单文件结构中相同  
                 path:文件的路径和名字，是一个列表结构，如"test"test.txt 列表为l4:test8test.txte  
          name:最上层的目录名字(字符串)  
          piece length:同单文件结构中相同  
          pieces:同单文件结构中相同   
(6)实例：  
用记事本打开一个.torrent可以看来类似如下内容  
d8:announce35:http://www.manfen.net:7802/announce13:creation datei1076675108e4
:infod6:lengthi17799e4:name62:MICROSOFT.WINDOWS.2000.AND.NT4.SOURCE.CODE-
SCENELEADER.torrent12:piece lengthi32768e6:pieces20:?W ?躐?緕排T酆ee

很容易看出  
announce＝<http://www.manfen.net:7802/announce>  
creation date＝1076675108秒(02/13/04 20:25:08)  
文件名=MICROSOFT.WINDOWS.2000.AND.NT4.SOURCE.CODE-SCENELEADER.torrent  
文件大小＝17799字节  
文件块大小＝32768字节  


<hr>



####<p>原文出处：<a href='https://wiki.theory.org/index.php/BitTorrentSpecification' target='blank'>BitTorrentSpecification</a></p>

###Identification

[BitTorrent](/index.php?title=BitTorrent&action=edit&redlink=1) is a peer-to-
peer file sharing protocol designed by Bram Cohen. Visit his pages at <http://www.bittorrent.com> BitTorrent is designed to facilitate file transfers among multiple peers across unreliable networks.

###Purpose

The purpose of this specification is to document version 1.0 of the BitTorrent protocol specification in detail. Bram's [protocol specification
page](http://bittorrent.org/beps/bep_0003.html) outlines the protocol in somewhat general terms, and lacks behaviorial detail in some areas. The hope is that this document will become a **formal** specification, written in clear, unambiguous terms, which can be used as a basis for discussion and implementation in the future.

This document is intended to be maintained and used by the BitTorrent development community. Everyone is invited to contribute to this document, with the understanding that the content here is intended to represent the current protocol, which is already deployed in a number of existing client
implementations.

This is not the place to suggest feature requests. For that, please go to the [mailing list](http://lists.ibiblio.org/mailman/listinfo/bittorrent).

###Scope

This document applies to the first version (i.e. version 1.0) of the BitTorrent protocol specification. Currently, this applies to the torrent file
structure, peer wire protocol, and the Tracker HTTP/HTTPS protocol specifications. As newer revisions of each protocol are defined, they should be specified on their own separate pages, **not here**.

###Related Documents

  * [Official protocol specification](http://bittorrent.org/beps/bep_0003.html)
  * [Developer and user wishlist](/index.php/BitTorrentWishList)
  * [Tracker protocol extensions](/index.php/BitTorrentTrackerExtensions)

###Conventions

In this document, a number of conventions are used in an attempt to present information in a concise and unambiguous fashion.

  * _peer_ v/s _client_: In this document, a _peer_ is any BitTorrent client participating in a download. The _client_ is also a peer, however it is the BitTorrent client that is running on the local machine. Readers of this specification may choose to think of themselves as the _client_ which connects to numerous _peers_.
  * _piece_ v/s _block_: In this document, a _piece_ refers to a portion of the downloaded data that is described in the metainfo file, which can be verified by a SHA1 hash. A _block_ is a portion of data that a _client_ may request from a _peer_. Two or more _blocks_ make up a whole _piece_, which may then be verified.
  * _defacto standard_: Large blocks of text in _italics_ indicates a practice so common in various client implementations of BitTorrent that it is considered a defacto standard.

In order to help others find recent changes that have been made to this document, please fill out the **Summary:** field when you do a edit. This should contain a brief (i.e. one-line) entry for each major change that you've made to the document.

###Bencoding

Bencoding is a way to specify and organize data in a terse format. It supports the following types: byte strings, integers, lists, and dictionaries.

####Byte Strings

Byte strings are encoded as follows: _<string length encoded in base ten ASCII>**:**<string data>_  
Note that there is no constant beginning delimiter, and no ending delimiter.

    **Example**: _**4:**_ _spam_ represents the string "spam"   

    **Example**: _**0:**_ represents the empty string ""

####Integers

Integers are encoded as follows: _**i**<integer encoded in base ten ASCII>**e**_  
The initial **i** and trailing **e** are beginning and ending delimiters.

    **Example**: _**i**3**e**_ represents the integer "3"
    **Example**: _**i**-3**e**_ represents the integer "-3"

_**i**-0**e**_ is invalid. All encodings with a leading zero, such as
_**i**03**e**_, are invalid, other than _**i**0**e**_, which of course corresponds to the integer "0".

  * _NOTE:_ The maximum number of bit of this integer is unspecified, but to handle it as a signed 64bit integer is mandatory to handle "large files" aka .torrent for more that 4Gbyte.

####Lists

Lists are encoded as follows: _**l**<bencoded values>**e**_  
The initial **l** and trailing **e** are beginning and ending delimiters.
Lists may contain any bencoded type, including integers, strings, dictionaries, and even lists within other lists.

    **Example**: _**l**4:spam4:eggs**e**_ represents the list of two strings: [ "spam", "eggs" ]   

    **Example**: _**le**_ represents an empty list: []

####Dictionaries

Dictionaries are encoded as follows: _**d**<bencoded string><bencoded
element>**e**_  
The initial **d** and trailing **e** are the beginning and ending delimiters.
Note that the keys must be bencoded strings. The values may be any bencoded type, including integers, strings, lists, and other dictionaries. Keys must be strings and appear in sorted order (sorted as raw strings, not alphanumerics).
The strings should be compared using a binary comparison, not a culture-specific "natural" comparison.

    **Example**: _**d**3:cow3:moo4:spam4:eggs**e**_ represents the dictionary { "cow" => "moo", "spam" => "eggs" }   

    **Example**: _**d**4:spaml1:a1:be**e**_ represents the dictionary { "spam" => [ "a", "b" ] }   

    **Example**: _**d**9:publisher3:bob17:publisher-webpage15:www.example.com18:publisher.location4:home**e**_ represents { "publisher" => "bob", "publisher-webpage" => "www.example.com", "publisher.location" => "home" }   

    **Example**: _**de**_ represents an empty dictionary {}

####Implementations

  * [C](https://sourceforge.net/p/funzix/code/ci/master/tree/bencode/) by [Mike Frysinger](/index.php?title=User:Vapier&action=edit&redlink=1)
  * [C](https://github.com/willemt/CHeaplessBencodeReader)
  * [C](https://github.com/cwyang/bencode) by [Chul-Woong Yang](https://github.com/cwyang)
  * [C#](https://github.com/Krusen/BencodeNET) by [Søren Kruse](https://twitter.com/sorenkrusen)
  * [C#](http://snipplr.com/view/37790/bencoding-encoder-and-decoder/) by [SuprDewd](/index.php?title=User:SuprDewd&action=edit&redlink=1)
  * [C#](http://bencode.codeplex.com/) by [LordMike](/index.php?title=User:LordMike&action=edit&redlink=1)
  * [Clojure](http://nakkaya.com/2009/11/02/decoding-bencoded-streams-in-clojure/) by [nakkaya](/index.php?title=User:Nakkaya&action=edit&redlink=1)
  * [Common Lisp](https://gist.github.com/2021424) by [osa1](/index.php?title=User:Osa1&action=edit&redlink=1)
  * [Elixir](https://github.com/folz/bento) by [Rodney Folz](https://twitter.com/rodneyfolz)
  * [Erlang](/index.php/Decoding_encoding_bencoded_data_with_erlang)
  * [Erlang](https://github.com/galina/bencoded) by [ladybug](/index.php?title=User:Ladybug&action=edit&redlink=1)
  * [Go](https://github.com/marksamman/bencode) by [Mark Samman](https://twitter.com/marksamman)
  * [Decoding encoding bencoded data with haskell](/index.php/Decoding_encoding_bencoded_data_with_haskell) by [Edi](/index.php?title=User:Edi&action=edit&redlink=1)
  * [Haskell](http://hackage.haskell.org/package/bencode) by [Mhitza](/index.php?title=User:Mhitza&action=edit&redlink=1)
  * [Java](https://bitbucket.org/gyuriX/bencoder) by [gyurix](/index.php?title=User:Gyurix&action=edit&redlink=1)
  * [Java](https://bitbucket.org/frazboyz/bencoder) by [Frazboyz](/index.php?title=User:Frazboyz&action=edit&redlink=1)
  * [JavaScript](http://demon.tw/my-work/javascript-bencode.html) by [Demon](http://demon.tw)
  * [JavaScript](https://github.com/benjreinhart/bencode-js) by [Ben Reinhart](http://benreinhart.com)
  * [JScript](/index.php/JScript:_Converting_a_torrent_file_to_a_JScript_dictionary) by [Sergej B.](/index.php?title=User:Sergej_B.&action=edit&redlink=1)
  * [Objective-C](http://www.stupendous.net/projects/bencoding-obj-c-class/) by [Chrome](/index.php?title=User:Chrome&action=edit&redlink=1)
  * [OCaml](http://cvs.savannah.gnu.org/viewvc/mldonkey/mldonkey/src/networks/bittorrent/bencode.ml?view=markup) by [MLDonkey](http://mldonkey.sourceforge.net/Main_Page)
  * [Perl](http://search.cpan.org/perldoc?Net::BitTorrent::Protocol::BEP03::Bencode)
  * [PHP](/index.php/Decoding_encoding_bencoded_data_with_PHP)
  * [PHP](http://github.com/jesseschalken/pure-bencode) by [Jesse Schalken](http://jesseschalken.com)
  * [PHP Extension](https://github.com/Frederick888/php-bencode) by [Frederick Zhang](https://blog.onee3.org)
  * [PHP Extension](http://code.google.com/p/php-bencode-extension/)
  * [Pixie](https://github.com/stuarth/pixie-bencode)
  * [Pony](https://github.com/mlajszczak/pony_bencode)
  * [Prolog](https://github.com/mndrix/bencode) by [mndrix](/index.php?title=User:Mndrix&action=edit&redlink=1)
  * [Python](/index.php/Decoding_bencoded_data_with_python) by [Hackeron](/index.php?title=User:Hackeron&action=edit&redlink=1)
  * [Scala](https://github.com/andreafey/torrent/blob/master/src/main/scala/torrent/Bcodr.scala) by [Andrea Fey](/index.php?title=User:Pilea&action=edit&redlink=1)
  * [Scheme](https://bitbucket.org/mahcuz/bencode-scheme) by [Mark Skilbeck](http://iammark.us/)
  * [VBScript](http://demon.tw/my-work/vbs-bencode.html) by [Demon](http://demon.tw)
  * [Elixir](https://github.com/patrickgombert/bencodex) by [Patrick Gombert](/index.php?title=User:Patrickgombert&action=edit&redlink=1)
  * [Ruby](https://github.com/kholbekj/bencoder) by [Kasper Holbek Jensen](http://kasper.codes)

###Metainfo File Structure

All data in a metainfo file is bencoded. The specification for bencoding is defined above.

The content of a metainfo file (the file ending in ".torrent") is a bencoded dictionary, containing the keys listed below. All character string values are
UTF-8 encoded.

  * **info**: a dictionary that describes the file(s) of the torrent. There are two possible forms: one for the case of a 'single-file' torrent with no directory structure, and one for the case of a 'multi-file' torrent (see below for details)
  * **announce**: The announce URL of the tracker (string)
  * **announce-list**: (optional) this is an extention to the official specification, offering backwards-compatibility. (list of lists of strings). 
    * The official request for a specification change is [here](http://bittorrent.org/beps/bep_0012.html).
  * **creation date**: (optional) the creation time of the torrent, in standard UNIX epoch format (integer, seconds since 1-Jan-1970 00:00:00 UTC)
  * **comment**: (optional) free-form textual comments of the author (string)
  * **created by**: (optional) name and version of the program used to create the .torrent (string)
  * **encoding**: (optional) the string encoding format used to generate the **pieces** part of the **info** dictionary in the .torrent metafile (string)

####Info Dictionary

This section contains the field which are common to both mode, "single file" and "multiple file".

  * **piece length**: number of bytes in each piece (integer)
  * **pieces**: string consisting of the concatenation of all 20-byte SHA1 hash values, one per piece (byte string, i.e. not urlencoded)
  * **private**: (optional) this field is an integer. If it is set to "1", the client MUST publish its presence to get other peers ONLY via the trackers explicitly described in the metainfo file. If this field is set to "0" or is not present, the client may obtain peer from other means, e.g. PEX peer exchange, dht. Here, "private" may be read as "no external peer source". 
    * **NOTE:** There is much debate surrounding private trackers.
    * The official request for a specification change is [here](http://bittorrent.org/beps/bep_0027.html).
    * Azureus was the first client to respect private trackers, [see their wiki](http://wiki.vuze.com/w/Private_torrent) for more details.

#####Info in Single File Mode

For the case of the **single-file** mode, the **info** dictionary contains the following structure:

  * **name**: the filename. This is purely advisory. (string)
  * **length**: length of the file in bytes (integer)
  * **md5sum**: (optional) a 32-character hexadecimal string corresponding to the MD5 sum of the file. This is not used by BitTorrent at all, but it is included by some programs for greater compatibility.

#####Info in Multiple File Mode

For the case of the **multi-file** mode, the **info** dictionary contains thefollowing structure:

  * **name**: the name of the directory in which to store all the files. This is purely advisory. (string)
  * **files**: a list of dictionaries, one for each file. Each dictionary in this list contains the following keys: 
    * **length**: length of the file in bytes (integer)
    * **md5sum**: (optional) a 32-character hexadecimal string corresponding to the MD5 sum of the file. This is not used by BitTorrent at all, but it is included by some programs for greater compatibility.
    * **path**: a list containing one or more string elements that together represent the path and filename. Each element in the list corresponds to either a directory name or (in the case of the final element) the filename. For example, a the file "dir1/dir2/file.ext" would consist of three string elements: "dir1", "dir2", and "file.ext". This is encoded as a bencoded list of strings such as **l4:**dir1**4:**dir2**8:**file.ext**e**

####Notes

  * The **piece length** specifies the nominal piece size, and is usually a power of 2. The piece size is typically chosen based on the total amount of file data in the torrent, and is constrained by the fact that too-large piece sizes cause inefficiency, and too-small piece sizes cause large .torrent metadata file. Historically, piece size was chosen to result in a .torrent file no greater than approx. 50 - 75 kB (presumably to ease the load on the server hosting the torrent files). 
    * Current best-practice is to _keep the piece size to 512KB or less,_ for torrents around 8-10GB, even if that results in a larger .torrent file. This results in a more efficient swarm for sharing files. The most common sizes are 256 kB, 512 kB, and 1 MB.
    * Every piece is of equal length except for the final piece, which is irregular. The number of pieces is thus determined by 'ceil( total length / piece size )'.
    * For the purposes of piece boundaries in the multi-file case, consider the file data as one long continuous stream, composed of the concatenation of each file in the order listed in the _files_ list. The number of pieces and their boundaries are then determined in the same manner as the case of a single file. Pieces may overlap file boundaries.
  * Each piece has a corresponding SHA1 hash of the data contained within that piece. These hashes are concatenated to form the _pieces** value in the above **_**info** dictionary. Note that this is **not** a list but rather a single string. The length of the string must be a multiple of 20.

###Tracker HTTP/HTTPS Protocol

The tracker is an HTTP/HTTPS service which responds to HTTP GET requests. The requests include metrics from clients that help the tracker keep overall statistics about the torrent. The response includes a peer list that helps the cclient participate in the torrent. The base URL consists of the "announce URL" as defined in the metainfo (.torrent) file. The parameters are then added to this URL, using standard CGI methods (i.e. a '?' after the announce URL, followed by 'param=value' sequences separated by '&').

Note that all binary data in the URL (particularly info_hash and peer_id) must be properly escaped. This means any byte not in the set 0-9, a-z, A-Z, '.',
'-', '_' and '~', must be encoded using the "%nn" format, where nn is the hexadecimal value of the byte. (See [RFC1738](http://www.faqs.org/rfcs/rfc1738.html) for details.)

For a 20-byte hash of \x12\x34\x56\x78\x9a\xbc\xde\xf1\x23\x45\x67\x89\xab\xcd
\xef\x12\x34\x56\x78\x9a,  
The right encoded form is %124Vx%9A%BC%DE%F1%23Eg%89%AB%CD%EF%124Vx%9A

####Tracker Request Parameters

The parameters used in the client->tracker GET request are as follows:

  * **info_hash**: urlencoded 20-byte SHA1 hash of the _value_ of the _info_ key from the Metainfo file. Note that the _value_ will be a bencoded dictionary, given the definition of the _info_ key above.
  * **peer_id**: urlencoded 20-byte string used as a unique ID for the client, generated by the client at startup. This is allowed to be any value, and may be binary data. _There are currently no guidelines for generating this peer ID. However, one may rightly presume that it must at least be unique for your local machine, thus should probably incorporate things like process ID and perhaps a timestamp recorded at startup. See peer_id  below for common client encodings of this field._
  * **port**: The port number that the client is listening on. Ports reserved for BitTorrent are typically 6881-6889. Clients may choose to give up if it cannot establish a port within this range.
  * **uploaded**: The total amount uploaded (since the client sent the 'started' event to the tracker) in base ten ASCII. While not explicitly stated in the official specification, the concensus is that this should be the total number of bytes uploaded.
  * **downloaded**: The total amount downloaded (since the client sent the 'started' event to the tracker) in base ten ASCII. While not explicitly stated in the official specification, the consensus is that this should be the total number of bytes downloaded.
  * **left**: The number of bytes this client still has to download in base ten ASCII. _Clarification: The number of bytes needed to download to be 100% complete and get all the included files in the torrent._
  * **compact**: Setting this to 1 indicates that the client accepts a compact response. The peers list is replaced by a peers string with 6 bytes per peer. The first four bytes are the host (in network byte order), the last two bytes are the port (again in network byte order). It should be noted that some trackers only support compact responses (for saving bandwidth) and either refuse requests without "compact=1" or simply send a compact response unless the request contains "compact=0" (in which case they will refuse the request.)
  * **no_peer_id**: Indicates that the tracker can omit peer id field in peers dictionary. This option is ignored if compact is enabled.
  * **event**: If specified, must be one of _started_, _completed_, _stopped_, (or empty which is the same as not being specified). If not specified, then this request is one performed at regular intervals. 
    * **started**: The first request to the tracker _must_ include the event key with this value.
    * **stopped**: Must be sent to the tracker if the client is shutting down gracefully.
    * **completed**: Must be sent to the tracker when the download completes. However, must not be sent if the download was already 100% complete when the client started. Presumably, this is to allow the tracker to increment the "completed downloads" metric based solely on this event.
  * **ip**: Optional. The true IP address of the client machine, in dotted quad format or rfc3513 defined hexed IPv6 address. _Notes: In general this parameter is not necessary as the address of the client can be determined from the IP address from which the HTTP request came. The parameter is only needed in the case where the IP address that the request came in on is not the IP address of the client. This happens if the client is communicating to the tracker through a proxy (or a transparent web proxy/cache.) It also is necessary when both the client and the tracker are on the same local side of a NAT gateway. The reason for this is that otherwise the tracker would give out the internal (RFC1918) address of the client, which is not routable. Therefore the client must explicitly state its (external, routable) IP address to be given out to external peers. Various trackers treat this parameter differently. Some only honor it only if the IP address that the request came in on is in RFC1918 space. Others honor it unconditionally, while others ignore it completely. In case of IPv6 address (e.g.: 2001:db8:1:2::100) it indicates only that client can communicate via IPv6._
  * **numwant**: Optional. Number of peers that the client would like to receive from the tracker. This value is permitted to be zero. If omitted, typically defaults to 50 peers.
  * **key**: Optional. An additional identification that is not shared with any other peers. It is intended to allow a client to prove their identity should their IP address change.
  * **trackerid**: Optional. If a previous announce contained a tracker id, it should be set here.

####Tracker Response

The tracker responds with "text/plain" document consisting of a bencoded
dictionary with the following keys:

  * **failure reason**: If present, then no other keys may be present. The value is a human-readable error message as to why the request failed (string).
  * **warning message**: (new, optional) Similar to failure reason, but the response still gets processed normally. The warning message is shown just like an error.
  * **interval**: Interval in seconds that the client should wait between sending regular requests to the tracker
  * **min interval**: (optional) Minimum announce interval. If present clients must not reannounce more frequently than this.
  * **tracker id**: A string that the client should send back on its next announcements. If absent and a previous announce sent a tracker id, do not discard the old value; keep using it.
  * **complete**: number of peers with the entire file, i.e. seeders (integer)
  * **incomplete**: number of non-seeder peers, aka "leechers" (integer)
  * **peers**: (dictionary model) The value is a list of dictionaries, each with the following keys: 
    * **peer id**: peer's self-selected ID, as described above for the tracker request (string)
    * **ip**: peer's IP address either IPv6 (hexed) or IPv4 (dotted quad) or DNS name (string)
    * **port**: peer's port number (integer)
  * **peers**: (binary model) Instead of using the dictionary model described above, the **peers** value may be a string consisting of multiples of 6 bytes. First 4 bytes are the IP address and last 2 bytes are the port number. All in network (big endian) notation.

As mentioned above, the list of peers is length 50 by default. If there are fewer peers in the torrent, then the list will be smaller. Otherwise, the tracker randomly selects peers to include in the response. _The tracker may choose to implement a more intelligent mechanism for peer selection when responding to a request. For instance, reporting seeds to other seeders could be avoided._

Clients may send a request to the tracker more often than the specified interval, if an event occurs (i.e. stopped or completed) or if the client needs to learn about more peers. However, it is considered bad practice to "hammer" on a tracker to get multiple peers. If a client wants a large peer list in the response, then it should specify the **numwant** parameter.

_**Implementer's Note**: Even 30 peers is **plenty**, the official client version 3 in fact only actively forms new connections if it has less than 30 peers and will refuse connections if it has 55. **This value is important to performance**. When a new piece has completed download, HAVE messages (see below) will need to be sent to most active peers. As a result the cost of broadcast traffic grows in direct proportion to the number of peers. Above 25, new peers are highly unlikely to increase download speed. UI designers are
**strongly** advised to make this obscure and hard to change as it is very rare to be useful to do so._

###Tracker 'scrape' Convention

By convention most trackers support another form of request, which queries the state of a given torrent (or all torrents) that the tracker is managing. This is referred to as the "scrape page" because it automates the otherwise tedious process of "screen scraping" the tracker's stats page.

The scrape URL is also a HTTP GET method, similar to the one described above.
However the base URL is different. To derive the scrape URL use the following steps: Begin with the announce URL. Find the last '/' in it. If the text immediately following that '/' isn't 'announce' it will be taken as a sign that that tracker doesn't support the scrape convention. If it does, substitute 'scrape' for 'announce' to find the scrape page.

Examples: (announce URL -> scrape URL) 
    
      ~http://example.com/announce          -> ~http://example.com/scrape
      ~http://example.com/x/announce        -> ~http://example.com/x/scrape
      ~http://example.com/announce.php      -> ~http://example.com/scrape.php
      ~http://example.com/a                 -> (scrape not supported)
      ~http://example.com/announce?x2%0644 -> ~http://example.com/scrape?x2%0644
      ~http://example.com/announce?x=2/4    -> (scrape not supported)
      ~http://example.com/x%064announce     -> (scrape not supported)
    

Note especially that entity unquoting is _not_ to be done. This standard is documented by Bram in the
[BitTorrent](/index.php?title=BitTorrent&action=edit&redlink=1) development
list archive: <http://groups.yahoo.com/group/BitTorrent/message/3275>

The scrape URL may be supplemented by the optional parameter _info_hash_, a 20-byte value as described above. This restricts the tracker's report to that
particular torrent. Otherwise stats for all torrents that the tracker is managing are returned. Software authors are strongly encouraged to use the
_info_hash_ parameter when at all possible, to reduce the load and bandwidth of the tracker.

You may also specify multiple info_hash parameters to trackers that support it. While this isn't part of the official specifications it has become somewhat a defacto standard - for example:

    
    
     http://example.com/scrape.php?info_hash=aaaaaaaaaaaaaaaaaaaa&info_hash=bbbbbbbbbbbbbbbbbbbb&info_hash=cccccccccccccccccccc
    

The response of this HTTP GET method is a "text/plain" or sometimes gzip compressed document consisting of a bencoded dictionary, containing the following keys:

  * **files**: a dictionary containing one key/value pair for each torrent for which there are stats. If _info_hash_ was supplied and was valid, this dictionary will contain a single key/value. Each key consists of a 20-byte binary _info_hash_. The value of each entry is another dictionary containing the following: 
    * **complete**: number of peers with the entire file, i.e. seeders (integer)
    * **downloaded**: total number of times the tracker has registered a completion ("event=complete", i.e. a client finished downloading the torrent)
    * **incomplete**: number of non-seeder peers, aka "leechers" (integer)
    * **name**: (optional) the torrent's internal name, as specified by the "name" file in the info section of the .torrent file

Note that this response has three levels of dictionary nesting. Here's an example:

`d5:_files_d20:....................d8:_complete_i**5**e10:_downloaded_i**50**e
10:_incomplete_i**10**eeee`

Where `....................` is the 20 byte info_hash and there are 5 seeders, 10 leechers, and 50 complete downloads.

####Unofficial extensions to scrape

Below are the response keys are being unofficially used. Since they are unofficial, they are all optional.

  * **failure reason**: Human-readable error message as to why the request failed (string). Clients known to handle this key: Azureus.
  * **flags**: a dictionary containing miscellaneous flags. The value of the flags key is another nested dictionary, possibly containing the following: 
    * **min_request_interval**: The value for this key is an integer specifying how the minimum number of seconds for the client to wait before scraping the tracker again. Trackers known to send this key: BNBT. Clients known to handle this key: Azureus.

###Peer wire protocol (TCP)

####Overview

The peer protocol facilitates the exchange of pieces as described in the
'_metainfo_ file.

_Note here that the original specification also used the term "piece" when
describing the peer protocol, but as a different term than "piece" in the
metainfo file. For that reason, the term "block" will be used in this
specification to describe the data that is exchanged between peers over the
wire._

A client must maintain state information for each connection that it has with
a remote peer:

  * **choked**: Whether or not the remote peer has choked this client. When a peer chokes the client, it is a notification that no requests will be answered until the client is unchoked. The client should not attempt to send requests for blocks, and it should consider all pending (unanswered) requests to be discarded by the remote peer.
  * **interested**: Whether or not the remote peer is interested in something this client has to offer. This is a notification that the remote peer will begin requesting blocks when the client unchokes them.

_Note that this also implies that the client will also need to keep track of
whether or not it is interested in the remote peer, and if it has the remote
peer choked or unchoked. So, the real list looks something like this:_

  * **am_choking**: this client is choking the peer
  * **am_interested**: this client is interested in the peer
  * **peer_choking**: peer is choking this client
  * **peer_interested**: peer is interested in this client

Client connections start out as "choked" and "not interested". In other words:

  * **am_choking** = 1
  * **am_interested** = 0
  * **peer_choking** = 1
  * **peer_interested** = 0

A block is downloaded by the client when the client is interested in a peer, and that peer is not choking the client. A block is uploaded by a client when the client is not choking a peer, and that peer is interested in the client.

It is important for the client to keep its peers informed as to whether or not it is interested in them. This state information should be kept up-to-date
with each peer even when the client is choked. This will allow peers to know if the client will begin downloading when it is unchoked (and vice-versa).

####Data Types

Unless specified otherwise, all integers in the peer wire protocol are encoded as four byte big-endian values. This includes the length prefix on all
messages that come after the handshake.

####Message flow

The peer wire protocol consists of an initial handshake. After that, peers communicate via an exchange of length-prefixed messages. The length-prefix is an integer as described above.

####Handshake

The handshake is a required message and must be the first message transmitted by the client. It is (49+len(pstr)) bytes long.

_handshake: <pstrlen><pstr><reserved><info_hash><peer_id>_

  * **pstrlen**: string length of <pstr>, as a single raw byte
  * **pstr**: string identifier of the protocol
  * **reserved**: eight (8) reserved bytes. All current implementations use all zeroes. Each bit in these bytes can be used to change the behavior of the protocol. _An email from Bram suggests that trailing bits should be used first, so that leading bits may be used to change the meaning of trailing bits._
  * **info_hash**: 20-byte SHA1 hash of the info key in the metainfo file. This is the same info_hash that is transmitted in tracker requests.
  * **peer_id**: 20-byte string used as a unique ID for the client. This is usually the same peer_id that is transmitted in tracker requests (but not always e.g. an anonymity option in Azureus).

In version 1.0 of the BitTorrent protocol, pstrlen = 19, and pstr = "BitTorrent protocol".

The initiator of a connection is expected to transmit their handshake immediately. The recipient may wait for the initiator's handshake, if it is capable of serving multiple torrents simultaneously (torrents are uniquely
identified by their info_hash). However, the recipient must respond as soon as it sees the info_hash part of the handshake (the peer id will presumably be sent after the recipient sends its own handshake). The tracker's NAT-checking feature does not send the peer_id field of the handshake._

If a client receives a handshake with an info_hash that it is not currently serving, then the client must drop the connection.

If the initiator of the connection receives a handshake in which the peer_id does not match the expected peer_id, then the initiator is expected to drop the connection. _Note that the initiator presumably received the peer information from the tracker, which includes the peer_id that was registered by the peer. The peer_id from the tracker and in the handshake are expected to match.__

#####peer_id

The peer_id is exactly 20 bytes (characters) long.

There are mainly two conventions how to encode client and client version information into the peer_id, Azureus-style and Shadow's-style.

Azureus-style uses the following encoding: '-', two characters for client id, four ascii digits for version number, '-', followed by random numbers.

For example: '-AZ2060-'...

known clients that uses this encoding style are:

  * '7T' - [aTorrent for Android](https://play.google.com/store/apps/details?id=com.mobilityflow.torrent&hl=en)
  * 'AB' - [AnyEvent::BitTorrent](http://search.cpan.org/dist/AnyEvent-BitTorrent/)
  * 'AG' - [Ares](http://aresgalaxy.sourceforge.net/)
  * 'A~' - [Ares](http://aresgalaxy.sourceforge.net/)
  * 'AR' - [Arctic](http://dev.int64.org/arctic.html)
  * 'AV' - [Avicora](http://sourceforge.net/projects/avicora/)
  * 'AT' - [Artemis](http://www.cyberartemis.com)
  * 'AX' - [BitPump](http://www.analogx.com/contents/download/network/bitpump.htm)
  * 'AZ' - [Azureus](http://azureus.sf.net)
  * 'BB' - [BitBuddy](http://www.btvampire.com)
  * 'BC' - [BitComet](http://www.bitcomet.com)
  * 'BE' - [Baretorrent](http://sourceforge.net/projects/baretorrent/)
  * 'BF' - [Bitflu](http://bitflu.workaround.ch/)
  * 'BG' - [BTG (uses Rasterbar libtorrent)](http://btg.berlios.de/)
  * 'BL' - [BitCometLite (uses 6 digit version number)](http://www.bitcomet.com/tools/bitcometlite/)
  * 'BL' - [BitBlinder](https://web.archive.org/web/20100407144429/http://www.bitblinder.com/)
  * 'BP' - [BitTorrent Pro (Azureus + spyware)](http://www.intelpeers.com)
  * 'BR' - [BitRocket](http://www.bitrocket.org)
  * 'BS' - [BTSlave](http://btslave.sourceforge.net)
  * 'BT' - [mainline BitTorrent (versions >= 7.9)](http://bittorrent.com)
  * 'BT' - [BBtor](http://bbtor.net)
  * 'Bt' - [Bt](https://github.com/atomashpolskiy/bt)
  * 'BW' - [BitWombat](http://bitwombat.com)
  * 'BX' - ~Bittorrent X
  * 'CD' - [Enhanced CTorrent](http://www.rahul.net/dholmes/ctorrent/)
  * 'CT' - [CTorrent](http://ctorrent.sourceforge.net)
  * 'DE' - [DelugeTorrent](http://www.deluge-torrent.org)
  * 'DP' - [Propagate Data Client](https://web.archive.org/web/20110128203704/http://propagatedata.com/)
  * 'EB' - [EBit](http://dywt.com.cn/)
  * 'ES' - [electric sheep](http://electricsheep.org)
  * 'FC' - [FileCroc](http://www.filecroc.com)
  * 'FD' - [Free Download Manager (versions >= 5.1.12)](http://www.freedownloadmanager.org)
  * 'FT' - [FoxTorrent](http://www.foxtorrent.com)
  * 'FX' - [Freebox BitTorrent](http://dev.freebox.fr/)
  * 'GS' - [GSTorrent](http://sourceforge.net/projects/gstorrent)
  * 'HK' - [Hekate](http://www.pps.jussieu.fr/~jch/software/hekate/)
  * 'HL' - [Halite](http://www.binarynotions.com/halite.php)
  * 'HM' - [hMule (uses Rasterbar libtorrent)](https://gforge.inria.fr/projects/hmule/)
  * 'HN' - [Hydranode](http://hydranode.com)
  * 'IL' - [iLivid](http://www.ilivid.com/)
  * 'JS' - [Justseed.it client](https://justseed.it)
  * 'JT' - [JavaTorrent](https://github.com/Johnnei/JavaTorrent)
  * 'KG' - [KGet](http://kget.sourceforge.net)
  * 'KT' - [KTorrent](http://ktorrent.org)
  * 'LC' - [LeechCraft](http://leechcraft.org)
  * 'LH' - [LH-ABC](http://code.google.com/p/lh-abc)
  * 'LP' - [Lphant](http://www.lphant.com)
  * 'LT' - [libtorrent](http://libtorrent.sf.net)
  * 'lt' - [libTorrent](http://libtorrent.rakshasa.no)
  * 'LW' - [LimeWire](http://www.limewire.org)
  * 'MK' - [Meerkat](http://www.themeerkat.net/)
  * 'MO' - [MonoTorrent](http://monotorrent.blogspot.com/)
  * 'MP' - [MooPolice](http://www.moopolice.de)
  * 'MR' - [Miro](http://www.getmiro.com)
  * 'MT' - [MoonlightTorrent](http://www.moonlighttorrent.com)
  * 'NB' - [Net::BitTorrent](http://search.cpan.org/dist/Net-BitTorrent)
  * 'NX' - [Net Transport](http://www.xi-soft.com)
  * 'OS' - [OneSwarm](http://oneswarm.cs.washington.edu)
  * 'OT' - [OmegaTorrent](http://www.omegatorrent.com)
  * 'PB' - [Protocol::BitTorrent](http://search.cpan.org/perldoc?Protocol::BitTorrent)
  * 'PD' - [Pando](http://www.pando.com)
  * 'PI' - [PicoTorrent](http://www.picotorrent.org)
  * 'PT' - [PHPTracker](http://php-tracker.org)
  * 'qB' - [qBittorrent](http://www.qbittorrent.org)
  * 'QD' - [QQDownload](http://im.qq.com/cyclone/)
  * 'QT' - Qt 4 Torrent example
  * 'RT' - [Retriever](http://www.halogenware.com/software/retriever.html)
  * 'RZ' - [RezTorrent](https://launchpad.net/reztorrent)
  * 'S~' - [Shareaza alpha/beta](http://shareaza.sourceforge.net)
  * 'SB' - ~Swiftbit
  * 'SD' - [Thunder (aka XùnLéi)](http://www.xunlei.com)
  * 'SM' - [SoMud](http://www.somud.com)
  * 'SP' - [BitSpirit](http://www.bitspirit.cc/en/)
  * 'SS' - SwarmScope
  * 'ST' - [SymTorrent](http://symtorrent.aut.bme.hu/)
  * 'st' - [sharktorrent](http://sharktorrent.com)
  * 'SZ' - [Shareaza](http://shareaza.sourceforge.net)
  * 'TB' - [Torch](http://www.torchbrowser.com/)
  * 'TE' - [terasaur Seed Bank](http://terasaur.org)
  * 'TL' - [Tribler (versions >= 6.1.0)](http://www.tribler.org/)
  * 'TN' - TorrentDotNET
  * 'TR' - [Transmission](https://transmissionbt.com/)
  * 'TS' - [Torrentstorm](http://www.torrentstorm.com)
  * 'TT' - [TuoTu](http://www.tuotu.com)
  * 'UL' - uLeecher!
  * 'UM' - [µTorrent for Mac](http://mac.utorrent.com)
  * 'UT' - [µTorrent](http://www.utorrent.com)
  * 'VG' - [Vagaa](http://www.vagaa.com)
  * 'WD' - [WebTorrent Desktop](http://webtorrent.io/desktop)
  * 'WT' - [BitLet](http://www.bitlet.org)
  * 'WW' - [WebTorrent](http://webtorrent.io)
  * 'WY' - [FireTorrent](http://www.wyzo.com/firetorrent/)
  * 'XF' - [Xfplay](http://www.xfplay.com/)
  * 'XL' - [Xunlei](http://www.xunlei.com)
  * 'XS' - XSwifter
  * 'XT' - [XanTorrent](http://www.xantorrent.pwp.blueyonder.co.uk/xantorrent.zip)
  * 'XX' - [Xtorrent](http://www.xtorrent.com)
  * 'ZT' - [ZipTorrent](http://www.ziptorrent.com)

Clients which have been seen in the wild and need to be identified:

  * 'BD' (example: -BD0300-)
  * 'NP' (example: -NP0201-)
  * 'wF' (example: -wF2200-)
  * 'hk' (example: -hk0010-) Chinese IP address, unrequestedly sends info dict in message 0xA, reconnects immediately after being disconnected, reserved bytes = 01,01,01,01,00,00,02,01

Shadow's style uses the following encoding: one ascii alphanumeric for client identification, up to five characters for version number (padded with '-' if
less than five), followed by three characters (commonly '---', but not always the case), followed by random characters. Each character in the version string
represents a number from 0 to 63. '0'=0, ..., '9'=9, 'A'=10, ..., 'Z'=35, 'a'=36, ..., 'z'=61, '.'=62, '-'=63.

A full explanation by Shad0w about the encoding style (including information about existing conventions on how the three characters after the version
string are used) can be found [here](http://forums.degreez.net/viewtopic.php?t=7070).

For example: 'S58B-----'... for Shadow's 5.8.11

known clients that uses this encoding style are:

  * 'A' - [ABC](http://pingpong-abc.sourceforge.net/)
  * 'O' - [Osprey Permaseed](http://osprey.ibiblio.org/)
  * 'Q' - [BTQueue](http://btqueue.sourceforge.net/)
  * 'R' - [Tribler (versions < 6.1.0)](http://www.tribler.org/)
  * 'S' - [Shadow's client](http://bt.degreez.net/)
  * 'T' - [BitTornado](http://bittornado.com)
  * 'U' - [UPnP NAT Bit Torrent](http://aaron2003.myftp.org/upnpclient.html)

Bram's client now uses this style... 'M3-4-2--' or 'M4-20-8-'.

[BitComet](http://www.bitcomet.com/) does something different still. Its peer_id consists of four ASCII characters 'exbc', followed by two bytes x and y, followed by random characters. The version number is x in decimal before the decimal point and y as two decimal digits after the decimal point.
[BitLord](http://www.bitlord.com/) uses the same scheme, but adds 'LORD' after the version bytes. An [unofficial patch](http://solidox.org/bc/) for BitComet
once replaced 'exbc' with 'FUTB'. The encoding for BitComet Peer IDs changed to Azureus-style as of BitComet version 0.59.

[XBT Client](http://xbtt.sourceforge.net/client/) has its own style too. Its peer_id consists of the three uppercase characters 'XBT' followed by three
ASCII digits representing the version number. If the client is a debug build, the seventh byte is the lowercase character 'd', otherwise it is a '-'.
Following that is a '-' then random digits, uppercase and lowercase letters.
Example: 'XBT054d-' at the beginning would indicate a debug build of version 0.5.4.

[Opera 8 previews and Opera 9.x releases](http://www.opera.com/) use the following peer_id scheme: The first two characters are 'OP' and the next four digits equal the build number. All following characters are random lowercase hexdecimal digits.

[MLdonkey](http://mldonkey.sourceforge.net/Main_Page) use the following peer_id scheme: the first characters are '-ML' followed by a dotted version then a '-' followed by randomness. e.g. '-ML2.7.2-kgjjfkd'

[Bits on Wheels](http://www.bitsonwheels.com/) uses the pattern '-BOWxxx-yyyyyyyyyyyy', where y is random (uppercase letters) and x depends on the version. Version 1.0.6 has xxx = A0C.

[Queen Bee](http://queenbee.se/) uses Bram's new style: 'Q1-0-0--' or 'Q1-10-0-' followed by random bytes.

[BitTyrant](http://bittyrant.cs.washington.edu/) is an Azureus fork and simply uses 'AZ2500BT' + random bytes as peer ID in its 1.1 version. Note the missing
dashes.

[TorrenTopia](http://www.torrentopia.org/) version 1.90 pretends to be or is derived from Mainline 3.4.6. Its peer ID starts with '346------'.

[BitSpirit](http://www.167bt.com/intl/) has several modes for its peer ID. In one mode it reads the ID of its peer and reconnects using the first eight bytes as a basis for its own ID. Its real ID appears to use '\0\3BS' (C notation) as the first four bytes for version 3.x and '\0\2BS' for version 2.x. In all modes the ID may end in 'UDP0'. Since BitSpirit 3.6 the peer ID uses Azureus style with characters 'SP' but without trailing '-' (as FlashGet).

[Rufus](http://rufus.sourceforge.net/) uses its version as decimal ASCII values for the first two bytes. The third and fourth bytes are 'RS'. What then follows is the nickname of the user and some random bytes.

[G3 Torrent](http://g3torrent.sourceforge.net/) starts its peer ID with '-G3' and appends up to 9 characters of the nickname of the user.

[FlashGet](http://www.flashget.com/) uses Azureus style with 'FG' but without the trailing '-'. Version 1.82.1002 still uses the version digits '0180'.

[BT Next Evolution](http://www.btnext.com/) is derived from BitTornado but tries to mimic Azureus style. The result is that its peer ID starts with '-NE', continues with a 4 digit version number and then directly goes on with the three characters that describe the type of client in Shad0w's peer ID style.

[AllPeers](http://www.allpeers.com/) takes the sha1 hash of a user dependent string and replaces the first few characters with "AP" + version string + "-".

[Qvod](http://www.qvod.com/) starts its id with the four letters "QVOD" and continues with its build number in four decimal digits (currently "0054"). The
remaining 12 characters are random uppercase hexdecimal digits. There appears to be a popular modified client in China that replaces the four characters in the beginning with random bytes.

[SpywareTerminator](http://www.spywareterminator.com) uses libtorrent to share its signature updates among users. It uses Azureus style with 'CS' and version
digits '2500'.

Many clients are using all random numbers or 12 zeroes followed by random numbers (like older versions of [Bram's client](http://www.bittorrent.com/)).

####Messages

All of the remaining messages in the protocol take the form of <length prefix><message ID><payload>. The length prefix is a four byte big-endian value. The message ID is a single decimal byte. The payload is message dependent.

#####keep-alive: <len=0000>

The **keep-alive** message is a message with zero bytes, specified with the length prefix set to zero. There is no message ID and no payload. Peers may
close a connection if they receive no messages (**keep-alive** or any other message) for a certain period of time, so a keep-alive message must be sent to
maintain the connection _alive_ if no command have been sent for a given amount of time. This amount of time is generally two minutes.

#####choke: <len=0001><id=0>

The **choke** message is fixed-length and has no payload.

#####unchoke: <len=0001><id=1>

The **unchoke** message is fixed-length and has no payload.

#####interested: <len=0001><id=2>

The **interested** message is fixed-length and has no payload.

#####not interested: <len=0001><id=3>

The **not interested** message is fixed-length and has no payload.

#####have: <len=0005><id=4><piece index>

The **have** message is fixed length. The payload is the zero-based index of a piece that has just been successfully downloaded and verified via the hash.

_Implementer's Note: That is the strict definition, in reality some games may be played. In particular because peers are extremely unlikely to download pieces that they already have, a peer may choose not to advertise having a piece to a peer that already has that piece. At a minimum "HAVE suppression" will result in a 50% reduction in the number of HAVE messages, this translates to around a 25-35% reduction in protocol overhead. At the same time, it may be worthwhile to send a HAVE message to a peer that has that piece already since it will be useful in determining which piece is rare._

_A malicious peer might also choose to advertise having pieces that it knows the peer will never download. Due to this attempting to model peers using this information is a **bad idea**_.

#####bitfield: <len=0001+X><id=5><bitfield>

The **bitfield** message may only be sent immediately after the handshaking sequence is completed, and before any other messages are sent. It is optional, and need not be sent if a client has no pieces.

The **bitfield** message is variable length, where X is the length of the bitfield. The payload is a bitfield representing the pieces that have been successfully downloaded. The high bit in the first byte corresponds to piece index 0. Bits that are cleared indicated a missing piece, and set bits indicate a valid and available piece. Spare bits at the end are set to zero.

Some clients (Deluge for example) send **bitfield** with missing pieces even if it has all data. Then it sends rest of pieces as **have** messages. They are saying this helps against ISP filtering of BitTorrent protocol. It is called **lazy bitfield**.

_A bitfield of the wrong length is considered an error. Clients should drop the connection if they receive bitfields that are not of the correct size, or if the bitfield has any of the spare bits set._

#####request: <len=0013><id=6><index><begin><length>

The **request** message is fixed length, and is used to request a block. The payload contains the following information:

  * **index**: integer specifying the zero-based piece index
  * **begin**: integer specifying the zero-based byte offset within the piece
  * **length**: integer specifying the requested length.

_**This section is under dispute! Please use the [discussion page](http://wiki.theory.org/Talk:BitTorrentSpecification#Messages:_request)
to resolve this!**_

_**View #1**_ According to the official specification, "All current implementations use 2^15 (32KB), and close connections which request an amount greater than 2^17 (128KB)." As early as version 3 or 2004, this behavior was changed to use 2^14 (16KB) blocks. As of version 4.0 or mid-2005, the mainline disconnected on requests larger than 2^14 (16KB); and some clients have
followed suit. Note that block requests are smaller than pieces (>=2^18 bytes), so multiple requests will be needed to download a whole piece.

_Strictly, the specification allows 2^15 (32KB) requests. The reality is near all clients will now use 2^14 (16KB) requests. Due to clients that enforce
that size, it is recommended that implementations make requests of that size. 
Due to smaller requests resulting in higher overhead due to tracking a greater number of requests, implementers are advised against going below 2^14 (16KB)._

_The choice of request block size limit enforcement is not nearly so clear cut. With mainline version 4 enforcing 16KB requests, most clients will use that size. At the same time 2^14 (16KB) is the _semi_-official (only _semi_ because the official protocol document has not been updated) limit now, so enforcing that isn't wrong. At the same time, allowing larger requests enlarges the set of possible peers, and except on very low bandwidth connections (<256kbps) multiple blocks will be downloaded in one choke-timeperiod, thus merely enforcing the old limit causes minimal performance degradation. Due to this factor, it is recommended that only the older 2^17 (128KB) maximum size limit be enforced._

_**View #2**_ This section has contained falsehoods for a large portion of the time this page has existed. This is the third time I (uau) am correcting this same section for incorrect information being added, so I won't rewrite it completely since it'll probably be broken again... Current version has at least the following errors: Mainline started using 2^14 (16384) byte requests when it was still the only client in existence; only the "official specification" still talked about the obsolete 32768 byte value which was in
reality neither the default size nor maximum allowed. In version 4 the request behavior did not change, but the maximum allowed size did change to equal the
default size. In latest mainline versions the max has changed to 32768 (note that this is the first appearance of 32768 for either default or max size
since the first ancient versions). "Most older clients use 32KB requests" is false. Discussion of larger requests fails to take latency effects into account.

#####piece: <len=0009+X><id=7><index><begin><block>

The **piece** message is variable length, where X is the length of the block.
The payload contains the following information:

  * **index**: integer specifying the zero-based piece index
  * **begin**: integer specifying the zero-based byte offset within the piece
  * **block**: block of data, which is a subset of the piece specified by index.

#####cancel: <len=0013><id=8><index><begin><length>

The **cancel** message is fixed length, and is used to cancel block requests.
The payload is identical to that of the "request" message. It is typically used during "End Game" (see the Algorithms section below).

#####port: <len=0003><id=9><listen-port>

The **port** message is sent by newer versions of the Mainline that implements a DHT tracker. The listen port is the port this peer's DHT node is listening on. This peer should be inserted in the local routing table (if DHT tracker is supported).

###Algorithms

####Queuing

_**This section is under dispute! Please use the [discussion page](http://wiki.theory.org/Talk:BitTorrentSpecification#Algorithms:_Queuing)
to resolve this!**_

_**View #1**_ In general peers are advised to keep a few unfullfilled requests on each connection. This is done because otherwise a full round trip is required from the download of one block to begining the download of a new block (round trip between PIECE message and next REQUEST message). On links with high BDP (bandwidth-delay-product, high latency or high bandwidth), this can result in a substantial performance loss.

_Implementer's note: This is the **most crucial performance item**. A static queue of 10 requests is reasonable for 16KB blocks on a 5mbps link with 50ms
latency. Links with greater bandwidth are becoming very common so UI designers are urged to make this readily available for changing. Notably cable modems were known for traffic policing and increasing this might of alleviated some of the problems caused by this._

_**View #2**_ NOTE: much of the information in this "Queuing" section is false or misleading. I'll just note that the "defaults to 5 outstanding requests"
hasn't been true for a long time, "32 KB blocks" is misleading since you normally don't use 32 KB blocks, and tuning queue length by changing it and trying to measure the effects is a bad idea.

####Super Seeding

_(This was not part of the original specification)_

_The super-seed feature in S-5.5 and on is a new seeding algorithm designed to help a torrent initiator with limited bandwidth "pump up" a large torrent,
reducing the amount of data it needs to upload in order to spawn new seeds in the torrent._

_When a seeding client enters "super-seed mode", it will not act as a standard seed, but masquerades as a normal client with no data. As clients connect, it
will then inform them that it received a piece -- a piece that was never sent, or if all pieces were already sent, is very rare. This will induce the client
to attempt to download only that piece._

_When the client has finished downloading the piece, the seed will not inform it of any other pieces until it has seen the piece it had sent previously present on at least one other client. Until then, the client will not have access to any of the other pieces of the seed, and therefore will not waste the seed's bandwidth._

_This method has resulted in much higher seeding efficiencies, by both inducing peers into taking only the rarest data, reducing the amount of redundant data sent, and limiting the amount of data sent to peers which do not contribute to the swarm. Prior to this, a seed might have to upload 150% to 200% of the total size of a torrent before other clients became seeds.
However, a large torrent seeded with a single client running in super-seed mode was able to do so after only uploading 105% of the data. This is 150-200% more efficient than when using a standard seed._

_Super-seed mode is '_NOT_ recommended for general use. While it does assist in the wider distribution of rare data, because it limits the selection of pieces a client can downlad, it also limits the ability of those clients to download data for pieces they have already partially retrieved. Therefore, super-seed mode is only recommended for initial seeding servers._

####Piece downloading strategy

Clients may choose to download pieces in random order.

_A better strategy is to download pieces in _[rarest
first](/index.php/Availability)_ order. The client can determine this by keeping the initial bitfield from each peer, and updating it with every **have** message. Then, the client can download the pieces that appear least frequently in these peer bitfields. Note that any Rarest First strategy should include randomization among at least several of the least common pieces, as
having many clients all attempting to jump on the same "least common" piece would be counter productive._

####End Game

When a download is almost complete, there's a tendency for the last few blocks to trickle in slowly. To speed this up, the client sends requests for all of its missing blocks to all of its peers. To keep this from becoming horribly inefficient, the client also sends a cancel to everyone else every time a block arrives.

_There is no documented thresholds, recommended percentages, or block counts that could be used as a guide or Recommended Best Practice here._

_When to enter end game mode is an area of discussion. Some clients enter end game when all pieces have been requested. Others wait until the number of blocks left is lower than the number of blocks in transit, and no more than 20. There seems to be agreement that it's a good idea to keep the number of pending blocks low (1 or 2 blocks) to minimize the overhead, and if you
randomize the blocks requested, there's a lower chance of downloading duplicates. More on the protocol overhead can be found here:_
<http://hal.inria.fr/inria-00000156/en>.

####Choking and Optimistic Unchoking

Choking is done for several reasons. TCP congestion control behaves very poorly when sending over many connections at once. Also, choking lets each peer use a tit-for-tat-ish algorithm to ensure that they get a consistent download rate.

The choking algorithm described below is the currently deployed one. It is very important that all new algorithms work well both in a network consisting
entirely of themselves and in a network consisting mostly of this one.

There are several criteria a good choking algorithm should meet. It should cap the number of simultaneous uploads for good TCP performance. It should avoid
choking and unchoking quickly, known as 'fibrillation'. It should reciprocate to peers who let it download. Finally, it should try out unused connections once in a while to find out if they might be better than the currently used ones, known as optimistic unchoking.

The currently deployed choking algorithm avoids fibrillation by only changing choked peers once every ten seconds.

Reciprocation and number of uploads capping is managed by unchoking the four peers which have the best upload rate and are interested. This maximizes the client's download rate. These four peers are referred to as _downloaders_, because they are interested in downloading from the client.

Peers which have a better upload rate (as compared to the _downloaders_) but aren't interested get unchoked. If they become interested, the _downloader_ with the worst upload rate gets choked. If a client has a complete file, it uses its upload rate rather than its download rate to decide which peers to unchoke.

For optimistic unchoking, at any one time there is a single peer which is unchoked regardless of its upload rate (if interested, it counts as one of the four allowed _downloaders_). Which peer is optimistically unchoked rotates every 30 seconds. Newly connected peers are three times as likely to start as
the current optimistic unchoke as anywhere else in the rotation. This gives them a decent chance of getting a complete piece to upload.

#####Anti-snubbing

Occasionally a [BitTorrent](/index.php?title=BitTorrent&action=edit&redlink=1)
peer will be choked by all peers which it was formerly downloading from. In such cases it will usually continue to get poor download rates until the optimistic unchoke finds better peers. To mitigate this problem, when over a minute goes by without getting any piece data while downloading from a peer,
[BitTorrent](/index.php?title=BitTorrent&action=edit&redlink=1) assumes it is
"snubbed" by that peer and doesn't upload to it except as an optimistic unchoke. This frequently results in more than one concurrent optimistic unchoke, (an exception to the exactly one optimistic unchoke rule mentioned above), which causes download rates to recover much more quickly when they falter.

###Official Extensions To The Protocol

Currently there are a few official extensions to the protocol.

#####Fast Peers Extensions

  * Reserved Bit: The third least significant bit in the 8th reserved byte i.e. reserved[7] |= 0x04

These extensions serve multiple purposes. They allow a peer to more quickly bootstrap into a swarm by giving a peer a specific set of pieces which they will be allowed download regardless of choked status. They reduce message overhead by adding HaveAll and HaveNone messages and allow explicit rejection of piece requests whereas previously only implicit rejection was possible
meaning that a peer might be left waiting for a piece that would never be delivered.

The specification is documented at the
[BitTorrent](/index.php?title=BitTorrent&action=edit&redlink=1) site here:
<http://bittorrent.org/beps/bep_0006.html>.

#####Distributed Hash Table

  * Reserved Bit: The last bit in the 8th reserved byte i.e. reserved[7] |= 0x01

This extension is to allow for the tracking of peers downloading torrents without the use of a standard tracker. A peer implementing this protocol becomes a "tracker" and stores lists of other nodes/peers which can be used to locate new peers.

The specification is documented at the
[BitTorrent](/index.php?title=BitTorrent&action=edit&redlink=1) site here:
<http://bittorrent.org/beps/bep_0005.html>.

BEP-32 extends the DHT with support for IPv6, and updates the specification in some minor ways. <http://www.pps.jussieu.fr/~jch/software/bittorrent/bep-dht-ipv6.html>

#####Connection Obfuscation

This extension allows the creation of obfuscated (encrypted) connections between peers. This can be used to bypass ISPs throttling BitTorrent traffic.

The specification is documented at
<http://wiki.vuze.com/w/Message_Stream_Encryption>.

_ The documentation is fairly complete, but ideally it would be clarified on several points including guidance on when encrypted connections should be attempted, fallback procedures to regular connections etc. _

###Unofficial Extensions To The Protocol

#####Azureus Messaging Protocol

  * Reserved Bit: 1

A protocol in its own right - if two clients indicate they support the protocol, then they should switch over to using it. It allows normal BitTorrent as well extension messages to be sent over it, and is documented [here](http://wiki.vuze.com/w/Azureus_messaging_protocol). Currently implemented by Azureus and Transmission.

It is not possible to use both this protocol and the LibTorrent extension protocol at the same time - if both clients indicate they support both, then they should follow the semantics defined by the [Extension Negotiation Protocol](http://wiki.vuze.com/w/Extension_negotiation_protocol).

#####WebSeeding

The possibility to seed a torrent via a web server is generally called WebSeeding. It allows the HTTP server to work as a peer in the BitTorrent network.

There are at least two specification for how to combine a torrent download with a HTTP download. The first standard, implemented by BitTornado is quite easy to implement in the client, but is intrusive on the HTTP in that it requires a script handling requests on the server side. i.e. A plain HTTP server that just serves plain files isn't enough. The benfits is that the
script can be more abuse resistant. This specification is found here: <http://bittornado.com/docs/webseed-spec.txt> or as [BEP-17](http://bittorrent.org/beps/bep_0017.html).

The second specification requires slightly more from the client, but downloads from plain HTTP servers. It is specified here:<http://www.getright.com/seedtorrent.html> or as [BEP-19](http://bittorrent.org/beps/bep_0019.html). It has been implemented by
GetRight, libtorrent, Mainline, BitComet, Vuze.

#####Extension protocol

  * Reserved Bit: 44, the fourth most significant bit in the 6th reserved byte i.e. reserved[5] |= 0x10

This is a protocol for exchanging extension information and was derived from an early version of azureus' extension protocol. It adds one message for
exchanging arbitrary handshake information including defined extension messages, mapping extensions to specific message IDs. It is documented here:
<http://www.libtorrent.org/extension_protocol.html> and is implemented at least by libtorrent, uTorrent, Mainline, Transmission, Azureus and BitComet.

It is not possible to use both this protocol and the Azureus Messaging Protocol at the same time - if both clients indicate they support both, then they should follow the semantics defined by the [Extension Negotiation Protocol](http://wiki.vuze.com/w/Extension_negotiation_protocol).

#####Extension Negotiation Protocol

  * Reserved bits: 47 and 48

These bits are used to allow two clients that support both the Azureus Messaging Protocol and LibTorrent's extension protocol to decide which of the two extensions should be used for communication, and is defined [here](http://wiki.vuze.com/w/Extension_negotiation_protocol).

#####BitTorrent Location-aware Protocol 1.0

  * Reserved Bit: 21

A Protocol, considering peers location (in geographical terms) for better performance. Specification can be found [here](http://wiki.theory.org/BitTorrent_Location-aware_Protocol_1.0_Specification).

#####SimpleBT Extension Protocol

  * Reserved Bits: fist reserved byte = 0x01, following bytes may need to be set to zero

An extension using message id 9 to add peer exchange and connection statistics exchange. The specification can be found [here](http://web.archive.org/web/20031002201124/btfans.3322.org/simplebt/ProtocalExtension.txt). The extension was in use in SimpleBT 0.32 to 0.36.1. Later versions of SimpleBT were called BitComet and used the similar but incompatible BitComet Extension Protocol.

#####BitComet Extension Protocol

  * Reserved Bits: first two reserved bytes = "ex"

There appears to be no official documentation.

In this protocol a peer announces the supported extensions by sending a message <len=0001+X><id=0xA0><extension 1>...<extension X> where <extension n> is (usually) the message id of the supported extension. When an extension consists of multiple messages, all ids need to be mentioned.

Extensions currently in use (TODO: reverse engineer semantics):

  * 0xA0 (EXT_SUPPORT) see above, needs to be included in its parameter list
  * 0xA1 (EXT_PEERREQ) ask for peer exchange, used in conjunction with EXT_PEERS
  * 0xA2 (EXT_PEERS) in reply to EXT_PEERREQ and for updates afterwards
  * 0xA3 (EXT_AUTH_SEED) appeared in BitComet 0.53, used in conjunction with EXT_AUTH_CRYPTOED
  * 0xA4 (EXT_AUTH_CRYPTOED)
  * 0xA5 (EXT_CONNGRANT) appeared in BitComet 0.48, used in conjunction with EXT_CONNACCEPT
  * 0xA6 (EXT_CONNACCEPT)
  * 0x06 (?) announced by BitSpirit instead of EXT_CONNACCEPT
  * 0xA7 (EXT_CHAT_MESSAGE) appeared in BitComet 0.53, vanished in 0.71
  * 0xA9 (EXT_HASH_REQ) appeared in BitComet 0.54, vanished in 0.71, used in conjunction with EXT_HASH
  * 0xAA (EXT_HASH)
  * 0xAB (EXT_REPORT_RATE_old) appeared in BitComet 0.54, was replaced by EXT_REPORT_RATE_new in 0.57
  * 0xAC (EXT_REPORT_INFO) appeared in BitComet 0.54, vanished in 0.71, reappeared in 0.82
  * 0xAD (EXT_REPORT_RATE_new) appeared in BitComet 0.57, vanished in 0.75, reappeared in 0.82
  * 0xAE (EXT_BC_PASSPORT) appeared in BitComet 0.75
  * 0xAF (EXT_DHE_PREFERRED) appeared in BitComet 0.75
  * 0xB0 (?) appeared in BitComet 0.86
  * 0xC0 (?) does not correspond to a message id, appeared in BitComet 0.49

A minimum implementation needs only accept EXT_SUPPORT, but EXT_PEERREQ and EXT_PEERS are supported by all known implementations.

###Reserved Bytes

_The reserved bits are numbered 1-64 in the following table for ease of
identification. Bit 1 corresponds to the most significant bit of the first
reserved byte. Bit 8 corresponds to the least significant bit of the first
reserved byte (i.e. byte[0] |= 0x01). Bit 64 is the least significant bit of
the last reserved byte i.e. byte[7] |= 0x01_

_ An orange bit is a known unofficial extension, a red bit is an unknown unofficial extension._

