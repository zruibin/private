
<!--BEGIN_DATA
{
    "create_date": "2019-12-07 15:21", 
    "modify_date": "2019-12-07 15:21", 
    "is_top": "0", 
    "summary": "WebRTC的拥塞控制和带宽策略", 
    "tags": "WebRTC、C/C++", 
    "file_name": "WebRTC的拥塞控制和带宽策略.md"
}
END_DATA-->


#### <p>原文出处：<a href='https://mp.weixin.qq.com/s/Ej63-FTe5-2pkxyXoXBUTw' target='blank'>WebRTC的拥塞控制和带宽策略</a></p>

> 网络的波动带来的卡顿直接影响着用户的体验，在WebRTC中设计了一套基于延迟和丢包反馈的拥塞机制（GCC）和带宽调节策略来保证延迟、质量和网路速度之间平衡，本文中重点是介绍基于trendline滤波的评估模型。本文来自学霸君资深架构师袁荣喜和萍乡学院辛锋的投稿，并由LiveVideoStack全文发布。

文 / 袁荣喜，辛锋

在视频通信的技术领域WebRTC已成为主流的技术标准，WebRTC包涵了诸多优秀的技术，譬如：音频数字信号处理技术（AEC, NS, AGC）、编解码技术、实时传输技术、P2P技术等，这些技术目的都是为了实现更好实时音视频方案。但是在高分辨率视频通信过程中，通信时延、图像质量下降和丢包卡顿是经常发生的事，甚至在WiFi环境下，一次视频重发的网络风暴可以引起WiFi网络间歇性中断，通信延迟和图像质量之间存在的排斥关系是实时视频过程中的主要矛盾。

分析WebRTC是如何解决这个矛盾之前，先来看看我们在在线教育互动的生产环境统计到的视频延迟和人感官的关系，大致如下：

<table style="line-height: inherit;"><tbody><tr class=""><td width="260" valign="top" style="word-break: break-all;"><p style="margin-left: 16px;margin-right: 16px;line-height: 1.5em;"><span style="font-size: 16px;color: rgb(89, 89, 89);">0 ~ 400毫秒</span></p></td><td width="262" valign="top" style="word-break: break-all;"><p style="margin-left: 16px;margin-right: 16px;line-height: 1.5em;"><span style="font-size: 16px;color: rgb(89, 89, 89);">人感觉不到视频在通信过程中的延迟</span></p></td></tr><tr><td width="253" valign="top" style="word-break: break-all;"><p style="margin-left: 16px;margin-right: 16px;line-height: 1.5em;"><span style="font-size: 16px;color: rgb(89, 89, 89);">400 ~ 800毫秒</span></p></td><td width="262" valign="top" style="word-break: break-all;"><p style="margin-left: 16px;margin-right: 16px;line-height: 1.5em;"><span style="font-size: 16px;color: rgb(89, 89, 89);">人能感觉到轻微延迟，但不影响通信互动</span></p></td></tr><tr><td width="269" valign="top" style="word-break: break-all;"><p style="margin-left: 16px;margin-right: 16px;line-height: 1.5em;"><span style="font-size: 16px;color: rgb(89, 89, 89);">800毫秒以上</span></p></td><td width="262" valign="top" style="word-break: break-all;"><p style="margin-left: 16px;margin-right: 16px;line-height: 1.5em;"><span style="font-size: 16px;color: rgb(89, 89, 89);">人能感觉到延迟而且影响通信互动</span></p></td></tr></tbody></table>


也就是说，通信过程中最好将视频延迟控制在800毫秒以内。除了延迟，视频图像质量也是个对人感官产生差异的关键因素，我们以640x480分辨率每秒24帧的H264编码情况下视频码率和人感官之间的关系（这组数据是我们通过小范围线上用户投票打分的数据）：

<table><tbody><tr class=""><td width="266" valign="top" style="word-break: break-all;"><p style="margin-left: 1em;margin-right: 1em;line-height: 1.5em;"><span style="font-size: 16px;color: rgb(89, 89, 89);">800kbps以上</span></p></td><td width="248" valign="top" style="word-break: break-all;"><p style="margin-left: 1em;margin-right: 1em;line-height: 1.5em;"><span style="font-size: 16px;color: rgb(89, 89, 89);">人对视频清晰度满意,感觉不到视频图像中的信息丢失</span></p></td></tr><tr><td width="267" valign="top" style="word-break: break-all;"><p style="margin-left: 1em;margin-right: 1em;line-height: 1.5em;"><span style="font-size: 16px;color: rgb(89, 89, 89);">480 ~ 800kbps<span class="" style="color: rgb(89, 89, 89);font-size: 16px;white-space: pre;">	</span></span></p></td><td width="248" valign="top" style="word-break: break-all;"><p style="margin-left: 1em;margin-right: 1em;line-height: 1.5em;"><span style="font-size: 16px;color: rgb(89, 89, 89);">人对视频清晰度基本满意，有时能感觉到视频图像中的信息丢失</span></p></td></tr><tr><td width="267" valign="top" style="word-break: break-all;"><p style="margin-left: 1em;margin-right: 1em;line-height: 1.5em;"><span style="font-size: 16px;color: rgb(89, 89, 89);">480kbps以下</span></p></td><td width="248" valign="top" style="word-break: break-all;"><p style="margin-left: 1em;margin-right: 1em;line-height: 1.5em;"><span style="font-size: 16px;color: rgb(89, 89, 89);">人对视频清晰度不满意，大部分时候无法辨认图像中的细节信息</span></p></td></tr></tbody></table>


