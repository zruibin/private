
<!--BEGIN_DATA
{
    "create_date": "2023-03-08 22:22", 
    "modify_date": "2023-03-08 22:22", 
    "is_top": "0", 
    "summary": "C++20之concept用法详解", 
    "tags": "C/C++", 
    "file_name": "C++20之concept用法详解.md"
}
END_DATA-->

#### <p>原文出处：<a href='https://km.woa.com/articles/show/572829?kmref=author_recommend' target='blank'>C++20之concept用法详解</a></p>

> 还在被各种看不懂的模板元困扰吗？还在被`enable_if`里面的那一嘟噜折磨得死去活来么？C++模板的福音来了！一文带你拿下C++20四大新理念之首——concept。

## Concept基础知识

### 为何要引入Concept？

我们在进行模板元编程的时候，经常会遇到一个问题：如何处理意料之外的类型的实例化？ 举例来说：

```cpp
template <typename T>
bool IsEqual(T left, T right) {
  return left == right;
}
```

当`T`实例化为`int`、`double`、`char`甚至`std::string`都不会有什么问题，但是如果遇到字符串常量：

```cpp
if (IsEqual("abc", str)) {}
```

这里的意义就有可能发生改变，我们知道在C++中，字符串常量会作为`const char[N]`类型出现的，而如果这里的`str`也恰好是C风格的字符串的话，那么这里就会成为「比较指针」是否相等，而不是「比较值」。

所以，这时我们就需要对模板进行限定，并不要所有的类型都可以用于实例化`IsEqual`，而是必须“符合某些条件”才可以。

因此，Concept要解决的问题，就是**对模板的实例化进行限定**，只有满足条件的类型才可以进行实例化，否则编译器将会拦截。

### 什么是Concept？

这里笔者又双叒叕要进行吐槽了……「concept」翻译成中文是「概念」的意思，有点太抽象了，不好理解。（当然也有可能是笔者英语不好吧，不太能够体会这个词有没有什么意会不可言传的含义~）。况且，这个表意如果放到中文里，很容易出现歧义，比如说我说「关于这个概念」，那请问这里的「概念」到底泛指的是「某种抽象」还是特指「concept」？好吧，为了避免这种歧义，笔者将在后面的叙述中，不将「concept」这个词进行翻译，而是直接保留原文；而如果出现「概念」的话，那就指抽象概念了，希望这里不要误导大家。

这里的concept最直白的解释就是「一个静态的bool类型」，如果它为`true`，那么表示模板可以实例化，如果为`false`则表示不允许实例化。

Concept语句需要书写在模板参数之后，模板实体之前，并且需要跟在`requires`关键字之后。我们举个最简单的例子：

```cpp
template <typename T>
requires true
struct Test1 {};

template <typename T>
requires false
struct Test2 {};
```

上例中，`Test1`后跟了一个Concept语句，并且恒为`true`，那么表示，对于任何情况下，`Test1`都是允许实例化的，比如`Test<int>`、`Test<void *>`、`Test<std::string>`甚至`Test<void>`都是合法的实例。自然，这种恒`true`的情况下就可以省略Concpet，也就是说它和下面是等价的：

```cpp
template <typename T>
struct Test1 {};
```

而对于`Test2`来说，它的Concept语句是恒`false`，也就是说任何情况下都不允许实例化。

当然了，直接这样写肯定是没意义的，我们需要让这个Concept成为一些用于判断的语句，它才有价值。例如对于一个模板类，当`T`的大小小于等于`8`时才可以实例化，那么就可以写作：

```cpp
template <typename T>
requires (sizeof(T) <= 8)
struct Test {};
```

可以看出，Concept基本就是在代替C++20之前的`std::enable_if`，解决的问题相同，但实现的思路却不同。`std::enable_if`利用的是SFINAE原则，按照更合适的模板匹配并进行实例化，把允许的「特例」进行实现，而「通用模板」则不实现，那么就可以似的通过SFINAE匹配到的类型可以正常编译，而其他类型则由于找不到通用的实现而无法通过编译（找不到type）。我们用C++17的标准改写上面的实例就是：

