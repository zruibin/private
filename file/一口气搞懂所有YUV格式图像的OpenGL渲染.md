 
<!--BEGIN_DATA
{
    "create_date": "2024-07-28 10:23", 
    "modify_date": "2024-07-28 10:23", 
    "is_top": "0", 
    "summary": "一口气搞懂所有YUV格式图像的OpenGL渲染", 
    "tags": "OpenGL", 
    "file_name": "一口气搞懂所有YUV格式图像的OpenGL渲染.md"
}
END_DATA-->

#### <p>原文出处：<a href='https://mp.weixin.qq.com/s/QYMNvgoItCqz3buXksCDkw' target='blank'>一口气搞懂所有YUV格式图像的OpenGL渲染</a></p>

> OpenGL ES 渲染 NV21、NV12、I420、YV12、YUYV、UYVY、I444

本文主要讲解常见的几类 YUV 格式图像渲染方式，如果对 YUV 格式不是很熟悉的同学可以翻看旧文**[一文掌握 YUV 图像的基本处理](http://mp.weixin.qq.com/s?__biz=MzIwNTIwMzAzNg==&mid=2654162691&idx=1&sn=50ccf8f9742ee8fe887dd29719a1df3a&chksm=8cf39c30bb841526fdc354191db5f4190f06a89344397f01d75dbdf97f95fe19ccca3cf4c1b9&scene=21#wechat_redirect)**，YUV 格式的介绍这里不再展开。

## 渲染 NV21、NV12 格式图像

NV21、NV12 可以看成同一种结构，**区别只是 uv 的交错排列顺序不同。**

渲染 NV21/NV12 格式图像需要使用 2 个纹理，分别用于保存 Y plane 和 UV plane 的数据，然后在片段着色器中分别对 2 个纹理进行采样，转换成 RGB 数据。

**需要用到 `GL_LUMINANCE` 和 `GL_LUMINANCE_ALPHA` 格式的纹理，其中 `GL_LUMINANCE` 纹理用来加载 NV21/NV12 Y Plane 的数据，`GL_LUMINANCE_ALPHA` 纹理用来加载 UV Plane 的数据。**

加载 NV21/NV12 的 2 个 Plane 数据到纹理，ppPlane[0] 表示 Y Plane 的指针，ppPlane[1] 表示 UV Plane 的指针，注意 2 个纹理的格式和宽高。

```cpp
//upload Y plane data  
glBindTexture(GL_TEXTURE_2D, m_yTextureId);  
glTexImage2D(GL_TEXTURE_2D, 
             0, 
             GL_LUMINANCE, 
             m_RenderImage.width, 
             m_RenderImage.height, 
             0, 
             GL_LUMINANCE, 
             GL_UNSIGNED_BYTE, 
             m_RenderImage.ppPlane[0]);  
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);  
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);  
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);  
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);  
glBindTexture(GL_TEXTURE_2D, GL_NONE);  

//update UV plane data  
glBindTexture(GL_TEXTURE_2D, m_uvTextureId);  
glTexImage2D(GL_TEXTURE_2D, 
             0, 
             GL_LUMINANCE_ALPHA, 
             m_RenderImage.width >> 1, 
             m_RenderImage.height >> 1, 
             0, GL_LUMINANCE_ALPHA, 
             GL_UNSIGNED_BYTE, 
             m_RenderImage.ppPlane[1]);  
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);  
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);  
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);  
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);  
glBindTexture(GL_TEXTURE_2D, GL_NONE);  
```

使用 2 个纹理渲染 NV21 格式图像的片段着色器：

```cpp
#version 300 es  

precision mediump float;                             
in vec2 v_texCoord;                                  
layout(location = 0) out vec4 outColor;              
uniform sampler2D y_texture;                         
uniform sampler2D uv_texture;        

void main()                                          
{                                                    
   vec3 yuv;                                          
   yuv.x = texture(y_texture, v_texCoord).r -0.063;  
   yuv.y = texture(uv_texture, v_texCoord).a-0.502;  
   yuv.z = texture(uv_texture, v_texCoord).r-0.502;  
    vec3 rgb = mat3(1.164, 1.164, 1.164,          
               0,          -0.392,    2.017,            
               1.596,   -0.813,    0.0) * yuv;       
    outColor = vec4(rgb, 1.0);                        
}                                                    
```

使用 2 个纹理渲染 NV12 格式图像的片段着色器（只是交换了一下 uv 分量）：

```cpp
#version 300 es        

precision mediump float;                             
in vec2 v_texCoord;                                  
layout(location = 0) out vec4 outColor;              
uniform sampler2D y_texture;                         
uniform sampler2D uv_texture;  

void main()                                          
{                                                    
   vec3 yuv;                                          
   yuv.x = texture(y_texture, v_texCoord).r -0.063;  
   yuv.z = texture(uv_texture, v_texCoord).a-0.502;  
   yuv.y = texture(uv_texture, v_texCoord).r-0.502;  
    vec3 rgb = mat3(1.164, 1.164, 1.164,          
               0,          -0.392,    2.017,            
               1.596,   -0.813,    0.0) * yuv;       
    outColor = vec4(rgb, 1.0);                        
}                                                    
```

当然也可以使用一张纹理实现 NV21/NV12 图像渲染，参考文章**[OpenGL ES 渲染 NV21/NV12 格式图像有哪些“姿势”？](http://mp.weixin.qq.com/s?__biz=MzIwNTIwMzAzNg==&mid=2654176354&idx=1&sn=995080128622903eab26e139cbe785f1&chksm=8cf35751bb84de47db1dbc9b264cf088160874d1277c320f9a4bf6cf5c9497487b6bb2a390cf&scene=21#wechat_redirect)**

## 渲染 I420、YV12 格式图像

I420 也是 YUV4:2:0 的采样方式，有 3 个 plane , 跟 YV12 格式的区别就是 uv plane 的位置不同。

4x4 的 I420 图像内存分布：

```cpp
(0  ~  3) Y00  Y01  Y02  Y03  
(4  ~  7) Y10  Y11  Y12  Y13  
(8  ~ 11) Y20  Y21  Y22  Y23  
(12 ~ 15) Y30  Y31  Y32  Y33  

(16 ~ 17) U00  U01  
(18 ~ 19) U10  U11  

(20 ~ 21) V00  V01  
(22 ~ 23) V10  V11  
```

类比 NV21 渲染 ，**可以将 I420 格式的三个 plane 数据加载到 3 个纹理，然后再分别采样。**

上传 I420 三个 plane 的数据到纹理：

```cpp
//upload Y plane data  
glBindTexture(GL_TEXTURE_2D, m_yTextureId);  
glTexImage2D(GL_TEXTURE_2D, 
             0, 
             GL_LUMINANCE, 
             m_RenderImage.width, 
             m_RenderImage.height, 
             0, 
             GL_LUMINANCE, 
             GL_UNSIGNED_BYTE, 
             m_RenderImage.ppPlane[0]);  
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);  
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);  
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);  
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);  
glBindTexture(GL_TEXTURE_2D, GL_NONE);  

//update U plane data  
glBindTexture(GL_TEXTURE_2D, m_uTextureId);  
glTexImage2D(GL_TEXTURE_2D, 
             0, 
             GL_LUMINANCE, 
             m_RenderImage.width >> 1,
             m_RenderImage.height >> 1, 
             0, 
             GL_LUMINANCE, 
             GL_UNSIGNED_BYTE, 
             m_RenderImage.ppPlane[1]);  
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);  
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);  
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);  
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);  
glBindTexture(GL_TEXTURE_2D, GL_NONE);  

//update V plane data  
glBindTexture(GL_TEXTURE_2D, m_vTextureId);  
glTexImage2D(GL_TEXTURE_2D, 
             0, 
             GL_LUMINANCE, 
             m_RenderImage.width >> 1, 
             m_RenderImage.height >> 1, 
             0, 
             GL_LUMINANCE, 
             GL_UNSIGNED_BYTE, 
             m_RenderImage.ppPlane[2]);  
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);  
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);  
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);  
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);  
glBindTexture(GL_TEXTURE_2D, GL_NONE);  
```

使用 3 个纹理渲染 I420 格式图像的片段着色器：

```cpp
#version 300 es 

precision mediump float;                             
in vec2 v_texCoord;                                  
layout(location = 0) out vec4 outColor;              
uniform sampler2D y_texture;                         
uniform sampler2D u_texture;  
uniform sampler2D v_texture;  

void main()                                          
{                                                    
   vec3 yuv;                                          
   yuv.x = texture(y_texture, v_texCoord).r -0.063;  
   yuv.y = texture(u_texture, v_texCoord).r-0.502;  
   yuv.z = texture(v_texture, v_texCoord).r-0.502;  
    vec3 rgb = mat3(1.164, 1.164, 1.164,          
               0,          -0.392,    2.017,            
               1.596,   -0.813,    0.0) * yuv;       
    outColor = vec4(rgb, 1.0);                        
}                                                    
```

**同上一节，渲染 YV12 格式只需要在 shader 中交换下 uv 分量，或者上传数据到纹理之前交换下 uv plane 的数据**，代码就不贴出来了，显得太啰嗦。

那么 I420/YV12 的渲染能不能只使用一张纹理就可以实现？

答案是可以的。**类似前文提到的，需要使用 OpenGL ES 3.0 texlFetch 来替代 texture 采样函数，因为 yuv 3 个 plane 都在同一张纹理上，所以不能执行任何形式的过滤和插值操，必须要精确获取像素的内容。**

我们把整个 I420 数据上传到一张 `GL_LUMINANCE` 纹理，尺寸 `[width,height * 3 / 2]` 。

```cpp
glBindTexture(GL_TEXTURE_2D, m_TextureId);  
glTexImage2D (GL_TEXTURE_2D, 
              0, 
              GL_LUMINANCE, 
              m_RenderImage.width, 
              m_RenderImage.height * 3 / 2, 
              0, 
              GL_LUMINANCE, 
              GL_UNSIGNED_BYTE, 
              m_RenderImage.ppPlane[0]);  
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);  
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);  
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);  
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);  
glBindTexture(GL_TEXTURE_2D, GL_NONE);  
```

只使用一张纹理渲染 I420 格式图像的片段着色器，shader 中需要传入图像的分辨率来确保采样的准确性，inputSize 为图像分辨率：

```cpp
#version 300 es  

precision highp float;  
in vec2 v_texCoord;  
uniform sampler2D y_texture;  
uniform vec2 inputSize;  
out vec4 outColor;  

void main() {  
    vec2 uv = v_texCoord;  
    uv.y *= 2.0 / 3.0;  

    float y = texture(y_texture, uv).r - 0.063;  
    vec2 pixelUV = v_texCoord * inputSize;  
    pixelUV.x = mod(pixelUV.y/2.0, 2.0) > 0.001 ? pixelUV.x / 2.0 + inputSize.x / 2.0 : pixelUV.x / 2.0;  
    pixelUV.y = floor(pixelUV.y / 4.0);  
    pixelUV.y += inputSize.y;  

    float u = texelFetch(y_texture, ivec2(int(pixelUV.x), int(pixelUV.y)), 0).r - 0.502;  
    pixelUV = v_texCoord * inputSize;  
    pixelUV.x = mod(pixelUV.y/2.0, 2.0) > 0.001 ? pixelUV.x / 2.0 + inputSize.x / 2.0 : pixelUV.x / 2.0;  
    pixelUV.y = floor(pixelUV.y / 4.0);  
    pixelUV.y += inputSize.y * 5.0 / 4.0;  

    float v = texelFetch(y_texture, ivec2(int(pixelUV.x), int(pixelUV.y)), 0).r - 0.502;  
    vec3 yuv = vec3(y,u,v);  

    highp vec3 rgb = mat3(1.164, 1.164, 1.164,  
    0,       -0.392,    2.017,  
    1.596,   -0.813,    0.0) * yuv;  

    outColor = vec4(rgb, 1.0);  
}
```

代码其实不太好理解的，**可以先点赞收藏，后面慢慢琢磨，可以加我微信进技术群交流。**

## 渲染 YUYV、UYVY 格式图像

YUYV 和 UYVY 格式用的是 YUV 4:2:2 的采样方式，2 个 Y 分量共用一对 UV 分量，一个像素占用 2 个字节。

YUYV 格式的存储格式：

```cpp
(0  ~  7)  Y00  U00  Y01  V00  Y02  U01   Y03  V01  
(8  ~ 15)  Y10  U10  Y11  V10  Y12  U11   Y13  V11  
(16 ~ 23)  Y20  U20  Y21  V20  Y22  U21   Y23  V21  
(24 ~ 31)  Y30  U30  Y31  V30  Y32  U31   Y33  V31  
```

参考 I420 的渲染方式，可以使用 2 个纹理来实现，由于 **YUYV、UYVY 格式是每 2 个字节才有一个 Y 分量**，可以使用 `GL_LUMINANCE_ALPHA` 格式纹理来采样 Y 分量；**每 4 个字节才出现一对 UV 分量**，可以使用 `GL_RGBA` 格式纹理来采样 UV 分量。

上传 YUYV、UYVY 数据到纹理：

```cpp
//upload YUYV、UYVY data  
glBindTexture(GL_TEXTURE_2D, m_yTextureId);  
glTexImage2D(GL_TEXTURE_2D, 
             0, 
             GL_LUMINANCE_ALPHA, 
             m_RenderImage.width, 
             m_RenderImage.height, 
             0, 
             GL_LUMINANCE_ALPHA, 
             GL_UNSIGNED_BYTE, 
             m_RenderImage.ppPlane[0]);  
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);  
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);  
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);  
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);  
glBindTexture(GL_TEXTURE_2D, GL_NONE);  

//update YUYV、UYVY data  
glBindTexture(GL_TEXTURE_2D, m_uvTextureId);  
glTexImage2D(GL_TEXTURE_2D, 
             0, 
             GL_RGBA, 
             m_RenderImage.width >> 1, 
             m_RenderImage.height, 0, 
             GL_RGBA, 
             GL_UNSIGNED_BYTE, 
             m_RenderImage.ppPlane[0]);  
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);  
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);  
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);  
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);  
glBindTexture(GL_TEXTURE_2D, GL_NONE);  
```

使用 2 个纹理渲染 YUYV 格式图像的片段着色器：

```cpp
#version 300 es     

precision mediump float;                             
in vec2 v_texCoord;                                  
layout(location = 0) out vec4 outColor;              
uniform sampler2D y_texture;                         
uniform sampler2D uv_texture; 

void main()                                          
{                                                    
    vec3 yuv;                                          
    yuv.x = texture(y_texture, v_texCoord).r -0.063;  
    vec4 yuyv = texture(uv_texture, v_texCoord);  
    yuv.y = yuyv.g - 0.502;  
    yuv.z = yuyv.a - 0.502;  

    vec3 rgb = mat3(1.164, 1.164, 1.164,          
               0,          -0.392,    2.017,            
               1.596,   -0.813,    0.0) * yuv;   

    outColor = vec4(rgb, 1.0);                        
}     
```

使用 2 个纹理渲染 UYVY 格式图像的片段着色器：

```cpp
#version 300 es       

precision mediump float;                             
in vec2 v_texCoord;                                  
layout(location = 0) out vec4 outColor;              
uniform sampler2D y_texture;                         
uniform sampler2D uv_texture;

void main()                                          
{                                                    
    vec3 yuv;                                          
    yuv.x = texture(y_texture, v_texCoord).a -0.063;  
    vec4 uyvy = texture(uv_texture, v_texCoord);  
    yuv.y = yuyv.r - 0.502;  
    yuv.z = yuyv.b - 0.502;  

    vec3 rgb = mat3(1.164, 1.164, 1.164,          
               0,          -0.392,    2.017,            
               1.596,   -0.813,    0.0) * yuv;       

    outColor = vec4(rgb, 1.0);                        
}     
```

另外，借助于 OpenGL ES 3.0 的 texlFetch 也可以实现只需要一张纹理就可以实现 YUYV、UYVY 格式图像渲染。

直接把整个 YUYV、UYVY 图像数据上传到一张 `GL_LUMINANCE_ALPHA` 格式的纹理，**在 shader 中通过偏移采样的方式获取 uv 值**，同样 shader 中需要传入图像的分辨率 inputSize 来确保采样的准确性。

```cpp
glBindTexture(GL_TEXTURE_2D, m_TextureId);  
glTexImage2D (GL_TEXTURE_2D, 
              0, 
              GL_LUMINANCE_ALPHA, 
              m_RenderImage.width, 
              m_RenderImage.height, 0, 
              GL_LUMINANCE_ALPHA, 
              GL_UNSIGNED_BYTE, 
              m_RenderImage.ppPlane[0]);  
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);  
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);  
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);  
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);  
glBindTexture(GL_TEXTURE_2D, GL_NONE);  
```

只使用一张纹理渲染 YUYV 格式图像的片段着色器：

```cpp
#version 300 es  

precision highp float;  
in vec2 v_texCoord;  
uniform sampler2D y_texture;  
uniform vec2 inputSize;  
out vec4 outColor; 

void main() {  
    //YUYV YUYV  
    vec2 uv = v_texCoord;  
    vec2 pixelUV = v_texCoord * inputSize;  
    pixelUV = floor(pixelUV);  
    vec4 col = texelFetch(y_texture, ivec2(int(pixelUV.x), int(pixelUV.y)), 0);  
    float y = col.r - 0.063;  
    float u,v;  

    if(mod(pixelUV.x, 2.0) > 0.01) {  
        v = col.a - 0.502;  
        pixelUV.x -= 1.0;  
        u = texelFetch(y_texture, ivec2(int(pixelUV.x), int(pixelUV.y)), 0).a - 0.502;  
    } else {  
        u = col.a - 0.502;  
        pixelUV.x += 1.0;  
        v = texelFetch(y_texture, ivec2(int(pixelUV.x), int(pixelUV.y)), 0).a - 0.502;  
    }  

    vec3 yuv = vec3(y,u,v);  
    vec3 rgb = mat3(1.164, 1.164, 1.164,  
    0,       -0.392,    2.017,  
    1.596,   -0.813,    0.0) * yuv;  

    outColor = vec4(rgb, 1.0);  
}  
```

只使用一张纹理渲染 UYVY 格式图像的片段着色器：

```cpp
#version 300 es  

precision highp float;  
in vec2 v_texCoord;  
uniform sampler2D y_texture;  
uniform vec2 inputSize;  
out vec4 outColor;  

void main() {  
    //UYVY UYVY  
    vec2 uv = v_texCoord;  
    vec2 pixelUV = v_texCoord * inputSize;  
    pixelUV = floor(pixelUV);  
    vec4 col = texelFetch(y_texture, ivec2(int(pixelUV.x), int(pixelUV.y)), 0);  
    float y = col.a - 0.063;  
    float u,v; 

    if(mod(pixelUV.x, 2.0) > 0.01) {  
        v = col.r - 0.502;  
        pixelUV.x -= 1.0;  
        u = texelFetch(y_texture, ivec2(int(pixelUV.x), int(pixelUV.y)), 0).r - 0.502;  
    } else {  
        u = col.r - 0.502;  
        pixelUV.x += 1.0;  
        v = texelFetch(y_texture, ivec2(int(pixelUV.x), int(pixelUV.y)), 0).r - 0.502;  
    }  

    vec3 yuv = vec3(y,u,v);  
    vec3 rgb = mat3(1.164, 1.164, 1.164,  
    0,       -0.392,    2.017,  
    1.596,   -0.813,    0.0) * yuv;  

    outColor = vec4(rgb, 1.0);  
}  
```

## 渲染 I444 格式图像

I444 使用的是 YUV 4:4:4 的采样方式，每个像素占用 3 个字节，yuv 各占一个字节，I444 有 3 个 plane 。

首先能想到是使用 3 个 `GL_LUMINANCE` 格式纹理来装载 3 个 plane 的数据，然后在 shader 分别采样出 yuv 值。

上传 I444 三个 plane 的数据到纹理：

```cpp
//upload Y plane data  
glBindTexture(GL_TEXTURE_2D, m_yTextureId);  
glTexImage2D(GL_TEXTURE_2D, 
             0, 
             GL_LUMINANCE, 
             m_RenderImage.width, 
             m_RenderImage.height, 
             0, 
             GL_LUMINANCE, 
             GL_UNSIGNED_BYTE, 
             m_RenderImage.ppPlane[0]);  
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);  
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);  
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);  
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);  
glBindTexture(GL_TEXTURE_2D, GL_NONE);  

//update U plane data  
glBindTexture(GL_TEXTURE_2D, m_uTextureId);  
glTexImage2D(GL_TEXTURE_2D, 
             0, 
             GL_LUMINANCE, 
             m_RenderImage.width, 
             m_RenderImage.height, 
             0, 
             GL_LUMINANCE, 
             GL_UNSIGNED_BYTE, 
             m_RenderImage.ppPlane[1]);  
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);  
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);  
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);  
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);  
glBindTexture(GL_TEXTURE_2D, GL_NONE); 

//update V plane data  
glBindTexture(GL_TEXTURE_2D, m_vTextureId);  
glTexImage2D(GL_TEXTURE_2D, 
             0, 
             GL_LUMINANCE, 
             m_RenderImage.width, 
             m_RenderImage.height, 
             0, 
             GL_LUMINANCE, 
             GL_UNSIGNED_BYTE, 
             m_RenderImage.ppPlane[2]);  
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);  
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);  
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);  
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);  
glBindTexture(GL_TEXTURE_2D, GL_NONE);  
```

使用 3 个纹理渲染 I444 格式图像的片段着色器（是不是跟 I420 使用的一样？）：

```cpp
#version 300 es      

precision mediump float;                             
in vec2 v_texCoord;                                  
layout(location = 0) out vec4 outColor;              
uniform sampler2D y_texture;                         
uniform sampler2D u_texture;  
uniform sampler2D v_texture;   

void main()                                          
{                                                    
    vec3 yuv;                                          
    yuv.x = texture(y_texture, v_texCoord).r -0.063;  
    yuv.y = texture(u_texture, v_texCoord).r-0.502;  
    yuv.z = texture(v_texture, v_texCoord).r-0.502;  
    
    vec3 rgb = mat3(1.164, 1.164, 1.164,          
               0,          -0.392,    2.017,            
               1.596,   -0.813,    0.0) * yuv;       
    
    outColor = vec4(rgb, 1.0);                        
}                                                    
```

**I444 的渲染推荐使用一张纹理，纹理格式 `GL_LUMINANCE` ，纹理尺寸[width, height * 3]，然后 yuv 三个 plane 各占纹理的 1/3 .**

上传 I444 数据到一张纹理：

```cpp
glBindTexture(GL_TEXTURE_2D, m_TextureId);  
glTexImage2D(GL_TEXTURE_2D, 
             0, 
             GL_LUMINANCE, 
             m_RenderImage.width, 
             m_RenderImage.height * 3, 
             0, 
             GL_LUMINANCE, 
             GL_UNSIGNED_BYTE, 
             m_RenderImage.ppPlane[0]);  
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);  
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);  
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);  
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);  
glBindTexture(GL_TEXTURE_2D, GL_NONE);  
```

只使用一张纹理渲染 I444 格式图像的片段着色器：

```cpp
#version 300 es  

precision highp float;  
in vec2 v_texCoord;  
uniform sampler2D y_texture;  
uniform vec2 inputSize;  
out vec4 outColor;  

void main() {  
    vec2 uv = v_texCoord;  
    uv.y *= 1.0 / 3.0;  

    float y = texture(y_texture, uv).r - 0.063;  
    uv.y += 1.0 / 3.0;  

    float u = texture(y_texture, uv).r - 0.502;  
    uv.y += 1.0 / 3.0;  

    float v = texture(y_texture, uv).r - 0.502;  
    vec3 yuv = vec3(y,u,v);  

    highp vec3 rgb = mat3(1.164, 1.164, 1.164,  
    0,       -0.392,    2.017,  
    1.596,   -0.813,    0.0) * yuv;  

    outColor = vec4(rgb, 1.0);  
}
```

由于 I444 yuv 三个 plane 各占纹理的 1/3 ，需要在 shader 中控制每个分量的采样范围，这样既可以节省 2 个纹理也提升了渲染效率。
