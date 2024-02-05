 
<!--BEGIN_DATA
{
    "create_date": "2022-03-26 11:20", 
    "modify_date": "2022-03-26 11:20", 
    "is_top": "0", 
    "summary": "H.264流媒体协议格式中的Annex B格式和AVCC格式深度解析", 
    "tags": "音视频", 
    "file_name": "H.264流媒体协议格式中的Annex B格式和AVCC格式深度解析.md"
}
END_DATA-->

#### <p>原文出处：<a href='https://blog.csdn.net/romantic_energy/article/details/50508332' target='blank'>H.264流媒体协议格式中的Annex B格式和AVCC格式深度解析</a></p>

本文需要读者对H.264流有一定的了解才可以理解2种格式差异。  
  
首先要理解的是没有标准的H.264基本流格式。文档中的确包含了一个Annex，特别是描述了一种可能的格式Annex B格式，但是这个并不是一个必须要求的格式。标准文档中指定了视频怎样编码成独立的包，但是这些包是怎样存储和传输的却是开放的。

## 一. Annex B

### A.Network Abstraction Layer Units

视频编码成的包叫做Network Abstraction Layer Units, 也简称为NALU、NAL，每个NALU包都可以被单独的解析和处理，每个NALU包的第一个字节包含了NALU类型，bit3-bit7包含的内容尤其重要(bit 0一定是off的，bit1-2指定了这个NALU是否被其他NALU引用)。  

NALU格式分为2类，VCL和non-VCL，总共有19种不同的NALU格式。  


> VCL, Video Coding Layer packets contain the actual visual information.  即视频编码后的数据
> Non-VCL, contain metadata that may or may not be required to decode the video.  非视频数据，配置信息

一个单独的NALU包、或者甚至一个VCL NALU包都不意味着是一个独立的帧，一帧数据可以被分割成几个NALU，一个或多个NALU组成了一个Access Units(AU)，AU包含了一个完整的帧。把帧分割成几个独立的NALU需要耗费许多CPU资源，所以分割帧数据并不经常使用。  

以下是所有定义了的NALU类型：  

```
0      Unspecified                                                    non-VCL
1      Coded slice of a non-IDR picture                               VCL
2      Coded slice data partition A                                   VCL
3      Coded slice data partition B                                   VCL
4      Coded slice data partition C                                   VCL
5      Coded slice of an IDR picture                                  VCL
6      Supplemental enhancement information (SEI)                     non-VCL
7      Sequence parameter set                                         non-VCL
8      Picture parameter set                                          non-VCL
9      Access unit delimiter                                          non-VCL
10     End of sequence                                                non-VCL
11     End of stream                                                  non-VCL
12     Filler data                                                    non-VCL
13     Sequence parameter set extension                               non-VCL
14     Prefix NAL unit                                                non-VCL
15     Subset sequence parameter set                                  non-VCL
16     Depth parameter set                                            non-VCL
17..18 Reserved                                                       non-VCL
19     Coded slice of an auxiliary coded picture without partitioning non-VCL
20     Coded slice extension                                          non-VCL
21     Coded slice extension for depth view components                non-VCL
22..23 Reserved                                                       non-VCL
24..31 Unspecified                                                    non-VCL
```
  
有几种NALU格式的包包含了非常有用的信息。  
  
```
Sequence Parameter Set (SPS). This non-VCL NALU contains information required to configure the decoder such as profile, level, resolution, frame rate.
Picture Parameter Set (PPS). Similar to the SPS, this non-VCL contains information on entropy coding mode, slice groups, motion prediction and deblocking filters.
Instantaneous Decoder Refresh (IDR). This VCL NALU is a self contained image slice. That is, an IDR can be decoded and displayed without referencing any other NALU save SPS and PPS.
Access Unit Delimiter (AUD). An AUD is an optional NALU that can be use to delimit frames in an elementary stream. It is not required (unless otherwise stated by the container/protocol, like TS), and is often not included in order to save space, but it can be useful to finds the start of a frame without having to fully parse each NALU.
```

### B. NALU Start Codes， NALU包开始码

一个NALU包中的数据并不包含它的大小(长度)信息,因此不能简单的连接NALU包来建立一个流，因为你不知道一个包从哪里结束，另一个包从哪里开始。   

Annex B格式用开始码来解决这个问题，即给每个NALU加上前缀码：2个或者3个0x00,后面再加一个0x01, 如：0x000001或者0x00000001。  

4字节类型的开始码在在连续的数据传输中非常有用，因为用字节来对齐、分割流数据，比如：用连续的31个bit0后接一个bit1来分割流数据，是很容易的。  