```cpp
template <typename T, typename = std::enable_if_t<sizeof(T) <= 8, void>>
struct Test {};
```

而当实例化的`T`不满足（例如用`std::string`实例化）时，会报错，因为找不到`std::enable_if<false, void>::type`。

Concept则是通过语言本身来解决这个问题的，自然会更加清晰直观。**它其实就是在模板定义之前，单独搞了一个专门的区域，用于定义模板可实例化的条件**，这样就不会出现满屏乱飞的`std::enable_if`和及其难以理解的模板嵌套。

### 使用STL工具来做Concept

既然Concept就是一个静态布尔值，那么STL当中的一些返回静态布尔类型的工具就天然可以作为Concept了，例如：

```cpp
template <typename T>
requires std::is_trivial_v<T> // 要求T是平凡的
struct Test1 {};

template <typename T>
requires std::is_base_of_v<google::protobuf::Message, T> // 要求T必须是protobuf的Message子类
struct Test2 {};
```

那么符合Concept怎么办？比如说要求「平凡 且 长度小于指针」，那么同样，可以利用合取工具：

```cpp
template <typename T>
requires std::conjunction_v<std::is_trivial<T>, 
                std::bool_constant<sizeof(T) <= sizeof(void *)>>
struct Test {};
```

但这个时候我们就会发现，代码又一次开始有“爆炸”的趋势，它比使用`std::enable_if`也强不到哪去了。既然C++20提出Concept的概念，那么一定会有更优雅的语法形式。

### Concept块

直接上代码，我们看看如何用「块」的形式表示上一节当中`conjunction`的表达式：

```cpp
template <typename T>
requires requires {
  std::is_trivial_v<T>;
  sizeof(T) <= sizeof(void *);
}
struct Test {};
```

这里出现了两个`requires`大家不要惊讶，前面章节我说过，concept书写的位置在模板参数之后，模板实体之前，并且要有`requires`标记。所以这里的第一个`requires`就是语法结构上的这个标记，用于表明，后面要跟一个concept。

而第二个`requires`则是用于定义一个concept中需要满足的条件列表，也就是说，它是用来修饰后面的大括号的，表示这个大括号里应当是concept块，而不是普通的代码块。

好吧算了……不吐槽了，大家适应一下这个语法~

在concept块中可以定义一组静态布尔语句，之间用分号隔开，它们之间是“逻辑与”的关系，也就是说所有的条件都需要满足，才认为这个concept是满足的。

需要注意的是，一个concept块本质就是一个静态布尔表达式，所以多个concept之间是可以用逻辑符来拼接的，例如：

```cpp
template <typename T>
requires requires {
  std::is_trivial_v<T>;
  sizeof(T) <= sizeof(void *);
} || std::is_trivially_copyable_v<T>
struct Test {};
```

这段例程也间接解答了“逻辑或”关系的concept之间如何表示。

当然了，后面的concept也可以替换成concept块：

```cpp
template <typename T>
requires requires {
  std::is_trivial_v<T>;
  sizeof(T) <= sizeof(void *);
} || requires {
  std::is_trivially_copyable_v<T>;
  sizeof(T) <= 2 * sizeof(void *);
}
struct Test {};
```

通过这段代码，也是希望读者能够体会到两个`requires`含义的不同。

### 独立定义Concept

如果每次我们都直接在模板里定义concept会有两个潜在的问题：一是有可能会由于concept过长而导致模板定义过长；二是如果多个模板需要使用同样的concept则无法复用。

因此，C++也提供了独立定义concept的方法：

```cpp
template <typename T>
concept Available = requires {
  std::is_trivial_v<T>;
  sizeof(T) <= sizeof(void *);
};
```

终于，concept不再仅仅是一种概念，还成为了C++20中的新关键字。用`concept`关键字可以定义一个独立的concept，独立定义的concept可以直接出现在模板的concept语句中：

