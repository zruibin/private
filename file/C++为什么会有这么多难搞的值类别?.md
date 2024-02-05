
<!--BEGIN_DATA
{
    "create_date": "2023-03-08 13:00", 
    "modify_date": "2023-03-08 13:00", 
    "is_top": "0", 
    "summary": "C++为什么会有这么多难搞的值类别?", 
    "tags": "C/C++", 
    "file_name": "C++为什么会有这么多难搞的值类别?.md"
}
END_DATA-->

#### <p>原文出处：<a href='https://km.woa.com/articles/show/571251' target='blank'>C++为什么会有这么多难搞的值类别?</a></p>

## 前言

相信大家在写C++的时候一定会经常讨论到「左值」「右值」「将亡值」等等的概念，在笔者的其他系列文章中也反复提及这几个概念，再加上一些「右值引用」「移动语义」等等这些概念的出现，说一点都不晕那一定是骗人的。

很多人都在吐槽C++，为什么要设计的这样复杂？就一个程序语言，还能搞出这么多值类别来？（话说可能自然语言都不见得有这么复杂吧……），那么这篇我们就来详细研究一下，为什么要专门定义这样的值类型，以及在这个过程中笔者自己的思考。

=====提示===（防杠）=====

中间篇幅得出的一些「临时结论」只是依据现有现象总结出来的，可能会跟最终结论有冲突，如果有读者有疑问，请先向后看，后面可能会颠覆这个临时结论

========================

## 一些吐槽

不得不吐槽一下，笔者认为，C++之所以复杂，C语言是原罪。因为C++一开始设计的目的，就是为给C来进行语法扩充的。因此，C++的设计方式和其他语言会有一些不同。

一般设计一门程序语言，应该是先设计一套语言体系，我希望这个语言提供哪些语法、哪些功能。之后再去根据这套理论体系来设计编译器，也就是说对于每一种语法如何解析，如何进行汇编。

但C++是不同的，因为在设计C++的语言体系的时候，就已经有完整的C语言了。因此，C++的语言体系建立其实是在C的语言体系、编译器实现以及标准库等这些之上，又重新建立的。所以说C++从设计之初，就决定了它没办法甩开C的缺陷。很多问题都是为了解决一个问题又不得不引入另一个问题，不断「找补」导致的。今天要细说的C++值类别（Value Category）就是其中非常有代表性的一个。

所以要想解释清为什么会有这些概念，我们就要从C语言开始，去猜测和体会C++设计者的初衷，遇到的问题以及「找补」的手段，这样才能真正理解这些概念是如何诞生的。

##  正式开始解释

### 从C语言开始讲起

在C语言当中其实并没有什么「左右值」之类的概念，单从值的角度来说C语言仅仅在意的是「可变量」和「不可变量」。但C更关心的是，数据存在哪里，首先是内存还是寄存器？为了区分「内存变量」还是「寄存器变量」，从而诞生了register和auto关键字（用register修饰的要放在寄存器中，auto修饰的由编译器来决定放在哪里，没有修饰符的要放在内存中）。

之后，即便是内存也要再继续细致划分，C把内存划分为4大区域，分别是全局区、静态区、堆区和栈区。而「栈区」主要依赖于函数（我觉得这个地方翻译成「存储过程」可能更合适），在C语言的视角来看，每一个程序就是一个过程（主函数），而这个过程执行的途中，会有很多子过程（其他函数），一个程序就是若干过程嵌套拼接和组合的结果。这其实也就是C语言「面向过程」的原因，因为它就是这样来设计的。从C语言衍生出的C++、OC、Go等其实都没有逃过这个设计框架。以OC为例，别看OC是面向对象的，但它仍然可以过程式开发，它的程序入口也是主函数，这个切入点来看它还是面相过程的，只是在执行这个过程中，衍生出了面向对象的操作。（这里就不详细展开了。）

那么以C语言的视角来看，一个函数其实就是一个过程，所以这个过程应该就需要相对独立的数据区域，仅仅在这个过程中生效，当过程结束，那这些数据也就不需要了。这就是函数的栈区的目的，我们管在栈区中的变量称作「局部变量」。

虽然栈区把不同过程之间的数据隔离开了，但是我们在过程的执行之间肯定是要有一些数据传递的，体现在C语法上就是函数的参数和返回值。正常来说，一个函数的调用过程是：

划分一个栈区用于当前函数的执行（这里其实只要确定一个栈底就好了）

把函数需要的所有数据入栈

执行函数体（也就是指令组了）

把函数的结果返回出去

栈区作废，可以重复利用

在早期版本的C语言（C89）中，每个函数中需要的局部变量都是要在函数头定义全的，也就是说函数体中是不能再单独定义变量的，主要就是为了让编译器能够划分好内存空间给每一个局部变量。但后来在C99标准里这个要求被放开了，但本质上来说原理是没有变的，编译器会根据局部变量定义的顺序来进行空间的分配。

要理解这一点，我们直接从汇编代码上来看是最直观的。首先给出一个用于验证的C代码：


```c
void Demo() {
  int a = 0;
  long b = 1;
  short c = 2;
}
```

将其转换为AMD64汇编是这样的：

```c
Demo:
        push    rbp
        mov     rbp, rsp
        mov     DWORD PTR [rbp-4], 0
        mov     QWORD PTR [rbp-16], 1
        mov     WORD PTR [rbp-18], 2
        nop
        pop     rbp
        ret
```

`rbp`寄存器中存放的就是栈底的地址，我们可以看到，`rbp-4`的位置放了变量`a`，因为`a`是`int`类型的，所以占用4个字节，也就是从`[rbp]`到`[rbp-4]`的位置都是变量`a`（这里注意里面是减法哈，按照小端序的话低字节是高位），然后按照我们定义变量的顺序来排布的（中间预留4字节是为了字节对齐）。

那如果函数有参数呢？会放在哪里？比如：

```c
void Demo(int in1, char in2) {
  int a = 0;
  long b = 1;
  short c = 2;
}
```

会转换为：

```c
Demo:
        push    rbp
        mov     rbp, rsp
        mov     DWORD PTR [rbp-36], edi
        mov     eax, esi
        mov     BYTE PTR [rbp-40], al
        mov     DWORD PTR [rbp-4], 0
        mov     QWORD PTR [rbp-16], 1
        mov     WORD PTR [rbp-18], 2
        nop
        pop     rbp
        ret
```

可以看出来，函数参数也是作为一种局部变量来使用的，我们可以看到这里处理参数都是直接处理内存的，也就是说在函数调用的时候，就是直接把拿着实参的值，在函数的栈区创建了一个局部变量。所以函数参数在函数内部也是作为局部变量来对待的。

那如果函数有返回值呢？请看下面实例：

```c
int Demo() {
  return 5;
}
```

会转义为：

```c
Demo:
        push    rbp
        mov     rbp, rsp
        mov     eax, 5
        pop     rbp
        ret
```

也就是说，返回值会直接写入寄存器，这样外部如果需要使用函数返回值的话，就直接从寄存器中取就好了。