如果接下来的bit是0(因为每个NALU都以bit0开始)，那么这就是一个NALU包数据的起始位置了。4字节类型的开始码通常只用于标识流中的随机访问点，如SPS PPS AUD和IDR，然后其他地方都用3字节类型的开始码以减少数据量。  

### C. Emulation Prevention Bytes， 防竞争字节

开始码能起作用是因为3字节的序列0x000000,0x000001,0x000002和0x000003(应该是所有的0x0000**)在non-VCL(原文是non-RBSP,译者修改)NALU包中是非法的，所以在构建ANLU包时，必须确保排除这些数值序列，这是由向每个这种类型的序列插入防竞争字节0x03实现的，那么插入防竞争字节后，0x000001变成了0x00000301。  

当解码的时候，查找和去除防竞争字节非常重要。因为防竞争字节可能出现在NALU包的任意位置，在文档中通常更方便的做法是假定它们已经被去除了，Raw Byte Sequence Payload原始字节序列负载 (RBSP)表示没有防竞争字节的数据序列(包)。  

### D. Example

以下是一个完整的例子：  

```
0x0000 | 00 00 00 01 67 64 00 0A AC 72 84 44 26 84 00 00
0x0010 | 03 00 04 00 00 03 00 CA 3C 48 96 11 80 00 00 00
0x0020 | 01 68 E8 43 8F 13 21 30 00 00 01 65 88 81 00 05
0x0030 | 4E 7F 87 DF 61 A5 8B 95 EE A4 E9 38 B7 6A 30 6A
0x0040 | 71 B9 55 60 0B 76 2E B5 0E E4 80 59 27 B8 67 A9
0x0050 | 63 37 5E 82 20 55 FB E4 6A E9 37 35 72 E2 22 91
0x0060 | 9E 4D FF 60 86 CE 7E 42 B7 95 CE 2A E1 26 BE 87
0x0070 | 73 84 26 BA 16 36 F4 E6 9F 17 DA D8 64 75 54 B1
0x0080 | F3 45 0C 0B 3C 74 B3 9D BC EB 53 73 87 C3 0E 62
0x0090 | 47 48 62 CA 59 EB 86 3F 3A FA 86 B5 BF A8 6D 06
0x00A0 | 16 50 82 C4 CE 62 9E 4E E6 4C C7 30 3E DE A1 0B
0x00B0 | D8 83 0B B6 B8 28 BC A9 EB 77 43 FC 7A 17 94 85
0x00C0 | 21 CA 37 6B 30 95 B5 46 77 30 60 B7 12 D6 8C C5
0x00D0 | 54 85 29 D8 69 A9 6F 12 4E 71 DF E3 E2 B1 6B 6B
0x00E0 | BF 9F FB 2E 57 30 A9 69 76 C4 46 A2 DF FA 91 D9
0x00F0 | 50 74 55 1D 49 04 5A 1C D6 86 68 7C B6 61 48 6C
0x0100 | 96 E6 12 4C 27 AD BA C7 51 99 8E D0 F0 ED 8E F6
0x0110 | 65 79 79 A6 12 A1 95 DB C8 AE E3 B6 35 E6 8D BC
0x0120 | 48 A3 7F AF 4A 28 8A 53 E2 7E 68 08 9F 67 77 98
0x0130 | 52 DB 50 84 D6 5E 25 E1 4A 99 58 34 C7 11 D6 43
0x0140 | FF C4 FD 9A 44 16 D1 B2 FB 02 DB A1 89 69 34 C2
0x0150 | 32 55 98 F9 9B B2 31 3F 49 59 0C 06 8C DB A5 B2
0x0160 | 9D 7E 12 2F D0 87 94 44 E4 0A 76 EF 99 2D 91 18
0x0170 | 39 50 3B 29 3B F5 2C 97 73 48 91 83 B0 A6 F3 4B
0x0180 | 70 2F 1C 8F 3B 78 23 C6 AA 86 46 43 1D D7 2A 23
0x0190 | 5E 2C D9 48 0A F5 F5 2C D1 FB 3F F0 4B 78 37 E9
0x01A0 | 45 DD 72 CF 80 35 C3 95 07 F3 D9 06 E5 4A 58 76
0x01B0 | 03 6C 81 20 62 45 65 44 73 BC FE C1 9F 31 E5 DB
0x01C0 | 89 5C 6B 79 D8 68 90 D7 26 A8 A1 88 86 81 DC 9A
0x01D0 | 4F 40 A5 23 C7 DE BE 6F 76 AB 79 16 51 21 67 83
0x01E0 | 2E F3 D6 27 1A 42 C2 94 D1 5D 6C DB 4A 7A E2 CB
0x01F0 | 0B B0 68 0B BE 19 59 00 50 FC C0 BD 9D F5 F5 F8
0x0200 | A8 17 19 D6 B3 E9 74 BA 50 E5 2C 45 7B F9 93 EA
0x0210 | 5A F9 A9 30 B1 6F 5B 36 24 1E 8D 55 57 F4 CC 67
0x0220 | B2 65 6A A9 36 26 D0 06 B8 E2 E3 73 8B D1 C0 1C
0x0230 | 52 15 CA B5 AC 60 3E 36 42 F1 2C BD 99 77 AB A8
0x0240 | A9 A4 8E 9C 8B 84 DE 73 F0 91 29 97 AE DB AF D6
0x0250 | F8 5E 9B 86 B3 B3 03 B3 AC 75 6F A6 11 69 2F 3D
0x0260 | 3A CE FA 53 86 60 95 6C BB C5 4E F3
```
  