```cpp
template <typename T>
requires Available<T>
struct Test {};
```

这里需要注意的是，与C++17中直接定义静态布尔类型不同，concept本身就是一个静态布尔类型了，所以不需要取`value`。如果用C++17的方式定义上面的则应该是：

```cpp
template <typename T>
struct Available : std::conjunction_v<
             std::is_trivial<T>, 
           std::bool_constant<sizeof(T) <= sizeof(void *)>
          > {}
template <typename T>
constexpr inline bool Available_v = Available<T>::value;
```

因此在concept中，我们再也不用考虑所谓“traits类型本身”“traits结果类型”“traits静态value”这些乱七八糟的概念，也不用考虑什么时候该加`_t`，什么时候该加`_v`。

### 更加强大的concept

前面我们介绍的是一些concept的简单用法，但其实concept远不止如此，它还可以更优雅地解决很多复杂的需求。

#### 判断某个成员是否存在

例如，我们要求类型`T`需要实现`desc`方法，如果用C++17的方法，是这样的：

```cpp
template <typename T, typename = void>
struct Test;

template <typename T>
struct Test<T, std::void_t<decltype(T::desc)>> {};
```

思路就是用SFINAE匹配，如果`T::desc`存在，那么会被`std::void_t`转化为`void`，并成功命中下面的偏特化。而如果`T::desc`不存在，则会命中上面的通用模板，又因为通用模板是未定义的，因此不能通过编译。但显然，写出这样的代码需要很高的门槛，必须对模板元编程烂熟于心，并熟练掌握SFINAE的匹配原则，然后给编译期玩出这样的文字游戏。

但有了concept，一切都变得简单了，现在我们可以这样写：

```cpp
template <typename T>
requires requires {
  T::desc; // 表示T::desc是合理语句
}
struct Test {};
```

在concept语句中，可以单纯写一个表达式，用于表示「可以执行这样的表达式」，用上面的例子来说就是，对于一个类型`T`，如果我能取到`T::desc`，那么就认为它符合要求。

然而这样带来了另一个问题就是，我不能确定`T::desc`到底是个什么，如果是个成员变量那也能通过：

```cpp
template <typename T>
requires requires {
  T::desc;
}
struct Test {};

struct T1 {
  static int desc;
};
struct T2 {
  static void desc();
};

void Demo() {
  Test<T1> t1; // OK
  Test<T2> t2; // OK
}
```

这种情况我们可以用`std::is_function`来解决：

```cpp
template <typename T>
requires requires {
  std::is_function_v<decltype(T::desc)>;
}
struct Test {};
```

#### 判断非静态成员变量

刚才的例程仅仅对静态成员生效，但如果我要求`desc`是非静态成员函数呢？用C++17的方法是这样：

```cpp
template <typename T, typename = void>
struct Available : std::false_type {};

template <typename T>
struct Available<T, std::void_t<decltype(&amp;T::desc)>> :
  std::is_member_function_pointer<decltype(&amp;T::desc)> {};

template <typename T, typename = std::enable_if_t<Available<T>::value>>
struct Test {};
```

而如果用concept，则会是这样：

```cpp
template <typename T>
requires requires(T t) {
  t.desc();
}
struct Test {};
```

隆重介绍concept语句的「参数列表」。在concept的`requires`后可以跟一个列表，来定义一些用于静态判断的“变量”，注意这里的变量是没有实际意义的，它也不会在实际执行时被初始化，它仅仅是用于承担“静态语法判断”的工作。

那么上面的例子可以解释为“对于一个`T`类型的变量，如果它可以执行`t.desc()`这样的语句，那么就视为合法”，那么我们也就达成了“判断`T`是否含有一个非动态成员函数`desc`”的目的。

#### 判断某个语句的返回值

那如果我要求`desc`是个非静态成员函数，并且返回值是`void`，参数为空，那怎么办？如果用C++17的方法，就要开始“花式炫技”了：