所以，上面的例子主要是想表明，C语言的设计对于编译器来说是相当友好的，从某种程度上来说，就是在给汇编语法做一个语法糖。数据的传递都是按照硬件的处理逻辑来布局的。请大家先记住这个函数之间传值的方式，参数就是普通的局部变量；返回的时候是把返回值放到寄存器，调用方会再从寄存器中拿。这个过程我们可以写一个更加直观的例子：

```c
int Demo1(int a) {
  return 5;
}
void Demo2() {
    int a = Demo1(2);
}
```

汇编后是：

```c
Demo1:
        push    rbp
        mov     rbp, rsp
        mov     DWORD PTR [rbp-4], edi
        mov     eax, 5
        pop     rbp
        ret
Demo2:
        push    rbp
        mov     rbp, rsp
        sub     rsp, 16
        mov     edi, 2
        call    Demo1
        mov     DWORD PTR [rbp-4], eax
        nop
        leave
        ret
```

这就非常说明问题了，函数传参时，因为已经构建了被调函数的栈空间，所以可以直接变量复制，但对于返回值，**这是本篇的第一个重点！！「函数返回值是放在寄存器中传递出去的」**。

寄存器传递数据固然方便，但寄存器长度是有上限的，如果需要传递的数据超过了寄存器的长度怎么办？

```c
struct Test {
  long a, b;
};
struct Test Demo() {
  struct Test t = {1, 2};
  return t;
}
```

汇编后是：

```c
Demo:
        push    rbp
        mov     rbp, rsp
        mov     QWORD PTR [rbp-16], 1
        mov     QWORD PTR [rbp-8], 2
        mov     rax, QWORD PTR [rbp-16]
        mov     rdx, QWORD PTR [rbp-8]
        pop     rbp
        ret
```

尴尬~~编译器竟然用了2个寄存器来返回数据……这太不给面子了，那我们就再狠一点，搞再长一点：

```c
struct Test {
  long a, b, c;
};

struct Test Demo() {
  struct Test t = {1, 2, 3};
  return t;
}
```

当结构体的长度再大一点的时候，情况就发生改变了：

```c
Demo:
        push    rbp
        mov     rbp, rsp
        mov     QWORD PTR [rbp-40], rdi
        mov     QWORD PTR [rbp-32], 1
        mov     QWORD PTR [rbp-24], 2
        mov     QWORD PTR [rbp-16], 3
        mov     rcx, QWORD PTR [rbp-40]
        mov     rax, QWORD PTR [rbp-32]
        mov     rdx, QWORD PTR [rbp-24]
        mov     QWORD PTR [rcx], rax
        mov     QWORD PTR [rcx+8], rdx
        mov     rax, QWORD PTR [rbp-16]
        mov     QWORD PTR [rcx+16], rax
        mov     rax, QWORD PTR [rbp-40]
        pop     rbp
        ret
```

我们能看到，这里做的事情很有趣，`[rbp-40]`~`[rpb-16]`这24个字节是局部变量`t`，函数执行后被写在了`[rdi]`~`[rdi+24]`这24个字节的空间的位置，而最后寄存器中存放的是`rdi`的值（汇报指令有点绕，受限于AMD64汇编语法的限制，不同种类寄存器之间不能直接赋值，所以它先搞到了`[rbp-40]`的内存位置，然后又写到了`rcx`寄存器中，所以后面的`[rcx+8]`其实就是`[rdi+8]`，最后`rax`中其实放的也是一开始的`rdi`的值）。那这个`rdi`寄存器的值是谁给的呢？我们加上调用代码来观察：

```c
struct Test {
  long a, b, c;
};

struct Test Demo1() {
  struct Test t = {1, 2, 3};
  return t;
}

void Demo2() {
  struct Test t = Demo1();
}
```

汇编成：

```c
Demo1:
        push    rbp
        mov     rbp, rsp
        mov     QWORD PTR [rbp-40], rdi
        mov     QWORD PTR [rbp-32], 1
        mov     QWORD PTR [rbp-24], 2
        mov     QWORD PTR [rbp-16], 3
        mov     rcx, QWORD PTR [rbp-40]
        mov     rax, QWORD PTR [rbp-32]
        mov     rdx, QWORD PTR [rbp-24]
        mov     QWORD PTR [rcx], rax
        mov     QWORD PTR [rcx+8], rdx
        mov     rax, QWORD PTR [rbp-16]
        mov     QWORD PTR [rcx+16], rax
        mov     rax, QWORD PTR [rbp-40]
        pop     rbp
        ret
Demo2:
        push    rbp
        mov     rbp, rsp
        sub     rsp, 32
        lea     rax, [rbp-32]
        mov     rdi, rax
        mov     eax, 0
        call    Demo1
        nop
        leave
        ret
```

也就是说，在这种场景下，调用`Demo1`之前，`rdi`写的就已经是`Demo2`中`t`的地址了。编译器其实是把「返回值」变成了「出参」，直接拿着「将要接受返回值的变量地址」进到函数里面来处理了。**这是本篇的第二个重点！！「函数返回值会被转换为出参，内部直接操作外部栈空间」**。

但假如，我们要的并不是「返回值的全部」，而是「返回值的一部分」呢？比如说：

```c
struct Test {
  long a, b, c;
};

struct Test Demo1() {
  struct Test t = {1, 2, 3};
  return t;
}

void Demo2() {
  long a = Demo1().a; // 只要其中的一个成员
}
```

那么这个时候会汇编成：

```c
Demo1:
        push    rbp
        mov     rbp, rsp
        mov     QWORD PTR [rbp-40], rdi
        mov     QWORD PTR [rbp-32], 1
        mov     QWORD PTR [rbp-24], 2
        mov     QWORD PTR [rbp-16], 3
        mov     rcx, QWORD PTR [rbp-40]
        mov     rax, QWORD PTR [rbp-32]
        mov     rdx, QWORD PTR [rbp-24]
        mov     QWORD PTR [rcx], rax
        mov     QWORD PTR [rcx+8], rdx
        mov     rax, QWORD PTR [rbp-16]
        mov     QWORD PTR [rcx+16], rax
        mov     rax, QWORD PTR [rbp-40]
        pop     rbp
        ret
Demo2:
        push    rbp
        mov     rbp, rsp
        sub     rsp, 32
        lea     rax, [rbp-32]
        mov     rdi, rax
        mov     eax, 0
        call    Demo1
        mov     rax, QWORD PTR [rbp-32]
        mov     QWORD PTR [rbp-8], rax
        nop
        leave
        ret
```

我们发现，虽然在`Demo2`中没有刚才那样完整的结构体变量`t`，但编译器还是会分配一片用于保存返回值的空间，把这个空间的地址写在`rdi`中，然后拿着这个空间到`Demo1`中来操作。等`Demo1`函数执行完，再根据需要，把这片空间中的数据**复制**给局部变量`a`。

换句话说，编译器其实是创建了一个匿名的结构体变量（我们姑且叫它`tmp`），所以上面的代码其实等价于：

