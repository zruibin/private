
<!--BEGIN_DATA
{
    "create_date": "2020-11-28 16:24", 
    "modify_date": "2020-11-28 16:24", 
    "is_top": "0", 
    "summary": "C++语言中std::array的神奇用法总结", 
    "tags": "C/C++", 
    "file_name": "C++语言中array的神奇用法总结.md"
}
END_DATA-->

#### <p>原文出处：<a href='https://bbs.huaweicloud.com/blogs/214624' target='blank'>C++语言中std::array的神奇用法总结</a></p>

>【摘要】 std::array是在C++11标准中增加的STL容器，它的设计目的是提供与原生数组类似的功能与性能。也正因此，使得std::array有很多与其他容器不同的特殊之处，比如：std::array的元素是直接存放在实例内部，而不是在堆上分配空间；std::array的大小必须在编译期确定；std::array的构造函数、析构函数和赋值操作符都是编译器隐式声明的……这让很多用惯了std::ve...

**std::array**是在C++11标准中增加的STL容器，它的设计目的是提供与原生数组类似的功能与性能。也正因此，使得**std::array**有很多与其他容器不同的特殊之处，比如：**std::array**的元素是直接存放在实例内部，而不是在堆上分配空间；**std::array**的大小必须在编译期确定；**std::array**的构造函数、析构函数和赋值操作符都是编译器隐式声明的……这让很多用惯了**std::vector**这类容器的程序员不习惯，觉得**std::array**不好用。  

但实际上，**std::array**的威力很可能被低估了。在这篇文章里，我会从各个角度介绍下**std::array**的用法，希望能带来一些启发。  

本文的代码都在C++17环境下编译运行。当前主流的**g++**版本已经能支持C++17标准，但是很多版本（如**gcc 7.3**）的C++17特性不是默认打开的，需要手工添加编译选项**-std=c++17**。  

### 自动推导数组大小

很多项目中都会有类似这样的全局数组作为配置参数：


```cpp
uint32_t g_cfgPara[] = {1, 2, 5, 6, 7, 9, 3, 4};
```

当程序员想要使用**std::array**替换原生数组时，麻烦来了：  


```cpp
array<uint32_t, 8> g_cfgPara = {1, 2, 5, 6, 7, 9, 3, 4};  // 注意模板参数“8”
```

程序员不得不手工写出数组的大小，因为它是**std::array**的模板参数之一。如果这个数组很长，或者经常增删成员，对数组大小的维护工作恐怕不是那么愉快
的。  

有人要抱怨了：**std::array**的声明用起来还没有原生数组方便，选它干啥？  