从上面的描述可以知道视频质量保持在一个可让人接受的质量范围是需要比较大的带宽码率支持的，如果加上控制延迟，则更需要网络有很好速度和稳定性。但是很不幸，我们现阶段的移动网络和家用WiFi并不是我们想象中的那么好，很难做到在实时视频通信中一个让人非常满意的程度。为了解决以上几个问题，WebRTC设计了一套基于延迟和丢包反馈的拥塞机制（GCC）和带宽调节策略来保证延迟、质量和网路速度之间平衡，这是一个持续循环过程，如下图：

![](./image/20191207-15200.webp)

图1：拥塞控制循环示意图


1） estimator通过RTCP的feedback反馈过来的包到达延迟增量和丢包率信息计算出网络拥塞状态并评估出适合当前网络传输的码率，根据这个码率改变视频编码器码率，然后改变pacer的码率

2） pacer会根据这个码率改变pacer的网络发送速度和padding比例，并用新的网络发送速度来定时触发发包事件。

3） sender收到pacer的发送事件，进行RTP报文发送。

4） receiver接收到RTP报文，进行arrival time统计和丢包统计

5） feedback定时对receiver统计的信息进行RTCP编码，并反馈到发送端的estimator进行新一轮的码率评估。

以上是整个WebRTC拥塞控制和带宽调节过程，下面这个示意图是这个过程涉及到WebRTC内部模块关系。  

![](./image/20191207-15201.webp)

图2：WebRTC的拥塞控制模块关系图

需要说明的是红框中基于接收端的kalman filter带宽评估模型已经在新版本的WebRTC中不采用了，只做了向前版本兼容，新版本的WebRTC都是采用发送端的trendline滤波器来做延迟带宽评估，本文中重点是介绍基于trendline滤波的评估模型，下面依次来分析WebRTC的这五个过程。

####1 estimator

estimator的功能就是通过接收端反馈过来的包到达时刻信息、丢包信息和REMB信息进行当前网络状态的码率评估，WebRTC拥塞控制有两部分：基于延迟的拥塞控制和基于丢包的拥塞控制，它是一个尽力而为的拥塞控制算法，牺牲了拥塞控制的公平性换取尽量大的吞吐量。从设计结构来描述向它输入延迟和丢包信息，它就会输出一个适应当前网络状态的码率值。示意图如下：

![](./image/20191207-15202.webp)

图3：WebRTC的CC estimator输入与输出  

从上图可以看出，estimator基于延迟的拥塞控制是通过trendline滤波再进行过载判断，最后根据过载情况进行aimd码率调控评估出一个bwebitrate码率，这个码率会合丢包评估出来的码率和remb来决定最后的码率。

##### 1.1 基于延迟的拥塞控制

基于延迟的拥塞控制是通过每组包的到达时间的延迟差（delta delay）的增长趋势来判断网络是否过载，如果过载进行码率下调，如果处于平衡范围维持当前码率，如果是网络承载不饱满进行码率上调。这里有几个关键技术:包组延迟评估、滤波器趋势判断、过载检测和码率调节。

###### 1.1.1 包组与延迟

WebRTC在评估延迟差的时候不是对每个包进行估算，而是采用了包组间进行延迟评估，这符合视频传输（视频帧是需要切分成多个UDP包）的特点，也减少了频繁计算带来的误差。那么什么是包组呢？就是距包组中第一个包的发送时刻t0小于5毫秒发送的所有的包成为一组，第一个超过5毫秒的包作为下一个包组第一个包。为了更好的说明包组和延迟间的关系，先来看示意图：

![](./image/20191207-15203.webp)
图4：包组与延迟示意图

