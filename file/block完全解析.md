<!--BEGIN_DATA
{
    "create_date": "2016-01-25 16:19", 
    "modify_date": "2016-01-25 16:19", 
    "is_top": "0", 
    "summary": "block完全解析", 
    "tags": "iOS", 
    "file_name": "block完全解析.md"
}
END_DATA-->


[http://www.cnblogs.com/biosli/archive/2013/05/29/iOS_Objective-C_Block.html](http://www.cnblogs.com/biosli/archive/2013/05/29/iOS_Objective-C_Block.html)

1、block是个什么？
简单说block就是一个“仿”对象。

在Objective-C中，类都是继承NSObject的，NSObject里面都会有个isa，是一个objc_class指针。
而block的对象，在clang的C++重写中，

^int(){printf("val"); return 111;};
这个block会被转化为

```
struct __block_impl {
  void *isa;
  int Flags;
  int Reserved;
  void *FuncPtr;
};

struct __testBlock_block_impl_0 {
  struct __block_impl impl;
  struct __testBlock_block_desc_0* Desc;
  __testBlock_block_impl_0(void *fp, struct __testBlock_block_desc_0 *desc, int flags=0) {
    impl.isa = &_NSConcreteStackBlock;
    impl.Flags = flags;
    impl.FuncPtr = fp;
    Desc = desc;
  }
};
```

____testBlock_block_impl_0是block结构，他的第一个属性也是一个结构__block_impl，而第一个参数也是一个isa的指针。

在运行时，NSObject和block的isa指针都是指向在对象一个4字节。

NSObject及派生类对象的isa指向Class的prototype，而block的isa指向了_NSConcreteStackBlock这个指针。

就是说当一个block被声明的时候他都是一个_NSConcreteStackBlock类的对象。

2、block对象的生存期

通常在Objective-C中，对象都是在堆上声明的。
当我们运行

	NSString *str = [[NSString alloc] init];

的时候，这个NSString就在堆上挂上号了，直到release的时候，引用计数减为0，这个对象才会被干掉。

再看一下block的内部实现，当我们实现

    {
        void (^testBlock) (void) =  ^{printf("看看这个block");};
        testBlock();
    }
的时候，在clang中会被转换为

    {
        void (*testBlock) (void) = (void (*)())&__main_block_impl_0((void *)__main_block_func_0, &__main_block_desc_0_DATA);
        ((void (*)(__block_impl *))((__block_impl *)testBlock)->FuncPtr)((__block_impl *)testBlock);
    }
 由此可见这个block是在栈上声明的，这就是说当block超过了这个“}”，这个block对象就会被回收。

我们做个实验：
Objective-C的源码（非ARC）

    block stackBlock;
    {
        int val = 10;
        stackBlock = ^{NSLog(@"val = %d", val);};
    }
    stackBlock();
转换后：

    block stackBlock;
    {
        int val = 10;
        stackBlock = (void (*)())&__main_block_impl_0((void *)__main_block_func_0, &__main_block_desc_0_DATA, val);
    }
    ((void (*)(__block_impl *))((__block_impl *)stackBlock)->FuncPtr)((__block_impl *)stackBlock);
    
上面的程序运行，不崩溃。

从这个转换后的结果来看，__main_block_impl_0这个在栈上声明的对象，在“}”结束应该就被释放了，可是在下面的调用中居然还可以用？

我认为这就是运气，个人不推荐在栈释放block对象后再使用block对象。

看看__main_block_impl_0的声明

```
struct __main_block_impl_0 {
  struct __block_impl impl;
  struct __main_block_desc_0* Desc;
  int val;
  __main_block_impl_0(void *fp, struct __main_block_desc_0 *desc, int _val, int flags=0) : val(_val) {
    impl.isa = &_NSConcreteStackBlock;
    impl.Flags = flags;
    impl.FuncPtr = fp;
    Desc = desc;
  }
};
```

