
<!--BEGIN_DATA
{
    "create_date": "2023-03-08 18:30", 
    "modify_date": "2023-03-08 18:30", 
    "is_top": "0", 
    "summary": "彻底征服C++模板", 
    "tags": "C/C++", 
    "file_name": "彻底征服C++模板.md"
}
END_DATA-->

#### <p>原文出处：<a href='https://km.woa.com/articles/show/572661' target='blank'>彻底征服C++模板</a></p>

## 前言

模板是C++体系中非常重要的一环，由其衍生的模板编程体系也算得上是C++特色，但也因为它学习门槛较高，语法很奇怪、反直觉让人望而却步。

笔者也经常碰到有人问我类似于「C++不写模板难道就不行吗？」「我们团队直接禁止写模板，我也没觉得对我的开发有什么影响啊。」「你这些特性我不用模板也能实现啊。」之类的问题。笔者仍然持有「困难的东西我们应当攻克下，再去客观评判其合理性。而不是为自己的逃避找开脱的理由」的态度，与此同时，笔者还认为「“能做”并不代表“适合”」，工具是用来帮助我们提升效率的，只有当我们充分了解了，才能判断何为「适用的场景」，从而真正让工具为我们的工作提供服务。因此感觉非常有必要出一篇完整且详细讲解C++模板编程的教程，来打通你的任督二脉。

本系列文章将会介绍如下的内容：

> 1. C++模板的基础知识，包括基础的语法和用法
> 2. C++模板的进阶知识，包括模板编译方式、特化和SFINAE法则
> 3. 模板元编程，这里会讲解其的思路和体系结构，并用一个手撸variant的项目作为终极实例
> 5. 「模板范式」的概念和其设计理念
> 6. 一些读者关心的问题的解答以及笔者的心得体会

一些说明：

> - 本文编写时C++20标准已经发行了一段时间了，但在业界还并不成熟，编译器对C++20标准的支持参差不齐，并且C++20标准的权威文档、示例等也比较匮乏，目前很少有团队在生产环境推行C++20标准的。因此出于这样大环境的考虑，本文主要以C++17为默认的标准，重点介绍的也是C++17标准下的各种情况，对于C++17、C++14、C++11和C++98则不会做特别的标注和区分。而对于C++20上会有比较重大变化，或是其他涉及C++20标准的点时会特别标注出来。
> - 「使用了模板」跟「模板元编程」是两回事，模板元编程是一套理论体系，模板仅仅是C++的一种语法类型。本文会先介绍模板的用法，然后也会介绍模板元编程。
> - 本文不是C++语言的入门教程，也不适合从来没有见过C++模板的读者，作为C++进阶性的用法，模板可以认为比基础C++语言更高一个层次，需要读者至少有C++语言的基础。本文更适合有稍微「涉猎」过C++模板编程，对它虽有些许支离破碎的理解和感悟，但希望建立一个完整、宏观的视角的读者，那么本篇文章会帮助你把这些碎片全部穿起来，建立一个完整的世界观，让你对C++模板的认识更上一层楼。
> - 本文在创作时原本的标题是《C++模板元编程详细教程》，但是后来发现其内容并不局限于模板元编程，而是帮助读者由浅入深从模板的基础概念开始建立，并把模板元编程仅作为了其中一个子单元存在，更加注重「穿线」和「引导」，因此将其更名。
> - 如果读者有任何问题，欢迎在评论区指正。笔者在后续发现文章问题的时候也会持续更正。

## C++模板的基础用法

### 模板的概念

「模(mú)板」原本是工程上的概念，我们用「浇注」这个工序更好理解。首先你得有个模具，里面是空心的，空心的形状正好是最终工件的形状。然后我们把铁水浇注进去，等冷却后，打开模具，取出里面的工件。

从上面的例子我们可以总结出这么两个要点：

模具本身不是工件，得用模具来生成工件

最终的工件材料取决于浇注进去的材料（比如说浇注铁水出铁件，浇注铝水就出铝件），模具只决定工件的形状

类比到C++的模板也是一样的：

模板本身不是实际代码，得用模板来生成代码（这个过程叫「实例化」）

用模板实例化的代码取决于模板参数，模板本身只是一个「实例化的方式」（这一点能够解释很多时候为什么模板本身没有报错，但是实例化后报错了。）

那么这里我们能够看到模板拥有2个要点：「参数（类比工件材料）」和「实例化方式（类比工件形状）」

### 写一个hello world级别的模板

有了上一节的2个要点，我们自然而然就可以引出模板的基本语法，下面展示一个最简单的模板：

```cpp
template <typename T>
void show(T t) {
  std::cout << t << std::endl;
}
```

`template`是模板关键字，表示后面即将定义一个模板。后面尖括号中的就是「模板参数」，这就是模板的第1个要点。之后的所有内容叫做「模板实现」，对应模板的第2个要点。

详细一点来解释就是，上面定义了一个「定义函数的方法」，参数中的`T`就是「材料」。把「材料」浇注到「模具」中就可以形成工件，也就是说，指定了「参数」的「模板函数」就可以形成「函数」。

那么使用模板的方法，就是给模板传递参数，使其实例化成为一个可实际调用的代码。以上面的例子来讲就是：

```cpp
void Demo() {
  show<int>(5); // 首先实例化show<int>函数，然后再调用show<int>函数
}
```

这里请读者一定一定要建立一个概念，模板本身并不是可使用的代码，必须实例化以后才是。也就是说，这里的`show`**并不是函数**，而是「模板函数」。「模板函数」经过**实例化**后才能成为「函数」，而函数才能直接调用。

那么上面使用模板就分了2个步骤。首先，给模板函数`show`指定参数，将其实例化成`show<int>`，成为一个函数。那么，这个`show<int>`函数怎么定义呢？那就要看模板是怎么实现的了（这就是前一节说的，模板其实规定了实例化的方式）。因此，我们这里得到的函数是：

```cpp
void show<int>(int t) {
  std::cout << t << std::endl;
}
```

第二步才是调用这个函数，所以这里尖括号中的`int`是模板参数，而小括号中的`5`则是函数实参。

请读者先熟悉并接受上面的理念，更加详细和深入的内容会在后面章节逐渐展开。

### 模板的分类

要问C++模板有哪些分类，倒不如问「哪些语法可以用模板生成」。按照这个维度，我们可以将模板分为：

> \- 模板类  
\- 模板函数  
\- 模板全局常量  
\- 模板类型重命名

接下来会简单展示一下各种类型的语法和大致用法。**注意：下面很多例程可能都不是非常准确，这里是为了方便读者理解才写的一个简化版本，不能够直接投入使用。**

#### 模板类

顾名思义，模板类就是用于生成「类」的模板。不过这里的「类」并不是单指`class`，我们知道在C++中，`class`和`struct`的区别仅仅在默认权限上，因此几乎都可以互相代替，不过这仅仅实在「语法」上。在实际使用中，我们更在意它直观表达的「语义」，因此对于纯数据类型的组合，一般更习惯用`struct`，而对于带有操作的自定义类型（或者理解为OOP中的「抽象」），一般更习惯用`class`。比如我们可以写一个模板`struct`：

```cpp
template <typename T1, typename T2>
struct Test {
  T1 t1;
  T2 t2;
};
```

只不过照着这种习惯来讲，「纯数据类型组合」似乎并没有太多写成模板的价值，所以对于模板类来说，`class`和`struct`的使用习惯还有那么一点不同。在模板类中，如果是用于「生成对象」的模板类，我们更习惯用`class`，而对于「模板元编程」的静态语言描述中，我们更习惯用`struct`。由于我们还没有详细介绍什么是「模板元编程」，因此读者暂且不必过多纠结，只需要知道`struct`关键字的模板也属于模板类就可以了。

下面例程就是一个简单的模板类和实例化调用的例子：

```cpp
template <typename T, size_t size>
class Array {
 public:
  Array();
  T &at();
  size_t size() const;
 private:
  T data_[size];
};

void Demo() {
  Array<int, 5> arr; // 实例化，并创建对象
  arr.at(1) = 6;
}
```

关于实例化的步骤，读者可以参考「写一个hello world级别的模板」章节中的描述。

刚才我们说，`class`和`struct`都可以模板化，成为模板类。那`union`呢？其实`union`跟`struct`是基本类似的，唯一的区别在于成员共享首地址。因此从语法上来说，同样是支持`union`模板的:

```cpp
template <typename T1, typename T2>
union Test {
  T1 m1_;
  T2 m2_;
};
```

只不过这种用法就跟「纯数据类型组合」的`struct`写成模板后类似，虽然语法上可行，但实际使用场景真的寥寥无几就是了（当然，一些炫技的骚操作除外，后面章节会详述）。

#### 模板函数

模板函数就是用模板生成一个函数，主体是一个函数。当然，普通函数、成员函数、包括lambda表达式都是可以写成模板的。下面就一口气给出这几个语法的例程：

```cpp
// 普通模板函数
template <typename T>
void show(const T &item) {
  std::cout << item << std::endl;
}

class Test {
 public:
  // 模板成员函数
  template <typename T>
  void mem_func(const T &item) {}
};

// 模板lambda表达式（只能是全局变量承载）
template <typename T>
auto f = [](const T &item) {}
```

实例化和使用的方式大致如下：

```cpp
void Demo() {
  show<int>(5);
  Test t;
  t.mem_func<double>(5.1);
  f<char>('A');
}
```

#### 模板全局常量

模板的全局常量一般是由一个模板类来做「引导」的，而且由于模板必须在编译期实例化，因此模板全局常量一定也会在编译期**有一个确定的值**，必须由`constexpr`修饰，而不可以是「变量」（不加`constexpr`的模板全局变量虽然语法允许，但并不完全符合模板定义的初衷，它更像是「生成不同类型的全局变量的一种语法糖」，远不及模板全局常量的意义大，所以暂时请读者建立「模板全局变量必须是常量表达式」的印象）。

下面给出一个例程：

```cpp
// 用于引导模板全局常量的模板类(用于判断一个类型的长度是否大于指针)
template <typename T>
struct IsMoreThanPtr {
  static bool value = sizeof(T) > sizeof(void *);
};

// 全局模板常量
template <typename T>
constexpr inline bool IsMoreThanPtr_v = IsMoreThanPtr<T>::value;
```

这样的用法在后面章节所要介绍的「模板元编程」中非常重要的作用，后续会详细介绍。

#### 模板类型重命名

C++中的类型重命名主要有两种语法，一种是`typedef`，另一种是`using`，它们都支持模板生成，效果是相同的。

模板类型重命名可以直接借用一个模板类来做「偏特化」，或者也可以像模板全局常量一样由一个模板类来引导，请看下面例程：

```cpp
// 普通的模板类
template <typename T, size_t size>
class Array {};

// 偏特化作用的模板类型重命名
template <typename T>
using DefaultArray = Array<T, 16>;

// 也可以作用给typedef语法
template <typename T>
typedef DefaultArray<T *> DefaultPtrArray;

void Demo() {
  DefaultArray<int> arr1; // 相当于Array<int, 16> arr1;
  DefaultPtrArray<char> arr2; // 相当于Array<char *, 16> arr2;
}
```

再展示一个由模板类做引导的例子：

```cpp
// 用于引导的模板类
template <typename T>
struct GetPtr {
  using type = T *;
};

// 用模板类引导的模板类型重命名
template <typename T>
using GetPtr_t = typename GetPtr<T>::type;
void Demo() {
  GetPtr_t<int> p; // 相当于typename GetPtr<int>::type p; 也相当于int *p;
}
```

上面这种写法同样在模板元编程中非常重要，后续章节会详细讲解。

### 模板参数

在上一章节中，我们展示了几种基本的模板语法，相信读者也注意到了在例程中展示的一些模板参数。那么这一节笔者将详细介绍模板参数。

C++的模板参数主要分为三种：

> 1\. 类型  
2\. 整数（或整数的衍生类型）  
3\. 模板

类型好理解，就是这个参数要求传入某种「数据类型」。整数也好理解，就是字面意思。但这个「整数的衍生类型」还有「模板参数模板」就比较有趣且复杂了，下面我们来逐一攻克。

#### 类型模板参数

模板参数中最常用的就是这里的类型了，用于传递一个类型来实例化模板。关键字是`typename`。先看一个简单的例子：

```cpp
template <typename T>
void show(T t) {
  std::cout << t << std::endl;
}
```

`show`是一个模板函数，接受1个参数`T`，并且它是一个类型参数。实例化的时候，就需要在`T`的位置传入一个类型标识符（例如`int`、`void*`或者`std::string`）。

```cpp
void Demo() {
  show<int>(5);
  show<void *>(nullptr);
  show<std::string>("abc");
}
```

这里值得一提的是，在早些版本的C++中，用于表示类型参数的关键字是`class`，但是这个关键字可能会产生歧义，让人觉得这里必须要传一个「类」类型。但其实并不是这样的，基本类型也是OK的。所以后续又支持了`typename`关键字来表示类型参数，更加贴近语义一些。不过`class`也保留下来了，现在用来表示「模板的类型参数」这里，两个关键字是相同的，没有区别。所以上面的例程也可以写作：

```cpp
template <class T>
void show(const T &t) {
  std::cout << t << std::endl;
}
```

正如上面例程展示的这样，类型模板参数除了直接使用以外，还可以和其他符号（比如`*`、`&`、`&&`、`const`等）进行组合。

#### 整数

我们在前面的章节也展示过整数作为模板参数的情况，当时的例子是：

```cpp
template <typename T, size_t size>
class Array {
  // ...
 private:
  T data[size];
};
```

那么这里的`size`就是整数，当然不止`size_t`类型，一切整型都是支持的，比如说`int`、`short`、`char`，甚至`bool`都是可以。

但这里需要再次强调一点，我们多次强调的一个问题，模板是编译期语法，因此，这里的整型数据也必须是编译期能确定的，比如说常数、常量表达式等，而不可以是动态的数据。请看下面例程：

```cpp
// 整数参数的模板
template <int N>
struct Test {};

void Demo() {
  Test<5> t1; // 常数OK
  constexpr int a = 5;
  Test<a> t2; // 常量表达式OK

  const int b = 6;
  Test<b> t3; // ERR，b是只读变量，不是常量
  Test<a * 3> t4; // 常数运算OK

  std::vector<int> ve {1, 2, 3};
  Test<ve.size()> t5; // ERR，size是运行时数据
  Test<ve[1]> t6; // ERR，ve的成员是运行时数据

  int arr1[] {1, 2, 3};
  Test<arr1[0]> t6; // ERR，arr1的成员是运行时数据
  constexpr int arr2[] {2, 4, 6};
  Test<arr2[1]> t7; // 常量表达式修饰的普通数组成员OK
}
```

所以请读者把握一个原则，就是只有编译期能够确定的量，才能用来实例化模板。

在C++20以前，只允许整数参数，但从C++20起，可以支持浮点数做参数，同样，只要是编译期能确定的量就OK：

```cpp
// C++20标准：
template <double C>
struct Test {};
```

#### 整数的衍生类型

说到整数的衍生类型，也就是说「可以用整数表示」，或者说「本质上是整数」的类型。

##### 指针类型

这里面最经典的就是指针，请看下面例程：

```cpp
template <int *p>
void f(int data;) {
  *p = data;
}
```

不过这里实例化时能够支持的数据就很有说头了。既然我们说指针是整数的衍生类型（指针本质就是地址，地址就是个整数），那么规则自然也是跟整数的规则是一样的，要「编译期能够确认的值」。

只不过，对于指针来说，「编译期能够确认的值」就应该指的是「编译期能够确定的地址」。但这显然是个伪命题，因为编译期根本不存在地址的概念，程序在只有在进程预加载的时候才会确定所有变量的地址。所以这个问题需要我们换一个角度来看。**如果说某一个变量，它的地址在程序运行期间能够一直不发生改变，或者说它不会中途被释放**的话，我们就认为这个变量的地址是「确定的」。或者说，这个地址一旦确定要给这个变量来使用，那么它就一直都会给它使用，而不会中途变成交给其他变量。

沿着这个思路，只要是「程序运行中确定的」地址，就可以用来实例化模板。下面给出一些实例：

```cpp
int a = 1; // 全局变量

class Test {
 public:
  int m1; // 成员变量
  static int m2; // 静态成员变量
};

int Test::m2 = 4;

void Demo() {
  int b = 2; // 局部变量
  static int c = 3; // 静态局部变量
  f<&a>(0); // OK，a是全局变量，程序运行期间不会被释放
  f<&b>(0); // ERR，b是局部变量，在局部代码块运行完毕后会被释放，所以说b的地址也有可能不仅仅表示b，回收后可能会表示其他数据，所以不可以
  f<&c>(0); // OK，c是静态局部变量，不会随着代码块的结束而释放
  f<&Test::m1>(0); // ERR，Test::m1其实并不是变量，要指定了对象才能确定，因此是非确定值，所以不可以
  f<&Test::m2>(0); // OK，Test::m1本质就是一个全局变量，在程序运行期间不会被释放，所以OK
}
```

希望读者能够通过上面的例子来理解什么是「不变的地址」，其实并不说是说地址不可变，因为地址本身就是不可变的。这里说的是，这个地址一直只表示确定的数据，而不会改变（不会被释放后重新分配给其他数据）。

##### 函数类型

既然讲到指针类型，那我们也逃不开一类特殊的指针——函数指针。函数指针其实本质上也是地址，所以同样属于整数的衍生类型。而分配给函数（指令段）的地址在程序执行过程中就是不会变的，但如果用的是变量的值那么同样会因为动态数据问题而报错。

文字解释不直观，我们还是来看例程：

```cpp
// 函数指针类型模板参数
template <void (*func)()>
void f() {
  func();
}

// 普通函数
void f1() {}
class Test {
 public:
  void f2() {} // 成员函数
  static void f3() {} // 静态成员函数
};

void Demo() {
  void (*pf1)() = &f1; // 局部变量
  constexpr void (*pf2)() = &f1; // 常量表达式
  f<&f1>(); // OK，函数本身就是地址不可变的
  f<&Test::f2>(); // ERR，虽然成员函数也是地址不可变的，但&Test::f2的类型是void (Test::*)()，类型不匹配所以报错
  f<&Test::f3>(); // OK，静态成员函数是地址不可变的，类型也匹配
  f<pf1>(); // ERR，pf1是静态数据，编译期值不确定，所以不可以
  f<pf2>(); // OK，用常量表达式修饰的在编译期可以确定，所以可以
}
```

在C语言中，直接使用函数名其实就会转义为函数指针类型。但C++引入了「函数类型」的概念，它在很多时候也是可以转换为函数指针类型的。那么在模板参数中，同样也支
持了「函数类型」，用法跟上述函数指针类型完全相同，并且还可以跟函数指针类型互用：

```cpp
// 函数类型模板参数
template <void func()>
void f() {
  func();
}

// 普通函数
void f1() {}
class Test {
 public:
  void f2() {} // 成员函数
  static void f3() {} // 静态成员函数
};

void Demo() {
  void (*pf1)() = &f1; // 局部变量
  constexpr void (*pf2)() = &f1; // 常量表达式
  f<f1>(); // OK
  f<&f1>(); // OK
  f<Test::f3>(); // OK
  f<&Test::f3>(); // OK
  f<pf2>(); // OK
  // 与前一例程相同，不再赘述
}
```

同样地，「函数类型」本身就可以隐式转换为「函数指针类型」，因此使用上都是互通的，就不再赘述了。不过这里提前剧透一下，虽然在大多数情况下函数类型和函数指针类型都可以互转，没有明显区别，但在一种特殊场景下二者会有着天壤之别，详情会在后续介绍到模板偏特化的章节中提到。

#### 模板类型

这个类型非常容易让人晕菜，所谓「模板类型的模板参数」，其实就是嵌套模板的意思，把「某一种类型的模板」作为一个参数传给另一个模板。请看示例：

```cpp
// 模板类型的模板参数
template <template <typename, typename> typename Tem>
void f() {
  Tem<int, std::string> te;
  te.show();
}

// 符合条件的模板类
template <typename T1, typename T2>
struct Test1 {
  void show() {std::cout << 1 << std::endl;}
};

template <typename T1, typename T2>
struct Test2 {
  void show() {std::cout << 2 << std::endl;}
};

// 不符合条件的模板类
template <int N>
struct Test3 {
  void show() {std::cout << 3 << std::endl;}
};

void Demo() {
  f<Test1>(); // 注意这里，要传模板，而不是实例化后的模板
  f<Test<int, int>>(); // ERR，模板参数类型不匹配
  f<Test2>(); // OK
  f<Test3>(); // ERR，类型不匹配
}
```

上述例子中，模板函数`f`接受一个参数，这个参数需要是一个模板类型，并且是一个「含有2个类型参数的模板」类型。

在实例化的示例中，`Test1`和`Test2`都是`template <typename, typename>`类型，所以可以用来实例化`f`。

而实例化后的`Test<int, int>`已经是一个普通类型了，也就是说它是一个`typename`类型，而不是`template <typename, typename>`类型，所以不匹配。同理，`Test3`是`template <int>`类型，也不是`template <typename, typename>`类型，所以不匹配。

### 变参模板

所谓的「变参」指的是「参数数量可以是任意的」，变参模板并不是独立的一种类型参数，我们可以认为它是「一组参数」，可以是一组类型参数，也可以是一组非类型参数。

先举一个例子来直观感受一下变参模板，我们写一个支持任意个数的参数相加的函数：

```cpp
template <typename... Args>
auto sum(Args... args) {
  return (... + args);
}

// 以下是测试Demo
void Demo() {
  auto a = sum(1, 2, 3, 4); // 10
  auto b = sum(1.5, 2, 3l); // 6.5
  auto c = sum(std::string("abc"), "def", "111"); // std::string("abcdef111")
  auto d = sum(2); // 2
}
```

相信读者不难看得出，这三个点就表示变参，不过三个点书写的位置是有讲究的，不同的位置表示的含义也略有不同。在上面的例子中，模板参数含有一个`typename... Args`，其中的三个点顿在了`typename`后面，表示这是一组类型参数，可以叫它「包（pack）」，而后面的`Args`就是这个「包」的名字。那么我们就知道，`Args`代表的并不是一个单一类型，而是一组类型参数组成的包。注意，模板的变参结构跟其他变参结构类似，都是只能出现一次，并且必须在列表最后，否则会造成解析的歧义。同时，变参结构在实际传递时，参数可以为空。

在函数参数中，可以看到有个`Args...`，由于`Args`本身是个包，那么给包后面加三个点表示「解包（Unpack）」，或者叫「展开（Unfold）」。所以参数中的解包，我们可以解读为，把`Args`中的每一个类型，平铺开，每一个类型都要对应一个函数的入参。而后面的`args`代表的就是这一组参数，它同样是一个「包」，但它则是由形参（本质就是局部变量）组成的包。

函数体中，可以看到出现了`(... + args)`的表达式，大家应该能猜到，这也是一种「解包」的语法，但这属于「按符号解包」的方式，与之对应的还有一种「直接解包」的方式，下面来分别讲解。

#### 变参的直接展开

所谓「直接展开」，其实指的是按「逗号」展开，逗号不仅仅指逗号运算，任何以逗号为分割符的地方都支持变参的展开。比如说，给一片自定义的内存资源池适配一个创建对象的方法，就可以这样来写（简化一下，先不考虑左右值传递的问题）：

```cpp
std::byte memory[16384]; // 这是一片内存资源池
void *head = memory; // 可用空间的头指针

// 在内存资源池上创建对象的函数
template <typename T, typename... Args>
T &Create(Args... args) {
  auto &obj = *new(head) T(args...);
  head += sizeof(T);
  return obj;
}
```

这里就是一个非常典型的直接展开的例子，展开后的参数会用逗号隔开。比如说我们这样调用：

```cpp
struct Test {
  Test(int, double) {}
};

void Demo() {
  auto test = Create<Test, int, double>(1, 2.5); // 会通过Test(int, double)构造函数构造
}
```