```c
void Demo2() {
  struct Test tmp = Demo1(); // 注意这个变量其实是匿名的
  int a = tmp.a;
}
```

### 小结

总结上面所说，对于一个函数的返回值：

  1. 如果能在一个寄存器存下，就会存到寄存器中

  2. 如果在一个寄存器存不下，就会考虑拆分到多个寄存器中

  3. 如果多个可用的寄存器都存不下，就会考虑直接用内存来存放，在调用函数之前先开放一片内存空间用于储存返回值，然后函数内部直接使用这片空间

  4. 如果调用方直接接收函数返回值，那么就会直接把这片空间标记给这个变量

  5. 如果调用方只使用返回值的一部分，那么这片空间就会成为一个匿名的空间存在（只有地址，但没有变量名）

这一套体系在C语言中其实并没有太多问题，但有了C++的拓展以后，就不一样了。

### 考虑上构造和析构函数会怎么样

C++在C的基础上，为结构体添加了构造函数和析构函数，为了能「屏蔽抽象内部的细节」，将构造和析构函数与变量的生命周期进行了绑定。在创建变量时会强制调用构造函数，而在变量释放时会强制调用析构函数。

如果是正常在一个代码块内，这件事自然是无可厚非的，我们也可以简单来验证一下：

```c
struct Test {
  Test() {}
  ~Test() {}
};

void Demo() {
  Test t;
}
```

汇编成：

```c
Test::Test() [base object constructor]:
        push    rbp
        mov     rbp, rsp
        mov     QWORD PTR [rbp-8], rdi
        nop
        pop     rbp
        ret
Test::~Test() [base object destructor]:
        push    rbp
        mov     rbp, rsp
        mov     QWORD PTR [rbp-8], rdi
        nop
        pop     rbp
        ret
Demo():
        push    rbp
        mov     rbp, rsp
        sub     rsp, 16
        lea     rax, [rbp-1]
        mov     rdi, rax
        call    Test::Test() [complete object constructor]
        lea     rax, [rbp-1]
        mov     rdi, rax
        call    Test::~Test() [complete object destructor]
        leave
        ret
```

注意C++由于支持了函数重载，因此函数签名里会带上参数类型，所以这里的函数名都比C语言直接汇编出来的多一个括号。

那如果一个自定义了构造和析构的类型做函数返回值的话会怎么样？比如：

```c
struct Test {
  Test() {}
  ~Test() {}
};

Test Demo1() {
  Test t;
  return t;
}

void Demo2() {
  Test t = Demo1();
}
```

这里我们给编译器加上`-fno-elide-constructors`参数来关闭返回值优化，这样能看到语言设计的本质，汇编后是：

```c
Test::Test() [base object constructor]:
        push    rbp
        mov     rbp, rsp
        mov     QWORD PTR [rbp-8], rdi
        nop
        pop     rbp
        ret
Test::~Test() [base object destructor]:
        push    rbp
        mov     rbp, rsp
        mov     QWORD PTR [rbp-8], rdi
        nop
        pop     rbp
        ret
Test::Test(Test const&) [base object constructor]:
        push    rbp
        mov     rbp, rsp
        mov     QWORD PTR [rbp-8], rdi
        mov     QWORD PTR [rbp-16], rsi
        nop
        pop     rbp
        ret
Demo1():
        push    rbp
        mov     rbp, rsp
        sub     rsp, 32
        mov     QWORD PTR [rbp-24], rdi
        lea     rax, [rbp-1]
        mov     rdi, rax												;注意这里rdi发生了改变！
        call    Test::Test() [complete object constructor]
        lea     rdx, [rbp-1]
        mov     rax, QWORD PTR [rbp-24]
        mov     rsi, rdx
        mov     rdi, rax
        call    Test::Test(Test const&) [complete object constructor]
        lea     rax, [rbp-1]
        mov     rdi, rax
        call    Test::~Test() [complete object destructor]
        nop
        mov     rax, QWORD PTR [rbp-24]
        leave
        ret
Demo2():
        push    rbp
        mov     rbp, rsp
        sub     rsp, 16
        lea     rax, [rbp-1]
        mov     rdi, rax
        call    Demo1()
        lea     rax, [rbp-1]
        mov     rdi, rax
        call    Test::~Test() [complete object destructor]
        leave
        ret
```

这次代码就非常有意思了，首先，编译器自动生成了一个拷贝构造函数`Test::Test(const Test &)`。接下来做的事情跟纯C语言结构体就有区别了，在`Demo2`中，由于我们仍然是用变量直接接收了函数返回值，所以它同样还是直接把`t`的地址，写入了`rdi`，这里行为和之前是一样的。但是在`Demo1`中，`rdi`的值写入了`rbp-24`的位置，但后面调用构造函数的时候传入的是`rbp-1`，所以说明这个位置才是`Demo1`中的`t`实际的位置，等待构造函数调用完之后，又调用了一次拷贝构造，这时传入的才是`rbp-24`，也就是外部传进来保存函数返回值的地址。

也就是说，由于构造函数和析构函数跟变量生命周期相绑定了，因此这时并不能直接把「函数返回值转出参」了，而是先生成一个局部变量，然后通过拷贝构造函数来构造「返回值」，再析构这个局部变量。所以整个过程会多一次拷贝和析构的过程。

这么做，是为了保证对象的行为自闭环，但**只有当析构函数和拷贝构造函数是非默认行为**的时候，这样做才有意义，如果真的就是C类型的结构体，那就没这个必要了，按照原来C的方式来编译即可。因此C++在这里强行定义了「平凡（trivial）」类型的概念，主要就是为了指导编译器，对于平凡类型，直接按照C的方式来编译，而对于非平凡的类型，要调用构造和析构函数，因此必须按照新的方式来处理（刚才例子那样的方式）。

那么这个时候再考虑一点，如果我们还是只使用返回值的一部分呢？比如说：

```c
struct Test {
  Test() {}
  ~Test() {}
  int a;
};

Test Demo1() {
  Test t;
  return t;
}

void Demo2() {
  int a = Demo1().a;
}
```

结果非常有趣：

```c
Test::Test() [base object constructor]:
        push    rbp
        mov     rbp, rsp
        mov     QWORD PTR [rbp-8], rdi
        nop
        pop     rbp
        ret
Test::~Test() [base object destructor]:
        push    rbp
        mov     rbp, rsp
        mov     QWORD PTR [rbp-8], rdi
        nop
        pop     rbp
        ret
Test::Test(Test const&) [base object constructor]:
        push    rbp
        mov     rbp, rsp
        mov     QWORD PTR [rbp-8], rdi
        mov     QWORD PTR [rbp-16], rsi
        mov     rax, QWORD PTR [rbp-8]
        mov     rdx, QWORD PTR [rbp-16]
        mov     edx, DWORD PTR [rdx]
        mov     DWORD PTR [rax], edx
        nop
        pop     rbp
        ret
Demo1():
        push    rbp
        mov     rbp, rsp
        sub     rsp, 32
        mov     QWORD PTR [rbp-24], rdi
        lea     rax, [rbp-4]
        mov     rdi, rax
        call    Test::Test() [complete object constructor]
        lea     rdx, [rbp-4]
        mov     rax, QWORD PTR [rbp-24]
        mov     rsi, rdx
        mov     rdi, rax
        call    Test::Test(Test const&) [complete object constructor]
        lea     rax, [rbp-4]
        mov     rdi, rax
        call    Test::~Test() [complete object destructor]
        nop
        mov     rax, QWORD PTR [rbp-24]
        leave
        ret
Demo2():
        push    rbp
        mov     rbp, rsp
        sub     rsp, 16
        lea     rax, [rbp-8]
        mov     rdi, rax
        call    Demo1()
        mov     eax, DWORD PTR [rbp-8]
        mov     DWORD PTR [rbp-4], eax						;这里是给局部变量a赋值
        lea     rax, [rbp-8]
        mov     rdi, rax
        call    Test::~Test() [complete object destructor]
        nop
        leave
        ret
```