```cpp
template <typename T, typename = void>
struct Available : std::false_type {};

template <typename T>
struct Available<T, std::void_t<decltype(&amp;T::desc)>> :
std::disjunction<
  std::is_same<decltype(&amp;T::desc), void (T::*)(void)>,
  std::is_same<decltype(&amp;T::desc), void (T::*)(void) const>,
  std::is_same<decltype(&amp;T::desc), void (T::*)(void) noexcept>,
  std::is_same<decltype(&amp;T::desc), void (T::*)(void) const noexcept>
> {};

template <typename T, typename = std::enable_if_t<Available<T>::value>>
struct Test {};

struct T1 {
  void desc();
};
struct T2 {
  int desc();
};
struct T3 {
  static int desc;
};

void Demo() {
  Test<T1> t1; // OK
  Test<T2> t2; // ERR
  Test<T3> t3; // ERR
}
```

对于函数是否含有`const`和`noexcept`都需要考虑到。但有了concpet，可以很优雅地解决这个问题：

```cpp
template <typename T>
requires requires(T t) {
  t.desc();
  std::is_same_v<decltype(t.desc()), void>;
}
struct Test {};
```

emmm...怎么说呢，好像也不算优雅。尽管它比`disjunction`的方式优雅多了，但这个返回值的判断仍然还是很奇怪。

由此，concept提供了用于语句返回值判断的语法，那么上面的代码可以改写成这样：

```cpp
template <typename T>
requires requires(T t) {
  {t.desc()}->std::same_as<void>;
}
struct Test {};
```

用一个大括号括起来的语句，表示取这个语句的返回值，当然，它的前提是这个语句能正常执行。那么，后面这个`std::same_as`又是何方神圣呢？

这是STL提供的一些concept之一，它的定义是：

```cpp
template <typename T1, typename T2>
concept same_as = std::is_same_v<T1, T2>;
```

没什么特别的，就是把`std::is_same_v`定义成了`concept`，但这却让它发挥了神奇的功效。在使用大括号表示语句返回值后，**返回值类型会传递给后面concept的第一个参数**，也就是说`{t.desc()}->std::same_as<void>`是把`t.desc()`语句的返回值传给了`std::same_as`的`T1`，而尖括号里的`void`则是传给了`T2`。

所以对于一个concept：

```cpp
template <typename T>
concept C1 = requires(T t) {
  {t.desc()}->std::same_as<void>;
};
```

就等价于：

```cpp
template <typename T>
concept C2 = requires(T t) {
  std::is_same_v<decltype(t.desc()), void>;
};
```

这下，concept的写法确实对得起“优雅”一词了。

### 小结

小结一下：

  * concept是`enable_if`的替代方案，用于约束模板是否允许实例化；

  * concept本质是一个静态布尔类型表达式，可以直接用布尔常量、或是静态布尔类型变量来代替；

  * C++17中的一些`_v`结尾的工具通常可以直接作为concept使用；

  * concept可以用`concept`关键字来独立定义；

  * 在concept块中，表达式均表示“能够这样执行”的含义，并且表达式之间是逻辑与的关系；

  * concept块可以有参数列表，来定义“语法解析”层面的“变量”；

  * concept块中可以用大括号返回表达式的返回值，并把返回值类型交给`->`后的concept的第一个模板参数。

## concept的高级语法

前面我们介绍了concpet的概念，还有基本的用法。不过到目前为止，我们见到的只能算是concept的「正统」形式，怎么说呢，尽管concept作为C++20的四大颠覆性特性之一（甚至之首），但单从形式上来看，还是有些一板一眼了。

```cpp
template <typename T>
requires SomeConditon<T>
struct ClassName {};
```

这种所谓的「标准形式」看上去还是很浓重的C++味道，它给人的感觉就是“嗯~这很C++”。经历过C++17洗礼的同学都知道，C++新标准很喜欢做的事情就是，发布一个看上去非常平平无奇的新特性，但稍微一展开、一组合，这个特性就爆炸了，让人拍案叫绝。同理，concept并不是只有这种标准用法，今天这篇我们就来让concept代码“飞起来~”

