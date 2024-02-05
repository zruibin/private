
<!--BEGIN_DATA
{
    "create_date": "2022-03-02 22:00", 
    "modify_date": "2022-03-02 22:00", 
    "is_top": "0", 
    "summary": "WebRTC代码目录与类说明", 
    "tags": "WebRTC", 
    "file_name": "WebRTC代码目录与类说明.md"
}
END_DATA-->

#### <p>原文出处：<a href='https://blog.csdn.net/wanghorse' target='blank'>WebRTC代码目录与类说明</a></p>

## 代码目录结构

```c
├── ./base  //基础平台库，包括线程、锁、socket等
├── ./build //编译脚本，gyp
├── ./common_audio  //基础公共的音频处理
│   ├── ./common_audio/include  //就一个类型转换头文件
│   ├── ./common_audio/resampler    //音频重采样代码
│   ├── ./common_audio/signal_processing    //音频信号处理代码，和硬件平台有关，有汇编代码
│   └── ./common_audio/vad  //vad代码
├── ./common_video  //基础的公共视频处理，如I420桢处理、scaler、plane
├── ./examples //例子
├── ./libjingle //libjingle
├── ./modules
│   ├── ./modules/audio_coding
│   │   ├── ./modules/audio_coding/codecs //音频codec处理，统一封装公共接口和各类不同的codec的具体处理，cng,g711,g722等
│   │   ├── ./modules/audio_coding/main //音频codec处理模块代码
│   │   │   ├── ./modules/audio_coding/main/acm2    //音频处理模块的主要代码
│   │   └── ./modules/audio_coding/neteq    //neteq代码
│   │       ├── ./modules/audio_coding/neteq/interface
│   │       ├── ./modules/audio_coding/neteq/mock
│   │       ├── ./modules/audio_coding/neteq/test
│   │       └── ./modules/audio_coding/neteq/tools
│   ├── ./modules/audio_conference_mixer    //音频合成代码
│   │   ├── ./modules/audio_conference_mixer/interface
│   │   └── ./modules/audio_conference_mixer/source
│   ├── ./modules/audio_device  //audio设备处理代码，采集和放音，android，ios，linux，mac，win
│   │   ├── ./modules/audio_device/main //AudioDeviceModule处理代码
│   ├── ./modules/audio_processing //音频前后端处理，aec，aecm,agc,beamformer,ns,transient
│   ├── ./modules/bitrate_controller    //码率模块控制代码
│   ├── ./modules/desktop_capture //桌面抓拍处理代码和各平台处理代码,mac,win,x11
│   ├── ./modules/interface
│   ├── ./modules/media_file    //播放录制文件模块代码，支持avi
│   ├── ./modules/pacing    //码率探测代码
│   ├── ./modules/remote_bitrate_estimator  //远端码率计算
│   ├── ./modules/rtp_rtcp //rtp、rtcp的处理代码，封装解封装，各种codec的不同处理、fec
│   ├── ./modules/utility
│   ├── ./modules/video_capture //视频摄像头采集代码，android、ios、linux、mac、win
│   ├── ./modules/video_coding //视频codec处理代码，i420、vp8、vp9
│   │   ├── ./modules/video_coding/codecs
│   │   ├── ./modules/video_coding/main //VideoCodingModule处理代码
│   ├── ./modules/video_processing //视频前后处理，brighten，color enhancement，deflickering，spatial resampler等
│   │   └── ./modules/video_processing/main //VideoProcessingModule
│   └── ./modules/video_render  //视频渲染代码，android，ios、linux、mac、windows、opengles
├── ./p2p //nat穿越代码，turn/stun等，服务器和客户端
│   ├── ./p2p/base
│   └── ./p2p/client
├── ./sound //未知
├── ./system_wrappers //系统api封装
├── ./test
├── ./tools //音视频测试工具代码
├── ./video //未知
├── ./video_engine  //视频引擎代码，视频的处理流程
└── ./voice_engine  //音频引擎代码，音频处理流程
```

## 目录结构分析

**api**

> WebRTC 接口层。包括 DataChannel, MediaStream, SDP相关的接口。各浏览器都是通过该接口层调用的 WebRTC。

