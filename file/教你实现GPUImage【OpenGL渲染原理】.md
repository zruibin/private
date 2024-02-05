 
<!--BEGIN_DATA
{
    "create_date": "2017-01-13 11:00", 
    "modify_date": "2017-01-13 11:00", 
    "is_top": "0", 
    "summary": "教你实现GPUImage【OpenGL渲染原理】", 
    "tags": "iOS", 
    "file_name": "教你实现GPUImage【OpenGL渲染原理】.md"
}
END_DATA-->

####<p>原文出处：<a href='http://www.jianshu.com/p/b3852409edbc#' target='blank'>教你实现GPUImage【OpenGL渲染原理】</a></p>

####一、前言

本篇主要讲解GPUImage底层是如何渲染的,GPUImage底层使用的是OPENGL,操控GPU来实现屏幕展示

由于网上OpenGL实战资料特别少，官方文档对一些方法也是解释不清楚，避免广大同学再次爬坑，本篇讲解了不少OpenGL的知识，并且还讲解了花了大量时间解决bug的注意点，曾经因为对glDrawArrays这个方法不熟悉，遇上Bug,晚上熬到凌晨四点都没解决，还是第二天中午解决的。

如果喜欢我的文章，可以关注我微博:[袁峥Seemygo](http://weibo.com/2034818060/profile?rightmod=1&wvr=6&mod=personinfo),也可以来[小码哥](http://www.520it.com)，了解下我们的iOS培训课程。后续还会更新更多内容,有任何问题，欢迎`简书留言`[袁峥Seemygo](http://www.jianshu.com/users/b09c3959ab3b/latest_articles)。。。

####二、GPUImageVideoCamera

  * 可以捕获采集的视频数据

  * 关键是捕获到一帧一帧视频数据如何展示？

  * 通过这个方法可以获取采集的视频数据
    
    
	    - (void)captureOutput:(AVCaptureOutput *)captureOutput didOutputSampleBuffer:(CMSampleBufferRef)sampleBuffer fromConnection:(AVCaptureConnection *)connection

  * 采集视频注意点：要设置采集竖屏，否则获取的数据是横屏
  * 通过AVCaptureConnection就可以设置
    
    
	    [videoConnection setVideoOrientation:AVCaptureVideoOrientationPortraitUpsideDown];

####三、自定义OpenGLView渲染视频

  * 暴露一个接口，获取采集到的帧数据，然后把帧数据传递给渲染View,展示出来
    
    
	    - (void)displayFramebuffer:(CMSampleBufferRef)sampleBuffer;

####四、利用OpenGL渲染帧数据并显示

  * 导入头文件#import <GLKit/GLKit.h>，GLKit.h底层使用了OpenGLES,导入它，相当于自动导入了OpenGLES
  * 步骤
    * 01-自定义图层类型
    * 02-初始化CAEAGLLayer图层属性
    * 03-创建EAGLContext
    * 04-创建渲染缓冲区
    * 05-创建帧缓冲区
    * 06-创建着色器
    * 07-创建着色器程序
    * 08-创建纹理对象
    * 09-YUV转RGB绘制纹理
    * 10-渲染缓冲区到屏幕
    * 11-清理内存

#####01-自定义图层类型

  * 为什么要自定义图层类型CAEAGLLayer? CAEAGLLayer是OpenGL专门用来渲染的图层，使用OpenGL必须使用这个图层
    
    
	    #pragma mark - 1.自定义图层类型
	    + (Class)layerClass
	    {
	        return [CAEAGLLayer class];
	    }

#####02-初始化CAEAGLLayer图层属性

  * 1.不透明度(opaque)=YES,CALayer默认是透明的，透明性能不好,最好设置为不透明.

  * 2.设置绘图属性

    * kEAGLDrawablePropertyRetainedBacking ：NO (告诉CoreAnimation不要试图保留任何以前绘制的图像留作以后重用)
    * kEAGLDrawablePropertyColorFormat ：kEAGLColorFormatRGBA8 (告诉CoreAnimation用8位来保存RGBA的值)
  * 其实设置不设置都无所谓，默认也是这个值,只不过GPUImage设置了
    
    
	    #pragma mark - 2.初始化图层
	    - (void)setupLayer
	    {
	        CAEAGLLayer *openGLLayer = (CAEAGLLayer *)self.layer;
	        _openGLLayer = openGLLayer;
	        // 设置不透明,CALayer 默认是透明的，透明性能不好,最好设置为不透明.
	        openGLLayer.opaque = YES;
	        // 设置绘图属性drawableProperties
	        // kEAGLColorFormatRGBA8 ： red、green、blue、alpha共8位
	        openGLLayer.drawableProperties = @{
	                                           kEAGLDrawablePropertyRetainedBacking :[NSNumber numberWithBool:NO],
	                                          kEAGLDrawablePropertyColorFormat : kEAGLColorFormatRGBA8
	                                           };
	    }

#####03-创建EAGLContext

  * 需要将它设置为当前context，所有的OpenGL ES渲染默认渲染到当前上下文
  * EAGLContext管理所有使用OpenGL ES进行描绘的状态，命令以及资源信息，要绘制东西，必须要有上下文，跟图形上下文类似。
  * 当你创建一个EAGLContext，你要声明你要用哪个version的API。这里，我们选择OpenGL ES 2.0
    
    
	    #pragma mark - 3、创建OpenGL上下文，并且设置上下文
	    - (void)setupContext
	    {
	        // 指定OpenGL 渲染 API 的版本，目前都使用 OpenGL ES 2.0
	        EAGLRenderingAPI api = kEAGLRenderingAPIOpenGLES2;
	        // 创建EAGLContext上下文
	        _context = [[EAGLContext alloc] initWithAPI:api];
	        // 设置为当前上下文，所有的渲染默认渲染到当前上下文
	        [EAGLContext setCurrentContext:_context];
	    }

#####04-创建渲染缓冲区

  * 有了上下文，openGL还需要在一块buffer进行描绘，这块buffer就是RenderBuffer

  * OpenGLES 总共有三大不同用途的color buffer，depth buffer 和 stencil buffer.

  * 最基本的是color buffer，创建它就好了 

######函数glGenRenderbuffers

    
    
    函数 void glGenRenderbuffers (GLsizei n, GLuint* renderbuffers)

  * 它是为renderbuffer(渲染缓存)申请一个id（名字）,创建渲染缓存
  * 参数n表示申请生成renderbuffer的个数
  * 参数renderbuffers返回分配给renderbuffer(渲染缓存)的id  
。 注意：返回的id不会为0，id 0 是OpenGL ES保留的，我们也不能使用id 为0的renderbuffer(渲染缓存)。

######函数glBindRenderbuffer

    
    
     void glBindRenderbuffer (GLenum target, GLuint renderbuffer)

  * 告诉OpenGL：我在后面引用GL_RENDERBUFFER的地方，其实是引用_colorRenderBuffer
  * 参数target必须为GL_RENDERBUFFER
  * 参数renderbuffer就是使用glGenRenderbuffers生成的id  
。 当指定id的renderbuffer第一次被设置为当前renderbuffer时，会初始化该 renderbuffer对象，其初始值为：

    
    
    width 和 height：像素单位的宽和高，默认值为0；
    internal format：内部格式，三大 buffer 格式之一 -- color，depth or stencil；
    Color bit-depth：仅当内部格式为 color 时，设置颜色的 bit-depth，默认值为0；
    Depth bit-depth：仅当内部格式为 depth时，默认值为0；
    Stencil bit-depth: 仅当内部格式为 stencil，默认值为0

######函数renderbufferStorage

    
    
    EAGLContext方法 - (BOOL)renderbufferStorage:(NSUInteger)target fromDrawable:(id<EAGLDrawable>)drawable

  * 把渲染缓存(renderbuffer)绑定到渲染图层(CAEAGLLayer)上，并为它分配一个共享内存。
  * 参数target，为哪个renderbuffer分配存储空间
  * 参数drawable，绑定在哪个渲染图层，会根据渲染图层里的绘图属性生成共享内存。
    
    
        //    底层调用这个分配内存
        glRenderbufferStorage(GL_RENDERBUFFER, GL_RGBA, _openGLLayer.bounds.size.width, _openGLLayer.bounds.size.height);

#####实战代码

    
    
    #pragma mark - 4、创建渲染缓存
    - (void)setupRenderBuffer
    {
        glGenRenderbuffers(1, &_colorRenderBuffer);
        glBindRenderbuffer(GL_RENDERBUFFER, _colorRenderBuffer);
        // 把渲染缓存绑定到渲染图层上CAEAGLLayer，并为它分配一个共享内存。
        // 并且会设置渲染缓存的格式，和宽度
        [_context renderbufferStorage:GL_RENDERBUFFER fromDrawable:_openGLLayer];
    }

#####05-创建帧缓冲区

  * 它相当于buffer(color, depth, stencil)的管理者，三大buffer可以附加到一个framebuffer上

  * 本质是把framebuffer内容渲染到屏幕

######函数glFramebufferRenderbuffer

    
    
    void glFramebufferRenderbuffer (GLenum target, GLenum attachment, GLenum renderbuffertarget, GLuint renderbuffer)

  * 该函数是将相关buffer()三大buffer之一)attach到framebuffer上,就会自动把渲染缓存的内容填充到帧缓存，在由帧缓存渲染到屏幕
  * 参数target，哪个帧缓存
  * 参数attachment是指定renderbuffer被装配到那个装配点上，其值是GL_COLOR_ATTACHMENT0, GL_DEPTH_ATTACHMENT, GL_STENCIL_ATTACHMENT中的一个，分别对应 color，depth和 stencil三大buffer。
  * renderbuffertarget:哪个渲染缓存
  * renderbuffer渲染缓存id
    
    
	    #pragma mark - 5、创建帧缓冲区
	    - (void)setupFrameBuffer
	    {
	        glGenFramebuffers(1, &_framebuffers);
	        glBindFramebuffer(GL_FRAMEBUFFER, _framebuffers);
	        // 把颜色渲染缓存 添加到 帧缓存的GL_COLOR_ATTACHMENT0上,就会自动把渲染缓存的内容填充到帧缓存，在由帧缓存渲染到屏幕
	        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_RENDERBUFFER, _colorRenderBuffer);
	    }