这个结构只做了构造函数，没有做析构函数，导致在对象弹栈的时候没有对对象内部变量赋值，所以飘在外面的地址都是野指针。
（注：clang这个命令不是全靠谱，只能作为参考，因为这个工具转换出来的C++文件无法通过编译，感觉只能作为研究参考）

3、block外传、赋值得上栈
咱们看看运气不好的时候：
准备工作，弄个新的iOS工程（非ARC的），然后在ViewController.m里定义一个blk类型。

typedef void (^blk) (void);
之后在弄个属性

@interface ViewController () {
      blk tempBlock;
}
@end
在viewDidLoad里面加上一个按钮，并声明一个block指针付给tempBlock

```
- (void)viewDidLoad
{
    [superviewDidLoad];
// Do any additional setup after loading the view, typically from a nib.
    
    UIButton *btn = [UIButton buttonWithType: UIButtonTypeRoundedRect];
    btn.frame = CGRectMake(100.0f, 100.0f, 100.0f, 30.0f);
    [btn setTitle: @"试试"forState: UIControlStateNormal];
    [btn addTarget: self
            action: @selector(btnClick:)
  forControlEvents:UIControlEventTouchUpInside];
    [self.viewaddSubview: btn];
    
    __blockint val = 10;
    tempBlock = ^{NSLog(@"val = %d", ++val);};
}
```


按钮点击的事件：

```
- (void) btnClick: (id) Sender {
    tempBlock();
}
```

当页面正常显示之后，点击按钮必然崩溃。

提示error: address doesn't contain a section that points to a section in a object file
原因就是tempBlock所指向的对象已经被回收了。

在Objective-C中，这种情况也可能是tempBlock所指的对象被autorelease了？

这样咱们吧tempBlock给retain一下不就好了么？

	tempBlock = [^{NSLog(@"val = %d", ++val);} retain];

结果依旧，可问题出在哪呢？

我认为这就是block是一个“仿”对象的造成的，从之前的分析来看，block的isa指向的不是object_class，而是_NSConcreteStackBlock，我想这个prototype里重新定义了咱们熟悉的retain/copy/release等NSObject所定义的函数。

retain这个函数在_NSConcreteStackBlock这个类的定义中，不会对指针做任何操作，所以才不会有影响。（同样release也是一样）

在block的各种使用说明中，都有一条，当block要作为参数外传、赋值时都要调用copy，咱们对比一下copy前后block的变化。

把刚才的实验改造一下：

```
- (void)viewDidLoad
{
    [superviewDidLoad];

     //生成按钮(略)
    
    NSLog(@"_NSConcreteStackBlock %@", [_NSConcreteStackBlock class]);
    
    __block int val = 10;
    blk stackBlock = ^{NSLog(@"val = %d", ++val);};
    NSLog(@"stackBlock: %@", stackBlock);
    
    tempBlock = [stackBlock copy];
    NSLog(@"tempBlock: %@", tempBlock);
}
```
打印出的结果：

```
2013-05-29 14:21:09.969 BlockTest[2070:c07] _NSConcreteStackBlock __NSStackBlock__
2013-05-29 14:21:09.970 BlockTest[2070:c07] stackBlock: <__NSStackBlock__: 0xbfffdb28>
2013-05-29 14:21:09.970 BlockTest[2070:c07] tempBlock: <__NSMallocBlock__: 0x756bf20>
```
在经过copy之后，对象的类型从____NSStackBlock____变为了____NSMallocBlock____
在Objective-C的设计中，我没见过copy一回把对象的类型也给变了的，再次说明了block是一种特殊的对象。
大家应该注意到__block标记的变量了吧，这个变量会随着block对象上堆一块上堆，这个部分上面的blogs和书中都有讲解，我就不叙述了。

另外还有一种类型block的类型____NSGlobalBlock____，当block里面没有局部变量的时候会block会变为这个类型,这个类型的retain/copy/release全都不会对对象有影响，可以当做静态block理解。
____NSMallocBlock____对象再次copy，不会再产生新的对象而是对原有对象进行retain。
经过实验几个block类型的retain/copy/release的功能如下（非ARC环境）：

