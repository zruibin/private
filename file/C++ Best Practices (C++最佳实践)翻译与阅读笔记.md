 
<!--BEGIN_DATA
{
    "create_date": "2022-01-04 23:20", 
    "modify_date": "2022-01-04 23:20", 
    "is_top": "0", 
    "summary": "C++ Best Practices (C++最佳实践)翻译与阅读笔记", 
    "tags": "C/C++", 
    "file_name": "C++ Best Practices (C++最佳实践)翻译与阅读笔记.md"
}
END_DATA-->

#### <p>原文出处：<a href='https://zhuanlan.zhihu.com/p/427778091' target='blank'>C++ Best Practices (C++最佳实践)翻译与阅读笔记</a></p>

> 这本书的副标题是： 45ish Simple Rules with Specific Action items for better C++,这本书是由公司大佬推荐的， 个人认为有必要掌握一下这45条最佳实践， 可以很大程度上提升代码的可读性和健壮性， 而且这本书也不长，翻译起来也会比较简单，比很多人推荐的Effective C++ 要容易读的多， 抽了一个十一的尾巴就翻译完了，`easy~`翻译的过程中去掉了欧美人写书时喜欢带上的口水话，从而让文章更加精炼。 ++我翻译的时候会带上一些自己的理解，这部分我用下划线标出来了， 注意区分++。
> 原书的链接位置在: [https://pan.baidu.com/s/1Z-tAHHXV5rxCqpWTRM5ZFA](https://link.zhihu.com/?target=https%3A//pan.baidu.com/s/1Z-tAHHXV5rxCqpWTRM5ZFA) 提取码: bgtc  

## 1. 导读

我以一个训练者的目标希望各位能够：

  1. 学习如何自己做实验；
  2. 不要仅仅信我说的话，要亲手实验；
  3. 学习到这门语言是如何工作的；
  4. 在下轮写代码的时候避免犯错；

## 2. 有关"最佳实践"

最佳实践实际上就是说： 1. 减少常见的错误； 2. 能够更快定位错误 3. 提升运行性能

**为什么要最佳实践？** _因为你的项目并不是一个特殊的项目_

如果你或者你同事在用C++编程，他们往往是在乎性能的，否则他们会用一些其它的语言。
我经常去一些公司他们都告诉我他们的项目是特殊的，因为他们想要快速完成功能。

警告： 他们都在出于相同的原因做着相同的决定。很少有例外， 例外者其实都是那些已经遵循这本书的组织。

## 3.使用工具： 自动测试

你需要一个单独的指令去跑所有的测试，如果你没有自动测试， 没有人会跑这些测试的：

  1. Catch2
  2. DocTest 
  3. GoogleTest
  4. Boost.Test

Ctest 是一个Cmake下用来测试的runner， 它可以很好地利用 Cmake的 `add_test` 特性。你需要很熟悉测试工具、搞清楚他们是怎么做的、并且从他们中选择一个。

没有自动化的测试， 这本书的其它部分就是没有意义的，在重构代码的时候，如果你不能验证你没有破坏现有的代码， 你就不能使用这些最佳实践。

Oleg Rabaev 说过：

==如果一个部分是很难测试的， 那它肯定没被设计好。 如果一个组成部分是容易测试的，那就意味它是有被很好的设计的。反过来说，一个好的设计，应该是一个容易被测试的设计。==

## 4.使用工具： 持续构建

没有自动化的测试， 那就很难去保证代码的质量。 在我生涯中的一些C++ 项目中，我的C++项目支持各种操作系统、各架构的组合。当你开始在不同平台、架构上组合不同的编译器的时候， 那就很有可能出现在一个平台能够使用在另外一个平台上不能使用的情况。为了解决这个问题，使用带有持续测试的持续构建工具吧。

  1. 测试你将支持的所有平台的组合。
  2. 将debug和最终发布分离
  3. 测试所有的配置项。
  4. 测试所有你需要支持的编译器

## 5.使用工具： 编译器警告

有许多警告你也许都没有在使用， 大多数警告实际上都是有好处的。 -Wall 并不是GCC和Clang提供的所有warning, `-Wextra`仍然只是warning中的冰山一角。

强烈考虑使用 `-Wpedantic(GCC/Clang)` 以及 `/permissive(msvc)` ,这些编译选项能够进制语言拓展项，并且让你更加接近于C++ 标准， 你今天开启越多的warning, 你以后就越容易迁移到其它平台。

## 6.使用工具： 静态分析

静态分析工具可以在不编译和运行你的代码的情况下来分析你的代码， 你的编译器实际上就是这么一个工具并且是你的第一道代码质量防线。许多这种工具都是免费的并且是开源的， CPPCheck 和clang-tidy是两种流行并且免费的工具， 大多数IDE和编辑器都能够支持。

## 7.使用工具： sanitizers

sanitizers是集成在gcc clang msvc下的一种运行时分析工具。如果你比较熟悉Valgrind, sanitizers提供了相似的功能但快了好几个数量级。

Address sanitizer, UB Sanitizer, Thread sanitizer 可以找到很多像魔法一样的问题，在写这本书的时候，msvc正在支持越来越多的sanitizer, gcc和clang 拥有更多对sanitizer的支持。

John Reghr 推荐在开发的时候永远开启ASan( Address Sanitizer) 和UBSan(Undefined Behaviour Sanitizer) 。

当类似于内存溢出的错误发生时， sanitizer 将会给你一个报告告诉你什么情况下会导致程序失败， 通常还会给出修复问题的建议。

你可以用如下的命令开启ASan 和UBSan:

    gcc -fsanitize=address,undefined <filetocompile>

## 8.慢下来

在C++中，一个问题往往有很多解决方案， 对于哪种方案是最优的有若干个观点存在。 从被人的项目里面复制粘贴代码是非常容易的，使用你觉得最满意的的方案去解决问题也是非常容易的（但这两种都是要避免的）， 要注意了：

如果解决方案似乎很复杂很大，停下。 这时候是一个很好的时间去走走然后好好思考这个方案。 当你结束了散步， 把你的设计方案和同事讨论一下，或者用橡皮鸭思考方法讲出来（++所谓橡皮鸭方法就是你对着一个橡皮鸭一五一十地说出你的思考过程和逻辑，从中可以察觉到自己的思维漏洞等++）如果你还没有发现一个直接的解决方法？去twitter上面问问吧。最关键的其实是不要盲目地去用你自己觉得满意的方案去解决问题， 要多停一段时间多思考。随着年龄的增长，我花在编程的时间越来越少，但是思考的时间却越来越多， 最后我实现解决方案的速度比以前越来越快，并且越来越简单。

## 9.C++ 不是魔法

这部分只是提醒你我们可以对C++的各个方面进行推理， 它并不是一个黑盒，也并不是一个魔法。

如果你有问题， 你通常可以很简单地去写个实验代码，它将自己回答你的这些问题。

## 10.C++ 不是纯面向对象的语言

Bjarne Stroustrup 在"The C++ Programming Language" 的第三版里面讲到：

==C++ 是一个通用的编程语言但是偏向于系统编程， 它比C更好， 支持数据抽象， 支持面向对象， 支持泛型编程 。==

你必须明白C++ 是一种多科目语言， 它很好的支持了当下的所有编程范式：

  * 过程式
  * 函数式
  * 面向对象
  * 泛型编程
  * 运行时编程（constexpr 以及模板元变成） 理解什么时候去用这些工具是写好C++的关键， 那些只执着用某一个编程范式的项目往往会错过这个语言的最佳特性。

## 11.学习一门其他语言

考虑到C++并不是一个纯面向对象的语言， 你必须掌握一些其它技术才能更好地使用C++，最好学会一门函数式语言比如Haskell.

## 12.const/constexpr 修饰一切常量

许多大佬说过这很多次了， 让一个对象修饰为`const` 有两个好处：

它迫使我们去思考这个对象的的初始化和生命周期， 这会影响程序的性能。 可以向代码的读者传达这是一个常量的意义
另外，如果它是一个static对象，编译器现在可以自由地将它移到内存的常量区，这可能会影响优化器的行为。

## 13.constexpr 修饰一切在编译阶段就已知的值

使用`## define`的日子早就一去不复返了， `constexpr`应该成为你新的默认选择。 很不幸的是，
人们总是过份高估constexpr的复杂程度， 所以就让我们把它拆解成最简单的东西说起吧~

如果你看到像这样的一些东西：

```cpp
在编译时期，数据就已经知道是static const 对象了： 
static const std::vector<int> angles{-90,-45,0,45,90}
```

那这种情况就需要把它变成：

```cpp
static constexpr std::array<int,5> angles{-90,-45,0,45,90}
```

`static constexpr` 在这里可以保证对象不会在每次这个函数/声明遇到时都会重新初始化。 由于static修饰了这个变量，它将存在于整个程序的生命周期， 而且我们知道它不会被初始化两次。

这两个代码的区别有三：

  1. 这个array的大小我们是能够在编译时期知道的
  2. 我们溢出了数组大小动态分配
  3. 我们不需要再对访问static 对象付出额外代价（++这点我没明白啥意思，原文是 We no longer pay the cost of accessing a static++) 主要收益来源于前两点。