#####06-创建着色器

######着色器

  * 什么是着色器? 通常用来处理纹理对象，并且把处理好的纹理对象渲染到帧缓存上，从而显示到屏幕上。
  * 提取纹理信息，可以处理顶点坐标空间转换，纹理色彩度调整(滤镜效果)等操作。
  * 着色器分为顶点着色器，片段着色器
    * 顶点着色器用来确定图形形状
    * 片段着色器用来确定图形渲染颜色
  * 步骤： 1.编辑着色器代码 2.创建着色器 3.编译着色器
  * 只要创建一次，可以在一开始的时候创建

######着色器代码

    
    
    // 顶点着色器代码
    NSString *const kVertexShaderString = SHADER_STRING
    (
     attribute vec4 position;
     attribute vec2 inputTextureCoordinate;
     varying vec2 textureCoordinate;
     void main()
     {
         gl_Position = position;
         textureCoordinate = inputTextureCoordinate;
     }
    );
    // 片段着色器代码
    NSString *const kYUVFullRangeConversionForLAFragmentShaderString = SHADER_STRING
    (
     varying highp vec2 textureCoordinate;
     precision mediump float;
     uniform sampler2D luminanceTexture;
     uniform sampler2D chrominanceTexture;
     uniform mediump mat3 colorConversionMatrix;
     void main()
     {
         mediump vec3 yuv;
         lowp vec3 rgb;
         yuv.x = texture2D(luminanceTexture, textureCoordinate).r;
         yuv.yz = texture2D(chrominanceTexture, textureCoordinate).ra - vec2(0.5, 0.5);
         rgb = colorConversionMatrix * yuv;
         gl_FragColor = vec4(rgb, 1);
     }
    );