### concept作为类型关键字使用

当一个concept恰好是修饰模板参数中的一个类型（而不是它的变体）时，concept可以直接作为类型关键字使用。这样描述可能不好理解，我们来看例子：

```cpp
template <typename T>
concept Condi1 = std::is_trivial_v<T>; // 这是一个concept

template <typename T>
requires Condi1<T> // 这里concept直接作用于T，而不是类似于T *或者std::decay_t<T>之类的
struct Test {};
```

上面例子中，`Test`模板类需要一个concpet名为`Condi1`，它直接作用于模板参数`T`上，那么就可以改写成下面的形式：

```cpp
template <Condi1 T>
struct Test {};
```

这就好像`Condi1`成为了一个类型关键字，理解为「符合Condi1定义的类型T」。

这里有一个需要注意的就是，如果作为类型关键字使用，那么它必须是一个`concept`定义，而不能是其他形式的静态布尔表达式，比如说：

```cpp
template <std::is_trivial_v T> // ERR，因为std::is_trivial_v并不是concept定义
struct Test {};
```

不过遇到修饰模板参数的变体，或者存在复合约束的时候，那就只能去使用`requires`语句了，比如说：

```cpp
template <typename T>
requires std::is_trivial_v<std::decay_t<T>> // 约束T的变体
struct Test1 {};

template <typename T>
requires std::is_trivial_v<T> &amp;&amp; (sizeof(T) <= sizeof(void *)) // 复合约束
struct Test2 {};
```

当然，它本身和`requires`语句并不冲突，遇到一些复合约束的时候，两种语法可以共存，比如：

```cpp
template <typename T>
concept Condi1 = std::is_trivial_v<T>;

template <typename T>
concept Condi2 = sizeof(std::decay_t<T>) < sizeof(void *);

template <Condi1 T1, typename T2>
requires Condi1<T2> &amp;&amp; Condi2<T2>
struct Test {};
```

### 模板函数的concept

前面的章节我们都在介绍模板类使用concept的情况，但其实对于模板函数，还会有不一样的风景等着我们。

首先，模板函数仍然支持concept的标准形式，比如：

```cpp
template <typename T>
requires std::is_trivial_v<T>
void f() {}
```

这种用法和模板类完全一致，不再赘述。那么当然它也支持用concept作为类型关键字的形式：

```cpp
template <typename T>
concept Trivial = std::is_trivial_v<T>;

template <Trivial T>
void f() {}
```

但模板函数相比模板类，多了一种可以确定模板参数的途径，那就是参数类型自动推导。回忆一下，对于模板函数来说，编译器可以根据实参类型来推导出模板参数类型，比如说：

```cpp
template <typename T, typename R>
void f(T t, R r) {}
void Demo() {
  f(1, 3.5); // 推导出f<int, double>
  f("abc", 6ul); // 推导出f<const char *, unsigned long>
}
```

而concept同样可以作为「参数类型」来修饰形参，比如：

```cpp
template <typename T>
concept Trivial = std::is_trivial_v<std::decay_t<T>>;
void f(Trivial auto t, Trivial auto r) {}

void Demo() {
  f(1, 3.5); // 会推导出f<int, double>，再分别去检查Trivial<int>和Trivial<double>是否合理
  f('A', std::string("abc")); // ERR，首先推导出f<char, std::string &amp;&amp;>而因为Trivial<std::string>会返false，因此不允许这种实例化
}
```

这个语法着实是把concept玩飞了，至此我们甚至不需要`template`关键字就可以定义一个模板函数了。当然这么做的缺点就在于，可能不容易让人意识到这是一个模板函数，于是把声明和实现分散在.h和.cpp中，导致链接错误。所以这里着重强调：**虽然这种语法没有出现`template`关键字，但它仍是模板，需要定义在头文件中！！**

### 使用concept后可能会遇到的疑惑

