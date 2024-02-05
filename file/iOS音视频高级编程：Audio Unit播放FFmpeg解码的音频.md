 
<!--BEGIN_DATA
{
    "create_date": "2020-06-02 23:42", 
    "modify_date": "2020-06-02 23:42", 
    "is_top": "0", 
    "summary": "iOS音视频高级编程：Audio Unit播放FFmpeg解码的音频", 
    "tags": "iOS、C/C++、WebRTC", 
    "file_name": "iOS音视频高级编程：Audio Unit播放FFmpeg解码的音频.md"
}
END_DATA-->

####<p>原文出处：<a href='https://blog.csdn.net/chmel_foxmail/article/details/70879817' target='blank'>iOS音视频高级编程：Audio Unit播放FFmpeg解码的音频</a></p>

###目录


文档描述了iOS播放经FFmpeg解码的音频数据的编程步骤，具体基于Audio Toolbox框架的Audio Session和AudioUnit框架提供的接口实现。在iOS 7及以上平台Audio Session已标识为废弃，改用AVAudioSession实现即可，编程逻辑基本保持一致。同时，尝试不解码的情况下，直接播放AAC流，这是个人理解的『硬解』AAC。  
所有测试数据均来自iPhone 6、iPhone 6p真机。

目录：  
|- FFmpeg解码音频在iOS播放的编程流程  
|-- AudioSessionInitialize初始化音频会话  
|-- 配置Audio Session  
|--- 配置属性  
|---- 音频回放  
|---- 配置硬件I/O缓冲区  
|--- 配置属性变化监听器  
|---- 音频输出变化  
|---- 输出音量变化  
|--- 激活音频会话  
|-- 配置Audio Unit  
|--- 描述输出单元  
|--- 获取组件  
|--- 核对输出流格式  
|--- 设置音频渲染回调函数  
|--- 初始化Audio Unit  
|-- 音频渲染回调函数传入未播放的音频数据  
|-- 释放资源  
|-- FFmpeg解码流程  
|-- 音频重采样  
|-- Accelerate框架在重采样过程的应用  
|- 程序运行存在的问题  
|-- MP3播放正常  
|-- 播放MP4中音频存在失真现象  
|- 最小实现代码  
|- Audio Unit直接播放AAC流的尝试  
|- 致谢  
|- 参考

####1、FFmpeg解码音频在iOS播放的编程流程

播放音频的开发方式和渲染视频略有区别，音频略微被动，系统主动回调我们指定的函数，在回调函数中，我们向系统传递过来的指针拷贝将要播放的音频数据，而视频的播放是我们主动往屏幕的帧缓冲区刷像素数据。那么，iOS上播放FFmpeg解码后的音频数据，比如AAC，需要如下编程步骤：

  1. AudioSessionInitialize初始化一个iOS应用的音频会话对象
  2. 配置Audio Session 
    * 配置属性 
      * kAudioSessionProperty_AudioCategory指定为音频播放
      * kAudioSessionProperty_PreferredHardwareIOBufferDuration配置更小的I/O迟延，通常情况不需要设置。
    * 配置属性变化监听器（观察者模式的应用），非最小功能要求，可不实现。
      * kAudioSessionProperty_AudioRouteChange
      * kAudioSessionProperty_CurrentHardwareOutputVolume
    * AudioSessionSetActive激活音频会话
  3. 配置Audio Unit 
    * 描述输出单元AudioComponentDescription
    * 获取组件AudioComponent
    * 核对输出流格式AudioStreamBasicDescription
    * 设置音频渲染回调结构体AURenderCallbackStruct并指定回调函数，这是真正向音频设备提供PCM数据的地方
    * 初始化Audio Unit
  4. 音频渲染回调函数传入未播放的音频数据
  5. 释放资源
  6. FFmpeg解码流程
  7. 音频重采样

下面详细描述每个步骤的操作。