######实战代码

    
    
    #pragma mark - 06、创建着色器
    - (void)setupShader
    {
        // 创建顶点着色器
        _vertShader = [self loadShader:GL_VERTEX_SHADER withString:kVertexShaderString];
        // 创建片段着色器
        _fragShader = [self loadShader:GL_FRAGMENT_SHADER withString:kYUVFullRangeConversionForLAFragmentShaderString];
    }
    // 加载着色器
    - (GLuint)loadShader:(GLenum)type withString:(NSString *)shaderString
    {
        // 创建着色器
        GLuint shader = glCreateShader(type);
        if (shader == 0) {
            NSLog(@"Error: failed to create shader.");
            return 0;
        }
        // 加载着色器源代码
        const char * shaderStringUTF8 = [shaderString UTF8String];
        glShaderSource(shader, 1, &shaderStringUTF8, NULL);
        // 编译着色器
        glCompileShader(shader);
        // 检查是否完成
        GLint compiled = 0;
        // 获取完成状态
        glGetShaderiv(shader, GL_COMPILE_STATUS, &compiled);
        if (compiled == 0) {
            // 没有完成就直接删除着色器
            glDeleteShader(shader);
            return 0;
        }
        return shader;
    }

#####07-创建着色器程序

  * 步骤： 1.创建程序 2.贴上顶点和片段着色器 3.绑定attribute属性 4.连接程序 5.绑定uniform属性 6.运行程序
  * 注意点：`第3步和第5步，绑定属性，必须有顺序，否则绑定不成功，造成黑屏`
    
    
	    #pragma mark - 7、创建着色器程序
	    - (void)setupProgram
	    {
	        // 创建着色器程序
	        _program = glCreateProgram();
	        // 绑定着色器
	        // 绑定顶点着色器
	        glAttachShader(_program, _vertShader);
	        // 绑定片段着色器
	        glAttachShader(_program, _fragShader);
	        // 绑定着色器属性,方便以后获取，以后根据角标获取
	        // 一定要在链接程序之前绑定属性,否则拿不到
	        glBindAttribLocation(_program, ATTRIB_POSITION, "position");
	        glBindAttribLocation(_program, ATTRIB_TEXCOORD, "inputTextureCoordinate");
	        // 链接程序
	        glLinkProgram(_program);
	        // 获取全局参数,注意 一定要在连接完成后才行，否则拿不到
	        _luminanceTextureAtt = glGetUniformLocation(_program, "luminanceTexture");
	        _chrominanceTextureAtt = glGetUniformLocation(_program, "chrominanceTexture");
	        _colorConversionMatrixAtt = glGetUniformLocation(_program, "colorConversionMatrix");
	        // 启动程序
	        glUseProgram(_program);
	    }