![](http://images.cnitblog.com/blog/31852/201305/29164119-4b0cf81e787c4da2a288695afcf2f865.png)

4、事情还没完

当一个block对象上堆了，他的声明周期就和一个普通的NSObject对象的方法一样了（这个应该是____NSMallocBlock____这个类的设计参考了NSObject对象的设计）
作为一个合格的Objective-C程序员，见到copy应该就想到release。

在非ARC环境下，copy了block后一定要在使用后release，不然会有内存泄露，而且泄露点是在系统级，在Instruments里跟不到问题触发点，比较上火。


我在这里想探讨的另外一个问题是设计原则，对于一个对象，当外传的时候我们都会想着把对象autorelease掉，比如：

```
- (NSArray *) myTestArray {
    NSArray *array = [[NSArray alloc] initWithObjects: @"a", @"b", @"c", nil];
    return [array autorelease];
}
```
同样，我们在向外传递block的时候一定也要做到，传给外面一个在堆上的，autorelease的对象。

```
- (blk) myTestBlock {
    __blockint val = 10;
    blk stackBlock = ^{NSLog(@"val = %d", ++val);};
    return [[stackBlock copy] autorelease];
}
```
第一步，copy将block上从栈放到堆上，第二步，autorelease防止内存泄露。

同样，有时我们会去将block放到别的类中做回调，如放到AFNetworking中的回调。
这时根据统一的设计原则，我们也应该给调用对象一个堆上的autorelease的对象。

总之，在把block对象外传的时候，我们要传出一个经过copy，再autorelease的block在堆上的__NSMallocBlock__对象。（个人观点，block是模仿NSObject对象发明的，就不要让调用方做与其他对象不一样的事）

5、说说ARC
上面的这些方法，说的都是非ARC编程的时候的注意事项，在ARC下很多规则都可以省略了。
因为在ARC下有个原则，只要block在strong指针底下过一道都会放到堆上。
看下面这个实验：


    {
        __blockint val = 10;
        __strong blk strongPointerBlock = ^{NSLog(@"val = %d", ++val);};
        NSLog(@"strongPointerBlock: %@", strongPointerBlock); //1
        
        __weak blk weakPointerBlock = ^{NSLog(@"val = %d", ++val);};
        NSLog(@"weakPointerBlock: %@", weakPointerBlock); //2
        
        NSLog(@"mallocBlock: %@", [weakPointerBlock copy]); //3
        
        NSLog(@"test %@", ^{NSLog(@"val = %d", ++val);}); //4
    }

得到的日志

```
2013-05-29 16:03:58.773 BlockTest[3482:c07] strongPointerBlock: <__NSMallocBlock__: 0x7625120>
2013-05-29 16:03:58.776 BlockTest[3482:c07] weakPointerBlock: <__NSStackBlock__: 0xbfffdb30>
2013-05-29 16:03:58.776 BlockTest[3482:c07] mallocBlock: <__NSMallocBlock__: 0x714ce60>
2013-05-29 16:03:58.777 BlockTest[3482:c07] test <__NSStackBlock__: 0xbfffdb18>
```

分析一下：
strong指针指向的block已经放到堆上了。
weak指针指向的block还在栈上（这种声明方法只在block上有效，正常的weak指针指向堆上对象，直接就会变nil，需要用strong指针过一道，请参考ARC的指针使用注意事项）
第三行日志同非ARC一样，会将block从栈移动到堆上。
最后一行日志，说明在单独声明block的时候，block还是会在栈上的。

在ARC下的另外一种情况，将block作为参数返回

```
- (__unsafe_unretained blk) blockTest {
    int val = 11;
    return ^{NSLog(@"val = %d", val);};
}
```

调用方

	NSLog(@"block return from function: %@", [self blockTest]);

得到的日志：

```
2013-05-29 16:09:59.489 BlockTest[3597:c07] block return from function: <__NSMallocBlock__: 0x7685640>
```

分析一下：

在ARC环境下，当block作为参数返回的时候，block也会自动被移到堆上。

在ARC下，只要指针过一下strong指针，或者由函数返回都会把block移动到堆上。
所以在将block传给回调方之前过一下strong指针，就可以满足我刚才阐述的设计原则。

总结：

上面的文字介绍了：
1、block在Objective-C环境下的结构

     block是一个“仿”对象
     
2、block声明的生存期

     栈上声明对象是会被回收的，如果要长期持有block对象请把她移到堆上
     
3、从栈到堆的转换时机

     栈上的block什么时候会在执行copy的时候移动到堆上，block可以有三种类型
     
4、我个人理解的一些设计准则

     给调用方一个堆上的，被autorelease的block对象。
     
5、在ARC下的一些注意事项

     过一下strong指针，他好，我也好。




[http://blog.devtang.com/blog/2013/07/28/a-look-inside-blocks/](http://blog.devtang.com/blog/2013/07/28/a-look-inside-blocks/)


###前言

这里 有关于 block 的 5 道测试题，建议你阅读本文之前先做一下测试。

先介绍一下什么是闭包。在 wikipedia 上，闭包的定义) 是:

>In programming languages, a closure is a function or reference to a function together with a referencing environment—a table storing a reference to each of the non-local variables (also called free variables or upvalues) of that function.

翻译过来，闭包是一个函数（或指向函数的指针），再加上该函数执行的外部的上下文变量（有时候也称作自由变量）。

block 实际上就是 Objective-C 语言对于闭包的实现。 block 配合上 dispatch_queue，可以方便地实现简单的多线程编程和异步编程，关于这个，我之前写过一篇文章介绍：《使用 GCD》。

本文主要介绍 Objective-C 语言的 block 在编译器中的实现方式。主要包括：

block 的内部实现数据结构介绍
block 的三种类型及其相关的内存管理方式
block 如何通过 capture 变量来达到访问函数外的变量
实现方式

数据结构定义

block 的数据结构定义如下（图片来自 这里)：