## 14.在大多数情况下使用auto来自动推断类型

我其实并不是一个永远使用auto的人， 但是让我来问你一个问题： std::count 函数返回的类型是什么？

我的回答是： 我不在乎。

```cpp
const auto result = std::count( /* stuff */ );
````

使用auto 避免没有必要的转换和数据丢失， 同样的场景经常在range-for 循环中出现，再举个栗子：

```cpp
有可能发生代价很高的转换
const std::string value = get_string_value();
```

`get_string_value()`的返回类型是什么？ 如果它是一个`std::string_view`或者是一个`const char *`, 我们将会有一个潜在的高代价的类型转化。

```cpp
不可能有高代价的性能转化的写法：
// 避免类型转化
const auto value = get_string_value();
```

另外， auto作为返回值实际上可以大幅度简化泛型代码：

```cpp
// C++98 template usage
template<typename Arithmetic>
Arithmetic divide(Arithmetic numerator, Arithmetic denominator) {
                    return numerator / denominator;
}
```

这个代码强制我们分子的类型和分母的类型都是同一种类型，非常难受。 但在C++98 里面怎么实现分子分母不同类型呢？

```cpp
template<typename Numerator, typename Denominator>
/*what's the return type*/
divide(Numerator numerator, Denominator denominator) {
                    return numerator / denominator;
}
```

可以看到，我们没有办法提供返回值的类型， C++98没有提供这种问题的解决方法，但是C++11通过尾置返回类型可以做到：

```cpp
// use trailing return type
template<typename Numerator, typename Denominator>
auto divide(Numerator numerator, Denominator denominator)
 -> decltype(numerator / denominator)
{
                    return numerator / denominator;
}
```

但是在C+14里面， 我们还可以把返回类型给省去，

```cpp
// use trailing return type
template<typename Numerator, typename Denominator>
auto divide(Numerator numerator, Denominator denominator){
    return numerator / denominator;
}
```

## 15.使用ranged-for循环而不是老的循环方法

我会用几个例子来说明这一点：

当循环时， `int`和 `std::size_t` 的问题

```cpp
for (int i = 0; i < container.size(); ++i) {
    // 糟糕，i 实际上不是int类型，是size_t类型，有类型不一致的问题
}
```

当循环时， 容器类型不一致的问题：

```cpp
for (auto itr = container.begin();itr != container2.end();++itr) {
    // 哦，我们大多数人都有过这种经历
}
```  

使用ranged-for的例子

```cpp
for (const auto &element : container) {
    // 消除了以上的两种问题
}
```

**注意： 永远不要在用ranged-for的时候修改容器自身**

## 16.使用ranged-for时配合auto使用

不使用auto会让你更容易不经意间犯一些错误：

意外的类型转换：

```cpp
for (const int value : container_of_double){
    // 意外的转换，很有可能会报warning
}
```

意外的继承切片问题

```cpp
for (const Base value : container_of_Derived){
    // 意外的发生了继承切片问题
}
```

正确做法

```cpp
for (const auto &value : container){
    // 不会发生意外的问题
}
```

优先考虑：

  1. 对于内部元素不可变类型的循环时选择 const auto &
  2. 对于内部元素可变类型的循环时选择 auto &
  3. auto && 当且仅当你需要一些奇怪的类型比如std::vector 时， 或者将元素移出容器时（++这个地方没懂， 原文： auto && only when you have to work with weird types like std::vector, or if moving elements out of the container++）

## 17.使用算法而不是循环

算法能够传达更多的含义并且能够符合”const 一切" 的思想， 在C++20 中， 我们有ranges, 这会使得算法用起来更加舒服。

使用函数的方式并且配合使用算法， 这会使C++ 的代码读起来更想是一个句子。

比如，检查一个container内是否有一个大于12的数：

```cpp
const auto has_value = std::any_of(begin(container), end(container), greater_than(12));
```

在极少数情况，编译器的静态分析工具可以能够提示你有现有的算法能够使用。

## 18.不要害怕使用模板

模板能够表现 C++ 中的DRY原则（Dont repeat yourself) ， 模板它可能是复杂的，令人生畏的， 并且是图灵完备的，但是它们也不必如此。 15年前， 业界似乎有一个盛行的态度是：“模板就不是给正常人写的"。

幸运的是， 这种观点放在今天越来越不正确了， 现在我们用更多的工具： concepts, generic lanbdas 等等。

我们将在接下来写一个简单的例子。假设我们想要写一个函数它可以除任意两个值：

```cpp
// 除两个double 类型的数
double divide(double numerator, double denominator){
    return numerator / denominator;
}