上图中有两个包组G1和G2, 其中第100号包与103号包的时间差小于5毫秒，那么100 ~ 103被划作一个包组。104与100之间时间超过5毫秒，那么104就是G2的第一个包，它与105、106、107划作一个包组。知道了包组的概念，那么我们怎么通过包组的延迟信息得到滤波器要的评估参数呢？滤波器需要的三个参数：发送时刻差值（delta_timestamp）、到达时刻差值(delta_arrival)和包组数据大小差值(delta_size)。从上图可以得出：

![](./image/20191207-15204.webp)  

###### 1.1.2 滤波器

我们通过包组信息计算到了delta_timestamp、delta_arrival和delta_size,那么下一步就是进行数据滤波来评估延迟增长趋势。在WebRTC实现了两种滤波器来进行延迟增长趋势的评估，分别是：kalman filter和trendline filter, 从图2中我们知道kalman filter是运行在接收端的，我在这里以不做介绍，有兴趣的可以参考https://www.jianshu.com/p/bb34995c549a。

这里介绍trendline filter，我们知道如果平稳网速下传输数据的延迟时间就是数据大小除以速度，如果这数据块很大，超过恒定网速下延迟上限，这意味着要它要占用其他后续数据块的传输时间，那么如此往复，网络就产生了延迟和拥塞。Trendline filter通过到达时间差、发送时间差和数据大小来得到一个趋势增长值，如果这个值越大说明网络延迟越来越严重，如果这个值越小，说明延迟逐步下降。以下是计算这个值的过程。

先计算单个包组传输增长的延迟，可以记作：  

![](./image/20191207-15205.webp)  

然后做每个包组的叠加延迟,可以记作：

![](./image/20191207-15206.webp)  

在通过累积延迟计算一个均衡平滑延迟值，alpha=0.9可以记作：

![](./image/20191207-15207.webp)  

然后统一对累计延迟和均衡平滑延迟再求平均，分别记作：

![](./image/20191207-15208.webp)  

我们将第i个包组的传输持续时间记作:

![](./image/20191207-15209.webp)  

趋势斜率分子值为：

![](./image/20191207-15210.webp)

趋势斜率分母值为：

![](./image/20191207-15211.webp)


最终的趋势值为：

![](./image/20191207-15212.webp)

######1.1.3过载检测

在计算得到trendline值后WebRTC通过动态阈值gamma\_1进行判断拥塞程度，trendline乘以周期包组个数就是m\_i,以下是判断拥塞程度的伪代码：

![](./image/20191207-15213.webp)

通过以上伪代码就可以判断出当前网络负载状态是否发生了过载，如果发生过载，WebRTC是通过一个有限状态机来进行网络状态迁徙，关于状态机细节可以参看下图：

![](./image/20191207-15214.webp)

图5:过载检测状态机

从上图可以看出，网络状态机的状态迁徙是由于网络过载状态发生了变化，所以状态迁徙作为了aimd带宽调节的触发事件，aimd根据当前所处的网络状态进行带宽调节，其过程是处于Hold状态表示维持当前码率，处于Decr状态表示需要进行码率递减，处于Incr状态需要进行码率递增。那他们是怎么递增和递减的呢？WebRTC引入了aimd算法解决这个问题。

###### 1.1.4 AIMD码率调节

aimd的全称是Additive Increase Multiplicative Decrease，意思是：和式增加，积式减少。aimdcontroller是TCP底层的码率调节概念，但是WebRTC并没有完全照搬TCP的机制，而是设计了套自己的算法，用公式表示为：

![](./image/20191207-15215.webp)  

如果处于Incr状态，增加码率的方式分为两种：一种是通信会话刚刚开始，相当于TCP慢启动，它会进行一个倍数增加，当前使用的码率乘以系数，系数是1.08；如果是持续在通信状态，其增加的码率值是当前码率在一个RTT时间周期所能传输的数据速率。

如果处于Decrease状态，递减原则是:过去500ms时间窗内的最大acked bitrate乘上系数0.85,acked bitrate通过feedback反馈过来的报文序号查找本地发送列表就可以得到。

aimd根据上面的规则最终计算到的码率就是基于延迟拥塞评估到的bwe bitrate码率。


##### 1.2基于丢包的拥塞控制

除了延迟因素外，WebRTC还会根据网络的丢包率进行拥塞控制码率调节，描述如下：

![](./image/20191207-15216.webp)  

解释下上面的公式：  

当丢包率<2%时，这个时候会将码率（base bitrate）增长5%,这个码率(base
bitrate)并不是当前及时码率，而是单位时间窗周期内出现的最小码率,WebRTC将这个时间窗周期设置在1000毫秒内。因为loss fraction是从接收端反馈过来的，中间会有时间差，这样做的目的是防止网络间歇性统计造成的网络码率增长过快而网络反复波动。