#####08-创建纹理对象

####纹理

  * 采集的是一张一张的图片，可以把图片转换为OpenGL中的纹理， 然后再把纹理画到OpenGL的上下文中
  * 什么是纹理？一个纹理其实就是一幅图像。
  * 纹理映射,我们可以把这幅图像的整体或部分贴到我们先前用顶点勾画出的物体上去.
  * 比如绘制一面砖墙，就可以用一幅真实的砖墙图像或照片作为纹理贴到一个矩形上，这样，一面逼真的砖墙就画好了。如果不用纹理映射的方法，则墙上的每一块砖都必须作为一个独立的多边形来画。另外，纹理映射能够保证在变换多边形时，多边形上的纹理图案也随之变化。
  * 纹理映射是一个相当复杂的过程，基本步骤如下：

    * 1）激活纹理单元、2）创建纹理 、3）绑定纹理 、4）设置滤波 
  * 注意：纹理映射只能在RGBA方式下执行

######函数glTexParameter

    
    
    void glTexParameter{if}[v](GLenum target,GLenum pname,TYPE param);
    {if}:表示可能是否i,f
    [v]:表示v可有可无

  * 控制滤波，滤波就是去除没用的信息，保留有用的信息
  * 一般来说，纹理图像为正方形或长方形。但当它映射到一个多边形或曲面上并变换到屏幕坐标时，纹理的单个纹素很少对应于屏幕图像上的像素。根据所用变换和所用纹理映射，屏幕上单个象素可以对应于一个纹素的一小部分（即放大）或一大批纹素（即缩小）
  * 固定写法
    
    
		/* 控制滤波 */  
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP);  
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP);