上面实例化的`Create<Test, int, double>`类型，首先模板参数在展开的时候，`Args`中含有两个类型，分别是`int, double`，这里就是用逗号展开的。后面的`args`中也是含有两个变量，同样是按照逗号隔开，所以其实实例化后的函数是这样的：

```cpp
Test &Create(int arg1, double arg2) {
  auto &obj = *new(head) Test(arg1, arg2);
  head += sizeof(Test);
  return obj;
}
```

#### 变参的嵌套展开

刚才我们介绍的是直接展开，但有时可能我们要在变参的基础上嵌套一个什么结构，然后再展开的，比如说：

```cpp
// 把数组中的某些角标元素取出来，组成新数组
template <typename T, int... N>
std::vector<T> GetSubVector(const std::vector<T> &src) {
  return std::vector<T> {src.at(N)...};
}

// 示例Demo
void Demo() {
  std::vector<int> ve {0, 11, 22, 33, 4};
  auto ve2 = GetSubVector<int, 1, 4, 1, 3, 0>(ve);
  // 执行后ve2会变成{11, 4, 11, 33, 0}
}
```

上面这个例子中，`N`是一个包，并且是整数包，对它展开的时候就没有用`N...`这样直接展开，而是加了一层结构，按照`src.at(N)...`的方式展开。这样展开后，每一个参数都会嵌套相同的结构，并且它们之间也是用逗号隔开的。所以`GetSubVector<int, 1, 4, 1, 3, 0>`其实会实例化成：

```cpp
std::vector<int> GetSubVector(const std::vector<int> &src) {
  return std::vector<int> {src.at(1), src.at(4), src.at(1), src.at(3), src.at(0)}; // N的嵌套方式展开
}
```

#### 按照符号展开

在C++17以前，变参只可以用逗号展开。回到一开始的例子，我们来实现任意个数的数相加，如果只能逗号展开，那么我们只能把它展开成函数参数，进行递归传递：

```cpp
// 递归终止条件（只有1个参数的情况）
template <typename T>
auto sum(T arg) {
  return arg;
}

// 2个以及以上的情况要进行递归
template <typename Head, typename... Args>
auto sum(Head head, Args... args) {
  return head + sum<Args...>(args...);
}
```

为了递归，我们就需要强行把第一个参数分离出来，并且还要写一个只有一个参数的特殊情况。下面来看一下调用的示例：

```cpp
void Demo() {
  auto a = sum<double, int, int, double>(1.5, 2, 2, 1.6);
}
```

首先，`sum<double, int, int, double>`不符合只有1个参数的条件，所以会命中下面的模板，实例化后的样子是：

```cpp
auto sum(double head, int arg0, int arg1, double arg2) {
  return head + sum<int, int, double>(arg0, arg1, arg2);
}
```

它会要求调用一个`sum<int, int, double>`函数，所以会继续实例化：

```cpp
auto sum(int head, int arg0, double arg1) {
  return head + sum<int, double>(arg0, arg1);
}
```

又会要求调用一个`sum<int, double>`，继续实例化：

```cpp
auto sum(int head, double arg0) {
  return head + sum<double>(arg0);
}
```

又会要求调用一个`sum<double>`，但是此时，命中了上面的模板定义，所以会按照上面的方式来实例化，变成：

```cpp
auto sum(double arg) {
  return arg;
}
```

到此截止，实现了一串数相加。这里提到的递归是模板实例化层面的递归，也就是递归生成模板实例化，而不是传统意义上的函数递归调用，这部分的详情在后面的章节还会有更加深入的介绍，当前只希望读者知道，在C++17以前，实现这种若干数相加的模板其实是不太容易的，需要借助这种模板递归。

但是在C++17提供了另一种变参展开方式，就是按照一个特定的符号展开（而不是逗号），可以极大程度上简化问题，增加代码可读性。这种按照符号展开的语法又被称为「折叠表达式」。我们再来看看一开始那个例子：

```cpp
template <typename... Args>
auto sum(Args... args) {
  return (... + args);
}
```

这里的`(... + args)`就是折叠表达式，表示按照加号展开。我们知道，运算符是有优先级和合并顺序的，因此要按符号展开，就必须指定这种展开顺序，换句话说，`((a ⊕ b) ⊕ c)`和`(a ⊕ (b ⊕ c))`到底选哪一种的问题（这里的「 ⊕ 」代指任意二元运算符）。

对于这个问题，C++的解决方案是通过变参包名和三个点的位置来示意（注意，这里就是一种强行的规定，没什么道理可言），三个点在左的，表示从左到右合并；三个点在右边的，表示从又到左合并。也就是：

```cpp
(... + args)
```

会展开为

```cpp
((((arg0 + arg1) + arg2) + ...) + argn)
```

而反过来的：

```cpp
(args + ...)
```

则会展开为

```cpp
(arg0 + (arg1 + (... + (argn_1 + argn))))
```

注意，**折叠表达式两端必须有括号！**。

我们刚才提到，折叠表达式只支持二元运算符，既然是二元运算符，如果遇到只有一个参数的时候怎么办呢？这时这个符号会被忽略，直接返回原值，所以`sum<int>`就会实例化为：

```cpp
auto sum(int arg) {
  return arg;
}
```

这就是我们使用折叠表达式不需要单独定义递归截止条件的原因。

说到二元运算符，就不得不聊到另一个问题，假如说我并不是希望仅仅包内的内容自行结合，而是要结合一个额外的内容呢？举例来说：

```cpp
// 实现一个输出打印任意参数的功能
template <typename... Args>
void Show(Args... args) {
  std::cout << (... << args); // 想想，如果这样写是对的吗？
}
```

上例中，并不是希望把所有参数自行通过左移运算得出后的结果去输出的，而是要「把第一个参数先跟`cout`结合，第二个参数应当跟前面的运算结果（同样还是`cout`）再集合，之后都是依次跟前面的结合」。所以这个需求下，`cout`就成了一个要参与表达式展开的一个内容了，所以C++提供了这种情况下的解决方法，就是把这个额外的操作数也写进折叠表达式：

```cpp
template <typename... Args>
void Show(Args... args) {
  (std::cout << ... << args); // 注意括号还是不能丢
}
```

那么上面的表达式展开后就变成了：

```cpp
((((std::cout << arg0) << arg1) << ...) << argn)
```

这样就强行让`cout`也参与了表达式的展开。我们知道`cout`其实是`std::ostream`的一个实例，其左移运算对应的函数原型是：

```cpp
class ostream {
 public:
  template <typename T>
  std::ostream &operator <<(T &&);
};
```

也就是说，`cout`和任何一个数据发生运算后，仍然会返回`cout`本身，所以按照上面的方式展开后，的确可以让`cout`依次和所有的变参相结合，达成我们「逐一输出」的目的。

我们把这种有额外内容参与的展开方式称为「二元展开」，相对的，前面那种方式就叫「一元展开」。注意，这里的「一元」「二元」并不表示运算符，因为不管是一元展开还是二元展开，都只能用二元运算符展开。这里的几元表示的是参与展开的成员有几个，如果只有一个包，自己内部展开的，就叫「一元展开」；而这种除了一个包，还需要一个额外内容参与展开的，就叫「二元展开」了。

同理，二元展开也有向右展开的版本：

```cpp
(args ⊕ ... ⊕ obj)
```

这种的就会从右开始结合。所以大家一定要注意，二元展开中，那个额外的内容，一定要写在三个点的同一侧（毕竟三个点的方向表示展开的方向），否则无意义。例如下面的折叠表达式中，有两个就是无意义的：

```cpp
(a + ... + args); // 二元展开，从左侧开始，先与a结合
(args ^ ... ^ a); // 二元展开，从右侧开始，先与a结合
(a - args - ...); // ERROR！语法错误
(... & args & a); // ERROR！语法错误
a - (args - ...); // 一元展开，展开后再与外面的内容进行运算
(... & args) & a; // 一元展开，展开后再与外面的内容进行运算
```

变参展开在后续内容中非常常见，也是极其重要的内容，请读者一定要理解其用法。

## C++模板进阶知识

### 模板参数自动推导

前面的篇幅我们讲解了C++模板的基本用法，并且强调了模板并非直接可用的代码，需要经历「实例化」，而实例化的过程其实就是指定参数的过程。

但如果模板只能通过显式指定参数来进行实例化的话，那C++模板的「威力」也就止步于此了，进而也就不会出现复杂的模板元编程体系这样的东西。所以C++模板还有一个非常重要的特性，就是模板参数的自动推导。

模板参数的自动推导主要分为3种：

> 1\. 根据函数参数自动推导（模板函数）  
2\. 根据构造参数自动推导（模板类）  
3\. 自定义构造推导（模板类）

需要强调的一点是，自动推导只能推导类型参数，而整数和整数派生参数是没法推导的，只能靠显式传入。

下面就来逐一介绍。

#### 根据函数参数自动推导

本条针对的是模板函数。再次强调，模板参数和函数参数是不同的东西，用于实例化模板的参数是模板参数，用于调用函数的参数是函数参数。直观上来说，尖括号里的是模板参数，圆括号里的是函数参数。

我们先来看一个例子：

```cpp
template <typename T>
void show(T t) {
  std::cout << t << std::endl;
}

void Demo() {
  int a = 5;
  show(a); // [1]
  show(5); // [2]
}
```

在上述例程中，`show`是一个模板函数，在下面两处标记的位置我们是直接调用`show`的，而没有指定模板参数，那么这时，就会触发模板参数的自动推导。

先来看一下`[1]`位置的调用，由于我们传入了参数`a`，编译器就会根据`a`的类型来推导模板参数`T`。在模板函数`show`的声明处，参数列表是`(Tt)`，所以`T`会根据`a`的类型来推导。那么问题来了，这里到底会推导出`int`还是`int &`还是`const int`还是`const int&`？

答案也很简单，**模板参数的自动推导是完全按照`auto`的推导原则进行的**。

也就是说，这里相当于`auto t = a;`，会推导出`int`，因此`T`会推导出`int`。

同理，针对于`[2]`位置的调用，我们传入的是一个常量`5`，照理说`int`、`const int`、`const int &`、`int &&`、`const int &&`都可以匹配，但根据`auto`的推导原则，仅仅保留「最简类型」，所以仍然会推导出`int`。

那么`[1]`和`[2]`的位置其实相当于：

```cpp
show<int>(a); // [1]
show<int>(5); // [2]
```

再次强调，**推导的原则与`auto`相同**。那么同样地，也就支持和`*`、`&`、`&&`、`const`的组合，下面给出几个实例：

```cpp
template <typename T>
void f1(T &t) {}

template <typename T>
void f2(const T &t) {}

template <typename T>
void f3(T *p) {}

void Demo() {
  f1(5); // 会报错，因为会推导出f1<int>，从而t的类型是int &，不能绑定常量
  int a = 1;
  f1(a); // f1<int>，t的类型是int &
  f2(a); // f2<int>，t的类型是const int &
  f3(a); // 会报错，因为会推导出f3<int>，此时t的类型是int *，int不能隐式转换为int *
  f3(&a); // f3<int>， t的类型是int *
}
```

这里需要注意的是，`T`是按照`auto`法则来推导的，但由于我们加上了修饰符，所以实际的函数参数`t`的类型是会带上这种描述符的，详情可以看上面例程的注释。

既然模板参数类型推导是按照`auto`法则，那就不得不提到一个特殊的推导，它就是`auto &&`。我们知道`auto &&`会根据绑定对象的左右性来推导出左值引用或是右值引用，同理对于用`&&`修饰的参数，在自动推导时也会拥有这样的特性。

换句话说，`T &&`也可以绑定可变值，此时会推导出左值引用。请看下面例程：

```cpp
template <typename T>
void f4(T &&t) {}

void Demo() {
  int a = 5;
  const int b = 10;
  f4(1); // f4<int>，t的类型是int &&
  f4(a); // f4<int &>，t的类型是int &
  f4(b); // f4<const int &>，t的类型是const int &
  f4(std::move(a)); // f4<int>，t的类型是int &&
}
```

因此，这里总结出2条规律：

> 1\. 当`T &&`匹配到可变值（也就是C++11里定义的「左值」）的时候，`T`会推导出左值引用，再根据引用折叠原则，最终实例化为左值引用  
2\. 当`T &&`匹配到不可变值（也就是C++11里定义的「右值」）的时候，`T`会推导出基本类型，最终实例化为右值引用

对于`auto &&`来说，我们只关心最终推导出的类型，并不会关心`auto`本身到底代表了什么。但对于模板的类型推导则不同，我们既要关心「模板参数推导出了什么类型」，又要关心「模板实例化后的函数参数是什么类型」。换做上面的例子来说就是，我们既要关系`T`推导出了什么，又要关心当`T`确定以后，`t`会变成什么类型。

那么按照上面的规律总结可以知道，即便我们传入的本身是一个右值引用（比如上面的`std::move(a)`），`T`依然会推导为`int`而并不是`int &&`。只不过实例化后的函数参数`t`的类型会变成`int &&`。

我相信有的读者在这里一定会产生疑问，既然「`T`推导出`int`」跟「`T`推导出`int &&`」的结果都是「`t`的类型是`int &&`」，那何必还要在此纠结呢？照目前的情况来说`f4<int>`和`f4<int &&>`可能确实看不出太大区别，但它会影响到模板的特化。如果我们定义了该种类型的特化，则会出现完全不同的行为。有关模板特化的内容将在后续章节详细讲解，请读者在此时记住，**利用函数参数自动推导出的模板参数永远不会推导出右值引用**，只可能推导出左值引用或者基本类型，这一点对于后续模板元编程是一个很重要的基础概念。

除了与引用、指针等组合外，还可以跟其他模板进行嵌套组合，编译器同样可以推导出正确的类型，请看例程：

```cpp
template <typename T>
struct Test {};

template <typename T>
void f(const Test<T> &t) {}

void Demo() {
  Test<int> t1;
  Test<char> t2;
  f(t1); // 推导出f<int>，t的类型是const Test<int> &
  f(t2); // 推导出f<char>，t的类型是const Test<char> &
}
```

这种技巧非常适用于各种模板库（比如说STL），例如我们希望把一个`vector`的内容连续地放入一个`buffer`中，就可以这样来写：

```cpp
#include <vector>
#include <cstdlib>
#include <cstddef>

template <typename T>
void CopyVec2Buf(const std::vector<T> &ve, void *buf, size_t buf_size) {
  if (buf_size < ve.size() * sizeof(T)) {
    return;
  }
  std::memcpy(buf, ve.data(), ve.size() * sizeof(T));
}

void Demo() {
  std::vector<int> ve{1, 2, 3, 4};
  std::byte buf[64];
  // 把ve的内容连续地复制到buf中
  CopyVec2Buf(ve, buf, 64); // 这里会推导出CopyVec2Buf<int>
}
```

模板函数之间还会存在重载问题，并且可能会引发二义性冲突，这部分内容将在后续章节详细介绍。

#### 根据构造参数自动推导

模板函数可以通过函数参数来自动推导，那么模板类呢？当然就是通过构造参数来推导了。

先来看一个简单的例子：

```cpp
template <typename T1, typename T2>
class Pair {
 public:
  Pair(const T1 &t1, const T2 &t2);
  void show() const;
 private:
  T1 t1_;
  T2 t2_;
};

template <typename T1, typename T2>
Pair<T1, T2>::Pair(const T1 &t1, const T2 &t2) : t1_(t1), t2_(t2) {}

template <typename T1, typename T2>
void Pair<T1, T2>::show() const {
  std::cout << "(" << t1_ << ", " << t2_ << ")" << std::endl;
}

void Demo() {
  Pair pair1{'a', 3.5}; // Pair<char, double>
  pair1.show();
  int a = 5;
  std::string str = "abc";
  Pair pair2{a, str}; // Pair<int, std::string>
  pair2.show();
}
```

上面的例子很好理解，就不过多赘述。但C++总是一种很「缺德」的语言，有的时候它的行为就是跟我们的直觉是相差甚远的，比如说：

```cpp
template <typename T>
struct Test {
  Test(const T &t) {}
};

void Demo() {
  Test t{"abc"}; // 推导出Test<char[4]>类型
}
```

是不是很无厘头？这里传入的字面量`"abc"`，所以符合我们直觉的应当是，字符串字面量会处理为一个全局区的数据，然后在局部用其地址代替，那么这里应当是`Test<const char *>`才对，但结果并不是我们想的这样的。

究其原因，我们还是要对C++的语法定义进行一些深入的研究。对于字符串字面量来说，编译器会把它识别为一个全局的字符数组，对于代码中出现的相同字符串字面量，都会用同一个全局字符数组来代替。举例来说：

```cpp
void Demo() {
  auto s1 = "abc";
  const char *s2 = "abc";
  std::string s3 = "abc";
}
```

当编译期发现有一个字符串字面量`"abc"`的时候，就会把它提取成一个全局的字符数组。所以上面的例子等价于：

```cpp
const char g_str1[] {'a', 'b', 'c'};
void Demo() {
  auto s1 = g_str1; // auto推导出const char *类型
  const char *s2 = g_str1; // 数组类型隐式转换为首元素的指针类型
  std::string s3{g_str1}; // 调用了string(const char *)构造函数
}
```

而当字符串字面量直接初始化字符数组的时候，并不会生成全局的字符数组，而是直接成为了初始化字符数组的语法糖：

```cpp
char str[] = "abc";
// 等价于
char str[] {'a', 'b', 'c', 0}; // 此时不会有g_str1之类的全局数组出现
```

因此，很多人印象中，「字符串字面量就是`const char *`类型」这个观念，其实是有一点点小问题的。因为它会被编译期理解为数组，而「数组」除了包含了首地址，还包含了长度的概念。只不过在大多数情况下，数组会“退化”成指针类型罢了。为了验证这个说法，我们做一个非常简单的小实验就好了：

```cpp
#include <iostream>

int main() {
  std::cout << sizeof("1234") << std::endl; // 5
  std::cout << sizeof(const char *) << std::endl; // 8
  return 0;
}
```

通过静态`sizeof`运算就可以验证上面的说法，因此`"1234"`其实是`const char [5]`类型，而不是`const char *`。

所以回到一开始的例子，用一个字符串字面量去实例化模板类的时候，编译器会识别为数组语法，因此把`T`推导为`char[4]`类型，而构造参数`t`就成为了`const char (&)[4]`类型，这是一个数组的引用类型。

```cpp
template <typename T>
struct Test {
  Test(const T &t) {}
};

void Demo() {
  Test t{"abc"}; // 推导出Test<char[4]>类型
}
```

但假如我们的模板类里有一些成员操作的话，就会导致这里报错，比如说:

```cpp
template <typename T>
struct Test {
  Test(const T &t): mem_(t) {}
  T mem_;
};

void Demo() {
  Test t{"abc"}; // 报错
}
```

实例化时会报错，原因就在于，构造函数中我们用`t`去初始化`mem_`，而此时`mem_`是`char [4]`类型，`t`是`const char(&)[4]`类型（本质上就是`char [4]`类型的常引用），两个数组类型是不能直接复制的，所以会报错。

但如果这时，我们显式实例化的话：

```cpp
template <typename T>
struct Test {
  Test(const T &t): mem_(t) {}
  T mem_;
};

void Demo() {
  Test<const char *> t{"abc"}; // OK
}
```

由于`Test`被强制实例化为`Test<const char *>`，那么此时`t`的类型就变成了`const char* const`类型，然后再接收字符串字面量的时候，数组类型会转化为数组首元素指针类型，也就是`const char [4]`转化为了`const char*`。而此时的`mem_`是`const char *`类型，自然就可以进行初始化的操作了（两个指针当然可以直接赋值）。

那这种情况要怎么办呢？我们能不能想办法让它不出现这种数组类型的实例化呢？答案是肯定的，那就要用到「模板参数类型推导指南」了，详见下节「自定义构造推导」。

#### 自定义构造推导

为了「促使」模板类能够按照我们希望的方式来进行类型推导并实例化，当我们发现自动的类型推导不满足需求的时候，就可以考虑添加一种自定义的构造推导，这个语法称之为「推导指南(Deduction Guide)」。

当定义了推导指南后，编译期会优先根据推导指南来进行实例化，如果没有合适的推导指南，才会根据构造函数参数来进行实例化。我们用推导指南来解决上一节实例化字符数组的问题：

```cpp
template <typename T>
struct Test {
  Test(const T &t): mem_(t) {}
  T mem_;
};

// Deduction Guide
template <typename T>
Test(T)->Test<T>;

void Demo() {
  Test t{"abc"}; // Test<const char *>
}
```

具体解释一下推导指南的语法，就是说对于类型`Test`，当构造参数是`T`的时候，我们要实例化为`Test<T>`。

相信有的读者看到这里会想，这不是废话嘛……本来不也是按这种方式推导的呀？但其实并不是！因为**推导指南会按照函数调用法则来识别**，也就是说，这里的`Test(T)`应当看做一个函数，当我们把`const char [4]`类型的参数传进函数参数的时候，就会转换为`const char*`。所以拥有了推导指南后，`T`会识别为`const char *`，再根据指南，实例化的结果就是`Test<const char *>`了。

当然了，遇到一些特殊需求（比如说你希望它推出对应的指针类型）也是可以方便地用推导指南来实现的：

```cpp
template <typename T>
struct Test {};

template <typename T>
Test(T)->Test<T *>;

void Demo() {
  int a = 0;
  Test t{a}; // Test<int *>
}
```

甚至可以做一些更定制化的组合，比如说：

```cpp
template <typename T>
struct Test {
  Test(T t) {}
};

template <typename T>
Test(T)->Test<T>;

// 如果传2个参数，按第二个走
template <typename T1, typename T2>
Test(T1, T2)->Test<T2>;

void Demo() {
  int a = 0;
  double b = 2.5;
  Test t1{a}; // Test<int>
  Test t2{a, b}; // Test<double>，注意此时调用的是Test<double>::Test(int, double)构造函数，又因为这个构造函数不存在所以会报错，可以通过偏特化解决
}
```

所以推导指南的用法远不止展示的这么简单，大家可以根据需要来发挥，另外它在后面重点介绍的模板元编程中也起了相当大的作用，希望读者可以理解渗透，打好基础。

### 模板特化

有了前面的基础，相信大家对模板编程已经有一点初步的感觉了。趁热打铁，这一章我们主要来介绍一下模板特化。

首先来看一下下面的例子：

```cpp
template <typename T>
void add(T &t1, const T &t2) {
  t1 += t2;
}
```

上面是一个简单的模板函数，用于把第二个参数的值加到第一个参数中去。这个模板函数对于基本数据类型的实例化都是没什么问题的，但是如果是字符串的话，那将会有问题：

```cpp
void Demo() {
  int a = 1, b = 3;
  add(a, b); // add<int>，调用符合预期
  char c1[16] = "abc";
  char c2[] = "123";
  add(c1, c2); // add<char *>， 调用不符合预期
}
```

这里的问题就在于，对于字符串类型（这里指原始C字符串，而不是`std::string`）来说，「相加」并不是简单的`+=`，因为字符串主要是用字符指针来承载的，指针相加是不合预期的。我们希望的是字符串拼接。

因此，我们希望，单独针对于`char *`的实例化能够拥有不同的行为，而不遵从「通用模板」中的定义。这种语法支持就叫做「特化」，或「特例」。可以理解为，针对于模板参数是某种特殊情况下进行的特殊实现。

因此，我们在通用模板的定义基础上，再针对`char *`类型定义一个特化：

```cpp
#include <cstring>
template <typename T>
void add(T &t1, const T &t2) {
  t1 += t2;
}

template <> // 模板特化也要用模板前缀，但由于已经特化了，所以参数为空
void add<char *>(char *&t1, char *const &t2) { // 特化要指定模板参数，模板体中也要使用具体的类型
  std::strcat(t1, t2);
}

void Demo() {
  int a = 1, b = 3;
  add(a, b); // add<int>是通过通用模板生成的，因此本质是a += b，符合预期
  char c1[16] = "abc";
  char c2[] = "123";
  add(c1, c2); // add<char *>有定义特化，所以直接调用特化函数，因此本质是strcat(c1, c2)，符合预期
}
```