当 2% < 丢包率 < 10%,维持当前的码率值

当 丢包率 >= 10%, 按丢包率进行当前码率递减，等到新的码率值

**丢包率决策出来的码率（base bitrate）只是一个参考值，WebRTC实际采用的带宽是base bitrate、remb bitrate和bwe bitrate中的最小值，这个最小值作为estimator最终评估出来的码率**

#### 2 pacer

在estimator根据网络状态决策出新的通信码率（target bitrate），它会将这个码率设置到pacer当中，要求pacer按照新的码率来计算发包频率。因为在视频通信中，单帧视频可能有上百KB,如果是当视频帧被编码器编码出来后，就立即进行RTP打包发送，瞬时会发送大量的数据到网络上，可能会引起网络衰减和通信恶化。WebRTC引入pacer，pacer会根据estimator评估出来的码率，按照最小单位时间（5ms）做时间分片进行递进发送数据，避免瞬时对网络的冲击。**pacer的目的就是让视频数据按照评估码率均匀的分布在各个时间片里发送，**
所以在弱网的WiFi环境，pacer是个非常重要的关键步骤。以下WebRTC中pacer的模型关系：

![](./image/20191207-15217.webp)

图6：pacer模型图

WebRTC中pacer的流程比较清晰，分为三步：

1. 如果一帧图像被编码和RTP切分打包后，先会将RTP报文存在待发送的队列中，并将报文元数据(packet id, size, timestamp, 重传标示)送到pacer queue进行排队等待发送，插入队列的元数据会进行优先级排序。

2. pacer timer会触发一个定时任务事件来计算budget，budget会算出当前时间片网络可以发送多少数据，然后从pacer queue当中取出报文元数据进行网络发送。

3. 如果pacer queue没有更多待发送的报文，但budget却还可以发送更多的数据，这个时候pacer会进行padding报文补充。

从上面的步骤描述中可以看出pacer有几个关键技术：pace queue、padding、budget。

##### 2.1 pace queue与优先级

pace queue是一个基于优先级排序的多维链表，它并不是一个先进先出的fifo,而是一个按优先级排序的list。

报文优先级规则

1. 优先级高的报文排在fifo的前面，低的排在后面。
2. 优先级是最先判断报文的QoS等级，等级越小的优先级越高
3. 其次是判断重发标示，重发的报文比普通报文的优先级更高
4. 再次是判断视频帧timestamp，越早的视频帧优先级更高。


pacer每次触发发送事件时是先从queue的最前面取出优先级最高的报文进行发送，这样做的目的是让视频在传输的过程中延迟尽量小，重传的报文尽快能到达防止等待卡顿。pace queue还可以设置最大延迟，如果超过最大延迟，会计算queue中数据发送所需要的码率，并且会把这个码率替代target bitrate作为budget参考码率来加速发送。

##### 2.2 budget

budget是个评估单位时间内可以发送多少数据量的一个机制，因为pacer是会根据pace
timer定时来触发发送检查。Budget会根据评估出来的参考码率计算这次定时事件能发送多少字节，可以表示为：

![](./image/20191207-15218.webp)

delta time是上次检查时间点和这次检查时间点的时间差。

target bitrate是pacer的参考码率，是由estimator根据网络状态评估出来的。

remain_bytes每次触发发包时会减去发送报文的长度size,如果remain_bytes > 0，继续从pace queue中取下一个报文进行发送，直到remain_bytes <=0 或者 pace queue没有更多的报文。

##### 2.3 pacer延迟

那么肯定有人会有疑问pacer queue和budget进定量计算来发送网络报文，相当于cache等待发送，难道不会引起延迟吗？可以肯定的说会引起延迟，但延迟不严重。pacer产生的延迟可以表示为：

![](./image/20191207-15219.webp)

假如评估出来的码率是10mbps, 一个视频关键帧的大小是300KB,那么这个关键帧造成的pacer
delay是240毫秒。从实际应用观察到的关键帧引起的pace delay在200 ~ 400毫秒之间，这个值相对于视频传输来说是比较大的，但是不严重。WebRTC为了减少这个延迟，会评估出尽量大的bitrate。那么怎么评估出尽量大的码率呢？从前面的estimator描述中我们知道要发送出尽量多的数据才能评估尽量大的码率，但是视频编码器不会发送多余的数据，所以WebRTC引入了padding机制来保障发送尽量大的数据来探测网络带宽上限。

##### 2.4 padding

pace padding除了保障能pace delay尽量小外，它可以让有限的带宽获得尽可能好的视频质量。padding的工作原理很简单，就是在单位时间片内把budget还剩余的空闲用padding数据填满。我个人认为**padding只是适合点对点通信，一旦涉及到多点分发，会因为padding占用很多服务转发带宽，这并不是一件好事情。**

