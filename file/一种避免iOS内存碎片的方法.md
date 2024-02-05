 
<!--BEGIN_DATA
{
    "create_date": "2017-03-20 11:11", 
    "modify_date": "2017-03-20 11:11", 
    "is_top": "0", 
    "summary": "一种避免iOS内存碎片的方法", 
    "tags": "iOS", 
    "file_name": "一种避免iOS内存碎片的方法.md"
}
END_DATA-->

####<p>原文出处：<a href='http://mp.weixin.qq.com/s/dDB9DYXWiIMMKiM6I3v2qA' target='blank'>一种避免iOS内存碎片的方法</a></p>

###一、引言

在和服务器传输文本的时候，可能会因为某一个字符的编码格式不同、少了一个字节、多了一个字节等原因导致整段文本都无法解码。而实际上如果可以找到这个字符，然后替换成其他字符的话，那整段文本其他字符都是可以解码的，用户在UI上也许能猜测出正确的字符是什么，这种体验是好于用户看到一片空白。

![](./image/FVVVrab.jpg)

代码的思路是对于无法用 `initWithData:encoding:` 方法解析的数据，则逐个字节的进行解析。源码的一个分支如下：

    
    
    while(检索未超过文件长度)
    {
        if(1字节长的编码)
        {/*正确编码，继续循环*/}
        else if (2字节长的编码)
        {
            CFStringRef cfstr = CFStringCreateWithBytes(kCFAllocatorDefault, {byte1, byte2}, 2, kCFStringEncodingUTF8, false);
            if (cfstr)
            {/*正确编码，继续循环*/}
            else
            {/*替换字符*/}
        }
        else if(3,4,5,6个字节长的解码)...
    }

发现无法解析的字符后进行替换。这个方法的弊端在于 `CFStringCreateWithBytes`方法分配的字符串是堆空间，如果数据过长，则很容易产生内存碎片。

解决这个问题有两种思路：一是在栈空间分配内存，二是分配一个可以重复利用的堆空间。

###二、CFAllocatorRef的研究

从 `CFStringCreateWithBytes` 提供的参数看，调用者可以指定内存分配器。查阅官方文档对第一个参数 `CFAllocatorRefalloc` 给出的释义：The allocator to use to allocate memory for the new string. Pass NULL or kCFAllocatorDefault to use the current default allocator。接下来研究下这个内存分配器的数据结构以及系统提供的六个分配器的区别。

先看下 `CFAllocatorRef` 的数据结构：

    
    
    typedef const struct CF_BRIDGED_TYPE(id) __CFAllocator * CFAllocatorRef;
    struct __CFAllocator {
        CFRuntimeBase _base;
        CFAllocatorRef _allocator;
        CFAllocatorContext _context;
    };

只考虑iOS平台的话， `__CFAllocator` 只有三个成员。其中 `CFAllocatorContext _context`是分配器的核心，其作用是可以自定义分配和释放的回调函数：

    
    
    typedef void *        (*CFAllocatorAllocateCallBack)(CFIndex allocSize, CFOptionFlags hint, void *info);
    typedef void        (*CFAllocatorDeallocateCallBack)(void *ptr, void *info);
    typedef struct {
        ...
        CFAllocatorAllocateCallBack        allocate;
        CFAllocatorDeallocateCallBack    deallocate;
        ...
    } CFAllocatorContext;

当系统使用这个分配器进行分配，释放，重分配等操作的时候会调用相应的回调函数来执行（上面代码省略了部分回调函数，有兴趣深入了解的同学可查看CFBase.m的源码 ）。

接下来看系统为提供的一系列

分配器的源码

（只考虑iOS平台）。

  * `kCFAllocatorMalloc` ：系统的分配和释放本质就是 `malloc()` , `realloc()` , `free()` 。 
    
        static void * __CFAllocatorCPPMalloc(CFIndex allocSize, CFOptionFlags hint, void *info)
    	{return malloc(allocSize);    }
    	
    	static void __CFAllocatorCPPFree(void *ptr, void *info)
    	{free(ptr);}

  * `kCFAllocatorMallocZone` :看源码这个分配器在iOS上和 `kCFAllocatorMalloc` 是一样的，但在Mac的操作系统上是有区别的（malloc和malloc_zone_malloc）。 

  * `kCFAllocatorNull` :其实什么都不会做，直接返回NULL。看文档说明主要是用于在释放的时候内存实际上不应该被释放。 
    
        static void *__CFAllocatorNullAllocate(CFIndex size, CFOptionFlags hint, void *info)
    	{ return NULL;}

  * `kCFAllocatorUseContext` :是一个固定的地址，它只用于 `CFAllocatorCreate()` 创建分配器的时候。表示创建分配器时使用自身的 `context->allocate` 方法来分配内存。因为分配器也是一个CF对象。 
    
        const CFAllocatorRef kCFAllocatorUseContext = (CFAllocatorRef)0x03ab;

  * `kCFAllocatorDefault` :这个是取系统当前的默认分配器，这个需要结合另外两个API来理。解： `CFAllocatorGetDefault` 和 `CFAllocatorSetDefault` 方法。（ 源码 中set方法有一段有意思的注释：系统retain了两次allocator，目的是为了在设置默认分配器的时候，之前的默认分配器不会释放。那这里不是会造成内存泄漏了吗？觉得要慎用）。 

  * `kCFAllocatorSystemDefault` :这个才是系统级别的默认分配器，如果不调用 `CFAllocatorSetDefault()` ，则用 `CFAllocatorGetDefault()` 取出的分配器就是这个。从源码来看，目前和 `kCFAllocatorMalloc` 没区别（也许很久之前因为 `__CFAllocatorSystemAllocate` 不是用malloc实现的。后来兼容了，这里的故事有知道的欢迎告知） 