上例简单展示了一下模板特化目标解决的问题，和其基本的语法。但其实模板特化远不止如此，它有着巨大的潜力。

模板的特化分两种情况，一种是全特化（有的地方也叫特例），一种是偏特化（有的地方也叫部分特化）。全特化相对简单一些，笔者会先来介绍。而偏特化会伴随SFINAE理论，它将会成为模板元编程最核心的理论基础。

#### 全特化与模板的链接方式

首先复习一下我们在开篇时候所提到的一个非常重要的概念。**模板本身不是可使用的代码，而是一种代码的升成方法。需要经过实例化后才能成为实际可用的代码。**比如说模板函数需要指定模板参数（可以是显式指定，也可以是编译器自动推导）实例化后，才能成为函数，同理，模板类也需要实例化后才能成为类。

然而「全特化」就是说，当**所有模板参数都指定了**的时候，才叫「全」。那么上一节中`add`的示例就是一个全特化，因为它原本只有一个模板参数，把它特化了自然是「完全」特化的。

而要谈到全特化，就不得不谈到一个非常容易踩坑的点，那就是模板的链接方式。在一个单独的.cpp文件中使用模板并不会有什么链接性问题，但如果在多个文件中都要使用呢？自然要通过「头文件声明+链接」的方式来完成了。

但模板本身又很特殊，它本身不是可用的代码，而是代码生成器，因此编译器会在编译期用模板来生成代码，注意，这个时候还没有开始链接！所以问题就产生了，假如我们按照直觉和习惯，把模板的声明和定义分文件来写，会怎么样呢？请看下面示例：

tmp.h

```cpp
#pragma once
template <typename T>
void f(const T &t); // 声明
```

tmp.cpp

```cpp
#include "tmp.h"
template <typename T>
void f(const T &t) {} // 实现
```

main.cpp

```cpp
#include "tmp.h"
int main() {
  f(1); // f<int>
  f(1.0); // f<double>
  return 0;
}
```

如果我们真的这么做了，你会发现链接时会报错。原因是这样的，我们在tmp.h中的这种写法，并不是「声明了一个模板函数」，模板函数本不是函数，是不需要声明的，大家记住模板永远是生成代码的工具。所以tmp.h中的写法是「声明了一组函数」，包括我们在`main`函数中使用的`f<int>`和`f<double>`，之所以能通过编译，就是因为tmp.h中存在它们的声明。换句话说，`template <typename T> void f(const T&);`相当于`void f<int>(const int &);`,`void f<double>(const double &);`,`void f<char *>(char *const &);`……这一系列的「函数声明」。

所以，编译是没问题的，但是链接的时候会报找不到`f<int>`和`f<double>`的实现。这是为什么呢？明明我在tmp.cpp中实现了呀！那我们来「换位思考一下」，假如你是编译器，我们知道「编译」过程是单文件行为，那么你现在来编译main.cpp，首先进行预处理，把`#include`替换成对应头文件内容，那么main.cpp就变成了:

```cpp
template <typename T>
void f(const T &t);
int main() {
  f(1); // f<int>
  f(1.0); // f<double>
  return 0;
}
```

上面的`f`是函数声明，下面编译主函数的时候，根据参数推导出了`f<int>`和`f<double>`，于是，通过上面的「模板函数声明」生成了2条实际的「函数声明」语句，也就是：

```cpp
void f<int>(const int &);
void f<double>(const double &);
```

调用都是符合声明的，OK，结束编译，我们得到了main.o。

好了，下面我们来编译tmp.cpp。同理，先做预处理，得到了：

```cpp
template <typename T>
void f(const T &t);
template <typename T>
void f(const T &t) {}
```

这时，**问题的关键点来了！**，这个模板函数`f`在当前这个编译单元中，并没有任何实例化，那么你自然就不知道应当按这个模板来生成哪些实例。所以，你**只能
什么都不做**，很无奈地生成了一个空白的tmp.o。

最后，main.o和tmp.o链接，main.o中的`f<int>`和`f<double>`都找不到实现，所以链接报错。

这就是模板的链接方式问题，由于模板都是编译期进行实例化，因此，必须在编译期就得知道需要哪些实例化，然后把这些实例化后的代码编译出来，再去参与链接，才能保证结果正确。

所以，要保证编译期能知道所有需要的实例，我们只能**把模板实现放在头文件里**。这样，每一个编译单元都能根据自己需要的实例来生成代码。也就是说，上面的代码应该改造成：

tmp.h

```cpp
#pragma once
template <typename T>
void f(const T &t);
template <typename T>
void f(const T &t) {} // 当然，文件内部没有声明依赖关系的时候，声明和实现可以合并
```

main.cpp

```cpp
#include "tmp.h"
int main() {
  f(1);
  f(1.0);
  return 0;
}
```

这时，在编译main.cpp时，就会把`f<int>`和`f<double>`的实例都编译出来，这样就不会链接报错了。

但这样会引入另一个问题，如果多个.cpp引入同一个含有模板的.h文件，并做了相同的实例化，会不会生成多份函数实现呢？这样链接的时候不是也会报错吗？

设计编译器的大佬们自然也想到这个问题了，那么解决方法就是，通过模板实例出的内容，会打上一个全局标记，最终链接时只使用一份（毕竟是从同一份模板生成出来的，每一份自然是相同的）。再换句更通俗易懂的说法就是**模板实例一定是`inline`的**，编译器会给每个模板实现自动打上`inline`标记，确保链接时全局唯一。

现在我们再回头看一下全特化模板，全特化模板已经是**实例化过**的了，因此并不会出现编译期不知道要怎么实例化的问题。如果这时我们还把实现放在头文件中会怎么样？

tmp.h

```cpp
#pragma once
template <typename T>
void f(T t) {} // 通用模板
template <>
void f<int>(int t) {} // 针对int的全特化
```

t1.cpp

```cpp
#include "tmp.h"
void Demo1() {
  f(1); // f<int>
}
```

t2.cpp

```cpp
#include "tmp.h"
void Demo2() {
  f(1); // f<int>
}
```

我们再来当一次编译期。首先编译t1.cpp，预处理展开，得到了`f<int>`的实现，所以把`f<int>`编译过来，输出t1.o。同理，编译t2.cpp后，也会有一份`f<int>`的实现在t2.o中。最后链接的时候，发现`f<int>`重定义了！

因此我们发现，**全特化的模板其实已经不是模板了**，在这里`f<int>`会按照普通函数一样来进行编译和链接。所以直接把实现放在头文件中，就有可能在链接时重定义。解决方法有两种，第一种就是我们手动补上`inline`关键字，提示编译期要打标全局唯一。

tmp.h

```cpp
#pragma once
template <typename T>
void f(T t) {} // 通用模板，编译器用通用模板生成的实例会自动打上inline
template <>
inline void f<int>(int t) {} // 针对int的全特化，必须手动用inline修饰后才能在编译期打标保证链接全局唯一
```

第二种方法就是，当做普通函数处理，我们把实现单独抽到一个编译单元中独立编译，最后在链接时才能保证唯一：

tmp.h

```cpp
#pragma once
template <typename T>
void f(T t) {} // 通用模板
template <>
void f<int>(int t); // 针对int的全特化声明（函数声明）
```

tmp.cpp

```cpp
#include "tmp.h"
template <>
void f<int>(int t) {} // 函数实现
```

之后，`f<int>`会随着tmp.cpp的编译，单独存在在tmp.o中，最后链接时就是唯一的了。

另外，对于特化的模板函数来说，参数必须是按照通用模板的定义来写的（包括个数、类型和顺序），但对于模板类来说，则没有任何要求，我们可以写一个跟通用模板压根没什么关系的一种特化，比如说：

```cpp
template <typename T>
struct Test { // 通用模板中有2个成员变量，1个成员函数
  T a, b;
  void f();
};

template <>
struct Test<int> { // 特化的内部定义可以跟通用模板完全不同
  double m;
  static int ff();
}
```

#### 偏特化

偏特化又叫部分特化，既然是「部分」的，那么就不会像全特化那样直接实例化了。偏特化的模板本质上还是模板，它仍然需要编译期来根据需要进行实例化的，所以，在链接方式上来说，全特化要按普通函数/类/变量来处理，而偏特化模板要按模板来处理。

先明确一个点：**模板函数不支持偏特化**，因此偏特化讨论的主要是模板类。

我们先来看一个最简单的偏特化的例子：

```cpp
template <typename T1, typename T2>
struct Test {};
template <typename T>
struct Test<int, T> {};
```

上面代码就是针对`Test`模板类，第一个参数为`int`时的「偏特化」，那么只要是第一个参数为`int`的时候，就会按照偏特化模板来进行实例化，否则会按照通用模板进行实例化。为了方便说明，我们在通用模板和偏特化模板中加一些用于验证性的代码：

```cpp
#include <iostream>
template <typename T1, typename T2>
struct Test {
};

template <typename T>
struct Test<int, T> {
  static void f();
};

template <typename T>
void Test<int, T>::f() {
  std::cout << "part specialization" << std::endl;
}

void Demo() {
  Test<int, int>::f(); // 按照偏特化实例化，有f函数
  Test<int, double>::f(); // 按照偏特化实例化，有f函数
  Test<double, int>::f(); // 按照通用模板实例化，不存在f函数，编译报错
}
```

偏特化模板本身仍然是模板，仍然需要经历实例化。但偏特化模板可以指定当一些参数满足条件时，应当按照指定方式进行实例化而不是通用模板定义的方式来实例化。

那如果偏特化和全特化同时存在呢？比如下面的情况：

```cpp
template <typename T1, typename T2>
struct Test {}; // 【0】通用模板

template <typename T>
struct Test<int, T> {}; // 【1】偏特化模板

template <>
struct Test<int, int> {}; // 【2】全特化模板

void Demo() {
  Test<int, int> t; // 按照哪个实例化？
}
```

先说答案，上面的实例会按照【2】的方式，也就是直接调用全特化。大致上来说，全特化优先级高于偏特化，偏特化高于通用模板。

对于函数来说，**模板函数不支持偏特化**，但支持重载，并且重载的优先级高于全特化。比如说：

```cpp
void f(int a, int b) {} // 重载函数

template <typename T1, typename T2>
void f(T1 a, T2 b) {} // 通用模板

template <>
void f<int, int>(int a, int b) {} // 全特化

void Demo() {
  f(1, 2); // 会调用重载函数
  f<>(1, 2); // 会调用全特化函数f<int, int>
  f(2.5, 2.6); // 会用通用模板生成f<double, double>
}
```

回到模板类的偏特化上，除了上面那种制定某些参数的偏特化以外，还有一种相对复杂的偏特化，请看示例：

```cpp
template <typename T>
struct Tool {}; // 这是另一个普通的模板类

template <typename T>
struct Test {}; // 【0】通用模板

template <typename T>
struct Test<Tool<T>> {}; // 【1】偏特化

void Demo() {
  Test<int> t1; // 使用【0】实例化Test<int>
  Test<Tool<int>>; // 使用【1】实例化Test<Tool<int>>
  Test<Tool<double>>; // 使用【1】实例化Test<Tool<double>>
}
```

有的资料会管上面这种特化叫做「模式特化」，用于区分普通的「部分特化」。但它们其实都属于偏特化的一种，因为偏特化都是相当于特化了参数的范围。在上面的例子中，我们是针对于「参数是`Tool`的实例类型」这种情况进行了特化。

所以，偏特化并不一定意味着模板参数数量变小，它有可能不变，甚至有可能是增加的，比如说：

```cpp
template <typename T1, typename T2>
struct Tool {}; // 这是另一个普通的模板类

template <typename T>
struct Test {}; // 【0】通用模板

template <typename T1, typename T2>
struct Test<Tool<T1, T2>> {}; // 【1】偏特化模板

template <typename T>
struct Test<Tool<int, T>> {}; // 【2】偏特化模板

void Demo() {
  Test<int> t1; // 【0】
  Test<Tool<int, double>> t2; // 【2】
  Test<Tool<double, int>> t3; // 【1】
}
```

所以偏特化的引入，让模板编程这件事有了爆炸性的颠覆，因为其中的组合可以随意发挥想象。但这里就引入了另一个问题，就比如上例中，【1】和【2】都是偏特化的一种，但为什么`Test<Tool<int, double>>`选择了【2】而不是【1】呢？这么说，看来不仅仅是跟全特化和通用模板存在优先级问题，多种偏特化之间也仍然存在优先级问题，那么编译器究竟是按照什么方式来进行偏特化匹配的呢？这就是我们下一节要着重研究的问题了。

### 偏特化模板的匹配优先级

在前面的章节我们提到了多种偏特化的模板的匹配优先级问题，那么当遇到多种偏特化时到底以哪一个为准呢？

这里，匹配优先级的原则是：**优先匹配特化程度更高的**。那么，怎么理解这个特化程度呢？我们先来举个最简单例子：

```cpp
template <typename T1, typename T2, typename T3>
struct Test {}; // 【0】

template <typename T1, typename T2>
struct Test<T1, T2, int> {}; // 【1】

template <typename T>
struct Test<T, int, int> {}; // 【2】

void Demo() {
  Test<double, int, int> t; // 匹配【2】而不是【1】
}
```

上面这个很好理解，因为`Test<double, int, int>`显然是【2】更加符合这种形式。

那是不是可以理解成，优先匹配参数少的那个呢？未必？请看下面的实例：

```cpp
template <typename T1, typename T2, typename T3>
struct Test {}; // 【0】

template <typename T1, typename T2>
struct Test<T1, T2, int> {}; // 【1】

template <typename T>
struct Test<int, int, T> {}; // 【2】

void Demo() {
  Test<int, int, int> t; // 匹配哪个？
}
```

大家可以先猜猜，上面这个例子会匹配哪个。如果按照参数少的来匹配，那应该匹配【2】才对。但实际情况是，哪个都不会匹配，会直接报错。

```cpp
Ambiguous partial specializations of 'Test<int, int, int>'
```

所以我们一定要理解那句「特化程度」，它并不以参数个数为评判标准。再来看一个例子：

```cpp
template <typename T1, typename T2>
struct Test {}; // 【0】

template <typename T1, typename T2, typename T3>
struct Test<T1, T2(T3)> {}; // 【1】

template <typename T>
struct Test<int, T> {}; // 【2】

void Demo() {
  Test<int, int(int)> t; // 会匹配哪个？
}
```

会匹配哪个呢？答案和上一个例子相同，会报Ambiguous的错误。所以说匹配时更关注的是参数的「形式」，而非个数。拿上面的例子来说，【1】号特化表示的是「第二个参数是一个函数类型，并且函数只有一个参数」的情况；【2】号特化表示的是「第一个参数为`int`的情况」。所以`Test<int, int(int)>`也是同时符合了，并没有「程度上」更贴近哪个，所以也会报错。