#### 3 sender

WebRTC的发送模块和拥塞控制控制相关的主要是增加了附加的RTP扩展来携带便宜接收端统计丢包率和延迟间隔的信息、配合pacer的发包策略、带宽分配和FEC策略的信息。

##### 3.1 RTP扩展

WebRTC为了配合接收端进行延迟包序列和丢包统计做了下列扩展：

>transport sequence传输通道的只增sequence，每次发送报文时自增长，配合接收端统计丢包、通过反馈这个sequence可以计算得到发包的时刻。
>
>
>TransmissionOffset 发送报文的相对时刻，这个相对时刻值t是发送报文的绝对时刻T1和视频帧时间戳T0差值。早期的WebRTC是在接收端进行estimate bitrate，所以过载判断是在接收端完成的，这个值就是为了kalman filter计算发包造成的延迟用的，新版本还携带这个值以便低版本的WebRTC能兼容。

##### 3.2  packet cache    

packet cache是一个key/value结构的包缓冲池，视频帧在进行RTP分片打包后不会立即发送出去，而是要等待pacer的发送信号进行发送。所以打包后会按[id,packet]键值对插入到packet cache中。一般packet cache会保存600个分片报文，最大9600个，插入新的会将最旧的报文删除，packet cache这样做的目的除了配合pacer发送外，也为了后面响应nack的丢包重传。

##### 3.3 NACK与丢包重传

![](./image/20191207-15220.webp)

图7:RTP NACK过程的示意图


WebRTC在评估到收发端之间RTT延迟比较小的时候会采用NACK来进行丢包补偿，NACK是一个请求重发过程，其流程如上图所示。这个过程有一个问题是在网络抖动和丢包很厉害的情况下有可能造成同一时刻收到很多NACK的重传请求，发送端瞬间把这些重传请求放入pacer中进行重发，这样pacer的延迟会增大，而且pace的参考码率会随着pace queue的延迟控制变的很大而出现间歇性网络风暴。WebRTC在处理NACK重传时设计了一个重传码率控制器,其设计原理是通过统计
单位时间窗口周期中发送的字节数据来限流，如果这个时间窗内发送的数据的码率大于estimator评估的码率，不进行当前NACK请求的重传，等待下一个NACK。

##### 3.4 FEC与码率分配

WebRTC应对丢包时除了NACK方式，在收发端之间RTT很大时候会开启FEC来进行丢包补偿，我们在这里不介绍FEC具体算法，只介绍FEC的码率分配策略。从整个通信机制我们很容易得出这样一个共识：

![](./image/20191207-15221.webp)

FEC bitrate到底应该设置多大呢？它先根据feedback中反馈过来的丢包率(loss
fraction)来确定使用哪一种FEC，在根据每中FEC和丢包率来确定FEC使用的码率，但需要满足一下条件:

![](./image/20191207-15222.webp)

feedback的码率被设定为target bitrate的5%,WebRTC是通过控制feekback的频率来进行调控分配的。padding bitrate是通过pacer queue和budget来控制的。Target
bitrate减去这些码率之和就是给视频编码器的码率。每次estimator评估出来码率后，会先进行这些计算得到最后的video bitrate,并将这个值作为编码器的编码码率，以此来达到防止拥塞的目的。

#### 4 receiver

receiver模块的工作相对来说比较简单，它就做三件事情:记录每个报文的到达时刻(arrival timestamp)、丢包率(lost fraction)和receiver bitrate。早期的WebRTC提供了图2红框当中kalman filter评估码率的评估器，因为kalman filter怕抖动特性且需要借助remb心跳进行反馈，remb的反馈周期是1秒，在收发端网络间歇性断开或者大抖动下，容易失效，所以WebRTC采用了在发送端进行估算，整个逻辑也更加简便。

#####4.1 报文到达时间

![](./image/20191207-15223.webp)

图8：到达报文统计图

上图是一个统计RTP报文到达时刻的序列图，图中的seq是RTP扩展中的transport sequence,接收端用一个k/v（[seq,arrival timestamp]）键值对数据结构来保存最近500毫秒未反馈的到达时刻信息,通过时间窗口周期来进行淘汰老的到达时刻记录。

##### 4.2 丢包率计算


丢包率计算过程是这样的，我们把上次统计丢包率时刻的最大sequence记着prev_seq, 把当前收到的最大sequence记着cur_seq,当前统计丢失的报文记着count，WebRTC在RTCP中描述丢包率采用的是uint8，为了保证精确度将256记着100%的丢包率，那么很容易得：

![](./image/20191207-15224.webp)