#####1.1、AudioSessionInitialize初始化音频会话

    
    
    AudioSessionInitialize(NULL,
            kCFRunLoopCommonModes,
            sessionInterruptionListener,
            (__bridge void *) (self)

AudioSessionInitialize指定音频回调函数在特定的RunLoop及相应的RunLoop模式下运行及传递给中断函数的用户自定义值。回调函数的说明如下。

> The interruption listener callback function. The application’s audio session object invokes the callback when the session is interrupted and (if the application is still running) when the interruption ends. Can be NULL. See AudioSessionInterruptionListener.

在调用其他音频会话相关服务前，必须先调用此函数。

> Your application must call this function before making any other Audio Session Services calls. You may activate and deactivate your audio session as needed (see AudioSessionSetActive), but should initialize it only once.

当应用进入前后台、解锁屏等事件出现时触发回调函数AudioSessionInterruptionListener，签名如下：

    
    
    // Invoked when an audio interruption in iOS begins or ends.
    typedef void (*AudioSessionInterruptionListener)( void *inClientData, UInt32 inInterruptionState );

  * 参数inClientData在AudioSessionInitialize中指定。
  * 参数inInterruptionState表明中断的状态。

初始化完成后，可通过AudioSessionGetProperty查询音频会话相关的信息，比如`kAudioSessionProperty_AudioRouteDescription`（iOS5以前使用`kAudioSessionProperty_AudioRoute`）获取音频输入输出信息，比如输入为麦克风、转出为扬声器。示例代码如下。

    
    
    UInt32 propertySize = sizeof(CFStringRef);
    CFStringRef route;
    AudioSessionGetProperty(kAudioSessionProperty_AudioRoute,
            &propertySize,
            &route);
    NSString *audioRoute = CFBridgingRelease(route);

`kAudioSessionProperty_AudioRouteDescription`比`kAudioSessionProperty_AudioRoute`输出更多信息，如下所示。

1、 kAudioSessionProperty_AudioRoute的输出


    AudioRoute: Speaker

2、 kAudioSessionProperty_AudioRouteDescription的输出


    AudioRoute: 
    {
    "RouteDetailedDescription_Inputs" =     (
                {
            "RouteDetailedDescription_ChannelDescriptions" =             (
                                {
                    "ChannelDescription_Name" = "iPhone Microphone";
                }
            );
            "RouteDetailedDescription_DataSources" =             (
                                {
                    DataSourceID = 1835216945;
                    DataSourceName = Bottom;
                    MicrophoneOrientation = 1651799149;
                    MicrophonePolarPattern = 1869442665;
                    MicrophonePolarPatterns =                     (
                        1869442665
                    );
                    MicrophoneRegion = 1819244402;
                },
                                {
                    DataSourceID = 1835216946;
                    DataSourceName = Front;
                    MicrophoneOrientation = 1718775412;
                    MicrophonePolarPattern = 1668441188;
                    MicrophonePolarPatterns =                     (
                        1869442665,
                        1668441188
                    );
                    MicrophoneRegion = 1970303090;
                },
                                {
                    DataSourceID = 1835216947;
                    DataSourceName = Back;
                    MicrophoneOrientation = 1650549611;
                    MicrophonePolarPattern = 1869442665;
                    MicrophonePolarPatterns =                     (
                        1869442665,
                        1935827812
                    );
                    MicrophoneRegion = 1970303090;
                }
            );
            "RouteDetailedDescription_HiddenDataSources" =             (
                                {
                    DataSourceID = 1634495520;
                    DataSourceName = All;
                }
            );
            "RouteDetailedDescription_ID" = 344;
            "RouteDetailedDescription_IsHeadphones" = 0;
            "RouteDetailedDescription_Name" = "iPhone Microphone";
            "RouteDetailedDescription_NumberOfChannels" = 1;
            "RouteDetailedDescription_PortType" = MicrophoneBuiltIn;
            "RouteDetailedDescription_SelectedDataSource" = 1835216946;
            "RouteDetailedDescription_UID" = "Built-In Microphone";
        }
    );
    "RouteDetailedDescription_Outputs" =     (
                {
            "RouteDetailedDescription_ChannelDescriptions" =             (
                                {
                    "ChannelDescription_Label" = "-1";
                    "ChannelDescription_Name" = Speaker;
                }
            );
            "RouteDetailedDescription_ID" = 345;
            "RouteDetailedDescription_IsHeadphones" = 0;
            "RouteDetailedDescription_Name" = Speaker;
            "RouteDetailedDescription_NumberOfChannels" = 1;
            "RouteDetailedDescription_PortType" = Speaker;
            "RouteDetailedDescription_UID" = Speaker;
        }
    );
    }
        

#####1.2、配置Audio Session

音频会话的配置由属性及属性值变化监听器组成，监听器可按需实现。

######1.2.1、配置属性

音频会话为必备步骤，I/O缓冲区可使用默认值。

#######1.2.1.1、音频回放

播放音乐的场景需设置`kAudioSessionProperty_AudioCategory`为`kAudioSessionCategory_MediaPlayback`，其他值可表示音频处理、录音等，所有枚举值如下所示。

    
    
    /*!
     @enum           AudioSession audio categories states
     @abstract       These are used with as values for the kAudioSessionProperty_AudioCategory property
     to indicate the audio category of the AudioSession.
     @constant       kAudioSessionCategory_AmbientSound
     Use this category for background sounds such as rain, car engine noise, etc.
     Mixes with other music.
     @constant       kAudioSessionCategory_SoloAmbientSound
     Use this category for background sounds.  Other music will stop playing.
     @constant       kAudioSessionCategory_MediaPlayback
     Use this category for music tracks.
     @constant       kAudioSessionCategory_RecordAudio
     Use this category when recording audio.
     @constant       kAudioSessionCategory_PlayAndRecord
     Use this category when recording and playing back audio.
     @constant       kAudioSessionCategory_AudioProcessing
     Use this category when using a hardware codec or signal processor while
     not playing or recording audio.
     */
    enum {
        kAudioSessionCategory_AmbientSound               = 'ambi',
        kAudioSessionCategory_SoloAmbientSound           = 'solo',
        kAudioSessionCategory_MediaPlayback              = 'medi',
        kAudioSessionCategory_RecordAudio                = 'reca',
        kAudioSessionCategory_PlayAndRecord              = 'plar',
        kAudioSessionCategory_AudioProcessing            = 'proc'
    };

当你遇到错误提示265: Unknown property ID:'medi'或类似问题时，意味着属性设置函数的第一个参数被错误的写成相应的值，如下所示。

    
    
    AudioSessionSetProperty(kAudioSessionCategory_MediaPlayback,
            sizeof(sessionCategory), 
            &sessionCategory)

#######1.2.1.2、配置硬件I/O缓冲区

当需要更小的I/O缓冲区时设置本属性，指定更小的缓冲区可让音频延时变小，但是占用更多CPU资源。然而，设置的值可能不被系统所采用，可由`kAudioSessionProperty_CurrentHardwareIOBufferDuration`查询设置后的实际值。文档说明如下。

> Your preferred hardware I/O buffer duration in seconds. Do not set this property unless you require lower I/O latency than is provided by default.
>
> A read/write Float32 value.
>
> The actual I/O buffer duration may be different from the value that you request, and can be obtained from the `kAudioSessionProperty_CurrentHardwareIOBufferDuration` property.
>
> Set the buffer size, this will affect the number of samples that get rendered every time the audio callback is fired   
> A small number will get you lower latency audio, but will make your processor work harder

参考代码：

    
    
    Float32 preferredBufferSize = 0.0232;
    AudioSessionSetProperty(kAudioSessionProperty_PreferredHardwareIOBufferDuration,
            sizeof(preferredBufferSize),
            &preferredBufferSize);

0.0232表示23毫秒。采样率44100、1024个采样点，那么，一包的时长就是

    
    
    1024 / 44100 = 0.0232

@[暴走大牙](http://www.jianshu.com/users/1ec036eb8418)在实践中发现，在Android上采集音频，3x23毫秒效果更佳。  
@二流提供了另一种理解：

    
    
    44100 / 1024 = 1秒 43包 
    1 / 43 = 0.023

######1.2.2、配置属性变化监听器

#######1.2.2.1、音频输出变化

注册`kAudioSessionProperty_AudioRouteChange`可让我们知道音频输出变化，比如插入耳机，文档说明如下。

> A CFDictionaryRef object containing the reason the audio route changed along with details on the previous and current audio route.
>
> The dictionary contains the keys and corresponding values described in Audio Route Change Dictionary Keys.
>
> The kAudioSessionProperty_AudioRouteChange dictionary is available to your app only by way of the AudioSessionPropertyListener callback function.

示例代码：

    
    
    AudioSessionAddPropertyListener(kAudioSessionProperty_AudioRouteChange,
            sessionPropertyListener,
            (__bridge void *) (self)

########1.2.2.2、输出音量变化

注册`kAudioSessionProperty_CurrentHardwareOutputVolume`可让我们知道输出音量出现变化，比如用户增大了音量，文档
说明如下。

> Indicates the current audio output volume as Float32 value between 0.0 and 1.0. Read-only. This value is available to your app by way of a property listener callback function. See AudioSessionAddPropertyListener.

示例代码：

    
    
    AudioSessionAddPropertyListener(kAudioSessionProperty_CurrentHardwareOutputVolume,
            sessionPropertyListener,
            (__bridge void *) (self))

#######1.2.3、激活音频会话

传递true则AudioSessionSetActive激活音频会话，反之则禁用它，可进行多次启、禁用操作。

> Activating your audio session may interrupt audio sessions belonging to other applications running in the background, depending on categories and priorities. Deactivating your audio session allows other, interrupted audio sessions to resume.
>
> When another active audio session does not allow mixing, attempting to activate your audio session may fail.
>
> When active is true this call may fail if the currently active AudioSession has a higher priority.

    
    
    AudioSessionSetActive(YES)

#####1.3、配置Audio Unit

Audio Unit才是真正进行音频输出的执行者。对于播放流媒体中的音频，StackOverflow有人说Audio Queue播放效果更好。

######1.3.1、描述输出单元

AudioComponentDescription用于描述音频组件的唯一性和标识符，拥有这些字段：

  * componentType: OSType，用唯一的4字节码标识了音频组件的通用类型。
  * componentSubType: OSType，表示此音频组件描述的具体类型。
  * componentManufacturer: OSType，厂家标识符，只能设置为苹果公司。
  * componentFlags: OSType，必须设置为0，除非已知请求的具体值。
  * componentFlagsMask: OSType，必须设置为0，除非已知请求的具体值。

componentType可设置为如下值：

>   * kAudioUnitType_Output  
> An output unit provides input, output, or both input and output simultaneously. It can be used as the head of an audio unit processing graph.
>
>   * kAudioUnitType_MusicDevice  
> An instrument unit can be used as a software musical instrument, such as a sampler or synthesizer. It responds to MIDI (Musical Instrument Digital Interface) control signals and can create notes.
>
>   * kAudioUnitType_MusicEffect  
> An effect unit that can respond to MIDI control messages, typically through a mapping of MIDI messages to parameters of the audio unit’s DSP algorithm.
>
>   * kAudioUnitType_FormatConverter  
> A format converter unit can transform audio formats, such as performing sample rate conversion. A format converter is also appropriate for deferred rendering and for effects such as varispeed. A format converter unit can ask for as much or as little audio input as it needs to produce a given output, while still completing its rendering within the time represented by the output buffer. For effect-like format converters, such as pitch shifters, it is common to provide both a realtime and an offline version. OS X, for example, includes Time-Pitch and Varispeed audio units in both realtime and offline versions.
>
>   * kAudioUnitType_Effect  
> An effect unit repeatedly processes a number of audio input samples to produce the same number of audio output samples. Most commonly, an effect unit has a single input and a single output. Some effects take side-chain inputs as well. Effect units can be run offline, such as to process a file without playing it, but are expected to run in realtime.
>
>   * kAudioUnitType_Mixer  
> A mixer unit takes a number of input channels and mixes them to provide one or more output channels. For example, the kAudioUnitSubType_StereoMixer audio unit in OS X takes multiple mono or stereo inputs and produce a single stereo output.
>
>   * kAudioUnitType_Panner  
> A panner unit is a specialized effect unit that distributes one or more channels in a single input to one or more channels in a single output. Panner units must support a set of standard audio unit parameters that specify panning coordinates.
>
>   * kAudioUnitType_OfflineEffect  
> An offline effect unit provides digital signal processing of a sort that cannot proceed in realtime. For example, level normalization requires examination of an entire sound, beginning to end, before the normalization factor can be calculated. As such, offline effect units also have a notion of a priming stage that can be performed before the actual rendering/processing phase is executed.
>
>   * kAudioUnitType_Generator  
> A generator unit provides audio output but has no audio input. This audio unit type is appropriate for a tone generator. Unlike an instrument unit, a generator unit does not have a control input.

componentSubType可设置为如下值：

>   * kAudioUnitSubType_GenericOutput  
> An audio unit that responds to start/stop calls and provides basic services for converting to and from linear PCM formats.
>
>   * kAudioUnitSubType_RemoteIO  
>An audio unit that interfaces to the audio inputs and outputs of iPhone OS devices. Bus 0 provides output to hardware and bus 1 accepts input from hardware. Called an I/O audio unit or sometimes a Remote I/O audio unit.
>
>
>   * kAudioUnitSubType_VoiceProcessingIO  
> An audio unit that interfaces to the audio inputs and outputs of iPhone OS devices and provides voice processing features. Bus 0 provides output to hardware and bus 1 accepts input from hardware. See the Voice-Processing I/O Audio Unit Properties enumeration for the identifiers for this audio unit’s properties.

示例代码如下。

    
    
    AudioComponentDescription description = {0};
    description.componentType = kAudioUnitType_Output;
    description.componentSubType = kAudioUnitSubType_RemoteIO;
    description.componentManufacturer = kAudioUnitManufacturer_Apple;

######1.3.2、获取组件

现在，由前面配置的AudioComponentDescription查找系统的音频处理插件链表是否存在对应的结果，存在才可处理我们将要提供的音频数据。在可处理的情况下返回AudioComponent，根据此音频组件创建一个音频组件实例。

    
    
    AudioComponent component = AudioComponentFindNext(NULL, &description);
    AudioComponentInstanceNew(component, &_audioUnit);

AudioComponentFindNext的功能描述如下：

> Finds the next component that matches a specified AudioComponentDescription structure after a specified audio component.

AudioComponentInstanceNew函数得到的就是AudioUnit实例，因为AudioUnit是AudioComponentInstance的别名。

    
    
    typedef AudioComponentInstance AudioUnit;

######1.3.3、核对输出流格式

这里主要为了设置AudioStreamBasicDescription成当前设置的采样率。不同于查询Audio Session的RouteDescription，此处k`AudioUnitScope_Input`表示传递给Audio Unit的数据。

> kAudioUnitScope_Input  
> The context for audio data coming into an audio unit

    
    
    AudioStreamBasicDescription _outputFormat;
    UInt32 size = sizeof(AudioStreamBasicDescription);
    AudioUnitGetProperty(_audioUnit,
            kAudioUnitProperty_StreamFormat,
            kAudioUnitScope_Input,
            0,
            &_outputFormat,
            &size);
    _outputFormat.mSampleRate = _samplingRate;
    AudioUnitSetProperty(_audioUnit,
            kAudioUnitProperty_StreamFormat,
            kAudioUnitScope_Input,
            0,
            &_outputFormat,
            size);
    UInt32 _numBytesPerSample = _outputFormat.mBitsPerChannel / 8;
    UInt32 _numOutputChannels = _outputFormat.mChannelsPerFrame;

通过AudioUnitGetProperty获取到的StreamFormat数据如下所示：

    
    
    (AudioStreamBasicDescription) $0 = {
      mSampleRate = 0
      mFormatID = 1819304813
      mFormatFlags = 41
      mBytesPerPacket = 4
      mFramesPerPacket = 1
      mBytesPerFrame = 4
      mChannelsPerFrame = 2
      mBitsPerChannel = 32
      mReserved = 0
    }

其中，采样率为0。对于正常速度播放的音频而言，我们需要将其修改为手机支持的采样率。文档指出，当播放的音频格式在iOS支持的音频格式列表中，可设置为0，具体我没验证过。现在的影音文件，多数采用48000采样率，在此需要进行重采样，后续文档再详细介绍。  
另外，1819304813表示kAudioFormatLinearPCM。

`_samplingRate`为设备当前的采样率，查询代码如下：

    
    
    AudioSessionGetProperty(kAudioSessionProperty_CurrentHardwareSampleRate,
            &size,
            &_samplingRate)

有关AudioStreamBasicDescription各字段的说明如下：

> An audio data format specification for a stream of audio.  
>
>Fields  
>
>mSampleRate  
The number of frames per second of the data in the stream, when the stream is played at normal speed. For compressed formats, this field indicates the number of frames per second of equivalent decompressed data.
>
> The mSampleRate field must be nonzero, except when this structure is used in a listing of supported formats (see “kAudioStreamAnyRate”).
>
> mFormatID  
>An identifier specifying the general audio data format in the stream. See “Audio Data Format Identifiers”. This value must be nonzero.
>
> mFormatFlags  
>Format-specific flags to specify details of the format. Set to 0 to indicate no format flags. See “Audio Data Format Identifiers” for the flags that apply to each format.
>
> mBytesPerPacket  
>The number of bytes in a packet of audio data. To indicate variable packet size, set this field to 0. For a format that uses variable packet size, specify the size of each packet using an AudioStreamPacketDescription structure.
>
> mFramesPerPacket  
>The number of frames in a packet of audio data. For uncompressed audio, the value is 1. For variable bit-rate formats, the value is a larger fixed number, such as 1024 for AAC. For formats with a variable number of frames per packet, such as Ogg Vorbis, set this field to 0.
>
> mBytesPerFrame  
>The number of bytes from the start of one frame to the start of the next frame in an audio buffer. Set this field to 0 for compressed formats.
>
> For an audio buffer containing interleaved data for n channels, with each sample of type AudioSampleType, calculate the value for this field as follows:
>  
>     mBytesPerFrame = n * sizeof (AudioSampleType);
>
> For an audio buffer containing noninterleaved (monophonic) data, also using AudioSampleType samples, calculate the value for this field as follows:
>  
>     mBytesPerFrame = sizeof (AudioSampleType);
>
> mChannelsPerFrame  
>The number of channels in each frame of audio data. This value must be nonzero.
>
> mBitsPerChannel  
>The number of bits for one audio sample. For example, for linear PCM audio using the kAudioFormatFlagsCanonical format flags, calculate the value for this field as follows:
>  
>     mBitsPerChannel = 8 * sizeof (AudioSampleType);
>
> Set this field to 0 for compressed formats.
>
> mReserved  
>Pads the structure out to force an even 8-byte alignment. Must be set to 0.
>
> You can configure an audio stream basic description (ASBD) to specify a linear PCM format or a constant bit rate (CBR) format that has channels of equal size. For variable bit rate (VBR) audio, and for CBR audio where the channels have unequal sizes, each packet must additionally be described by an AudioStreamPacketDescription structure.
>
> A field value of 0 indicates that the value is either unknown or not applicable to the format.
>
> Always initialize the fields of a new audio stream basic description structure to zero, as shown here:
>  
>  
>     AudioStreamBasicDescription myAudioDataFormat = {0};
>
> To determine the duration represented by one packet, use the mSampleRate field with the mFramesPerPacket field, as follows:
>  
>  
>     duration = (1 / mSampleRate) * mFramesPerPacket
>
> In Core Audio, the following definitions apply:
>
>   * An audio stream is a continuous series of data that represents a sound, such as a song.
>   * A channel is a discrete track of monophonic audio. A monophonic stream has one channel; a stereo stream has two channels.
>   * A sample is single numerical value for a single audio channel in an audio stream.
>   * A frame is a collection of time-coincident samples. For instance, a linear PCM stereo sound file has two samples per frame, one for the left channel and one for the right channel.
>   * A packet is a collection of one or more contiguous frames. A packet defines the smallest meaningful set of frames for a given audio data format, and is the smallest data unit for which time can be measured. In linear PCM audio, a packet holds a single frame. In compressed formats, it typically holds more; in some formats, the number of frames per packet varies.
>   * The sample rate for a stream is the number of frames per second of uncompressed (or, for compressed formats, the equivalent in decompressed) audio.

######1.3.4、设置音频渲染回调函数

    
    
    AURenderCallbackStruct callbackStruct;
    callbackStruct.inputProc = renderCallback;
    callbackStruct.inputProcRefCon = (__bridge void *) (self);
    AudioUnitSetProperty(_audioUnit,
            kAudioUnitProperty_SetRenderCallback,
            kAudioUnitScope_Input,
            0,
            &callbackStruct,
            sizeof(callbackStruct));

######1.3.5、初始化Audio Unit

所有设置操作结束后，初始化Audio Unit开始音频播放。

    
    
    AudioUnitInitialize(_audioUnit);
    AudioOutputUnitStart(_audioUnit);

#####1.4、音频渲染回调函数传入未播放的音频数据

回调函数会传递音频缓冲区列表AudioBufferList给我们，在此先对此进行重置操作。

    
    
    for (int iBuffer = 0; iBuffer < ioData->mNumberBuffers; ++iBuffer) {
        memset(ioData->mBuffers[iBuffer].mData, 
            0, 
            ioData->mBuffers[iBuffer].mDataByteSize);
    }

然后逐个传递已解码的音频包给回调函数的AudioBufferList参数。

#####1.5、释放资源

结束音频输出时，要先停止再逆初始化，流程如下所示。

    
    
    AudioOutputUnitStop(_audioUnit)
    AudioUnitUninitialize(_audioUnit);
    AudioComponentInstanceDispose(_audioUnit);
    AudioSessionSetActive(NO);
    AudioSessionRemovePropertyListenerWithUserData(kAudioSessionProperty_AudioRouteChange,
                    sessionPropertyListener,
                    (__bridge void *) (self));
    AudioSessionRemovePropertyListenerWithUserData(kAudioSessionProperty_CurrentHardwareOutputVolume,
                    sessionPropertyListener,
                    (__bridge void *) (self));

#####1.6、FFmpeg解码流程

以FFmpeg3.0为例，每次循环读取音频包数据，解码时可能有剩余数据，故需要判断是否解码完整，否则继续解码当前音频包的剩余数据，接着进行音频重采样，示例代码如下：

    
    
    av_register_all();
    printf("%s Using FFmpeg: %s\n", __FUNCTION__, av_version_info());
    AVFormatContext *context = avformat_alloc_context();
    int ret;
    NSString *path = [[NSBundle mainBundle] pathForResource:@"Forrest_Gump_IMAX.mp4" ofType:nil];
    const char *url = path.UTF8String;
    avformat_open_input(&context, url, NULL, NULL);
    avformat_find_stream_info(context, NULL);
    av_dump_format(context, 0, url, 0);
    int audioStreamIndex = -1;
    for (int i = 0; i < context->nb_streams; ++i) {
        if (AVMEDIA_TYPE_AUDIO == context->streams[i]->codec->codec_type) {
            audioStreamIndex = i;
            break;
        }
    }
    if (-1 == audioStreamIndex) {
        printf("%s audio stream not found.\n", __FUNCTION__);
        exit(-1);
    }
    AVStream *audioStream = context->streams[audioStreamIndex];
    AVCodec *audioCodec = avcodec_find_decoder(context->audio_codec_id);
    avcodec_open2(audioStream->codec, audioCodec, NULL);
    AVPacket packet, *pkt = &packet;
    AVFrame *audioFrame = av_frame_alloc();
    int gotFrame = 0;
    while (0 == av_read_frame(context, pkt)) {
        if (audioStreamIndex == pkt->stream_index) {
            // 循环解码，直到当前包无剩余数据
                    avcodec_decode_audio4(audioStream->codec, audioFrame, &gotFrame, pkt);
                    if (gotFrame)
                            // 进行音频重采样
        }
        av_packet_unref(pkt);
    }

#####1.7、音频重采样

根据之前看过的雷霄骅博士的博客，目前，FFmpeg 3.0 avcodec_decode_audio4函数解码出来的音频数据是单精度浮点类型，值范围为[0, 1.0]。iOS可播放Float类型的音频数据，范围和FFmpeg解码出来的PCM不同，故需要进行重采样。

    
    
    const int bufSize = av_samples_get_buffer_size(NULL,
            _audioCodecCtx->channels,
            _audioFrame->nb_samples,
            _audioCodecCtx->sample_fmt,
            1);
    const NSUInteger sizeOfS16 = 2;
    const NSUInteger numChannels = _audioCodecCtx->channels;
    int numFrames = bufSize / (sizeOfS16 * numChannels);
    SInt16 *s16p = (SInt16 *) _audioFrame->data[0];
    if (_swrContext) {
        if (!_swrBuffer || _swrBufferSize < (bufSize * 2)) {
            _swrBufferSize = bufSize * 2;
            _swrBuffer = realloc(_swrBuffer, _swrBufferSize);
        }
        Byte *outbuf[2] = {_swrBuffer, 0};
        numFrames = swr_convert(_swrContext,
            outbuf,
            numFrames * 2,
            (const uint8_t **) _audioFrame->data,
            numFrames);
        if (numFrames < 0) {
            NSLog(@"fail resample audio");
            return nil;
        }
        s16p = _swrBuffer;
    }
    const NSUInteger numElements = numFrames * numChannels;
    NSMutableData *data = [NSMutableData dataWithLength:numElements * sizeof(float)];
    vDSP_vflt16(s16p, 1, data.mutableBytes, 1, numElements);
    float scale = 1.0 / (float) INT16_MAX;
    vDSP_vsmul(data.mutableBytes, 1, &scale, data.mutableBytes, 1, numElements);

`_swrContext`为重采样上下文，将给定的音频源的声道、声道布局和采样率转换为输出设备的声道、声道布局和采样率，具体转换由`swr_convert`函数完成。然而，上述代码存在重采样错误，主要体现中播放flt16类型的音频时，计算出来的numFrames值比`AVFrame.nb_samples`值大，比如，对于AAC编码的立体声音频，numFrames等于2048，而nb_samples只有1024，这导致播放时出现失真现象，修复代码在文档后续部分给出。`_swrContext`的初始化代码如下所示。

    
    
    _swrContext = swr_alloc_set_opts(NULL,
            av_get_default_channel_layout(hw.numOutputChannels),
            AV_SAMPLE_FMT_S16,
            hw.samplingRate,
            av_get_default_channel_layout(audioCodecCtx->channels),
            audioCodecCtx->sample_fmt,
            audioCodecCtx->sample_rate,
            0,
            NULL);

根据FFmpeg注释，下面代码完成了平面浮点数采样格式至交错的16位带符号整数、从48kHz至44.1kHz的降采样与5.1声道至立体声的降混合的转换，当然最终转换得调用`swr_convert`函数。

    
    
    SwrContext *swr = swr_alloc();
    av_opt_set_channel_layout(swr, "in_channel_layout",  AV_CH_LAYOUT_5POINT1, 0);
    av_opt_set_channel_layout(swr, "out_channel_layout", AV_CH_LAYOUT_STEREO,  0);
    av_opt_set_int(swr, "in_sample_rate",     48000,                0);
    av_opt_set_int(swr, "out_sample_rate",    44100,                0);
    av_opt_set_sample_fmt(swr, "in_sample_fmt",  AV_SAMPLE_FMT_FLTP, 0);
    av_opt_set_sample_fmt(swr, "out_sample_fmt", AV_SAMPLE_FMT_S16,  0);

等效代码为

    
    
    SwrContext *swr = swr_alloc_set_opts(NULL,  // we're allocating a new context
            AV_CH_LAYOUT_STEREO,  // out_ch_layout
            AV_SAMPLE_FMT_S16,    // out_sample_fmt
            44100,                // out_sample_rate
            AV_CH_LAYOUT_5POINT1, // in_ch_layout
            AV_SAMPLE_FMT_FLTP,   // in_sample_fmt
            48000,                // in_sample_rate
            0,                    // log_offset
            NULL);                // log_ctx

#####1.8、Accelerate框架在重采样过程的应用

音频重采样后，还调用了几个`vDSP_`函数，如下所示。这些函数都是Accelerate框架的成员，它提供了音频、信号处理、图像处理等应用需要的函数。

    
    
    vDSP_vflt16(s16p, 1, data.mutableBytes, 1, numElements);
    float scale = 1.0 / (float) INT16_MAX;
    vDSP_vsmul(data.mutableBytes, 1, &scale, data.mutableBytes, 1, numElements);

`vDSP_vflt16`将非交错的16位带符号整数（non-interleaved 16-bit signed integers）转换成单精度浮点数。为什么是16位带符号整数？原因是，这取决于AudioStreamBasicDescription.mBitsPerChannel字段的值。当AudioStreamBasicDescription.mBitsPerChannel为16时，则调用`vDSP_vflt16`。当AudioStreamBasicDescription.mBitsPerChannel为32时，则调用`vDSP_vflt32`。

####2、程序运行存在的问题

基于前面的实现，进行一些测试。

#####2.1、MP3（s16p）播放正常

播放正常，信息如下。

    
    
    Input #0, mp3, from '1A Hero s Sacrifice.mp3':
      Metadata:
        major_brand     : mp42
        minor_version   : 0
        compatible_brands: isommp42
        encoder         : Lavf55.19.100
      Duration: 00:07:05.09, start: 0.025057, bitrate: 128 kb/s
        Stream #0:0: Audio: mp3, 44100 Hz, stereo, s16p, 128 kb/s

执行日志如下。

    
    
    AudioRoute: Speaker
    We've got 1 output channels
    Current sampling rate: 44100.000000
    Current output volume: 0.687500
    Current output bytes per sample: 4
    Current output num channels: 2
    audio codec smr: 44100 fmt: 6 chn: 2 tb: 0.000000 resample
    audio device smr: 44100 fmt: 4 chn: 2

#####2.2、播放MP4（fltp）中音频存在失真现象

简单起见，只播放MP4中音频，有明显失真现象，文件信息如下。

    
    
    Input #0, mov,mp4,m4a,3gp,3g2,mj2, from 'Forrest_Gump_IMAX.mp4':
      Metadata:
        major_brand     : isom
        minor_version   : 512
        compatible_brands: isomiso2avc1mp41
        encoder         : Lavf56.19.100
      Duration: 00:00:31.21, start: 0.036281, bitrate: 878 kb/s
        Stream #0:0(und): Video: h264 (High) (avc1 / 0x31637661), yuv420p, 640x352, 748 kb/s, 23.98 fps, 23.98 tbr, 24k tbn, 47.95 tbc (default)
        Metadata:
          handler_name    : VideoHandler
        Stream #0:1(und): Audio: aac (LC) (mp4a / 0x6134706D), 44100 Hz, stereo, fltp, 128 kb/s (default)
        Metadata:
          handler_name    : SoundHandler

执行日志。

    
    
    AudioRoute: Speaker
    We've got 1 output channels
    Current sampling rate: 44100.000000
    Current output volume: 0.687500
    Current output bytes per sample: 4
    Current output num channels: 2
    audio codec smr: 44100 fmt: 8 chn: 2 tb: 0.000023 resample
    audio device smr: 44100 fmt: 4 chn: 2

不同于播放MP3文件的是，音频轨的编码信息。设备相关信息并不发生变化。下面做些小测试，失真问题基本不会由它们引起，保险起见，还是实测为准：

  * 替换kCFRunLoopDefaultMode为kCFRunLoopCommonModes，依然使用主运行循环，不进行任何屏幕操作，失真现象一样。
  * 非主运行循环与kCFRunLoopCommonModes。失真现象一样

排除CPU资源占用问题后，那么就剩一种情况了，重采样时计算有误。下面修复`handAudio`方法，此时播放fltp数据类型的音频不再失真，同时播放S16P类型的MP3也无失真现象。

    
    
    numFrames = swr_convert(_swrContext,
            outbuf,
            _audioFrame->nb_samples * 2,
            (const uint8_t **)_audioFrame->data,
            _audioFrame->nb_samples);

####3、最小实现代码

前面分析了每个代码段的作用，现给出最小实现参考代码。

    
    
    #pragma mark - Audio Session Callback
    void inInterruptionListener(void *inClientData, UInt32 inInterruptionState) {
        switch (inInterruptionState) {
            case kAudioSessionBeginInterruption:
                printf("interruption state kAudioSessionBeginInterruption\n");
                break;
            case kAudioSessionEndInterruption:
                printf("interruption state kAudioSessionEndInterruption\n");
                break;
            default:
                printf("Unkown interruption state\n");
                break;
        }
    }
    #pragma mark - Audio Session
    - (void)setupAudioSession {
        OSStatus status = AudioSessionInitialize(NULL, 
            kCFRunLoopDefaultMode, 
            inInterruptionListener, 
            (__bridge void *)self);
        if (kAudioSessionNoError != status) {
            printf("AudioSessionInitialize failed with %ld", status);
        }
        UInt32 sessionCategory = kAudioSessionCategory_MediaPlayback;
        status = AudioSessionSetProperty(kAudioSessionProperty_AudioCategory, 
            sizeof(sessionCategory), 
            &sessionCategory);
        AudioSessionSetActive(true);
    }
    #pragma mark - Audio Unit Callback
    OSStatus renderCallback(void *inRefCon,
                            AudioUnitRenderActionFlags *ioActionFlags,
                            const AudioTimeStamp *inTimeStamp,
                            UInt32 inBusNumber,
                            UInt32 inNumberFrames,
                            AudioBufferList *ioData) {
        // 静音
        for (int iBuffer = 0; iBuffer < ioData->mNumberBuffers; ++iBuffer) {
            memset(ioData->mBuffers[iBuffer].mData, 0, ioData->mBuffers[iBuffer].mDataByteSize);
        }
        // 下面填充实际的音频数据
        // ...
        return kAudioSessionNoError;
    }
    #pragma mark - Audio Unit
    - (void)setupAudioUnit {
        AudioComponentDescription audioComponentDescription = {
            .componentType = kAudioUnitType_Output,
            .componentSubType = kAudioUnitSubType_RemoteIO,
            .componentManufacturer = kAudioUnitManufacturer_Apple, 
            0};
        AudioComponent audioComponent = AudioComponentFindNext(NULL, 
            &audioComponentDescription);
        if (!audioComponent) {
            printf("audioComponent == NULL\n");
        }
        AudioComponentInstance componentInstance = NULL;
        AudioComponentInstanceNew(audioComponent, &componentInstance);
        AudioStreamBasicDescription outputFormat;
        UInt32 size = sizeof(AudioStreamBasicDescription);
        AudioUnitGetProperty(componentInstance, 
            kAudioUnitProperty_StreamFormat, 
            kAudioUnitScope_Input, 
            0, 
            &outputFormat, 
            &size);
        outputFormat.mSampleRate = 441000;
        AudioUnitSetProperty(componentInstance, 
            kAudioUnitProperty_StreamFormat, 
            kAudioUnitScope_Input, 
            0, 
            &outputFormat, size);
        AURenderCallbackStruct renderCallbackRef = {
            .inputProc = renderCallback,
            .inputProcRefCon = (__bridge void *) (self)};
        AudioUnitSetProperty(componentInstance, 
            kAudioUnitProperty_SetRenderCallback, 
            kAudioUnitScope_Input, 
            0, 
            &renderCallbackRef, 
            sizeof(renderCallbackRef));
        OSStatus status = AudioUnitInitialize(componentInstance);
        NSLog(@"status = %ld", status);
        AudioOutputUnitStart(componentInstance);
    }

####4、Audio Unit直接播放AAC流的尝试

Audio Unit和Audio Queue都可以直接播放本地AAC文件。现在尝试在不解码成PCM的情况下，播放直播中的AAC流数据。

    
    
    AudioStreamBasicDescription streamFormat = {
        .mSampleRate        = 441000,
        .mFormatID            = kAudioFormatMPEG4AAC,
        .mFormatFlags        = kAudioFormatFlagIsFloat,
        .mFramesPerPacket    = 1,
        .mChannelsPerFrame    = 2,
        .mBitsPerChannel    = 16,
        .mBytesPerPacket    = 2 * sizeof (Float32),
        .mBytesPerFrame        = 2 * sizeof (Float32)};

AudioUnitInitialize初始化时返回错误码0x666D743F（1718449215），表示上述参数有误。

####致谢

因本人对音频了解较少，关于音频的S16P与FLT16转换问题，感谢同事强总提供SDL只能播放S16P的提示。另外，也是自己粗心，去年草草地过了一遍SDL1.2源码，应该是当时没看懂，总之现在基本没印象了。  
感谢@[暴走大牙](http://www.jianshu.com/users/1ec036eb8418)、二流，两位热情解说了0.0232这个数值。

####参考

  * [KxMovie](https://github.com/kolyvan/kxmovie) 感谢Kolyvan在2012年开源了此项目，它影响了后来的开源项目，如ijkplayer，同样我在去年盛夏刚接触音视频开发时也学习了该项目