这里仍然会分配一个匿名的空间用于接收返回值，然后再从这个匿名空间中取值复制给局部变量`a`。从上面的代码能看出，匿名空间在`rbp-8`的位置，局部变量`a`在`rbp-4`的位置。但这里非常有意思的是，在给局部变量赋值后，立刻对匿名空间做了一次析构（所以它把`rbp-8`写到了`rdi`中，然后`call`了析构函数）。**这是本篇的第三个重点！！「如果用匿名空间接收函数返回值的话，在处理完函数调用语句后，匿名空间将会被析构」**。

### 左值（Left-hand-side Value）、纯右值（Pure Right-hand-side Value）与将亡值（Expiring Value）

讲了这么多，总算能回到主线上来了，先来归纳一下前文出现的3个重点：

  1. 函数返回值是放在寄存器中传递出去的

  2. 函数返回值会被转换为出参，内部直接操作外部栈空间

  3. 如果用匿名空间接收函数返回值的话，在处理完函数调用语句后，匿名空间将会被析构

其实对应了函数返回数据的3种处理方式：

  1. 直接存在寄存器里

  2. 直接操作用于接收返回值的变量（如果是平凡的，直接操作；如果是非平凡的，先操作好一个局部变量，然后再拷贝过来）

  3. 先放在一个临时的内存空间中，使用完后再析构掉

C++按照这个特征来划分了prvalue和xvalue。（注意，英语中所有以"ex"开头的单词，如果缩写的话会缩写为"x"而不是"e"，就比如说"Extreme Dynamic Range"缩写是"XDR"而不是"EDR"; "Extensible Markup Language"缩写为"XML"而不是"EML"。）

所谓prvalue，翻译为“纯右值”，表示的就是第1种，也就是用寄存器来保存的情况，或者就是字面常量。举例来说，`1`这就是个纯右值，它在汇编中就是一个单纯的常数。然后就是返回值通过寄存器来进行的这种情况。对于C/C++这种语言来说，我们可以尽情操作内存，但没法染指寄存器，所以在它看来，寄存器中的数就跟一个常数值一样，只能感知到它的值而已，不能去操控，不能去改变。换一种说法，**prvalue就是「没有内存实体」的值**，常数没有内存实体，寄存器中的数据也没有内存实体。所以prvalue没有地址。

而对于第2种的情况，「返回值」的这件事情其实是不存在的，只是语义上的概念。实际就是操作了一个调用方的栈空间。因此，这种情况就等价于普通的变量，它是一个lvalue，它是实实在在可控的，有内存实体，程序可以操作。

对于第3种的情况，「返回值」被保存在一个匿名的内存空间中，它在完成某一个动作之后就失效了（非平凡析构类型的就会调用析构函数）。比如用上一节的例子来说，从`Demo1`函数的返回值（匿名空间）获取了成员`a`交给了局部变量，然后，这个匿名空间就失效了，所以调用了`~Demo`析构函数。我们把这种值称为xvalue（将亡值），xvalue也有内存实体。

以目前得到的信息来说，xvalue和lvalue的区别就在于生命周期。在C++中生命周期比在C中更加重要，在C中讨论生命周期其实仅仅在于初始化和赋值的问题（比如说局部static变量的问题），但到了C++中，生命周期会直接决定了构造和析构函数的调用，因此更加重要。xvalue会在当前语句结束时立刻析构，而lvalue会在所属代码块结束时再析构。所以针对于xvalue的情况，在C中并不明显，反正我们是从匿名的内存空间读取出数据来，这件事情就结束了；但C++中就会涉及析构函数的问题，这就是xvalue在C++中非常特殊的原因。

### xvalue取址问题与C++引用

对于prvalue来说，它是纯「值」或「寄存器值」，因此不能取地址，这件事无可厚非。但对于xvalue来说呢？xvalue有内存实体，但为什么也不能取地址呢？

原因就是在于，原本C语言在设计这个部分的时候，函数返回值究竟要写到一个局部变量里，还是要写到一个匿名的内存空间里这件事是不能仅通过一个函数调用语句来判断，而是要通过上下文。也就是说，`struct Test t = Demo1();`的时候，`t`本身的地址就是返回值地址，此时返回值是lvalue（因为`t`就是lvalue）；而如果是`int ta = Demo1().a;`的时候，返回值的地址是一个匿名的空间，此时返回值就是xvalue，而这里的`ta`就不再是返回值的地址。所以，如果你什么都不给，单纯给一个`Demo1();`，**编译器就无法判断要选取哪一种方式**，所以干脆就不支持`&Demo1();`这种写法，你得表达清楚了，我才能确定你要的是谁的地址。所以前一种情况下的`&t`就是返回值所在的地址，而后一种情况的`&ta`就并不是返回值所在地址了。

原本C中的这种方式倒是也合理，但是C++却引入了「引用」的概念，希望让「xx的引用」从「语义上」成为「xx的别名」这种感觉。但C++在实现引用的时候，又没法做到真的给变量起别名，所以转而使用指针的语法糖来实现引用。比如说：

```c
int a = 5;
int &r = a;
```

语义上，表达的是「`a`是一个变量，`r`代指这个变量，对`r`做任何行为就等价于对`a`做同样的行为，所以`r`是`a`的替身（引用）」。但实际上却做的是「定义了一个新的变量`pr`，初始化为`a`的地址，对`p`做任何行为就等价于对`*pr`做任何行为，这是一个取地址和解指针的语法糖」。

既然本质是指针，那么指针的解类型就是可以手动定义的，同理，变量的引用类型也是可以手动定义的。（本质上就不是别名，如果是别名的话，那类型怎么能变化呢？）比如说：

```c
int a = 5;
char &r = reinterpret_cast<char &>(a);
```

上面这种写法是成立的，因为它的本质就是：

```c
int a = 5;
char *pr = reinterpret_cast<char *>(&a);
```

变化的仅仅是指针的解类型而已。自然没什么问题。既然解类型可以强转，自然也就符合隐式转换特性，我们知道可变指针可以隐式转换为不可变指针，那么「可变引用」也自然可以隐式转换为「不可变引用」，比如说：