######函数glPixelStorei

    
    
     void glPixelStorei(GLenum pname, GLint param);

  * 设置像素存储方式
  * pname：像素存储方式名
  * 一种是`GL_PACK_ALIGNMENT`，用于将像素数据打包,一般用于压缩。
  * 另一种是`GL_UNPACK_ALIGNMENT`，用于将像素数据解包，一般生成纹理对象，就需要用到解包.
  * param：用于指定存储器中每个像素行有多少个字节对齐。这个数值一般是1、2、4或8，  
一般填1，一个像素对应一个字节;

######函数CVOpenGLESTextureCacheCreateTextureFromImage

    
    
    CVOpenGLESTextureCacheCreateTextureFromImage(CFAllocatorRef  _Nullable allocator, CVOpenGLESTextureCacheRef  _Nonnull textureCache, CVImageBufferRef  _Nonnull sourceImage, CFDictionaryRef  _Nullable textureAttributes, GLenum target, GLint internalFormat, GLsizei width, GLsizei height, GLenum format, GLenum type, size_t planeIndex, CVOpenGLESTextureRef  _Nullable * _Nonnull textureOut)

  * 根据图片生成纹理
  * 参数allocator kCFAllocatorDefault,默认分配内存
  * 参数textureCache 纹理缓存
  * 参数sourceImage 图片
  * 参数textureAttributes NULL
  * 参数target , GL_TEXTURE_2D(创建2维纹理对象)
  * 参数internalFormat GL_LUMINANCE，亮度格式
  * 参数width 图片宽
  * 参数height 图片高
  * 参数format GL_LUMINANCE 亮度格式
  * 参数type 图片类型 GL_UNSIGNED_BYTE
  * 参数planeIndex 0,切面角标，表示第0个切面
  * 参数textureOut 输出的纹理对象
    
        fotmat格式                    描述
	    GL_ALPHA            按照ALPHA值存储纹理单元
	    GL_LUMINANCE        按照亮度值存储纹理单元
	    GL_LUMINANCE_ALPHA    按照亮度和alpha值存储纹理单元
	    GL_RGB                按照RGB成分存储纹理单元
	    GL_RGBA                按照RGBA成分存储纹理单元