但是，这个抱怨只该限于C++17之前，C++17带来了[类模板参数推导](https://en.cppreference.com/w/cpp/language/class_template_argument_deduction)特性，你不再需要手工指定类模板的参数：  

```cpp
array g_cfgPara = {1, 2, 5, 6, 7, 9, 3, 4};  // 数组大小与成员类型自动推导
```

看起来很美好，但很快就会有人发现不对头：数组元素的类型是什么？还是**std::uint32_t**吗？  
有人开始尝试只提供元素类型参数，让编译器自动推导长度，遗憾的是，它不会奏效。  


```cpp    
array<uint32_t> g_cfgPara = {1, 2, 5, 6, 7, 9, 3, 4};  // 编译错误
```

好吧，暂时看起来**std::array**是不能像原生数组那样声明。下面我们来解决这个问题。  

### 用函数返回std::array

问题的解决思路是用函数模板来替代类模板——因为C++允许函数模板的部分参数自动推导——我们可以联想到**std::make_pair**、**std::make_tuple**这类辅助函数。巧的是，C++标准真的在TS v2试验版本中推出过[std::make_array](https://en.cppreference.com/w/cpp/experimental/make_array)，然而因为类模板参数推导的问世，这个工具函数后来被删掉了。  

但显然，用户的需求还是存在的。于是在C++20中，又新增了一个辅助函数[std::to_array](https://en.cppreference.com/w/cpp/container/array/to_array)。  

别被C++20给吓到了，这个函数的代码其实很简单，我们可以把它拿过来定义在自己的C++17代码中[1]。  


```cpp
template<typename R, typename P, size_t N, size_t... I>
constexpr array<R, N> to_array_impl(P (&a)[N], std::index_sequence<I...>) noexcept
{
    return { {a[I]...} };
}

template<typename T, size_t N>
constexpr auto to_array(T (&a)[N]) noexcept
{
    return to_array_impl<std::remove_cv_t<T>, T, N>(a, std::make_index_sequence<N>{});
}

template<typename R, typename P, size_t N, size_t... I>
constexpr array<R, N> to_array_impl(P (&&a)[N], std::index_sequence<I...>) noexcept
{
    return { {move(a[I])...} };
}

template<typename T, size_t N>
constexpr auto to_array(T (&&a)[N]) noexcept
{
    return to_array_impl<std::remove_cv_t<T>, T, N>(move(a), std::make_index_sequence<N>{});
}
```

细心的朋友会注意到，上面这个定义与C++20的推荐实现有所差异，这是有目的的。稍后我会解释这么干的原因。  
现在让我们尝试下用新方法解决老问题：  


```cpp
auto g_cfgPara = to_array<int>({1, 2, 5, 6, 7, 9, 3, 4});  // 类型不是uint32_t？
```

不对啊，为什么元素类型不是原来的**std::uint32_t**？  
这是因为模板参数推导对**std::initializer_list**的元素拒绝隐式转换，如果你把**to_array**的模板参数从**int**改为**uint32_t**，会得到如下编译错误：  


```cpp
D:\Work\Source_Codes\MyProgram\VSCode\main.cpp:51:61: error: no matching function for call to 'to_array<uint32_t>(<brace-enclosed initializer list>)'
  auto g_cfgPara = to_array<uint32_t>({1, 2, 5, 6, 7, 9, 3, 4});
D:\Work\Source_Codes\MyProgram\VSCode\main.cpp:34:16: note: candidate: 'template<class T, long long unsigned int N> constexpr auto to_array(T (&)[N])'
  constexpr auto to_array(T (&a)[N]) noexcept
                ^~~~~~~~
D:\Work\Source_Codes\MyProgram\VSCode\main.cpp:34:16: note:   template argument deduction/substitution failed:
D:\Work\Source_Codes\MyProgram\VSCode\main.cpp:51:61: note:   mismatched types 'unsigned int' and 'int'
  auto g_cfgPara = to_array<uint32_t>({1, 2, 5, 6, 7, 9, 3, 4});
D:\Work\Source_Codes\MyProgram\VSCode\main.cpp:46:16: note: candidate: 'template<class T, long long unsigned int N> constexpr auto to_array(T (&&)[N])'
  constexpr auto to_array(T (&&a)[N]) noexcept
                ^~~~~~~~
D:\Work\Source_Codes\MyProgram\VSCode\main.cpp:46:16: note:   template argument deduction/substitution failed:
D:\Work\Source_Codes\MyProgram\VSCode\main.cpp:51:61: note:   mismatched types 'unsigned int' and 'int'
```

Hoho，有点惨是不，绕了一圈回到原点，还是不能强制指定类型。  

这个时候，之前针对**std::array**做的修改派上用场了：我给**to_array_impl**增加了一个模板参数，让输入数组的元素和返回**std::array**的元素用不同的类型参数表示，这样就给类型转换带来了可能。为了实现转换到指定的类型，我们还需要添加两个工具函数：  


```cpp
template<typename R, typename P, size_t N>
constexpr auto to_typed_array(P (&a)[N]) noexcept
{
    return to_array_impl<R, P, N>(a, std::make_index_sequence<N>{});
}

template<typename R, typename P, size_t N>
constexpr auto to_typed_array(P (&&a)[N]) noexcept
{
    return to_array_impl<R, P, N>(move(a), std::make_index_sequence<N>{});
}
```

这两个函数和**to_array**的区别是：它带有3个模板参数：第一个是要返回的**std::array**的元素类型，后两个和**to_array**一样。这样我们就可以通过指定第一个参数来实现定制**std::array**元素类型了。


```cpp
auto g_cfgPara = to_typed_array<uint32_t>({1, 2, 5, 6, 7, 9, 3, 4});  // 自动把元素转换成uint32_t
```

这段代码可以编译通过和运行，但是却有类型转换的编译告警。当然，如果你胆子够大，可以在**to_array_impl**函数中放一个**static_cast**来消除告警。但是编译告警提示了我们一个不能忽视的问题：如果万一输入的数值溢出了怎么办？  


```cpp
auto g_a = to_typed_array<uint8_t>({256, -1});  // 数字超出uint8_t范围
```

编译器还是一样的会让你编译通过和运行，**g_a**中的两个元素的值将分别为0和255。如果你不明白为什么这两个值和入参不一样，你该复习下整型溢出与回绕的知
识了。  

显然，这个方案还不完美。但我们可以继续改进。  

### 编译期字面量数值合法性校验

首先能想到的做法是在**to_array_impl**函数中放入一个if判断之类的语句，对于超出目标数值范围的输入抛出异常或者做其他处理。这当然可行，但要注意的是这些工具函数是可以在运行期调用的，对于这种常用的基础函数来说，性能至关重要。一旦在里面加入了错误判断，意味着运行时的每一次调用性能都会下降。  

理想的设计是：只有在编译期生成的数组才进行校验，并且报编译错误。但运行时调用函数时不要加入任何校验。  

可惜的是，至少在C++20之前，没有办法指定函数只允许在编译期执行[2]。那有没有其他手段呢？  

熟悉C++的人知道：C++的编译期处理大多可以用模板的trick来完成——因为模板参数一定是编译期常量。因此我们可以用模板参数来完成编译期处理——只要把数组元素全部作为模板的非类型参数就可以了。当然，这里有个问题：模板的非类型参数的类型怎么确定？正好C++17提供了**auto**模板参数的功能，可以派上用场：  


```cpp
template<typename T>
constexpr void CheckIntRanges() noexcept {}  // 用于终结递归

template<typename T, auto M, auto... N>
constexpr void CheckIntRanges() noexcept
{
    // 防止无符号与有符号比较
    static_assert(!((std::numeric_limits<T>::min() >= 0) && (M < 0)));
    // 范围校验
    static_assert((M >= std::numeric_limits<T>::min()) && 
                  (M <= std::numeric_limits<T>::max()));
                  
    CheckIntRanges<T, N...>();
}

template<typename T, auto... N>
constexpr auto DeclareArray() noexcept
{
    CheckIntRanges<T, N...>();
    array<T, sizeof...(N)> a{{static_cast<T>(N)...}};
    return a;
};
```

注意这个函数中，所有的校验都通过**static_assert**完成。这就保证了校验一定只会发生在编译期，不会带来任何运行时开销。  
**DeclareArray**的使用方法如下：  


```cpp
constexpr auto a1 = DeclareArray<uint8_t, 1, 2, 3, 4, 255>();  // 声明一个std::array<uint8_t, 5>，元素分别为1, 2, 3, 4, 255
static_assert(a1.size() == 5);
static_assert(a1[3] == 4);
auto a2 = DeclareArray<uint8_t, 1, 2, 3, -1>();  // 编译错误，-1超出uint8_t范围
auto a3 = DeclareArray<uint16_t, 1, 2, 3, 65536>();  // 编译错误，65536超出uint16_t范围
```

这里有一个误区需要说明：有些人可能会把**DeclareArray**声明成这样：  


```cpp
template<typename T, T... N>  // 注意N的类型为T
constexpr auto DeclareArray() noexcept
```

这么做的话，会发现对数值的校验总是能通过——因为模板参数在进入校验之前就已经被转换为**T**类型了。如果你的编译器不支持C++17的**auto**模板参数，那么可以通过使用**std::uint64_t**、**std::int64_t**这些“最大”的类型来间接达到目的。  

另一点要说明的是，C++对于非类型模板参数的允许类型存在限制，**DeclareArray**的方法只能用于数组元素为基本类型的场景（至少在C++20以前如此）。但是这也足够了。如果数组的元素是自定义类型，就可以通过自定义的构造函数等方法来控制类型转换。  

如果你看到这里觉得有点意思了，那就对了，后面还有更过瘾的。  

### 编译期生成数组

C++11中新增的**constexpr**修饰符可以在编译期完成很多计算工作。但是一般**constexpr**函数只能返回单个值，一旦你想用它返回一串对象的集合，就会遇到麻烦：STL容器都有动态内存申请功能，不能作为编译期常量（至少在C++20之前如此）；而原生数组作为返回值会退化为指针，导致返回悬空的指针。即使是返回数组的引用也是不行的，会产生悬空的引用。  


```cpp
constexpr int* Func() noexcept
{
    int a[] = {1, 2, 3, 4};
    return a;  // 严重错误！返回局部对象的地址
}
```

直到**std::array**的出现，这个问题才得到较好解决。**std::array**既可以作为编译期常量，又可以作为函数返回值。于是，它成为了编译期返回集合数据的首选。  

在上面**to_array**等工具函数的实现中，我们已经见过了编译期返回数组是怎么做的。这里我们再大胆一点，写一个编译期冒泡排序：  


```cpp
template<typename T, size_t N>
constexpr std::array<T, N> Sort(const std::array<T, N>& numbers) noexcept
{
    std::array<T, N> sorted(numbers);
    for (int i = 0; i < N; ++i) {
        for (int j = N - 1; j > i; --j) {
            if (sorted[j] < sorted[j - 1]) {
                T t = sorted[j];
                sorted[j] = sorted[j - 1];
                sorted[j - 1] = t;
            }
        }
    }
    return sorted;
}

int main()
{
    constexpr std::array<int, 4> before{4, 2, 3, 1};
    constexpr std::array<int, 4> after = Sort(before);
    static_assert(after[0] == 1);
    static_assert(after[1] == 2);
    static_assert(after[2] == 3);
    static_assert(after[3] == 4);
    return 0;
}
```

因为整个排序算法都是在编译期完成，所以我们没有必要太关注冒泡排序的效率问题。当然，只要你愿意，完全可以写出一个编译期快速排序——毕竟**constexpr**函数也可以在运行期使用，不好说会不会有哪个憨憨在运行时调用它。  

在编写**constexpr**函数时，有两点需要注意：  

1. **constexpr**函数中不能调用非**constexpr**函数。因此在交换元素时不能用**std::swap**，排序也不能直接调用**std::sort**。  
2. 传入的数组是**constexpr**的，因此参数类型必须加上**const**，也不能对数据进行就地排序，必须返回一个新的数组。  

虽然限制很多，但编译期算法的好处也是巨大的：如果运算中有数组越界等未定义行为，编译将会失败。相比起运行时的测试，编译期测试**constexpr**函数能有效的提前拦截问题。而且只要编译通过就意味着测试通过，比起额外跑白盒测试用例方便多了。  

上面的一大串**static_assert**语句让人看了不舒服。这么写的原因是**std::array**的**operator==**函数并非**constexpr**（至少在C++20前如此）。但是我们也可以自己定义一个模板函数用于判断两个数组是否相等：  


```cpp
template<typename T, typename U, size_t M, size_t N>
constexpr bool EqualsImpl(const T& lhs, const U& rhs)
{
    static_assert(M == N);
    for (size_t i = 0; i < M; ++i) {
        if (lhs[i] != rhs[i]) {
            return false;
        }
    }
    return true;
}

template<typename T, typename U>
constexpr bool Equals(const T& lhs, const U& rhs)
{
    return EqualsImpl<T, U, size(lhs), size(rhs)>(lhs, rhs);
}

template<typename T, typename U, size_t N>
constexpr bool Equals(const T& lhs, const U (&rhs)[N])
{
    return EqualsImpl<T, const U (&)[N], size(lhs), N>(lhs, rhs);
}

int main()
{
    constexpr std::array<int, 4> before{4, 2, 3, 1};
    constexpr std::array<int, 4> after = Sort(before);
    static_assert(Equals(after, {1, 2, 3, 4}));  // 比较std::array和原生数组
    static_assert(!Equals(before, after));  // 比较两个std::array
    return 0;
}
```

我们定义的**Equals**比**std::array**的比较运算符更强大，甚至可以在**std::array**和原生数组之间进行比较。  

对于**Equals**有两点需要说明：  

1. **std::size**是C++17提供的工具函数，对各种容器和数组都能返回其大小。当然，这里的**Equals**只会允许编译期确定大小的容器传入，否则触发编译失败。  
2. **Equals**定义了两个版本，这是被C++的一个限制所逼的迫不得已：C++禁止**{...}**这种**std::initializer_list**字面量被推导为模板参数类型，因此我们必须提供一个版本声明参数类型为数组，以便**{1, 2, 3, 4}**这种表达式能作为参数传进去。  

编译期排序是一个启发性的尝试，我们可以用类似的方法生成其他的编译期集合常量，比如指定长度的自然数序列：  


```cpp
template<typename T, size_t N>
constexpr auto NaturalNumbers() noexcept
{
    array<T, N> arr{0};  // 显式初始化不能省
    for (size_t i = 0; i < N; ++i) {
        arr[i] = i + 1;
    }
    return arr;
}

int main()
{
    constexpr auto arr = NaturalNumbers<uint32_t, 5>();
    static_assert(Equals(arr, {1, 2, 3, 4, 5}));
    return 0;
}
```

这段代码的编译运行都没有问题，但它并不是推荐的做法。原因是在**NaturalNumbers**函数中，先定义了一个内容全0的局部数组，然后再挨个修改它的值，这样没有直接返回指定值的数组效率高。有人会想能不能把**arr**的初始化给去掉，但这样会导致编译错误——**constexpr**函数中不允许定义没有初始化的局部变量。  
可能有人觉得这些计算都是编译期完成的，对运行效率没影响——但是不要忘了**constexpr**函数也可以在运行时调用。  

更好的做法可以参见前面**to_array**函数的实现，让数组的初始化一气呵成，省掉挨个赋值的步骤。  
我们用这个新思路，写一个通用的数组生成器，它可以接受一个函数对象作为参数，通过调用这个函数对象来生成数组每个元素的值。下面的代码还演示了下如何用这个生成器在编译期生成奇数序列和斐波那契数列。  


```cpp
template<typename T>
constexpr T OddNumber(size_t i) noexcept
{
    return i * 2 + 1;
}

template<typename T>
constexpr T Fibonacci(size_t i) noexcept
{
    if (i <= 1) {
        return 1;
    }
    return Fibonacci<T>(i - 1) + Fibonacci<T>(i - 2);
}

template<typename T, size_t N, typename F, size_t... I>
constexpr array<std::remove_cv_t<T>, N> GenerateArrayImpl(F f, std::index_sequence<I...>) noexcept
{
    return { {f(I)...} };
}

template<size_t N, typename F, typename T = invoke_result_t<F, size_t>>
constexpr array<T, N> GenerateArray(F f) noexcept
{
    return GenerateArrayImpl<T, N>(f, std::make_index_sequence<N>{});
}

int main()
{
    constexpr auto oddNumbers = GenerateArray<5>(OddNumber<uint8_t>);
    static_assert(Equals(oddNumbers, {1, 3, 5, 7, 9}));
    constexpr auto fiboNumbers = GenerateArray<5>(Fibonacci<uint32_t>);
    static_assert(Equals(fiboNumbers, {1, 1, 2, 3, 5}));
    // 甚至可以传入lambda来定制要生成的数字序列（限定C++17）
    constexpr auto specified = GenerateArray<3>([](size_t i) { return i + 10; });
    static_assert(Equals(specified, {10, 11, 12}));
    return 0;
}
```

最后那个传入**lambda**来定制数组的做法存在一个疑问：**lambda**是**constexpr**函数吗？答案为：可以是，但需要C++17支持。  

**GenerateArray**这个数组生成器将会在后面发挥重大作用，继续往下看。  

### 截取子数组

**std::array**并未提供输入一个指定区间来建立新容器的构造函数，但是借助上面的数组生成器，我们可以写个辅助函数来实现子数组生成操作（这里再次用上了**lambda**函数作为生成算法）。  


```cpp
template<size_t N, typename T>
constexpr auto SubArray(T&& t, size_t base) noexcept
{
    return GenerateArray<N>([base, t = forward<T>(t)](size_t i) { return t[base + i]; });
}

template<size_t N, typename T, size_t M>
constexpr auto SubArray(const T (&t)[M], size_t base) noexcept
{
    return GenerateArray<N>([base, &t](size_t i) { return t[base + i]; });
}

int main()
{
    // 以std::initializer_list字面量为原始数据
    constexpr auto x = SubArray<3>({1, 2, 3, 4, 5, 6}, 2);  // 下标为2开始，取3个元素
    static_assert(Equals(x, {3, 4, 5}));
    // 以std::array为原始数据
    constexpr auto x1 = SubArray<2>(x, 1);  // 下标为1开始，取2个元素
    static_assert(Equals(x1, {4, 5}));
    // 以原生数组为原始数据
    constexpr uint8_t a[] = {9, 8, 7, 6, 5};
    constexpr auto y = SubArray<2>(a, 3);
    static_assert(Equals(y, {6, 5}));  // 下标为3开始，取2个元素
    // 以字符串为原始数据，注意生成的数组不会自动加上'\0'
    constexpr const char* str = "Hello world!";
    constexpr auto z = SubArray<5>(str, 6);
    static_assert(Equals(z, {'w', 'o', 'r', 'l', 'd'}));  // 下标为6开始，取5个元素
    
    // 以std::vector为原始数据，非编译期计算
    vector<int32_t> v{10, 11, 12, 13, 14};
    size_t n = 2;
    auto d = SubArray<3>(v, n);  // 运行时生成数组
    assert(Equals(d, {12, 13, 14}));  // 注意不能用static_assert，不是编译期常量
    return 0;
}
```

使用**SubArray**时，模板参数**N**是要截取的子数组大小，入参**t**是任意能支持下标操作的类型，入参**base**是截取元素的起始位置。
由于**std::array**的大小在编译期是确定的，因此**N**必须是编译期常量，但参数**base**可以是运行时变量。  
当所有入参都是编译期常量时，生成的子数组也是编译期常量。  
**SubArray**提供了两个版本，目的也是为了让**std::initializer_list**字面量可以作为参数传入。  

### 拼接多个数组

采用类似的方式可以做多个数组的拼接，这里同样用了**lambda**作为生成函数。  


```cpp
template<typename T>
constexpr auto TotalLength(const T& arr) noexcept
{
    return size(arr);
}

template<typename P, typename... T>
constexpr auto TotalLength(const P& p, const T&... arr) noexcept
{
    return size(p) + TotalLength(arr...);
}

template<typename T>
constexpr auto PickElement(size_t i, const T& arr) noexcept
{
    return arr[i];
}

template<typename P, typename... T>
constexpr auto PickElement(size_t i, const P& p, const T&... arr) noexcept
{
    if (i < size(p)) {
        return p[i];
    }
    return PickElement(i - size(p), arr...);
}

template<typename... T>
constexpr auto ConcatArrays(const T&... arr) noexcept
{
    return GenerateArray<TotalLength(arr...)>([&arr...](size_t i) { return PickElement(i, arr...); });
}

int main()
{
    constexpr int32_t a[] = {1, 2, 3};  // 原生数组
    constexpr auto b = to_typed_array<int32_t>({4, 5, 6});  // std::array
    constexpr auto c = DeclareArray<int32_t, 7, 8>();  // std::array
    constexpr auto x = ConcatArrays(a, b, c);  // 把3个数组拼接在一起
    static_assert(Equals(x, {1, 2, 3, 4, 5, 6, 7, 8}));
    return 0;
}
```

和之前一样，**ConcatArrays**使用了模板参数来同时兼容原生数组和**std::array**，它甚至可以接受任何编译期确定长度的自定义类型参与拼接。  
**ConcatArrays**函数因为可变参数的语法限制，没有再对**std::initializer_list**字面量进行适配，这导致**std::initializer_list**字面量不能再直接作为参数：  


```cpp
constexpr auto x = ConcatArrays(a, {4, 5, 6});  // 编译错误
```

但是我们有办法规避这个问题：利用前面介绍过的工具把**std::initializer_list**先转成**std::array**就可以了：  


```cpp
constexpr auto x = ConcatArrays(a, to_array({4, 5, 6}));  // OK
```

### 编译期拼接字符串

**std::array**适合用来表示字符串么？回答这个问题前，我们先看看原生数组是否适合表示字符串：  
    
```cpp
char str[] = "abc";  // str数组大小为4，包括结尾的'\0'
```

上面是很常见的写法。由于数组名可退化为指针，**str**可用于各种需要字符串的场合，如传给**cout**打印输出。  

**std::array**作为对原生数组的替代，自然也适合用来表示字符串。有人可能会觉得**std::array**没法直接作为字符串类型使用，不太方便。但实际上只要调用**data**方法，**std::array**就会返回能作为字符串使用的指针：  


```cpp
constexpr auto str = to_array("abc");  // to_array可以将字符串转换为std::array
static_assert(str.size() == 4);
static_assert(Equals(str, "abc"));  // Equals也可以接受字符串字面量
cout << str.data();  // 打印字符串内容
```

由于字符串字面量是**char[]**类型，因此前面所编写的工具函数，都可以将字符串作为输入参数。上面的**Equals**只是其中一个例子。  

那之前写的数组拼接函数**ConcatArrays**能用于拼接字符串么？能，但结果和我们想的有差异：  


```cpp
constexpr auto str = ConcatArrays("abc", "def");
static_assert(str.size() == 8);  // 长度不是7？
static_assert(Equals(str, {'a', 'b', 'c', '\0', 'd', 'e', 'f', '\0'}));
```

因为每个字符串结尾都有**'\0'**结束符，用数组拼接方法把它们拼到一起时，中间的**'\0'**没有被去掉，导致结果字符串被切割为了多个C字符串。  

这个问题解决起来也很容易，只要在拼接数组时把所有数组的最后一个元素（**'\0'**）去掉，并且在返回数组的末尾加上**'\0'**就可以了。下面的代码实现了字符串拼接功能，非类型参数**E**是字符串的结束符，通常为**'\0'**，但是也允许定制。我们甚至可以利用它来拼接结束符为其他值的对象，比如消息、报文等。  


```cpp
// 最后一个字符，放入结束符
template<auto E>
constexpr auto PickChar(size_t i)
{
    return E;
}

template<auto E, typename P, typename... T>
constexpr auto PickChar(size_t i, const P& p, const T&... arr)
{
    if (i < (size(p) - 1)) {
        if (p[i] == E) {  // 结束符不允许出现在字符串中间
            throw "terminator in the middle";
        }
        return p[i];
    }
    if (p[size(p) - 1] != E) {  // 结束符必须是最后一个字符
        throw "terminator not at end";
    }
    return PickChar<E>(i - (size(p) - 1), arr...);
}

template<typename... T, auto E = '\0'>
constexpr auto ConcatStrings(const T&... str)
{
    return GenerateArray<TotalLength(str...) - sizeof...(T) + 1>([&str...](size_t i) { 
                return PickChar<E>(i, str...);
            });
}

int main()
{
    constexpr char a[] = "I ";  // 原生数组形式的字符串
    constexpr auto b = to_array("love ");  // std::array形式的字符串
    constexpr auto str = ConcatStrings(a, b, "C++");  // 拼接 数组 + std::array + 字符串字面量
    static_assert(Equals(str, "I love C++"));
    return 0;
}
```

这段代码中用了两个**throw**，这是为了校验输入的参数是否都为合法的字符串，即：字符串长度=容器长度-1。如果不符合该条件，会导致拼接结果的长度计算错误。  
当编译期的计算抛出异常时，只会出现编译错误，因此只要不在运行时调用**ConcatStrings**，这两个**throw**语句不会有更多影响。  
但因为这个校验的存在，强烈不建议在运行期调用**ConcatStrings**做拼接，何况运行期也没必要用这种方法——**std::string**的加法操作它不香么？  

有人会想：能否在编译期计算字符串的实际长度，而不是用容器的长度呢？这个方法看似可行，定义一个编译期计算字符串长度的函数确实很容易：  


```cpp
template<typename T, auto E = '\0'>
constexpr size_t StrLen(const T& str) noexcept
{
    size_t i = 0;
    while (str[i] != E) {
        ++i;
    }
    return i;
}

constexpr const char* g_str = "abc";

int main()
{
    // 利用StrLen把一个字符串按实际长度转成std::array
    constexpr auto str = SubArray<StrLen(g_str) + 1>(g_str, 0);
    static_assert(Equals(str, "abc"));
    return 0;
}
```

但是，一旦你试图把**StrLen**放到**ConcatStrings**的内部去声明数组长度，就会产生问题：C++的**constexpr**机制要求只有在能看到输入参数的**constexpr**属性的地方，才允许**StrLen**的返回结果确定为**constexpr**。而在函数内部时，看到的参数类型并不是**constexpr**。  

当然我们可以变通一下，做出一些有趣的工具，比如使用万恶的宏：  


```cpp
// 把一个字符串按实际长度转成std::array
#define StrToArray(x) SubArray<StrLen(x) + 1>(x, 0)
constexpr const char* g_str = "abc";

int main()
{
    // 使用宏，可以让constexpr指针类型也参与编译期字符串的拼接
    constexpr auto str = ConcatStrings(StrToArray(g_str), "def");
    static_assert(Equals(str, "abcdef"));
    return 0;
}
```

使用宏以后，**ConcatStrings**连编译期不确定大小的指针类型都可以间接作为输入了[3]。如果你狠得下心使用变参宏，甚至可以定义出按实际字符串长度计算结果数组长度的更通用拼接函数。但我严重怀疑这种需求的必要性——毕竟我们只是做编译期的拼接，而编译期的字符串不应该会有结束符位置不在末尾的场景。  

看到这里的人，或多或少该佩服一下**std::array**的强大了。上面这些编译期操作，用原生数组很难完成吧？  

### 展望C++20——打破更多的枷锁

我在文章中说了多少次“至少在C++20之前如此”？不记得了，但是能确定的是：C++20会带来很多美好的东西：**std::array**会有**constexpr**版本的比较运算符；函数可以用[consteval](https://en.cppreference.com/w/cpp/language/consteval)限定只在编译期调用；模板非类型参数允许更多的类型；STL容器对象可以作为**constexpr**常量……所有这一切，都只是C++20的minor更新而已，在绝大多数的特性介绍中，它们连提都不会被提到！  

可想而知，用上C++20以后，编程会发生多大的变化。那时我们再来找找更多有趣的用法。  

### 尾注

[1] **to_array**定义了两个版本，分别以左值引用和右值引用作为参数类型。按照C++11的最优实践，这样的函数本应该只定义一个版本并且使用完美转发。但是**to_array**的场景如果用万能引用会带来一个问题：C++禁止**std::initializer_list**字面量**{...}**被推导为模板类型参数，完美转发方案会导致**std::initializer_list**字面量不能作为**to_array**的入参。在后面内容中我们会看到多次这个限制所带来的影响。  
[2] C++20加入了[consteval](https://en.cppreference.com/w/cpp/language/consteval)修饰符，可以指定函数只允许在编译期调用。  
[3] 需要注意的是：**constexpr**用于修饰指针时，表示的是指针本身为常量（而不是其指向的对象）。和**const**不同，**constexpr**并不允许放在类型声明表达式的中间。因此如果要在编译期计算一个**constexpr**指针指向的字符串长度，这个字符串必须位于静态数据区里，不能位于栈或者堆上（否则其地址无法在编译期确定）。