```c
int a = 5;
const int &r = a;
// 等价于：
const int &r = const_cast<const int &>(a);
// 等价于
const int *pr = &a;
// 等价于
const int *pr = const_cast<const int *>(&a);
```

绕来绕去本质都是指针的行为。刚才我们说到rvalue是不能取址的，那么自然，我们就**不能用一个普通的引用来接收函数返回值**：

```c
Test &r = Demo1(); // 不可以！因为它等价于
Test *pr = &Demo1(); // 这个不可以，所以上面的也不可以
```

### 常引用与右值（Right-hand-side Value）

虽然引用本质上就是指针的语法糖，但C++并不满足于此，它为了让「语义」更加接近人类的直觉，它做了这样一件事：**让用`const`修饰的引用可以绑定函数的返回值**。

从语义上来说，它不希望我们程序员去区分「寄存器返回值」还是「内存空间返回值」，既然是函数的返回值，你就可以认为它是一个「纯值」就好了。或者换一个说法，如果你要屏蔽寄存器这一层的硬件实现，我们就不应该区分寄存器返回值还是内存返回值，而是**假设寄存器足够大**，那么函数返回值就一定是个「纯值」。那么这个「纯值」就叫做rvalue。

这就是我前面提到的「语言设计」层面，在语言设计上，函数返回值就应当是个rvalue，只不过在编译器实现的时候，根据返回值的大小，决定它放到寄存器里还是内存里，放寄存器里的就是prvalue，放内存里的就是xvalue。**所以prvalue和xvalue合称rvalue**，就是这么来的。

而用`const`修饰的引用，它绑定普通变量的时候，语义上解释为「一个变量的替身，并且不可变」，实际上是「含了一次`const_cast`隐式转换的指针的语法糖」。

当它绑定函数返回值的时候，语义上解释为「一个值的替身（当然也是不可变的）」，实际上是代指一片内存空间，如果函数是通过寄存器返回的，那么就把寄存器的值复制到这片空间，而如果函数是通过内存方式返回的，那么就把这片内存空间传入函数中作为「类似于出参」的方式。

两种方式都同为「一个替身，并且不可变」，因此又把`const`修饰的引用叫做「常引用」。

等等！这里好像有点奇怪哎？！照这么说的话，常引用去接受函数返回值的情况，不是跟一个普通变量去接受返回值的情况一模一样了吗？**对，是的，没错！你的想法是对的！**，下面两行代码其实会生成相同的汇编指令：

```c
struct Test {
  long a, b, c;
};

Test Demo1() {
  Test t{1, 2, 3};
  return t;
}

void Demo2() {
  const Test &t1 = Demo1();
  // 汇编指令等价于
  const Test t2 = Demo1();
}
```

他们都是划分了一片内存区域，然后把地址传到函数里去使用的（也就是返回值转出参的情况）。同理，如果返回值是通过寄存器传递的也是一样：

```c
int Demo1() {
  return 2;
}

void Demo2() {
  const int &t1 = Demo1();
  // 汇编指令等价于
  const int t2 = Demo1();
}
```

所以，上面两个例子中，无论是`t1`还是`t2`，本质都是一个普通的局部变量，它们有内存实体，并且生命周期跟随栈空间，因此都是lvalue。**这是本文第四个重点！！「引用本身是lvalue」**。也就是说，函数返回值是rvalue（有可能是prvalue，也有可能是xvalue），但如果你用引用来接收了，它就会变成lvalue。

### 目前阶段的结论

这里再回过头来看一下，**刚才我们说「函数返回值是rvalue」这事好像就有一点问题了**。从理论上来理解用一个变量或引用来接收一个rvalue这种说法是没错的，但其实编译期并不是单纯根据函数返回值这一件事来决定如何处理的，而是要带上上下文（或者说，返回值的长度以及使用返回值的方式）。所以**单独讨论`f()`是什么值类型并没有意义**，而是要根据上下文。我们总结如下：

  1. 常量一定是prvalue（比如说`1`、`'a'`、`5.6f`）。

  2. 变量、引用（包括常引用）都是lvalue，哪怕是用于接受函数返回值，它也是lvalue。（这里一种情况是通过寄存器复制过来的，但复制完它已经成为变量了，所以是lvalue；另一种是直接把变量地址传到函数中去接受返回值的，这样它本身也是lvalue）。

  3. 只有当仅使用返回值的一部分（类似于`f().a`的形式）的这种情况，会使用临时空间（匿名的，会在当前语句结束后析构），这种情况下的临时空间是xvalue。

### 这里的设计初衷

所以，各位发现了吗？C++在设计时应当很单纯地认为value分两类：一类是变量，一类是值。变量它有内存实体，可以出现在赋值语句的左边，所以称为「左值」；值没有内存实体，只能出现在赋值语句的右边，所以称为「右值」。

但在实现时，却受到了C语言特性的约束（更准确来说是硬件的约束），造成我们不能把所有的右值都按照统一的方式来传递，所以才按照C语言处理返回值的方式强行划分出了prvalue和xvalue，其作用就是用来指导析构函数的调用，以实现对象系统的自闭环。

C语言原本就比较面相硬件，所以它的处理是对于机器来说更加合理的。而C++则希望能提供一套对程序员更加友好的「语义」，所以它在「语义」的设计上是对人更加合理的，就比如这里的常引用，其实就是想成为一个「不可变的替身」。但又必须向下兼容C的解析方式，因此做了一系列的语法糖。而语法糖背后又会触发底层硬件不同处理方式的问题，所以又不得不为了区分，而强行引入奇怪的概念（比如这里的xvalue）。

原本「找补」到这里（划分出了xvalue和常引用的概念后）基本已经可以子闭环了。但C++偏偏就是非常倔强，又“贴心”地给程序员提供了「移动语义」，让当前的这个闭环瞬间被打破，然后又不得不建立一个新的理论闭环。

### 再来研究一次返回局部变量（C++14的情况）

上一篇我们提到过类似于下面这样的实例：

```c
struct Test {
  Test() {}
  ~Test() {}
};

Test Demo1() {
  Test t;
  return t;
}

void Demo2() {
  Test t = Demo1();
}
```

C++17对应的汇编指令在前面已经贴出，需要的读者可以去前面取用。当时我们说「常引用去接受函数返回值的情况，跟一个普通变量去接受返回值的情况一模一样」，我相信有读者一定在这里有千百万个问号，为什么会有这样奇怪的设计。这里毫不意外地命中了历史遗留问题，也就是说这个问题也是「找补」之后出现的。所以要想搞清楚，我们就得看看老版本的C++标准下，它是怎么回事。

这里，我们给出C++14标准下的汇编（编译参数：`-fno-elide-constructors -std=c++14`）：