######实战代码

    
    
    #pragma mark - 7、创建纹理对象，渲染采集图片到屏幕
    - (void)setupTexture:(CMSampleBufferRef)sampleBuffer
    {
        // 获取图片信息
        CVImageBufferRef imageBufferRef = CMSampleBufferGetImageBuffer(sampleBuffer);
        // 获取图片宽度
        GLsizei bufferWidth = (GLsizei)CVPixelBufferGetWidth(imageBufferRef);
        _bufferWidth = bufferWidth;
        GLsizei bufferHeight = (GLsizei)CVPixelBufferGetHeight(imageBufferRef);
        _bufferHeight = bufferHeight;
        // 创建亮度纹理
        // 激活纹理单元0, 不激活，创建纹理会失败
        glActiveTexture(GL_TEXTURE0);
        // 创建纹理对象
        CVReturn err;
        err = CVOpenGLESTextureCacheCreateTextureFromImage(kCFAllocatorDefault, _textureCacheRef, imageBufferRef, NULL, GL_TEXTURE_2D, GL_LUMINANCE, bufferWidth, bufferHeight, GL_LUMINANCE, GL_UNSIGNED_BYTE, 0, &_luminanceTextureRef);
        if (err) {
            NSLog(@"Error at CVOpenGLESTextureCacheCreateTextureFromImage %d", err);
        }
        // 获取纹理对象
        _luminanceTexture = CVOpenGLESTextureGetName(_luminanceTextureRef);
        // 绑定纹理
        glBindTexture(GL_TEXTURE_2D, _luminanceTexture);
        // 设置纹理滤波
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
        // 激活单元1
        glActiveTexture(GL_TEXTURE1);
        // 创建色度纹理
        err = CVOpenGLESTextureCacheCreateTextureFromImage(kCFAllocatorDefault, _textureCacheRef, imageBufferRef, NULL, GL_TEXTURE_2D, GL_LUMINANCE_ALPHA, bufferWidth / 2, bufferHeight / 2, GL_LUMINANCE_ALPHA, GL_UNSIGNED_BYTE, 1, &_chrominanceTextureRef);
        if (err) {
            NSLog(@"Error at CVOpenGLESTextureCacheCreateTextureFromImage %d", err);
        }
        // 获取纹理对象
        _chrominanceTexture = CVOpenGLESTextureGetName(_chrominanceTextureRef);
        // 绑定纹理
        glBindTexture(GL_TEXTURE_2D, _chrominanceTexture);
        // 设置纹理滤波
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
    }

#####09-YUV转RGB绘制纹理

  * 纹理映射只能在RGBA方式下执行
  * 而采集的是YUV，所以需要把YUV 转换 为 RGBA，
  * 本质其实就是改下矩阵结构
  * 注意点（熬夜凌晨的bug）：`glDrawArrays如果要绘制着色器上的点和片段，必须和着色器赋值代码放在一个代码块中，否则找不到绘制的信息，就绘制不上去，造成屏幕黑屏`
  * 之前是把glDrawArrays和YUV转RGB方法分开，就一直黑屏.

######函数glUniform1i

    
    
    glUniform1i(GLint location, GLint x)

  * 指定着色器中亮度纹理对应哪一层纹理单元
  * 参数location:着色器中纹理坐标
  * 参数x：指定那一层纹理

######函数glEnableVertexAttribArray

    
    
    glEnableVertexAttribArray(GLuint index)

  * 开启顶点属性数组,只有开启顶点属性，才能给顶点属性信息赋值

######函数glVertexAttribPointer

    
    
    glVertexAttribPointer(GLuint indx, GLint size, GLenum type, GLboolean normalized, GLsizei stride, const GLvoid *ptr)

  * 设置顶点着色器属性，描述属性的基本信息
  * 参数indx：属性ID，给哪个属性描述信息
  * 参数size：顶点属性由几个值组成，这个值必须位1，2，3或4；
  * 参数type：表示属性的数据类型
  * 参数normalized:GL_FALSE表示不要将数据类型标准化
  * 参数stride 表示数组中每个元素的长度；
  * 参数ptr 表示数组的首地址

######函数glBindAttribLocation

    
    
    glBindAttribLocation(GLuint program, GLuint index, const GLchar *name)

  * 给属性绑定ID，通过ID获取属性,方便以后使用
  * 参数program 程序
  * 参数index 属性ID
  * 参数name 属性名称