至此我们基本将concept的概念和用法介绍完毕了。但正如我前面所说的，一个新特性本身可能没有太多东西，但和其他特性组合一下就可能会“爆炸”，所以本节主要介绍concept特性相关的可能会遇到的疑惑点。

#### 模板特化

如果一个模板用了concept修饰，它还能不能被特化呢？答案是可以！concept本身不影响SFINAE的匹配原则，同样支持特化。但是必须有一个前提，就是说**特化类型必须符合concept，否则不许特化**，举例来说：

```cpp
#include <concepts> // STL标准库提供了很多concept可以使用
template <std::integral T> // 要求T必须是整数
struct Test {};

template <>
struct Test<long> {}; // OK，对于long类型的特化

template <>
struct Test<std::string> {}; // ERR，因为std::string本身不符合std::integral，因此不可以特化

void Demo() {
  Test<int> t1; // 用通用模板进行实例化Test<int>
  Test<long> t2; // 会使用Test<long>的特化
}
```

而对于偏特化同样是允许的，但也是要符合concept的类型。比如：

```cpp
template <std::integral T1, std::integral T2>
struct Test {};

template <typename T>
struct Test<int, T> {}; // 偏特化，OK
```

#### concept用作偏特化

我们可以定义用concept约束的偏特化。举例来说：

```cpp
template <typename T>
struct Test {};

template <std::integral T>
struct Test<T> {};

void Demo() {
  Test<int> t1; // 由于int符合std::integral，因此用偏特化模板实例化Test<int>
  Test<std::string> t2; // 会用通用模板实例化Test<std::string>
}
```

在上面例子中，`Test`通用模板原本是没有被concept约束的，我们可以定义如果`T`符合“某些特性”的话，就使用一种特化。比如说上面就是当`T`符合`std::integral`时，使用下面的特化。因此，这里本质是也一种模板的偏特化。

需要注意的是，与其他偏特化一致，如果某种实例同时命中多个偏特化，却没有针对于这种类型的全特化模板时，将会报二义性错误：

```cpp
template <typename T>
struct Test {};

template <std::integral T>
struct Test<T> {};

template <typename T>
requires (sizeof(T) == 1)
struct Test<T> {};

void Demo() {
  Test<int> t1;
  Test<std::string> t2;
  Test<char> t3; // Ambiguous partial specializations of 'Test<char>'
}
```

另一个要注意的是，偏特化必须要“更加特化”，也就是说偏特化后的范围应当比特化前的范围更窄，但并没有窄到只剩一种类型（不然就叫全特化了），例如：

```cpp
template <std::integral T>
struct Test {};

template <std::unsigned_integral T> // 针对于无符号数的偏特化
struct Test<T> {};
```

首先，**偏特化的约束必须包含通用模板中的约束**，这里`unsigned_integral`表示无符号整数，而`integral`表示整数，显然有包含关系。当然了，这种包含关系并不是看出来的，而是要从定义上包含，我们看看`unsigned_integral`的定义就知道了：

```cpp
template <typename T>
concept unsigned_integral = std::integral<T> &amp;&amp; !std::signed_integral<T>;
```

因为`unsigned_integral`内部已经包含`unsigned_integral`了，所以才OK。但是如果你用的是两种不搭噶的concept，就会报错，比如说：

```cpp
template <typename T>
requires (sizeof(T) <= 16)
struct Test {};

template <typename T>
requires (sizeof(T) <= 8)
struct Test<T> {}; // Class template partial specialization is not more specialized than the primary template
```

尽管这里，长度小于`8`确实是包含在长度小于`16`中了，但编译器不会做这种集合运算，你必须要显式定义出来才行，所以正确的做法是：

```cpp
template <typename T>
concept Con1 = (sizeof(T) <= 16);

template <typename T>
concept Con2 = Con1<T> &amp;&amp; (sizeof(T) <= 8); // 尽管包含Con1是句废话，但必须要写

template <Con1 T>
struct Test {};

template <Con2 T> 
struct Test<T> {}; // 因为Con2显式包含了Con1，所以才OK
```

注意这里是「显式」包含才可以，比如说下面这种就不可以：