```c
Test::Test() [base object constructor]:
        push    rbp
        mov     rbp, rsp
        mov     QWORD PTR [rbp-8], rdi
        nop
        pop     rbp
        ret
Test::~Test() [base object destructor]:
        push    rbp
        mov     rbp, rsp
        mov     QWORD PTR [rbp-8], rdi
        nop
        pop     rbp
        ret
Test::Test(Test const&) [base object constructor]:
        push    rbp
        mov     rbp, rsp
        mov     QWORD PTR [rbp-8], rdi
        mov     QWORD PTR [rbp-16], rsi
        nop
        pop     rbp
        ret
Demo1():
        push    rbp
        mov     rbp, rsp
        sub     rsp, 32
        mov     QWORD PTR [rbp-24], rdi
        lea     rax, [rbp-1]
        mov     rdi, rax
        call    Test::Test() [complete object constructor]
        lea     rdx, [rbp-1]
        mov     rax, QWORD PTR [rbp-24]
        mov     rsi, rdx
        mov     rdi, rax
        call    Test::Test(Test const&) [complete object constructor]
        lea     rax, [rbp-1]
        mov     rdi, rax
        call    Test::~Test() [complete object destructor]
        nop
        mov     rax, QWORD PTR [rbp-24]
        leave
        ret
Demo2():
        push    rbp
        mov     rbp, rsp
        sub     rsp, 16
        lea     rax, [rbp-1]
        mov     rdi, rax
        call    Demo1()
        lea     rdx, [rbp-1]
        lea     rax, [rbp-2]
        mov     rsi, rdx
        mov     rdi, rax
        call    Test::Test(Test const&) [complete object constructor]
        lea     rax, [rbp-1]
        mov     rdi, rax
        call    Test::~Test() [complete object destructor]
        lea     rax, [rbp-2]
        mov     rdi, rax
        call    Test::~Test() [complete object destructor]
        leave
        ret
```

当时我们说，针对这种情况，由于`Test`类型是「非平凡」的（因为构造、析构函数都已经自定义了），为了保证对象行为的完整性，`Demo1`中的局部变量`t`需要在其对应的栈空间结束时进行析构。因此就不能再按照平凡类型的方式，直接使用外部的变量了，而是要经过一次「复制」。也就是说，用`Demo1`中的`t`作为参数，调用一次拷贝构造函数来构造`Demo2`中的`t`（也就是`Demo1`的返回值），然后再把`Demo1`中的`t`进行析构。

这些都没变，但唯一变化的是相比C++17标准多了一次复制和析构，这是哪里的问题呢？通过观察汇编代码我们可以发现，多的一次拷贝是在`Demo2`中。那么也就是说，在早版本的C++中，**对于用变量接收非平凡类型的返回值时，按xvalue处理**。也就是说当我们是用一个变量来接收函数返回值的时候，编译器还是会划分一片匿名的临时空间来接收返回值的，接收完之后再用这个临时对象来构造新的局部变量。因此，这种情况下，返回值就是xvalue，然后我们用xvalue来构造了一个lvalue。（这是很多其他资料给出的结论，大家不用再质疑了！因为C++14及以前版本就是这样设计的）。

正是因为这种设计，我们再去解释「常引用可以接收函数返回值」这件事就更容易了。从语义上来说，常引用是可以直接绑定这片匿名的临时空间的，绑定后，就相当于不再「匿名」。那么，直接用变量接收返回值，其实就等价于先用常引用接收返回值，然后再用它来构造新的局部变量：

```c
void Demo2() {
  Test t = Demo1(); 
  // 等价于
  const Test &tmp = Demo1(); // 常引用接收返回值（临时空间）
  Test t = tmp; // 拷贝构造
}
```

原本这样设计其实就是能够让这个临时空间拥有一个名字（引用），但这就会出现另一个问题，如果这时，临时空间还是立即释放的话，那么再使用的时候就会出现野指针错误。用上面的例子来说，假如`Demo1()`返回值按xvalue来处理的话，那么`const Test &tmp = Demo1();`语句结束时，这片空间就应该释放了，临时空间中的对象也要析构掉。那么此时，`tmp`这个引用就会**指向了已经释放的空间**，成为野引用。之后再用`tmp`去构造`t`的时候，就会出现解野指针错误，这显然是违背了原本「给临时空间起个名字」的用意。

为了解决这个问题，C++不得不让这片临时空间「延长它的寿命」，这样后面才能去使用它。所以，**当用常引用接收函数返回值时，临时空间不会立即释放，而是跟随常引用成为了栈上的变量**。所以上面例子中，`tmp`所指的对象并不会立刻析构，而是会等到`Demo2`函数结束。

这样来说事情就特别奇怪了，用常引用接收的函数返回值不仅没有成为xvalue，反而是成为了一个独立的变量了，比较违背直觉（直觉是，引用了临时空间，但实际上这种情况下反而没有临时空间了，而是会出现一个lvalue）。但如果直接用变量来接收返回值的话，倒是会出现一个临时空间（返回xvalue），然后再多一次拷贝（用临时对象拷贝构造局部对象）和析构（析构临时对象）。这也很反直觉（直觉是用局部变量接收返回值，但其实是多生成了一次xvalue）。

离谱……相当离谱！难道就没有一种完美的方案，可以表达这种「用局部变量接收返回值」并且「不出现额外的临时对象」吗？右值引用就这么诞生了！

### 右值引用(rvalue-reference)与复制省略(Copy Elision)

以C++14及以前的标准来说，我们发现，如果直接用一个变量来接收返回值，会多一次临时对象的拷贝和析构，用常引用虽然可以减少这一次拷贝，但常引用是用`const`修饰的，不可修改（如果要修改的话，还是得再去拷贝构造一个新的变量）。而为了解决这个问题，C++引入了「右值引用」。

其实这个语法完完全全就是为了解决函数返回值问题的，但为什么叫「右值引用」呢？我们在前面解释过，从语义上来说，返回值可以理解为都是rvalue（可能是prvalue，可能是xvalue），因此用来接收rvalue的引用，就被叫做了rvalue-reference，翻译为「右值引用」。但大家一定一定要知道的是，这是「语义」上的解释，实际只要有引用来接收函数返回值的话，它就会变成lvalue。

```c
void Demo2() {
  Test &&t = Demo1(); // 用右值引用接收函数返回值
}
```

从行为上来说，右值引用接收函数返回值和用常引用接收函数返回值的情况几乎完全相同，区别仅仅在于，右值引用不需要`const`修饰，因此可以更改。相比直接用变量来接收的情况，少了一次xvalue的中间值，也就减少了一次复制和析构。那么结论也就呼之欲出了：**右值引用从语义上来说，是对右值的引用，但一旦完成了这种引用，其实整个过程就不会出现右值了，而是用一个左值来保存返回值**，这就是我们为什么一直强调说「右值引用本身是左值」了。

来看一下完整的实例：

```c
struct Test {
  Test() {}
  ~Test() {}
};

Test Demo1() {
  Test t;
  return t;
}

void Demo2() {
  Test &&t = Demo1();
}
```

汇编结果（编译参数：`-fno-elide-constructors -std=c++14`）：