######函数glDrawArrays

    
    
    glDrawArrays(GLenum mode, GLint first, GLsizei count)

  * 作用：使用当前激活的顶点着色器的顶点数据和片段着色器数据来绘制基本图形
  * mode：绘制方式 一般使用GL_TRIANGLE_STRIP，三角形绘制法
  * first：从数组中哪个顶点开始绘制，一般为0
  * count:数组中顶点数量，在定义顶点着色器的时候，就定义过了，比如vec4,表示4个顶点
  * 注意点,如果要绘制着色器上的点和片段，必须和着色器赋值代码放在一个代码块中，否则找不到绘制的信息，就绘制不上去，造成屏幕黑屏。

######实战代码

    
    
    // YUV 转 RGB，里面的顶点和片段都要转换
    - (void)convertYUVToRGBOutput
    {
        // 在创建纹理之前，有激活过纹理单元，就是那个数字.GL_TEXTURE0,GL_TEXTURE1
        // 指定着色器中亮度纹理对应哪一层纹理单元
        // 这样就会把亮度纹理，往着色器上贴
        glUniform1i(_luminanceTextureAtt, 0);
        // 指定着色器中色度纹理对应哪一层纹理单元
        glUniform1i(_chrominanceTextureAtt, 1);
        // YUV转RGB矩阵
        glUniformMatrix3fv(_colorConversionMatrixAtt, 1, GL_FALSE, _preferredConversion);
        // 计算顶点数据结构
        CGRect vertexSamplingRect = AVMakeRectWithAspectRatioInsideRect(CGSizeMake(self.bounds.size.width, self.bounds.size.height), self.layer.bounds);
        CGSize normalizedSamplingSize = CGSizeMake(0.0, 0.0);
        CGSize cropScaleAmount = CGSizeMake(vertexSamplingRect.size.width/self.layer.bounds.size.width, vertexSamplingRect.size.height/self.layer.bounds.size.height);
        if (cropScaleAmount.width > cropScaleAmount.height) {
            normalizedSamplingSize.width = 1.0;
            normalizedSamplingSize.height = cropScaleAmount.height/cropScaleAmount.width;
        }
        else {
            normalizedSamplingSize.width = 1.0;
            normalizedSamplingSize.height = cropScaleAmount.width/cropScaleAmount.height;
        }
        // 确定顶点数据结构
        GLfloat quadVertexData [] = {
            -1 * normalizedSamplingSize.width, -1 * normalizedSamplingSize.height,
            normalizedSamplingSize.width, -1 * normalizedSamplingSize.height,
            -1 * normalizedSamplingSize.width, normalizedSamplingSize.height,
            normalizedSamplingSize.width, normalizedSamplingSize.height,
        };
        // 确定纹理数据结构
        GLfloat quadTextureData[] =  { // 正常坐标
            0, 0,
            1, 0,
            0, 1,
            1, 1
        };
        // 激活ATTRIB_POSITION顶点数组
        glEnableVertexAttribArray(ATTRIB_POSITION);
        // 给ATTRIB_POSITION顶点数组赋值
        glVertexAttribPointer(ATTRIB_POSITION, 2, GL_FLOAT, 0, 0, quadVertexData);
        // 激活ATTRIB_TEXCOORD顶点数组
        glVertexAttribPointer(ATTRIB_TEXCOORD, 2, GL_FLOAT, 0, 0, quadTextureData);
        // 给ATTRIB_TEXCOORD顶点数组赋值
        glEnableVertexAttribArray(ATTRIB_TEXCOORD);
        // 渲染纹理数据,注意一定要和纹理代码放一起
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4);
    }

#####10-渲染缓冲区到屏幕

  * 注意点：`必须设置窗口尺寸glViewport`
  * 注意点：`渲染代码必须调用[EAGLContext setCurrentContext:_context]`
  * 原因：因为是多线程，每一个线程都有一个上下文，只要在一个上下文绘制就好，设置线程的上下文为我们自己的上下文,就能绘制在一起了，否则会黑屏.
  * 注意点：`每次创建纹理前，先把之前的纹理引用清空[self cleanUpTextures]，否则卡顿`