```cpp
template <typename T>
requires (sizeof(T) <= 16)
struct Test {};

template <typename T>
requires (sizeof(T) <= 16) &amp;&amp; (sizeof(T) <= 8)
struct Test<T> {}; // 仍然不可以，因为没有「显式」包含
```

下面这种形式也算「显式」包含，所以也是OK的：

```cpp
template <typename T>
concept Con1 = (sizeof(T) <= 16);

template <typename T>
requires Con1<T>
struct Test {};

template <typename T>
requires Con1<T> &amp;&amp; (sizeof(T) <= 8) // 因为这里也显式用到Con1了，所以OK
struct Test<T> {};
```

通过这些例子就是希望读者能明白在利用concept进行偏特化时，如何才算符合「偏特化」要求。

#### 函数重载

由于模板函数不能偏特化，因此也不会出现前一节出现的各种问题。不过函数是支持重载的，用concept修饰的模板函数并不影响函数重载，请看例程：

```cpp
void f(std::integral auto t) {}

void f(int t) {} // OK

int f(double t) {return 0;} // OK
```

由于函数重载的优先级大于SFINAE匹配，因此这里的函数重载都是OK的。当然，它同样不影响模板全特化：

```cpp
void f(std::integral auto t) {std::cout << 1 << std::endl;}

void f(int t) {std::cout << 2 << std::endl;}

template <>
void f<int>(int t) {std::cout << 3 << std::endl;}

void Demo() {
  f(1u); // 打印1
  f(1); // 打印2
  f<>(1); // 打印3
}
```

上面例子说明了函数重载优先级大于SFINAE，所以`f(1)`会调用重载函数。而显式添加了`<>`后，强制使用模板实例，再进行SFINAE时全特化优先级大于通用模板，所以会调用全特化实例。

总之这些都跟以前的模板没有任何变化，主要需要大家牢记的一点就是**用concept修饰的函数虽然没有`template`关键字，但它依然是模板函数**，其他的东西就都可以推出来了。

#### 模板函数的“偏特化”

大家应该注意到了，我这里的“偏特化”是打双引号的。的确，C++20仍然是**不允许模板函数的偏特化**的，比如：

```cpp
template <typename T, typename R>
void f2() {};

template <typename T>
void f2<T, int>() {} // Function template partial specialization is not allowed
```

但引入了concept之后，模板函数却可以支持「concept的偏特化」，请看例子：

```cpp
void f(std::integral auto t) {std::cout << 1 << std::endl;}

void f(std::unsigned_integral auto t) {std::cout << 2 << std::endl;}

void Demo() {
  f(1); // 打印1
  f(1u); // 打印2
}
```

相信细心的读者应该已经发现了，其实这并不是「偏特化」，而是**函数重载**，所以这种情况下，并不要求按照前面章节所叙述的模板类的那种偏特化原理，即便两个concept是不包含的，也仍然能通过编译。

但是一定要注意，一旦某种类型同时命中多个模板函数，则会直接报二义性错误，比如：

```cpp
template <typename T>
concept Small = sizeof(T) == 1;

void f(std::integral auto t) {std::cout << 1 << std::endl;}

void f(Small auto t) {std::cout << 2 << std::endl;}

void Demo() {
  f(1); // 打印1
  f('A'); // Call to 'f' is ambiguous
}
```

由于`char`类型的实例化同时命中了两个模板定义，因此无法生成两个重载函数，所以直接报二义性错误了，这一点希望大家在使用时能够注意。

## 总结

C++20跟C++11类似，给C++标准给出了一个新的方向标。

而作为C++中最困难的模板元编程，原本旨在不断扩充编译期功能，最大程度上把「更多的事情闭环在运行之前」。但这同时也让C++的模板语法愈发复杂，可读性直线下降，对学习者也是各种强烈劝退。而在Concept的帮助下模板元编程得到了非常好的简化，因此可以算得上是一次拨乱反正，大大降低了使用C++模板范式的门槛。