**call**

> 存放的是 WebRTC “呼叫（Call）” 相关逻辑层的代码。

**audio**

> 存放音频网络逻辑层相关的代码。音频数据逻辑上的发送，接收等代码。

**video**

> 存放视频逻辑层及视频引擎层的相关的代码。视频数据逻辑上的发送，接收等代码。
>> 视频引擎层就是指如何控制视频采集，处理和编解码操作的逻辑。

**voice_engine**

> 存放音频引擎代码。主要是控制音频的采集，处理，编解码的操作。
>> 这个目录后面可能也会被拿掉。
 
**sdk**

> 存放了 Android 和 IOS 层代码。如视频的采集，渲染代码都在这里。

**pc**

> 存放一些业务逻辑层的代码。如 channel, session等。

**common_audio**

> 存放一些音频的基本算法。包括环形队列，博利叶算法，滤波器等。

**common_video**

> 存放了视频算法相关的常用工具，如libyuv, sps/pps分析器，I420缓冲器等。

**modules**

> 这个目录是 WebRTC 代码中最重要的一个目录。里面包括了音视频的采集，处理，编解码器，混音等。
>> 视频的渲染部分已经从这里删除了。因为没有浏览器需要用到这里的渲染代码。如果使用Native API 做二次开发，需要自己写视频渲染相关的代码。
 
**modules 目录下还包括以下几个子目录**：

```c
audio_coding : 音频编解码相关代码。
audio_conference_mixer : 会议混音相关代码。
audio_device : 音频采集与音频播放相关代码。
audio_mixer : 混音相关代码，这部分是后加的。
audio_processing : 音频前后处理的相关代码。
bitrate_controller : 码率控制相关代码。
congestion_controller : 流控相关的代码。
desktop_capture : 桌面采集相关的代码。
media_file : 播放媒体文件相关的代码。
pacing : 码率探测相关的代码。
remote_bitrate_estimator : 远端码率估算相关的代码。
rtp_rtcp : rtp/rtcp协议相关代码。
video_capture : 视频采集相关的代码。
video_coding : 视频编解码相关的代码。
video_processing : 视频前后处理相关的代码。
```

**media**

> 存放媒体相关的代码。

**p2p**

> p2p相关的代码。

**rtc_base**

> 存放了一些基础代码。如线程，事件，socket等相关的代码。

**rtc_tools**

> 存放了一些工具代码。如视频帧比较，I420转RGB，视频帧分析。

**stats**

> 存放各种数据统计相关的类。

**libjingle**

> 网络库。

**system_wrapper**

> 与操作系统相关的代码，如 CPU特性，原子操作，读写锁，时钟等。

## VoiceEngine和VideoEngine主要的控制类说明

**1. VideoEngineImpl**

> VideoEngine对外提供的集成接口实现类， 其继承了VideoEngine对外提供的所有接口实现类，包括`ViEBaseImpl/ViECaptureImpl/ViEFileImpl/ViEImageProcessImpl/ViENetworkImpl/ViERTP_RTCPImpl/ViEExternalCodecImpl/VideoEngine`

**2. ViEBaseImpl**

> VideoEngine对外提供的操作类，基本都有此类提供，如创建删除通道、开始停止发送、开始停止接受等

**3. ViEChannel**

> VideoEngine的channel类，一个视频收发通道一个VieChannel对象， 管理channel的信息，管理ModuleRtpRtcpImpl，VideoCodingModuleImpl负责channel处理流程控制，如开始发送、接受等；音频通道的链接

**4. ViEEncoder**

> 类似ViEChannel，在某些应用场景下可以替换VieChannel；但只负责发送Channel

**5. ViERenderImpl**

> VideoEngine的Render流程控制类，控制Render的流程，如启动、暂停，处理回调数据，管理具体的Render操作类； 注册进VieChannel

**6. ViECaptureImpl**

> VideoEngine中Capture的流程控制类，控制Capture流程，管理具体的Capture操作类，和VIEEncoder关联起来

**7. VoiceEngineImpl**