```c
Test::Test() [base object constructor]:
        push    rbp
        mov     rbp, rsp
        mov     QWORD PTR [rbp-8], rdi
        nop
        pop     rbp
        ret
Test::~Test() [base object destructor]:
        push    rbp
        mov     rbp, rsp
        mov     QWORD PTR [rbp-8], rdi
        nop
        pop     rbp
        ret
Test::Test(Test const&) [base object constructor]:
        push    rbp
        mov     rbp, rsp
        mov     QWORD PTR [rbp-8], rdi
        mov     QWORD PTR [rbp-16], rsi
        nop
        pop     rbp
        ret
Demo1():
        push    rbp
        mov     rbp, rsp
        sub     rsp, 32
        mov     QWORD PTR [rbp-24], rdi
        lea     rax, [rbp-1]
        mov     rdi, rax
        call    Test::Test() [complete object constructor]
        lea     rdx, [rbp-1]
        mov     rax, QWORD PTR [rbp-24]
        mov     rsi, rdx
        mov     rdi, rax
        call    Test::Test(Test const&) [complete object constructor]
        lea     rax, [rbp-1]
        mov     rdi, rax
        call    Test::~Test() [complete object destructor]
        nop
        mov     rax, QWORD PTR [rbp-24]
        leave
        ret
Demo2():
        push    rbp
        mov     rbp, rsp
        sub     rsp, 16
        lea     rax, [rbp-9]
        mov     rdi, rax
        call    Demo1()
        lea     rax, [rbp-9]
        mov     QWORD PTR [rbp-8], rax
        lea     rax, [rbp-9]
        mov     rdi, rax
        call    Test::~Test() [complete object destructor]
        leave
        ret
```

有没有发现，这种情况下跟C++17标准下，直接用变量接收函数返回值的情况是一样的了。那么也就是说，C++17标准下，针对于变量直接接收函数返回值的这种情况，规定了减少一次xvalue的生成，我们称之为「复制省略（Copy Elision）」。

### 小结一下

所以整件事情的心路历程就很有意思了，我们来小结一下整个「找补」的过程：

  1. 对于非平凡类型，为了保证对象的行为完整性，函数返回值会单独作为一个临时对象，如果需要在栈上使用，那么会拷贝给栈上的变量。

  2. 为了希望这片临时空间能够被代码捕获到，于是允许了用常引用来绑定函数返回值。但如果这时返回值仍然保持xvalue的特性的话，会引入野指针问题，违背了「引用临时空间」的原意，因此不得不将这种情况改成lvalue，让常引用所引用的空间跟随其所在的栈空间来「延长」声明周期。

  3. 又因为常引用有`const`修饰，不能修改对象，因此引入了「右值引用」，当用右值引用绑定函数返回值时，行为跟常引用是一致的，可以减少一次xvalue的生成，「延长」声明周期，同时还可以修改对象。

  4. 又发现还是直接用变量来接收函数返回值更加直观、符合直觉，而这种情况下xvalue的生成并没有太大的必要，因此又规定了「复制省略」，来优化这一次复制。（优化之后，用变量接收函数返回值和用右值引用接收函数返回值就完全没有区别了；而用const变量接收函数返回值跟用常引用接收函数返回值也没有区别了。）

这里需要额外解释一下，上面的实例我们都添加了`-fno-elide-constructors`这个编译参数，其实它就是用于关闭编译器的自动复制省略的。在C++17以前，虽然语言标准是没有定义复制省略的，但编译器早早就发现了这个问题，于是做了一些定制化的优化（称为返回值优化，Return Value Optimization，或RVO），这个参数就是关闭RVO，完全按照语言标准来进行编译。而在C++17标准中，定义了复制省略的方式，因此编译器就必须按照语言标准定义的那样来处理返回值了，所以在C++17标准下，这个编译参数也就不再生效了。

通过上面的介绍，这个value体系应该闭环了吧？不！还差得远呢……

### 移动语义

原本，右值引用概念的引入就是为了做返回值优化的，但有了Copy Elision（以下简称CE）以后，仿佛右值引用在这个场景下了一个菜鸡，但这并不意味着右值引用将会成为历史语法而惨遭淘汰。因为它还有另一个重要的用途——移动语义。

移动语义原本是为了解决资源复用问题的，我们来看下面这个实例：

```c
class String {
 public:
  String();
  ~String();
  String(const String &);
 private:
  char *buf_;
};

// 由于算法本身不是本例程的重点，因此忽略掉一切扩容和优化问题，简单书写
String::String(): buf_(new char[1024]) {}

String::~String() {
  if (buf != nullptr) {
    delete [] buf_;
  }
}

String::String(const String &str) : buf_(new char[1024]) {
  std::memcpy(buf_, str.buf_, 1024);
}

void Demo1() {
  String str1;
  // 这里对str1做了一些操作，比如说添加了一些数据之类的
  return str1;
}

void Demo2() {
  String str = Demo1(); // 会触发一次拷贝构造
}
```

注意在上例中，我们用一个简单的字符串处理类来说明问题。`Demo2`中，用`str`来接收`Demo1`的返回值，这里会触发CE，直接用`Demo1`中的局部变量来拷贝构造这里的`str`。拷贝构造会调用拷贝构造函数，而我们可以看到，拷贝构造函数中是一次内存的深复制。也就是说，我们构造`str`会先分配一片空间，然后把`str1`中的`buf_`对应的数据拷贝到了`str`的`buf_`中，然后跟随着`Demo1`的结束，刚才`str1`的这片空间会被释放掉（析构函数中有`delete []`）。

这平白多一次内部的数据复制，就成为了C++希望优化的点。假如说，新的对象能够「直接拾取」原有对象的内部空间，岂不是可以节约资源，减少复制？于是C++引入了「移动构造函数」和「移动赋值函数」，就是说，当你用了一个「马上就不用的对象」来构造新对象的时候，就调用这个移动构造函数，里面应当执行浅复制，来延长内部资源的寿命。

那么，怎么区分「马上就不用的对象」和「一会还要继续用的对象」呢？看这里所谓「马上就不用的对象」是不是很符合xvalue的定义？那我就看看，如果我是用一个xvalue来构造新对象的话，我就复用资源；而如果是一个普通的lvalue的话，那说明它后面还有用，我就复制资源。那如何表示这个参数只接受xvalue呢？有三种方法：1.用变量接收；2.用常引用接收；3.用右值引用接收。

那么这里，C++又从「语义」上做了区分。当右值引用做函数参数时，认为优先匹配函数返回值。什么意思呢？就是对于重载函数的情况，如果我们**直接用函数返回值作为实参的话，优先匹配右值引用的重载**。用例子来说就是：

```c
#include <iostream>

struct Test {};
Test Demo1() {
  Test t;
  return t;
} 

void f(const Test &) {
  std::cout << 1 << std::endl;
}

void f(Test &&) {
  std::cout << 2 << std::endl;
}

void Demo2() {
  Test t;
  f(t); // 1
  f(Demo1()); // 2
}
```

这里有2个`f`函数的重载，对于`f(t)`这种调用来说，由于`t`本身是普通变量，不是直接函数返回值，那么这种情况只能命中常引用的版本，所以会打印`1`。而对于`f(Demo1())`这种调用来说，两个版本的`f`都可以匹配，但由于我们刚才提到的优先原则，如果存在右值引用的重载版本，遇到直接用函数返回值作为形参的这种情况，优先匹配右值引用的重载，所以会打印`2`。