######函数glViewport

    
        glViewport(GLint x, GLint y, GLsizei width, GLsizei height)

  * 设置OpenGL渲染窗口的尺寸大小,一般跟图层尺寸一样.

  * 注意：在我们绘制之前还有一件重要的事情要做，我们必须告诉OpenGL渲染窗口的尺寸大小

######方法presentRenderbuffer

    
    
    - (BOOL)presentRenderbuffer:(NSUInteger)target

  * 是将指定renderbuffer呈现在屏幕上

######实战代码

    
    
    #pragma mark - 10.渲染帧缓存
    - (void)displayFramebuffer:(CMSampleBufferRef)sampleBuffer
    {
        // 因为是多线程，每一个线程都有一个上下文，只要在一个上下文绘制就好，设置线程的上下文为我们自己的上下文,就能绘制在一起了，否则会黑屏.
        if ([EAGLContext currentContext] != _context) {
            [EAGLContext setCurrentContext:_context];
        }
        // 清空之前的纹理，要不然每次都创建新的纹理，耗费资源，造成界面卡顿
        [self cleanUpTextures];
        // 创建纹理对象
        [self setupTexture:sampleBuffer];
        // YUV 转 RGB
        [self convertYUVToRGBOutput];
        // 设置窗口尺寸
        glViewport(0, 0, self.bounds.size.width, self.bounds.size.height);
        // 把上下文的东西渲染到屏幕上
        [_context presentRenderbuffer:GL_RENDERBUFFER];
    }

#####11-清理内存

  * 注意：`只要有Ref结尾的，都需要自己手动管理，清空`

######函数glClearColor

    
    
    glClearColor (GLclampf red, GLclampf green, GLclampf blue, GLclampfalpha)

  * 设置一个RGB颜色和透明度，接下来会用这个颜色涂满全屏.

######函数glClear

    
    
    glClear (GLbitfieldmask)

  * 用来指定要用清屏颜色来清除由mask指定的buffer，mask可以是 GL_COLOR_BUFFER_BIT，GL_DEPTH_BUFFER_BIT和GL_STENCIL_BUFFER_BIT的自由组合。
  * 在这里我们只使用到 color buffer，所以清除的就是 clolor buffer。
    
    
	    #pragma mark - 11.清理内存
	    - (void)dealloc
	    {
	        // 清空缓存
	        [self destoryRenderAndFrameBuffer];
	        // 清空纹理
	        [self cleanUpTextures];
	    }
	    #pragma mark - 销毁渲染和帧缓存
	    - (void)destoryRenderAndFrameBuffer
	    {
	        glDeleteRenderbuffers(1, &_colorRenderBuffer);
	        _colorRenderBuffer = 0;
	        glDeleteBuffers(1, &_framebuffers);
	        _framebuffers = 0;
	    }
	    // 清空纹理
	    - (void)cleanUpTextures
	    {
	        // 清空亮度引用
	        if (_luminanceTextureRef) {
	            CFRelease(_luminanceTextureRef);
	            _luminanceTextureRef = NULL;
	        }
	        // 清空色度引用
	        if (_chrominanceTextureRef) {
	            CFRelease(_chrominanceTextureRef);
	            _chrominanceTextureRef = NULL;
	        }
	        // 清空纹理缓存
	        CVOpenGLESTextureCacheFlush(_textureCacheRef, 0);
	    }

####GPUImage工作原理

  * GPUImage最关键在于GPUImageFramebuffer这个类，这个类会保存当前处理好的图片信息。
  * GPUImage是通过一个链条处理图片，每个链条通过target连接,每个target处理完图片后，会生成一个GPUImageFramebuffer对象，并且把图片信息保存到GPUImageFramebuffer。
  * 这样比如targetA处理好，要处理targetB,就会先取出targetA的图片，然后targetB在targetA的图片基础上在进行处理.