// 你不希望分子的类型被提升到double类型：
float divide ( float numerator, float denominator){
    return numerator / denominator;
}

// 当然，你还想两个int类型的相除
int divide ( int numerator, int denominator){
    return numerator / denominator;
}

// template 就是为了这种情况而设计的：
// 最基础的template 
template<typename T>
T divide(T numerator, T denominator){
    return numerator / denominator;
}

// 大多数的例子都用T来表示， 就像我刚才做的那样，但是不要这么做，给你的类型一个有意义的名字：
template<typename Arithmetic>
Arithmetic divide(Arithmetic numerator, Arithmetic denominator){
    return numerator / denominator;
}
```

## 19.不要copy paste代码

如果你发现自己正在选中一块代码并且复制它， 停下！

后退一步并且再看下这些代码：

  1. 为什么你要复制它？
  2. 这个代码和你的目标代码有多少相似？
  3. 构造一个函数有意义吗？
  4. 记住， 不要害怕使用模板！

我发现这个简单的条例可以对我的代码质量有着最直接的影响， 如果我们即将在当前的函数中进行粘贴一段代码， 那就考虑使用lambda 。C++14的lambda 配合上泛型参数（也叫auto），可以让你更加容易写出可复用的代码还不要处理template 语法。

## 20.遵循“零法则"

在正确的情况下，没有析构函数总是更好的。 空的析构函数会损失一部分性能，并且：

  1. 它会让类型不再简单；
  2. 没有函数用途；
  3. 会影响内联的析构；
  4. 不经意间禁止了移动操作。 如果你提供了一个自定义的删除行为， std::unique_ptr 可以帮助你遵循0法则

## 21.如果你一定手动管理资源， 遵循“五法则”

如果你需要提供一个自定义的析构函数，那你必须同时对其它特殊成员函数进行 =delete, =default,或者实现它们。这个规则一开始叫“三法则”，在C++11后变成了“五法则”

```cpp
// 特殊的成员函数
struct S {
    S(); // default constructor
        // does not affect other special member functions