这是一个完整的访问单元（AU），包括3个NALU包，如你所见，数据序列以开始码开始，后面接了一个SPS（SPS以0x67开始），在SPS中，你可以看到有2个防竞争字节。没有这些字节那么非法的数据序列就会出现在这些位置。然后可以看到一个开始码后面接着一个PPS（PPS以0x68开始），然后是一个最后的开始码，后面跟着一个IDR包。这是一个完整的H.264流，如果你把这些数据以16进制的方式保存到一个以.264为后缀名的文件中，可以把这些数据转换成以下图片：

![](./image/20220326-1120-3.png)  
  
Annex B格式通常用于实时的流格式，比如说传输流，通过无线传输的广播、DVD等。在这些格式中通常会周期性的重复SPS和PPS包，经常是在每一个关键帧之前，因此据此建立解码器可以一个随机访问的点，这样就可以加入一个正在进行的流，及播放一个已经在传输的流。  

## 二. AVCC

另一个存储H.264流的方式是AVCC格式，在这种格式中，每一个NALU包都加上了一个指定其长度(NALU包大小)的前缀(in big endian format大端格式)，这种格式的包非常容易解析，但是这种格式去掉了Annex B格式中的字节对齐特性，而且前缀可以是1、2或4字节，这让AVCC格式变得更复杂了，指定前缀字节数(1、2或4字节)的值保存在一个头部对象中(流开始的部分)，这个头通常称为'extradata'或者'sequence header'，它的基本格式如下：  

```
bits    
8   version ( always 0x01 )
8   avc profile ( sps[0][1] )
8   avc compatibility ( sps[0][2] )
8   avc level ( sps[0][3] )
6   reserved ( all bits on )
2   NALULengthSizeMinusOne    // 这个值是（前缀长度-1），值如果是3，那前缀就是4，因为4-1=3
3   reserved ( all bits on )
5   number of SPS NALUs (usually 1)
repeated once per SPS:
  16     SPS size
  variable   SPS NALU data
8   number of PPS NALUs (usually 1)
repeated once per PPS
  16    PPS size
  variable PPS NALU data
```
  
使用上面的例子，那么AVCC extradata看起来像是这样的：  

```
0x0000 | 01 64 00 0A FF E1 00 19 67 64 00 0A AC 72 84 44
0x0010 | 26 84 00 00 03 00 04 00 00 03 00 CA 3C 48 96 11
0x0020 | 80 01 07 68 E8 43 8F 13 21 30
```

你会发现SPS和PPS被存储在了非NALU包中（out of band带外），即独立于基本流数据。这些数据的存储和传输是文件容器的任务，超出了本文的范畴。  

**注意：虽然AVCC格式不使用起始码，防竞争字节还是有的。**  
  
另外，extradata中有一个命名比较容易让人困惑的变量NALULengthSizeMinusOne，这个变量告诉我们用几个字节来存储NALU的长度（前缀：1、2或4），如果NALULengthSizeMinusOne是0，那么每个NALU使用一个字节的前缀来指定长度，那么每个NALU包的最大长度是255字节，这个明显太小了，这种方式对于存储一个完整的关键帧来说太小了。使用2个字节的前缀来指定长度，那么每个NALU包的最大长度是64K字节，这个对于我们的例子来说是足够了，但是限制还是比较大；3字节是比较完美的，但是因为一些原因没有被广泛支持；因此，4字节长度的前缀是目前使用最多的方式，也是这里我们使用的方式：  
  