![http://blog.devtang.com/images/block-struct.jpg](http://blog.devtang.com/images/block-struct.jpg)


对应的结构体定义如下：

```
struct Block_descriptor {
    unsigned long int reserved;
    unsigned long int size;
    void (*copy)(void *dst, void *src);
    void (*dispose)(void *);
};

struct Block_layout {
    void *isa;
    int flags;
    int reserved;
    void (*invoke)(void *, ...);
    struct Block_descriptor *descriptor;
    /* Imported variables. */
};
```

通过该图，我们可以知道，一个 block 实例实际上由 6 部分构成：

isa 指针，所有对象都有该指针，用于实现对象相关的功能。

flags，用于按 bit 位表示一些 block 的附加信息，本文后面介绍 block copy 的实现代码可以看到对该变量的使用。

reserved，保留变量。

invoke，函数指针，指向具体的 block 实现的函数调用地址。

descriptor， 表示该 block 的附加描述信息，主要是 size 大小，以及 copy 和 dispose 函数的指针。

variables，capture 过来的变量，block 能够访问它外部的局部变量，就是因为将这些变量（或变量的地址）复制到了结构体中。

该数据结构和后面的 clang 分析出来的结构实际是一样的，不过仅是结构体的嵌套方式不一样。但这一点我一开始没有想明白，所以也给大家解释一下，如下 2 个结构体 SampleA 和 SampleB 在内存上是完全一样的，原因是结构体本身并不带有任何额外的附加信息。

```
struct SampleA {
    int a;
    int b;
    int c;
};

struct SampleB {
    int a;
    struct Part1 {
        int b;
    };
    struct Part2 {
        int c;
    };
};
```

在 Objective-C 语言中，一共有 3 种类型的 block：

_NSConcreteGlobalBlock 全局的静态 block，不会访问任何外部变量。
_NSConcreteStackBlock 保存在栈中的 block，当函数返回时会被销毁。
_NSConcreteMallocBlock 保存在堆中的 block，当引用计数为 0 时会被销毁。
我们在下面会分别来查看它们各自的实现方式上的差别。

###研究工具：clang

为了研究编译器是如何实现 block 的，我们需要使用 clang。clang 提供一个命令，可以将 Objetive-C 的源码改写成 c 语言的，借此可以研究 block 具体的源码实现方式。该命令是

	clang -rewrite-objc block.c

###NSConcreteGlobalBlock 类型的 block 的实现

我们先新建一个名为 block1.c 的源文件：

```
#include <stdio.h>

int main()
{
    ^{ printf("Hello, World!\n"); } ();
    return 0;
}
```

然后在命令行中输入clang -rewrite-objc block1.c即可在目录中看到 clang 输出了一个名为 block1.cpp 的文件。该文件就是 block 在 c 语言实现，我将 block1.cpp 中一些无关的代码去掉，将关键代码引用如下：

```
struct __block_impl {
    void *isa;
    int Flags;
    int Reserved;
    void *FuncPtr;
};

struct __main_block_impl_0 {
    struct __block_impl impl;
    struct __main_block_desc_0* Desc;
    __main_block_impl_0(void *fp, struct __main_block_desc_0 *desc, int flags=0) {
        impl.isa = &_NSConcreteStackBlock;
        impl.Flags = flags;
        impl.FuncPtr = fp;
        Desc = desc;
    }
};
static void __main_block_func_0(struct __main_block_impl_0 *__cself) {
    printf("Hello, World!\n");
}

static struct __main_block_desc_0 {
    size_t reserved;
    size_t Block_size;
} __main_block_desc_0_DATA = { 0, sizeof(struct __main_block_impl_0) };

int main()
{
    (void (*)())&__main_block_impl_0((void *)__main_block_func_0, &__main_block_desc_0_DATA) ();
    return 0;
}
```

下面我们就具体看一下是如何实现的。__main_block_impl_0 就是该 block 的实现，从中我们可以看出：

一个 block 实际是一个对象，它主要由一个 isa 和 一个 impl 和 一个 descriptor 组成。

在本例中，isa 指向 _NSConcreteGlobalBlock， 主要是为了实现对象的所有特性，在此我们就不展开讨论了。

由于 clang 改写的具体实现方式和 LLVM 不太一样，并且这里没有开启 ARC。所以这里我们看到 isa 指向的还是_NSConcreteStackBlock。但在 LLVM 的实现中，开启 ARC 时，block 应该是 _NSConcreteGlobalBlock 类型，具体可以看 [《objective-c-blocks-quiz》](http://blog.parse.com/2013/02/05/objective-c-blocks-quiz/) 第二题的解释。

impl 是实际的函数指针，本例中，它指向 __main_block_func_0。这里的 impl 相当于之前提到的 invoke 变量，只是 clang 编译器对变量的命名不一样而已。

descriptor 是用于描述当前这个 block 的附加信息的，包括结构体的大小，需要 capture 和 dispose 的变量列表等。结构体大小需要保存是因为，每个 block 因为会 capture 一些变量，这些变量会加到 __main_block_impl_0 这个结构体中，使其体积变大。在该例子中我们还看不到相关 capture 的代码，后面将会看到。

NSConcreteStackBlock 类型的 block 的实现

我们另外新建一个名为 block2.c 的文件，输入以下内容：

```
#include <stdio.h>

int main() {
    int a = 100;
    void (^block2)(void) = ^{
        printf("%d\n", a);
    };
    block2();

    return 0;
}
```

用之前提到的 clang 工具，转换后的关键代码如下：

```
struct __main_block_impl_0 {
    struct __block_impl impl;
    struct __main_block_desc_0* Desc;
    int a;
    __main_block_impl_0(void *fp, struct __main_block_desc_0 *desc, int _a, int flags=0) : a(_a) {
        impl.isa = &_NSConcreteStackBlock;
        impl.Flags = flags;
        impl.FuncPtr = fp;
        Desc = desc;
    }
};
static void __main_block_func_0(struct __main_block_impl_0 *__cself) {
    int a = __cself->a; // bound by copy
    printf("%d\n", a);
}

static struct __main_block_desc_0 {
    size_t reserved;
    size_t Block_size;
} __main_block_desc_0_DATA = { 0, sizeof(struct __main_block_impl_0)};

int main()
{
    int a = 100;
    void (*block2)(void) = (void (*)())&__main_block_impl_0((void *)__main_block_func_0, &__main_block_desc_0_DATA, a);
    ((void (*)(__block_impl *))((__block_impl *)block2)->FuncPtr)((__block_impl *)block2);

    return 0;
}
```

在本例中，我们可以看到：

本例中，isa 指向 _NSConcreteStackBlock，说明这是一个分配在栈上的实例。
main_block_impl_0 中增加了一个变量 a，在 block 中引用的变量 a 实际是在申明 block 时，被复制到 main_block_impl_0 结构体中的那个变量 a。因为这样，我们就能理解，在 block 内部修改变量 a 的内容，不会影响外部的实际变量 a。
main_block_impl_0 中由于增加了一个变量 a，所以结构体的大小变大了，该结构体大小被写在了 main_block_desc_0 中。
我们修改上面的源码，在变量前面增加 __block 关键字：

```
#include <stdio.h>

int main()
{
    __block int i = 1024;
    void (^block1)(void) = ^{
        printf("%d\n", i);
        i = 1023;
    };
    block1();
    return 0;
}
```

生成的关键代码如下，可以看到，差异相当大：

```
struct __Block_byref_i_0 {
    void *__isa;
    __Block_byref_i_0 *__forwarding;
    int __flags;
    int __size;
    int i;
};

struct __main_block_impl_0 {
    struct __block_impl impl;
    struct __main_block_desc_0* Desc;
    __Block_byref_i_0 *i; // by ref
    __main_block_impl_0(void *fp, struct __main_block_desc_0 *desc, __Block_byref_i_0 *_i, int flags=0) : i(_i->__forwarding) {
        impl.isa = &_NSConcreteStackBlock;
        impl.Flags = flags;
        impl.FuncPtr = fp;
        Desc = desc;
    }
};
static void __main_block_func_0(struct __main_block_impl_0 *__cself) {
    __Block_byref_i_0 *i = __cself->i; // bound by ref

    printf("%d\n", (i->__forwarding->i));
    (i->__forwarding->i) = 1023;
}

static void __main_block_copy_0(struct __main_block_impl_0*dst, struct __main_block_impl_0*src) {_Block_object_assign((void*)&dst->i, (void*)src->i, 8/*BLOCK_FIELD_IS_BYREF*/);}

static void __main_block_dispose_0(struct __main_block_impl_0*src) {_Block_object_dispose((void*)src->i, 8/*BLOCK_FIELD_IS_BYREF*/);}

static struct __main_block_desc_0 {
    size_t reserved;
    size_t Block_size;
    void (*copy)(struct __main_block_impl_0*, struct __main_block_impl_0*);
    void (*dispose)(struct __main_block_impl_0*);
} __main_block_desc_0_DATA = { 0, sizeof(struct __main_block_impl_0), __main_block_copy_0, __main_block_dispose_0};

int main()
{
    __attribute__((__blocks__(byref))) __Block_byref_i_0 i = {(void*)0,(__Block_byref_i_0 *)&i, 0, sizeof(__Block_byref_i_0), 1024};
    void (*block1)(void) = (void (*)())&__main_block_impl_0((void *)__main_block_func_0, &__main_block_desc_0_DATA, (__Block_byref_i_0 *)&i, 570425344);
    ((void (*)(__block_impl *))((__block_impl *)block1)->FuncPtr)((__block_impl *)block1);
    return 0;
}
```

从代码中我们可以看到：

源码中增加一个名为 __Block_byref_i_0 的结构体，用来保存我们要 capture 并且修改的变量 i。
main_block_impl_0 中引用的是 Block_byref_i_0 的结构体指针，这样就可以达到修改外部变量的作用。
__Block_byref_i_0 结构体中带有 isa，说明它也是一个对象。
我们需要负责 Block_byref_i_0 结构体相关的内存管理，所以 main_block_desc_0 中增加了 copy 和 dispose 函数指针，对于在调用前后修改相应变量的引用计数。
NSConcreteMallocBlock 类型的 block 的实现

NSConcreteMallocBlock 类型的 block 通常不会在源码中直接出现，因为默认它是当一个 block 被 copy 的时候，才会将这个 block 复制到堆中。以下是一个 block 被 copy 时的示例代码 (来自 这里)，可以看到，在第 8 步，目标的 block 类型被修改为 _NSConcreteMallocBlock。

```
static void *_Block_copy_internal(const void *arg, const int flags) {
    struct Block_layout *aBlock;
    const bool wantsOne = (WANTS_ONE & flags) == WANTS_ONE;

    // 1
    if (!arg) return NULL;

    // 2
    aBlock = (struct Block_layout *)arg;

    // 3
    if (aBlock->flags & BLOCK_NEEDS_FREE) {
        // latches on high
        latching_incr_int(&aBlock->flags);
        return aBlock;
    }

    // 4
    else if (aBlock->flags & BLOCK_IS_GLOBAL) {
        return aBlock;
    }

    // 5
    struct Block_layout *result = malloc(aBlock->descriptor->size);
    if (!result) return (void *)0;

    // 6
    memmove(result, aBlock, aBlock->descriptor->size); // bitcopy first

    // 7
    result->flags &= ~(BLOCK_REFCOUNT_MASK);    // XXX not needed
    result->flags |= BLOCK_NEEDS_FREE | 1;

    // 8
    result->isa = _NSConcreteMallocBlock;

    // 9
    if (result->flags & BLOCK_HAS_COPY_DISPOSE) {
        (*aBlock->descriptor->copy)(result, aBlock); // do fixup
    }

    return result;
}
```

###变量的复制

对于 block 外的变量引用，block 默认是将其复制到其数据结构中来实现访问的，如下图所示（图片来自 这里）：

![http://blog.devtang.com/images/block-capture-1.jpg](http://blog.devtang.com/images/block-capture-1.jpg)

对于用 __block 修饰的外部变量引用，block 是复制其引用地址来实现访问的，如下图所示（图片来自 这里）：

![http://blog.devtang.com/images/block-capture-2.jpg](http://blog.devtang.com/images/block-capture-2.jpg)


###LLVM 源码

在 LLVM 开源的关于 block 的实现源码，其内容也和我们用 clang 改写得到的内容相似，印证了我们对于 block 内部数据结构的推测。

ARC 对 block 类型的影响

在 ARC 开启的情况下，将只会有 NSConcreteGlobalBlock 和 NSConcreteMallocBlock 类型的 block。

原本的 NSConcreteStackBlock 的 block 会被 NSConcreteMallocBlock 类型的 block 替代。证明方式是以下代码在 XCode 中，会输出 <__NSMallocBlock__: 0x100109960>。在苹果的 官方文档 中也提到，当把栈中的 block 返回时，不需要调用 copy 方法了。

```
#import <Foundation/Foundation.h>

int main(int argc, const char * argv[])
{
    @autoreleasepool {
        int i = 1024;
        void (^block1)(void) = ^{
            printf("%d\n", i);
        };
        block1();
        NSLog(@"%@", block1);
    }
    return 0;
}
```

我个人认为这么做的原因是，由于 ARC 已经能很好地处理对象的生命周期的管理，这样所有对象都放到堆上管理，对于编译器实现来说，会比较方便。


