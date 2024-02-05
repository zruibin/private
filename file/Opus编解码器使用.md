
<!--BEGIN_DATA
{
    "create_date": "2021-03-03 14:20", 
    "modify_date": "2021-03-03 14:20", 
    "is_top": "0", 
    "summary": "Opus编解码器使用", 
    "tags": "音视频", 
    "file_name": "Opus编解码器使用.md"
}
END_DATA-->

#### <p>原文出处：<a href='https://juejin.cn/post/6844903998831460360' target='blank'>Opus编解码器使用</a></p>

[Opus官方编码器实现](https://github.com/xiph/opus),包括:

  * Opus Encoder
  * Opus Decoder
  * Repacketizer
  * Opus Multistream API
  * Opus library information functions
  * Opus Custom 编解码示例文件:[github.com/xiph/opus/b…](https://github.com/xiph/opus/blob/master/src/opus_demo.c) 文档地址:[www.opus-codec.org/docs/opus_a…](https://www.opus-codec.org/docs/opus_api-1.1.3/index.html)

## 编码器

### 类型定义

typedef struct OpusEncoder OpusEncoder //Opus encoder 状态.

### 函数

| Function | 说明 |
| ---- | ---- |
| `int opus_encoder_get_size(int channels)` | 获得 OpusEncoder结构的大小 -|
| `OpusEncoder * opus_encoder_create(opus_int32 Fs, int channels, int application, int *error)` | 分配和初始化 encoder状态. |
| `int opus_encoder_init(OpusEncoder *st, opus_int32 Fs, int channels, int application)` | 初始化一个以前分配的编码器状态。所指向的内存圣必须至少是opus_encoder_get_size()返回的大小. |
| `opus_int32 opus_encode(OpusEncoder *st, const opus_int16 *pcm, int frame_size, unsigned char *data, opus_int32 max_data_bytes)` | 对一个Opus帧进行编码|
| `opus_int32 opus_encode_float(OpusEncoder *st, const float *pcm, int frame_size, unsigned char *data, opus_int32 max_data_bytes)` | 根据浮点输入对一个Opus帧进行编码 |
| `void opus_encoder_destroy(OpusEncoder *st)` | 释放一个根据opus_encoder_create()已分配的OpusEncoder对象 |
| `int opus_encoder_ctl(OpusEncoder *st, int request,...)` | 向一个Opus编码器执行一个 CTL 函数. |

### 详细描述

本节描述了用于编码Opus的过程和函数。既然Opus是一个有状态的编解码器，编码过程始于创建一个编码器状态，用以下方法做到：

```cpp
int error;
OpusEncoder *enc;
enc = opus_encoder_create(Fs, channels, application, &error);
```

从这一点上, enc可以用于编码音频流。一个编码器状态在同一时间不得用于多于一个音频流。同样,编码器状态不能对于每帧重新初始化。当`opus_encoder_create()`为状态分配内存时，它也可以初始化预分配的内存：

```cpp
int size;
int error;
OpusEncoder *enc;
size = opus_encoder_get_size(channels);
enc = malloc(size);
error = opus_encoder_init(enc, Fs, channels, application);
```

`opus_encoder_get_size()`返回编码器状态要求的大小。注意,这段代码的未来版本可能改变大小,所以没有assuptions应该对它做出。编码器状态在内存中总是连续,复制它只要一个浅拷贝就足够了。使用opus_encoder_ctl()接口可以改变一些编码器的参数设置。所有这些参数都已有缺省值，所以只在必要的情况下改变它们。最常见的参数设置修改是：

```cpp
opus_encoder_ctl(enc, OPUS_SET_BITRATE(bitrate));
opus_encoder_ctl(enc, OPUS_SET_COMPLEXITY(complexity));
opus_encoder_ctl(enc, OPUS_SET_SIGNAL(signal_type));
```

在这里：

  * bitrate（比特率）的单位是比特/秒(b/s)
  * complexity（复杂性）是一个值从1到10,1最低，10最高，值越大越复杂
  * `signal_type`（信号的类型）包括OPUS_AUTO(缺省), `OPUS_SIGNAL_VOICE`, or `OPUS_SIGNAL_MUSIC`。

看Encoder related CTLs 和 Generic CTLs可以获得可设置和查询的参数详细清单。在一个音频流处理过程中，大多数参数可以设置或修改。 **为了对一个帧进行编码，必须正确地用音频数据的帧(2.5, 5, 10, 20, 40 或60 毫秒)来调用`opus_encode()`或`opus_encode_float()`函数。**

```cpp
len = opus_encode(enc, audio_frame, frame_size, packet, max_packet);
```

在这里：

  * `audio_frame`（音频帧）是`opus_int16`(或用于`opus_encode_float()`的浮点)格式的音频数据
  * `frame_size`（帧大小）是样本中帧的最大数(每个通道)
  * packet（包）是写成压缩数据的字节数组,
  * `max_packet`是可以写入包的字节数的最大值推荐(4000字节)。不要使用max_packet控制VBR的目标比特率,而应该用`OPUS_SET_BITRATE CTL`。 `opus_encode()` 和`opus_encode_float()`返回实际写入包的字节数。返回值可以是负数,这表明一个错误已经发生。如果返回值是1个字节,那么包不需要传播(DTX)。 一旦一个编码器状态已不再需要，可以用以下方式解构：

```cpp
opus_encoder_destroy(enc);
```

如果编码器是用`opus_encoder_init()`创建的，而不是使用`opus_encoder_create()`函数，那么不需要采取行动，要求从潜在的释放为它手动分配的内存(上述例子是调用free(enc))中分离。

### 类型定义文档

```cpp 
typedef struct OpusEncoder OpusEncoder //Opus编码器状态。
```

这包含了一个Opus编码器的完整状态。它是位置独立的，并且可以自由复制。

### 函数文档

```cpp  
opus_int32 opus_encode(
    OpusEncoder *       st,
    const opus_int16 *  pcm,
    int                 frame_size,
    unsigned char *     data,
    opus_int32          max_data_bytes 
)   
```

对一个Opus帧进行编码。

| 参数 |  | |
| ---- | ---- | ---- |
| [in] | st | `OpusEncoder*:编码器状态` |
| [in] | pcm | `opus_int16*: 输入信号(如果是2 通道有交叉). 长度是 frame_size* channels*sizeof(opus_int16)` |
| [in] | `frame_size` | int:输入信号的每通道样本数. |
| [out] | data | `unsigned char*: 输出负载。必须包含至少max_data_bytes 的容量。` |
| [in] | max_data_bytes | `opus_int32`: 为输出负载所分配的内存大小。可以用于限制固定比特率的最大上限，但不能用作唯一的比特率限制，可以用OPUS_SET_BITRATE来控制比特率。|

返回值：   成功，是被编码包的长度（字节数）; 失败，一个负的错误代码.

```cpp
opus_int32 opus_encode_float(
    OpusEncoder *   st,
    const float *   pcm,
    int             frame_size,
    unsigned char * data,
    opus_int32      max_data_bytes
) 
```

根据浮点输入对一个 Opus帧进行编码.

| 参数 |  | |
| ---- | ---- | ---- |
| [in] | st | `OpusEncoder*`:编码器状态 |
| [in] | pcm | `float*`:浮点格式的输入(如果是2 通道有交叉)，正常范围在+/-1.0之间.超过该范围的采样也是支持的，但它将被解码器用整型API截取，并且只能在知道远端支持扩展的动态范围的情况下使用。长度是`frame_size* channels*sizeof(float)` |
| [in] | `frame_size` | int: 输入信号的每通道样本数. 这必须是编码器采样率的Opus帧大小。比如，48 kHz 下允许值有120, 240, 480, 960, 1920, 和 2880。少于10毫秒的采样（48 kHz 有480个样本），将阻止编码器使用LPC或混合模式。|
| [out] | data | `unsigned char*`:输出负载。必须包含至少max_data_bytes 的容量。|
| [in] | `max_data_bytes` | `opus_int32`: 为输出负载所分配的内存大小。可以用于限制固定比特率的最大上限，但不能用作唯一的比特率限制，可以用`OPUS_SET_BITRATE`来控制比特率。|

返回值：成功，是被编码包的长度（字节数），失败，一个负的错误代码。

```cpp
OpusEncoder* opus_encoder_create(
    opus_int32   Fs,
    int     channels,
    int     application,
    int *   error 
) 
```

分配和初始化一个编码器状态。包括三种编码模式：

  * `OPUS_APPLICATION_VOIP`：在给定比特率条件下为声音信号提供最高质量，它通过高通滤波和强调共振峰和谐波增强了输入信号。它包括带内前向错误检查以预防包丢失。典型的VOIP应用程序使用这种模式。由于进行了增强，即使是高比特率的情况下，输出的声音与输入相比，听起来可能不一样。
  * `OPUS_APPLICATION_AUDIO`：对大多数非语音信号，如音乐，在给定比特率条件下提供了最高的质量。使用这种模式的场合包括音乐、混音(音乐/声音),广播,和需要不到15 毫秒的信号延迟的其他应用。
  * `OPUS_APPLICATION_RESTRICTED_LOWDELAY`：配置低延迟模式将为减少延迟禁用语音优化模式。这种模式只能在刚初始化或刚重设编码器的情况下使用，因为在这些情况下编解码器的延迟被修改了。

(当心！）当调用者知道语音优化模式不再需要时，配置低延迟模式是有用的。

| 参数 |  |  |
| ---- | ---- | ---- |
| [in] | Fs | `opus_int32`: 输入信号的采样率(Hz)，必须是8000、12000、16000、24000、或48000。|
| [in] | channels | int:输入信号的通道数(1 or 2) 。|
| [in] | application | int:编码模式`(OPUS_APPLICATION_VOIP/OPUS_APPLICATION_AUDIO/OPUS_APPLICATION_RESTRICTED_LOWDELAY)` |
| [out] | error | `int*`: 错误代码 |

注意：无论选择什么样的采样率和通道数, 如果选择的比特率太低，Opus编码器可以切换到一个较低的音频带宽或通道数。这也意味着总是使用48kHz立体声输入和让编码器优化编码是安全的。

```cpp
int opus_encoder_ctl(
    OpusEncoder *    st,
    int     request,
    ... 
)
```

向一个Opus编码器执行一个 CTL 函数.一般其请求和后续的参数是由一个提供便利的宏来产生的。

| 参数 |  | | 
| ---- | ---- | ---- |
| [in] | st | `OpusEncoder*`: 编码器状态 |
| [in] | request | int：这个及所有其他参数应被1个在Generic CTLs 或Encoder related CTLs所提供便利的宏来替代 |

参见: 

- Generic CTLs
- Encoder related CTLs

```cpp
void opus_encoder_destroy(OpusEncoder *   st) 
```

Frees an OpusEncoder allocated by opus_encoder_create().释放一个根据`opus_encoder_create()`已分配的OpusEncoder对象。

| 参数 |  | |
| ---- | ---- | ---- |
| [in] | st | `OpusEncoder*`: 用于释放的编码器状态。|

```cpp
int opus_encoder_get_size(int     channels)
```

获得 OpusEncoder结构的大小。

| 参数 |  | |
| ---- | ---- | ---- |
| [in] | channels | int: 通道数，必须是1或2. |

返回:   字节数的大小.

```cpp
int opus_encoder_init(
    OpusEncoder *   st,
    opus_int32      Fs,
    int     channels,
    int     application 
)   
```

初始化一个以前分配的编码器状态。状态所指向的内存必须至少是opus_encoder_get_size()返回的大小.在这里，应用程序不要用系统自动分配内存，而要准备用自己的分配器。 参见:`opus_encoder_create()`,`opus_encoder_get_size()`。为重设一个以前初始化的状态，使用`OPUS_RESET_STATE CTL`.

| 参数 |  |  |
| ---- | ---- | ---- |
| [in] | st | `OpusEncoder*`: 编码器状态 |
| [in] | Fs | `opus_int32`: 输入信号的采样率(Hz)，必须是8000、12000、16000、24000、或48000。|
| [in] | channels | int: 输入信号的通道数(1 or 2) |
| [in] | application | int: 编码模式(`OPUS_APPLICATION_VOIP/OPUS_APPLICATION_AUDIO/OPUS_APPLICATION_RESTRI CTED_LOWDELAY`) |

返回值: 成功，`OPUS_OK`，失败，错误代码。

## 解码器Opus Decoder

### 类型定义

```cpp 
typedef struct OpusDecoder OpusDecoder //Opus 解码器状态.
```

### 函数

| functon |  |
| ---- | ---- |
| `int opus_decoder_get_size(int channels)` | 获得OpusDecoder 结构的大小. |
| `OpusDecoder * opus_decoder_create(opus_int32 Fs, int channels, int *error)` | 分配和初始化解码器状态. |
| `int opus_decoder_init(OpusDecoder *st, opus_int32 Fs, int channel)` | 初始化以前分配的解码器状态.|
| `int opus_decode(OpusDecoder *st, const unsigned char *data, opus_int32 len, opus_int16 *pcm, int frame_size, int decode_fec)` | 解码一个 Opus 包. |
| `int opus_decode_float(OpusDecoder *st, const unsigned char *data, opus_int32 len, float *pcm, int frame_size, int decode_fec)` | 解码一个浮点输出的Opus 包，. |
| `int opus_decoder_ctl(OpusDecoder *st, int request,...)` | 向一个Opus解码器执行CTL 函数。 |
| `void opus_decoder_destroy(OpusDecoder *st)` | 释放通过opus_decoder_create().分配过的OpusDecoder。|
| `int opus_packet_parse(const unsigned char *data, opus_int32 len, unsigned char *out_toc, const unsigned char *frames[48], short size[48], int *payload_offset)` | 将一个 opus 包解析成1个或多个帧. |
| `int opus_packet_get_bandwidth(const unsigned char *data)` | 获得一个Opus包的带宽. |
| `int opus_packet_get_samples_per_frame(const unsigned char *data, opus_int32 Fs)` | 获得Opus 包每帧的样本数。 |
| `int opus_packet_get_nb_channels(const unsigned char *data)` | 获得Opus 包的通道数。 |
| `int opus_packet_get_nb_frames(const unsigned char packet[], opus_int32 len)` | 获得Opus 包所有帧的数量. |
| `int opus_packet_get_nb_samples(const unsigned char packet[], opus_int32 len, opus_int32 Fs)` | 获得Opus 包的样本数。 |
| `int opus_decoder_get_nb_samples(const OpusDecoder *dec, const unsigned char packet[], opus_int32 len)` | 获得Opus 包的样本数。|

### 详细描述

与编码相似，解码进程也是开始于创建一个解码器状态。用以下方法做到：

```cpp
int error;
OpusDecoder *dec;
dec = opus_decoder_create(Fs, channels, &error);
```

在这里：   

- Fs 是采样率，必须是8000, 12000, 16000, 24000, 或 48000   
- channels 是通道数(1 或 2)   
- error 将保存出错情况下的错误代码(或成功状态下的`OPUS_OK`)   
- 返回值是一个新创建的用于解码的解码器状态

当`opus_decoder_create()`为状态分配内存时, 它也可以初始化预分配的内存：

```cpp    
int size;
int error;
OpusDecoder *dec;
size = opus_decoder_get_size(channels);
dec = malloc(size);
error = opus_decoder_init(dec, Fs, channels);
```

`opus_decoder_get_size()`返回解码器状态要求的大小. 注意,这段代码的未来版本可能改变大小,所以没有assuptions应该对它做出。解码器状态在内存中总是连续,复制它只要一个浅拷贝就足够了。

为解码一个帧, `opus_decode()` 或 `opus_decode_float()`必须用压缩音频数据的包来调用: `frame_size = opus_decode(dec, packet, len, decoded, max_size, 0)`; 

在这里   

- packet 是包含压缩数据的字节数组   
- len 是包内字节的精确数量   
- decoded 是opus_int16(或由`opus_decode_float()`定义的浮点型)格式的解码后的音频数据。   
- max_size是可以放入解码帧的每个通道各样本中帧的最大值`opus_decode()`和`opus_decode_float()`返回从包解码后的每通道样本的数量。如果这个值是负的，表示有错误发生。如果包损坏或音频缓冲太小不足以容纳解码后的音频，错误就会发生。

Opus是包含重叠块的有状态的编解码器，其结果是Opus包并不是彼此独立编码。包必须按正确的次序，连续地进入解码器进行正确的解码。丢失的包可以用遗失隐藏来替换，遗失隐藏用一个空的指针和0长度的包来调用解码器。一个单独的编解码器状态在一个时间只能由一个单独的线程来访问，调用者执行任何需要的锁定。各分开的音频数据流可以用各自分开的解码器状态平行地进行解码，除非API库在编译时用了`NONTHREADSAFE_PSEUDOSTACK`定义。

### 类型定义文档

```cpp
typedef struct OpusDecoder OpusDecoder //Opus 解码器状态.
```

这包含了一个Opus解码器的完整状态。它是位置独立的，并且可以自由复制。 参见:`opus_decoder_create,opus_decoder_init`

### 函数文档

```cpp
int opus_decode(
    OpusDecoder *   st,
    const unsigned char *   data,
    opus_int32      len,
    opus_int16 *    pcm,
    int     frame_size,
    int     decode_fec 
)   
```

对一个Opus包进行解码。

| 参数 |  |  |
| ---- | ---- | ---- |
| [in] | st | `OpusDecoder*`: 解码器状态 |
| [in] | data | `char*:`输入负载.对包丢失使用一个空指针来表示。|
| [in] | len | `opus_int32`:在输入负载中的字节数 |
| [out] | pcm | `opus_int16*`: 输出信号（如果是2通道有交叉）。长度等于`frame_size* channels*sizeof(opus_int16)` |
| [in] | `frame_size` | int：在PCM可用空间中每通道的样本数。如果小于最大包的时长（120毫秒，4848kHz5760个），这个函数将不能解码一些包。如果是PLC(data==NULL) 或 FEC(`decode_fec=1`)的情况，那么`frame_size`必须正好是丢失音频的时长，否则解码器无法在解码下一个包时进入优化状态。对于PLC 和 FEC 的情况，`frame_size`必须是2.5毫秒的倍数。|
| [in] | decode_fec | int: 对于请求任何带内前向错误纠正数据进行解码的状态标志(0 or 1) 。如果没有这样的数据可用，帧在解码时被认为已经丢失。|

返回: 解码样本的数量，或错误代码。

```cpp
int opus_decode_float(
    OpusDecoder *   st,
    const unsigned char *   data,
    opus_int32      len,
    float *     pcm,
    int     frame_size,
    int     decode_fec 
)   
```

用浮点输出格式解码一个Opus包。

| 参数 |  |  |
| ---- | ---- | ---- |
| [in] | st | `OpusDecoder*:` 解码器状态 |
| [in] | data | `char*:`输入负载.对包丢失使用一个空指针来表示。|
| [in] | len | `opus_int32`: 在输入负载中的字节数 |
| [out] | pcm | `float*`:输出信号（如果是2通道有交叉）。长度等于`frame_size* channels*sizeof(float)` |
| [in] | `frame_size` | int：在PCM可用空间中每通道的样本数。如果小于最大包的时长（120毫秒，4848kHz5760个），这个函数将不能解码一些包。如果是PLC(data==NULL) 或 FEC(`decode_fec=1`)的情况，那么`frame_size`必须正好是丢失音频的时长，否则解码器无法在解码下一个包时进入优化状态。对于PLC 和 FEC的情况，`frame_size`必须是2.5毫秒的倍数。|
| [in] | `decode_fec` | int: 对于请求任何带内前向错误纠正数据进行解码的状态标志(0 or 1) 。如果没有这样的数据可用，帧在解码时被认为已经丢失。 |

返回: 解码样本的数量，或错误代码。

```cpp
OpusDecoder* opus_decoder_create(
    opus_int32   Fs,
    int     channels,
    int *   error 
) 
```

分配和初始化解码器状态.

| 参数 |  |  |
| ---- | ---- | ---- |
| [in] | Fs | `opus_int32`: 解码的采样率(Hz). 必须是 8000, 12000, 16000, 24000, 或 48000. |
| [in] | channels | int: 用于解码的通道数(1 or 2) |
| [out] | error | `int*`:成功时是 `OPUS_OK` Success或错误代码 |

```cpp
int opus_decoder_ctl(
    OpusDecoder *   st,
    int     request,
    ... 
) 
```

向一个Opus解码器执行一个 CTL 函数. 一般其请求和后续的参数是由一个提供便利的宏来产生的。

| 参数 |  |
| ---- | ---- |
| st | `OpusDecoder*`: 解码器状态.!|
| request | int：这个及所有其他剩余参数应被1个在Generic CTLs 或Encoder related CTLs所提供便利的宏来替代! |

参见: Generic CTLs   Decoder related CTLs

```cpp
void opus_decoder_destroy(OpusDecoder *st)
```

释放一个根据`opus_decoder_create()`已分配的OpusDecoder对象.

| 参数 |  |
| ---- | ---- |
| st | OpusDecoder*:用于释放的解码器状态。|

```cpp
int opus_decoder_get_nb_samples(
    const OpusDecoder * dec,
    const unsigned char packet[],
    opus_int32 len 
) 
```

获得一个Opus包的样本数

| 参数 |  |  |
| ---- | ---- | ---- |
| [in] | dec | `OpusDecoder*`: 解码器状态 |
| [in] | packet | `char*`: Opus包 |
| [in] | len | `opus_int32`: 包的长度 |

返回:  样本的数量  返回值: `OPUS_INVALID_PACKET`：通过的被压缩数据已损坏或其格式不被支持。

```cpp
int opus_decoder_get_size(int channels)
```

获得OpusDecoder结构的大小。

| 参数 |  |  |
| ---- | ---- | ---- |
| [in] | channels | int: 通道数，必须是1或2.|

返回: 字节数的大小.

```cpp
int opus_decoder_init(
    OpusDecoder *   st,
    opus_int32      Fs,
    int     channels 
) 
```

初始化一个以前分配过的解码器状态.   

- 状态必须至少是`opus_decoder_get_size()`返回的大小.   
- 在这里，应用程序不要用系统自动分配内存，而要准备用自己的分配器。 参见:`opus_decoder_create`,`opus_decoder_get_size`,为重设一个以前初始化的状态，使用`OPUS_RESET_STATE CTL`

| 参数 |  |  |
| ---- | ---- | ---- |
| [in] | st | `OpusDecoder*`: 解码器状态. |
| [in] | Fs | `opus_int32`: 准备解码的采样率(Hz). 必须是8000、12000、16000、24000、或48000. |
| [in] | channels | int: 解码的通道数(1 or 2) |

返回值:  成功，`OPUS_OK` ，失败，错误代码。

```cpp
int opus_packet_get_bandwidth(const unsigned char *data)
```

获得一个Opus包的带宽。

| 参数 |  |  |
| ---- | ---- | ---- |
| [in] | data | `char*`: Opus 包 |

返回值:

  * `OPUS_BANDWIDTH_NARROWBAND` 窄带(4kHz bandpass)
  * `OPUS_BANDWIDTH_MEDIUMBAND` 中等带宽(6kHz bandpass)
  * `OPUS_BANDWIDTH_WIDEBAND` 宽带(8kHz bandpass)
  * `OPUS_BANDWIDTH_SUPERWIDEBAND` 高宽带(12kHz bandpass)
  * `OPUS_BANDWIDTH_FULLBAND` 全宽带(20kHz bandpass)
  * `OPUS_INVALID_PACKET` 通过的被压缩数据已损坏或其格式不被支持
```cpp
int opus_packet_get_nb_channels(const unsigned char *data)
```

获得Opus包的通道数。

| 参数 |  |  |
| ---- | ---- | ---- |
| [int] | data | `char*`:Opus包 |

返回:  通道数量 
返回值: `OPUS_INVALID_PACKET`通过的被压缩数据已损坏或其格式不被支持

```cpp
int opus_packet_get_nb_frames(
    const unsigned char     packet[],
    opus_int32      len 
)       
```

获得Opus包所有帧的数量.

| 参数 |  |  |
| ---- | ---- | ---- |
| [in] | packet | `char*`: Opus 包 |
| [in] | len | `opus_int32`:包的长度 |

返回: 帧的数量 
返回值: `  `OPUS_INVALID_PACKET`通过的被压缩数据已损坏或其格式不被支持

```cpp
int opus_packet_get_nb_samples(
    const unsigned char     packet[],
    opus_int32      len,
    opus_int32      Fs 
)   
```

获得Opus包的样本数。

| 参数 |  |  |
| ---- | ---- | ---- |
| [in] | | packet |
| [in] | len | `opus_int32`: 包的长度 |
| [in] | | Fs |

返回: 样本的数量 
返回值:`OPUS_INVALID_PACKET`通过的被压缩数据已损坏或其格式不被支持

```cpp
int opus_packet_get_samples_per_frame(
    const unsigned char *   data,
    opus_int32      Fs 
)   
```

获得Opus包每帧的样本数。

| 参数 |  |  |
| ---- | ---- | ---- |
| [in] | data | `char*`: Opus 包. 必须包含至少一个字节的数据。|
| [in] | Fs | `opus_int32`: 采样率（Hz）.必须是400的倍数，否则结果不准确。|

返回: 每帧样本的数量.

```cpp
int opus_packet_parse(
    const unsigned char *   data,
    opus_int32      len,
    unsigned char *     out_toc,
    const unsigned char *   frames[48],
    short   size[48],
    int *   payload_offset 
)   
```

将一个opus包解析成1个或多个帧. `Opus_decode`在内部执行这个操作，所以大多数应用程序不需要用到这个函数。这个函数不复制各帧，返回的指针是输入包内部的指针。

| 参数 |  |  |
| ---- | ---- | ---- |
| [in] | data | `char*`:要进行解析的 Opus包 |
| [in] | len | `opus_int32`: 数据的大小 |
| [out] | `out_toc` | `char*`: TOC 指针 |
| [out] | frames | `char*`[48] 封装过的帧 |
| [out] | size | short[48] 封装过的帧的大小 |
| [out] | `payload_offset` | `int*`: 返回在包内负载的位置(按字节) |

返回: 帧的数量

## Repacketizer

Repacketizer可将多个包Opus合并成一个包，或将以前合并的包分离成多个Opus包。

### 类型定义

```cpp   
typedef struct OpusRepacketizer OpusRepacketizer
```

### 函数

```cpp  
int opus_repacketizer_get_size(void)
//获得 OpusRepacketizer结构的大小

OpusRepacketizer* opus_repacketizer_init(OpusRepacketizer *rp)
//(重新)初始化以前分配过的repacketizer 状态. 

OpusRepacketizer* opus_repacketizer_create(void)
//为用opus_repacketizer_init()产生的新repacketizer 分配内存和初始化。

void opus_repacketizer_destroy(OpusRepacketizer *rp)
//释放通过opus_repacketizer_create()分配过的OpusRepacketizer 

int opus_repacketizer_cat(OpusRepacketizer *rp, 
    const unsigned char *data, 
    opus_int32 len )
//给当前的repacketizer 状态增加一个包。 

opus_int32 opus_repacketizer_out_range(
    OpusRepacketizer *rp, 
    int begin, int end, 
    unsigned char *data, 
    opus_int32 maxlen)
//通过opus_repacketizer_cat()从以前提交给repacketizer状态的数据构建一个新的包。

int opus_repacketizer_get_nb_frames(OpusRepacketizer *rp)
//返回最后一次调用opus_repacketizer_init() 或 opus_repacketizer_create()后，到当前为止通过opus_repacketizer_cat()提交的包数据所包含的帧的总数。 

opus_int32 opus_repacketizer_out(
    OpusRepacketizer *rp, 
    unsigned char *data, 
    opus_int32 maxlen)
//通过opus_repacketizer_cat()从以前提交给repacketizer状态的数据构建一个新的包。
```

### 详细描述

Repacketizer可将多个包Opus合并成一个包，或将以前合并的包分离成多个Opus包。 分离有效的包可以保证成功，然而，只有在所有的帧都有相同的编码模式、带宽、帧大小，并且合并后的包总的时长不超过120毫秒，合并有效的包才能成功。对多流包的操作不会成功，除了这些包由来自同一音频流的数据组成的退化情况。 

重构包的过程开始于创建一个repacketizer状态，创建既可以通过调用opus_repacketizer_create()函数也可以通过自己分配内存的方式来进行，例如

```cpp
OpusRepacketizer *rp;
rp =(OpusRepacketizer*)malloc(opus_repacketizer_get_size());
if(rp != NULL)
    opus_repacketizer_init(rp);
```

之后应用程序应通过`opus_repacketizer_cat()`来提交包，用`opus_repacketizer_out()`或`opus_repacketizer_out_range()`提取新的包，然后通过`opus_repacketizer_init()`为下一套输入包重设状态。

下面的例子中，将一个系列的包分离成各单独的帧：

```cpp
unsigned char *data;
int len;
while(get_next_packet(&data, &len))
{
    unsigned char out[1276];
    opus_int32 out_len;
    int nb_frames;
    int err;
    int i;
    err = opus_repacketizer_cat(rp, data, len);
    if(err != OPUS_OK)
    {
        release_packet(data);
        return err;
    }
    nb_frames = opus_repacketizer_get_nb_frames(rp);
    for(i = 0; i < nb_frames; i++)
    {
        out_len = opus_repacketizer_out_range(rp, i, i+1, out, sizeof(out));
        if(out_len < 0)
        {
            release_packet(data);
            return(int)out_len;
        }
        output_next_packet(out, out_len);
    }
    opus_repacketizer_init(rp);
    release_packet(data);
}
```

可选择将一个系列的帧合并到各个包中，每个包包含最多`TARGET_DURATION_MS`毫秒的数据:

```cpp
// The maximum number of packets with duration TARGET_DURATION_MS occurs
// when the frame size is 2.5 ms, for a total of(TARGET_DURATION_MS*2/5)
// packets.
unsigned char *data[(TARGET_DURATION_MS*2/5)+1];
opus_int32 len[(TARGET_DURATION_MS*2/5)+1];
int nb_packets;
unsigned char out[1277*(TARGET_DURATION_MS*2/2)];
opus_int32 out_len;
int prev_toc;
nb_packets = 0;
while(get_next_packet(data+nb_packets, len+nb_packets))
{
    int nb_frames;
    int err;
    nb_frames = opus_packet_get_nb_frames(data[nb_packets], len[nb_packets]);
    if(nb_frames < 1)
    {
        release_packets(data, nb_packets+1);
        return nb_frames;
    }
    nb_frames += opus_repacketizer_get_nb_frames(rp);
    // If adding the next packet would exceed our target, or it has an
    // incompatible TOC sequence, output the packets we already have before
    // submitting it.
    // N.B., The nb_packets > 0 check ensures we've submitted at least one
    // packet since the last call to opus_repacketizer_init(). Otherwise a
    // single packet longer than TARGET_DURATION_MS would cause us to try to
    // output an(invalid) empty packet. It also ensures that prev_toc has
    // been set to a valid value. Additionally, len[nb_packets] > 0 is
    // guaranteed by the call to opus_packet_get_nb_frames() above, so the
    // reference to data[nb_packets][0] should be valid.
    if(nb_packets > 0 &&(
       ((prev_toc & 0xFC) !=(data[nb_packets][0] & 0xFC)) ||
        opus_packet_get_samples_per_frame(data[nb_packets], 48000)*nb_frames >
        TARGET_DURATION_MS*48))
    {
        out_len = opus_repacketizer_out(rp, out, sizeof(out));
        if(out_len < 0)
        {
            release_packets(data, nb_packets+1);
            return(int)out_len;
        }
        output_next_packet(out, out_len);
        opus_repacketizer_init(rp);
        release_packets(data, nb_packets);
        data[0] = data[nb_packets];
        len[0] = len[nb_packets];
        nb_packets = 0;
    }
    err = opus_repacketizer_cat(rp, data[nb_packets], len[nb_packets]);
    if(err != OPUS_OK)
    {
        release_packets(data, nb_packets+1);
        return err;
    }
    prev_toc = data[nb_packets][0];
    nb_packets++;
}
// Output the final, partial packet.
if(nb_packets > 0)
{
    out_len = opus_repacketizer_out(rp, out, sizeof(out));
    release_packets(data, nb_packets);
    if(out_len < 0)
        return(int)out_len;
    output_next_packet(out, out_len);
}
```

合并包的一个可替代方案是仅仅无条件地调用`opus_repacketizer_cat()`直到失败。这样，可以用`opus_repacketizer_out()`来获得合并后的包，`opus_repacketizer_cat()`输入的包需要重新添加到一个新的重新初始化的repacketizer状态.

### 类型定义文档

```cpp
typedef struct OpusRepacketizer OpusRepacketizer
```

### 函数文档

```cpp  
int opus_repacketizer_cat( OpusRepacketizer * rp,
    const unsigned char *   data,
    opus_int32      len 
) 
```

添加一个包到当前repacketizer状态。   

这个包必须符合自从最后一次调用opus_repacketizer_init()后，已经提交给repacketizer状态的任何包的配置。这意味着它必须有相同的编码模式、带宽、帧大小和通道数。可以提前进行检查，方法是通过监测包第一个字节的前6位，检查它们是否与其他任何已提交的包的第一个字节的前6位项匹配。添加这个包以后，单个包的总时长，以及在repacketizer状态的音频总时长都不能超过120毫秒。
This packet must match the configuration of any packets already submitted for repacketization since the last call to opus_repacketizer_init(). This means that it must have the same coding mode, audio bandwidth, frame size, and channel count. This can be checked in advance by examining the top 6 bits of the first byte of the packet, and ensuring they match the top 6 bits of the first byte of any previously submitted packet. The total duration of audio in the repacketizer state also must not exceed 120 ms, the maximum duration of a single packet, after adding this packet.   

用`opus_repacketizer_out()` 或`opus_repacketizer_out_range()`，当前repacketizer状态的内容可以被提取到新的包。   

The contents of the current repacketizer state can be extracted into new packets using `opus_repacketizer_out()` or `opus_repacketizer_out_range()`.   

如果想添加不同配置的包，或加更多的超过120毫秒的音频数据，就必须调用`opus_repacketizer_init()`来清除repacketizer状态。如果一个包太大不能整体添加到当前repacketizer状态，它的任何一部分也不能添加，即使这个包包含多个帧，其中部分也许适合添加。如果你想添加这样的包的部分内容，你应当首先使用另一个repacketizer来将这些包分离成适合添加的小片，再一个个地将这些小片加入目标repacketizer状态。   

In order to add a packet with a different configuration or to add more audio beyond 120 ms, you must clear the repacketizer state by calling opus_repacketizer_init(). If a packet is too large to add to the current repacketizer state, no part of it is added, even if it contains multiple frames, some of which might fit. If you wish to be able to add parts of such packets, you should first use another repacketizer to split the packet into pieces and add them individually.

参见: `opus_repacketizer_out_range`  `opus_repacketizer_out` `opus_repacketizer_init`

| 参数 |  |  |
| ---- | ---- | ---- |
| [in] | rp | `OpusRepacketizer*`:将要添加包的repacketizer状态。 The repacketizer state to which to add the packet. |
| [in] | data | const unsigned char*:包数据。应用程序必须确保这个指针合法有效直到对`opus_repacketizer_init() `或`opus_repacketizer_destroy()`的下一次调用。The packet data. The application must ensure this pointer remains valid until the next call to `opus_repacketizer_init()` or `opus_repacketizer_destroy()`.|
| [in] | len | `opus_int32`: 包数据中的字节数。The number of bytes in the packet data. |

返回: 表示操作成功与否的错误代码。 An error code indicating whether or not the operation succeeded. 
返回值: `OPUS_OK`包的内容已被添加到repacketizer状态。The packet's contents have been added to the repacketizer状态. `OPUS_INVALID_PACKET`包的TOC系列无效，该系列不能与以前提交的包相匹配（编码模式、音频带宽、帧大小或通道数不吻合），或添加这个包将导致存储在repacketizer状态的声音时长超过120毫秒。The packet did not have a valid TOC sequence, the packet's TOC sequence was not compatible with previously submitted packets(because the coding mode, audio bandwidth, frame size, or channel count did not match), or adding this packet would increase the total amount of audio stored in the repacketizer状态 to more than 120 ms.

```cpp
OpusRepacketizer* opus_repacketizer_create(void)
```

为用`opus_repacketizer_init()`产生的新repacketizer分配内存和初始化。 Allocates memory and initializes the new repacketizer with `opus_repacketizer_init()`.

```cpp
void opus_repacketizer_destroy(OpusRepacketizer *rp)
```

释放通过`opus_repacketizer_create()`分配过的OpusRepacketizer。 Frees an OpusRepacketizer allocated by `opus_repacketizer_create()`. 

| 参数 |  |  |
| ---- | ---- | ---- |
| [in] | rp | `OpusRepacketizer*`:将被释放的repacketizer状态。 State to be freed.|

```cpp
int opus_repacketizer_get_nb_frames(OpusRepacketizer *rp)
```

返回最后一次调用`opus_repacketizer_init()`或`opus_repacketizer_create()`后，到当前为止通过`opus_repacketizer_cat()`提交的包数据所包含的帧的总数。
Return the total number of frames contained in packet data submitted to the repacketizer状态 so far via `opus_repacketizer_cat()` since the last call to `opus_repacketizer_init()` or `opus_repacketizer_create()`.

这里定义了能被`opus_repacketizer_out_range()` 或 `opus_repacketizer_out()`提取的有效包的范围。 This defines the valid range of packets that can be extracted with `opus_repacketizer_out_range()` or `opus_repacketizer_out()`. 

| 参数 |  |  |
| ---- | ---- | ---- |
| [in] | rp | `OpusRepacketizer*`: 包含各帧的repacketizer状态。The repacketizer状态 containing the frames. |

返回: 提交给repacketizer状态的包所包含的帧的总数。 The total number of frames contained in the packet data submitted to the repacketizer状态.

```cpp
int opus_repacketizer_get_size( void )
```

获得 OpusRepacketizer结构的大小 Gets the size of an OpusRepacketizer structure. 
返回:结构体字节的大小 The size in bytes.

```cpp    
OpusRepacketizer* opus_repacketizer_init( OpusRepacketizer * rp )
```

(重新)初始化以前分配过的repacketizer 状态(Re)initializes a previously allocated repacketizer状态. Repacketizer状态必须至少有opus_repacketizer_get_size()返回的大小。这适用于不使用malloc()，而是用自己的分配器的应用程序。它也要被调用来重设正在等待重构的那些包的队列，如果最大包时长达到120ms或你希望用不同的Opus配置（编码模式、音频带宽、帧大小或通道数）来提交包的时候，这么做就有必要了。这么做如果失败了，系统将阻止用`opus_repacketizer_cat()`添加新的包。
The state must be at least the size returned by `opus_repacketizer_get_size()`. 
This can be used for applications which use their own allocator instead of malloc(). It must also be called to reset the queue of packets waiting to be repacketized, which is necessary if the maximum packet duration of 120 ms is reached or if you wish to submit packets with a different Opus configuration(coding mode, audio bandwidth, frame size, or channel count). Failure to do so will prevent a new packet from being added with opus_repacketizer_cat(). 

参见: `opus_repacketizer_create opus_repacketizer_get_size opus_repacketizer_cat` 

| 参数 |  |  |
| ---- | ---- | ---- |
| [in] | rp | `OpusRepacketizer*`:需要(重新)初始化的repacketizer状态 返回: 输入的同一个repacketizer状态的指针。 A pointer to the same repacketizer状态 that was passed in.|

```cpp
opus_int32 opus_repacketizer_out(
    OpusRepacketizer *rp,
    unsigned char *     data,
    opus_int32      maxlen 
) 
```

通过`opus_repacketizer_cat()`从以前提交给repacketizer状态的数据构建一个新的包。 Construct a new packet from data previously submitted to the repacketizer状态 via `opus_repacketizer_cat()`.

返回迄今提交进单一个包的所有数据可以提供便利，这么做等同于调用`opus_repacketizer_out_range(rp, 0, `opus_repacketizer_get_nb_frames(rp),data, maxlen)` This is a convenience routine that returns all the data submitted so far in a single packet. It is equivalent to calling `opus_repacketizer_out_range(rp, 0,opus_repacketizer_get_nb_frames(rp), data, maxlen)`

| 参数 |  |  |
| ---- | ---- | ---- |
| [in] | rp | `OpusRepacketizer*`: 准备构建新包的repacketizer状态。The repacketizer状态 from which to construct the new packet. |
| [out] | data | `const unsigned char*`: 将要存储输出包的缓冲区。The buffer in which to store the output packet. maxlen `opus_int32`: 将要存入输出缓冲区的字节最大数。为保证成功，这个值应该至少为`1277_opus_repacketizer_get_nb_frames(rp)`。然而，`1_opus_repacketizer_get_nb_frames(rp)`加上自从上次调用`opus_repacketizer_init()`或`opus_repacketizer_create()`以来所有提交包数据的大小，也是足够的，也可能小得多（此话似有矛盾）。 The maximum number of bytes to store in the output buffer. In order to guarantee success, this should be at least `1277_opus_repacketizer_get_nb_frames(rp)`. However, `1_opus_repacketizer_get_nb_frames(rp)` plus the size of all packet data submitted to the repacketizer since the last call to `opus_repacketizer_init()` or `opus_repacketizer_create()` is also sufficient, and possibly much smaller.|

返回: 成功，输出包总的大小，失败，错误代码。 The total size of the output packet on success, or an error code on failure. 
返回值: `OPUS_BUFFER_TOO_SMALL` 最大容量maxlen不足以包含整个输出包。maxlen was insufficient to contain the complete output packet.

```cpp
opus_int32 opus_repacketizer_out_range(
    OpusRepacketizer *      rp,
    int     begin,
    int     end,
    unsigned char *     data,
    opus_int32      maxlen 
)   
```

通过`opus_repacketizer_cat()`从以前提交给repacketizer状态的数据构建一个新的包。 Construct a new packet from data previously submitted to the repacketizer状态 via `opus_repacketizer_cat()`. 

| 参数 |  |  |
| ---- |  ---- | ---- |
| [in] | rp | `OpusRepacketizer*`: 准备构建新包的repacketizer状态。The repacketizer state from which to construct the new packet. begin int: 准备输出的当前repacketizer状态第一帧的索引。The index of the first frame in the current repacketizer state to include in the output. end int: 准备输出的当前repacketizer状态最后一帧的索引再加1.One past the index of the last frame in the current repacketizer state to include in the output. |
| [out] |  data |  `const unsigned char*`: 准备存储输出包的缓冲区。The buffer in which to store the output packet. maxlen `opus_int32`: 将要存入输出缓冲区的字节最大数。为保证成功，这个值应该至少为`1277_opus_repacketizer_get_nb_frames(rp)`。然而，`1_opus_repacketizer_get_nb_frames(rp)`加上自从上次调用`opus_repacketizer_init()`或`opus_repacketizer_create()`以来所有提交包数据的大小，也是足够的，也可能小得多（此话似有矛盾）。 The maximum number of bytes to store in the output buffer. In order to guarantee success, this should be at least 1276 for a single frame, or for multiple frames, 1277*(end-begin). However, 1*(end-begin) plus the size of all packet data submitted to the repacketizer since the last call to `opus_repacketizer_init()` or `opus_repacketizer_create()` is also sufficient, and possibly much smaller. |

返回: 成功，输出包总的大小，失败，错误代码。 The total size of the output packet on success, or an error code on failure. 返回值: `OPUS_BAD_ARG` （begin,end）是帧无效的位置(begin < 0, begin >= end, or end > `opus_repacketizer_get_nb_frames()`). [begin,end) was an invalid range of frames(begin < 0, begin >= end, or end > `opus_repacketizer_get_nb_frames()`). `OPUS_BUFFER_TOO_SMALL` 最大容量maxlen不足以包含整个输出包。maxlen was insufficient to contain the complete output packet.

## Opus Multistream API

Multistream API允许将多个Opus数据流组合成一个包，能够支持多达255通道。 The multistream API allows individual Opus streams to be combined into a single packet, enabling support for up to 255 channels.

### 类型定义

```cpp   
typedef struct OpusMSEncoder
OpusMSEncoder
```

Opus 多流编码器状态.

```cpp
typedef struct OpusMSDecoder
OpusMSDecoder
```

Opus多留解码器状态.

### 多流编码器函数

```cpp  
//获得OpusMSEncoder结构的大小.
opus_int32
opus_multistream_encoder_get_size(int streams, int coupled_streams)

//分配和初始化多流编码器状态。
OpusMSEncoder * opus_multistream_encoder_create(opus_int32 Fs, int channels, int streams, int coupled_streams, const unsigned char *mapping, int application, int *error)

//初始化以前分配的多流编码器状态。
int opus_multistream_encoder_init(OpusMSEncoder *st, opus_int32 Fs, int channels, int streams, int coupled_streams, const unsigned char *mapping, int application)

//编码一个多流Opus帧。
int opus_multistream_encode(OpusMSEncoder *st, const opus_int16 *pcm, int frame_size, unsigned char *data, opus_int32 max_data_bytes)

//从浮点型输入编码一个多流Opus帧。
int opus_multistream_encode_float(OpusMSEncoder *st, const float *pcm, int frame_size, unsigned char *data, opus_int32 max_data_bytes)

//释放经 opus_multistream_encoder_create()分配过的OpusMSEncoder 。 
void opus_multistream_encoder_destroy(OpusMSEncoder *st)

//向一个多流Opus编码器执行CTL 函数。
int opus_multistream_encoder_ctl(OpusMSEncoder *st, int request,...)
```

### 多流解码器函数

```cpp  
//获得OpusMSDecoder结构的大小.
opus_int32
opus_multistream_decoder_get_size(int streams, int coupled_streams)

//分配和初始化多流解码器状态。
OpusMSDecoder * opus_multistream_decoder_create(opus_int32 Fs, int channels, int streams, int coupled_streams, const unsigned char *mapping, int *error)

//初始化以前分配的多流编码器状态对象。
int opus_multistream_decoder_init(OpusMSDecoder *st, opus_int32 Fs, int channels, int streams, int coupled_streams, const unsigned char *mapping)

//解码一个多流Opus包。
int opus_multistream_decode(OpusMSDecoder *st, const unsigned char *data, opus_int32 len, opus_int16 *pcm, int frame_size, int decode_fec)

//用浮点型输出解码一个多流Opus包。
int opus_multistream_decode_float(OpusMSDecoder *st, const unsigned char *data, opus_int32 len, float *pcm, int frame_size, int decode_fec)

//向一个多流Opus解码器执行CTL 函数。 
int opus_multistream_decoder_ctl(OpusMSDecoder *st, int request,...)

//释放经 opus_multistream_decoder_create()分配过的OpusMSDecoder。 
void opus_multistream_decoder_destroy(OpusMSDecoder *st)
```

### 详细描述

多流 API允许将多个Opus数据流组合成一个包，能够支持多达255通道。 The multistream API allows individual Opus streams to be combined into a single packet, enabling support for up to 255 channels. 不象一个基本的Opus流，在解码器能成功解释编码器生成的包内的数据前，编码器和解码器必须就通道配置协商一致。一些基本的信息，比如包时长，可以不需要特别的协商就可以计算获得。 Unlike an elementary Opus stream, the encoder and decoder must negotiate the channel configuration before the decoder can successfully interpret the data in the packets produced by the encoder. Some basic information, such as packet duration, can be computed without any special negotiation. 

多流Opus包的格式是定义在Ogg封装的规格，也是基于RFC 6716附录B所阐述的自限定Opus框架。标准的Opus包正好是多流Opus包的退化版本，可以用对流API进行编码和解码，只要在初始化编码器和解码器时将流数量设置为1. The format for multistream Opus packets is defined in the Ogg encapsulation specification and is based on the self-delimited Opus framing described in Appendix B of RFC 6716. Normal Opus packets are just a degenerate case of multistream Opus packets, and can be encoded or decoded with the multistream API by setting streams to 1 when initializing the encoder or decoder. 

多流Opus数据流能包含最多255个基本的Opus流，这些既可以是“组队的”也可以是“非组队的”，表明解码器被配置来分别用1或2个通道来解码它们。这些流是有序的，以便所有组队的流起初就能出现（似乎不够恰当）。 Multistream Opus streams can contain up to 255 elementary Opus streams. These may be either "uncoupled" or "coupled", indicating that the decoder is configured to decode them to either 1 or 2 channels, respectively. The streams are ordered so that all coupled streams appear at the beginning.

一张映射表用来定义哪个解码通道i应被用于哪个输入/输出(I/O)通道j。这张表典型地作为一个无符号字符型阵列。让i = mapping[j]也就是I/O通道j的索引。如果i< `2_coupled_streams`,那么i若为偶数，I/O 通道 j被按照数据流的左声道进行编码；若i为奇数，I/O通道 j被按照数据流的右声道进行编码。其他情况下，I/O 通道 j被按照数据流的单声道编码(i - `coupled_streams`),除非它有特殊的值255，在这种情况下它将被从编码中彻底删掉（解码器将其作为静音重建）。i的每个值不是特殊值255就是小于streams + `coupled_streams`。 A mapping table defines which decoded channel i should be used for each input/output(I/O) channel j. This table is typically provided as an unsigned char array. Let i = mapping[j] be the index for I/O channel j. If i < `2_coupled_streams`, then I/O channel j is encoded as the left channel of stream(i/2) if i is even, or as the right channel of stream(i/2) if i is odd. Otherwise, I/O channel j is encoded as mono in stream(i - `coupled_streams`), unless it has the special value 255, in which case it is omitted from the encoding entirely(the decoder will reproduce it as silence). Each value i must either be the special value 255 or be less than streams + `coupled_stream`s. 

必须说明，编码器的输出通道应使用Vorbis（免费音乐格式）的通道规则。解码器可能希望应用一个附加的排列以映射用于实现不同输出通道规则的编码器（例如用于WAV规则的输出）。 The output channels specified by the encoder should use the Vorbis channel ordering. A decoder may wish to apply an additional permutation to the mapping the encoder used to achieve a different output channel order(e.g. for outputing in WAV order). 

多流包包含对应每个流的各Opus包，在单一多流包内的所有Opus包必须有相同的时长。因此，一个多流包的时长可以从位于包开始位置的第一个流的TOC序列提取，就象一个基本的Opus流： Each multistream packet contains an Opus psacket for each stream, and all of the Opus packets in a single multistream packet must have the same duration. Therefore the duration of a multistream packet can be extracted from the TOC sequence of the first stream, which is located at the beginning of the packet, just like an elementary Opus stream:

```cpp
int nb_samples;
int nb_frames;
nb_frames = opus_packet_get_nb_frames(data, len);
if(nb_frames < 1)
    return nb_frames;
nb_samples = opus_packet_get_samples_per_frame(data, 48000) * nb_frames;
```

一般的编码和解码过程执行完全相同的标准Opus Encoder 和 Opus Decoder API。如何使用相应的多流函数可以查阅它们的说明文档。 The general encoding and decoding process proceeds exactly the same as in the normal Opus Encoder and Opus Decoder APIs. See their documentation for an overview of how to use the corresponding multistream functions.

### 类型定义文档

```cpp    
typedef struct OpusMSDecoder OpusMSDecoder
```

Opus多流解码器状态。 Opus multistream decoder state.

这包含了一个Opus多流解码器的完整状态。它是位置独立的，并且可以自由复制。 This contains the complete state of a multistream Opus decoder. It is position independent and can be freely copied.

参见: `opus_multistream_decoder_create opus_multistream_decoder_init`

```cpp
typedef struct OpusMSEncoder OpusMSEncoder
```

Opus多流编码器状态。 Opus multistream encoder state.

这包含了一个Opus多流编码器的完整状态。它是位置独立的，并且可以自由复制。 This contains the complete state of a multistream Opus encoder. It is position independent and can be freely copied.

参见: `opus_multistream_encoder_create opus_multistream_encoder_init`

### 函数文档

```cpp    
int opus_multistream_decode(
    OpusMSDecoder *     st,
    const unsigned char *   data,
    opus_int32      len,
    opus_int16 *    pcm,
    int     frame_size,
    int     decode_fec 
)   
```

解码一个多流Opus包。 Decode a multistream Opus packet. 

| 参数: | | |
| --- | --- | --- |
| | st | `OpusMSDecoder*`: Opus多流解码器状态。Multistream decoder state. |
| [in] | data |  `const unsigned char*`:输入负载.对包丢失使用一个空指针来表示。 Input payload. Use a NULL pointer to indicate packet loss.|
| | len | `opus_int32`: 在输入负载中的字节数。Number of bytes in payload.|
| [out] | pcm | `opus_int16*`:使用交叉样本的输出信号。必须有容纳`frame_size_channels`样本数的空间。Output signal, with interleaved samples. This must contain room for `frame_size_channels` samples. |
| | `frame_size` | int: 在PCM可用空间中每通道的样本数。如果小于最大包的时长（120毫秒，4848kHz5760个），这个函数将不能解码一些包。如果是PLC(data==NULL) 或 FEC(`decode_fec=1`)的情况，那么`frame_size`必须正好是丢失音频的时长，否则解码器无法在解码下一个包时进入优化状态。对于PLC 和 FEC 的情况，`frame_size`必须是2.5毫秒的倍数。The number of samples per channel of available space in pcm. If this is less than the maximum packet duration(120 ms; 5760 for 48kHz), this function will not be capable of decoding some packets. In the case of PLC(data==NULL) or FEC(`decode_fec`=1), then frame_size needs to be exactly the duration of audio that is missing, otherwise the decoder will not be in the optimal state to decode the next incoming packet. For the PLC and FEC cases, `frame_size` must be a multiple of 2.5 ms. |
| | `decode_fec` | int: 对于请求任何带内前向错误纠正数据进行解码的状态标志(0 or 1) 。如果没有这样的数据可用，帧在解码时被认为已经丢失。 Flag(0 or 1) to request that any in-band forward error correction data be decoded. If no such data is available, the frame is decoded as if it were lost. 返回: 成功，解码样本的数量，失败，负的错误代码。Number of samples decoded on success or a negative error code(see Error codes) on failure. |

```cpp
int opus_multistream_decode_float(
    OpusMSDecoder *     st,
    const unsigned char *   data,
    opus_int32      len,
    float *     pcm,
    int     frame_size,
    int     decode_fec 
) 
```

用浮点输出格式解码一个多流Opus包。 Decode a multistream Opus packet with floating point output. 

| 参数: | | |
| --- | --- | --- |
| | st | `OpusMSDecoder*`: Opus多流解码器状态。Multistream decoder state.|
| [in] | data | `const unsigned char*`:输入负载.对包丢失使用一个空指针来表示。 Input payload. Use a NULL pointer to indicate packet loss. |
| | len | `opus_int32`: 在输入负载中的字节数。 Number of bytes in payload.|
| [out] | pcm | `opus_int16*`:使用交叉样本的输出信号。必须有容纳`frame_size_channels`样本数的空间。Output signal, with interleaved samples. This must contain room for `frame_size_channels` samples.|
| | `frame_size` | int: 在PCM可用空间中每通道的样本数。如果小于最大包的时长（120毫秒，4848kHz5760个），这个函数将不能解码一些包。如果是PLC(data==NULL) 或 FEC(`decode_fec`=1)的情况，那么`frame_size`必须正好是丢失音频的时长，否则解码器无法在解码下一个包时进入优化状态。对于PLC 和 FEC 的情况，`frame_size`必须是2.5毫秒的倍数。The number of samples per channel of available space in pcm. If this is less than the maximum packet duration(120 ms; 5760 for 48kHz), this function will not be capable of decoding some packets. In the case of PLC(data==NULL) or FEC(`decode_fec`=1), then frame_size needs to be exactly the duration of audio that is missing, otherwise the decoder will not be in the optimal state to decode the next incoming packet. For the PLC and FEC cases, `frame_size` must be a multiple of 2.5 ms. |
| | `decode_fec` |  int: 对于请求任何带内前向错误纠正数据进行解码的状态标志(0 or 1) 。如果没有这样的数据可用，帧在解码时被认为已经丢失。 Flag(0 or 1) to request that any in-band forward error correction data be decoded. If no such data is available, the frame is decoded as if it were lost. |

返回: 成功，解码样本的数量，失败，负的错误代码。Number of samples decoded on success or a negative error code(see Error codes) on failure.
    
```cpp
OpusMSDecoder* opus_multistream_decoder_create(
    opus_int32      Fs,
    int     channels,
    int     streams,
    int     coupled_streams,
    const unsigned char *   mapping,
    int *   error 
) 
```

分配和初始化多流解码器状态。 Allocates and initializes a multistream decoder state.

当结束时要调用`opus_multistream_decoder_destroy()`来释放这个对象。 Call `opus_multistream_decoder_destroy()` to release this object when finished. 

| 参数: | | |
| --- | --- | --- |
| | Fs | `opus_int32`: 解码的采样率(Hz). 必须是 8000, 12000, 16000, 24000, 或 48000.Sampling rate to decode at(in Hz). This must be one of 8000, 12000, 16000, 24000, or 48000.|
| | channels | int: 用于解码的通道数，这个数最大是255，可能与编码通道(streams + coupled_streams)的数量不同。Number of channels to output. This must be at most 255. It may be different from the number of coded channels(streams + coupled_streams). |
| | streams | int:编码进输入的数据流的总数，必须不能超过255. The total number of streams coded in the input. This must be no more than 255. |
| | coupled_streams | int: 要解码为组对流（2通道）的数据流的数量。必须不大于数据流的总数。另外，编码通道(streams + `coupled_streams`)的数量必须不大于255.Number of streams to decode as coupled(2 channel) streams. This must be no larger than the total number of streams. Additionally, The total number of coded channels(streams + `coupled_streams`) must be no more than 255. |
| [in] | mapping | const unsigned char[channels]:被编码通道与输出通道的映射关系表。Mapping from coded channels to output channels, as described in Opus Multistream API.|
| [out] | error | `int *`:成功，返回`OPUS_OK`，失败，返回错误代码。 Returns `OPUS_OK` on success, or an error code(see Error codes) on failure.|

```cpp
int opus_multistream_decoder_ctl(
    OpusMSDecoder *     st,
    int     request,
    ... 
)      
```

向一个Opus多流解码器执行一个 CTL 函数. Perform a CTL function on a multistream Opus decoder.
一般其请求和后续的参数是由一个提供便利的宏来产生的。 Generally the request and subsequent arguments are generated by a convenience macro. 

| 参数: | |
| --- | --- |
| st | `OpusMSDecoder*`: 多流解码器状态。Multistream decoder state. |
|  |  Request : 这个及所有其他剩余参数应被1个在Generic CTLs，Decoder相关的CTLs, 或Multistream 具体的编码器和解码器CTLs所提供便利的宏来替代。This and all remaining parameters should be replaced by one of the convenience macros in Generic CTLs, Decoder related CTLs, or Multistream specific encoder and decoder CTLs. |

参见: Generic CTLs Decoder related CTLs Multistream specific encoder and decoder CTLs
    
```cpp
void opus_multistream_decoder_destroy(OpusMSDecoder * st)
```

释放一个根据`opus_multistream_decoder_create()`已分配的OpusMSDecoder对象. Frees an OpusMSDecoder allocated by `opus_multistream_decoder_create()`. 

| 参数: | |
| --- | --- |
| st | OpusMSDecoder: 用于释放的多流解码器状态。Multistream decoder state to be freed.|

```cpp
opus_int32 opus_multistream_decoder_get_size(
    int streams,
    int coupled_streams
)
```

获得 OpusMSDecoder结构的大小。 Gets the size of an OpusMSDecoder structure. 

| 参数: | |
| --- | --- |
| streams | int: 编码进输入的数据流的总数，必须不能超过255. The total number of streams coded in the input. This must be no more than 255. |
| `coupled_streams` |  int: 要解码为组对流（2通道）的数据流的数量。必须不大于数据流的总数。另外，编码通道(streams + `coupled_streams`)的数量必须不大于255.Number streams to decode as coupled(2 channel) streams. This must be no larger than the total number of streams. Additionally, The total number of coded channels(streams + `coupled_streams`) must be no more than 255. |

返回: 成功，字节数，失败，负的错误代码。 The size in bytes on success, or a negative error code(see Error codes) on error.

```cpp    
int opus_multistream_decoder_init(
    OpusMSDecoder *     st,
    opus_int32      Fs,
    int     channels,
    int     streams,
    int     coupled_streams,
    const unsigned char *   mapping 
) 
```

初始化一个以前分配过的解码器状对象。 Intialize a previously allocated decoder state object. 

st所指向的内存必须至少是`opus_multistream_decoder_get_size()`返回的大小，是给不用系统自动分配内存，而要准备用自己的分配器的应用程序用的。为重设以前初始化的状态，使用`OPUS_RESET_STATE CTL`。 The memory pointed to by st must be at least the size returned by `opus_multistream_decoder_get_size()`. This is intended for applications which use their own allocator instead of malloc. To reset a previously initialized state, use the OPUS_RESET_STATE CTL. 

参见:`opus_multistream_decoder_create opus_multistream_deocder_get_size` 

| 参数: | | |
| --- | --- | --- |
|  | st | `OpusMSEncoder*`:准备初始化的多流解码器状态。Multistream encoder state to initialize.|
|  | Fs | `opus_int32`: 解码的采样率(Hz). 必须是 8000, 12000, 16000, 24000, 或 48000.Sampling rate to decode at(in Hz). This must be one of 8000, 12000, 16000, 24000, or 48000.|
|  | channels | int: 用于输出的通道数，这个数最大是255，可能与编码通道(streams + `coupled_streams`)的数量不同。Number of channels to output. This must be at most 255. It may be different from the number of coded channels(streams + `coupled_streams`).|
|  | streams | int: 编码进输入的数据流的总数，必须不能超过255.The total number of streams coded in the input. This must be no more than 255.|
|  | `coupled_streams` | int: 要解码为组对流（2通道）的数据流的数量。必须不大于数据流的总数。另外，编码通道(streams + `coupled_streams`)的数量必须不大于255.Number of streams to decode as coupled(2 channel) streams. This must be no larger than the total number of streams. Additionally, The total number of coded channels(streams + `coupled_streams`) must be no more than 255.|
| [in] | mapping | const unsigned char[channels]: 被编码通道与输出通道的映射关系表。Mapping from coded channels to output channels, as described in Opus Multistream API.|

返回: 成功，返回`OPUS_OK`，失败，返回错误代码。 `OPUS_OK` on success, or an error code(see Error codes) on failure.

```cpp
int opus_multistream_encode(
    OpusMSEncoder *     st,
    const opus_int16 *      pcm,
    int     frame_size,
    unsigned char *     data,
    opus_int32      max_data_bytes 
)   
```

对一个多流Opus帧进行编码。 Encodes a multistream Opus frame. 

| 参数: | | |
| --- | --- | --- |
| | st | `OpusMSEncoder*`:多流编码器状态。Multistream encoder state.|
| [in] | pcm | `const opus_int16*`:使用交叉样本的输入信号。必须有容纳`frame_size_channels`样本数的空间。The input signal as interleaved samples. This must contain `frame_size_channels` samples.|
| | `frame_size` | int: 输入信号的每通道使用交叉样本的输出信号。必须有容纳`frame_size*channels`样本数的空间。数. 这必须是编码器采样率的Opus帧大小。比如，48 kHz 下允许值有120, 240, 480, 960, 1920, 和 2880。少于10毫秒的采样（48 kHz 有480个样本），将阻止编码器使用LPC或混合模式。Number of samples per channel in the input signal. This must be an Opus frame size for the encoder's sampling rate. For example, at 48 kHz the permitted values are 120, 240, 480, 960, 1920, and 2880. Passing in a duration of less than 10 ms(480 samples at 48 kHz) will prevent the encoder from using the LPC or hybrid modes. |
| [out] | data | `unsigned char*`:输出负载。必须包含至少`max_data_bytes的容量。 Output payload. This must contain storage for at least `max_data_bytes`.|
| [in] | `max_data_bytes` | `opus_int32`: 为输出负载所分配的内存大小。可以用于限制固定比特率的最大上限，但不能用作唯一的比特率限制，可以用`OPUS_SET_BITRATE`来控制比特率。Size of the allocated memory for the output payload. This may be used to impose an upper limit on the instant bitrate, but should not be used as the only bitrate control. `Use OPUS_SET_BITRATE` to control the bitrate. |

返回: 成功，是被编码包的长度（字节数），失败，一个负的错误代码。 The length of the encoded packet(in bytes) on success or a negative error code(see Error codes) on failure.

```cpp
int opus_multistream_encode_float(
    OpusMSEncoder *     st,
    const float *   pcm,
    int     frame_size,
    unsigned char *     data,
    opus_int32      max_data_bytes 
)
```

根据浮点输入对一个 Opus帧进行编码. Encodes a multistream Opus frame from floating point input. 

| 参数: | | |
| --- | --- | --- |
| | st | `OpusMSEncoder*`:多流编码器状态。Multistream encoder state.|
| [in] | pcm | `const float*`:交叉样本的输入信号，正常范围在+/-1.0之间. 超过该范围的采样也是支持的，但它将被解码器用整型API截取，并且只能在知道远端支持扩展的动态范围的情况下使用。必须有容纳`frame_size_channels`样本数的空间。The input signal as interleaved samples with a normal range of +/-1.0. Samples with a range beyond +/-1.0 are supported but will be clipped by decoders using the integer API and should only be used if it is known that the far end supports extended dynamic range. This must contain `frame_size_channels` samples.|
| | `frame_size` | int: 输入信号的每通道使用交叉样本的输出信号。必须有容纳`frame_size*channels`样本数的空间。数. 这必须是编码器采样率的Opus帧大小。比如，48 kHz 下允许值有120, 240, 480, 960, 1920, 和 2880。少于10毫秒的采样（48 kHz 有480个样本），将阻止编码器使用LPC或混合模式。Number of samples per channel in the input signal. This must be an Opus frame size for the encoder's sampling rate. For example, at 48 kHz the permitted values are 120, 240, 480, 960, 1920, and 2880. Passing in a duration of less than 10 ms(480 samples at 48 kHz) will prevent the encoder from using the LPC or hybrid modes.|
| [out] | data | `unsigned char*`:输出负载。必须包含至少`max_data_bytes`的容量。Output payload. This must contain storage for at least `max_data_bytes`.|
| [in] | `max_data_bytes` | `opus_int32`: 为输出负载所分配的内存大小。可以用于限制固定比特率的最大上限，但不能用作唯一的比特率限制，可以用`OPUS_SET_BITRATE`来控制比特率。Size of the allocated memory for the output payload. This may be used to impose an upper limit on the instant bitrate, but should not be used as the only bitrate control. Use `OPUS_SET_BITRATE` to control the bitrate.|

返回: 成功，是被编码包的长度（字节数），失败，一个负的错误代码。 The length of the encoded packet(in bytes) on success or a negative error code(see Error codes) on failure.

```cpp
OpusMSEncoder* opus_multistream_encoder_create(
    opus_int32      Fs,
    int     channels,
    int     streams,
    int     coupled_streams,
    const unsigned char *   mapping,
    int     application,
    int *   error 
)   
```

分配和初始化多流编码器状态。 Allocates and initializes a multistream encoder state.

当结束时要调用`opus_multistream_encoder_destroy()`来释放这个对象。 Call `opus_multistream_encoder_destroy()` to release this object when finished. 

| 参数: | | |
| --- | --- | --- |
| | Fs | `opus_int32`: 解码的采样率(Hz). 必须是 8000, 12000, 16000, 24000, 或 48000.Sampling rate of the input signal(in Hz). This must be one of 8000, 12000, 16000, 24000, or 48000.|
| | channels | int: 输入信号中的通道数，这个数最大是255，可能比编码通道(streams + `coupled_streams`)的数量更大。Number of channels in the input signal. This must be at most 255. It may be greater than the number of coded channels(streams + `coupled_streams`).|
| | streams | int从:输入要编码的数据流的总数，必须不能超过通道数. The total number of streams to encode from the input. This must be no more than the number of channels.|
| | `coupled_streams` | int: 要编码的组对（2通道）数据流的总数，必须不大于数据流的总数。另外，编码通道(streams + `coupled_streams`)的总数必须不超过输入通道的数量.Number of coupled(2 channel) streams to encode. This must be no larger than the total number of streams. Additionally, The total number of encoded channels(streams + `coupled_streams`) must be no more than the number of input channels.|
| [in] | mapping | const unsigned char[channels]: 被编码通道与输入通道的映射关系表。作为一个额外的限制，多流编码器不允许对一个通道不可用的组对数据流进行编码，因为这个想法太烂了。Mapping from encoded channels to input channels, as described in Opus Multistream API. As an extra constraint, the multistream encoder does not allow encoding coupled streams for which one channel is unused since this is never a good idea.|
| | application | int: 目标编码器应用程序，必须是以下之一：The target encoder application. This must be one of the following: * `OPUS_APPLICATION_VOIP` 改进语音清晰度的处理信号。Process signal for improved speech intelligibility. * `OPUS_APPLICATION_AUDIO` 偏好与原始输入的正确性。Favor faithfulness to the original input.* `OPUS_APPLICATION_RESTRICTED_LOWDELAY` 通过使特定操作模式失效以使编码延迟尽可能小。Configure the minimum possible coding delay by disabling certain modes of operation.|
| [out] | error | `int *`:成功，返回`OPUS_OK`，失败，返回错误代码。Returns `OPUS_OK` on success, or an error code(see Error codes) on failure.|

```cpp
int opus_multistream_encoder_ctl(
    OpusMSEncoder *     st,
    int     request,
        ... 
) 
```

向一个Opus多流编码器执行一个 CTL 函数. Perform a CTL function on a multistream Opus encoder.

一般其请求和后续的参数是由一个提供便利的宏来产生的。 Generally the request and subsequent arguments aregenerated by a convenience macro. 

| 参数: | |
| --- | --- |
| st | `OpusMSEncoder*`: 多流编码器状态。Multistream encoder state. |
| | request：这个及所有其他剩余参数应被1个在Generic CTLs，Encoder相关的CTLs,或Multistream 具体的编码器和解码器CTLs所提供便利的宏来替代。This and all remaining parameters should be replaced by one of the convenience macros in Generic CTLs, Encoder related CTLs, or Multistream specific encoder and decoder CTLs. |

参见: Generic CTLs Encoder related CTLs Multistream specific encoder and decoder CTLs

`void opus_multistream_encoder_destroy(OpusMSEncoder *st)`释放一个根据`opus_multistream_encoder_create()`已分配的OpusMSEncoder对象. Frees an OpusMSEncoder
allocated by `opus_multistream_encoder_create()`. 

| 参数: | |
| --- | --- |
| st | `OpusMSEncoder*`:用于释放的多流编码器状态。 Multistream encoder state to be freed.|

```cpp
opus_int32 opus_multistream_encoder_get_size(
    int     streams,
    int     coupled_streams 
)   
```

获得 OpusMSEncoder结构的大小。 Gets the size of an OpusMSEncoder structure. 

| 参数: | |
| --- | --- |
| streams | int: 从输入用于编码的数据流的总数，必须不能超过255. The total number of streams to encode from the input. This must be no more than 255.|
| `coupled_streams` | int: 要编码的组对流（2通道）的数量。必须不大于数据流的总数。另外，编码通道(streams + `coupled_streams`)的数量必须不大于255.Number of coupled(2 channel) streams to encode. This must be no larger than the total number of streams. Additionally, The total number of encoded channels(streams + `coupled_streams`) must be no more than 255. |

返回: 成功，字节数，失败，负的错误代码。 The size in bytes on success, or a negative error code(see Error codes) on error.
    
```cpp
int opus_multistream_encoder_init(
    OpusMSEncoder *     st,
    opus_int32      Fs,
    int     channels,
    int     streams,
    int     coupled_streams,
    const unsigned char *   mapping,
    int     application 
)   
```

初始化一个以前分配过的编码器状对象。 Initialize a previously allocated multistream encoder state. st所指向的内存必须至少是`opus_multistream_encoder_get_size()`返回的大小，是给不用系统自动分配内存，而要准备用自己的分配器的应用程序用的。为重设以前初始化的状态，使用`OPUS_RESET_STATE CTL`。 The memory pointed to by st must be at least the size returned by `opus_multistream_encoder_get_size()`. This is intended for applications which use their own allocator instead of
malloc. To reset a previously initialized state, use the `OPUS_RESET_STATE CTL`. 

参见: `opus_multistream_encoder_create opus_multistream_encoder_get_size` 

| 参数: | | |
| --- | --- | --- |
| | st | `OpusMSEncoder*`:准备初始化的多流编码器状态。Multistream encoder state to initialize.|
| | Fs | `opus_int32`: 输入信号的采样率(Hz). 必须是 8000, 12000, 16000, 24000, 或 48000.Sampling rate of the input signal(in Hz). This must be one of 8000, 12000, 16000, 24000, or 48000.|
| | channels | int: 输入信号中的通道数，这个数最大是255，可能大于编码通道(streams + `coupled_streams`)的数量。Number of channels in the input signal. This must be at most 255. It may be greater than the number of coded channels(streams + `coupled_streams`).|
| | streams | int: 从输入要编码的数据流的总数，必须不大于通道的数量. The total number of streams to encode from the input. This must be no more than the number of channels.|
| | `coupled_streams` | int: 要编码的组对（2通道）数据流的总数，必须不大于数据流的总数。另外，编码通道(streams + `coupled_streams`)的总数必须不超过输入通道的数量.Number of coupled(2 channel) streams to encode. This must be no larger than the total number of streams. Additionally, The total number of encoded channels(streams + `coupled_streams`) must be no more than the number of input channels.|
| [in] | mapping | const unsigned char[channels]: 被编码通道与输入通道的映射关系表。作为一个额外的限制，多流编码器不允许对一个通道不可用的组对数据流进行编码，因为这个想法太烂了。Mapping from encoded channels to input channels, as described in Opus Multistream API. As an extra constraint, the multistream encoder does not allow encoding coupled streams for which one channel is unused since this is never a good idea.|
| | application | int: 目标编码器应用程序，必须是以下之一：The target encoder application. This must be one of the following: - `OPUS_APPLICATION_VOIP`改进语音清晰度的处理信号。Process signal for improved speech intelligibility. - `OPUS_APPLICATION_AUDIO`偏好与原始输入的正确性。Favor faithfulness to the original input. - `OPUS_APPLICATION_RESTRICTED_LOWDELAY`通过使特定操作模式失效以使编码延迟尽可能小。Configure the minimum possible coding delay by disabling certain modes of operation. |

返回: 成功，返回`OPUS_OK`，失败，返回错误代码。 `OPUS_OK` on success, or an error code(see Error codes) on failure.

## Opus library information functions

本节描述了Opus库信息函数

### 函数

Converts an opus error code into a human readable string.

```cpp
const char * opus_strerror(int error)
```

Gets the libopus version string.

```cpp
const char * opus_get_version_string(void)
```

### 函数文档

```cpp
const char* opus_get_version_string(void )
```

获得libopus的版本信息，用字符串表示。 Gets the libopus version string. 返回: 版本字符串。Version string

```cpp
const char* opus_strerror(int error )
```

将Opus错误代码转换为人可读的字符串。 Converts an opus error code into a human readable string.

| 参数: | | |
| --- | --- | --- |
| [in] | error | int: 错误号。Error number 返回: 错误字符串。Error string|

## Opus Custom

Opus Custom是Opus规范和参考实现的可选部分，可用于使用与正常API不同的独特API，并且支持非正常的帧大小。Opus Custom只用于一些非常特别的应用程序，这些应用程序需要处理与2.5、 5、10或20ms不同的帧规格（由于复杂度或其他潜在原因），互操作性就不那么重要了。 Opus Custom is an optional part of the Opus specification and reference implementation which uses a distinct API from the regular API and supports frame sizes that are not normally supported. Use of Opus Custom is discouraged for all but very special applications for which a frame size different from 2.5, 5, 10, or 20 ms is needed(for either complexity or latency reasons) and where interoperability is less important.

### 类型定义

编码器状态Contains the state of an encoder.

```cpp
typedef struct OpusCustomEncoder
OpusCustomEncoder
```

解码器状态State of the decoder.

```cpp  
typedef struct OpusCustomDecoder
```

包含用于创建编码器的所有必要信息的模式The mode contains all the information necessary to create an encoder.

### 函数

```cpp
OpusCustomMode *
opus_custom_mode_create(opus_int32 Fs, int frame_size, int *error)
```

创建新的模式结构。Creates a new mode struct.

```cpp
void opus_custom_mode_destroy(OpusCustomMode *mode)
```

解构一个模式结构。Destroys a mode struct.

```cpp
int opus_custom_encoder_get_size(const OpusCustomMode *mode, int channels)
```

获得OpusCustomEncoder 结构的大小。Gets the size of an OpusCustomEncoder structure.

```cpp
OpusCustomEncoder * opus_custom_encoder_create(const OpusCustomMode *mode, int channels, int *error)
```

创建新的编码器状态。Creates a new encoder state.

```cpp
int opus_custom_encoder_init(OpusCustomEncoder *st, const OpusCustomMode *mode, int channels)
```

初始化一个以前分配过的编码器状态，st所指向的内存必须是`opus_custom_encoder_get_size返回的大小。Initializes a previously allocated encoder state The memory pointed to by st must be the size returned by `opus_custom_encoder_get_size`.

```cpp
void opus_custom_encoder_destroy(OpusCustomEncoder *st)
```

解构一个编码器状态。Destroys a an encoder state.

```cpp 
int opus_custom_encode_float(OpusCustomEncoder *st, const float *pcm, int frame_size, unsigned char *compressed, int maxCompressedBytes)
```

给一个音频帧进行编码。Encodes a frame of audio.

```cpp
int opus_custom_encode(OpusCustomEncoder *st, const opus_int16 *pcm, int frame_size, unsigned char *compressed, int maxCompressedBytes)
```

给一个音频帧进行编码。Encodes a frame of audio.

```cpp
int opus_custom_encoder_ctl(OpusCustomEncoder *OPUS_RESTRICT st, int request,...)
```

为一个Opus 定制编码器执行一个CTL 函数。Perform a CTL function on an Opus custom encoder.

```cpp  
int opus_custom_decoder_get_size(const OpusCustomMode *mode, int channels)
```

获得一个OpusCustomDecoder 结构的大小。Gets the size of an OpusCustomDecoder structure.

```cpp  
OpusCustomDecoder * opus_custom_decoder_create(const OpusCustomMode *mode, int channels, int *error)
```

创建新的解码器状态。Creates a new decoder state.

```cpp
int opus_custom_decoder_init(OpusCustomDecoder *st, const OpusCustomMode *mode, int channels)
```

初始化一个以前分配过的解码器状态，st所指向的内存必须是`opus_custom_decoder_get_size`返回的大小。Initializes a previously allocated decoder state The memory pointed to by st must be the size returned by `opus_custom_decoder_get_size`.

```cpp
void opus_custom_decoder_destroy(OpusCustomDecoder *st)
```

解构一个解码器状态。Destroys a an decoder state.

```cpp  
int opus_custom_decode_float(OpusCustomDecoder *st, const unsigned char *data, int len, float *pcm, int frame_size)
```

使用浮点输出解码一个Opus定制帧。Decode an opus custom frame with floating point output.

```cpp
int opus_custom_decode(OpusCustomDecoder *st, const unsigned char *data, int len, opus_int16 *pcm, int frame_size)
```

解码一个Opus定制帧。Decode an opus custom frame.

```cpp
int opus_custom_decoder_ctl(OpusCustomDecoder *OPUS_RESTRICT st, int request,...)
```

为一个Opus 定制解码器执行一个CTL 函数。Perform a CTL function on an Opus custom decoder.

### 详细描述

Opus Custom是Opus规范和参考实现的可选部分，可用于使用与正常API不同的独特API，并且支持非正常的帧大小。O

pus Custom只用于一些非常特别的应用程序，这些应用程序需要处理与2.5、 5、10或20ms不同的帧规格（由于复杂度或其他潜在原因），互操作性就不那么重要了。 Opus Custom is an optional part of the Opus specification and reference implementation which uses a distinct API from the regular API and supports frame sizes that are not normally supported. Use of Opus Custom is discouraged for all but very special applications for which a frame size different from 2.5, 5, 10, or 20 ms is needed(for either complexity or latency reasons) and where interoperability is less important. 

除了互操作性的限制外，Opus定制的使用还会导致大部分的编解码器功能不能使用，并且通常会在一个给定的比特率上降低可达到的质量。正常情况下当应用程序需要从编解码器获得一个不同的帧大小，它应当建立缓冲区以容纳帧所需空间，但这会增加一小点延迟，而这一小点延迟对一些非常低延迟应用程序来说是重要的。一些传输协议（特别是恒定流量的RF传输协议）可能也可以对特殊时长帧的处理达到最佳。 In addition to the interoperiability limitations the use of Opus custom disables a substantial chunk of the codec and generally lowers the quality available at a given bitrate. Normally when an application needs a different frame size from the codec it should buffer to match the sizes but this adds a small amount of delay which may be important in some very low latency applications. Some transports(especially constant rate RF transports) may also work best with frames of particular durations. 

如果在编译期激活，libopus仅支持定制模式。 Libopus only supports custom modes if they are enabled at compile time. Opus定制API与普通API相似，但`opus_encoder_create和opus_decoder_create`的调用一个附加的模式参数，这个模式参数是通过调用`opus_custom_mode_create`产生的结构。编码器和解码器必须达成一个模式，使用相同的采样率(fs)和帧规格(frame size),这些参数必须或者被示意在波段外，或固定在一个特别的实现过程中。 The Opus Custom API is similar to the regular API but the `opus_encoder_create` and `opus_decoder_create` calls take an additional mode parameter which is a structure produced by a call to opus_custom_mode_create. Both the encoder and decoder must create a mode using the same sample rate(fs) and frame size(frame size) so these parameters must either be signaled out of band or fixed in a particular implementation.

与普通的类似，Opus定制模式支持飞行帧大小转换，不过这些可用的大小取决于使用中的特殊帧大小。对于单一数据流的一些开头的帧的大小，飞行帧大小是可用的。
Similar to regular Opus the custom modes support on the fly frame size switching, but the sizes available depend on the particular frame size in use. For some initial frame sizes on a single on the fly size is available.

### 类型定义文档

```cpp
typedef struct OpusCustomDecoder OpusCustomDecoder
```

解码器状态。State of the decoder. 对于每个数据流，需要一个解码器状态。解码器状态在数据流的开头一次性初始化。对于每个帧不要创新初始化。
One decoder state is needed for each stream. It is initialized once at the beginning of the stream. Do not re-initialize the state for every frame.Decoder state

```cpp
typedef struct OpusCustomEncoder OpusCustomEncoder
```

编码器状态。Contains the state of an encoder.

对于每个数据流，需要一个编码器状态。编码器状态在数据流的开头一次性初始化。对于每个帧不要创新初始化。 One encoder state is needed for each stream. It is initialized once at the beginning of the stream. Do not re-initialize the state for every frame. Encoder state

```cpp
typedef struct OpusCustomMode OpusCustomMode
```

包含用于创建编码器的所有必要信息的模式 The mode contains all the information necessary to create an encoder. 
编码器和解码器需要用完全相同的模式来初始化，否则输出将会被破坏。 Both the encoder and decoder need to be initialized with exactly the same mode, otherwise the output will be corrupted. Mode configuration

### 函数文档

```cpp
int opus_custom_decode(
    OpusCustomDecoder *     st,
    const unsigned char *   data,
    int     len,
    opus_int16 *    pcm,
    int     frame_size 
) 
```

解码一个Opus定制帧。 Decode an opus custom frame. 

| 参数: | | |
| --- | --- | --- |
| [in] | st | `OpusCustomDecoder*`:解码器状态Decoder state|
| [in] | data | `char*`:输入负载.对包丢失使用一个空指针来表示。 Input payload. Use a NULL pointer to indicate packet loss|
| [in] | len | int: 在输入负载中的字节数Number of bytes in payload|
| [out] | pcm | `opus_int16*`:输出信号（如果是2通道有交叉）。长度等于`frame_size_channels_sizeof(opus_int16)`。Output signal(interleaved if 2 channels). length is `frame_size_channels_sizeof(opus_int16)`|
| [in] | | `frame_size`: 在*pcm的可用空间每通道的样本数。Number of samples per channel of available space in *pcm. |

返回: 解码样本的数量，或错误代码。Number of decoded samples or Error codes
    
```cpp
int opus_custom_decode_float(
    OpusCustomDecoder *     st,
    const unsigned char *   data,
    int     len,
    float *     pcm,
    int     frame_size 
)
```

用浮点输出解码一个Opus定制帧。 Decode an opus custom frame with floating point output. 

| 参数: | | |
| --- | --- | --- |
| [in] | st | `OpusCustomDecoder*`:解码器状态。 Decoder state|
| [in] | data | `char*`:输入负载.对包丢失使用一个空指针来表示。 Input payload. Use a NULL pointer to indicate packet loss|
| [in] | len | int: 在输入负载中的字节数Number of bytes in payload|
| [out] | pcm | `float*`:输出信号（如果是2通道有交叉）。长度等于`frame_size_channels_sizeof(float)`。Output signal(interleaved if 2 channels). length is `frame_size_channels_sizeof(float)`|
| [in] | | `frame_size`: 在*pcm的可用空间每通道的样本数。Number of samples per channel of available space in *pcm. |

返回: 解码样本的数量，或错误代码。Number of decoded samples or Error codes

```cpp 
OpusCustomDecoder* opus_custom_decoder_create(
    const OpusCustomMode *      mode,
    int     channels,
    int *   error 
)
```

创建新的解码器状态。 Creates a new decoder state. 
每个数据流需要有它自己的解码器状态（不能与同时发生的数据流共享）。 Each stream needs its own decoder state(can't be shared across simultaneous streams). 

| 参数: | | |
| --- | --- | --- |
| [in] | mode | OpusCustomMode: 包含关于数据流的特征的所有信息（必须与用于编码器的相同）。Contains all the information about the characteristics of the stream(must be the same characteristics as used for the encoder)|
| [in] | channels | int: 通道数。Number of channels|
| [out] | error | `int*`: 返回错误代码。Returns an error code |

返回: 新创建的解码器状态。Newly created decoder state.
    
```cpp
int opus_custom_decoder_ctl( 
    OpusCustomDecoder *OPUS_RESTRICT    st,
    int     request,
        ... 
)   
```

为Opus定制解码器执行一个CTL函数。 Perform a CTL function on an Opus custom decoder.
一般其请求和后续的参数是由一个提供便利的宏来产生的。 Generally the request and subsequent arguments are generated by a convenience macro. 参见: Generic CTLs

```cpp
void opus_custom_decoder_destroy( OpusCustomDecoder * st ) 
//解构一个解码器状态。Destroys a an decoder state.
```

| 参数: | | |
| --- | --- | --- |
| [in] | st | `OpusCustomDecoder*`:将要释放的状态。 State to be freed.|

```cpp
int opus_custom_decoder_get_size(
    const OpusCustomMode *      mode,
    int     channels 
)   
```

获得OpusCustomDecoder结构的大小。 Gets the size of an OpusCustomDecoder structure. 

| 参数: | | |
| --- | --- | --- |
| [in] | mode | `OpusCustomMode *`: 模式配置。Mode configuration|
| [in] | channels | int: 通道数。Number of channels 返回: 大小。size|

```cpp
int opus_custom_decoder_init(
    OpusCustomDecoder *     st,
    const OpusCustomMode *      mode,
    int     channels 
)
```

初始化一个以前分配过的解码器状态.st所指向的内存 必须是`opus_custom_decoder_get_size()`返回的大小.在这里，应用程序不要用系统自动分配内存，而要准备用自己的分配器。 Initializes a previously allocated decoder state The memory pointed to by st must be the size retured by `opus_custom_decoder_get_size`. This is intended for applications which use their own allocator instead of malloc. 

参见: `opus_custom_decoder_create(),opus_custom_decoder_get_size()`,为重设一个以前初始化的状态，使用`OPUS_RESET_STATE CTL`.To reset a previously initialized state use the `OPUS_RESET_STATE` CTL.

| 参数: | | |
| --- | --- | --- |
| [in] | st | `OpusCustomDecoder*`:解码器状态.Decoder state|
| [in] | mode | `OpusCustomMode *`:包含关于数据流的特征的所有信息（必须与用于编码器的相同）。Contains all the information about the characteristics of the stream(must be the same characteristics as used for the encoder)|
| [in] | channels | int: 通道数。Number of channels |

返回: 成功，`OPUS_OK`，失败，错误代码。`OPUS_OK` Success or Error codes
    
```cpp
int opus_custom_encode(
    OpusCustomEncoder *     st,
    const opus_int16 *      pcm,
    int     frame_size,
    unsigned char *     compressed,
    int     maxCompressedBytes 
)
```

编码一个音频帧。 Encodes a frame of audio. 

| 参数: | | |
| --- | --- | --- |
| [in] | st | `OpusCustomEncoder*`:编码器状态Encoder state|
| [in] | pcm | `opus_int16*`: 16位格式信号的PCM音频（原本的字节存储次序）。每通道必须恰好有`frame_size`个样本。PCM audio in signed 16-bit format(native endian). There must be exactly `frame_size` samples per channel.|
| [in] | `frame_size` | int: 输入信号每帧的样本数。Number of samples per frame of input signal|
| [out] | compressed | `char *`: 压缩数据被写入到这。可能不是PCM格式，必须具有maxCompressedBytes 的长度。The compressed data is written here. This may not alias pcm and must be at least maxCompressedBytes long.|
| [in] | maxCompressedBytes | int: 用于压缩帧的字节最大数（从一帧到另一帧时可以改变）。Maximum number of bytes to use for compressing the frame(can change from one frame to another) 返回: 写入到“压缩区”的字节数。如果是负的，表示是一个错误(见错误代码)。将该长度以某种方式传递给解码器很重要，如没有这么做，无法进行解码。Number of bytes written to "compressed". If negative, an error has occurred(see error codes). It is IMPORTANT that the length returned be somehow transmitted to the decoder. Otherwise, no decoding is possible.|

```cpp
int opus_custom_encode_float(
    OpusCustomEncoder *     st,
    const float *   pcm,
    int     frame_size,
    unsigned char *     compressed,
    int     maxCompressedBytes 
)   
```

编码一个音频帧。 Encodes a frame of audio. 

| 参数: | | |
| --- | --- | --- |
| [in] | st | `OpusCustomEncoder*`: 编码器状态Encoder state|
| [in] | pcm | `float*`: 浮点格式的PCM音频数据，正常范围在+/-1.0之间. 超过该范围的采样也是支持的，但它将被解码器用整型API截取，并且只能在知道远端支持扩展的动态范围的情况下使用。每通道必须有准确的`frame_size`样本。PCM audio in float format, with a normal range of +/-1.0. Samples with a range beyond +/-1.0 are supported but will be clipped by decoders using the integer API and should only be used if it is known that the far end supports extended dynamic range. There must be exactly `frame_size` samples per channel.|
| [in] | `frame_size` | int: 输入信号每帧的样本数。Number of samples per frame of input signal|
| [out] | compressed | `char *`:压缩数据被写入到这。可能不是PCM格式，必须具有maxCompressedBytes 的长度。 The compressed data is written here. This may not alias pcm and must be at least maxCompressedBytes long.|
| [in] | maxCompressedBytes | int: 用于压缩帧的字节最大数（从一帧到另一帧时可以改变）。 Maximum number of bytes to use for compressing the frame(can change from one frame to another) |

返回: 写入到“压缩区”的字节数。如果是负的，表示是一个错误(见错误代码)。将该长度以某种方式传递给解码器很重要，如没有这么做，无法进行解码。 Number of bytes written to "compressed". If negative, an error has occurred(see error codes). It is IMPORTANT that the length returned be somehow transmitted to the decoder. Otherwise, no decoding is possible.
    
```cpp
OpusCustomEncoder* opus_custom_encoder_create(
    const OpusCustomMode *      mode,
    int     channels,
    int *   error 
)
```

创建新的编码器状态。 Creates a new encoder state. 每个数据流需要有它自己的编码器状态（不能与同时发生的数据流共享）。 Each stream needs its own encoder state(can't be shared across simultaneous streams). 

| 参数: | | |
| --- | --- | --- |
| [in] | mode | `OpusCustomMode*`:包含关于数据流的特征的所有信息（必须与用于解码器的相同）。 Contains all the information about the characteristics of the stream(must be the same characteristics as used for the decoder)|
| [in] | channels | int: 通道数。Number of channels|
| [out] | error | `int*`:返回错误代码。Returns an error code 返回: 新创建的编码器状态。Newly created encoder state.|

```cpp
int opus_custom_encoder_ctl(
    OpusCustomEncoder *OPUS_RESTRICT    st,
    int     request,
        ... 
)
```

为Opus定制编码器执行一个CTL函数。 Perform a CTL function on an Opus custom encoder. 
一般其请求和后续的参数是由一个提供便利的宏来产生的。 Generally the request and subsequent arguments are generated by a convenience macro.

参见: Encoder related CTLs

```cpp
void opus_custom_encoder_destroy( OpusCustomEncoder * st ) 
//解构一个编码器状态。Destroys a an encoder state.
```

| 参数: | | |
| --- | --- | --- |
| [in] | st | `OpusCustomEncoder*`:需要释放的状态。State to be freed.|

```cpp
int opus_custom_encoder_get_size(
    const OpusCustomMode *      mode,
    int     channels 
)
```

获得OpusCustomEncoder结构的大小。 Gets the size of an OpusCustomEncoder structure. 

| 参数: | | |
| --- | --- | --- |
| [in] | mode | `OpusCustomMode *`:模式配置。Mode configuration|
| [in] | channels | int: 通道数。 Number of channels 返回: 大小。size|

```cpp
int opus_custom_encoder_init(
    OpusCustomEncoder *     st,
    const OpusCustomMode *      mode,
    int     channels 
)
```

初始化一个以前分配过的编码器状态.st所指向的内存 必须是`opus_custom_encoder_get_size()`返回的大小.在这里，应用程序不要用系统自动分配内存，而要准备用自己的分配器。 Initializes a previously allocated encoder state The memory pointed to by st must be the size returned by `opus_custom_encoder_get_size`. This is intended for applications which use their own allocator instead of malloc. 

参见: `opus_custom_encoder_create()`,`opus_custom_encoder_get_size()`,为重设一个以前初始化的状态，使用`OPUS_RESET_STATE` CTL. To reset a previously initialized state use the OPUS_RESET_STATE CTL.

| 参数: | | |
| --- | --- | --- |
| [in] | st | `OpusCustomEncoder*`: 编码器状态.Encoder state|
| [in] | mode | `OpusCustomMode *`:包含关于数据流的特征的所有信息（必须与用于解码器的相同）。Contains all the information about the characteristics of the stream(must be the same characteristics as used for the decoder)|
| [in] | channels | int: 通道数。Number of channels |

返回: 成功，`OPUS_OK` ，失败，错误代码。`OPUS_OK` Success or Error codes
    
```cpp
OpusCustomMode* opus_custom_mode_create(
    opus_int32      Fs,
    int     frame_size,
    int *   error 
)
```

创建新的模式结构。 Creates a new mode struct.
这个模式结构将传递给编码器和解码器使用。在使用它的编码器和解码器被解构前，该模式结构必须不能被解构。 This will be passed to an encoder or decoder. The mode MUST NOT BE DESTROYED until the encoders and decoders that use it are destroyed as well. 

| 参数: | | |
| --- | --- | --- |
| [in] | Fs | int: 采用率（8000至96000Hz）Sampling rate(8000 to 96000 Hz)|
| [in] | `frame_size` | int: 编码给每个包（每通道）的采样数（64－1024，因子分解必须包括0或2、3、5，不能是其他素数）。Number of samples(per channel) to encode in each packet(64 - 1024, prime factorization must contain zero or more 2s, 3s, or 5s and no other primes)|
| [out] | error | `int*`: 返回的错误代码（如为Null，表示没有错误）。Returned error code(if NULL, no error will be returned) 返回: 一个新创建的模式对象。A newly created mode|

```cpp
void opus_custom_mode_destroy( OpusCustomMode * mode )
```

解构一个模式结构。 Destroys a mode struct. 注意，须在所有使用这个模式对象的编码器和解码器解构后才能调用这个函数。 Only call this after all encoders and decoders using this mode are destroyed as well. 

| 参数: | | |
| --- | --- | --- |
| [in] | mode | `OpusCustomMode*`: 将要释放的模式结构。Mode to be freed.|