> VoiceEngine对外提供的集成接口类，其集成了VoiceEngine对外提供的所有接口实现类，包括`VoEAudioProcessingImpl/VoECodecImpl/VoEDtmfImpl/VoEExternalMediaImpl/VoEFileImpl/VoEHardwareImpl/VoENetEqStatsImpl/VoENetworkImpl/VoERTP_RTCPImpl/VoEVideoSyncImpl/VoEVolumeControlImpl/VoEBaseImpl`

**8. VoEBaseImpl**

> VoiceEngine对外提供的基本操作类，包括创建删除通道，开始停止发送，开始停止接受等； 管理放音设备和采集设备其继承AudioTransport类，还需处理抓取的音频（送至channel中），和需要放音的音频（从channel中取）

**9. Channel**

> VoiceEngine的channel类，一个音频收发通道一个Channel对象，管理channel的信息，管理AudioCodingModule，ModuleRtpRtcpImpl，AudioProcessing等控制channel的处理流程

## rtp_rtcp模块分析

**1. 对外提供的主要流程接口**
     
```c
收包的调用接口RtpReceiverImpl::IncomingRtpPacket
发包的调用接口ModuleRtpRtcpImpl::SendOutgoingData
收包处理之后的回调接口RtpData
```

**2. 主要处理类**

```c
ModuleRtpRtcpImpl， 控制模块，是个Module，自己能够独立处理
RtpPacketizer/RtpPacketizerH264/RtpPacketizerVp8 具体格式的解桢处理类
RtpDepacketizer/RtpDepacketizerH264/RtpDepacketizerVp8/ 具体格式的解析RTP包头的处理类
RtpReceiverImpl 接受RTP包的处理和接口类
RTPReceiverStrategy/RTPReceiverVideo/RTPReceiverAudio 具体的处理接受RTP包的类，Audio包含TelephoneEven的处理
RTPSender/RTPSenderAudio/RTPSenderVideo 发送RTP包类，被ModuleRtpRtcpImpl管理和调用，其中还需要解桢，管理和组FEC
FecReceiverImpl，FEC收包处理函数，被VIE调用
```

**3. 主要功能**：

```c
解析RTP包头，解桢分包，FEC解析和封装；负责调用发包模块
不包含功能：RTP的组桢功能，乱序，buffer，纠错
```

## video_coding模块分析

**1. 对外提供的主要接口**

```c
VideoCodingModuleImpl::IncomingPacket， 收包处理接口，在RTP解析流程之后调用
VideoCodingModuleImpl::Decode， 处理解码的接口
VCMReceiveCallback 解码完成之后的回调接口
VideoCodingModuleImpl::AddVideoFrame 发送frame接口，原始的视频数据I420
VCMPacketizationCallback 编码完成之后提供给外面的回调接口
```

**2. 主要的处理类**

```c
VideoCodingModuleImpl， module处理和控制类，管理和维护VideoSender和VideoReceiver
VideoReceiver， Video收包和解码的处理，调用DecodedImageCallback进行进行解码
VCMReceiver， video收包的处理，管理VCMJitterBuffer
VCMJitterBuffer， video的buffer，组桢，乱序，抖动等处理
VideoSender，视频发送的具体的类， 管理VCMGenericEncoder接口类
VCMGenericEncoder， 具体的管理编码类，维护VideoEncoder
VCMEncodedFrameCallback，实现Encode模块提供的回调接口，用于编码完成之后的处理
VP8Encoder/VP8Decoder/...， 具体的编解码封转类
```

**3. 主要功能**

```c
处理jitterbuffer，组桢、抖动、乱序等处理； 处理编码解码；管理video的编码解码流程
```

## video_render模块分析

**1. 对外接口**

```c
VideoRender 创建控制等接口
VideoRenderCallback 推送render数据接口
```

**2. 主要类**

```c
ModuleVideoRenderImpl 控制类
IncomingVideoStream 用于接收Render数据
VideoRenderLinuxImpl/VideoX11Channel Linux下的render封装类
VideoRenderIosImpl/VideoRenderCallback iOS下的render封装类，
VideoRenderWindowsImpl/D3D9Channel windows下的render封装，使用d3d9
VideoRenderAndroid/AndroidNativeOpenGl2Channel android下的render，使用opengl进行Render，调用还需要JAVA来调用
AndroidSurfaceViewChannel android下的render，java成进行Render
```