    // If you define any of the following, you must deal with
    // all the others.

    S(const S &); // 拷贝构造

    S(S&&);     // 移动构造 

    S &operator=(const S &); // 拷贝赋值

    S &operator=(S &&); //  移动赋值 
};
```

当你不知道怎么去处理它们的时候，`=delete` 对于这些特殊的成员函数来说是一个非常安全的处理方法.

当你在声明带有虚函数的基类时，你也应该遵循”五法则“：

```cpp
struct Base {
    virtual void do_stuff();
    // because of the virtual function we know this class
    // is intended for polymorphic use, therefore our

    // tools will tell us to define a virtual destructor
    virtual ~Base() = default;
    // and now we need to declare the other special members
    // a good safe bet is to delete them, because properly and safely
     // copying or assigning an object via a reference or pointer
     // to a base class is hard / impossible

    S(S&&) = delete;
    S(const &S) = delete;
    S &operator=(const S &) = delete;
    S &operator=(S &&) = delete;
};

struct Derived : Base {
// We don't need to define any of the special members
// here, they are all inherited from `Base`.    
}
```

## 22.不要调用未定义的行为（UB行为）

现在我们知道有很多未定义的行为是很难追踪的， 在接下来的几节中我将给出一些例子。最重要的事情是你需要理解，未定义行为的存在会破坏你整个程序。

> 一个符合规范的实现在运行一个格式良好的程序时，应该产生可以观测的行为，相同的程序和相同的输入应该产生与之相对应的行为。  

但是， 如果一个程序中包含着一个未定义的行为， 这段代码对执行输入的程序也就没有要求。（甚至对第一个未定义操作之前的操作也没有要求）

如果你有未定义的行为， 整个程序的执行就会变得很诡异。

## 23.不要判断this 为nullptr，这是UB行为

```cpp
int Class::member() {
    if (this == nullptr) {
        // removed by the compiler, it would be UB
        // if this were ever null
        return 42;
    } else {
        return 0;
    }
}
```

严格意义上说，这并不是对未定义行为的校验。但是这个校验不可能会失败， 如果this等于`nullptr`,那你将会处于一个UB行为的状态中。人们过去经常经常这么做，但这永远是一个UB行为。 你不能从一个对象的生命周期以外去访问一个对象。 从理论上来说，this=null的唯一可能就是你在调用一个null对象的成员。

## 24.不要判断对象的引用是nullptr，这是UB行为

```cpp
int get_value(int &thing) {
    if (&thing == nullptr) {
        // removed by compiler
        return 42;
    } else {
        return thing;
    }
}
```

不要尝试它，这是一个UB行为， 永远认为引用所指向的是一个存在的对象， 在你设计API时可以合理使用这一点。

## 25.避免在switch语句中使用default

这个问题可以用以下一系列的例子来阐明， 从这个开始：

```cpp
enum class Values {
    val1,
    val2
};

std::string_view get_name(Values value) {
    switch (value) {
        case val1: return "val1";
        case val2: return "val2";
    }
}
```

如果你开启了所有`warning`， 你将会得到一个"not all code paths return a value" 的警告，这从技术上说是正确的。

我们可以调用 `get_name(static_cast<Values>(15))` ， 这并不违法任何C++的规定，但函数不返回任何值这一点是个UB行为。

你可以尝试这样修复代码：

```cpp
enum class Values {
    val1,
    val2
};

std::string_view get_name(Values value) {
    switch (value) {
        case val1: return "val1";
        case val2: return "val2";
        default: return "unknown";
    }
}
```

但是呢这样会引入一个新的问题：

```cpp
enum class Values {
    val1,
    val2，
    val3, // 这里增加一个值
};

std::string_view get_name(Values value) {
    switch (value) {
        case val1: return "val1";
        case val2: return "val2";
        default: return "unknown";
    }
    // 编译器不会诊断出来val3没有处理
}
```

实际上，我们更倾向于这样的代码：

```cpp
enum class Values {
    val1,
    val2，
    val3, // 这里增加一个值
};

std::string_view get_name(Values value) {
    switch (value) {
        case val1: return "val1";
        case val2: return "val2";
    }  // 没有处理的enum 值这里会有warning
    return "unknown" 
}
```

## 26. 使用带作用域的枚举值

C++11 引入了带作用域的枚举值， 目的是为了解决很多从C继承过来的问题。

```cpp
C++98 enums
enum Choices {
    option1 // value in the global scope
};

enum OtherChoices {
    option2
};

int main() {
    int val = option1;
    val = option2; // no warning
}
```

`enum Choices` 和`OtherChoices`它们俩很容易被搞混， 并且它们引入了全局命名空间下的标识符。

  * enum class Choices;
  * enum class OtherChoices;

在这些枚举类中的值都是带有限定作用域的，并且更加强类型。

```cpp
C++11 scoped enumeration
enum class Choices {
    option1
};

enum class OtherChoices {
    option2
};