###三、自定义分配器

看完系统提供的分配器后发现都是在堆空间分配内存，没有合适的。后发现系统提供了另外一个API： `CFAllocatorCreate`。这时可以考虑自定义一个分配器，分配器在分配内存的时候，返回一块固定大小的内存重复使用。

    
    
    void *customAlloc(CFIndex size, CFOptionFlags hint, void *info)
    {
        return info;
    }
    void *customRealloc(void *ptr, CFIndex newsize, CFOptionFlags hint, void *info)
    {
        NSLog(@"警告:发生了内存重新分配");
        return NULL;//不写这个回调系统也是返回NULL的。这里简单的打句log。
    }
    void customDealloc(void *ptr, void *info)
    {
        //因为alloc的地址是外部传来的，所以应该由外部来管理，这里不要释放
    }
    CFAllocatorRef customAllocator(void *address)
    {
        CFAllocatorRef allocator = NULL;
        if (NULL == allocator)
        {
            CFAllocatorContext context = {0, NULL, NULL, NULL, NULL, customAlloc, customRealloc, customDealloc, NULL};
            context.info = address;
            allocator = CFAllocatorCreate(kCFAllocatorSystemDefault, &context);
        }
        return allocator;
    }
    int main()
    {
        char allocAddress[160] = {0};
        CFAllocatorRef allocator = customAllocator(allocAddress);
        CFStringRef cfstr = CFStringCreateWithBytes(allocator, tuple, 2, kCFStringEncodingUTF8, false);
        if (cfstr)
        {
             //CFRelease(cfstr);//这里不要释放，这里分配的内存是allocAddress的栈空间，由系统自己自己回收就好
        }
        CFAllocatorDeallocate(kCFAllocatorSystemDefault, (void *)allocator);
    }

这里用了一个技巧是重复使用的内存首地址利用context的info来传递。allocAddress的大小为什么是160个字节呢？这个大小只要取
`CFStringRef` 需要的最大长度就可以了。如果自己项目需要引用这个方法，需要考虑这个size需要设置多大。（取决于`CFStringCreateWithBytes()` 的 `numBytes` 参数值，这里会有字节对齐的知识）。

创建的CFAllocatorRef也是在堆空间上，它也需要被释放。系统同样提供了释放API： `CFAllocatorDeallocate`。这里需要注意dealloc的allocator需要和create时是同一个allocator。否则无法释放，造成内存泄漏。

###四、结语

自定义分配器让我们对内存的分配拥有了一定的可操作性，文中的应用场景是在创建对象时返回一块固定的内存区域重复使用，避免了重复创建和释放导致的内存碎片问题。这种可操作性相信以后在解决内存方面问题时会为你多提供一种解决方案。

CFBase的源码 最近一次更新是2015.9.11日。这份源码最新也是基于iOS9的。在写这种底层代码的时候需要格外小心，作者在写的时候因为`CFAllocatorCreate` 和 `CFAllocatorDeallocate`的allocator参数传的不同，导致内存泄漏，需要多多测试。发布到外网的时候需要加上灰度策略以及开关控制。

最后分享一个额外小知识，iOS线程的默认栈空间大小是512KB（这个在苹果出了新系统和新机器后可能会变大，所以使用的时候尽量多测试）。这里踩过坑， 程序源码
中orignalBytes一开始是临时变量，分配在栈上，但是由于字符串太长，导致栈溢出crash，所以后面分配在堆上了。

###参考链接

1. https://github.com/opensource-apple/CF

2. https://gist.github.com/oleganza/781772

3. https://developer.apple.com/library/prerelease/content/documentation/CoreFoundation/Conceptual/CFMemoryMgmt/Tasks/CustomAllocators.html

4. https://developer.apple.com/library/prerelease/content/qa/qa1419/_index.html