**3. 主要功能**

对于各个系统平台的render实现和封装

## video_capture模块分析

**1. 对外接口**

```c
VideoCaptureModule     控制接口
VideoCaptureDataCallback Vie中的ViECapturer继承，用于响应抓包数据
```

**2. 主要类**

```c
VideoCaptureImpl， 继承VideoCaptureModule，用于控制和抽象具体的capture执行接口
VideoCaptureAndroid， 继承VideoCaptureImpl，android的capture类， 抓取在JAVA层中完成，并回调VideoCaptureDataCallback 
VideoCaptureIos，继承VideoCaptureImpl，iOS的capture类
VideoCaptureModuleV4L2，继承VideoCaptureImpl，Linux的capture类，增加了一个线程，用于select句柄
VideoCaptureMacQTKit，继承VideoCaptureImpl，mac的capture类， 具体由mac的VideoCaptureMacQTKitObjC实现
VideoCaptureDS， 继承VideoCaptureImpl，windows的capture类，有Dshow实现
VideoCaptureMF， 继承VideoCaptureImpl，windows的capture类，实现Media Foundation API
```

**3. 主要功能**

对各个系统Capture驱动的封装

## audio_device模块分析

**1. 对外接口**

```c
AudioDeviceModule， 采音放音接口，音量控制，静音控制等
```

**2. 主要类**

```c
AudioDeviceModuleImpl， 对外提供的主要实现类，硬件实现主要调用AudioDeviceGeneric，管理AudioDeviceGeneric，AudioDeviceBuffer和AudioDeviceUtility
AudioDeviceGeneric， 硬件接口类，采音和放音、音量控制等等， 被不同的系统实现集成
AudioDeviceLinuxALSA, 继承AudioDeviceGeneric类， 主要调用AudioMixerManagerLinuxALSA（linux下alsa声卡驱动封装类）
AudioDeviceLinuxPulse, 继承AudioDeviceGeneric类， 主要调用AudioMixerManagerLinuxPulse（linux下pulse声卡驱动封装类）
AudioDeviceMac, 继承AudioDeviceGeneric类， 主要调用AudioMixerManagerMac（max下声卡驱动封装类）
AudioDeviceWindowsCore/AudioDeviceWindowsWave, 继承AudioDeviceGeneric， windows下的两套实现类
AudioDeviceIOS, 继承AudioDeviceGeneric类， iOS下的实现类   
OpenSlesInput, OpenSlesOutput， Android下的opensles的实现封装类
AudioRecordJni, AudioTrackJni， android下的JNI实现类，放音和采集动作有JAVA层实现
AudioDeviceTemplate， 模板类，继承AudioDeviceGeneric类，用于采集和放音分开的类
AudioDeviceBuffer， 保存和Device的交互的音频数据
```

**3. 主要功能**

对各个系统平台的声卡驱动的封装和处理接口

## audio_coding模块分析和audio_conference_mixer模块分析

**audio_coding**

**1. 主要接口**

```c
AudioCodingModuleImpl::RegisterReceiveCodec 初始化Codec
AudioCodingModuleImpl::IncomingPacket 收包
AudioCodingModuleImpl::PlayoutData10Ms neteq处理，并解码，返回原始数据
AudioCodingModuleImpl::Add10MsData 存储数据
AudioCodingModuleImpl::Process 编码，并调用channel回调
```

**2. 主要功能类**

```c
AudioDecoder/AudioEncoder audio编解码接口类
NetEqImpl neteq的主要接口和处理类，负责neteq的相关功能流程，以及调用AudioDecoder和AudioEnder相关编解码接口
```

**3. 主要功能**

neteq， 处理语音编解码，管理编解码库

**AudioProcessingImpl**

**1. 主要接口**

```c
AudioConferenceMixerImpl::Process 主要处理类，遍历所有channel，回调出来原始数据，进行混音
AudioConferenceMixerImpl::SetMixabilityStatus 加入到混音器
```

**2. 主要功能类**

```c
AudioConferenceMixerImpl 混音的控制类
```

**3. 主要功能**

混音





