int main() {
    int val = option1;
    int val2 = Choices::option1;
    Choices val = Choices::option1;
    val = OtherChoices::option2;
}
```

这个带enum class的版本没有花太多功夫就可以让它们不那么容易被搞混， 并且它们的标识符现在是带作用域的，并不是全局的。

`enum Struct`和 `enum class` 其实是等价的，只是逻辑上enum struct更加合理， 因为它的成员是public公开的。

## 27. 使用if constexpr 而不是SFINAE(Substituion Failure Is Not An Error)

SFINAE是一种很难读懂的代码（++不懂SFINAE的参考知乎的这个文章[文章](https://zhuanlan.zhihu.com/p/21314708)） ，if constexpr 没有SFINAE那么灵活，但是当你能用它的时候就尽量用它.

我们来看一下之前在_Prefer auto in Many Cases_的文章中举的相除的例子：

```cpp
template<typename Numerator, typename Denominator>
auto divide(Numerator numerator, Denominator denominator)
{
    return numerator / denominator;
}
```  

好， 那当我们要做整数相除的时候， 我们现在想要加一个不同的行为该怎么做呢？ 在C++17以前， 我们会使用SFINAE("Substitution Failure is not An Error") 这个特性。 基本意思就是说， 如果一个函数无法编译， 那它就会从重载解析中删除。 举个例子：

_SFINAE 版本的删除_

```cpp
#include <stdexcept>
#include <type_traits>
#include <utility>

template <typename Numerator, typename Denominator,
        std::enable_if_t<std::is_integral_v<Numerator> &&
        std::is_integral_v<Denominator>,int> = 0>
auto divide(Numerator numerator, Denominator denominator) {
    // is integer division
    if (denominator == 0) {
        throw std::runtime_error("divide by 0!");
    }
    return numerator / denominator;
}

template <typename Numerator, typename Denominator,
std::enable_if_t<std::is_floating_point_v<Numerator> ||
                std::is_floating_point_v<Denominator>,
                int> = 0>
auto divide(Numerator numerator, Denominator denominator) {
    // is floating point division
    return numerator / denominator;
}
```

C++17 的 if constexpr 语法可以简化这个代码：

```cpp
#include <stdexcept>
#include <type_traits>
#include <utility>

template <typename Numerator, typename Denominator>
auto divide(Numerator numerator, Denominator denominator) {
if constexpr (std::is_integral_v<Numerator> && std::is_integral_v<Denominator>) {
    // is integral division
    if (denominator == 0) {
        throw std::runtime_error("divide by 0!");
    }
}
   return numerator / denominator;
}
```

注意，if constexpr块中的代码在语法上仍然必须是正确的. if constexpr 跟#define是不一样的。

## 28. 用Concepts约束你的模板参数（C++20)

Concepts比起SFINAE会给你带来更好的报错信息以及更快的编译时间， 另外还会比SFINAE有更好的可读性。我们继续构建我们上一章的例子 ，这是上一章用if constexpr 写出来的代码：

```cpp
#include <stdexcept>
#include <type_traits>
#include <utility>

template <typename Numerator, typename Denominator>
auto divide(Numerator numerator, Denominator denominator) {
if constexpr (std::is_integral_v<Numerator> && std::is_integral_v<Denominator>) {
    // is integral division
    if (denominator == 0) {
        throw std::runtime_error("divide by 0!");
    }
}
   return numerator / denominator;
}
```

用concept我们可以把它分解成两个不同的函数。Concepts可以在许多不同的场景下使用， 这个版本在函数声明以后用了一个简单的requires从句：

```cpp
#include <stdexcept>
#include <type_traits>
#include <utility>

// overload resolution will pick the most specific version
template <typename Numerator, typename Denominator>
auto divide(Numerator numerator, Denominator denominator) requires
    (std::is_integral_v<Numerator>&& std::is_integral_v<Denominator>) {
    // is integral division
    if (denominator == 0) {
        throw std::runtime_error("divide by 0!");
    }
    return numerator / denominator;
}

template <typename Numerator, typename Denominator>
auto divide(Numerator numerator, Denominator denominator) {
    return numerator / denominator;
}
```  

这个版本用了concepts作函数参数， C++20 甚至还有“auto concept" , 这是个隐式模板函数。

```cpp
#include <stdexcept>
#include <concepts>

auto divide(std::integral auto numerator,
            std::integral auto denominator) {
    // is integer division
    if (denominator == 0) {
        throw std::runtime_error("divide by 0!");
    }
    return numerator / denominator;
}