这里需要提的是WebRTC在统计报文是否丢失是通过sequence的连续性和网络的jitter时间来确定的，只有落在jitter抖动范围之外的丢包才是算是作丢包。

##### 4.3 接收码率统计

接收端码率统计采用的是最近单位时间窗（1000毫秒）周期内收到的的字节数来计算，WebRTC设计了一个1毫秒为最小单位的窗口数组来进行统计,每个最小单位是数字，这个数字是在这个时刻收到的网络数据大小，大致的示意图如下：

![](./image/20191207-15225.webp)

图9：接收码率统计示意图

计算码率只需要将红框中所有的数字加起来，当时间发生改变后，就红框就向右移动并且填写新时刻接收到的数据大小，等下一个统计时刻既可。

#### 5 feedback

前面介绍的estimator依赖于feedback反馈的报文到达时刻和丢包率来进评估码率的，也就是说feedback需要将这些信息及时反馈给接收端，主要是记录的报文到达时刻、通道丢包率和remb带宽。因为报文到达时刻和丢包率统计都是多个数据项，WebRTC利用了report block来进行编码存放。为了有效的利用RTCP的report block空间，WebRTC采用了相对时间转换和位压缩算法来对到达时间序列做编码压缩。

除了report编码，feedback的周期也很重要，如果是单纯的remb反馈，一般是1秒一次反馈。但如果是需要反馈报文的到达时间，它会根据占用5%的tar get bitrate来计算发送feedback的时间间隔，计算流程如下：

![](./image/20191207-15226.webp)

feedback interval需要满足一个条件：50ms < interval < 250ms,这个条件中的 50ms< internal是为了防止interval太小造成发送feedback太过频繁而消耗网络性能，而interval < 250ms是为了防止feedback频次太低造成estimator反应迟钝。

#### 6 总结

以上就是WebRTC拥塞控制和码率调节策略的5个过程，里面涉及到很多传输相关的技术，我在这里也是简单介绍了下其工作原理，很多细节的并没有描述出来，也很难描述出来，有兴趣的同学可以翻看WebRTC的源代码。如果觉得webRTC代码费劲，我照虎画猫将WebRTC的拥塞控制用C重新实现了个简易版本,但是去掉了padding，可到<a href='https://github.com/yuanrongxi/razor' target='blank'>https://github.com/yuanrongxi/razor</a>下载。

##### 6.1 效果

WebRTC的GCC在网络适应上表现还是比较良好的，既然兼顾延迟，也能兼顾丢包，网络发生拥塞时在2 ~ 3秒内能评估出相对的码率来适应当前的网络状态，但是会造成短时间的卡顿。对于网络发生间歇性丢包，在2秒左右能将传输码率适配到当前网络状态。它在网络相对稳定且延迟较大的网络进行高分辨率传输时，视频很稳定，适合长距离延迟稳定的网络环境。在弱网环境下，WebRTC容易将码率降到很低而造成图像失真。

#### 6.2 网络大抖动

对于乱序和抖动WebRTC的拥塞控制显得有点无力，如果抖动超过rtt*2/3时，基于kalman
filter的带宽评估机制不起作用（不知道是不是我用错了）；基于trendline滤波的评估机制波动很大，敏感度不够，不能完全反应当前的网络过载状态，尤其是在终端Wi-Fi拥挤的情况下，比较容易造成间歇性风暴。

#### 6.3 延迟问题

WebRTC的pacer在传输大分辨率视频时，关键帧会引起大约200毫秒的延时，尤其是在移动4G网络下这个问题更加明显，海康威视工程师郑鹏提出了用H.264的intre\_refresh模式来应对，在测试过程中确实比较适合WebRTC用来减少关键帧造成的延迟，但是intre\_refresh是普通模式编码CPU的3倍左右，而且很多移动设备的编码器不一定支持。

总之，WebRTC的拥塞控制存在反应慢、怕抖动的特性，但是这块也是WebRTC改进最为频繁的模块，几乎每个版本都有新的改进。要彻底解决这样的问题，需要从视频编码器和网络传输进行融合来解决，以后我用单独的篇幅来介绍下这样的解决方案。


<hr>

#### <p>原文出处：<a href='https://www.jianshu.com/p/9061b6d0a901' target='blank'>WebRTC的拥塞控制技术（Congestion Control）</a></p>

### 1. 概述

对于共享网络资源的各类应用来说，拥塞控制技术的使用有利于提高带宽利用率，同时也使得终端用户在使用网络时能够获得更好的体验。在协议层面上拥塞控制是TCP的一个总要的组成部分；但是对于非面向链接的传输层协议，如UDP，其在协议层面上并没有对拥塞控制进行强制性的要求，这样做保证了最优的传输性能，且在拥塞控制的设计上也保留了更大的灵活性。

