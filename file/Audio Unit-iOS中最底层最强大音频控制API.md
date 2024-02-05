 
<!--BEGIN_DATA
{
    "create_date": "2020-08-02 20:53", 
    "modify_date": "2020-08-02 20:53", 
    "is_top": "0", 
    "summary": "Audio Unit: iOS中最底层最强大音频控制API", 
    "tags": "iOS", 
    "file_name": "Audio Unit-iOS中最底层最强大音频控制API.md"
}
END_DATA-->

####<p>原文出处：<a href='https://juejin.im/post/6844903838994923534' target='blank'>Audio Unit: iOS中最底层最强大音频控制API</a></p>

####阅读前提:

  * Audio Session基础([Audio Session](https://juejin.im/post/6844903834385383431))
  * Core Audio基本数据结构([Core Audio](https://juejin.im/post/6844903834293108743))
  * 音视频基础知识
  * C/C++ 简单数据结构,函数使用

以下概念是文中常用的词语,因为其含义一般直接用英文表达, 一般不需中文翻译,可将其理解为固定名词词组.

  * audio unit: 主要介绍的技术名称
  * audio processing graph: 另一种处理audio unit的技术
  * node: 承载audio unit的容器
  * input scope /output scope : 可理解为音频流动的位置(比如从input scope流向output scope)
  * input element : 连接输入端硬件(如麦克风)的一个组件.
  * output element : 连接输出端硬件(如扬声器)的一个组件.
  * bus: 与element概念相同,在文中强调信号流时使用“bus”，在强调音频单元的特定功能方面时使用“element”，\
  * I/O Units: 输入输出常用的audio unit类型,其中包括Remote I/O unit, Voice-Processing I/O, Generic Output unit三种类型.

注意每个element还可能具有input scope与output scope.

####Overview

Audio Unit : iOS提供音频处理插件,支持混合,均衡,格式转换和实时输入/输出,用于录制,播放,离线渲染和实时对话,例如VoIP(互联网协议语音).可以从iOS应用程序动态加载和使用它.

Audio Unit通常在称为audio processing graph的封闭对象的上下文中工作，如图所示。在此示例中，您的应用程序通过一个或多个回调函数将音频发送到graph中的第一个audio unit，并对每个audio unit进行单独控制。 最终生成的I / O unit直接输出给连接的硬件.

![](./image/20200802-204931)

audio unit是iOS音频层面中最底层的编码层,如果要充分利用它需要对audio unit有更深入的了解.除非你需要实时播放同步的声音,低延迟的输入输出或是一些音频优化的其他特性,否则请使用Media Player, AVFoundation, OpenAL, or Audio Toolbox等上层框架.

#####优点

Audio Unit提供了更快,模块化的音频处理,同时提供了强大的个性化功能，如立体声声像，混音，音量控制和音频电平测量。如果想充分使用它的功能,必须深入了解包括音频数据流格式，回调函数和音频单元架构等基础知识。

  * 出色的响应能力: 可以通过回调函数访问实时的音频数据.可以直接使用audio unit合成乐器音,实时同步语音.
  * 动态的重新配置: 围绕AUGraph opaque类型构建的 audio processing graph API允许以线程安全的方式动态组装，重新配置和重新排列复杂的音频处理链，同时处理音频。这是iOS中唯一提供此功能的音频API。

#####生命周期

  * 运行时,获取对动态可链接库的引用，该库定义您要使用的audio unit
  * 新建一个audio unit实例
  * 根据需求配置audio unit
  * 初始化audio unit以准备处理音频
  * 开启audio unit
  * 控制audio unit
  * 用完后释放audio unit

#####选择设计模式

  * 配置audio session负责app与硬件间的交互,配置I/O unit: I/O units有两个独立元素(elements)组成,一个从输入端硬件接收音频数据,一个将音频数据送给输出端硬件.可以根据需求选择我们要开启的元素.
  * 构造audio processing graph: 在audio processing graph中，必须指定音频数据流格式.
  * 控制audio units的生命周期:建立audio unit的连接并注册回调函数.

###一.工作原理

![](./image/20200802-204937)

如图所示,audio unit是iOS中音频最底层的API,audio unit仅在高性能,专业处理声音的需求下使用才有意义.

####1. audio unit提供了快速的,模块化的音频处理

使用场景

  * 以最低延迟的方式同步音频的输入输出,如VoIP.
  * 手动同步音视频,如游戏,直播类软件
  * 使用特定的audio unit:如回声消除,混音,音调均衡
  * 一种处理链架构:将音频处理模块组装成灵活的网络。这是iOS中唯一提供此功能的音频API。

#####1.1. iOS中的audio unit

<table>
<thead>
<tr>
<th>功能</th>
<th>Audio units</th>
</tr>
</thead>
<tbody>
<tr>
<td>Effect</td>
<td>iPod Equalizer</td>
</tr>
<tr>
<td>Mixing</td>
<td>3D Mixer,Multichannel Mixer</td>
</tr>
<tr>
<td>I/O</td>
<td>Remote I/O, Voice-Processing I/O, Generic Output</td>
</tr>
<tr>
<td>Format conversion</td>
<td>Format Converter</td>
</tr>
</tbody>
</table>

  * Effect Unit

提供一组预设均衡曲线，如重低音,流行音等等。

  * Mixer Units

    * 3D Mixer unit: OpenAL构建的基础,如果需要3D Mixer unit特性,建议直接使用OpenAL,因为它提供了很多封装好的功能强大的API.
    * Multichannel Mixer unit: 为一个或多个声道的声音提供混音功能,以立体声输出.你可以单独打开或关闭其中一个声道的声音,调节音量,快进快退等.
  * I/O Units

    * Remote I/O unit: 直接连接输入,输出的音频硬件,以低延迟的方式访问单个接收或发出的音频采样点.提供了格式转换功能,
    * Voice-Processing I/O: 通过声学的回声消除拓展了Remote I/O unit,常用于VoIP或语音通信的应用.它还提供了自动增益校正,语音处理质量调整和静音等功能.
    * Generic Output unit: 不连接音频硬件而是提供了一种机制:将处理链的输出传递给应用程序.通常用来做离线音频处理.
  * Format Converter Unit

通常通过I/O unit间接使用.

#####1.2. 同时使用两个Audio Unit APIs

iOS有一个用于直接处理audio units的API，另一个用于处理audio processing graphs,可以同时使用这两种API.然而这两种API中有一部分功能是相同的,如下:

  * 获取audio units的动态可链接库的引用
  * 实例化audio units
  * 连接audio units并注册回调函数
  * 启动和停止音频流

#####1.3. 指定Audio Unit属性以获取其引用对象

    
    
    AudioComponentDescription ioUnitDescription;
    ioUnitDescription.componentType          = kAudioUnitType_Output;
    ioUnitDescription.componentSubType       = kAudioUnitSubType_RemoteIO;
    ioUnitDescription.componentManufacturer  = kAudioUnitManufacturer_Apple;
    ioUnitDescription.componentFlags         = 0;
    ioUnitDescription.componentFlagsMask     = 0;

    AudioComponent foundIoUnitReference = AudioComponentFindNext (
                                              NULL,
                                              &ioUnitDescription
                                          );
    AudioUnit ioUnitInstance;
    AudioComponentInstanceNew (
        foundIoUnitReference,
        &ioUnitInstance
    );


`AudioComponentFindNext`:第一个参数设置为NULL表示使用系统定义的顺序查找第一个匹配的audio unit.如果你将上一个使用的audio unit引用传给该参数,则该函数将继续寻找下一个与之描述匹配的audio unit.

还可以使用audio processing graph API初始化audio unit

    
    
    // Declare and instantiate an audio processing graph
    AUGraph processingGraph;
    NewAUGraph (&processingGraph);

    // Add an audio unit node to the graph, then instantiate the audio unit
    AUNode ioNode;
    AUGraphAddNode (
        processingGraph,
        &ioUnitDescription,
        &ioNode
    );

    AUGraphOpen (processingGraph); // indirectly performs audio unit instantiation
    // Obtain a reference to the newly-instantiated I/O unit
    AudioUnit ioUnit;
    AUGraphNodeInfo (
        processingGraph,
        ioNode,
        NULL,
        &ioUnit
    );


#####1.4. Audio Units的Scopes,Elements.

如下图,Audio Units由Scopes,Elements组成.

![](./image/20200802-204940)

  * scope: audio unit内部的编程上下文,scope概念有一点抽象,可以这样理解,比如input scope表示里面所有的element都需要一个输入。output scope 表示里面所有的element都会输出到某个地方。至于global scope应该是用来配置一些和输入输出概念无关的属性。

  * element: 当element是input/output scope的一部分时,它类似于物理音频设备中的信号总线.因此这两个术语"element, bus"在audio unit中是一个含义.本文档在强调信号流时使用“bus”，在强调音频单元的特定功能方面时使用“element”，例如I / O unit的输入和输出element.

上图展示了audio unit的一种常见架构，其中输入和输出上的element数量相同。然而,不同的audio unit使用不同架构。例如，mixer unit可能具有多个输入element但是具有单个输出element。

  * global scope:作为整体应用于audio unit并且不与任何特定音频流相关联.它只有一个element。该范围仅适用于个别属性,比如每个片的最大帧数(kAudioUnitProperty_MaximumFramesPerSlice)

input , output scopes直接参与通过audio unit移动一个或多个音频流.audio进入input scope并从output scope离开 。属性或参数可以作为整体应用于input或output scope，例如kAudioUnitProperty_ElementCount.其他属性和参数（如enable I / O属性（kAudioOutputUn itProperty_EnableIO）或volume参数（kMultiChannelMixerParam_Volume））适用于特定scope的element.

>注意: 可以这样理解scope,scope就是音频流动的方位,比如从input scope流动到 output scope, 而element是与硬件挂钩的,比如input element是跟麦克风连接的,音频从input element的input scope流入,从它的output scope流出.

#####1.5. 使用属性配置Audio Units

    
    
    UInt32 busCount = 2;
    OSStatus result = AudioUnitSetProperty (
        mixerUnit,
        kAudioUnitProperty_ElementCount,   // the property key
        kAudioUnitScope_Input,             // the scope to set the property on
        0,                                 // the element to set the property on
        &busCount,                         // the property value
        sizeof (busCount)
    );


  * kAudioOutputUnitProperty_EnableIO

用于在I / O unit上启用或禁用输入或输出。默认情况下，输出已启用但输入已禁用。

  * kAudioUnitProperty_ElementCount

配置mixer unit上的输入elements的数量

  * kAudioUnitProperty_MaximumFramesPerSlice

为了指定音频数据的最大帧数，audio unit应该准备好响应于回调函数调用而产生。对于大多数音频设备，在大多数情况下，您必须按照参考文档中的说明设置此属性。如果不这样做，屏幕锁定时您的音频将停止。

  * kAudioUnitProperty_StreamFormat

指定特定audio unit输入或输出总线的音频流数据格式。

大多数属性只能在audio unit没有初始化时指定,但是某些特定属性可以在audio unit运行时设置,如`kAUVoiceIOProperty_MuteOutput`静音功能.

要测试属性的可用性，访问其值以及监视其值的更改，请使用以下函数：

  * AudioUnitGetPropertyInfo: 测试属性是否可用;如果是，则为其值提供数据大小.
  * AudioUnitGetProperty,AudioUnitSetProperty: 获取,设置一个属性值
  * AudioUnitAddPropertyListener,AudioUnitRemovePropertyListenerWithUserData: 监听,移除监听对于特定属性.

#####1.6. 用户交互

audio unit parameter是用户可以在audio unit运行时提交的参数,通过下面的函数实现.

  * AudioUnitGetParameter
  * AudioUnitSetParameter

#####1.7. I/O Units基本特征

![](./image/20200802-204946)

尽管这两个elements是audio unit的一部分,但你的app应该把它们当做两个独立的实体.例如,你可以根据需求使用`kAudioOutputUnitProperty_EnableIO`属性独立启用或禁用每个element.如上图,Element 1直接与音频输入硬件(麦克风)连接,在蓝色区域输入端的连接范围对于开发者是不透明的,开发者可以在黄色区域,即Element 1输出端获取麦克风采集的音频数据.同样地,Element 0的输出端直接与音频硬件(扬声器)连接,开发者可以将音频数据交给Element 0的输入端,输出端是不透明的.

实际使用过程中,我们经常需要选择使用哪个element,使用时我们常使用它们的编号而不是名称,input element编号为1,output elemnet编号为0.(可以将input首字母I当做1,ouput首字母O当做0来记忆)

如上图所示,每个element都有自己的输入,输入范围.这是为了更加清楚的描述.例如,在一个同时具备输入输出音频的app中,你可以收到音频从inputelement的 output scope, 发送音频给output element的input scope.

#####2. Audio Processing Graphs管理Audio Units

audio processing graph(AUGraph)：基于Core Foundation风格的数据结构，常用来管理audio unit处理链. graph可以利用多个audio unit与回调函数，以用来解决任意音频处理方法。

  * `AUGraph`类型保证了线程安全.例如播放音频时,允许你添加一个均衡器或者在mixer输入端更换回调函数.`AUGraph`提供了音频动态配置在iOS平台.
  * `AUNode`: 代表graph上下文中单个的audio unit.使用graph时,我们常用它作为代理与audio unit交互,而不是直接使用audio unit.

当我们将graph放在一起时,必须使用audio unit的API配置每个audio unit. 而nodes则不能直接配置audio unit.因此,使用graph必须同时使用这两套API.

使用AUNode实例对象(使用node代表一个完整的audio processing subgraph)作为一个复杂graph中的element.在这种情况下, I/O unit结尾的subgraph必须是Generic Output unit(不能连接音频硬件的I/O unit).

步骤

  * 向graph中添加nodes
  * 通过nodes直接配置audio units
  * 互相连接nodes

######2.1. Audio Processing Graph拥有精确的I/O Unit.

无论你正在录制,播放或是同步,每个audio processing graph都有一个I/0 unit.通过`AUGraphStart`与`AUGraphStop`可以开启或停止音频流.通过`AudioOutputUnitStart`与`AudioOutputUnitStop`可以开启或停止I/O unit.通过这种方式，graph的I / O单元负责graph中的音频流。

######2.2. 线程安全

audio processing graph API保证了线程安全.此API中的某些功能会将一个audio unit添加到稍后要执行的更改列表中.指定完整的更改集后，然后要求graph去实现它们。

以下是audio processing graph API支持的一些常见重新配置及其相关功能：

  * 添加,移除audio unit nodes (AUGraphAddNode, AUGraphRemoveNode)
  * 添加移除nodes间的连接(AUGraphConnectNodeInput, AUGraphDisconnectNodeInput)
  * 连接audio unit input bus的回调函数.(AUGraphSetNodeInputCallback) 

![](./image/20200802-204952)

以下是一个重新配置运行中的audio processing graph.例如,构建一个graph包含Multichannel Mixer unit与Remote I/O unit.用于播放合成两种输入源的混音效果.将两个输入源的数据送给Mix的input buses.mixer的输出端连接I/OUnit的output element最终将声音传给硬件.

![](./image/20200802-204959)

在上面这种情况下,用户如果想在任一一路流前插入一个均衡器.可以添加一个iPod EQ unit在从硬件输入端到mixer输入端之前.如图,以下是重新配置的步骤

  * 1.通过调用`AUGraphDisconnectNodeInput`断开mixer unit input 1 的“beats sound”回调。
  * 2.添加一个包含iPod EQ unit的audio unit node到graph中.可以通过配置ASBD以生成iPod EQ unit,然后调用`AUGraphAddNode`将其加入到graph.此时,iPod EQ unit已具有实例化对象但未初始化,已经存在于graph中但未参与音频流.
  * 3.配置,初始化iPod EQ unit. 
    * 调用`AudioUnitGetProperty`从mixer的输入端检索`kAudioUnitProperty_StreamFormat`流格式.
    * 调用两次`AudioUnitSetProperty`,一次设置iPod EQ unit’s input流格式,一次设置输出流格式.
    * 调用`AudioUnitInitialize`以分配内存准备使用.这个函数是线程不安全的.但是，当iPod EQ unit尚未主动参与audio processing graph时，必须在序列时执行它，因为此时没有调用AUGraphUpdate函数。
  * 4.通过调用`AUGraphSetNodeInputCallback`将“beats sound”回调函数添加到iPod EQ input端。

上面1,2,4步使用`AUGraph*`开头的函数,都会被添加到graph的任务执行列表中.通过调用`AUGraphUpdate`执行这些未开始任务.如果成功返回,则graph已经被动态重新配置并且iPod EQ也已经就位正在处理音频数据.

######2.3. 通过graph "pull" 音频流

在audio processing graph可以使用类似生产者消费者模式,消费者在需要更多音频数据时通知生产者。请求音频数据流的方向与音频流提供的方向正好相反.

![](./image/20200802-205006)

对一组音频数据的每个请求称为渲染调用(render call)，也称为拉流(pull)。该图表示拉流为灰色“控制流”箭头。拉流请求的数据更恰当地称为一组音频样本帧(audio sample frames)。反过来，响应拉流而提供的一组音频样本帧被称为slice.提供slice的代码称为渲染回调函数( render callback function).

  * 调用`AUGraphStart`函数.虚拟输出设备调用Remote I/O unit output element的回调函数.该调用请求一片处理过的音频数据帧。
  * Remote I/O unit的回调函数在其输入缓冲区中查找要处理的音频数据。如果有数据等待处理,Remote I/O unit将使用它.否则，如图所示，它将调用应用程序连接到其输入的任何内容的回调函数。Remote I/O unit的输入端连接一个effect unit的输出端.I/O uni从effect unit中拉流,请求一组音频数据帧.
  * effect unit的行为与Remote I/O unit一样.当它需要音频数据时,它从输入连接中获取它.上例中,effect unit从回调函数中获取音频数据
  * effect unit处理回调函数中获取的音频数据. effect unit然后将先前请求的（在步骤2中）处理的数据提供给Remote / O unit
  * Remote I/O unit通过effect unit提供的音频片。然后，Remote I/O unit 将最初请求的处理过的片（在步骤1中）提供给虚拟输出设备。这完成了一个拉动周期。

#####3. 回调函数中将音频传给audio unit

为了从本地文件或内存中将音频传给audio unit的input bus.使用符合`AURenderCallback`回调函数完成.audio unit input需要一些音频数据帧将调用回调函数.

回调函数是唯一可以对音频帧做处理的地方,同时,回调函数必须遵守严格的性能要求.以录制为例,回调函数是按照固定时间间隔进行唤醒调用,如果我们在间隔时间内还没有处理完上一帧数据,那么下一帧数据到达时将产生一个间隙的效果.因此回调函数内应尽量避免加锁，分配内存，访问文件系统或网络连接，或以其他方式在回调函数的主体中执行耗时的任务。

    
    
    static OSStatus MyAURenderCallback (
        void                        *inRefCon,
        AudioUnitRenderActionFlags  *ioActionFlags,
        const AudioTimeStamp        *inTimeStamp,
        UInt32                      inBusNumber,
        UInt32                      inNumberFrames,
        AudioBufferList             *ioData
    ) { /* callback body *


  * inRefCon: 注册回调函数时传递的指针,一般可传本类对象实例,因为回调函数是C语言形式,无法直接访问本类中属性与方法,所以将本例实例化对象传入可以间接调用本类中属性与方法.
  * ioActionFlags: 让回调函数为audio unit提供没有处理音频的提示.例如，如果应用程序是合成吉他并且用户当前没有播放音符，请执行此操作。在要为其输出静默的回调调用期间，在回调体中使用如下语句：`*ioActionFlags |= kAudioUnitRenderAction_OutputIsSilence;`当您希望产生静默时，还必须显式地将ioData参数指向的缓冲区设置为0。
  * inTimeStamp: 表示调用回调函数的时间,可以用作音频同步的时间戳.每次调用回调时, mSampleTime 字段的值都会由 inNumberFrames参数中的数字递增。例如, 如果你的应用是音序器或鼓机, 则可以使用 mSampleTime 值来调度声音。
  * inBusNumber: 调用回调函数的audio unit bus.允许你通过该值在回调函数中进行分支.另外,当audio unit注册回调函数时,可以指定不同的`inRefCon`为每个bus.
  * inNumberFrames: 回调函数中提供的音频帧数.这些帧的数据保存在`ioData`参数中.
  * ioData: 真正的音频数据,如果设置静音,需要将buffer中内容设置为0.

#####4. 音频流格式启用数据流

  * AudioStreamBasicDescription结构 (简称ASBD)
    
    
    struct AudioStreamBasicDescription {
        Float64 mSampleRate;
        UInt32  mFormatID;
        UInt32  mFormatFlags;
        UInt32  mBytesPerPacket;
        UInt32  mFramesPerPacket;
        UInt32  mBytesPerFrame;
        UInt32  mChannelsPerFrame;
        UInt32  mBitsPerChannel;
        UInt32  mReserved;
    };

    typedef struct AudioStreamBasicDescription  AudioStreamBasicDescription;

    size_t bytesPerSample = sizeof (AudioUnitSampleType);

    AudioStreamBasicDescription stereoStreamFormat = {0};
    stereoStreamFormat.mFormatID          = kAudioFormatLinearPCM;
    stereoStreamFormat.mFormatFlags       = kAudioFormatFlagsAudioUnitCanonical;
    stereoStreamFormat.mBytesPerPacket    = bytesPerSample;
    stereoStreamFormat.mBytesPerFrame     = bytesPerSample;
    stereoStreamFormat.mFramesPerPacket   = 1;
    stereoStreamFormat.mBitsPerChannel    = 8 * bytesPerSample;
    stereoStreamFormat.mChannelsPerFrame  = 2;           // 2 indicates stereo
    stereoStreamFormat.mSampleRate        = graphSampleRate;


首先,应该确定采样值的数据类型,上面使用的是`AudioUnitSampleType`,这是大部分audio units推荐的类型,在iOS平台上,被定义为8.24位固定的整型数据.接下来定义ASBD类型变量,初始化为0代表不包含任何数据.(注意,不能跳过该步,否则可能产生一些想不到的问题.).然后就是对ASBD赋值,设备PCM类型表示未压缩的音频数据,

  * mFormatFlags(metaflag): 某些audio unit使用不规则的音频数据格式即不同的音频数据类型，则mFormatFlags字段需要不同的标志集。 例如:3D Mixer unit需要`UInt16`类型数据作为采样值且`mFormatFlags`需要设置为`kAudioFormatFlagsCanonical`.

  * mBytesPerPacket: 每个音频包中有多少字节数

  * mBytesPerFrame: 每一帧中有多少字节

  * mFramesPerPacket: 每个包中有多少帧

  * mBitsPerChannel: 每个声道有多少位

在audio processing graph中你必须在关键点设置音频数据格式.其他点,系统将会设置这个格式.IOS设备上的音频输入和输出硬件具有系统确定的音频流格式,并且格式始终是未压缩的, 采用交错的线性 PCM 格式.

![](./image/20200802-205011)

如上图, 麦克风表示输入的音频硬件。系统确定输入硬件的音频流格式, 并将其施加到 Remote I/O unit’s 的input element的output scope内。同样，扬声器表示输出音频硬件。系统确定输出硬件的流格式，并将其施加到Remote I/O unit’s output element的output scope。

开发者则负责在两个Remote I/O unit’s elements之间建立音频流格式.I/O unit则自动在硬件与自身连接的一端做一个必要的格式转换.

audio unit连接的一个关键功能 (如图1-8 所示) 是, 该连接将音频数据流格式从其源音频单元的输出传播到目标音频单元的输入。这是一个关键点, 因此值得强调的是: 流格式传播是通过音频单元连接的方式进行的, 仅在一个方向上进行--从源音频单元的输出到目标音频单元的输入。

虽然我们通过ASBD灵活的设置音频数据流的属性(如采样率),但是建议还是使用当前设备硬件默认使用值.因为如果保持一致,系统不需要做采样率转换,这可以降低能耗同时提高音频质量.

###二.Audio Unit使用步骤

####1.选择设计模式

  * 仅仅只有一个 I/O unit.
  * audio processing graph中使用单一音频流格式,
  * 要求你去设置流的格式,或则仅仅设置其中一部分.

正确的设置流格式在建立音频流中显得至关重要.这些模式大多依赖于音频流格式从源到目的地的自动传播,它们之间通过audio unit连接.合理利用传播的特性可以减少代码书写量,同时,你必须保证清楚了解每种模式需要如何进行设置.可以在不使用audio processing graph的情况下实现任一一种模式,但是使用它可以减少代码书写量并支持动态重新配置.

#####1.1. I/O Pass Through

I/O Pass Through传递模式在不处理音频的情况下将传入的音频直接发送到输出硬件.

![](./image/20200802-205019)

如上图所示,输入端硬件将它的格式告诉Remote I/O unit的input element.开发者则在I/O unit的输出端指定了流格式,audio unit内部将根据需求自动进行转换,为了避免采样率转换,我们在定义ASBD时最好使用硬件使用的采样率.在上图,我们不必指定I/O unit的输出element,因为数据格式会从输入的element传给输出.同理,传给硬件的流将会根据硬件需要完成一次自动转换.

#####1.2. I/O不带有回调函数

app可以添加一个或多个audio unit在Remote I/O unit’s elements之间.例如使用多通道Mixer unit将传入的麦克风音频定位到立体声域中，或提供输出音量控制,在这中模式下,仍然没有用到回调函数.它简化了模式，但限制了其实用性。如果没有呈现回调函数，就无法直接操作音频。

![](./image/20200802-205025)

在这种模式下,和Pass Through模式相同,你可以配置这两个Remote I/O unit.为了设置多通道Mixer unit,你必须把你的音频流采样率设置给mixer output.mixer的输入端音频流格式会自动设置通过接收从I/O unit输出端传递来的音频流.同理,Output element输入端的格式也将自动设置通过流传递.

>使用此模式必须设置`kAudioUnitProperty_MaximumFramesPerSlice`属性.

#####1.3. I/O带有回调函数

通过注册回调函数在Remote I/O unit的input,output elements之间,开发者可以在音频数据送到输出硬件之前操控它.比如,通过回调函数调节输出音频的音量,还可以添加颤音、环调制、回波或其他效果(Accelerate framework中有相关API).

![](./image/20200802-205036)

如图所示,这个模式使用两个Remote I/O unit, 回调函数被附加在output element的input scope.当output element需要音频数据时,系统会触发回调,紧接着,回调完成后系统将数据传给output element的input scope.

>必须显式启动input在Remote I/O unit.因为它默认是禁止的.

#####1.4. 仅输出的回调函数

该模式通常用于游戏,专业音频app使用.简单的说,该模式在直接连接在Remote I/O unit的output element的input scope.可以利用此模式完成复杂的音频结构,如将几种不同的声音混合在一起,然后通过输出硬件播放他们,如下图.

![](./image/20200802-205043)

如上图所示,注意iPod EQ需要开发者设置Input,output两者的流格式.而 Multichannel Mixer仅仅只需要设置它输出的采样率即可.正如前面说到过,完整的音频流格式信息会在传递的过程中自动赋值.

#####1.5. 其他

audio unit还有两种主要的设计模式.

  * 录制与分析音频: 创建一个带有回调的仅输入的app.回调函数会首先被唤醒,随后将数据传给Remote I/O unit’s input element.但是大多数情况下直接使用audio queue更为简单方便. audio queue使用起来更加灵活,因为它的回调函数不在一个实时的线程上.
  * Generic Output unit: 离线音频处理.不像Remote I/O unit,这个audio unit不连接设备的音频硬件.当你使用它发送音频到app时,它仅仅取决于你的应用程序调用它的渲染方法.

####2.构建App

  * 配置audio session
  * 指定audio unit
  * 创建audio processing graph,然后获取audio unit
  * 配置audio unit
  * 连接audio unit nodes
  * 提供用户界面
  * 初始化然后开启audio processing graph.

#####2.1. 配置Audio Session

audio session是app与硬件交互的中介。设置采样率，

    
    
    NSError *audioSessionError = nil;
    AVAudioSession *mySession = [AVAudioSession sharedInstance];     // 1
    [mySession setPreferredHardwareSampleRate: graphSampleRate       // 2
                                        error: &audioSessionError];
    [mySession setCategory: AVAudioSessionCategoryPlayAndRecord      // 3
                                        error: &audioSessionError];
    [mySession setActive: YES                                        // 4
                   error: &audioSessionError];
    self.graphSampleRate = [mySession currentHardwareSampleRate];    // 5


  * 1.获取audio session单例对象
  * 2.请求当前设备硬件使用的采样率.
  * 3.设置音频分类。`AVAudioSessionCategoryPlayAndRecord`指的是支持音频输入与输出。
  * 4.激活audio session
  * 5.激活audio session后更新采样率。

你还可以配置一些其他功能，如采样率为44.1kHz默认的duration是大概23ms，相当于每次采集1024个采样点。如果你的app要求延迟很低，你可以最低设置0.005ms（相当于256个采样点）

    
    
    self.ioBufferDuration = 0.005;
    [mySession setPreferredIOBufferDuration: ioBufferDuration
                                      error: &audioSessionError];


#####2.2. 指定audio unit

配置完audio session后还无法直接获得audio unit,通过`AudioComponentDescription`赋值可以得到一个指定的audio unit. (1.3中讲到如何赋值)

#####2.3. 构建Audio Processing Graph

  * 实例化`AUGraph`对象（代表 audio processing graph）。
  * 实例化一个或多个`AUNode`对象(每一个代表一个 audio unit in the graph.)。
  * 添加nodes到graphgraph并且实例化
  * 打开graph并且实例化 audio units
  * 获得audio unit引用
    
    
    AUGraph processingGraph;
    NewAUGraph (&processingGraph);
    AUNode ioNode;
    AUNode mixerNode;
    AUGraphAddNode (processingGraph, &ioUnitDesc, &ioNode);
    AUGraphAddNode (processingGraph, &mixerDesc, &mixerNode);


调用`AUGraphAddNode`函数后,graph被实例化并且拥有nodes.为了打开graph并且实例化audio unit需要调用`AUGraphOpen` `AUGraphOpen (processingGraph);`

通过`AUGraphNodeInfo`函数获取对audio unit实例的引用

    
    
    AudioUnit ioUnit;
    AudioUnit mixerUnit;
    AUGraphNodeInfo (processingGraph, ioNode, NULL, &ioUnit);
    AUGraphNodeInfo (processingGraph, mixerNode, NULL, &mixerUnit);


#####2.4.配置audio unit.

iOS中每种audio unit都有其配置的方法,我们应该熟悉一些常用的audio unit配置.

Remote I/O unit, 默认输入禁用,输出可用.如果仅仅使用输入,你必须相应地重新配置 I/O unit.除了Remote I/O与Voice-Processing I/O unit之外所有的audio
unit都必须配置`kAudioUnitProperty_MaximumFramesPerSlice`属性.该属性确保audio unit 准备好响应于回调函数产生足够数量的音频数据帧。

#####2.5. 注册并实现回调函数

对于需要使用回调函数的设计模式,我们必须注册并实现相应的回调函数.此外,还可以通过回调函数拉取音频数据流.

    
    
    AURenderCallbackStruct callbackStruct;
    callbackStruct.inputProc        = &renderCallback;
    callbackStruct.inputProcRefCon  = soundStructArray;

    AudioUnitSetProperty (
        myIOUnit,
        kAudioUnitProperty_SetRenderCallback,
        kAudioUnitScope_Input,
        0,                 // output element
        &callbackStruct,
        sizeof (callbackStruct)
    );

    AURenderCallbackStruct callbackStruct;
    callbackStruct.inputProc        = &renderCallback;
    callbackStruct.inputProcRefCon  = soundStructArray;
    AUGraphSetNodeInputCallback (
        processingGraph,
        myIONode,
        0,                 // output element
        &callbackStruct
    );

    // ... some time later
    Boolean graphUpdated;
    AUGraphUpdate (processingGraph, &graphUpdated);


#####2.6. 连接Audio Unit Nodes

使用`AUGraphConnectNodeInput`与`AUGraphDisconnectNodeInput`函数可以建立,断开Node.它们是线程安全的并且降低代码的开销,因为如果不适用graph我们将必须手动实现.

    
    
    AudioUnitElement mixerUnitOutputBus  = 0;
    AudioUnitElement ioUnitOutputElement = 0;
    AUGraphConnectNodeInput (
        processingGraph,
        mixerNode,           // source node
        mixerUnitOutputBus,  // source node bus
        iONode,              // destination node
        ioUnitOutputElement  // desinatation node element
    );


当然,我们也可以直接使用audio unit的属性建立连接,如下.

    
    
    AudioUnitElement mixerUnitOutputBus  = 0;
    AudioUnitElement ioUnitOutputElement = 0;
    AudioUnitConnection mixerOutToIoUnitIn;
    mixerOutToIoUnitIn.sourceAudioUnit    = mixerUnitInstance;
    mixerOutToIoUnitIn.sourceOutputNumber = mixerUnitOutputBus;
    mixerOutToIoUnitIn.destInputNumber    = ioUnitOutputElement;

    AudioUnitSetProperty (
        ioUnitInstance,                     // connection destination
        kAudioUnitProperty_MakeConnection,  // property key
        kAudioUnitScope_Input,              // destination scope
        ioUnitOutputElement,                // destination element
        &mixerOutToIoUnitIn,                // connection definition
        sizeof (mixerOutToIoUnitIn)
    );


#####2.7. 提供用户界面

一般而言，我们需要提供一个用户界面，让用户微调音频行为。可以定制用户界面以允许用户调整特定的音频单元参数，并在某些特殊情况下调整音频单元属性。

#####2.8. 初始化并开启Audio Processing Graph

调用`AUGraphInitialize`初始化audio processing graph.

  * 为每个audio units单独自动调用AudioUnitInitialize函数来初始化graph所拥有的audio units。 （如果要在不使用graph的情况下构建处理链，则必须依次显式初始化每个audio unit）
  * 验证graph的连接与音频数据流格式
  * 通过不同audio unit的连接传播指定格式的音频流数据。
    
    
    OSStatus result = AUGraphInitialize (processingGraph);
    // Check for error. On successful initialization, start the graph...
    AUGraphStart (processingGraph);
    // Some time later
    AUGraphStop (processingGraph);


####3.故障排除提示

通过函数返回值可以检查调用是否成功.

请留意函数调用之间的依赖,例如,仅仅只能在audio processing graph初始化成功后再开启它.其次,利用`CAShow`函数可以打印当前graph的状态.

确保ASBD初始化赋值为0. `AudioStreamBasicDescription stereoStreamFormat = {0};`.将ASBD的字段初始化为0可确保没有字段包含垃圾数据。(注意:作为类声明中的实例变量 - 其字段会自动初始化为0，无需自己初始化它们)

    
    
    - (void) printASBD: (AudioStreamBasicDescription) asbd {
        char formatIDString[5];
        UInt32 formatID = CFSwapInt32HostToBig (asbd.mFormatID);
        bcopy (&formatID, formatIDString, 4);
        formatIDString[4] = '\0';
        NSLog (@"  Sample Rate:         %10.0f",  asbd.mSampleRate);
        NSLog (@"  Format ID:           %10s",    formatIDString);
        NSLog (@"  Format Flags:        %10X",    asbd.mFormatFlags);
        NSLog (@"  Bytes per Packet:    %10d",    asbd.mBytesPerPacket);
        NSLog (@"  Frames per Packet:   %10d",    asbd.mFramesPerPacket);
        NSLog (@"  Bytes per Frame:     %10d",    asbd.mBytesPerFrame);
        NSLog (@"  Channels per Frame:  %10d",    asbd.mChannelsPerFrame);
        NSLog (@"  Bits per Channel:    %10d",    asbd.mBitsPerChannel);
    }

###三.类型对比

####1. 使用I/O Unit

iOS提供了三种I/O unit.大部分应用使用Remote I/O unit,它连接到输入和输出音频硬件，并提供对各个传入和传出音频样本值的低延迟访问.对于VoIP应用，Voice-Processing I/O unit通过添加声学回声消除和其他功能来扩展远程I / O单元。要将音频发送回应用程序而不是输出音频硬件，请使用通用输出单元。

#####1.1. Remote I/O Unit

Remote I/O unit（子类型kAudioUnitSubType_RemoteIO）连接到设备硬件，用于输入，输出或同时输入和输出。用于播放，录制或低延迟同时输入和输出，不需要回声消除。

设备的音频硬件将其音频流格式强制放置在 Remote I/O unit的外侧。audio unit提供硬件音频格式和应用音频格式之间的格式转换，通过附带的格式转换器audio unit进行格式转换.

input element input scope 从输入硬件获取音频格式, output element output scope从输出硬件获取音频格式,

在input元素的输出范围上设置应用程序格式。 input元素根据需要在其输入和输出范围之间执行格式转换。使用应用程序流格式的硬件采样率。如果输出元素的输入范围由音频单元连接提供，则它从该连接获取其流格式。但是，如果它由渲染回调函数提供，请在其上设置应用程序格式。

<table>
<thead>
<tr>
<th>Audio unit feature</th>
<th>Details</th>
</tr>
</thead>
<tbody>
<tr>
<td>Elements</td>
<td>一个input element,一个output element</td>
</tr>
<tr>
<td>建议使用属性</td>
<td>kAudioFormatLinearPCM,kAudioFormatFlags,AudioUnitSampleType,AudioUnitCanonical</td>
</tr>
<tr>
<td>注意点</td>
<td>Remote I/O unit朝外侧从音频硬件获取其格式,input element从输入端硬件获取,output element 从输出端硬件获取.</td>
</tr>
<tr>
<td>属性注意</td>
<td>不需要设置kAudioUnitProperty_MaximumFramesPerSlice</td>
</tr>
</tbody>
</table>

#####1.2.Voice-Processing I/O Unit

Voice-Processing I/O unit（子类型kAudioUnitSubType_VoiceProcessingIO）具有 Remote I/O unit 的特性，并且添加了回声抑制。它还增加了自动增益校正，语音处理质量调整和静音功能。这是用于VoIP（互联网协议语音）应用程序的正确I/O unit。

#####1.3. Generic Output Unit

在将audio processing graph的输出发送到应用程序而不是输出音频硬件时，请使用此类型为kAudioUnitSubType_GenericOutput的音频单元。通常使用Generic Output Unit进行离线音频处理。与其他I / O units一样，Generic Output unit包含格式转换器。因此可以在audio processing graph中使用的流格式与所需格式之间执行格式转换。

####2. Using Mixer Units

iOS提供两种mixer units。在大多数情况下，您应该使用Multichannel Mixer unit，它可以为任意数量的单声道或立体声流提供混音。如果您需要3D Mixer unit的功能，请使用OpenAL。OpenAL建立在3D混音器单元之上，提供与简单API相同的性能，非常适合游戏应用程序开发。

默认情况下，kAudioUnitProperty_MaximumFramesPerSlice属性设置为1024，当屏幕锁定并且显示器休眠时，这是不够的。如果您的应用在屏幕锁定时播放音频，则必须增加此属性的值，除非音频输入处于活动状态。做如下：

  * 如果音频输入处于活动状态，则无需为`kAudioUnitProperty_MaximumFramesPerSlice`属性设置值。
  * 如果音频输入未激活，请将此属性设置为值4096。

#####2.1.Multichannel Mixer Unit

Multichannel Mixer unit（子类型`kAudioUnitSubType_MultiChannelMixer`）可接收任意数量的单声道或立体声流，并将它们组合成单个立体声输出。它控制每个输入和输出的音频增益，并允许您分别打开或关闭每个输入。从iOS4.0开始，多声道混音器支持每个输入的立体声声像。

<table>
<thead>
<tr>
<th>Audio unit feature</th>
<th>Details</th>
</tr>
</thead>
<tbody>
<tr>
<td>Elements</td>
<td>一个或多个(单声道或多声道)input element,一个多声道output element</td>
</tr>
<tr>
<td>建议使用属性</td>
<td>kAudioFormatLinearPCM,kAudioFormatFlags,AudioUnitSampleType,AudioUnitCanonical</td>
</tr>
<tr>
<td>注意点</td>
<td>如果输入由audio unit连接则从该连接获取其流格式。如果输入由回调函数提供在bus上设置完整的流格式,使用与回调提供的数据相同的流格式。在output scope，仅需要设置采样率。</td>
</tr>
<tr>
<td>属性</td>
<td>kAudioUnitProperty_MeteringMode</td>
</tr>
</tbody>
</table>

注意点: iPod EQ单元提供一组预定义的色调均衡曲线作为出厂预设。通过访问音频单元的`kAudioUnitProperty_FactoryPresets`属性获取可用EQ设置数组。使用它作为kAudioUnitProperty_PresentPreset属性的值来应用设置。

#####2.2. 3D Mixer Unit

3D Mixer unit: 控制每个输入的立体声声像，播放速度和增益，并控制其他特征，例如与收听者的视距,输出具有音频增益控制。通常，如果需要3D Mixer unit的功能，最佳选择是使用OpenAL.

<table>
<thead>
<tr>
<th>Audio unit feature</th>
<th>Details</th>
</tr>
</thead>
<tbody>
<tr>
<td>Elements</td>
<td>一个或多个单声道input element,一个多声道output element</td>
</tr>
<tr>
<td>建议使用属性</td>
<td>UInt16,kAudioFormatFlagsAudioUnitCanonical</td>
</tr>
<tr>
<td>注意点</td>
<td>如果输入由audio unit连接则从该连接获取其流格式。如果输入由回调函数提供在bus上设置完整的流格式,使用与回调提供的数据相同的流格式。在output scope，仅需要设置采样率。</td>
</tr>
</tbody>
</table>

注意点: iPod EQ单元提供一组预定义的色调均衡曲线作为出厂预设。通过访问音频单元的kAudioUnitProperty_FactoryPresets属性获取可用EQ设置数组。使用它作为kAudioUnitProperty_PresentPreset属性的值来应用设置。

####3.Using Effect Units

iPod EQ unit （子类型kAudioUnitSubType_AUiPodEQ）是iOS4中提供的唯一效果单元。这与内置iPod应用程序使用的均衡器相同。要查看该音频设备的iPod应用程序用户界面，请转至设置> iPod> EQ。该音频单元提供一组预设均衡曲线，如低音增强器，流行音乐和口语。

<table>
<thead>
<tr>
<th>Audio unit feature</th>
<th>Details</th>
</tr>
</thead>
<tbody>
<tr>
<td>Elements</td>
<td>一个input element,一个output element (该element可以是单声道或双声道)</td>
</tr>
<tr>
<td>建议使用属性</td>
<td>kAudioFormatLinearPCM,AudioUnitSampleType,kAudioFormatFlagsAudioUnitCanonical</td>
</tr>
<tr>
<td>注意点</td>
<td>如果输入由audio unit连接则从该连接获取其流格式。如果输入由回调函数提供在bus上设置完整的流格式,使用与回调提供的数据相同的流格式。在output scope，设置用于输入的相同完整流格式。</td>
</tr>
<tr>
<td>Properties</td>
<td>kAudioUnitProperty_FactoryPresets,kAudioUnitProperty_PresentPreset</td>
</tr>
</tbody>
</table>

注意点: iPod EQ单元提供一组预定义的色调均衡曲线作为出厂预设。通过访问音频单元的`kAudioUnitProperty_FactoryPresets`属性获取可用EQ设置数组。使用它作为`kAudioUnitProperty_PresentPreset`属性的值来应用设置。

默认情况下，`kAudioUnitProperty_MaximumFramesPerSlice`属性设置为1024，当屏幕锁定并且显示器休眠时，这是不够的。如果您的应用在屏幕锁定时播放音频，则必须增加此属性的值，除非音频输入处于活动状态。做如下：

  * 如果音频输入处于活动状态，则无需为`kAudioUnitProperty_MaximumFramesPerSlice`属性设置值。
  * 如果音频输入未激活，请将此属性设置为值4096。

####4.Audio Units 标识符键

此表提供了访问每个iOS audio unit的动态链接库所需的标识符键以及其简要说明。
<table>
<thead>
<tr>
<th>名称与描述</th>
<th>键名称</th>
<th>相应编解码器</th>
</tr>
</thead>
<tbody>
<tr>
<td>Converter unit (提供音频格式转换在线性PCM与其他压缩格式)</td>
<td>kAudioUnitType_FormatConverter,kAudioUnitSubType_AUConverter,kAudioUnitManufacturer_Apple</td>
<td>aufc,conv,appl</td>
</tr>
<tr>
<td>iPod Equalizer unit(提供iPod均衡器的功能)</td>
<td>kAudioUnitType_Effect</td>
<td>kAudioUnitSubType_AUiPodEQ</td>
</tr>
<tr>
<td>3D Mixer unit (支持混合多个音频流，输出平移，采样率转换等)</td>
<td>kAudioUnitType_Mixer,kAudioUnitSubType_AU3DMixerEmbedded,kAudioUnitManufacturer_Apple</td>
<td>aumx,3dem,appl</td>
</tr>
<tr>
<td>Multichannel Mixer unit (支持将多个音频流混合到单个流中)</td>
<td>kAudioUnitType_Mixer,kAudioUnitSubType_MultiChannelMixer,kAudioUnitManufacturer_Apple</td>
<td>aumx,mcmx,appl</td>
</tr>
<tr>
<td>Generic Output unit (支持转换为线性PCM格式和从线性PCM格式转换;可用于启动和停止graph)</td>
<td>kAudioUnitType_Output,kAudioUnitSubType_GenericOutput,kAudioUnitManufacturer_Apple</td>
<td>auou,genr,appl</td>
</tr>
<tr>
<td>Remote I/O unit(连接到设备硬件以进行输入，输出或同时输入和输出)</td>
<td>kAudioUnitType_Output,kAudioUnitSubType_RemoteIO,kAudioUnitManufacturer_Apple</td>
<td>auou,rioc,appl</td>
</tr>
<tr>
<td>Voice Processing I/O unit(具有I / O单元的特性，并为双向通信增加了回声抑制功能)</td>
<td>kAudioUnitType_Output,kAudioUnitSubType_VoiceProcessingIO,kAudioUnitManufacturer_Apple</td>
<td>auou,vpio,appl</td>
</tr>
</tbody>
</table>

#####[Apple官方文档](https://developer.apple.com/library/archive/documentation/MusicAudio/Conceptual/AudioUnitHostingGuide_iOS/Introduction/Introduction.html#//apple_ref/doc/uid/TP40009492-CH1-SW1)