auto divide(auto numerator, auto denominator){
    return numerator / denominator;
}
```

## 29. 将你的泛型代码去模板化

尽可能地将代码移出模板之外， 使用其它函数或者使用基类都可以，编译器仍然可以内联它们。（并不是不用模板，而是模板内的代码尽可能移出去）

去模板化可以提高编译速度并且减少二进制文件的大小，二者都很有用。 它还可以消除模板膨胀。

每次函数模板实例化时都会生成一个新lambda函数

```cpp
template<typename T>
void do_things()
{
    // this lambda must be generated for each
    // template instantiation
    // 这个lambda函数在每个模板实例化的时候都会被生成一次
    auto lambda = [](){ /* some lambda that doesn't capture */ };
    auto value = lambda();
}
```

与之相对应的是

```cpp
auto some_function(){ /* do things */ 

template<typename T>
void do_things()
{
    auto value = some_function();
}
```  

现在只编译了一个版本的内部逻辑，编译器决定它们是否应该内联。在基类和模板派生类中会用到相似的技巧。

## 30. 使用Lippincott 函数

与“去模板化"相同的道理， 这是在异常处理中的一个DRY（Dont't repeat yourself) 原则。如果你有很多异常类型需要处理，你可能会写出如下代码：

```cpp
void use_thing() {
    try {
        do_thing();
    } catch (const std::runtime_error &) {
    // handle it
    } catch (const std::exception &) {
    // handle it
    }
}

void use_other_thing() {
    try {
        do_other_thing();
    } catch (const std::runtime_error &) {
        // handle it
    } catch (const std::exception &) {
        // handle it
    }
}
```

Lippincott 函数提供了一种中心化的异常处理套路：

```cpp
void handle_exception() {
    try {
        throw; // re-throw exception already in flight
    } catch (const std::runtime_error &) {
    } catch (const std::exception &) { }
}

void use_thing() {
    try {
        do_thing();
    } catch (...) {
        handle_exception();
    }
}

void use_other_thing() {
    try {
        do_other_thing();
    } catch (...) {
        handle_exception();
    }
}
```  

这个小技巧不是啥新东西， 它早在C++98时就可以使用了。

## 31. 担心全局状态(Global State）

对全局状态进行推理是很难的， 任何非`const` 的`static`值或者`std::shared_ptr` 都可能是一个潜在的全局状态，你永远不知道谁可能会更新这个值或者它是否是线程安全的。

当一个函数改变了一个全局状态时，它会导致不易察觉的并且很难去追溯的bug， 另一个函数要么会依赖这个变化，要么会受到它的负面影响。

## 32. 让你的接口很难用错

你的接口是你的第一道防线， 如果你提供了一个很容易用错的接口， 你的用户就会错误地使用它。 如果你提供了一个很难用错的接口， 你的用户就会很难去把它用错。但这是C++, 他们总能找到办法的。

设计一个很难用错的接口有时会导致代码的冗长， 你必须选择哪一个是最重要的， 是正确的代码还是短的代码？

## 33. 考虑如果调用错了API是否会导致UB错误

你是否接受一个空指针？ 它是否是个可选参数？如果一个`nullptr`传入你的函数会发生什么？如果一个异常范围的值传入你的函数会发生什么？有些开发者会在内部接口和外部接口里面做个区分，他们允许一些不安全的API在内部接口中使用。

不过你能保证外部的使用者永远不调用内部的API嘛？你能保证内部使用者永远不误用API嘛？

## 34. 大量使用[[nodiscard]]

`[[nodiscard]]`(C++17提供) 是一个C++的特性，它告诉编译器如果返回值被放弃了则需要警告，

它可以用在函数上：

```cpp
[[nodiscard]] int get_value();
int main()
{
    // warning, [[nodiscard]] value ignored

    get_value();
}
```

可以用在类型上：

```cpp
struct [[nodiscard]] ErrorCode{};
ErrorCode get_value();
int main()
{
    // warning, [[nodiscard]] value ignored

    get_value();
}
```

## 35. 使用强类型

考虑一下POSIX socket的API

```cpp
socket(int, int, int);
```

每个参数代表：

  * 类型
  * 协议
  * 域名 这个设计是有问题的， 但是我们代码里面隐藏了更多比这个更不明显的问题。比如一个构造函数：

`Rectangle(int, int, int, int);` 这个函数可能是指`(x,y,width, height)`, 也有可能是指`(x1, y1, x2, y2)`, 或者不太可能但是仍然有可能出现的是含义是`(width, height, x, y)`

那你认为下面这个API怎么样呢？

_强类型API_

```cpp
struct Position {、
    int x;
    int y;
};

struct Size {
    int width;
    int height;
};

struct Rectangle {
    Position position;
    Size size;
};  

Rectangle(Position, Size);
```

这可以延伸出来其它的具有操作符重载的组合语句：

```cpp
// Return a new rectangle that has been
// moved by the offset amount passed in
Rectangle operator+(Rectangle, Position);
```

## 避免bool类型的参数

这章的预发布读者指出， steve Maguire 在他的《编写可靠的代码》的第五章中说过:"要让代码在调用时易于理解“。在C++11中， enum class 提供给了你一种很容易的方法去添加强类型，从而避免布尔类型的参数， 这会使你的API更难用错。

考虑以下代码：

_参数顺序不明显_

```cpp
struct Widget {
    // this constructor is easy to use wrong, we
    // can easily transpose the parameters
    Widget(bool visible, bool resizable);
}
```

与如下代码相比：

强类型带作用域的枚举值

```cpp
struct Widget {
    enum struct Visible { True, False };
    enum struct Resizable { True, False };
    // still possible to use this wrong, but MUCH harder
    Widget(Visible visible, Resizable resizable);
}
```

## 36. 不要返回裸指针

返回一个裸指针会让读者和使用者很难去思考明白它的所有权。 选择引用智能指针， 非归属指针包装器（？++没明白，原文是non owning pointer wrapper++) ，或者考虑可选引用（++没明白是啥，原文是optional reference++)。

返回一个裸指针的函数示例

```cpp
int *get_value();
```

谁拥有这个返回值？是我吗？当我用完它，我是否需要去delete掉这个指针？

或者考虑一种更坏的情况， 如果这个内存使用malloc来分配的，我是不是需要调用free来释放它？

这是个指向单个int值的指针，还是一个int数组？

这个代码有太多问题了， 甚至用`[[no discard]]`都不能帮助我们

## 37. 优先用栈而不是堆

栈对象（非动态分配的作用域在本地的对象）对于优化器更加友好、缓存更加友好、并且可能被优化器完全删除。 正如Björn Fahller所言，”假设任何指针间接指向都是一次cache miss”

用最简单的话来说：

_ok,用栈并且这可以被优化_

```cpp
std::string make_string() {
 return "Hello World"; 
}
```

_不好， 使用了堆_

```cpp
std::unique_ptr<std::string> make_string() {
    return std::make_unique<std::string>("Hello World");
}
```

_OK_

```cpp
void use_string() {
    // This string lives on the stack
    std::string value("Hello World");
}
```

_非常糟糕的写法， 用了堆还内存泄露_

```cpp
void use_string() {
    // The string lives on the heap
    std::string *value = new std::string("Hello World");
}
```

> 记住，`std::string`本身也会在内部分配内存， 并且用的是堆， 如果你的目标是不用任何堆， 你需要用一些其它方法来打到。其实我们的目标是不分配不必要的堆。  

总体来说， 用`new` 创建的对象（或者用`make_unique`或者`make_shared`创建的对象） 都是堆对象，并且拥有动态存储周期（Dynamic Storage Duration), 在本地作用域下创建的对象都是栈对象， 并且具有自动存储周期（Automactic Storage Duration)

## 38. 不要再使用new

你已经避免使用堆并且使用智能指针来管理内存资源了对吧。 再进一步， 在少数一些你需要用堆的情况下，请确保使用 `std::make_unique<>()(C++14)`，在很少见的情况下你需要共享对象的所有权，这时候使用`std::make_shared<>()(c++11)`

## 39. 了解你的容器

优先以这种顺序选择你的容器：

  * std::array<>
  * std::vector<>

## std::array

一个固定大小的分配在栈上的连续容器， 数据的多少必须在编译时期知道， 你必须拥有足够的栈空间去承载数据。 这个容器可以帮助我们优先使用栈而不是堆。已知的位置以及内存连续性会让std::array<>是一个“负成本抽象"(negative cost abstraction)", 因为编译器知道数据的大小和位置， 它可以用额外的一系列优化手段来优化。

## std::vector

一个动态大小分配在堆上的连续容器， 尽管编译器不知道数据最终会驻留在哪里，但他知道元素的在内存中是紧密布局的。内存的连续性给了编译器更多的优化空间并且对缓存更加友好。

> 几乎任何其它事情都需要评论和解释原因， 对于小型的容器， 带有线性搜索的map可能比`std::map`性能要更好。但是别对这点太痴迷了，如果你需要kv查找， 用`std::map`并且评估一下它是否有你想要的性能表现和特性。  

## 40. 避免使用std::bind和std::function

尽管编译器继续提升,优化器也在继续解决这些类型的复杂性， 这些仍然有很有可能去增加编译时间和运行时间的开销。C++14 的`lambda`，具有广义的捕获表达式功能， 能够做到和`std::bind`同样的事情。

用`std::bind`去改变参数的顺序

```cpp
#include <functional>

double divide(double numerator, double denominator) {
    return numerator / denominator;
}

auto inverted_divide = std::bind(divide, std::placeholders::_2,std::placeholders::_1);
```

用lambda去改变参数的顺序

```cpp
#include <functional>

double divide(double numerator, double denominator) {
    return numerator / denominator;
}

auto inverted_divide = [](const auto numerator, const auto denominator) {
    return divide(denominator/numerator)
}
```

## 41. 跳过c++11版本

如果你在正在转向”现代C++", 请跳过Cpp11版本, Cpp14修复了许多Cpp11的漏洞。

其中语言层面的特性包括：

  1. C++11 版本的`constexpr` 隐式地指定了所有成员函数为const(即不能修改this)， 这在C++14已经被改变。
  2. C++11缺少对函数对auto 返回类型的推导(`lambdas`有）
  3. C++11没有`auto`或者可变Lambda参数的
  4. C++14新增`[[deprecated]]`特性
  5. C++14新增了数字分隔符， 比如`1'000'000`
  6. 在C++14里`constexpr` 函数可以有多个return

库层面特性包括：

  1. `std::make_unique` 在C++14中加入
  2. C++11没有`std::exchange`
  3. C++14新增了对`std::array`的`constexpr`支持
  4. `cbegin`, `cend`, `crbegin`, 和`crend` 这些自由函数(`free function` ,没有入参的函数） 为了和begin 和end这些在C++11加入的标准容器中的自由函数保持一致而被加入了。

## 42. 对于重要的类型，不要使用initializer_list

`Initializer List`在C++里面是一个重载项， `Initializer Lists`被用于直接初始化数值。
`initializer_list`被用于向函数或者构造器传入一个value list。

接下来举几个例子讲一下`initializer_list`的一些异常行为（摘自本书作者的youtube上的[讲解视频](https://www.youtube.com/watch?v=sSlmmZMFsXQ)：

```cpp
auto f(int i, int j, int k){
    return std::initializer_list<int>{i, j, k};
}

int main() {
   int argc = 1;
   for (int i: f(argc+1, argc+2, argc+3)){
       std::cout << i << ",";
   }
}
```

最终的结果实际上是个UB行为， 因为上面这段代码的函数f等价于

```cpp
auto f(int i, int j, int k){
    return std::initializer_list<int>{i, j, k};
}

auto f(int i, int j, int k){
    const int __a[] = {i, j, k};
    return std::initializer_list<int>{__a, __a+3}; // pointer local
}
```

因此同理，下面这段代码是没有办法编译成功的(因为unique_ptr不能转让所有权）：

```cpp
#include <vector>
#include <memory>

std::vector<std::unique_ptr<int>> data{
    std::make_unique<int>(40), std::make_unique<int>(2)
};
```

## 43. 使用工具： Build Generators

  * CMake
  * Meson
  * Bazel
  * Others

裸make file或者visual studio的项目文件让上面列出的每个东西都很棘手并难以去实现。 使用build tool工具去帮助你维护在不同平台和编译器之间的可移植性。对待你的build script就想对待你的其它code一样， 它们也有自己的一套best practise, 并且非常容易就写出一个不易维护的build sciprt， 就像写出一个不可维护的C++代码一样。在使用cmake --build的情况下， Build generators同时也可以帮助抽象和简化你的持续集成环境， 这样无论你在用什么平台开发，都可以做出正确的事情。

## 44. 使用包管理工具

最近几年开发者对C++的包管理工具表现出了浓厚的兴趣， 有两个成为了其中最著名的包管理工具：

  * Vcpkg
  * Conan

使用一个包管理工具是绝对有好处的， 包管理工具可以提高可以提高可移植性并且降低开发人员的管理成本。

## 45. 缩短构建时间

对于减少构建时间带来的痛苦，有以下一些很实用的建议：

  1. 将你的代码尽可能地去模板化（不是不用模板）
  2. 在有意义的地方使用前向声明（所谓前向声明是指：A.h引用B.h， B.h又要引用A.h，这时候解决问题的办法是在B.h里面只声明一下A.h里面的A类）
  3. 在你的build system中开启PCH（precompile headers)
  4. 使用ccache
  5. 了解unity builds
  6. 了解外部模板(extern template)能做什么以及它的局限性
  7. 使用构建分析工具去看构建时间被花费在了哪里

**使用IDE**

我所观察到的使用现代IDE最令人惊喜的一个特性就是： IDE对你的代码做了实时分析。实时分析就意味着你在键入代码的时候编译器就知道它是否要编译，因此你会花上更少的时间去等待构建。

## 46. 使用工具: 支持多编译器

在你的平台上你至少要支持两种编译器。 每个编译器都会做不同的分析并且以一种略微不同的方式来实现标准。如果你使用Visual Studio，你应该能够在clang和cl.exe之间灵活切换。 你还可以使用WSL并且开启远程linux 构建。

如果你使用linux系统，你应该能够在GCC和Clang之间能够灵活切换。

> 注意， 在macOS上，确保你在使用的编译器是你想使用的那个，因为gcc 命令很可能是一个苹果公司安装的clang的软连接  

## 47. 模糊测试(Fuzzing)和变异测试(Mutating)

你的想象力限制了你能够构建的测试用例， 你是否有尝试恶意调用API？你有故意去传入一些格式错误的数据给你的输入吗？你是否处理一些未知或者未经信任的数据来源？

在所有可能的情况组合中为所有可能的函数调用生成所有可能的输入是不可能的， 很幸运的是，有工具来为我们解决这些问题。

## 模糊测试

模糊测试工具能够生成各种长度的随机字符串，这种测试能够约束你用合适的方法去处理这些数据，模糊测试工具分析那些从你的测试执行过程中生成出来的覆盖率数据并且使用那些信息去删除多余的测试并且产生新且特殊的测试用例。

理论上来说，如果给它足够的时间，模糊测试可以对你需要测试的代码最终达到100%的代码覆盖率。 结合AddressSanitizer, 它可以成为寻找你代码中bug的强有力的工具。在一个很有趣的文章里面描述了模糊测试工具和AddressSainitzer的组合是如何在小于6个小时内发现OpenSSL的安全漏洞的。

## 变异测试

编译测试是通过修改你代码里的条件和变量来进行测试工作的，举个例子：

```cpp
bool greaterThanFive(const int value) { 
    return value > 5; // comparison
}

void tests() {
 assert(greaterThanFive(6));
 assert(!greaterThanFive(4));
}
```

编译测试能够修改你的常量5或者>运算符， 所以你的code变成：

```cpp
bool greaterThanFive(const int value) {
    return value < 5; // mutated
```

任何能够继续通过的测试用例都属于"存活下来的变异测试用例"， 这就预示着要么你的代码存在bug要么这是一个有缺陷的测试。

## 48. 继续你的C++学习

如果你想变得更强你就要持续不断地学习， 世面上有许多你可以在你的C++学习上使用在资源。(++若干年后， 你就会发现，你变禿了，也变强了++)