WebRTC为我们提供了强大的音视频媒体引擎，前端开发者可以通过调用几个简单的js接口就能实现基于Web浏览器的实时音视频通信。而在媒体数据传输上，WebRTC采用了实时性较强UDP协议，并使用了RTP/RTCP技术。本文的主要内容就是介绍WebRTC中基于RTP/RTCP实现的拥塞控制技术。

### 2. 拥塞控制算法

WebRTC采用了两种拥塞控制算法：（1）基于延迟（delay-based）的拥塞控制算法；（2）基于丢包（loss-based）的拥塞控制算法。算法（1）由数据的接收方实现，接收方需要记录每个数据包到达的时间和大小，并计算每个数据分组之间（inter-group）的延迟的变化，由此判断当前网络的拥塞情况，并最终输出码率估计值由RTCP feedback（TMMBR或REMB）反馈给发送方；算法（2）则由数据的发送方来实现，发送方通过从接收方周期性发来的RTCP RR（Receiver Report）中获取丢包信息以及计算RTT，并结合TMMBR或REMB中携带的码率信息算得最终的码率值，然后由媒体引擎根据码率来配置编码器，从而实现码率的自适应调整。从上面的描述可以看出，这两个算法在系统中并不是孤立存在的。

![](./image/20191207-152109.webp)
拥塞控制算法时序图.png

#### 2.1 基于延迟（delay-based）的拥塞控制算法

基于延迟的拥塞控制算法可以分成以下4个部分：（1）到达时间模型（arrive-time model）;（2）预过滤（Pre-filtering）；（3）到达时间滤波器（arrive-time filter）；（4）过载检测器（over-use detector）。

![](./image/20191207-152110.webp)
基于延迟的拥塞控制算法.png

##### 2.1.1 到达时间模型（arrive-time model）

设相邻两个数据分组到达接收方的时间间隔为t(i) - t(i-1)，而两者被发送的时间间隔则为T(i) - T(i-1)，那么就有延迟变量**d(i)=t(i)-t(i-1) - (T(i)-T(i-1))**。如果d(i) > 0，就说明数据在网络传输时存在延迟的现象。

在WebRTC中延迟变量d(i) = w(i)被视为随机过程W中一个采样点，并且是链路承载能力、网络当前传输状况以及当前发送速率等因素综合作用的结果。该随机过程W符合正态分布。当网络发生过载（over-use）时，我们期望w(i)会上升；当网络空闲（Under-use）时，则期望w(i)会下降。

测量方程进一步改写为 d(i) = m(i) + v(i)，其中m(i)符合均值为0的正态分布（标准正态分布），v(i)表示为网络抖动等因素带来的对数据延迟的影响。

##### 2.1.2 预过滤（Pre-filtering）

预过滤的目的是处理由于通道中断造成的延迟瞬间变大的情况。在通道发生中断时，数据包会持续进入网络队列中，而当通道恢复时，所有的数据包会在一个burst时间（5ms）里面全部发送，而这些数据包可能原先包分布于多个数据分组。而预过滤所要做的就是将这些在同一个burst时间里发送的数据包合为一个数据分组。

>这里涉及到了WebRTC中关于数据传输的一个设计--**PacedSender**。Encoded数据完成RTP封装之后先是被保存在本地应用的队列中，而不是直接发送到网络。此时可以将PacedSender视为一个数据发送的节拍器，它每隔一个burst时间启动一次，启动之后会将队列中的RTP包全数发出。

数据包会在下面两种情况下被划分到一个数据分组：

  * 在同一个burst时间区间内被发送的数据包序列；
  * 一个数据包与相邻数据包的到达时间间隔小于一个burst时间，同时d(i) < 0，那么这个数据包将会被划到当前的分组中。

#####2.1.3 到达时间滤波器（arrive-time filter）

在此系统希望通过预测m(i)来检测当前的网络是否过载；而这里所采用的预测方法是**卡尔曼滤波（Kalman filter）**。  
状态方程：m(i+1) = m(i) + u(i)， 其中u(i)表示为状态噪声，符合0均值正态分布。  
测量方程：d(i) = m(i) + v(i)， 其中v(i)表示为测量噪声，符合0均值正态分布。  
卡尔曼滤波器根据“5组公式”来迭代更新m(i) 的估计值m\_hat(i)，该估计值m\_hat(i)则是下文过载检测器的检测依据。关于卡尔曼滤波器如何实现预测的详细介绍在这里就不做展开了，可参考文献**[3]**。

##### 2.1.4 过载检测器（over-use detector）