大家注意，这里的这种优先原则并没有什么道理可言，就是语言标准强行规定的，用于区分你是变量传入，还是函数返回值直接传入。所以，有了这个原则，我们就可以完善刚才的移动构造函数了：

```c
class String {
 public:
  String();
  ~String();
  String(const String &);
  String(String &&); // 移动构造函数
 private:
  char *buf_;
};

String::String(String &&str): buf_(str.buf_) { // 直接浅复制
  str.buf_ = nullptr;
}

// 【其他函数实现省略，可以看前面的例程】
void Demo2() {
  String str = Demo1(); // 调用移动构造函数
}
```

有了这个例子我们就知道了，右值引用最大的价值已经不在于优化返回值了，而是用于**标记实参是否是直接的函数返回值**。

**！！重点来了！！** 有些教程资料可能会这么解释：函数返回值是右值，所以有右值引用接收，所以表「移动」语义的函数参数是右值引用。乍一看这个说法好像没问题，但其实经不起推敲，因为其实整个过程没有出现任何一个右值。对于`String`的移动构造函数来说，`str`是右值引用，在它的内部就是一个普通的变量，当我们在`Demo2`中用他来接收`Demo1`返回值的时候，命中了「右值引用接收函数返回值」这一情况，根据我们之前的分析，此时`str`是lvalue。所以整个过程是没有出现一个rvalue的。

这就是笔者反复强调，C++的「语义」和「实际处理」的区别。所以这里从语义上来说函数返回值是rvalue，包括常数也是一种rvalue，所以右值引用做函数参数时，用于「接收」一个rvalue。那么这里更加强调的是语义上的「接收」，这里希望接收一个右值。但右值引用本身其实就是一个栈上的普通变量，它是lvalue。

笔者更希望大家能够看到它的本质，右值引用做函数参数是为了优先匹配直接传入函数返回值的情况，从而跟常引用做参数来进行区分。匹配之后会按照返回值转出参的这种方式，成为一个栈上的普通变量，自然就是lvalue。

而通常情况下，用右值引用接收一个对象，是为了复用它的资源，来进行浅复制的。就好像，我们把原本的资源「移动」到了新的对象当中去，因此称之为「移动语义」。含有移动语义的构造函数就称为「移动构造函数」、含有移动语义的赋值函数就称为「移动赋值函数」。所以大家一定要清楚，这里的「移动」是「语义」上的，并没有真的移动，一般就是用来做浅复制的。当然了，你确实可以用右值引用做参数但是不做「移动」的事情（就比如说我们之前的例子中那个`f`函数一样），所以更加说明了这是「语义」上的，而实际只是一个软约束。

这样一来这个值类型体系总该闭环了吧？兄弟你还是太天真了，接下来就是整个体系里最复杂的一个环节——std::move。

### std::move

刚才我们解释了如果用一个右值（函数返回值、函数返回值的一部分、或者常数）做参数时，会命中右值引用的重载版本，从而实现移动语义，做浅复制，来节省资源。

但如果我们想对一个不是右值的量做同样的事情呢？这里还是用上一节的`String`为例：

```c
void Demo2() {
  String str1;
  String str2 = str1; // 这里会调用拷贝构造，因为str1是左值
}
```

如果我希望，用`str1`构造`str2`时，不用拷贝构造，而是用移动构造呢？或者说，虽然`str1`是个左值，但我仍然希望复用它里面的资源给到新的对象，这怎么办？这就要用到魔法操作了。我们知道，如果要进行移动语义，那么就需要用右值引用来接收。但现在`str1`是个左值，我们要是能给他强行「掰右」的话，不就可以「欺骗」编译器，把它当做右值来处理了嘛。反正移动语义本身就是个软约束，又不会真的去check入参的左右性。

所以，我们的魔法操作就是，把这个`str1`，伪装成右值，骗过编译器去触发右值引用的重载函数。像这样：

```c
void Demo2() {
  String str1;
  String str2 = static_cast<String &&>(str1); // 强制转成右值引用，去触发移动构造函数
}
```

这里多说一嘴，定义新变量时后面的等号并不是赋值，而是构造参数的语法糖，也就是说上面等价于

```c
String str2(static_cast<String &&>(str1)); // 构造参数，所以是用来匹配函数参数的
```

上面的这个操作由于过于魔幻，因此STL提供了一个工具函数来封装这个魔法操作，由于它的目的是为了触发移动语义，因此这个函数被命名为`std::move`，下面是它的实现：

```c
template <typename T>
constexpr std::remove_reference_t<T> &&move(T &&ref) noexcept {
  return static_cast<std::remove_reference_t<T> &&>(ref);
}
```

因此，刚才的代码也可以写作：

```c
void Demo2() {
  String str1;
  String str2 = std::move(str1); // 强制转成右值引用，去触发移动语义
}
```

那么这里请读者一定一定要把握一个原则，**`std::move`的本质是为了伪装，它并不能改变变量的左右性**。也就是说，`std::move(str1)`并不能把`str`变成rvalue，它本身是个变量，那么它就是lvalue，一直都是。`move`的作用仅仅在于，构造`str2`的时候能触发移动构造函数，仅此而已，其他的什么都没变。

那么也就是说，尽管我们用了「移动语义」来构造了`str2`，但其实`str1`还是存在的，该是什么样还是什么样，并不会真的被「移动」。而此时的`str2`是`str1`的浅复制版本，原本的话它们的`buf_`会指向同一片空间的，但因为我们在移动构造函数中强制把原来的对象`buf_`给置空了，因此这里`str1`内部会出现空指针。所以这里有一次印证了「移动语义是软约束」这件事，使用之后行为如何，会不会出问题，完全取决我们代码怎么写的。

## 总结

还有一个概念笔者一直都没有提，那就是glvalue（广义左值，Generalized Left-side-hand Value），lvalue和xvalue合称glvalue，原因就是他们都有内存实体。但其实这个概念并不常用，主要是因为xvalue虽然有内存实体，但是无法直接取地址，因此在主框架的设计中，还是把xvalue当做rvalue来处理了。

C++之所以会出现这么多难搞的值类别，就是为了在兼容C方式的同时，提供一种更高级的语义封装。所以C++纠结就纠结在这里，一方面希望提供一些高级的语法，让程序员可以屏蔽掉一些底层的概念。另一方面反倒又引入了奇怪的概念让程序员不得不去深入理解底层。所以笔者自己对C++的经验就是，学习的时候要「深」，一定要搞清底层；而实际使用的时候要「高」，应当使用更加符合直觉的高级语法来屏蔽底层实现。

本篇文章并没有直接去按理论列举C++有哪些值类型，分别是什么定义。而是带着大家从汇编指令出发，一点一点的去猜测和体会这样设计的初衷和底层原理，希望能够给读者提供一些不同角度的理解和不一样的思路。