```
0x0000 | 00 00 02 41 65 88 81 00 05 4E 7F 87 DF 61 A5 8B
0x0010 | 95 EE A4 E9 38 B7 6A 30 6A 71 B9 55 60 0B 76 2E
0x0020 | B5 0E E4 80 59 27 B8 67 A9 63 37 5E 82 20 55 FB
0x0030 | E4 6A E9 37 35 72 E2 22 91 9E 4D FF 60 86 CE 7E
0x0040 | 42 B7 95 CE 2A E1 26 BE 87 73 84 26 BA 16 36 F4
0x0050 | E6 9F 17 DA D8 64 75 54 B1 F3 45 0C 0B 3C 74 B3
0x0060 | 9D BC EB 53 73 87 C3 0E 62 47 48 62 CA 59 EB 86
0x0070 | 3F 3A FA 86 B5 BF A8 6D 06 16 50 82 C4 CE 62 9E
0x0080 | 4E E6 4C C7 30 3E DE A1 0B D8 83 0B B6 B8 28 BC
0x0090 | A9 EB 77 43 FC 7A 17 94 85 21 CA 37 6B 30 95 B5
0x00A0 | 46 77 30 60 B7 12 D6 8C C5 54 85 29 D8 69 A9 6F
0x00B0 | 12 4E 71 DF E3 E2 B1 6B 6B BF 9F FB 2E 57 30 A9
0x00C0 | 69 76 C4 46 A2 DF FA 91 D9 50 74 55 1D 49 04 5A
0x00D0 | 1C D6 86 68 7C B6 61 48 6C 96 E6 12 4C 27 AD BA
0x00E0 | C7 51 99 8E D0 F0 ED 8E F6 65 79 79 A6 12 A1 95
0x00F0 | DB C8 AE E3 B6 35 E6 8D BC 48 A3 7F AF 4A 28 8A
0x0100 | 53 E2 7E 68 08 9F 67 77 98 52 DB 50 84 D6 5E 25
0x0110 | E1 4A 99 58 34 C7 11 D6 43 FF C4 FD 9A 44 16 D1
0x0120 | B2 FB 02 DB A1 89 69 34 C2 32 55 98 F9 9B B2 31
0x0130 | 3F 49 59 0C 06 8C DB A5 B2 9D 7E 12 2F D0 87 94
0x0140 | 44 E4 0A 76 EF 99 2D 91 18 39 50 3B 29 3B F5 2C
0x0150 | 97 73 48 91 83 B0 A6 F3 4B 70 2F 1C 8F 3B 78 23
0x0160 | C6 AA 86 46 43 1D D7 2A 23 5E 2C D9 48 0A F5 F5
0x0170 | 2C D1 FB 3F F0 4B 78 37 E9 45 DD 72 CF 80 35 C3
0x0180 | 95 07 F3 D9 06 E5 4A 58 76 03 6C 81 20 62 45 65
0x0190 | 44 73 BC FE C1 9F 31 E5 DB 89 5C 6B 79 D8 68 90
0x01A0 | D7 26 A8 A1 88 86 81 DC 9A 4F 40 A5 23 C7 DE BE
0x01B0 | 6F 76 AB 79 16 51 21 67 83 2E F3 D6 27 1A 42 C2
0x01C0 | 94 D1 5D 6C DB 4A 7A E2 CB 0B B0 68 0B BE 19 59
0x01D0 | 00 50 FC C0 BD 9D F5 F5 F8 A8 17 19 D6 B3 E9 74
0x01E0 | BA 50 E5 2C 45 7B F9 93 EA 5A F9 A9 30 B1 6F 5B
0x01F0 | 36 24 1E 8D 55 57 F4 CC 67 B2 65 6A A9 36 26 D0
0x0200 | 06 B8 E2 E3 73 8B D1 C0 1C 52 15 CA B5 AC 60 3E
0x0210 | 36 42 F1 2C BD 99 77 AB A8 A9 A4 8E 9C 8B 84 DE
0x0220 | 73 F0 91 29 97 AE DB AF D6 F8 5E 9B 86 B3 B3 03
0x0230 | B3 AC 75 6F A6 11 69 2F 3D 3A CE FA 53 86 60 95
0x0240 | 6C BB C5 4E F3
```
  
AVCC格式的一个优点是在开始配置解码器的时候可以跳到流的中间播放，这种格式通常用于可以被随机访问的多媒体数据，如存储在硬盘的文件。也因为这个特性，MP4、MKV通常用AVCC格式来存储。  