通过Kalman 滤波器能够获得延迟变量m(i)的估计值，而过载检测器的工作原理其实就是通过m(i)与阈值del\_var\_th进行比较来对当前的网络拥塞状况进行检测。如果m(i) > del\_var\_th且m(i) > m(i-1)，同时该状态至少持续了overuse_time_th毫秒，则判断为网络过载（**Over-use**）；如果m(i) < -del\_var\_th，则判断为网络空闲（**Under-use**）；剩余的情况都被判断为**Normal**状态。

由此可见，阈值del\_var\_th的设计对于整个算法的性能来说至关重要。如果del\_var\_th的值设得过大，那么整个算法的动态就会显得过于平滑，此时只有在数据分组严重delay时检测器才会触发over-use的信号；相反的，如果del\_var\_th的值设得过小，那么检测器就会对delay非常敏感，从而导致频繁触发over-use信号。因此，WebRTC提出了针对阈值del\_var\_th的动态调整算法：

**del_vat_th(i) = del\_var\_th(i-1)+ (t(i) - t(i-1)) * K(i) * (|m(i)| - del\_var\_th(i-1))**

其中，当|m(i)| < del\_var\_th(i-1)时K(i)=K_d；否则，K(i)=K_u。

> 在WebRTC中本小节所涉及的各参数的参考值如下：  
_del\_var\_th(0) = 12.5 ms, overuse_time_th = 10 ms, K_u=0.01, K_d=0.00018_

##### 2.1.5 速率控制（rate control）

速率控制子系统根据当前网络的拥塞情况（由过载检测器提供），计算带宽估计值并请求发送方对速率进行调整。该子系统通过有限状态机对速率进行自适应调整。其状态迁移如下图所示：

![](./image/20191207-152111.webp)
速率控制状态机.png

  * **状态 Increase**： 表明当前没有检测到网络拥塞，在此状态下传输速率需要逐步增加；它先是通过乘性增加来调整速率（乘性因子为1.08），当速率接近临界值时再通过加性增加逐步收敛，而这里所谓的临界值是指上一次在**状态Decrease** 时统计的下行码率；
  * **状态 Decrease**： 表明当前检测到了网络拥塞，在此状态下传输速率需要逐步下降；在这里，WebRTC所采用的方法是乘性下降，其乘性因子为0.85；
  * **状态 Hold**： 表明保持当前的速率不做改变。

速率控制子系统最终会输出一个**带宽估计值A_hat**，并通过RTCP Feedback（TMMBR/REMB）请求发送方进行速率调整。

#### 2.2 基于丢包（Loss-based）的拥塞控制算法

基于丢包的拥塞控制是通过对**丢包率，RTT和带宽估计值A_hat**这三个参数进行决策而实现的。其中带宽估计值A_hat正是由上节中的速率控制子系统所提供。

基于丢包的拥塞控制在每次收到对方发送RTCP之后都会运行：

  * 当丢包率保持在[2%, 10%]时，当前数据发送方的带宽估计值As_hat保持不变；
  * 当丢包率大于10%时，带宽估计值将会降低：As\_hat(i) = As(i-1)*(1-p)，其中p为丢包率；
  * 当丢包率小于2%时，带宽估计值将会上升：As\_hat(i) = As(i-1)*1.05。

As_hat更新之后将与A_hat进行比较，然后取两者中的较小值作为最终的带带宽估计值。

> 其实在原生的代码中，系统还会将丢包率和RTT作为参数，通过**TFRC [RFC
5348]**的吞吐率计算公式对当前的带宽进行估计，而最终的估计值则是取三者中的最小值。

### 3. 后语

通过上文的介绍，我们知道WebRTC中的拥塞控制算法还是非常完备的。其分别针对数据包的延迟和丢包设计了delay-based和loss-based拥塞控制算法，在两者的共同作用之下，WebRTC能够满足大部分场景下的实时视频通话业务。但是，如果有要对WebRTC中的媒体引擎进行移植的朋友，首先要分析一下WebRTC的拥塞控制算法是否满足你的业务需求：如果是开发独立应用，由于业务闭环，直接使用现有的算法应该问题不大；但是，如果是用于开发提供类似VoLTE/VoWIF
I这样的运营商增值服务的应用，需要依据运营商的技术手册和[3GGP协议](https://www.jianshu.com/p/e903570ed350)等来对拥塞控制算法进行适配。

> **Reference**  
[1] A Google Congestion Control Algorithm for Real-Time Communication draft-ietf-rmcat-gcc-02  
[2] RFC 5348  
[3] [http://blog.csdn.net/xiahouzuoxin/article/details/39582483](https://link.jianshu.com?t=http://blog.csdn.net/xiahouzuoxin/article/details/39582483)  
[4] 3GPP TS 26.114