例子还有很多，这里就不过多列举了，总之，偏特化模板匹配的原则就是「特化程度更高者优先」，如果遇到可以同时命中多种的时候，将会报错（除非有更加匹配的特化，或者有对应的全特化，那么它会优先）。请读者一定要理解这里的「程度」究竟是什么含义。（这里只能说，要去体会了，[官方说明文档](https://www.apiref.com/cpp-zh/cpp/language/template_specialization.html)中有一些比较晦涩的描述，但我更建议大家直接动手写几个例子试一试，会比直接阅读这种规则描述要体会得更快、更彻底一些~）

### SFINAE

终于，我们来到了模板元编程前的最后一个基础知识——SFINAE。直接解释SFINAE会有点困难，也会让读者看着一头雾水，所以笔者打算稍后再来解释概念，我们先来看个引子：假如我现在要写一个模板函数，这个函数接收一个参数。最直接的方法就是这样：

```cpp
template <typename T>
void f(T t) {}
```

但这样的问题就在于，如果`T`比较大，或者是一个不可复制的类型，那这样传参就会有问题，这种情况下应当用引用来传参：

```cpp
template <typename T>
void f(const T &t) {}
```

但如果改成这样，对于那些基本类型（比如说`int`、`char`之类的）来说，是徒增了它的开销（引用本质是指针，所以多了一个指针的空间开销，以及若干取值、解指针的操作开销）。那能不能想个办法，把这两种情况都支持？暂时我们先不考虑是否可拷贝的问题，我们把长度小于等于一个指针大小的类型，用复制的方式传参，大于一个指针大小的类型，用引用传参。怎么做呢？其实方法很多，我们这里介绍一种可以引出SFINAE的方法，先看一下我们现在的诉求：

```cpp
template <typename T>
void f(T t) {}

template <typename T>
void f(const T &t) {}

// 这里给一个比指针长的类型用来测试
struct Test {
  int arr[16];
};
```

上面这个例子中，我们写了2个同名的模板函数`f`，但我们希望针对一个确定的`T`时，只会按照**其中的一个**进行实例化。比如说`f<int>`就用第一种实例化，`f<Test>`就用第二种实例化。

但假如不加任何限制的话，编译器就会把两个`f`都进行实例化，比如说`f<int>`就会同时生成一组重载函数：

```cpp
void f<int>(int t);
void f<int>(const int &t);
```

那么这时候我们再调用比如说`f<int>(1)`的时候，就会报错，因为两种函数原型都可以命中。

那如何让它只选其中的一个来生成实例呢？这需要我们用一个辅助类来完成：

```cpp
template <typename T, bool Cond>
struct EnableIf {};

template <typename T>
struct EnableIf<T, true> {
  using type = T;
};

template <typename T>
void f(typename EnableIf<T, sizeof(T) <= sizeof(void *)>::type t) {
  std::cout << 1 << std::endl;
}

template <typename T>
void f(typename EnableIf<T, (sizeof(T) > sizeof(void *))>::type const &t) {
  std::cout << 2 << std::endl;
}

void Demo() {
  f<int>(1); // 打印1
  Test t;
  f<Test>(t); // 打印2
}
```

上面例程中，我们使用了一个辅助类`EnableIf`，接收两个参数。大家注意看第二个参数，是一个布尔类型，我们针对于第二个参数为`true`的情况进行了偏特化，此时把`T`透传出来。那么也就是说，第二个参数为`true`的时候，才存在`type`这个成员，而`false`时会命中通用模板，此时是没有`type`这个成员的。

然后我们在两个模板函数`f`中都使用了`typename EnableIf::type`，只是第二参数传入的条件不同。那么这个时候编译器会怎么做呢？这就是模板实例化时的一个核心环节——匹配（Substitution）。

所谓的「匹配」就是指，**编译器会拿着实参去尝试实例化**，比如，实例化`f<int>`的时候，编译器会先尝试用第一个模板函数来实例化，也就是变成了：

```cpp
void f(typename EnableIf<int, sizeof(int) <= sizeof(void *)>::type t);
```

然后这里的判断条件是符合的，所以替换为`true`：

```cpp
void f(typename EnableIf<int, true>::type t);
```

这时会去实例化`EnableIf<int, true>`，命中了它的偏特化，里面是有`type`的，而`typename EnableIf<int, true>::type`就是`int`，所以这里就变成了：

```cpp
void f(int t);
```

没什么问题，于是编译器就按照这个模板生成了`f<int>`函数，函数原型是`void f<int>(int)`。我们称这个过程为「匹配成功（Substitution Success）」。

那对于`f<Test>`呢？同理，也会发生类似的过程。首先，按照第一个模板参数来尝试实例化：

```cpp
void f(typename EnableIf<Test, sizeof(Test) <= sizeof(void *)>::type t);
```

然后判断条件不符合，所以替换为`false`：

```cpp
void f(typename EnableIf<Test, false>::type t);
```

接下来实例化`EnableIf<Test, false>`，没有命中偏特化，因此要用通用模板来实例化。但`EnableIf<Test, false>`中并没有`type`这个成员。因此，`typename EnableIf<Test, false>::type`这个表达就是个错误的表达，无法用它来实例化。我们把这个过程称之为「匹配失败（Substitution Failure）」。

**注意，重点来了！！**虽然匹配失败了，但这时编译器并不会立刻报错，而是会**继续尝试匹配其他的模板**，因为我们还有一个模板函数`f`还没尝试呢！于是，编译器会继续用第二个模板尝试实例化：
    
```cpp
void f(typename EnableIf<Test, sizeof(Test) > sizeof(void *)>::type const &t);
```

变成：

```cpp
void f(typename EnableIf<Test, true>::type const &t);
```

同理，命中了偏特化，此时`typename EnableIf<Test, true>::type`就是`Test`，所以变成了：

```cpp
void f(Test const &t);
```

没问题，于是按照这个模板进行实例化，函数原型是：`void f<Test>(Test const &t)`。

因此，编译器在实例化模板时，如果遇到多个同名模板，则会逐一「尝试」匹配，在这个过程中如果发生了失败，并不会马上报错，因此把这种特性称之为「匹配失败不是错误（Substitution Failure Is Not An Error，简称SFINAE，我个人为了方便会直接读成/'sfɪni:/，但这个不是规范哈，依次按照字母读是绝对OK的！）」。

这里我们写的`EnableIf`其实就是STL中提供的`std::enable_if`的一个简化版。SFINAE是模板元编程最重要的理论基础，整个静态推导都是基于「构造一种模式，让其匹配成功或者失败」的方式来进行的。

## 模板元编程

### STL中提供的工具

从这一章开始，我们将正式介绍模板元编程。在STL中已经提供了很多静态的工具可供使用，模板元编程过程中自然少不了使用这些工具。当然，由于我们是模板元编程的详细教程，因此我也会带着大家来手写这些工具的源码。

需要注意的是，并不是所有的工具都是能手撸出来的，有极个别工具的底层实现依赖于编译器的“魔法操作”，真的遇到了那我们也没办法，其余能够手撸的，笔者都会介绍其手
动实现方法。

STL中提供的模板元主要收纳在`type_traits`头文件中，有兴趣的读者可以查看[官方的API参考文档](https://www.apiref.com/cpp-zh/cpp/header/type_traits.html)。

### 模板元编程的两个要素

在上一节，我们引出了`std::enable_if`的用法，开启了模板编程的新纪元。STL中的`std::enable_if`跟我们上一节写的demo还是稍微有一点区别的，下面是它的实现：

```cpp
template <bool cond, typename T = void>
struct enable_if {};

template <typename T>
struct enable_if<true, T> {
  using type = T;
};
```

从这个模板元的元老中可以看出，它有2个要素，一个是用于静态判断的`cond`，另一个是用于类型处理的`T`。所以，模板元编程无非就是做两件事，一个是静态数学计算（包括了布尔类型的逻辑运算和整数类型的数值运算。这里的「静态」是指编译期行为。）；另一个是类型处理（type traits，也被翻译为「类型萃取」）。

所以，**静态计算**和**类型处理**的编写过程，就称为「模板元编程」。把这两个要素的结果放到`enable_if`（或类型行为的模板）中，再通过SFINAE特性生成需要的代码再去参与编译。

强调一下，模板元编程是完完全全的编译期行为，任何设计运行期才能确定的数据都不可用，因此我们的编程思维跟普通代码编写的思维也是完全不同的，请读者一定要注意。

### 静态计算

静态计算主要有整数运算（C++20起也支持浮点数运算了）和逻辑运算。其中逻辑运算是重点，也是我们在模板元编程中最常用到的静态计算。下面分别来介绍。

#### 整数运算

静态的整数运算在模板元编程中并不是特别常用，类似于数组元素个数这样的静态参数，往往在编写的时候都是确定好的，并不需要做额外的运算，即便是做了，可能也就是`+1`这种非常简单的运算，笔者在这里就不着重来介绍了。

我们看一个真正意义上使用静态整数运算的例子。假如我要在程序中用到斐波那契数列的第30项。注意！我只用它的第30项，30这个数是静态确定的，并不是程序的输入。我应该怎么做？

相信有读者会说，「嗨！这还不简单！写个计算的函数不就好了嘛！」

```cpp
uint64_t Fib(uint16_t n) {
  if (n == 0 || n == 1) {
    return 1;
  }
  return Fib(n - 2) + Fib(n - 1);
}

void Demo() {
  std::cout << Fib(30) << std::endl;
}
```

这样做肯定是正确的，但仔细想想，`Fib`这个函数会跟随程序编译成一段指令，每次程序运行的时候，都会执行这段指令，现场算出`Fib(30)`，再打印出来。但斐波那契数列第30项它就是一个固定值呀！何必每次都要现算呢？

给出这样的提示，相信又会有读者会说，「哦，那我知道了！我先手算一遍，第30项应该是1346269，所以直接用这个值去替换」。

```cpp
void Demo() {
  std::cout << 1346269 << std::endl;
}
```

非常好！如果你能想到这里，那离成功已经近一大步了！这里的`1346269`就是个固定值，斐波那契数列第30项无论什么时候都是这个值，不需要再去计算。可直接这样写上去一个魔数会让程序可读性变差，所以我们应该搞一个名字给它：

```cpp
uint64_t fib_30 = 1346269;
void Demo() {
  std::cout << fib_30 << std::endl;
}
```

可读性是有了，但这样会引入另一个问题，`fib_30`是一个全局变量，既然是变量，它就是占内存空间的，并且会在主函数执行之前对其进行初始化。换句话说，上面的程序变成了，一开始先分配一片内存空间，把`1346269`这个值写进去，等后面需要用的时候，读取这片内存空间。

看得出，这片内存空间也是多余的，还是那句话，`1346269`这个值永久不变，编译期就应该确定，因此我们要再优化一下，让编译器用常量的方式来处理它：

```cpp
constexpr uint64_t fib_30 = 1346269; // 这里换成宏定义也是一样的效果
void Demo() {
  std::cout << fib_30 << std::endl;
}
```

好，上面的需求我们解决了。那假如，这时我除了要用第30项以外，还要用第18、21、24和28项，怎么办？嗯，都算出来写上去肯定是一种方法：

```cpp
constexpr uint64_t fib_18 = 4181;
constexpr uint64_t fib_21 = 17711;
constexpr uint64_t fib_24 = 75025;
constexpr uint64_t fib_30 = 1346269;

void Demo() {
  std::cout << 18 << "->" << fib_18 << std::endl;
  std::cout << 21 << "->" << fib_21 << std::endl;
  std::cout << 24 << "->" << fib_24 << std::endl;
  std::cout << 30 << "->" << fib_30 << std::endl;
}
```

但这时我们就发现了，这不是长久之计，毕竟咱不可能在程序里穷举出所有的数列的项，更何况像数值计算这种事怎么能是人工手算呢？万一算错一个数字都会有问题。我们要的效果是，**在程序运行之前，就把需要的数列项的值计算好**，而在程序运行的时候，这些值就是常数值了。因此，这就需要用到静态的数值计算。

编写的思路同样是递归，只不过要用模板元编程的方式，让所有的数值计算变为静态期。请看例程：

```cpp
template <uint16_t N>
struct Fib {
  constexpr static uint64_t value = Fib<N - 2>::value + Fib<N - 1>::value;
};
template <>
struct Fib<0> {
  constexpr static uint64_t value = 1;
};
template <>
struct Fib<1> {
  constexpr static uint64_t value = 1;
};
void Demo() {
  std::cout << 18 << "->" << Fib<18> << std::endl;
  std::cout << 21 << "->" << Fib<21> << std::endl;
  std::cout << 24 << "->" << Fib<24> << std::endl;
  std::cout << 30 << "->" << Fib<30> << std::endl;
}
```

这里把`Fib`定义为一个模板类，其成员`value`是一个静态量，表示对应的数列项的值。通用模板中定义其为前两项的和，然后把第0项和第1项单独特化出来。这样一来，我们就实现了完全编译期计算的目的。

这样做的好处不仅仅是提升程序的运行性能，还可以把计算的值用做其他模板元。比如说，我希望定义一个数组，它的元素个数是斐波那契数列的第10项，那么就可以写成：

```cpp
void Demo() {
  std::array<int, Fib(10)> arr; // Fib(10)是编译期可确定的值，因此可以传递
}
```

而这种情况如果是动态计算出的值，则无法作为函数参数传递，也就是说，下面这种写法是非法的：

```cpp
uint64_t fib(uint16_t n) {
// 省略实现
}

void Demo() {
  std::array<int, fib(10)> arr; // 非法，因为fib(10)不是编译期可确定的值
  int arr2[fib(10)]; // 同理非法（有的编译器可能会优化容错使这种写法通过编译，但按语言标准来说，这种写法是非法的）
}
```

然而，在程序中用到数列的某一项这种需求其实几乎不存在，我们也仅仅是在讲解知识点的时候用做示例。真正在模板元编程中起作用的静态数值计算，其实是用于生成序列的功能。笔者将会在后续章节详细介绍生成序列的方法以及其用途。

#### 逻辑运算

静态逻辑运算不单单是对数值做逻辑判断（比如说`N>0`这种），在模板元编程中，更多的是对「类型」进行是非判断。下面举一些例子可能更容易说明。

##### 简单的静态判断

假如我希望判断当前类型是否是某一类型，如何来做？这里我们仍然是利用偏特化，下面例程用于展示，判断`T1`和`T2`是否是同一类型：

```cpp
template <typename T1, typename T2>
struct is_same {
  constexpr static bool value = false;
};

template <typename T>
struct is_same<T, T> {
  constexpr static bool value = true;
};

// 下面是一个demo，利用enable_if，当参数为int时才生效
template <typename T>
typename std::enable_if<is_same<T, int>::value, void>::type
f(T t) {
}
```

上面例子本身很好理解，就不过多啰嗦了。不过不知道大家是否能发现，在处理这些静态逻辑判断时，使用的这些工具类，都会有一个静态的成员常量，我们这里叫`value`。当然了，实际上你把它叫什么名字都不影响使用，只不过在模板元编程中，我们倾向于符合STL当中的规范，使用`value`这个名字。

另一点就是，像上面这样把`value`展开来写会比较长，容易出错，也降低了一些可读性。在STL当中，把计算属性的部分抽象出了一个基类，同时，又给布尔类型的实例起了别名，就像下面这样：

```cpp
template <typename T, T val> // 注意这里的写法
struct integer_constant {
  constexpr static T value = val;
};

// 对布尔类型的实例单独起名
template <bool val>
using bool_constant = integer_constant<bool, val>;
```

那么上一节讲到的斐波那契数列前两项的特化就可以改写成：

```cpp
template <>
struct Fib<0> : std::integer_constant<uint64_t, 1> {};

template <>
struct Fib<1> : std::integer_constant<uint64_t, 1> {};
```

就避免了展开去写容易出错且可读性低的问题。

同时，由于布尔类型只有`true`和`false`两个取值，因此`bool_constant<true>`和`bool_constant<false>`也被单独定义了出来：

```cpp
using true_value = bool_constant<true>;
using false_value = bool_constant<false>;
```

这样一来，我们改写一下前面的`is_same`：

```cpp
template <typename T1, typename T2>
struct is_same : false_value {};

template <typename T>
struct is_same<T, T> : true_value {};
```

后续的示例中，我们都会采用这种方式而不是自行展开，也倡导读者在进行模板元编程时，按照这样隐形的规范来编写，这样别人在使用时会更方便。

由`is_same`还派生出了很多其他的，比如说`is_void`，`is_null_pointer`，`is_integral`等等，这里就不展开介绍了，感兴趣的读者可以去看STL源码，或者到[参考手册](https://www.apiref.com/cpp-zh/cpp/header/type_traits.html)中查看其实现方式。

##### 模板元的与或非运算

逻辑运算既然有了，自然少不了与或非这3个基本布尔运算。这里的难点在于，如果我们拿到的是值，那直接用`&&`、`||`、`!`即可对值进行运算。但现在我们拿到的是逻辑模板元，也就是`true_value`或`false_value`的派生类。多个模板元之间如何进行布尔运算，得到一个新的模板元呢？

这里要先扯个题外话，「与」「或」「非」是工科范畴的叫法，通俗来说就是「俗称」，它们在离散数学领域是有一个「学名」的，分别叫做「合取(conjunction)」「析取(disjunction)」「取反(negation)」运算，STL中也是按照这个来命名的。

模板元编程里，思路都是一样的，就是偏特化，我们先来实现一下取反运算，其实就是对`true`和`false`的实例，写一个相反的特化即可：

```cpp
template <typename T>
struct negation {};

template <>
struct negation<true_value> : false_value {};

template <>
struct negation<false_value> : true_value {};
```

这样一来，`negation<true_value>`会得到`false_value`，`negation<false_value>`会得到`true_value`，而对于其他类型的`negation<T>`则会命中通用模板，并不含有`value`成员，用于表示此项不合法。

那么合取和析取运算怎么写呢？我们知道，合取和析取运算是可以联立的，也就是多个值进行合取或析取。不过首先，我们先看看仅两个项的情况：

```cpp
template <typename T1, typename T2>
struct conjunction : false_value {};

template <typename T2>
struct conjunction<true_value, T2> : T2 {};
```

根据逻辑短路原则，如果`T1`是`false_value`，那么直接返回`false_value`；如果`T1`是`true_value`，那么结果跟`T2`保持一致。

同理，析取也可以写出来：

```cpp
template <typename T1, typename T2>
struct disjunction : true_value {};

template <typename T2>
struct disjunction<false, T2> : T2 {};
```

那么，多项的怎么处理呢？这时候就是递归大法好了，我们在两项相同的思路上来进行扩展：

```cpp
template <typename... Args>
struct conjunction : false_value {};

// 单独考虑仅一个true_value的情况
template <>
struct conjunction<true_value> : true_value {};

// 多项的情况就是拆开，把第一项单独拿出来，如果第一项是true_value，那么就按后面的走，如果是false，此偏特化不命中，走向通用模板，而通用模板就是false_value
template <typename... Args>
struct conjunction<true_value, Args...> : conjunction<Args...> {};

// 用于验证的demo
void Demo() {
	 std::cout << conjunction<true_value, true_value, false_value>::value << std::endl; // 打印0
	 std::cout << conjunction<true_value, true_value, true_value>::value << std::endl; // 打印1
	 std::cout << conjunction<false_value, false_value, false_value>::value << std::endl; // 打印0
}
```

请读者着重去理解上面例程中的那几行注释。如果合取的没问题了，那么析取的也自然没问题：

```cpp
template <typename... Args>
struct disjunction : true_value {};

template <>
struct disjunction<false_value> : false_value {};

template <typename... Args>
struct disjunction<false_value, Args...> : disjunction<Args...> {};
```

趁热打铁，来尝试这样一个需求：实现一个模板函数，包含两个参数，当这两个参数都是有符号的浮点数(`float`或`double`)时才生效。利用合取、析取以及`enable_if`来完成，不使用其他工具，那么效果如下：

```cpp
template <typename T1, typename T2>
typename std::enable_if<
  std::conjunction<std::disjunction<
  					   std::is_same<T1, float>,
                       std::is_same<T1, double>
                      >, std::disjunction<
                       std::is_same<T2, float>,
                       std::is_same<T2, double>
                      >
                    >::value,
  void>::type 
f() {}
```

### 类型处理

模板元编程的另一要素便是类型处理，英文叫type traits，所以也被翻译为「类型萃取」。其实这里的「萃取」并没有多么高大上的意思，类比前面章节介绍的「数值计算」，数值计算的结果应该是一个数值，而类型处理的结果就应该是个类型。

#### 条件类型

最简单的类型处理就是进行条件选择，类似于if-else，如果条件为真则返回类型1，为假则返回类型2。STL中提供了`std::conditional`，其实现如下：

```cpp
template <bool cond, typename T1, typename T2>
struct conditional {
  using type = T1;
};

template <typename T1, typename T2>
struct conditional<false, T1, T2> {
  using type = T2;
};

// 以下是使用的Demo
template <typename T>
void f(typename conditional<std::is_fundamental<T>::value, T, const T &>::type t) {
}

void Demo() {
  int a = 0;
  std::string str = "abc";
  f(a); // f<int>(int)
  f(str); // f<std::string>(const std::string &)
}
```

上面的例子不难，但是值得解释的东西还是蛮多的，我们一个一个来。`conditional`是一个用于类型处理的辅助类，它拥有3个参数，第一个参数是一个静态布尔值，用于表示判断条件；后两个参数是用于选择的类型。当条件为真时，`type`成员会定义为前一个类型；当条件为假时，`type`成员会定义为后一个类型。

与前面介绍的`value`同理，这里的`type`也是STL中约定的命名方式，原则上可以不遵守，但倡导大家来遵守。`type`表示的就是这个辅助类的输出，既然这个辅助类的作用是「类型处理」，那么自然要输出一个类型。

在使用的Demo中我们可以看到，`conditional<xxx, T, const T &>`就是这里的辅助类型，而里面的`xxx`就需要一个静态布尔值。我们在这里用`std::is_fundamental`来判断一个类型是不是基本数据类型。取`std::is_fundamental<T>::value`获取这个判断的结果。再取`conditional<xxx, T, const T &>::type`用来获取类型处理的结果。

值得注意的是，`conditional<xxx, T1, T2>`本身是一种类型，但这个是**辅助类本身的类型**，而要**通过辅助类拿到类型处理的结果类型**则是要取一次`type`，也就是`typename
conditional<xxx, T1, T2>::type`。

因此，上面就是一个最简单的类型处理的模板元和它的使用方式。

#### 辅助工具

相信大家应该已经发现了，使用这些辅助类型，再取成员（`value`或者`type`）会让代码迅速变长，尤其是取`type`的时候，还要加上`typename`，这玩意要是有嵌套的话，可读性会直接炸掉。因此，推荐的做法是针对这些辅助类搭配一个辅助工具，让代码变短，增强可读性。例如：

```cpp
// 针对is_fundamental写的辅助工具
template <typename T>
constexpr inline bool is_fundamental_v = is_fundamental<T>::value;

// 针对conditional写的辅助工具
template <bool cond, typename T1, typename T2>
using conditional_t = typename conditional<cond, T1, T2>::type;
```

有了这两个工具，上一节的Demo代码就可以改写成：

```cpp
template <typename T>
void f(conditional_t<is_fundamental_v<T>, T, const T &> t) {
}
```

在STL中，C++17标准下所有的模板元都配置了对应的辅助工具，用于数值计算的配备了对应`_v`结尾的工具，用于获取`value`；用于类型处理的配备了对应
`_t`结尾的工具，用于获取`type`。所以上面的Demo如果完全使用STL则应该是：

```cpp
template <typename T>
void f(std::conditional_t<std::is_fundamental_v<T>, T, const T &> t) {
}
```

在后面的教程中，我们使用STL工具的时候，如果要使用`type`或者`value`，我们都会优先使用辅助工具。而如果我们自己来编写模板元的话，也会按照这种方式来定义一个辅助工具去使用。这里也倡导大家如果要自行编写模板元，那么也应当按照这种方式提供对应的辅助工具。

#### 变换型的类型处理

我们再来看一些其他的类型处理模板元。

我希望提供一个用于**去掉const**的工具，也就是说，如果一个类型有`const`修饰，那么返回去掉`const`后的类型，如果没有的话就原样返回。这个工具应该怎么做？

这里要注意的是，「一个类型有`const`修饰」是指这个类型本身，而不包括它内部含有的类型。举例来说，`const int *`并没有用`const`修饰，因为这个类型本身是指针类型，而`const`修饰的是它的解指针类型（也就是对这个指针做解操作得到的默认类型，比如说`T *`的解类型是`T`，`const T *`的解类型是`const T`）。因此它去掉`const`后应该还是它本身。而`int *const`类型才是用`const`修饰的，应当变换为`int *`。同理，`const int *const`应当变为`const int *`。再同理，`const int &`也应当是原样输出。

STL中也提供这样的工具，叫做`remove_const`，实现如下：

```cpp
template <typename T>
struct remove_const {
  using type = T;
};

template <typename T>
struct remove_const<const T> {
  using type = T;
};

// 辅助工具
template <typename T>
using remove_const_t = typename remove_const<T>::type;
```

这时，当类型本身被`const`修饰时，会命中偏特化，`T`会识别为去掉`const`后的类型，因此`type`也就去掉了`const`。简单测试一下效果如下，读者也可以自行验证：

```cpp
void Demo() {
  std::remove_const_t<int> a1; // int
  std::remove_const_t<const int> a2; // int
  std::remove_const_t<const int *> a3; // const int *
  std::remove_const_t<const int (*const)[5]> a4; // const int (*)[5]
  std::remove_const_t<void *const *> a6; // void *const *
  std::remove_const_t<void ** const> a7; // void **
  std::remove_const_t<void *const &> a8; // void *const &
}
```

#### 完全退化

按照上一节的方法，我们自然也可以写出去掉指针符的，去掉引用符的，去掉右值引用符的，去掉`volatile`的，甚至可以组合起来，这些笔者在这里就不多介绍了，感兴趣的读者可以参考[官方参考手册](https://www.apiref.com/cpp-zh/cpp/header/type_traits.html)或阅读源码查看其实现。

不过有一种特殊的需求值得单拎出来讨论一下的。首先我们先来看一个例子：

```cpp
template <typename T>
struct Test {
  Test(const T &t) {}
};

void Demo() {
  Test t{"abc"}; // 推导出Test<char[4]>类型
}
```

如果你是从头开始读本教程的，那么这个例子你应该会非常熟悉，这是前面「模板参数自动推导」章节中的一个例子。由于C++的特殊性，一些类型在函数传参的时候会进行隐式转换，例如数组类型会转换成首元素指针。另外就是各种形式的引用，在模板类型传递的时候也会很让人头大（这个在后面章节会有详细的例子）。因此，STL提供了一个模板，用于「完全退化」，它会去掉各种乱七八糟的修饰符，保留类型本身，并且遇到数组类型时会转换为首元素指针类型（注意这里仍然是类型本身的修饰符，或数组，内部嵌套的类型是不会改变的）。它就是`std::decay`，实现如下：

```cpp
template <typename T>
struct decay {
 private:
  using U = std::remove_reference_t<T>;
 public:
  using type = std::conditional_t< 
        std::is_array_v<U>,
        std::remove_extent_t<U> *, // 如果是数组就转指针
        std::conditional_t< 
            std::is_function_t<U>,
            std::add_pointer_t<U>, // 如果是函数就转函数指针
            std::remove_cv_t<U>  // 其他情况则去掉const和volatile
  >>;
};

template <typename T>
using decay_t = typename decay<T>::type;
```

如果读者对于其中`is_array`、`remove_extent`、`is_function`、`add_pointer`、`remove_cv`的实现有疑问的话，可以参阅[官方参考手册](https://www.apiref.com/cpp-zh/cpp/header/type_traits.html)或阅读源码查看其实现。

有了`decay`以后，很多事情就好办了，它也是非常常用的一个工具。刚才那个例子就可以改写成：

```cpp
template <typename T>
struct Test {
  Test(std::decay_t<T> const &t) {}
};

void Demo() {
  Test t{"abc"}; // 推导出Test<char[4]>类型，但传参时通过decay，实际调用的构造函数是Test(const char *const &t)
}
```

这样就避免了实例化生成`Test(const char (&t)[4])`类型的构造函数了。

#### 函数类型的处理

如果我希望处理出一个函数类型的返回值，要怎么办呢？请看例程：

```cpp
template <typename T>
struct GetRet {
};

template <typename R, typename... Args>
struct GetRet<R(Args...)> {
  using type = R;
};

template <typename T>
using GetRet_t = typename GetRet<T>::type;

// 以下是示例
int f() {return 0;}

void Demo() {
  GetRet_t<decltype(f)> a;
  std::cout << std::is_same_v<std::decay_t<decltype(a)>, int>; // true
}
```

我们注意到，此时的偏特化，用到了前面章节模板基础知识中的「函数类型」，也就是说，只有符合`R(Args...)`形式的参数才会入到这个偏特化中。那么在这种情况下，「函数类型」和「函数指针类型」就是截然不同的。也就是说下面的代码不能正确解析：

```cpp
void Demo() {
  GetRet_t<decltype(f)> a; // f是函数类型，可以正确推导
  GetRet_t<decltype(&f)> b; // &f是函数指针类型，不能命中偏特化，而是会用通用模板，又因为通用模板不含type成员，因此这里报错
}
```

同样，仿函数类型、lambda类型、函数对象类型、成员函数类型都无法命中，进而无法取出返回值。因此，我们如果希望支持所有的情况，那就还要考虑支持其他的类型。对于仿函数和lambda类型来说，我们就要去取出它的`operator ()`方法的返回值类型，对于函数对象类型来说也是一样的。所以我们代码可以改造成：

```cpp
template <typename T>
struct GetRet {
 private:
  using DT = std::decay_t<T>;
 public:
  // 如果内部含有operator()就取它的类型
  using type = typename GetRet<decltype(&DT::operator())>::type;
};

// 对于函数类型
template <typename R, typename... Args>
struct GetRet<R(Args...)> {
  using type = R;
};

// 对于函数指针类型
template <typename R, typename... Args>
struct GetRet<R(*)(Args...)> {
  using type = R;
};

// 对于非静态成员函数类型
template <typename T, typename R, typename... Args>
struct GetRet<R(T::*)(Args...)> {
  using type = R;
};

template <typename T, typename R, typename... Args>
struct GetRet<R(T::*)(Args...) const> {
  using type = R;
};

template <typename T>
using GetRet_t = typename GetRet<T>::type;
// 测试用例
int f() {return 0;}
struct T1 {
  int m();
};

struct T2 {
  int operator()();
};

void Demo() {
// 函数类型
  GetRet_t<decltype(f)> a;
  // 函数指针类型
  GetRet_t<decltype(&f)> b;
  // 仿函数类型
  GetRet_t<T2> c;
  // lambda类型
  GetRet_t<decltype([]()->int{return 0;})> d;
  // 非静态成员函数类型
  GetRet_t<decltype(&T1::m)> e;
  // 函数对象类型
  GetRet_t<std::function<int()>> g;
  std::cout << std::is_same_v<std::decay_t<decltype(a)>, int>; // true
  std::cout << std::is_same_v<std::decay_t<decltype(b)>, int>; // true
  std::cout << std::is_same_v<std::decay_t<decltype(c)>, int>; // true
  std::cout << std::is_same_v<std::decay_t<decltype(d)>, int>; // true
  std::cout << std::is_same_v<std::decay_t<decltype(e)>, int>; // true
  std::cout << std::is_same_v<std::decay_t<decltype(g)>, int>; // true
}
```

这样做确实可以解决问题，但是有点太「老实巴交」了，踏踏实实去适配所有情况肯定是比较保守的做法，只不过对于当前这个需求，我们还有一种更简单的做法：

```cpp
template <typename T>
struct GetRet {
  // 直接invoke这个类型的成员，推导返回值
  using type = decltype(std::declval<std::decay_t<T>>()());
};

// 对于非静态成员函数类型（这个还是要单独适配）
template <typename T, typename R, typename... Args>
struct GetRet<R(T::*)(Args...)> {
  using type = R;
};

template <typename T, typename R, typename... Args>
struct GetRet<R(T::*)(Args...) const> {
  using type = R;
};
```

这里需要解释一下`declval`的功能。在类型变换中，我们是没有实际数据的，换句话说，不会真的去定义一个`T`类型的变量，而仅仅是需要它来参与类型的变换。但假如这时`T`不含有无参构造的话，就会失败：

```cpp
struct Test {
  Test(int); // 没有无参构造
  void method();
};

template <typename T>
struct XXX {
  using type = decltype(T{}.method()); // 这里构造T{}的时候会失败
};
```

这里我们为了调用非静态成员函数`method`，就不得不构造一个`T`类型的对象，但这个对象只在静态分析的时候才有，并不需要真的构造，所以它的构造函数是怎么样的不重要，但上面这种情况又会让编译器去匹配构造函数的问题，从而产生错误。

为了解决这个「仅需要类型，而不想做构造检测」的问题，我们只能想其他的方法，例如这样：

```cpp
template <typename T>
struct XXX {
  // 通过指针转换，避开构造检测机制
  using type = decltype((static_cast<T *>(nullptr))->method());
};
```

而STL中就提供了`declval`工具，用来避开构造检测而生成一个纯类型的对象，实现如下：

```cpp
template <typename T>
T declval() {
// 不需要实现，因为它不会真正被调用，仅仅用于静态处理获取类型
} 
```

所以，刚才的例子我们就可以改写成：

```cpp
struct Test {
  Test(int); // 没有无参构造
  void method();
};

template <typename T>
struct XXX {
  using type = decltype(declval<T>().method()); // 这样就不会构造失败了
};
```

再回头看一开始的例子：

```cpp
template <typename T>
struct GetRet {
  // 直接invoke这个类型的成员，推导返回值
  using type = decltype(std::declval<std::decay_t<T>>()());
};
```

前面`std::declval<std::decay_t<T>>()`用于生成这个纯类型的对象，再后面一个`()`就表示invoke行为（对于函数、函数指针会进行调用；对于仿函数、lambda、函数对象类型则会调用其`operator()`函数），再对调用行为进行一次`decltype`即可获取到返回值类型。

那，如果我们想获取参数类型呢？比如说，我想获取函数的第二个参数的类型，要怎么做？这时，由于不像返回值那样可以直接invoke来判断，参数类型的获取就只能用传统的方法了，效果如下：

```cpp
template <typename T>
struct Get2ndArg {
 private:
  using DT = std::decay_t<T>;
 public:
  // 如果内部含有operator()就取它的类型
  using type = typename Get2ndArg<decltype(&DT::operator())>::type;
};

template <typename R, typename Arg1, typename Arg2, typename... Args>
struct Get2ndArg<R(Arg1, Arg2, Args...)> {
  using type = Arg2;
};

template <typename R, typename Arg1, typename Arg2, typename... Args>
struct Get2ndArg<R(*)(Arg1, Arg2, Args...)> {
  using type = Arg2;
};

template <typename T, typename R, typename Arg1, typename Arg2, typename... Args>
struct Get2ndArg<R(T::*)(Arg1, Arg2, Args...)> {
  using type = Arg2;
};

template <typename T, typename R, typename Arg1, typename Arg2, typename... Args>
struct Get2ndArg<R(T::*)(Arg1, Arg2, Args...) const> {
  using type = Arg2;
};

template <typename T>
using Get2ndArg_t = typename Get2ndArg<T>::type;
```

如果要获取第一个参数，或者第N个参数的类型，那么都是相同的道理，这里就不再啰嗦了。

#### 自定义类型的处理

单一的类型处理我们已经体验过了，那对于复杂类型呢？比如说，判断类型`T`中是否存在一个名为`f`的成员？

这个需求里，最主要的思路就是，我们要「尝试」来推导一下`T::f`的类型，如果这个东西存在，那么就能够推导出来（尽管推导出来的类型是什么我们并不关心）；而如果不存在`T::f`这个东西，那么就会实例化失败，从而触发SFINAE继续匹配通用模板。

##### 判断T是否含有一个类型为int的成员f

首先我们先来简化一下问题，这里我们要求`T::f`必须是`int`类型的静态成员，那么代码如下：

```cpp
template <typename T, typename V = int> // V是辅助参数
struct HasMemberF : std::false_type {}; // 判断T中是否函数f成员

template <typename T>
struct HasMemberF<T, decltype(T::f)> : std::true_type {};

template <typename T>
constexpr inline bool HasMemberF_v = HasMemberF<T>::value;

// 以下是Demo
struct T1 {
  static int f; // 符合条件
};

struct T2 {
 static double f; // 含有f但类型不匹配
};

struct T3 {}; // 不含f

void Demo() {
  std::cout << HasMemberF_v<T1> << std::endl; // 1
  std::cout << HasMemberF_v<T2> << std::endl; // 0
  std::cout << HasMemberF_v<T3> << std::endl; // 0
  std::cout << HasMemberF_v<int> << std::endl; // 0
}
```

着重解释一下这里的写法，首先，通用模板中含有2个参数，但是第二个参数`V`是用做辅助参数的，我们给它默认参数为`int`。之后，其实我们是要给`HasMemberF<T, int>`来绑定`true_type`的。但仅当`T::f`的类型是`int`时才生效。

例如，当传入的参数是`T1`时，`decltype(T1::f)`是`int`，因此，下面的偏特化便存在，也就是模板会变成：

```cpp
template <typename T, typename V = int>
struct HasMemberF : std::false_type {};

template <typename T>
struct HasMemberF<T, int> : std::true_type {}; // 当T是T1时，decltype(T::f)变成int，所以偏特化存在
```

而又因为通用模板中，`V`默认就是`int`，所以`HasMemberF<T1>`就是`HasMemberF<T1, int>`，显然是命中了偏特化的，因此`value`为`true`。

而当用`T2`来实例化时，下面的偏特化也存在，但是变成了：

```cpp
template <typename T, typename V = int>
struct HasMemberF : std::false_type {};

template <typename T>
struct HasMemberF<T, double> : std::true_type {}; // 当T是T2时，decltype(T::f)变成double，所以偏特化存在
```

再来看`T3`的情况，由于`T3`不存在成员`f`，所以`decltype(T3::f)`就成为了不合法语句，根据SFINAE原则，这里的偏特化也就不会生成代码。所以仅仅存在一个通用模板，那么`HasMemberF<T3>`自然会命中通用模板，其`value`是`false`。`HasMemberF<int>`跟`HasMemberF<T3>`是相同的道理。

那如果不要求`T::f`是静态的，只要是`int`类型成员就符合呢？道理是相同的，只不过由于非静态成员不能直接通过类型来取出（`T::f`语句不合法），因此只能换一种方式，通过`declval`来取出（`std::declval<T>().f`）。下面是代码：

```cpp
template <typename T, typename V = int>
struct HasMemberF : std::false_type {};

template <typename T>
struct HasMemberF<T, decltype(std::declval<T>().f)> : std::true_type {}; // 这里用std::declval<T>().f代替T::f

template <typename T>
constexpr inline bool HasMemberF_v = HasMemberF<T>::value;

// 以下是Demo
struct T1 {
  static int f; // 符合条件，静态int成员
};

struct T2 {
  int f; // 符合条件，非静态int成员
};

struct T3 {}; // 不含f

void Demo() {
  std::cout << HasMemberF_v<T1> << std::endl; // 1
  std::cout << HasMemberF_v<T2> << std::endl; // 1
  std::cout << HasMemberF_v<T3> << std::endl; // 0
}
```

这样，无论静态还是非静态，只要是`int`类型就符合。

但如果我要求只想筛选出非静态的怎么办？那就只能通过取地址的方式拿出成员变量了（`&T::f`取出成员的指针类型），代码如下：

```cpp
template <typename T, typename V = int T::*> // 注意这里改成成员指针类型
struct HasMemberF : std::false_type {};

template <typename T>
struct HasMemberF<T, decltype(&T::f)> : std::true_type {};

template <typename T>
constexpr inline bool HasMemberF_v = HasMemberF<T>::value;

// 以下是Demo
struct T1 {
  static int f; // 不符合条件，静态int成员
};

struct T2 {
  int f; // 符合条件，非静态int成员
};

struct T3 {}; // 不含f

void Demo() {
  std::cout << HasMemberF_v<T1> << std::endl; // 0
  std::cout << HasMemberF_v<T2> << std::endl; // 1
  std::cout << HasMemberF_v<T3> << std::endl; // 0
}
```

##### 判断T中是否含有成员f

确定类型的成员判断我们已经会了，那此时如果需求变为「判断类型`T`中是否含有成员`f`」呢？换句话说，现在我们不关心`f`是什么类型了，变量也好，函数也好，静态也好，非静态也好，只要它里面有一个叫`f`的成员就算数。这种的怎么做呢？

其实思路还是没变的，只不过我们要对推导出的类型来做多一步处理了。上一节中，通用模板的辅助参数的默认值要符合偏特化当中生成的，才能让使用时命中偏特化。但现在既然对类型不关心了，那么也就是说，**无论`decltype`出什么类型，我们都要给它转换成一个相同的类型`X`**，然后让通用模板的第二个参数默认值设定为`X`即可。示例如下：

```cpp
struct X {}; // 辅助类型，仅用作静态推导，无运行期意义

// 辅助工具，用于把任意类型转为X
template <typename T>
using ToX = X;

template <typename T, typename V = X> // 注意这里改成X
struct HasMemberF : std::false_type {};

template <typename T>
struct HasMemberF<T, ToX<decltype(&T::f)>> : std::true_type {};

template <typename T>
constexpr inline bool HasMemberF_v = HasMemberF<T>::value;

// 以下是Demo
struct T1 {
  static int f; // 符合条件，含有f
};

struct T2 {
  double f; // 符合条件，含有f
};

struct T3 {}; // 不含f

struct T4 {
  int f() const; // 符合条件，含有f
  void f2();
};

void Demo() {
  std::cout << HasMemberF_v<T1> << std::endl; // 1
  std::cout << HasMemberF_v<T2> << std::endl; // 1
  std::cout << HasMemberF_v<T3> << std::endl; // 0
  std::cout << HasMemberF_v<T4> << std::endl; // 0
}
```

到这里大家应该能发现，其实这个辅助类型`X`是什么并不重要，只要**通用模板的第二个参数的默认值**和**偏特化中映射出的类型**相匹配即可完成功能。比如说我们可以把`X`改成`int`：

```cpp
// 辅助工具，用于把任意类型转为int
template <typename T>
using ToInt = int;

template <typename T, typename V = int> // 注意这里改成int
struct HasMemberF : std::false_type {};

template <typename T>
struct HasMemberF<T, ToInt<decltype(&T::f)>> : std::true_type {};

template <typename T>
constexpr inline bool HasMemberF_v = HasMemberF<T>::value;
```

或者改成`void`也是一样的效果：

```cpp
// 辅助工具，用于把任意类型转为void
template <typename T>
using ToVoid = void;

template <typename T, typename V = void> // 注意这里改成void
struct HasMemberF : std::false_type {};

template <typename T>
struct HasMemberF<T, ToVoid<decltype(&T::f)>> : std::true_type {};

template <typename T>
constexpr inline bool HasMemberF_v = HasMemberF<T>::value;
```

而STL中，提供了一个工具叫`void_t`，用于把任意类型（任意个数的任意类型）转换为`void`类型，实现如下：

```cpp
template <typename... Args>
using void_t = void;
```

因此，我们这里就可以直接用`void_t`来代替自定义繁琐的工具，所以这个功能的最终版本是这样的：

```cpp
template <typename T, typename V = void>
struct HasMemberF : std::false_type {};

template <typename T>
struct HasMemberF<T, std::void_t<decltype(&T::f)>> : std::true_type {};

template <typename T>
constexpr inline bool HasMemberF_v = HasMemberF<T>::value;
```

这就是用于判断某个类型中是否函数某个成员的模板元的编写方法。

### 实现一个动态的get

如果读者对元组工具，也就是`std::tuple`很熟悉的话，那么对`std::get`也一定不陌生。我们可以通过`std::get<N>(tu)`的方式把原组的第`N`个元素取出来。

但是，不知道大家有没有思考过这样一个问题，`std::get`是静态模板工具，所以参数`N`必须要编译期确定。那为什么STL不提供一个动态序号获取元组元素的能力呢？也就是说类似`tu.get(n)`，其中`n`是函数参数（运行期数据）。最主要的原因就在于类型不确定，假如说我们真的要给`tuple`提供一个`get`方法，那么方法的返回值是不确定的，于是这就成了一个RTTI（Run-Time Type Identification）方法。而STL是模板库，并不提供任何RTTI行为，自然也就不会提供类似的方法。

但假如，我们在实际开发中，针对某个元组，可以确定（或可以正确处理）它的类型，在这种情况下希望可以提供一个动态的`get`工具应当如何来做？举例来说：

```cpp
class Base {
 public:
  virtual void f() const = 0;
};

class Ch1 : public Base {
 public:
  void f() const override {}
};

class Ch2 : public Base {
 public:
  void f() const override {}
};

// 利用多态调用f方法
template <typename... Args>
std::enable_if_t<
	std::conjunction_v<
			std::is_base_of<Base, Args>...
	>, void> 
InvokeF(const std::tuple<Args...> &tup, size_t index) {
  // 考虑这里应该怎么写
}

void Demo() {
  // 一个元组，里面都是Base的子类对象
  std::tuple tu{Ch1{}, Ch2{}, Ch1{}};
  InvokeF(tu, 1); // 调用Ch2的f方法，注意这个参数1是运行期数据
}
```

解释一下上面例程，`Ch1`和`Ch2`都是`Base`类的子类，`InvokeF`函数是传入一个元组`tup`和一个序号`index`，我们要把`tup`的第`index`个元素拿出来，去调用它的`f`方法，这里要求`tup`的元素都必须是`Base`的子类。

现在问题就在于，`index`是一个运行期数据，我们用`std::get<index>`肯定是不可以的，那怎么办？只能采用**编译期展开**的方式。

具体来说就是，由于我们这里的元组类型是编译期确定的，那么对应的变参数量也就是确定的（比如上面例程中就是3个），那么，我们就在编译期生成分别应对假如`index`就是这种情况，应当怎么去做。

以上面例程为例，由于编译期不知道`index`可能是几，但针对`std::tuple<Ch1, Ch2, Ch1>`这种类型的元组来说，`index`只能是`0`、`1`、`2`这3种情况时才可以有合法处理。所以，我们就分别写出当`index`为`0`、`1`、`2`时，应当做的处理。这个就叫做「编译期展开」，也就是在编译期枚举出运行时可能传入的所有数据，分别生成对应的代码指令，然后当运行期数据确定的时候去执行对应的指令。

如果手动来写，就应该写成：

```cpp
template <typename... Args>
void InvokeF_0(const std::tuple<Args...> &tu) {
  std::get<0>(tu).f();
}

template <typename... Args>
void InvokeF_1(const std::tuple<Args...> &tu) {
  std::get<1>(tu).f();
}

template <typename... Args>
void InvokeF_2(const std::tuple<Args...> &tu) {
  std::get<2>(tu).f();
}

template <typename... Args>
void InvokeF(const std::tuple<Args...> &tu, size_t index) {
  if (index == 0) {
    InvokeF_0(tu);
  } else if (index == 1) {
  	InvokeF_1(tu);
  } else if (index == 2) {
  	InvokeF_2(tu);
  }
}
```

但这是我们假定元组是3个元素的情况。可实际场景下，元组的元素个数是不确定的，如何利用模板来生成呢？思路就是，逐个尝试，递归生成函数。请看代码：

```cpp
// 辅助工具，一个用于尝试匹配的递归模板
template <int N, typename... Args>
void TryInvokeF(const std::tuple<Args...> &tup, size_t index) {
  if constexpr (N < sizeof...(Args)) { // 递归终止条件（静态的）
    // 尝试index是不是本次递归的
    if (index == N) {
      std::get<N>(tup).f(); // 如果符合，就取出元素，并调用f
      return;
    }
    // 如果不符合，就生成下一个模板实例，再去判断是否符合
    TryInvokeF<N + 1, Args...>(tup, index); // ！！这一行是精华所在！！
  }
}

// 利用多态调用f方法
template <typename... Args>
std::enable_if_t<
  std::conjunction_v<
      std::is_base_of<Base, Args>...
  >, void>
InvokeF(const std::tuple<Args...> &tup, size_t index) {
  // 如果index不在合法范围中，直接按照异常处理
  if (index >= sizeof...(Args)) { // sizeof...是静态工具，用于获取变参个数
    return;
  }
  TryInvokeF<0, Args...>(tup, index); // 从0开始尝试
}

void Demo() {
  // 一个元组，里面都是Base的子类对象
  std::tuple tu{Ch1{}, Ch2{}, Ch1{}};
  InvokeF(tu, 1); // 调用Ch2的f方法，注意这个参数1是运行期数据
}
```

这里提供了一个辅助工具`TryInvokeF`，其中的`if constexpr`语句用于做编译期静态数据的判断，不符合条件的将不会生成代码。所以，这里我们要求`N`不可以大于等于变参个数。对于上面例子来说，`N`只能小于`3`，而在`InvokeF`中调用了`TryInvokeF<0, Args...>`函数，因此模板实例化时会生成`N`为`0`时的情况，而`TryInvokeF<0, Args...>`中调用了`TryInvokeF<1, Args...>`，所以还会继续实例化。里面又调用了`TryInvokeF<2, Args...>`，所以还会实例化。直至`TryInvokeF<2, Args...>`中调用了`TryInvokeF<3, Args...>`，而`TryInvokeF<3, Args...>`里由于不满足`if constexpr`的条件，所以到此为止。

也就是说，对于`std::tuple<Ch1, Ch2, Ch1>`这个元组来说，编译器生成了`TryInvokeF<0, Ch1, Ch2, Ch1>`，`TryInvokeF<1, Ch1, Ch2, Ch1>`，`TryInvokeF<2, Ch1, Ch2, Ch1>`和`TryInvokeF<3, Ch1, Ch2, Ch1>`这4个函数实例。而最后一个`TryInvokeF<3, Ch1, Ch2, Ch1>`是空的，前面的3个内部调用了后面的那个。

到了运行期，根据`index`值的不同，会调用不同深度的函数，当发现`N`和`index`值相等时，递归结束。

请读者仔细体会模板元编程当中的「递归」，这里的递归并不是运行时的函数栈递归，而是模板实例化时的递归实例化，根据一个静态数值，递归实例化出了若干个函数。而进入运行期后，其实就不能算真正意义上的递归调用了（因为并不是在一个函数里自己调自己，而是分别链式的去调用实例化后的若干函数。）请读者仔细体会二者的区别。

### 展开元组

如果我们想实现一个「调用」对象的方法，这个对象可能是函数、函数指针、仿函数实例、函数对象、lambda等，总之是一个可调用的对象。要怎么办？其实非常简单，直接透传参数即可：

```cpp
template <typename T, typename... Args>
decltype(auto) invoke(T &&obj, Args&&... args) {
  return obj(std::forward<Args>(args)...);
}

// 以下是验证Demo
void f(int a) {
  std::cout << a << std::endl;
}

void Demo() {
  invoke(f, 4); // 函数
  invoke(&f, 5); // 函数指针
  int s = invoke([](int a, int b){return a + b;}, 5, 6); // lambda
  int r = invoke(std::greater<int>{}, 6, 7); // 仿函数
  std::function<void(int)> t{f};
  invoke(t, 2); // 函数对象
}
```

上面展示的也是`std::invoke`的一个简化版实现（暂时没有考虑到非静态成员函数的问题），但假如，需要传入函数的参数并不是直接填入的，而是保存在一个元组中，那怎么做呢？

```cpp
void f(int a, double b) {}

void Demo() {
  std::tuple arg{1, 3.5}; // 参数在元组中
  apply(f, arg); // 用元组调用函数，这个功能如何实现？
}
```

那我们就需要把元组展开，依次填写到`invoke`的参数中。可是，元组只能通过`std::get`的方式取出其中的数据，也就是说，我们需要依次使用`std::get<0>`、`std::get<1>`、`std::get<2>`……去操作元组，拿出所有的数据，然后依次填写到`invoke`的参数中。对于上例来说应该是

```cpp
template <typename F, typename Arg0, typename Arg1>
decltype(auto) apply(F &&func, std::tuple<Arg0, Arg1> &&tup) {
  return invoke(func, std::get<0>(tup), std::get<1>(tup));
}
```

由此可以观察到，如果我们能得到一个静态的序列`{0, 1, 2, 3, ...}`，那么这里就可以按照这个序列来展开，也就是说：

```cpp
template <typename F, typename Tup, size_t... Index>
decltype(auto) apply(F &&func, Tup &&tup) {
  return invoke(func, std::get<Index>(tup)...); // 通过Index来展开
}
```

现在只要这个`Index`能够正确地按照`{0, 1, 2, 3, ...}`的方式填写进去，我们的问题就解决了。可是，我们总不能要求使用者手动去填写把？

```cpp
void test(int a, double b, char c) {}

void Demo() {
  std::tuple arg{1, 3.5, 'A'}; // 参数在元组中
  apply<void(*)(int, double, char), 0, 1, 2>(test, arg); // 这不太扯了？
}
```

所以，现在就需要一个工具，能够根据元组的元素个数，自动生成一个序列，从`0`开始，一直到`N - 1`。因此，我们需要构造一个辅助工具，用于把`N`变成`0, 1, 2, ..., N - 2, N - 1`这样的序列。代码如下：

```cpp
// 序列类，类型本身无运行意义，仅用于静态处理，只会用到它的模板参数
template <size_t... Index>
struct sequence {};

// 用于生成序列（递归大法好）
template <size_t N, size_t... Index>
struct make_sequence : make_sequence<N - 1, N - 1, Index...> {}; // 注意这里的写法，是这个功能的重点

// 递归终点（注意不能无限递归下去，到0就要截止了）
template <size_t... Index>
struct make_sequence<0, Index...> {
  // 这个时候序列已经生成了，所以把这个序列交给sequence
  using result = sequence<Index...>;
};
```

现在来解释一下上面是如何生成序列的。在`make_sequence`中，第一个参数`N`表示「还剩几个数没有进入序列」，而后面的`Index`就是现在已经产生的序列。举个例子来说，`make_sequence<3>`，现在`N`是`3`，表示还有3个数要处理，而后面的`Index`是空的，所以这是初始状态。根据代码继承的写法（递归），`make_sequence<3>`应当继承自`make_sequence<2， 2>`。

对于`make_sequence<2, 2>`来说，还有2个数字要处理，已经处理完的序列是`2`，再根据继承写法进行递归，它继承自`make_sequence<1, 1, 2>`。同理，`make_sequence<1, 1, 2>`继承自`make_sequence<0, 0, 1, 2>`。这时，由于`N`变为`0`了，所以命中了下面的偏特化（递归结束），在`make_sequence<0, 0, 1, 2>`中，成员`result`被定义为`` sequence<0, 1, 2>``，这就得到了我们想要的序列。

那么这仍然是一个模板元编程中很独特的用法，虽然我们用到了继承的写法，但这里其实跟OOP中的继承完全没有关系，这些工具类也不会实例化出现在运行期，我们仅仅是通过这种方式来生成一个序列而已。请读者一定要体会这种模板元编程的「feel」。

当已经拥有这个序列以后，就好办了，在`apply`函数中，用它进行`std::get`展开即可，下面是完整代码：

```cpp
// 序列类，类型本身无运行意义，仅用于静态处理，只会用到它的模板参数
template <size_t... Index>
struct sequence {};

// 用于生成序列
template <size_t N, size_t... Index>
struct make_sequence : make_sequence<N - 1, N - 1, Index...> {};

// 递归终点
template <size_t... Index>
struct make_sequence<0, Index...> {
  // 这个时候序列已经生成了，所以把这个序列交给sequence
  using result = sequence<Index...>;
};

template <typename F, typename Tup, size_t... Index>
decltype(auto) apply_detail(F &&func, Tup &&tup, sequence<Index...> &&) {
  return std::invoke(func, std::get<Index>(tup)...); // 通过Index来展开
}

template <typename F, typename Tup>
decltype(auto) apply(F &&func, Tup &&tup) {
  return apply_detail(func, tup, typename make_sequence<std::tuple_size_v<std::decay_t<Tup>>>::result{});
}

// 测试Demo
void f(int, double) {}

void Demo() {
  std::tuple tu{1, 3.4};
  apply(f, tu);
}
```

这里的另一个要点在于，为了让`apply_detail`函数能自动生成`Index`，我们利用了模板的实例化自动推导，根据传入的第三个参数（序列）来自动推导模板参数。所以在`apply`函数把生成的序列通过参数传递了进去。但这里由于辅助类都没有任何数据，也没有自定义的构造、析构函数，因此编译器并不会生成额外的汇编指令，大家可以放心去使用。

### 多选一结构

这一章我们来看看如何编写一个多选一的结构，STL中提供了`std::variant`，我们就来实现一个简易版。（注意下面我们实现的variant与STL中的是有区别的，但大体思路是相同的，请读者不要以本节的代码参考使用`std::variant`）。

我们的诉求是，创建一个数据结构，「可能」存放多种类型，但同一时间只能有一种，并且可以在运行期变化为另一种。这里比较容易想到的做法就是用共合体类型存储数据，再加一个用于表示当前哪种数据是生效的`index`。请看代码：

```cpp
template <typename T1, typename T2>
class variant {
public:
  // 针对每种情况的构造
  variant(const T1 &t1);
  variant(const T2 &t2);
private:
  union {
    T1 t1;
    T2 t2;
  } data;
  int index; // 当前生效的数据序号
};
```

只不过这样我们很快就会发现很多严重的问题：

  1. 对于任意个数的参数，无法映射到`union`结构中；

  2. 如果数据类型不含无参构造函数，`union`结构的构造会报错；

  3. `variant`的构造函数依赖数据类型的拷贝构造，对于不可拷贝类型来说无法创建。

因此，我们必须换一个思路。既然一开始我们想到用`union`，主要也是为了内存空间的复用，所以我们只需要自己来维护一片数据空间就好了，以参数类型中长度最大的为准，创建一个缓存空间即可。

```cpp
template <typename... Types>
class variant {
 private:
  void *data = std::malloc(std::max(sizeof(Types)...)); // 计算出最长的Type
  int index; // 当前生效的数据序号
};
```

接下来的任务就是，构造函数。由于这里的`Types`是变参，所以无法穷举，与此同时，我们希望可以就地构造，跳过「拷贝构造」这个阶段，以支持不可拷贝类型的数据，因此必须有一个`Index`来标识，后面跟变参：

```cpp
template <typename... Types>
class variant {
 public:
  template <size_t Index, typename... Args>
  variant(Args &&... args); // 大概是这个意思
 private: 
  void *data = std::malloc(std::max(sizeof(Types)...)); // 计算出最长的Type
  int index; // 当前生效的数据序号
};
```

然而，出于语法限制，构造函数用模板生成的话，是无法手动实例化的，例如：

```cpp
variant<1, int> va; // <1, int>会识别为类型的模板参数，而不是构造函数的模板参数
```

因此，构造函数的模板参数只能依赖于自动推导，所以，我们就需要提供一个工具，用来「传递」这个`Index`。

```cpp
template <size_t Index>
struct in_place_index_t {}; // 单纯的静态工具，用于传递Index，没有运行期意义

template <size_t Index>
constexpr inline in_place_index_t<Index> in_place_index; // 对应in_place_index_t类型的实例

template <typename... Types>
class variant {
 public:
  template <size_t Index, typename... Args>
  variant(const in_place_index_t<Index> &, Args &&... args);
 private:
  void *data = std::malloc(std::max(sizeof(Types)...)); 
  int index;
};
```

然后，构造时，也同样通过`in_place_index`来构造，传递这个`Index`：

```cpp
 // 用于测试的类型
struct Test1 {
  Test1(int, double);
};

struct Test2 {
  Test2(char, int);
};

void Demo() {
  variant<Test1, Test2> var{in_place_index<0>, 1, 1.5}; // 用于构造Test1类型
  variant<Test1, Test2> var{in_place_index<1>, 'A', 1}; // 用于构造Test2类型
}
```

那么接下来的问题就是如何解析了，`variant`本身的参数是一组`typename`列表，但构造传进来的是一个`Index`序号，如何对应呢？相信读者到现在应该已经建立初步的感觉了，没错，递归大法好！

```cpp
template <size_t Index, typename Head, typename... Args>
struct get_type_by_index : get_type_by_index<Index - 1, Args...> {};

template <typename Head, typename... Args>
struct get_type_by_index<0, Head, Args...> {
  using type = Head;
};

// 验证Demo
void Demo() {
  std::cout << std::is_same_v<typename get_type_by_index<2, int, double, char, void *>::type , char> << std::endl; // 1
}
```

有了这个工具，我们就可以从类型列表里通过`Index`取出对应的类型了，以此来完成`variant`的构造函数：

```cpp
// 实现构造函数
template <typename... Types>
template <size_t Index, typename... Args>
variant<Types...>::variant(const in_place_index_t<Index> &, Args &&... args): index(Index) {
  // 先把需要构造的类型拿出来
  using data_type = typename get_type_by_index<Index, Args...>::type;
  // 在data处进行就地构造
  new(data) std::decay_t<data_type>(std::forward<Args>(args)...);
}
```

最难的构造已经完成了，我们先实现一下周边功能，析构、拷贝构造和赋值函数先放一放，给出一个阶段性的代码：

```cpp
template <size_t Index>
struct in_place_index_t {}; // 单纯的静态工具，用于传递Index，没有运行期意义

template <size_t Index>
constexpr inline in_place_index_t<Index> in_place_index; // 对应in_place_index_t类型的实例

template <size_t Index, typename Head, typename... Args>
struct get_type_by_index : get_type_by_index<Index - 1, Args...> {};

template <typename Head, typename... Args>
struct get_type_by_index<0, Head, Args...> {
  using type = Head;
};

template <typename... Types>
class variant {
 public:
  template <size_t Index, typename... Args>
  variant(const in_place_index_t<Index> &, Args &&... args);
  // 获取当前序号
  int index() const;
  // 取出数据
  template <size_t Index>
  auto get() const -> std::add_lvalue_reference_t<std::decay_t<typename get_type_by_index<Index, Types...>::type>>;

 private:
  void *data_ = std::malloc(std::max(sizeof(Types)...)); // 计算出最长的Type
  int index_; // 当前生效的数据序号
};

// 实现构造函数
template <typename... Types>
template <size_t Index, typename... Args>
variant<Types...>::variant(const in_place_index_t<Index> &, Args &&... args): index_(Index) {
  // 先把需要构造的类型拿出来
  using data_type = typename get_type_by_index<Index, Args...>::type;
  // 在data处进行就地构造
  new(data_) std::decay_t<data_type>(std::forward<Args>(args)...);
}

// 获取序号
template <typename... Types>
int variant<Types...>::index() const {
  return index_;
}

// 取出数据（这个功能在std::variant中其实实现在std::get中）
template <typename... Types>
template <size_t Index>
auto variant<Types...>::get() const -> std::add_lvalue_reference_t<std::decay_t<typename get_type_by_index<Index, Types...>::type>> {
  using data_type = std::decay_t<typename get_type_by_index<Index, Types...>::type>;
  return *static_cast<data_type *>(data_);
}
```

接下来我们要攻克的，就是析构、拷贝构造、拷贝赋值这几个问题了，它们的难点在于，没有静态的`Index`参数可供使用，但还要找到现在数据的类型。就拿析构来说，析构函数并没有静态的`Index`参数，只有一个运行时的`index`成员，但我们要找到此时`index_`成员表示的`data_`所指向数据的实际类型，然后调用这个类型的析构函数。拷贝构造、拷贝赋值也同样需要先析构现有数据，所以面临同样的问题。

这种情况怎么办呢？类比前面章节介绍的元组的动态get方法，我们这里也采取「静态穷举生成所有可能情况代码」的方法。

以析构为例，在析构时，要根据`index_`去判断当前保存的数据是哪一种类型的，然后去调用对应类型的析构函数。因此，我们需要在静态期就提供每一种类型的析构方法，然后将它们和类型的`Index`关联起来，这样在运行时就可以调用了。

```cpp
template <typename... Types>
class variant {
 public:
  // 无关代码暂时省略 
  ~variant(); // 析构函数
 private:
  void *data_ = std::malloc(std::max(sizeof(Types)...));
  int index_; // 当前生效的数据序号
  // 生成每一个Type下对应类型的析构方法
  template <typename Type>
  void destory_data();
};

template <typename... Types>
template <typename Type>
void variant<Types...>::destory_data() {
  // 用data_指针按照对应的类型调用析构函数
  static_cast<std::add_pointer_t<Type>>(data_)->~Type();
}

// 实现析构函数
template <typename... Types>
variant<Types...>::~variant() {
  // 析构函数中，把所有的index对应的destory_data保存下来（编译期完成这样一个映射表）
  std::array<void (variant<Types...>::*)(), sizeof...(Types)> destory_functions {
    &variant<Types...>::destory_data<Types>... // 按照类型参数展开，把对应的destory_data实例的函数指针保存下来
  };

  // 到了运行期，根据当前实际的index_值，选择对应的析构方法
  if (data_ != nullptr) {
    (this->*destory_functions.at(index_))();
    std::free(data_);
  }
}
```

对于拷贝构造、拷贝赋值来说，首先把原来的内容析构调，然后再根据被复制方的`index_`，来调用对应的构造函数。于是，我们还需要补充一个`index_`与构造函数的映射表，思路和析构完全相同：

```cpp
template <typename... Types>
class variant {
 public:
  // 无关代码先省略
  variant(const variant &va);
 private:
  void *data_ = std::malloc(std::max(sizeof(Types)...));
  int index_; // 当前生效的数据序号

  // 生成每一个Type下对应类型的析构方法
  template <typename Type>
  void destory_data();

  // 生成每一个Type下对应类型的构造方法
  // 注意，由于我们要把生成的所有方法保存在数组中，因此函数类型需要一致，所以参数用泛型指针
  template <typename Type>
  void create_data(const void *obj);
};

template <typename... Types>
template <typename Type>
void variant<Types...>::create_data(const void *obj) {
  // 用data_指针按照对应的类型调用拷贝构造
  new(data_) Type(*static_cast<const Type *>(obj));
}

template <typename... Types>
variant<Types...>::variant(const variant &va): index_(va.index_) {
  // 静态期保存所有类型的构造函数
  std::array<void (variant<Types...>::*)(const void *), sizeof...(Types)> create_functions {
    &variant<Types...>::create_data<Types>...
  };
  // 动态时根据index_调用对应的构造
  (this->*create_functions.at(index_))(va.data_);
}
```

有了这样的思路，那么我们就可以完善所有的代码了，拷贝赋值函数可以按照相同的方法写出来了（只不过需要先析构，再重新构造）。下面给出整个项目的完整代码：

```cpp
// 辅助工具
template <size_t Index>
struct in_place_index_t {}; // 单纯的静态工具，用于传递Index，没有运行期意义

template <size_t Index>
constexpr inline in_place_index_t<Index> in_place_index; // 对应in_place_index_t类型的实例

template <size_t Index, typename Head, typename... Args>
struct get_type_by_index : get_type_by_index<Index - 1, Args...> {};

template <typename Head, typename... Args>
struct get_type_by_index<0, Head, Args...> {
  using type = Head;
};

// variant结构的声明
template <typename... Types>
class variant {
 public:
  template <size_t Index, typename... Args>
  variant(const in_place_index_t<Index> &, Args &&... args);
  variant(const variant &va);
  variant(variant &&va);
  ~variant();
  variant &operator =(const variant &va);
  variant &operator =(variant &&va);
  // 获取当前序号
  int index() const;

  // 取出数据
  template <size_t Index>
  auto get() const -> std::add_lvalue_reference_t<std::decay_t<typename get_type_by_index<Index, Types...>::type>>;

 private:
  void *data_ = std::malloc(std::max(sizeof(Types)...));
  int index_; // 当前生效的数据序号

  // 生成每一个Type下对应类型的析构方法
  template <typename Type>
  void destory_data();

  // 生成每一个Type下对应类型的构造方法
  template <typename Type>
  void create_data(const void *obj);
};

// 实现构造函数
template <typename... Types>
template <size_t Index, typename... Args>
variant<Types...>::variant(const in_place_index_t<Index> &, Args &&... args): index_(Index) {
  using data_type = typename get_type_by_index<Index, Args...>::type;
  new(data_) std::decay_t<data_type>(std::forward<Args>(args)...);
}

// 实现析构函数
template <typename... Types>
variant<Types...>::~variant() {
  // 析构函数中，把所有的index对应的destory_data保存下来（编译期完成这样一个映射表）
  std::array<void (variant::* const)(), sizeof...(Types)> destory_functions {
    &variant::destory_data<Types>...
  };

  // 到了运行期，根据当前实际的index_值，选择对应的析构方法
  if (data_ != nullptr) {
    (this->*destory_functions.at(index_))();
    std::free(data_);
  }
}

// 实现拷贝构造函数
template <typename... Types>
variant<Types...>::variant(const variant &va): index_(va.index_) {
  // 静态期保存所有类型的构造函数
  std::array<void (variant<Types...>::*)(const void *), sizeof...(Types)> create_functions {
    &variant<Types...>::create_data<Types>...
  };

  // 动态时根据index_调用对应的构造
  (this->*create_functions.at(index_))(va.data_);
}

// 实现拷贝赋值函数
template <typename... Types>
variant<Types...> &variant<Types...>::operator =(const variant &va) {
  // 先析构现有数据
  std::array<void (variant<Types...>::*)(), sizeof...(Types)> destory_functions {
    &variant<Types...>::destory_data<Types>...
  };
  (this->*destory_functions.at(index_))();
  
  // 再重新构造
  std::array<void (variant<Types...>::*)(const void *), sizeof...(Types)> create_functions {
    &variant<Types...>::create_data<Types>...
  };
  (this->*create_functions.at(index_))(va.data_);
  
  return *this;
}

// 实现移动构造函数
template <typename... Types>
variant<Types...>::variant(variant &&va): index_(va.index_), data_(va.index_) {
  // 上面直接浅拷贝即可，然后把被移动的data_置空
  va.data_ = nullptr;
  va.index_ = -1; // 标记为不合法值
}

// 实现移动赋值函数
template <typename... Types>
variant<Types...> &variant<Types...>::operator =(variant &&va) {
  // 先析构现有数据
  std::array<void (variant<Types...>::*)(), sizeof...(Types)> destory_functions {
    &variant<Types...>::destory_data<Types>...
  };
  (this->*destory_functions.at(index_))();
  
  // 再浅拷贝
  data_ = va.data_;
  index_ = va.index_;
  // 把被移动的data_置空
  va.data_ = nullptr;
  va.index_ = -1; // 标记为不合法值
  return *this;
}

// 私有方法的实现
template <typename... Types>
template <typename Type>
void variant<Types...>::create_data(const void *obj) {
  // 用data_指针按照对应的类型调用拷贝构造
  new(data_) Type(*static_cast<const Type *>(obj));
}

template <typename... Types>
template <typename Type>
void variant<Types...>::destory_data() {
  // 用data_指针按照对应的类型调用析构函数
  static_cast<std::add_pointer_t<Type>>(data_)->~Type();
}

// 公有方法的实现
// 获取序号
template <typename... Types>
int variant<Types...>::index() const {
  return index_;
}

// 取出数据（这个功能在std::variant中其实实现在std::get中）
template <typename... Types>
template <size_t Index>
auto variant<Types...>::get() const -> std::add_lvalue_reference_t<std::decay_t<typename get_type_by_index<Index, Types...>::type>> {
  using data_type = std::decay_t<typename get_type_by_index<Index, Types...>::type>;
  return *static_cast<data_type *>(data_);
}
```

### 通过类型访问

在上一节里，我们实现的简化版`variant`仅仅提供了一个通过`Index`来获取数据的方法。但有时我们可能更希望通过类型来获取数据（假如该类型是唯一的）。因此，我们就希望能够提供一个，在类型唯一的前提下，通过类型来获取数据的`get`方法。

既然已经有了用`Index`来获取的方法，那么只需要想办法把类型转换成`Index`即可，所以我们的思路就是「逐个来试，找到为止」。请看代码：

```cpp
// 辅助工具，用于在列表中找到第一次出现Target类型的Index
template <typename Target, typename Head, typename... Types>
struct get_index_from_types {
  // 递归查找，把上一层的递归值+1
  constexpr static int value = get_index_from_types<Target, Types...>::value + 1;
};

template <typename Target, typename... Types>
struct get_index_from_types<Target, Target, Types...> { // 列表第一项是目的类型时，视为找到
  constexpr static int value = 0;
};

template <typename Target>
struct get_index_from_types<Target, Target> { // 只剩一个并且匹配到了，仍视为找到
  constexpr static int value = 0;
};

template <typename Target, typename Head>
struct get_index_from_types<Target, Head> { // 只剩一个还不匹配时，视为没找到
};

// 验证用Demo
void Demo() {
  std::cout << get_index_from_types<int, double, char, int>::value << std::endl; // 2
  std::cout << get_index_from_types<int, int, char, int>::value << std::endl; // 0
  std::cout << get_index_from_types<int, int>::value << std::endl; // 0
  std::cout << get_index_from_types<int, double, char, std::string>::value << std::endl; // ERR，未找到，所以报错
}
```

可能有读者会疑惑，为什么要针对只剩一个切匹配到的情况单独给一个特化？这是因为，假如我们不提供`get_index_from_types<Target, Target>`的特化，那么根据优先级原则，`get_index_from_types<int, int>`会同时命中`get_index_from_types<Target, Target, Types...>`和`get_index_from_types<Target, Head>`这两种特化，会报二义性错误。所以我们不得不单独给出`get_index_from_types<Target, Target>`的特化。

有了这个工具就好办了，我们就可以给`variant`提供一个通过类型来获取数据的接口了：

```cpp
template <typename... Types>
class variant {
 public:
  // 省略无关代码
  // 取出数据-通过Index
  template <size_t Index>
  auto get() const -> std::add_lvalue_reference_t<std::decay_t<typename get_type_by_index<Index, Types...>::type>>;
  // 取出数据-通过类型
  template <typename T>
  auto get() const -> std::add_lvalue_reference_t<std::decay_t<T>>;
 private:
  void *data_ = std::malloc(std::max(sizeof(Types)...));
  int index_; // 当前生效的数据序号
  // 省略无关代码
};

template <typename... Types>
template <typename T>
auto variant<Types...>::get() const -> std::add_lvalue_reference_t<std::decay_t<T>> {
  // 先拿出Index
  constexpr int Index = get_index_from_types<T, Types...>::value;
  // 然后再调用原本的get
  return this->get<Index>();
}
```

这里就不再跟上节的拼一个完整代码了，主要是希望读者掌握在类型列表中找到某个类型的位置的模板元编程方法。

### 访问器

前面的篇幅我们介绍了如何实现一个简化版的`variant`，而由于STL中已经提供了`std::variant`，这是一个成熟的工具了，所以大家在实际开发应用中，可以直接使用STL的工具。后面的篇幅中遇到使用多选一结构的场景也会切换为使用`std::variant`，而不再使用前面例程中的`variant`。读者可以参考[C++官方参考手册](https://www.apiref.com/cpp-zh/cpp/utility/variant.html)中对于它的介绍。

在使用`std::variant`时，我们经常会有这样的一个场景：对于可能出现的多种类型，每种类型对应一个不同的处理函数，然后根据运行时实际的类型选择不同的
函数。用代码示例就是：

```cpp
// 针对不同类型的处理函数
void f(int data) {}
void f(double data) {}
void f(char data) {}

void Demo() {
  std::variant<int, double, char> va;
  if (auto int_data = std::get_if<int>(&va); int_data != nullptr) { // 如果是int类型
    f(*int_data);
  } else if (auto double_data = std::get_if<double>(&va); double_data != nullptr) { // 如果是double类型
    f(*double_data);
  } else if (auto char_data = std::get_if<char>(&va); char_data != nullptr) { // 如果是char类型
    f(*char_data);
  }
}
```

这样的用法应该很常见，但是按照上例的写法会很冗长，因此，如果能够提供一个工具，直接作用在`variant`上，自动根据当前数据类型来调用对应的函数，岂不是会让代码更加简洁方便？这就是这一节要介绍的内容——访问器(visitor)。

#### 一个简单的访问器

那么，说来说去，这个所谓的「访问器」到底是什么呢？简单来说，就是对刚才那一组`f`函数进行的一个封装，比如说：

```cpp
struct Vis {
  void f(int data) {}
  void f(double data) {}
  void f(char data) {}
};
```

这就是一个简单的访问器，可以用于处理含有`int`、`double`和`char`类型的`variant`。我们把「用访问器来处理`variant`」的这个动作就叫做「访问」。不过由于这里把用于访问的方法叫做了`f`，并不是STL中标准规定的，因此为了适配「访问」工具，我们这里要按照STL中的规定，使用仿函数方法，也就是把`f`改成`operator()`：

```cpp
struct Vis {
  void operator()(int data) {}
  void operator()(double data) {}
  void operator()(char data) {}
};
```

STL中提供了`std::visit`方法，表示「访问」这个动作，也就是将访问器作用于`variant`上。我们先来介绍访问器的用法，然后下一节再来介绍「访问」方法是如何实现的。

先来看一下`std::visit`的函数原型：

```cpp
template <typename Visitor, typename... Variants>
constexpr auto visit(Visitor&& vis, Variants&&... vars);
```

很简单，传入一个访问器，再传入**一组**`variant`。也就是说，这个函数是支持传入多个`variant`的情况，不过暂时我们先不考虑这么复杂，先看看对于一个`variant`的情况。

需要说明的是，在C++17标准下，我们无法指定返回值，而是要求访问器中所有方法的返回值必须一致（可以理解为，前面例程中的`f`函数重载，都必须是同一个返回值类型）。在C++20中此方法进行了扩展，支持不同类型返回值的访问器，但要求手动指定`visit`的返回值：

```cpp
// C++20起
template <typename R, typename Visitor, typename... Variants>
constexpr R visit(Visitor&& vis, Variants&&... vars);
```

同样，我们还是简化问题，只考虑C++17标准中，访问器中的方法返回值一致的情况。前面的`Vis`访问器就是符合要求的，因为里面每一个`operator()`都是`void`返回值，所以就可以这样来调用：

```cpp
void Demo() {
  std::variant<int, double, char> va;
  // 创建访问器实例
  Vis vis;
  // 通过访问器进行访问
  std::visit(vis, va);
}
```

`std::visit`函数就会根据`variant`中当前的数据，去调用访问器中对应的处理方法。不过访问器如果仅仅只能这样来写，那还是太LOW了，我们来看看它怎么飞起来的吧。

#### 可动态构造的访问器

要想正确使用访问器，就要求访问器中的每一个用于访问的方法都要可以正常分发到。举刚才的例子来说：

```cpp
// 一个支持int, double, char的访问器
struct Vis {
  void f(int data) {std::cout << 1;}
  void f(double data) {std::cout << 2;}
  void f(char data) {std::cout << 3;}
};

void Demo() {
  // 创建访问器实例
  Vis vis;
  // 通过访问器方法应该能够正确分发数据
  vis.f(1); // 1
  vis.f(1.0); // 2
  vis.f('A'); // 3
}
```

也就是说，我们分别把`int`、`double`和`char`传入访问器的访问方法中，是可以正确调用到对应的方法的。上面的例子中，访问方法都定义在同一个访问器类中，形成重载函数，这自然是没问题的。可如果，访问方法在不同的类型中，或者是以独立函数、函数对象、lambda等形式存在的话怎么办？

我们首先考虑，如果这3个访问函数，分属3个类，要怎么构造这个访问器呢？

```cpp
struct Vis1 {
  void f(int data) {std::cout << 1;}
};

struct Vis2 {
  void f(int data) {std::cout << 2;}
};

struct Vis3 {
  void f(int data) {std::cout << 3;}
};
```

那么此时，我们就构造一个「集合类」，能够同时复用3个类的`f`函数：

```cpp
struct Vis : Vis1, Vis2, Vis3 { // 多继承，先把函数继承下来
  using Vis1::f; // 再复用父类的f函数
  using Vis2::f;
  using Vis3::f;
};
```

这样我们就间接构造了一个访问器。下面的调用也是合法的：

```cpp
void Demo() {
  // 创建访问器实例
  Vis vis;
  // 通过访问器方法应该能够正确分发数据
  vis.f(1); // 1
  vis.f(1.0); // 2
  vis.f('A'); // 3
}
```

既然`f`函数通过这种方法可行，那么更加规范的`opeartor()`函数也应该是同理：

```cpp
struct Vis1 {
  void operator()(int data) {std::cout << 1;}
};

struct Vis2 {
  void operator()(double data) {std::cout << 2;}
};

struct Vis3 {
  void operator()(char data) {std::cout << 3;}
};

struct Vis : Vis1, Vis2, Vis3 { 
  using Vis1::operator(); 
  using Vis2::operator();
  using Vis3::operator();
};

void Demo() {
  // 创建访问器实例
  Vis vis;
  // 通过访问器方法应该能够正确分发数据
  vis(1); // 1
  vis(1.0); // 2
  vis('A'); // 3
}
```

利用这种方法，我们就可以进行访问器的合并，并且，可以写一个模板，来支持任意类型的访问器合并：

```cpp
template <typename... Base_Visitor>
struct Visitor : Base_Visitor... { // 多继承父类展开
  using Base_Visitor::operator()...; // 函数复用展开
}

void Demo() {
  // 直接用模板构造访问器
  Visitor<Vis1, Vis2, Vis3> vis;
  vis(1); // 1
  vis(1.0); // 2
  vis('A'); // 3
}
```

这样就实现了一个动态生成的访问器（注意这里的「动态」指的是可以根据不同类型，生成不同的访问器，并不是指「运行时」。毕竟模板都是编译期动作。）

我们知道lambda表达式的本质就是一个匿名的仿函数类型，那么是不是我们也可以直接用lambda来创建访问器呢？

```cpp
void Demo() {
  auto vis1 = [](int data) {};
  auto vis2 = [](double data) {};
  auto vis3 = [](char data) {};
  Visitor<decltype(vis1), decltype(vis2), decltype(vis3)> vis;
  vis(1);
  vis(1.0);
  vis('A');
}
```

OK，确实没有问题，只不过这种写法有点奇怪，我们能不能想办法让访问器自动推导出lambda的类型呢？大家还记得「推导指南」吗？由于`Visitor`只能提供默认的构造函数（因为本来也没有什么需要构造的成员），所以我们不能指望编译期通过构造参数来推导实例化类型，所以只能手写一个推导指南了：

```cpp
template <typename... Base_Visitor>
struct Visitor : Base_Visitor... {
  using Base_Visitor::operator()...; 
}

// 补充一个推导指南
template <typename... Types>
Visitor(Types &&...) -> Visitor<std::decay_t<Types>...>;

void Demo() {
  auto vis1 = [](int data) {};
  auto vis2 = [](double data) {};
  auto vis3 = [](char data) {};
  // 直接用lambda构造访问器
  Visitor vis{vis1, vis2, vis3};
  vis(1);
  vis(1.0);
  vis('A');
}
```

由于实现了推导指南，编译期就会按照指南，把`Visitor vis{vis1, vis2, vis3}`推到为`Visitor<decltype(vis1), decltype(vis2), decltype(vis3)>`，而又因为`Visitor`并没有一个对应3个参数的构造函数，**因此这里还是会调用默认的无参构造函数**，而不会报错（多啰嗦一句，请读者一定要分清这里编译期和运行期的不同。模板实例化推导是编译期事项，而构造函数则是运行期事项，二者并不冲突。当没有实现自定义的推导指南时，编译器会根据构造参数来推导，而如果实现了就会按照推导指南来推导，这与调用哪个构造函数并没有直接关系）。

甚至，我们都可以直接把lambda写到`vis`里面：

```cpp
void Demo() {  
  Visitor vis{
    [](int data) {},
    [](double data) {},
    [](char data) {}
  };

  vis(1);
  vis(1.0);
  vis('A');
}
```

注意，如果你发现传变量进去是OK的，但是直接传lambda会报错的话，要检查一下推导指南中有没有去掉引用符（或者`decay`），因为lambda本身是xvalue，会推导出右值引用类型，而引用类型不能做父类，所以没有去掉引用符的话会引起报错。

掌握了访问器的写法，操作`variant`就更方便了，比如说：

```cpp
// 通用访问器
template <typename... Base_Visitor>
struct Visitor : Base_Visitor... {
  using Base_Visitor::operator()...; 
}

template <typename... Types>
Visitor(Types &&...) -> Visitor<std::decay_t<Types>...>;

void Demo() {
  std::variant<int, double char> va;

  // 直接在visit函数里构造访问器
  int res = std::visit(Visitor {
    [](int data)->int {return 1;},
    [](double data)->int {return 2;},
    [](char data)->int {return 3}
  }, va);
}
```

### 访问函数

上一节我们介绍了如何编写一个「访问器」，以及用`std::visit`来实现访问。那么这一节就来手撸一个访问函数`visit`，用于使用访问器来访问`variant`。

前面我们介绍过如何写一个动态的`get`方法，这里的思路与它如出一辙，在静态编译期把`variant`的所有情况都生成一个对应的方法，这里我们就需要与访问器进行关联，调用对应的访问方法。等到运行时，根据当前`variant`的`index`值选择调用对应的访问函数。

我们这里只实现一个支持单个`variant`的情况，如果读者希望实现一个跟STL中相同的支持多个`variant`的情况可以尝试自行完成。话不多说，直接上代码：

```cpp
// 辅助函数2
template <typename Visitor, typename R, typename Variant, size_t Index>
R visit_detail_invoke(Visitor &&vis, Variant &&var) {
  return std::invoke(vis, std::get<Index>(var));
}

// 辅助函数1
template <typename Visitor, typename R, typename Variant, size_t... Index>
R visit_detail(Visitor &&vis, Variant &&var, const std::index_sequence<Index...> &) {
  std::array<R(Visitor &&, void *), std::variant_size_v<Variant>> funcs {
    // 按照变参展开，如果遇到类型相同的也会匹配同一个函数实例
    &visit_detail_invoke<Visitor, R, Variant, Index>...
  };

  // 根据运行期的index选择调用哪个函数
  return funcs.at(var.index())(vis, var);
}

template <typename Visitor, typename... Args>
auto visit(Visitor &&vis, std::variant<Args...> &&var) -> decltype(vis(std::get<0>(var))) {
  using R = decltype(vis(std::get<0>(var))); // 用0号类型类型去调用访问器，只是为了推导出对应的返回值类型
  using Seq = std::make_index_sequence<sizeof...(Args)>; // 构造一个序列，用于展开

  return visit_detail<Visitor, std::variant<Args...>>(vis, var, Seq{});
}
```

先别急，我来解释一下上面做的事。首先我们先看`visit`函数，这一层要做2件事，首先是取得返回值。我们知道在C++17标准中的`visit`要求访问器返回值类型必须保持一致，所以这里，不管用`variant`的哪种类型成员去访问，返回值结果都应该是一致的。又因为我们不知道类型的个数，但至少它能有1个类型，所以就用0号去获取。`decltype(vis(std::get<0>(var)))`就是尝试用0号类型去访问，获得的返回值。

接下来，就是所谓编译期要把所有可能得情况都生成一个对应处理函数的步骤。由于`variant`中可能会出现多种相同类型的情况，这种情况下，相同类型的数据应该能命中同一个访问器方法才对。于是我们还是需要按照`Index`展开，而不是按照`Args...`展开（因为如果按类型展开的话，遇到重复类型，调用`std::get<T>`时会报错）。既然要按`Index`展开，就需要先生成一个从`0`到`size - 1`的序列，于是我们用了`std::make_index_sequence`来生成序列（这部分的具体实现可以参考前面动态get的章节）。

第二层`visit_detail`就不再接收类型变参，转为接收序列，因此`variant`的具体参数就被屏蔽了，在`visit`里调用的时候会把`std::variant<Args...>`整体类型传递给`visit_detail`的`Variant`参数。接下来就是按照`Index`展开了，对每一种可能出现的类型进行适配，把对应的处理函数（`visit_detail_invoke`的一个实例）保存下来。(注意这里我们用了`std::array<R(xxx), N>`类型，数组元素是函数类型，其实就等价与函数指针类型，也就是说等价于`std::array<R(*)(xxx), N>`。）

第三层`visit_detail_invoke`就是使用访问器进行访问了，首先把对应`Index`的数据取出来，然后调用访问器方法即可。（例子里使用了`std::invoke`，其实直接写成`vis(std::get<Index>(var));`也是一样的。）

至此，我们从「多选一结构」到「访问器」到「访问函数」，体验了一个闭环，希望以此为例子，能让读者深度体验模板元编程的用途和使用方法。

## 模板范式

详细体验过模板元编程理念和方法之后，我们要再来介绍一下C++的多范式。虽然一开始C++是为了给C语言扩充以适配OOP（面相对象编程）范式的，但后来成熟了的C++语言本身开放性很足，因此能够使用多种编程范式。同时又因为STL本身并没有使用OOP范式，而是把模板玩出了花，因此「模板范式」在C++中也有了弥足轻重的地位。

所谓「模板范式」，其核心理念就是「在编译期，确定尽量多的事情」。也就是说，它倾向于把更多的工作交给编译期来完成，以减少程序运行时期的不确定因素。

举例来说，某处代码需要调用一个对象的`method`方法，它并不关心这个对象的类型是什么，只要它实现了`method`方法就可以使用。单独这么说可能有点抽象，我们换一个更加贴近实际的例子。前端开发中，`TableView`类表示一个列表视图，每一个列表视图的实例都需要一个数据的提供者，来告诉他这个列表中应该显示哪些内容。但是，`TableView`它并不关心这个数据是谁给的，有可能是网络回包，有可能是主控制器，也有可能是其他的控件。是谁不重要，只要能给我提供数据即可，所以我要求这个数据的提供方实现`std::string GetData()`方法。

对于上面这个例子来说，如果我们采用传统OOP范式，自然会想到定义一个「协议类」（或者叫「接口类」），来作为数据提供方的类型。

```cpp
// 协议类
class TableViewDataSource {
 public:
  virtual std::string GetData() const;
};

// 使用者
class TableView {
  public:
   void SetDataSource(TableViewDataSource *data_source);
  private:
   TableViewDataSource *data_source_;
};
```

当`TableView`需要获取数据时，只需要从数据源调用方法即可：

```cpp
if (data_source_ != nullptr) {
  auto data = data_source_->GetData();
  // 处理data
}
```

此时，假如要充当数据源的是一个http请求类，我们就可以通过「继承协议类」的方式来「遵守协议」，让它成为「数据源」。

```cpp
// 它可能有自己原本的父类，称为「属性父类」，而成为数据源继承的是「协议父类」
class HttpRequest : public SocketReq, public TableViewDataSource {
 public:
  ... // 一些自己的方法
  // 实现协议类方法
  std::string GetData() const override;
};
```

这是前端开发中非常常用的手段，也是最符合OOP范式的方法。但我们发现，OOP范式的实现基于多态，也就是`TableViewDataSource`类型的泛化子类中的方法，对应的`GetData`是一个虚函数。C++中，虚函数的实现基于虚函数表，也就是说，所有`TableViewDataSource`的子类的实例，内部都含有一个虚函数表，里面存放了所有虚函数对应的函数指针。

显然，这种方式主要的处理阶段是运行时，运行时通过对象的虚函数表，找到对应的虚函数再进行调用的。而C++除了可以使用这种更加依靠运行时的OOP范式以外，还可以使用更加依赖编译期的模板范式来实现相同的方法。请看示例：

```cpp
// 用于判断类型T中是否含有GetData方法
template <typename T, typename V = std::string>
struct IsDataSource : std::false_value {};

template <typename T>
struct IsDataSource<T, decltype(std::declval<T>().GetData())> : std::true_value {};
class TableView {
 public:
  template <typename DataSource>
  std::enable_if_t<IsDataSource<DataSource>::value, std::string>
  GetData(DataSource *data_source) const {
    return data_source->GetData();
  };
};
```

这里，我们直接在静态编译期就判断了传进来的类型是否实现了`GetData`方法，（具体的判断方法在前面章节都已经介绍过了），这样一来，只要你的类型实现了`GetData`方法，就可以直接用作数据源，无需提供协议类，也就无需额外生成虚函数表，运行时的开销就被降低了。

```cpp
// 不需要多继承，不会改变继承链
class HttpRequest : public SocketReq {
 public:
  ... // 一些自己的方法
  // 实现数据源方法，不需要虚函数
  std::string GetData() const;
};

// 使用时
void Demo() {
  HttpRequest hr;
  TableView tv;
  tv.GetData(&hr); // hr、tv中都不携带虚函数表，如果hr的类型不符合要求，编译期就直接会被拦截
}
```

这就是所谓的「模板范式」，倾向于把尽可能多的工作放在编译期。当然，它的缺点也很明显，就是可读性会变差，如果仅仅是上面示例这种「协议类」的需求，笔者个人还是更倾向于选择使用OOP范式的写法，维护性会更高一些。但是借此例子希望读者能够认识到「模板范式」，体会它与OOP范式的不同，以及理解C++的多范式性。

当然，上面的这个例子不仅仅是OOP范式和模板范式可以实现，我们是甚至都可以用函数式编程的思路来解决：

```cpp
class TableView {
 public:
  void SetDataSource(std::function<std::string()> func) {
    get_data_func_ = func;
  }
  std::string GetData() const {
    return get_data_func_();
  };
 private:
  std::function<std::string()> get_data_func_;
};

class HttpRequest : public SocketReq {
 public:
  std::string GetData() const;
};

void Demo() {
  TableView tv;
  HttpRequest hr;
  tv.SetDataSource(std::bind(&HttpRequest::GetData, &hr)); // 脱离数据源对象实体，直接把函数传进去
  tv.GetData(); 
}
```

这跟模板范式又是完全不同的思路，不过函数式编程不是本篇的重点，因此不在这里过多介绍了。

## 总结与感悟

整个C++模板编程教程系列到这里就接近尾声了，如果你能读到这里，笔者非常感谢支持！最后这一章将以Q&A的方式，展示一些笔者被问到的，或者是一些笔者认为大家可能会有疑惑的问题的解答，同时穿插着希望分享给读者的感悟。

### Q&A

#### Q1：C++为什么不能官方支持反射、RTTI等这些特性？

这个问题源于C++本身的设计理念和历史因素。C++诞生之时，就是希望对C语言进行一个扩展，或者我们可以简单理解为，C++就是C的一个新版本，所以它打一开始就不是冲着「一门新的编程语言」来设计的，所以这就注定C++不会颠覆C语言的理念。

另一方面，在C++诞生的那个年代，硬件资源其实是非常昂贵的，所以更加倾向于把更多的工作留给编译期，这样可以「一劳永逸」，与此同时，C++也是像C语言一眼，考虑的是跨平台，能够支持尽可能多的架构、平台、内核等，所以，编译器可以根据不同的平台，做针对性的优化。而如果把这些工作放到了运行期，那编译器就望尘莫及了。

所以说，C++的设计理念就让它更加注重编译期处理，模板就是非常针对性的语法，因此C++一直都在扩充模板语法的各种功能，而并没有把重点放在运行期的功能特性上。

#### Q2：OC也是C的扩充，为什么就不像C++这么蹩脚呢？

也有读者曾问过我，Objective-C也是基于C语言扩展来的，可以完全兼容C，但它却完全没有受C语言的束缚，将静态期和运行期的分离做得相当到位，同时也很好地支持反射、RTTI等特性。为什么C++不这样做，而是要用很多蹩脚的静态期语法？

笔者觉得这个问题问得本身就有点小问题，其实OC跟C++对于C语言来说完全是两个维度。在Q1里面笔者解释过，C++原本是作为C的新版本出现的，换句话说，C++其实就是C语言，它自然进化后成为了C++，而现在的C语言反倒成为了原始C语言的一个分支，或者说一个克隆版了。

OC是在C的基础上，扩充了很多动态语言特性来的，而这里跟C++是完全不冲突的。因为OC是在「C的基础上」扩充的，而「C++就是新版的C」，那么OC自然也可以支持C++，或者说，使用C++的静态属性，在此基础上扩展动态特性，这也是OK的。为了区分，这种语言也被叫做Objective-C++。OC的动态特性语法和C++的静态特性语法可以同时存在，完全不冲突。

这种感觉就像，C++是「长大后的C」，而OC是「拿着武器的C」，那么长大后的C也可以拿着武器呀。因此说C++和OC对C的扩充完全是两个维度的，互不冲突。

#### Q3：模板元编程语法晦涩难懂，实际开发中是不是应当避免？

这也是一个灵魂拷问问题，对于C++的模板元编程，业界的看法一致都是两极分化严重。支持的人爱不释手，反对的人如视仇雠。而且双方长时间稳定地对峙，谁也别想说征服谁。

笔者还是认为，完事不可一棒子打死，既然大家能争执，就说明这件事情一定同时存在正反两面。我们要做的并不是站队，然后一定要跟对方争个输赢来。而是应当首先，学会、掌握它，然后去客观分析它的优缺点，并且针对使用的场景得出是否应当使用的结论。

C++模板的优点就是尽可能多的事情在编译期解决了，性能会高，并且有时候一些代码改成模板生成会减少代码量，提升开发效率；而它的缺点也是显而易见的，就是语法晦涩，并且门槛高，需要对使用者有一定技术上的要求。

因此，在实际开发中，应当根据工程项目注重的点的情况、项目成员平均技术水平的情况、项目开发投入的情况、项目潜在交接可能性情况、项目负责人员流动性情况等等等等诸多因素去考虑，这里应当使用哪种范式和要求。而不要一棍子打死，全面禁用某个特性。

而对于个人来说，无论是否需要投入生产，笔者认为都应当自己先掌握，掌握了我们才有去评判的资格。这就好比「我会做饭，但是我不需要做（有人为我服务，偶尔没人给我做了我也能自己做）」跟「我不会做饭，我只能指着别人给我做（没人做的时候我只能饿肚子）」是截然不同的处境。

#### Q4：模板范式是不是才算真正的「C++味道」？

这个问题跟Q3其实正好是反过来的。的确，模板范式是STL整个采用的编程风格，也是很多真正意义上的「C++崇尚者」强烈推荐的方式。

模板是C++的特色，的确是其他编程语言中见不到的，非常有特点、非常奇特的语法，甚至可以称作「奇技淫巧」的一种用法了。所以可能会让人有「这才是真正的C++」的感觉。

但笔者认为，C++最大的用途一定是编写程序，只有它投入了生产，创造了价值，它才有意义。这就跟数学、物理学等等学科是相同的道理。我们研究这些学科，最大的意义是它能够为我们的生产提供帮助，提供方法。举例来说，我们想计算一个矩形材料的面积，只要用「长×宽」这就够了。你不能说，这种算法不够「数学」，我们一定要用专业的计算面积的数学方法，硬要把它写成：

<svg xmlns="http://www.w3.org/2000/svg" width="14.305ex" height="5.23ex" role="img" focusable="false" viewBox="0 -1399.9 6322.7 2311.8" xmlns:xlink="http://www.w3.org/1999/xlink" aria-hidden="true" style="vertical-align: -2.063ex;"><defs><path id="MJX-1-TEX-I-1D446" d="M308 24Q367 24 416 76T466 197Q466 260 414 284Q308 311 278 321T236 341Q176 383 176 462Q176 523 208 573T273 648Q302 673 343 688T407 704H418H425Q521 704 564 640Q565 640 577 653T603 682T623 704Q624 704 627 704T632 705Q645 705 645 698T617 577T585 459T569 456Q549 456 549 465Q549 471 550 475Q550 478 551 494T553 520Q553 554 544 579T526 616T501 641Q465 662 419 662Q362 662 313 616T263 510Q263 480 278 458T319 427Q323 425 389 408T456 390Q490 379 522 342T554 242Q554 216 546 186Q541 164 528 137T492 78T426 18T332 -20Q320 -22 298 -22Q199 -22 144 33L134 44L106 13Q83 -14 78 -18T65 -22Q52 -22 52 -14Q52 -11 110 221Q112 227 130 227H143Q149 221 149 216Q149 214 148 207T144 186T142 153Q144 114 160 87T203 47T255 29T308 24Z"></path><path id="MJX-1-TEX-N-3D" d="M56 347Q56 360 70 367H707Q722 359 722 347Q722 336 708 328L390 327H72Q56 332 56 347ZM56 153Q56 168 72 173H708Q722 163 722 153Q722 140 707 133H70Q56 140 56 153Z"></path><path id="MJX-1-TEX-LO-222B" d="M114 -798Q132 -824 165 -824H167Q195 -824 223 -764T275 -600T320 -391T362 -164Q365 -143 367 -133Q439 292 523 655T645 1127Q651 1145 655 1157T672 1201T699 1257T733 1306T777 1346T828 1360Q884 1360 912 1325T944 1245Q944 1220 932 1205T909 1186T887 1183Q866 1183 849 1198T832 1239Q832 1287 885 1296L882 1300Q879 1303 874 1307T866 1313Q851 1323 833 1323Q819 1323 807 1311T775 1255T736 1139T689 936T633 628Q574 293 510 -5T410 -437T355 -629Q278 -862 165 -862Q125 -862 92 -831T55 -746Q55 -711 74 -698T112 -685Q133 -685 150 -700T167 -741Q167 -789 114 -798Z"></path><path id="MJX-1-TEX-I-1D44E" d="M33 157Q33 258 109 349T280 441Q331 441 370 392Q386 422 416 422Q429 422 439 414T449 394Q449 381 412 234T374 68Q374 43 381 35T402 26Q411 27 422 35Q443 55 463 131Q469 151 473 152Q475 153 483 153H487Q506 153 506 144Q506 138 501 117T481 63T449 13Q436 0 417 -8Q409 -10 393 -10Q359 -10 336 5T306 36L300 51Q299 52 296 50Q294 48 292 46Q233 -10 172 -10Q117 -10 75 30T33 157ZM351 328Q351 334 346 350T323 385T277 405Q242 405 210 374T160 293Q131 214 119 129Q119 126 119 118T118 106Q118 61 136 44T179 26Q217 26 254 59T298 110Q300 114 325 217T351 328Z"></path><path id="MJX-1-TEX-N-30" d="M96 585Q152 666 249 666Q297 666 345 640T423 548Q460 465 460 320Q460 165 417 83Q397 41 362 16T301 -15T250 -22Q224 -22 198 -16T137 16T82 83Q39 165 39 320Q39 494 96 585ZM321 597Q291 629 250 629Q208 629 178 597Q153 571 145 525T137 333Q137 175 145 125T181 46Q209 16 250 16Q290 16 318 46Q347 76 354 130T362 333Q362 478 354 524T321 597Z"></path><path id="MJX-1-TEX-I-1D459" d="M117 59Q117 26 142 26Q179 26 205 131Q211 151 215 152Q217 153 225 153H229Q238 153 241 153T246 151T248 144Q247 138 245 128T234 90T214 43T183 6T137 -11Q101 -11 70 11T38 85Q38 97 39 102L104 360Q167 615 167 623Q167 626 166 628T162 632T157 634T149 635T141 636T132 637T122 637Q112 637 109 637T101 638T95 641T94 647Q94 649 96 661Q101 680 107 682T179 688Q194 689 213 690T243 693T254 694Q266 694 266 686Q266 675 193 386T118 83Q118 81 118 75T117 65V59Z"></path><path id="MJX-1-TEX-N-28" d="M94 250Q94 319 104 381T127 488T164 576T202 643T244 695T277 729T302 750H315H319Q333 750 333 741Q333 738 316 720T275 667T226 581T184 443T167 250T184 58T225 -81T274 -167T316 -220T333 -241Q333 -250 318 -250H315H302L274 -226Q180 -141 137 -14T94 250Z"></path><path id="MJX-1-TEX-I-1D465" d="M52 289Q59 331 106 386T222 442Q257 442 286 424T329 379Q371 442 430 442Q467 442 494 420T522 361Q522 332 508 314T481 292T458 288Q439 288 427 299T415 328Q415 374 465 391Q454 404 425 404Q412 404 406 402Q368 386 350 336Q290 115 290 78Q290 50 306 38T341 26Q378 26 414 59T463 140Q466 150 469 151T485 153H489Q504 153 504 145Q504 144 502 134Q486 77 440 33T333 -11Q263 -11 227 52Q186 -10 133 -10H127Q78 -10 57 16T35 71Q35 103 54 123T99 143Q142 143 142 101Q142 81 130 66T107 46T94 41L91 40Q91 39 97 36T113 29T132 26Q168 26 194 71Q203 87 217 139T245 247T261 313Q266 340 266 352Q266 380 251 392T217 404Q177 404 142 372T93 290Q91 281 88 280T72 278H58Q52 284 52 289Z"></path><path id="MJX-1-TEX-N-29" d="M60 749L64 750Q69 750 74 750H86L114 726Q208 641 251 514T294 250Q294 182 284 119T261 12T224 -76T186 -143T145 -194T113 -227T90 -246Q87 -249 86 -250H74Q66 -250 63 -250T58 -247T55 -238Q56 -237 66 -225Q221 -64 221 250T66 725Q56 737 55 738Q55 746 60 749Z"></path><path id="MJX-1-TEX-I-1D451" d="M366 683Q367 683 438 688T511 694Q523 694 523 686Q523 679 450 384T375 83T374 68Q374 26 402 26Q411 27 422 35Q443 55 463 131Q469 151 473 152Q475 153 483 153H487H491Q506 153 506 145Q506 140 503 129Q490 79 473 48T445 8T417 -8Q409 -10 393 -10Q359 -10 336 5T306 36L300 51Q299 52 296 50Q294 48 292 46Q233 -10 172 -10Q117 -10 75 30T33 157Q33 205 53 255T101 341Q148 398 195 420T280 442Q336 442 364 400Q369 394 369 396Q370 400 396 505T424 616Q424 629 417 632T378 637H357Q351 643 351 645T353 664Q358 683 366 683ZM352 326Q329 405 277 405Q242 405 210 374T160 293Q131 214 119 129Q119 126 119 118T118 106Q118 61 136 44T179 26Q233 26 290 98L298 109L352 326Z"></path></defs><g stroke="currentColor" fill="currentColor" stroke-width="0" transform="matrix(1 0 0 -1 0 0)"><g data-mml-node="math"><g data-mml-node="mi"><use xlink:href="#MJX-1-TEX-I-1D446"></use></g><g data-mml-node="mo" transform="translate(922.8, 0)"><use xlink:href="#MJX-1-TEX-N-3D"></use></g><g data-mml-node="msubsup" transform="translate(1978.6, 0)"><g data-mml-node="mo"><use xlink:href="#MJX-1-TEX-LO-222B"></use></g><g data-mml-node="mi" transform="translate(1013.4, 1088.1) scale(0.707)"><use xlink:href="#MJX-1-TEX-I-1D44E"></use></g><g data-mml-node="mn" transform="translate(556, -896.4) scale(0.707)"><use xlink:href="#MJX-1-TEX-N-30"></use></g></g><g data-mml-node="mi" transform="translate(3582.7, 0)"><use xlink:href="#MJX-1-TEX-I-1D459"></use></g><g data-mml-node="mo" transform="translate(3880.7, 0)"><use xlink:href="#MJX-1-TEX-N-28"></use></g><g data-mml-node="mi" transform="translate(4269.7, 0)"><use xlink:href="#MJX-1-TEX-I-1D465"></use></g><g data-mml-node="mo" transform="translate(4841.7, 0)"><use xlink:href="#MJX-1-TEX-N-29"></use></g><g data-mml-node="mi" transform="translate(5230.7, 0)"><use xlink:href="#MJX-1-TEX-I-1D451"></use></g><g data-mml-node="mi" transform="translate(5750.7, 0)"><use xlink:href="#MJX-1-TEX-I-1D465"></use></g></g></g></svg>

甚至是：

<svg xmlns="http://www.w3.org/2000/svg" width="36.039ex" height="5.635ex" role="img" focusable="false" viewBox="0 -1578.8 15929.1 2490.7" xmlns:xlink="http://www.w3.org/1999/xlink" aria-hidden="true" style="vertical-align: -2.063ex;"><defs><path id="MJX-2-TEX-I-1D446" d="M308 24Q367 24 416 76T466 197Q466 260 414 284Q308 311 278 321T236 341Q176 383 176 462Q176 523 208 573T273 648Q302 673 343 688T407 704H418H425Q521 704 564 640Q565 640 577 653T603 682T623 704Q624 704 627 704T632 705Q645 705 645 698T617 577T585 459T569 456Q549 456 549 465Q549 471 550 475Q550 478 551 494T553 520Q553 554 544 579T526 616T501 641Q465 662 419 662Q362 662 313 616T263 510Q263 480 278 458T319 427Q323 425 389 408T456 390Q490 379 522 342T554 242Q554 216 546 186Q541 164 528 137T492 78T426 18T332 -20Q320 -22 298 -22Q199 -22 144 33L134 44L106 13Q83 -14 78 -18T65 -22Q52 -22 52 -14Q52 -11 110 221Q112 227 130 227H143Q149 221 149 216Q149 214 148 207T144 186T142 153Q144 114 160 87T203 47T255 29T308 24Z"></path><path id="MJX-2-TEX-N-3D" d="M56 347Q56 360 70 367H707Q722 359 722 347Q722 336 708 328L390 327H72Q56 332 56 347ZM56 153Q56 168 72 173H708Q722 163 722 153Q722 140 707 133H70Q56 140 56 153Z"></path><path id="MJX-2-TEX-LO-222C" d="M114 -798Q132 -824 165 -824H167Q195 -824 223 -764T275 -600T320 -391T362 -164Q365 -143 367 -133Q439 292 523 655T645 1127Q651 1145 655 1157T672 1201T699 1257T733 1306T777 1346T828 1360Q884 1360 912 1325T944 1245Q944 1220 932 1205T909 1186T887 1183Q866 1183 849 1198T832 1239Q832 1287 885 1296L882 1300Q879 1303 874 1307T866 1313Q851 1323 833 1323Q819 1323 807 1311T775 1255T736 1139T689 936T633 628Q574 293 510 -5T410 -437T355 -629Q278 -862 165 -862Q125 -862 92 -831T55 -746Q55 -711 74 -698T112 -685Q133 -685 150 -700T167 -741Q167 -789 114 -798ZM642 -798Q660 -824 693 -824H695Q723 -824 751 -764T803 -600T848 -391T890 -164Q893 -143 895 -133Q967 292 1051 655T1173 1127Q1179 1145 1183 1157T1200 1201T1227 1257T1261 1306T1305 1346T1356 1360Q1412 1360 1440 1325T1472 1245Q1472 1220 1460 1205T1437 1186T1415 1183Q1394 1183 1377 1198T1360 1239Q1360 1287 1413 1296L1410 1300Q1407 1303 1402 1307T1394 1313Q1379 1323 1361 1323Q1347 1323 1335 1311T1303 1255T1264 1139T1217 936T1161 628Q1102 293 1038 -5T938 -437T883 -629Q806 -862 693 -862Q653 -862 620 -831T583 -746Q583 -711 602 -698T640 -685Q661 -685 678 -700T695 -741Q695 -789 642 -798Z"></path><path id="MJX-2-TEX-I-1D453" d="M118 -162Q120 -162 124 -164T135 -167T147 -168Q160 -168 171 -155T187 -126Q197 -99 221 27T267 267T289 382V385H242Q195 385 192 387Q188 390 188 397L195 425Q197 430 203 430T250 431Q298 431 298 432Q298 434 307 482T319 540Q356 705 465 705Q502 703 526 683T550 630Q550 594 529 578T487 561Q443 561 443 603Q443 622 454 636T478 657L487 662Q471 668 457 668Q445 668 434 658T419 630Q412 601 403 552T387 469T380 433Q380 431 435 431Q480 431 487 430T498 424Q499 420 496 407T491 391Q489 386 482 386T428 385H372L349 263Q301 15 282 -47Q255 -132 212 -173Q175 -205 139 -205Q107 -205 81 -186T55 -132Q55 -95 76 -78T118 -61Q162 -61 162 -103Q162 -122 151 -136T127 -157L118 -162Z"></path><path id="MJX-2-TEX-N-28" d="M94 250Q94 319 104 381T127 488T164 576T202 643T244 695T277 729T302 750H315H319Q333 750 333 741Q333 738 316 720T275 667T226 581T184 443T167 250T184 58T225 -81T274 -167T316 -220T333 -241Q333 -250 318 -250H315H302L274 -226Q180 -141 137 -14T94 250Z"></path><path id="MJX-2-TEX-I-1D460" d="M131 289Q131 321 147 354T203 415T300 442Q362 442 390 415T419 355Q419 323 402 308T364 292Q351 292 340 300T328 326Q328 342 337 354T354 372T367 378Q368 378 368 379Q368 382 361 388T336 399T297 405Q249 405 227 379T204 326Q204 301 223 291T278 274T330 259Q396 230 396 163Q396 135 385 107T352 51T289 7T195 -10Q118 -10 86 19T53 87Q53 126 74 143T118 160Q133 160 146 151T160 120Q160 94 142 76T111 58Q109 57 108 57T107 55Q108 52 115 47T146 34T201 27Q237 27 263 38T301 66T318 97T323 122Q323 150 302 164T254 181T195 196T148 231Q131 256 131 289Z"></path><path id="MJX-2-TEX-N-29" d="M60 749L64 750Q69 750 74 750H86L114 726Q208 641 251 514T294 250Q294 182 284 119T261 12T224 -76T186 -143T145 -194T113 -227T90 -246Q87 -249 86 -250H74Q66 -250 63 -250T58 -247T55 -238Q56 -237 66 -225Q221 -64 221 250T66 725Q56 737 55 738Q55 746 60 749Z"></path><path id="MJX-2-TEX-I-1D451" d="M366 683Q367 683 438 688T511 694Q523 694 523 686Q523 679 450 384T375 83T374 68Q374 26 402 26Q411 27 422 35Q443 55 463 131Q469 151 473 152Q475 153 483 153H487H491Q506 153 506 145Q506 140 503 129Q490 79 473 48T445 8T417 -8Q409 -10 393 -10Q359 -10 336 5T306 36L300 51Q299 52 296 50Q294 48 292 46Q233 -10 172 -10Q117 -10 75 30T33 157Q33 205 53 255T101 341Q148 398 195 420T280 442Q336 442 364 400Q369 394 369 396Q370 400 396 505T424 616Q424 629 417 632T378 637H357Q351 643 351 645T353 664Q358 683 366 683ZM352 326Q329 405 277 405Q242 405 210 374T160 293Q131 214 119 129Q119 126 119 118T118 106Q118 61 136 44T179 26Q233 26 290 98L298 109L352 326Z"></path><path id="MJX-2-TEX-LO-222B" d="M114 -798Q132 -824 165 -824H167Q195 -824 223 -764T275 -600T320 -391T362 -164Q365 -143 367 -133Q439 292 523 655T645 1127Q651 1145 655 1157T672 1201T699 1257T733 1306T777 1346T828 1360Q884 1360 912 1325T944 1245Q944 1220 932 1205T909 1186T887 1183Q866 1183 849 1198T832 1239Q832 1287 885 1296L882 1300Q879 1303 874 1307T866 1313Q851 1323 833 1323Q819 1323 807 1311T775 1255T736 1139T689 936T633 628Q574 293 510 -5T410 -437T355 -629Q278 -862 165 -862Q125 -862 92 -831T55 -746Q55 -711 74 -698T112 -685Q133 -685 150 -700T167 -741Q167 -789 114 -798Z"></path><path id="MJX-2-TEX-I-1D44E" d="M33 157Q33 258 109 349T280 441Q331 441 370 392Q386 422 416 422Q429 422 439 414T449 394Q449 381 412 234T374 68Q374 43 381 35T402 26Q411 27 422 35Q443 55 463 131Q469 151 473 152Q475 153 483 153H487Q506 153 506 144Q506 138 501 117T481 63T449 13Q436 0 417 -8Q409 -10 393 -10Q359 -10 336 5T306 36L300 51Q299 52 296 50Q294 48 292 46Q233 -10 172 -10Q117 -10 75 30T33 157ZM351 328Q351 334 346 350T323 385T277 405Q242 405 210 374T160 293Q131 214 119 129Q119 126 119 118T118 106Q118 61 136 44T179 26Q217 26 254 59T298 110Q300 114 325 217T351 328Z"></path><path id="MJX-2-TEX-N-30" d="M96 585Q152 666 249 666Q297 666 345 640T423 548Q460 465 460 320Q460 165 417 83Q397 41 362 16T301 -15T250 -22Q224 -22 198 -16T137 16T82 83Q39 165 39 320Q39 494 96 585ZM321 597Q291 629 250 629Q208 629 178 597Q153 571 145 525T137 333Q137 175 145 125T181 46Q209 16 250 16Q290 16 318 46Q347 76 354 130T362 333Q362 478 354 524T321 597Z"></path><path id="MJX-2-TEX-I-1D44F" d="M73 647Q73 657 77 670T89 683Q90 683 161 688T234 694Q246 694 246 685T212 542Q204 508 195 472T180 418L176 399Q176 396 182 402Q231 442 283 442Q345 442 383 396T422 280Q422 169 343 79T173 -11Q123 -11 82 27T40 150V159Q40 180 48 217T97 414Q147 611 147 623T109 637Q104 637 101 637H96Q86 637 83 637T76 640T73 647ZM336 325V331Q336 405 275 405Q258 405 240 397T207 376T181 352T163 330L157 322L136 236Q114 150 114 114Q114 66 138 42Q154 26 178 26Q211 26 245 58Q270 81 285 114T318 219Q336 291 336 325Z"></path><path id="MJX-2-TEX-I-1D465" d="M52 289Q59 331 106 386T222 442Q257 442 286 424T329 379Q371 442 430 442Q467 442 494 420T522 361Q522 332 508 314T481 292T458 288Q439 288 427 299T415 328Q415 374 465 391Q454 404 425 404Q412 404 406 402Q368 386 350 336Q290 115 290 78Q290 50 306 38T341 26Q378 26 414 59T463 140Q466 150 469 151T485 153H489Q504 153 504 145Q504 144 502 134Q486 77 440 33T333 -11Q263 -11 227 52Q186 -10 133 -10H127Q78 -10 57 16T35 71Q35 103 54 123T99 143Q142 143 142 101Q142 81 130 66T107 46T94 41L91 40Q91 39 97 36T113 29T132 26Q168 26 194 71Q203 87 217 139T245 247T261 313Q266 340 266 352Q266 380 251 392T217 404Q177 404 142 372T93 290Q91 281 88 280T72 278H58Q52 284 52 289Z"></path><path id="MJX-2-TEX-N-2C" d="M78 35T78 60T94 103T137 121Q165 121 187 96T210 8Q210 -27 201 -60T180 -117T154 -158T130 -185T117 -194Q113 -194 104 -185T95 -172Q95 -168 106 -156T131 -126T157 -76T173 -3V9L172 8Q170 7 167 6T161 3T152 1T140 0Q113 0 96 17Z"></path><path id="MJX-2-TEX-I-1D466" d="M21 287Q21 301 36 335T84 406T158 442Q199 442 224 419T250 355Q248 336 247 334Q247 331 231 288T198 191T182 105Q182 62 196 45T238 27Q261 27 281 38T312 61T339 94Q339 95 344 114T358 173T377 247Q415 397 419 404Q432 431 462 431Q475 431 483 424T494 412T496 403Q496 390 447 193T391 -23Q363 -106 294 -155T156 -205Q111 -205 77 -183T43 -117Q43 -95 50 -80T69 -58T89 -48T106 -45Q150 -45 150 -87Q150 -107 138 -122T115 -142T102 -147L99 -148Q101 -153 118 -160T152 -167H160Q177 -167 186 -165Q219 -156 247 -127T290 -65T313 -9T321 21L315 17Q309 13 296 6T270 -6Q250 -11 231 -11Q185 -11 150 11T104 82Q103 89 103 113Q103 170 138 262T173 379Q173 380 173 381Q173 390 173 393T169 400T158 404H154Q131 404 112 385T82 344T65 302T57 280Q55 278 41 278H27Q21 284 21 287Z"></path></defs><g stroke="currentColor" fill="currentColor" stroke-width="0" transform="matrix(1 0 0 -1 0 0)"><g data-mml-node="math"><g data-mml-node="mi"><use xlink:href="#MJX-2-TEX-I-1D446"></use></g><g data-mml-node="mo" transform="translate(922.8, 0)"><use xlink:href="#MJX-2-TEX-N-3D"></use></g><g data-mml-node="msub" transform="translate(1978.6, 0)"><g data-mml-node="mo"><use xlink:href="#MJX-2-TEX-LO-222C"></use></g><g data-mml-node="mi" transform="translate(1084, -896.4) scale(0.707)"><use xlink:href="#MJX-2-TEX-I-1D446"></use></g></g><g data-mml-node="mi" transform="translate(3735.3, 0)"><use xlink:href="#MJX-2-TEX-I-1D453"></use></g><g data-mml-node="mo" transform="translate(4285.3, 0)"><use xlink:href="#MJX-2-TEX-N-28"></use></g><g data-mml-node="mi" transform="translate(4674.3, 0)"><use xlink:href="#MJX-2-TEX-I-1D460"></use></g><g data-mml-node="mo" transform="translate(5143.3, 0)"><use xlink:href="#MJX-2-TEX-N-29"></use></g><g data-mml-node="mi" transform="translate(5532.3, 0)"><use xlink:href="#MJX-2-TEX-I-1D451"></use></g><g data-mml-node="mi" transform="translate(6052.3, 0)"><use xlink:href="#MJX-2-TEX-I-1D460"></use></g><g data-mml-node="mo" transform="translate(6799.1, 0)"><use xlink:href="#MJX-2-TEX-N-3D"></use></g><g data-mml-node="msubsup" transform="translate(7854.9, 0)"><g data-mml-node="mo"><use xlink:href="#MJX-2-TEX-LO-222B"></use></g><g data-mml-node="mi" transform="translate(1013.4, 1088.1) scale(0.707)"><use xlink:href="#MJX-2-TEX-I-1D44E"></use></g><g data-mml-node="mn" transform="translate(556, -896.4) scale(0.707)"><use xlink:href="#MJX-2-TEX-N-30"></use></g></g><g data-mml-node="msubsup" transform="translate(9459, 0)"><g data-mml-node="mo"><use xlink:href="#MJX-2-TEX-LO-222B"></use></g><g data-mml-node="mi" transform="translate(1013.4, 1088.1) scale(0.707)"><use xlink:href="#MJX-2-TEX-I-1D44F"></use></g><g data-mml-node="mn" transform="translate(556, -896.4) scale(0.707)"><use xlink:href="#MJX-2-TEX-N-30"></use></g></g><g data-mml-node="mi" transform="translate(10992.4, 0)"><use xlink:href="#MJX-2-TEX-I-1D453"></use></g><g data-mml-node="mo" transform="translate(11542.4, 0)"><use xlink:href="#MJX-2-TEX-N-28"></use></g><g data-mml-node="mi" transform="translate(11931.4, 0)"><use xlink:href="#MJX-2-TEX-I-1D465"></use></g><g data-mml-node="mo" transform="translate(12503.4, 0)"><use xlink:href="#MJX-2-TEX-N-2C"></use></g><g data-mml-node="mi" transform="translate(12948.1, 0)"><use xlink:href="#MJX-2-TEX-I-1D466"></use></g><g data-mml-node="mo" transform="translate(13438.1, 0)"><use xlink:href="#MJX-2-TEX-N-29"></use></g><g data-mml-node="mi" transform="translate(13827.1, 0)"><use xlink:href="#MJX-2-TEX-I-1D451"></use></g><g data-mml-node="mi" transform="translate(14347.1, 0)"><use xlink:href="#MJX-2-TEX-I-1D465"></use></g><g data-mml-node="mi" transform="translate(14919.1, 0)"><use xlink:href="#MJX-2-TEX-I-1D451"></use></g><g data-mml-node="mi" transform="translate(15439.1, 0)"><use xlink:href="#MJX-2-TEX-I-1D466"></use></g></g></g></svg>

那就真的是把简单问题复杂化了，不要较真，去追求这种「数学味道」。

相比自然学科，C++的这种「工具性」还要更强一点，我们千万不要为了研究而研究，为了让代码更像C++而放弃真正更高效更简洁的写法，就像继承多态可以很简洁方便地解决的问题，咱们就没必要硬给他搞成模板了吧。

最合适的才是最好用的，我们做理论研究的时候自然是要把这些学会、学精，但真的在生产实践的时候，还是应当选择最适合的。

#### Q5：C++20中的concept跟模板的关系是什么？

C++20标准引入的「concept」概念，也属于模板的一种，或者说是对C++17及以前的模板元编程的一次拨乱反正，大幅提高了模板的可读性和可测试性，但它归根结底仍然属于模板的一种，所以从「实例化」「编译期行为」等角度来说，concept都是符合模板的定义的，因此也具有模板的所有性质。

对concept感兴趣的读者可以参考[C++20之concept用法详解](https://km.woa.com/articles/show/572829)。

#### Q6：STL容器为什么不支持存入引用？

这个问题其实很好解释，如果我们自己来写一些最简的容器：

```cpp
template <typename T, size_t N>
class Array {
 private:
  T data[N];
};

template <typename T>
class Vector {
 public:
  Vector(size_t n) : data(new T[n]) {}
 private:
  T *data;
};
```

我们看看，如果`T`是引用的话，能编译通过吗？

```cpp
// 假如T是int &的时候
class Array<int &, 5> {
 private:
  int &data[5]; // 显然编译不通过
};

class Vector<int &> {
 public:
  Vector(size_t n) : data(new int &[n]) {} // 编译不通过
 private:
  int &*data; // 编译不通过
};
```

所以理由很简单，就是实例化引用的时候，编译不过。

那为什么不针对引用类型，给他特化成对应的指针类型呢？

```cpp
template <typename T>
class Vector<T &> { // 针对引用类型进行特化
 public:
  Vector(size_t n) : data(new T *[n]), // 这里转换指针类型
                     size(n) {} 
  void push_back(T &ele) {
    data[size++] = &ele; // 引用都转换为指针
  }

 private:
  T *data; // 成员还用指针 
  size_t size;
};
```

看起来上面这样操作很完美，把引用类型转为了指针的语法糖。但它其实存在一个很严重的问题，就是自动类型推导：

```cpp
void Demo() {
  int a = 5;
  Vector ve{a}; // 请问这里是推Vector<int>还是Vector<int &>类型？
}
```

照理说，`a`在此是个左值，所以应该推引用类型才对，但这么做大多数情况都是反直觉的，所以在各种隐式推导和转换的时候会出问题。（其实在内存管理上也存在问题，比如说`pop_back`操作时不会析构，因为转换为指针了，所以并不负责引用对象的生命周期，也可能会出现潜在的问题。）

所以，在STL中规定，容器存储的是「对象」，变量、指针都可以视为「对象」，但引用并不是，所以不允许存储，除非我们用「引用对象」，也就是`std::reference_wrapper`来封装成对象才能存入容器。
