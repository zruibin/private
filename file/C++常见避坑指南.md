 
<!--BEGIN_DATA
{
    "create_date": "2024-02-27 18:00", 
    "modify_date": "2024-02-27 18:00", 
    "is_top": "0", 
    "summary": "C++常见避坑指南", 
    "tags": "C/C++", 
    "file_name": "C++常见避坑指南.md"
}
END_DATA-->

#### <p>原文出处：<a href='https://mp.weixin.qq.com/s/ivmOl-qGALnHEVbwKANiug' target='blank'>C++常见避坑指南</a></p>

作者：gouglegou

> C++ 从入门到放弃？本文主要总结了在C++开发或review过程中常见易出错点做了归纳总结，希望借此能增进大家对C++的了解，减少编程出错，提升工作效率，也可以作为C++开发的避坑攻略。

## 空指针调用成员函数会crash？？

当调用一个空指针所指向的类的成员函数时，大多数人的反应都是程序会crash。空指针并不指向任何有效的内存地址，所以在调用成员函数时会尝试访问一个不存在的内存地址，从而导致程序崩溃。

事实上有点出乎意料，先来看段代码：

```cpp
class MyClass {  
public:  
    static void Test_Func1() {  
        cout << "Handle Test_Func1!" << endl;  
    }  
    void Test_Func2() {  
        cout << "Handle Test_Func2!" << endl;  
    }  
    void Test_Func3() {  
        cout << "Handle Test_Func3! value:" << value << endl;  
    }  
    virtual void Test_Func4() {  
        cout << "Handle Test_Func4!" << endl;  
    }

    int value = 0;  
};  

int main() {  
    MyClass* ptr = nullptr;  
    ptr->Test_Func1(); // ok, print Handle Test_Func1!  
    ptr->Test_Func2(); // ok, print Handle Test_Func2!  
    ptr->Test_Func3(); // crash  
    ptr->Test_Func4(); // crash  return 0;  
}  
```

上面例子中，空指针对`Test_Func1`和`Test_Func2`的调用正常，对`Test_Func3`和`Test_Func4`的调用会crash。可能很多人反应都会crash，实际上并没有，这是为啥？

类的成员函数并不与具体对象绑定，所有的对象共用同一份成员函数体，当程序被编译后，成员函数的地址即已确定，这份共有的成员函数体之所以能够把不同对象的数据区分开来，靠的是隐式传递给成员函数的this指针，成员函数中对成员变量的访问都是转化成`this->数据成员`的方式。因此，从这一角度说，成员函数与普通函数一样，只是多了this指针。而类的静态成员函数只能访问静态成员变量，不能访问非静态成员变量，所以静态成员函数不需要this指针作为隐式参数。

因此，`Test_Func1`是静态成员函数，不需要this指针，所以即使ptr是空指针，也不影响对`Test_Fun1`的正常调用。`Test_Fun2`虽然需要传递隐式指针，但是函数体中并没有使用到这个隐式指针，所以ptr为空也不影响对`Test_Fun2`的正常调用。`Test_Fun3`就不一样了，因为函数中使用到了非静态
的成员变量，对value的调用被转化成`this->value`,也就是`ptr->value`,而ptr是空指针，因此会crash。`Test_Fun4`是虚函数，有虚函数的类会有一个成员变量，即虚表指针，当调用虚函数时，会使用虚表指针，对虚表指针的使用也是通过隐式指针使用的，因此`Test_Fun4`的调用也会crash。

同理，以下`std::shared_ptr`的调用也是如此，日常开发需要注意，记得加上判空。

```cpp
std::shared_ptr<UrlHandler> url_handler;  
...  
if(url_handler->IsUrlNeedHandle(data)) {  
    url_handler->HandleUrl(param);  
}  
```

## 字符串相关

### 字符串查找

对字符串进行处理是一个很常见的业务场景，其中字符串查找也是非常常见的，但是用的不好也是会存在各种坑。常见的字符串查找方法有：`std::string::find、std::string::find_first_of、std::string::find_first_not_of、std::string::find_last_of`，各位C++ Engineer都能熟练使用了吗？先来段代码瞧瞧：

```cpp
bool IsBlacklistDllFromSrv(const std::string& dll_name) {  
    try {  
        std::string target_str = dll_name;  
        std::transform(target_str.begin(), target_str.end(), target_str.begin(), ::tolower);  
        if (dll_blacklist_from_srv.find(target_str) != std::string::npos) {  
            return true;  
        }  
    }  
    catch (...) {  
    }  
    return false;  
}
```

上面这段代码，看下来没啥问题的样子。但是仔细看下来，就会发现字符串比对这里逻辑不够严谨，存在很大的漏洞。std::string::find只是用来在字符串中查找指定的子字符串，只要包含该子串就符合，如果`dll_blacklist_from_srv = "abcd.dll;hhhh.dll;test.dll"`是这样的字符串，传入d.dll、hh.dll、dll;test.dll也会命中逻辑，明显是不太符合预期的。

这里顺带回顾下C++ std::string常见的字符串查找的方法：

`std::string::find` 用于在字符串中查找指定的子字符串。如果找到了子串，则返回子串的起始位置,否则返回std::string::npos。用于各种字符串操作，例如判断子字符串是否存在、获取子字符串的位置等。通过结合其他成员函数和算法，可以实现更复杂的字符串处理逻辑。

`std::string::find_first_of` 用于查找字符串中第一个与指定字符集合中的任意字符匹配的字符，并返回其位置。可用来检查字符串中是否包含指定的某些字符或者查找字符串中第一个出现的特定字符

`std::string::find_first_not_of` 用于查找字符串中第一个不与指定字符集合中的任何字符匹配的字符，并返回其位置。

`std::string::find_last_of` 用于查找字符串中最后一个与指定字符集合中的任意字符匹配的字符，并返回其位置。可以用来检查字符串中是否包含指定的某些字符，或者查找字符串中最后一个出现的特定字符

`std::string::find_last_not_of` 用于查找字符串中最后一个不与指定字符集合中的任何字符匹配的字符，并返回其位置。

除了以上几个方法外，还有查找满足指定条件的元素`std::find_if`，

`std::find_if` 是 C++ 标准库中的一个算法函数，用于在指定范围内查找第一个满足指定条件的元素，并返回其迭代器。需要注意的是，使用`std::find_if` 函数时需要提供一个可调用对象（例如 lambda 表达式或函数对象），用于指定查找条件。

```cpp
std::vector<int> vec = {1, 2, 3, 4, 5};  
auto it = std::find_if(vec.begin(), vec.end(), [](int x) { return x % 2 == 0; });  
if (it != vec.end()) {  
    std::cout << "Found even number: " << *it << std::endl;  
}   
```

此外，在业务开发有时候也会遇到需要C++ boost库支持的`starts_with`、`ends_with`。如果用C++标准库来实现，常规编写方法可如下：

```cpp
bool starts_with(const std::string& str, const std::string& prefix) {  
    return str.compare(0, prefix.length(), prefix) == 0;  
}

bool ends_with(const std::string& str, const std::string& suffix) {  
    if (str.length() < suffix.length()) {  
        return false;  
    } else {  
        return str.compare(str.length() - suffix.length(), suffix.length(), suffix) == 0;  
    }  
}  
```

以上代码中，`starts_with` 函数和 `ends_with` 函数分别用于检查字符串的前缀和后缀。两个函数内部都使用了std::string::compare 方法来比较字符串的子串和指定的前缀或后缀是否相等。如果相等，则说明字符串满足条件，返回 true；否则返回false。

### std::string与std::wstring转换

对字符串进行处理是一个很常见的业务场景，尤其是C++客户端开发，我们经常需要在窄字符串std::string与宽字符串std::wstring之间进行转换，有时候一不小心就会出现各种中文乱码。还有就是一提到窄字符串与宽字符串互转以及时不时出现的中文乱码，很多人就犯晕。

在 C++ 中，std::string和std::wstring之间的转换涉及到字符编码的转换。如果在转换过程中出现乱码，可能是由于字符编码不匹配导致的。要正确地进行std::string 和 std::wstring之间的转换，需要确保源字符串的字符编码和目标字符串的字符编码一致，避免C++中的字符串处理乱码，可以使用Unicode编码(如UTF-8、UTF-16或UTF-32)来存储和处理字符串。

我们想要处理或解析一些Unicode数据，例如从Windows REG文件读取，使用std::wstring变量更能方便的处理它们。例如：std::wstring ws=L"中国a"(6个八位字节内存：0x4E2D0x56FD 0x0061)，我们可以使用ws[0]获取字符“中”，使用ws[1]获取字符“国”，使用ws[2]获取字符“国”获取字符 'a' 等，这个时候如果使用std::string，ws[0]拿出来的就是乱码。

此外还受代码页编码的影响(比如VS可以通过文件->高级保存选项->编码 来更改当前代码页的编码)。

下面是一些示例代码，演示了如何进行正确的转换，针对Windows平台，官方提供了相应的系统Api(MultiByteToWideChar)：

```cpp
std::wstring Utf8ToUnicode(const std::string& str) {  
    int len = str.length();  
    if (0 == len)  
        return L"";  
    int nLength = MultiByteToWideChar(CP_UTF8, 0, str.c_str(), len, 0, 0);  
    std::wstring buf(nLength + 1, L'\0');  
    MultiByteToWideChar(CP_UTF8, 0, str.c_str(), len, &buf[0], nLength);  
    buf.resize(wcslen(buf.c_str()));  
    return buf;  
}  

std::string UnicodeToUtf8(const std::wstring& wstr) {  
    if (wstr.empty()) {  
        return std::string();  
    }  
    int size_needed = WideCharToMultiByte(CP_UTF8, 0, &wstr[0], static_cast<int>(wstr.size()), nullptr, 0, nullptr, nullptr);  
    std::string str_to(size_needed, 0);  
    WideCharToMultiByte(CP_UTF8, 0, &wstr[0], static_cast<int>(wstr.size()), &str_to[0], size_needed, nullptr, nullptr);  
    return str_to;  
}  
```

如果使用C++标准库来实现，常规写法可以参考下面：

```cpp
#include <iostream>  
#include <string>  
#include <locale>  
#include <codecvt>  

// 从窄字符串到宽字符串的转换  
std::wstring narrowToWide(const std::string& narrowStr) {  
    try {  
        std::wstring_convert<std::codecvt_utf8<wchar_t>> converter;  
        return converter.from_bytes(narrowStr);  
    } catch (...) { // 如果传进来的字符串不是utf8编码的，这里会抛出std::range_error异常  
        return {};  
    }  
}  

// 从宽字符串到窄字符串的转换  
std::string wideToNarrow(const std::wstring& wideStr) {  
    try {  
        std::wstring_convert<std::codecvt_utf8<wchar_t>> converter;  
        return converter.to_bytes(wideStr);  
    } catch (...) {  
        return {};  
    }  
}  

//utf8字符串转成string  
std::string utf8ToString(const char8_t* str) {  
    std::wstring_convert<std::codecvt_utf8_utf16<char16_t>, char16_t> convert;  
    std::u16string u16str = convert.from_bytes(  
        reinterpret_cast<const char*>(str),  
        reinterpret_cast<const char*>(str + std::char_traits<char8_t>::length(str)));  
    return std::wstring_convert<std::codecvt_utf8_utf16<char16_t>, char16_t>{}.to_bytes(u16str);  
} 

int main(){  
    {  
        std::wstring wideStr = L"Hello, 你好!";  
        std::string narrowStr = wideToNarrow(wideStr);  
        std::wstring convertedWideStr = narrowToWide(narrowStr);  
    } 
    {  
        //std::string narrowStr = "Hello, 你好!"; (1)  
        std::string narrowStr = utf8ToString(u8"Hello, 你好!"); //(2)  
        std::wstring wideStr = narrowToWide(narrowStr);  
        std::string convertedNarrowStr = wideToNarrow(wideStr);  
    }      
    return 0;  
}  
```

(1)首先std::string不理解编码，在CPP官方手册里面也解释了，std::string处理字节的方式与所使用的编码无关，如果用于处理多字节或可变长
度字符的序列(例如 UTF-8)，则此类的所有成员以及它的迭代器仍然以字节(而不是实际的编码字符)为单位进行操作，如果用来处理包含中文的字符串就可能出现乱码。这里直接将包含中文的字符串赋值给std::string，无法保证是UTF8编码，进行转换时会提示std::range_error异常；此外，std::wstring是会理解编码的，其中的字符串通常使用 UTF-16 或 UTF-32 编码，这取决于操作系统和编译器的实现。

(2)这里由于使用u8""构造了UTF8编码字符串，但是不能直接用来构造std::string，所以进行转了下utf8ToString;

### 全局静态对象

大家有没有在工程代码中发现有下面这种写法，将常量字符串声明为静态全局的。

```cpp
static const std::string kVal="hahahhaha";

static const std::wstring kxxConfigVal="hahahhaha";
```

**优点**：

可读性好：使用有意义的变量名，可以清晰地表达变量的含义和用途，提高了代码的可读性。

安全性高：由于使用了 const 关键字，这个字符串变量是不可修改的，可以避免意外的修改和安全问题。

生命周期长：静态变量的生命周期从程序启动到结束，不受函数的调用和返回影响。

**缺点**：

构造开销：静态变量的初始化发生在程序启动时也就是执行main()之前，会增加程序启动的时间和资源消耗。大量的这种静态全局对象，会拖慢程序启动速度

静态变量共享：静态变量在整个程序中只有一份实例，可能会导致全局状态共享和难以调试的问题。

此外，静态变量的初始化顺序可能会受到编译单元(源文件)中其他静态变量初始化顺序的影响，因此在跨编译单元的情况下，静态变量的初始化顺序可能是不确定的。

**在实际编程中，还是不太建议使用全局静态对象，建议的写法：**

要声明全局的常量字符串，可以使用 const 关键字和 extern 关键字的组合:

```cpp
// constants.h  
extern const char* GLOBAL_STRING;  

// constants.cpp  
#include "constants.h"  
const char* GLOBAL_STRING = "Hello, world!";  
constexpr char* kVal="hahhahah";
```

使用 constexpr 关键字来声明全局的常量字符串:  

```cpp
// constants.h  
constexpr const char* GLOBAL_STRING = "Hello, world!";  
```

## 迭代器删除

在处理缓存时，容器元素的增删查改是很常见的，通过迭代器去删除容器(`vector/map/set/unordered_map/list`)元素也是常有的，但这其中使用不当也会存在很多坑。

```cpp
std::vector<int> numbers = { 88, 101, 56, 203, 72, 135 };  

auto it = std::find_if(numbers.begin(), numbers.end(), [](int num) {  
    return num > 100 && num % 2 != 0;  
});  

vec.erase(it);  
```

上面代码，查找std::vector中大于 100 并且为奇数的整数并将其删除。`std::find_if` 将从容器的开头开始查找，直到找到满足条件的元素或者
遍历完整个容器，并返回迭代器it，然后去删除该元素。但是这里没有判断it为空的情况，直接就erase了，如果erase一个空的迭代器会引发crash。很多新手程序员会犯这样的错误，随时判空是个不错的习惯。

删除元素不得不讲下`std::remove` 和 `std::remove_if`，用于从容器中移除指定的元素，函数会将符合条件的元素移动到容器的末尾，并返回指向新的末尾位置之后的迭代器，最后使用容器的erase来擦除从新的末尾位置开始的元素。

```cpp
std::vector<std::string> vecs = { "A", "", "B", "", "C", "hhhhh", "D" };  
vecs.erase(std::remove(vecs.begin(), vecs.end(), ""), vecs.end());  
// 移除所有偶数元素  
vec.erase(std::remove_if(vec.begin(), vec.end(), [](int x) { return x % 2 == 0; }), vec.end());  
```

这里的erase不用判空，其内部实现已经有判空处理。

```cpp
_CONSTEXPR20 iterator erase(const_iterator _First, const_iterator _Last) noexcept(  
        is_nothrow_move_assignable_v<value_type>) /* strengthened */ {  
    const pointer _Firstptr = _First._Ptr;  
    const pointer _Lastptr  = _Last._Ptr;  
    auto& _My_data          = _Mypair._Myval2;  
    pointer& _Mylast        = _My_data._Mylast;  
    // ....  

    if (_Firstptr != _Lastptr) { // something to do, invalidate iterators  
        _Orphan_range(_Firstptr, _Mylast);  
        const pointer _Newlast = _Move_unchecked(_Lastptr, _Mylast, _Firstptr);  
        _Destroy_range(_Newlast, _Mylast, _Getal());  
        _Mylast = _Newlast;  
    }  
    return iterator(_Firstptr, _STD addressof(_My_data));  
}  
```

此外，STL容器的删除也要小心迭代器失效，先来看个vector、list、map删除的例子：

```cpp
// vector、list、map遍历并删除偶数元素  
std::vector<int> elements = { 1, 2, 3, 4, 5 };  
for (auto it = elements.begin(); it != elements.end();) {  
    if (*it % 2 == 0) {  
        elements.erase(it++);  
    } else {  
        it++;  
    }  
} 
// Error  

std::list<int> cont{ 88, 101, 56, 203, 72, 135 };  
for (auto it = cont.begin(); it != cont.end(); ) {  
    if (*it % 2 == 0) {  
        cont.erase(it++);  
    } else {  
        it++;  
    }  
}  
// Ok  

std::map<int, std::string> myMap = { {1, "one"}, {2, "two"}, {3, "three"}, {4, "four"}, {5, "five"} };  
// 遍历并删除键值对，删除键为偶数的元素  
for (auto it = myMap.begin(); it != myMap.end(); ) {  
    if (it->first % 2 == 0) {  
        myMap.erase(it++);  
    } else {  
        it++;  
    }  
}  
// Ok  
```

上面几类容器同样的遍历删除元素，只有vector报错crash了，map和list都能正常运行。其实vector调用erase()方法后，当前位置到容器末尾元素的所有迭代器全部失效了，以至于不能再使用。

迭代器的失效问题：对容器的操作影响了元素的存放位置，称为迭代器失效。迭代器失效的情况：

● 当容器调用erase()方法后，当前位置到容器末尾元素的所有迭代器全部失效。

● 当容器调用insert()方法后，当前位置到容器末尾元素的所有迭代器全部失效。

● 如果容器扩容，在其他地方重新又开辟了一块内存，原来容器底层的内存上所保存的迭代器全都失效。

迭代器失效有三种情况，由于底层的存储数据结构，分三种情况：

**序列式迭代器失效**，序列式容器(std::vector和std::deque)，其对应的数据结构分配在连续的内存中，对其中的迭代器进行insert和erase操作都会使得删除点和插入点之后的元素挪位置，进而导致插入点和删除掉之后的迭代器全部失效。可以利用erase迭代器接口返回的是下一个有效的迭代器。

**链表式迭代器失效**，链表式容器(std::list)使用链表进行数据存储，插入或者删除只会对当前的节点造成影响，不会影响其他的迭代器。可以利用erase迭代器接口返回的是下一个有效的迭代器，或者将当前的迭代器指向下一个erase(iter++)。

**关联式迭代器失效**，关联式容器，如map, set,multimap,multiset等，使用红黑树进行数据存储，删除当前的迭代器，仅会使当前的迭代器失效。erase迭代器的返回值为 void(C++11之前)，可以采用erase(iter++)的方式进行删除。值得一提的是，在最新的C++11标准中，已经新增了一个map::erase函数执行后会返回下一个元素的iterator，因此可以使用erase的返回值获取下一个有效的迭代器。

在实现上有两种模板，其一是通过 erase 获得下一个有效的 iterator，使用于序列式迭代器和链表式迭代器(C++11开始关联式迭代器也可以使用)

```cpp
for (auto it = elements.begin(); it != elements.end(); ) {  
    if (ShouldDelete(*it)) {  
        it = elements.erase(it); // erase删除元素，返回下一个迭代器  
    } else {  
        it++;  
    }  
}  
```

其二是，递增当前迭代器，适用于链表式迭代器和关联式迭代器。

```cpp
for (auto it = elements.begin(); it != elements.end(); ) {  
    if (ShouldDelete(*it)) {  
        elements.erase(it++);   
    } else {  
        it++;  
    }  
}  
```

## 对象拷贝

在众多编程语言中C++的优势之一便是其高性能，可是开发者代码写得不好(比如：很多不必要的对象拷贝)，直接会影响到代码性能，接下来就讲几个常见的会引起无意义拷贝的场景。

**for循环：**

```cpp
std::vector<std::string> vec;  
for(std::string s: vec) {  
}  
// or  
for(auto s: vec) {  
}  
```

这里每个string都会被拷贝一次，为避免无意义拷贝可以将其改成：

`for(const auto& s: vec)` 或者 `for (const std::string& s: vec)`

**lambda捕获**

```cpp
// 获取对应消息类型的内容  
std::string GetRichTextMessageXxxContent(const std::shared_ptr<model::Message>& message,  
    const std::map<model::MessageId, std::map<model::UserId, std::string>>& related_user_names,  
    const model::UserId& login_userid,  
    bool for_message_index) {  
    // ...  
    // 解析RichText内容  
    return DecodeRichTextMessage(message, [=](uint32_t item_type, const std::string& data) {  
    std::string output_text;  
    // ...  
    return output_text;  
    });  
}  
```

上述代码用于解析获取文本消息内容，涉及到富文本消息的解析和一些逻辑的计算，高频调用，他在解析RichText内容的callback中直接简单粗暴的按值捕获了所有变量，将所有变量都拷贝了一份，这里造成不必要的性能损耗，尤其上面那个std::map。这里可以改成按引用来捕获，规避不必要的拷贝。

lambda函数在捕获时会将被捕获对象拷贝，如果捕获的对象很多或者很占内存，将会影响整体的性能，可以根据需求使用引用捕获或者按需捕获：

`auto func = &a{};`

`auto func = a = std::move(a){};` (限C++14以后)

**隐式类型转换**

```cpp
std::map<int, std::string> myMap = {{1, "One"}, {2, "Two"}, {3, "Three"}};  
for (const std::pair<int, std::string>& pair : myMap) {  
    //...  
}  
```

这里在遍历关联容器时，看着是const引用的，心想着不会发生拷贝，但是因为类型错了还是会发生拷贝，std::map 中的键值对是以 `std::pair<const Key, T>` 的形式存储的，其中key是常量。因此，在每次迭代时，会将当前键值对拷贝到临时变量中。在处理大型容器或频繁遍历时，这种拷贝操作可能会产生一些性能开销，所以在遍历时推荐使用`const auto&`，也可以使用结构化绑定：`for(const auto& [key, value]: map){}` (限C++17后)

**函数返回值优化**

RVO是Return Value Optimization的缩写，即返回值优化，NRVO就是具名的返回值优化，为RVO的一个变种，此特性从C++11开始支持。为了更清晰的了解编译器的行为，这里实现了构造/析构及拷贝构造、赋值操作函数，如下:

```cpp
class Widget {  
public:  
    Widget() {  
    std::cout << "Widget: Constructor" << std::endl;  
    }  
    Widget(const Widget& other) {  
        name = other.name;  
        std::cout << "Widget: Copy construct" << std::endl;  
    }  
    Widget& operator=(const Widget& other) {  
        std::cout << "Widget: Assignment construct" << std::endl;  
        name = other.name;  
        return *this;  
    }  
    ~Widget() {  
        std::cout << "Widget: Destructor" << std::endl;  
    }  
public:  
    std::string name;  
}; 

Widget GetMyWidget(int v) {  
    Widget w;  
    if (v % 2 == 0) {  
        w.name = 1;  
        return w;  
    } else {  
        return w;  
    }  
}  

int main(){  
    const Widget& w = GetMyWidget(2); // (1)  
    Widget w = GetMyWidget(2); // (2)  
    GetMyWidget(2); // (3)  
    return 0;  
}  
```

运行上面代码，跑出的结果：

```cpp
未优化：(msvc 2022, C++14)  

Widget: Constructor  
Widget: Copy construct  
Widget: Destructor  
Widget: Destructor  

优化后：  

Widget: Constructor  
Widget: Destructor  
```

针对上面(1)(2)(3)的调用，我之前也是有点迷惑，以为要减少拷贝必须得用常引用来接，但是发现编译器进行返回值优化后(1)(2)(3)运行结果都是一样的，也就是日常开发中，针对函数中返回的临时对象，可以用对象的常引用或者新的一个对象来接，最后的影响其实可以忽略不计的。不过个人还是倾向于对象的常引用来接，一是出于没有优化时(编译器不支持或者不满足RVO条件)可以减少一次拷贝，二是如果返回的是对象的引用时可以避免拷贝。但是也要注意不要返回临时对象的引用。

```cpp
// pb协议接口实现  
inline const ::PB::XXXConfig& XXConfigRsp::config() const {  
    //...  
}  

void XXSettingView::SetSettingInfo(const PB::XXConfigRsp& rsp){  
    const auto config = rsp.config(); // 内部返回的是对象的引用，这里没有引用来接导致不必要的拷贝  
}  
```

当遇到上面这种返回对象的引用时，外部最好也是用对象的引用来接，减少不必要的拷贝。

此外，如果Widget的拷贝赋值操作比较耗时，通常在使用函数返回这个类的一个对象时也是会有一定的讲究的。

```cpp
// style 1  
Widget func(Args param);  
// style 2  
bool func(Widget* ptr, Args param);  
```

上面的两种方式都能达到同样的目的，但直观上的使用体验的差别也是非常明显的：

> style 1只需要一行代码，而style 2需要两行代码，可能大多数人直接无脑style 1

```cpp
// style 1  
Widget obj = func(params);  

// style 2  
Widget obj;  
func(&obj, params);  
```

但是，能达到同样的目的，消耗的成本却未必是一样的，这取决于多个因素，比如编译器支持的特性、C++语言标准的规范强制性等等。

看起来style 2虽然需要写两行代码，但函数内部的成本却是确定的，只会取决于你当前的编译器，外部即使采用不同的编译器进行函数调用，也并不会有多余的时间开销和稳定性问题。使用style 1时，较复杂的函数实现可能并不会如你期望的使用RVO优化，如果编译器进行RVO优化，使用style 1无疑是比较好的选择。利用好编译器RVO特性，也是能为程序带来一定的性能提升。

**函数传参使用对象的引用**

effective C++中也提到了：以pass-by-reference-to-const替换pass-by-value

指在函数参数传递时，将原本使用"pass-by-value"(按值传递)的方式改为使用 "pass-by-reference-to-const"(按常量引用传递)的方式。

在 "pass-by-value" 中，函数参数会创建一个副本，而在 "pass-by-reference-to-const" 中，函数参数会成为原始对象的一个引用，且为了避免修改原始对象，使用了常量引用。

通过使用 "pass-by-reference-to-const"，可以避免在函数调用时进行对象的拷贝操作，从而提高程序的性能和效率；还可以避免对象被切割问题：当一个派生类对象以传值的方式传入一个函数，但是该函数的形参是基类，则只会调用基类的构造函数构造基类部分，派生类的新特性将会被切割。此外，使用常量引用还可以确保函数内部不会意外地修改原始对象的值。

## std::shared_ptr线程安全

对`shared_ptr`相信大家都很熟悉，但是一提到是否线程安全，可能很多人心里就没底了，借助本节，对`shared_ptr`线程安全方面的问题进行分析和解释。`shared_ptr`的线程安全问题主要有两种：

1. 引用计数的加减操作是否线程安全; 
2. `shared_ptr`修改指向时是否线程安全。

**引用计数**

`shared_ptr`中有两个指针，一个指向所管理数据的地址，另一个指向执行控制块的地址。

执行控制块包括对关联资源的引用计数以及弱引用计数等。在前面我们提到`shared_ptr`支持跨线程操作，引用计数变量是存储在堆上的，那么在多线程的情况下，指向同一数据的多个`shared_ptr`在进行计数的++或--时是否线程安全呢？

引用计数在STL中的定义如下：

```cpp
_Atomic_word _M_use_count;   // #shared  
_Atomic_word _M_weak_count;  // #weak + (#shared != 0)  
```

当对`shared_ptr`进行拷贝时，引入计数增加，实现如下：

```cpp
 template <>  
 inline bool _Sp_counted_base<_S_atomic>::_M_add_ref_lock_nothrow() noexcept {  
     // Perform lock-free add-if-not-zero operation.  
     _Atomic_word __count = _M_get_use_count();  
     do {  
         if (__count == 0) return false;  
         // Replace the current counter value with the old value + 1, as  
         // long as it's not changed meanwhile.  
     } while (!__atomic_compare_exchange_n(&_M_use_count, &__count, __count + 1, true, __ATOMIC_ACQ_REL,  
                                           __ATOMIC_RELAXED));  
     return true;  
 } 

 template <>  
 inline void _Sp_counted_base<_S_single>::_M_add_ref_copy() {  
     ++_M_use_count;  
 }  
```

对引用计数的增加主要有以下2种方法：`_M_add_ref_copy`函数，对`_M_use_count + 1`，是原子操作。`_M_add_ref_lock`函数，是调用`__atomic_compare_exchange_n`实现的，主要逻辑仍然是`_M_use_count + 1`，而该函数是线程安全的，和`_M_add_ref_copy`的区别是对不同`_Lock_policy`有不同的实现，包含直接加、原子操作加、加锁。

因此我们可以得出结论：在多线程环境下，管理同一个数据的`shared_ptr`在进行计数的增加或减少的时候是线程安全的，这是一波原子操作。

**修改指向**

修改指向分为操作同一个`shared_ptr`对象和操作不同的`shared_ptr`对象两种。

**多线程代码操作的是同一个shared_ptr的对象**

比如std::thread的回调函数，是一个lambda表达式，其中引用捕获了一个`shared_ptr`对象

```cpp
shared_ptr<A> sp1 = make_shared<A>();  
std::thread td([&sp1] () {....});  
```

又或者通过回调函数的参数传入的`shared_ptr`对象，参数类型是指针或引用:

指针类型：`void fn(shared_ptr<A>* sp) { ... } std::thread td(fn, &sp1);`

引用类型：`void fn(shared_ptr<A>& sp) { ... } std::thread td(fn, std::ref(sp1));`

当你在多线程回调中修改`shared_ptr`指向的时候，这时候确实不是线程安全的。

```cpp
void fn(shared_ptr<A>& sp) {  
  if (..) {  
      sp = other_sp;  
  } else if (...) {  
      sp = other_sp2;  
  }  
}  
```

`shared _ptr`内数据指针要修改指向，sp原先指向的引用计数的值要减去1，`other_sp`指向的引用计数值要加1。然而这几步操作加起来并不是一个原子操作，如果多个线程都在修改sp的指向的时候，那么有可能会出问题。比如在导致计数在操作-1的时候，其内部的指向已经被其他线程修改过了，引用计数的异常会导致某个管理的对象被提前析构，后续在使用到该数据的时候触发coredump。当然如果你没有修改指向的时候，是没有问题的。也就是：

同一个`shared_ptr`对象被多个线程同时读是安全的

同一个`shared_ptr`对象被多个线程同时读写是不安全的

**多线程代码操作的不是同一个shared_ptr的对象。**

这里指的是管理的数据是同一份，而`shared_ptr`不是同一个对象，比如多线程回调的lambda是按值捕获的对象。

```cpp
std::thread td([sp1] () {....});  
```

或者参数传递的`shared_ptr`是值传递，而非引用：

```cpp
 void fn(shared_ptr<A> sp) {  
     ...  
 }  
 std::thread td(fn, sp1);  
```

这时候每个线程内看到的sp，他们所管理的是同一份数据，用的是同一个引用计数。但是各自是不同的对象，当发生多线程中修改sp指向的操作的时候，是不会出现非预期的异常行为的。也就是说，如下操作是安全的：

```cpp
void fn(shared_ptr<A> sp) {  
  if (..) {  
      sp = other_sp;  
  } else if (...) {  
      sp = other_sp2;  
  }  
}  
```

尽管前面我们提到了如果是按值捕获(或传参)的`shared_ptr`对象，那么该对象是线程安全的，然而话虽如此，但却可能让人误入歧途。因为我们使用`shared_ptr`更多的是操作其中的数据，对齐管理的数据进行读写，尽管在按值捕获的时候`shared_ptr`是线程安全的，我们不需要对此施加额外的同步操作(比如加解锁），但是这并不意味着`shared_ptr`所管理的对象是线程安全的！请注意这是两回事。

最后再来看下std官方手册是怎么讲的：

> All member functions (including copy constructor and copy assignment) can be called by multiple threads on different instances of `shared_ptr` without additional synchronization even if these instances are copies and share ownership of the same object. If multiple threads of execution access the same instance of `shared_ptr` without synchronization and any of those accesses uses a non-const member function of `shared_ptr` then a data race will occur; the `shared_ptr` overloads of atomic functions can be used to prevent the data race.

这段话的意思是，`shared_ptr` 的所有成员函数(包括复制构造函数和复制赋值运算符)都可以由多个线程在不同的 `shared_ptr` 实例上调用，即使这些实例是副本并且共享同一个对象的所有权。如果多个执行线程在没有同步的情况下访问同一个 `shared_ptr` 实例，并且这些访问中的任何一个使用了 `shared_ptr` 的非 const 成员函数，则会发生数据竞争；可以使用`shared_ptr`的原子函数重载来防止数据竞争。

我们可以得到下面的结论：

1、 多线程环境中，对于持有相同裸指针的`std::shared_ptr`实例，所有成员函数的调用都是线程安全的。

a. 当然，对于不同的裸指针的 `std::shared_ptr` 实例，更是线程安全的

b. 这里的 “成员函数” 指的是 `std::shared_ptr` 的成员函数，比如 get ()、reset ()、operrator->()等

2、 多线程环境中，对于同一个`std::shared_ptr`实例，只有访问const的成员函数，才是线程安全的，对于非const成员函数，是非线程安全的，需要加锁访问。

首先来看一下 `std::shared_ptr` 的所有成员函数，只有前3个是 non-const 的，剩余的全是 const 的：

<table><thead><tr style="border-width: 1px 0px 0px;border-right-style: initial;border-bottom-style: initial;border-left-style: initial;border-right-color: initial;border-bottom-color: initial;border-left-color: initial;border-top-style: solid;border-top-color: rgb(204, 204, 204);background-color: white;"><th style="border-top-width: 1px;border-color: rgb(204, 204, 204);text-align: left;background-color: rgb(240, 240, 240);font-size: 14px;min-width: 85px;"><strong style="font-weight: border;color: #3e4753;">成员函数</strong></th><th style="border-top-width: 1px;border-color: rgb(204, 204, 204);text-align: left;background-color: rgb(240, 240, 240);font-size: 14px;min-width: 85px;"><strong style="font-weight: border;color: #3e4753;">是否const</strong></th></tr></thead><tbody style="border-width: 0px;border-style: initial;border-color: initial;"><tr style="border-width: 1px 0px 0px;border-right-style: initial;border-bottom-style: initial;border-left-style: initial;border-right-color: initial;border-bottom-color: initial;border-left-color: initial;border-top-style: solid;border-top-color: rgb(204, 204, 204);background-color: white;"><td style="border-color: rgb(204, 204, 204);font-size: 14px;min-width: 85px;">operator=</td><td style="border-color: rgb(204, 204, 204);font-size: 14px;min-width: 85px;">non-const</td></tr><tr style="border-width: 1px 0px 0px;border-right-style: initial;border-bottom-style: initial;border-left-style: initial;border-right-color: initial;border-bottom-color: initial;border-left-color: initial;border-top-style: solid;border-top-color: rgb(204, 204, 204);background-color: rgb(248, 248, 248);"><td style="border-color: rgb(204, 204, 204);font-size: 14px;min-width: 85px;">reset</td><td style="border-color: rgb(204, 204, 204);font-size: 14px;min-width: 85px;">non-const</td></tr><tr style="border-width: 1px 0px 0px;border-right-style: initial;border-bottom-style: initial;border-left-style: initial;border-right-color: initial;border-bottom-color: initial;border-left-color: initial;border-top-style: solid;border-top-color: rgb(204, 204, 204);background-color: white;"><td style="border-color: rgb(204, 204, 204);font-size: 14px;min-width: 85px;">swap</td><td style="border-color: rgb(204, 204, 204);font-size: 14px;min-width: 85px;">non-const</td></tr><tr style="border-width: 1px 0px 0px;border-right-style: initial;border-bottom-style: initial;border-left-style: initial;border-right-color: initial;border-bottom-color: initial;border-left-color: initial;border-top-style: solid;border-top-color: rgb(204, 204, 204);background-color: rgb(248, 248, 248);"><td style="border-color: rgb(204, 204, 204);font-size: 14px;min-width: 85px;">get</td><td style="border-color: rgb(204, 204, 204);font-size: 14px;min-width: 85px;">const</td></tr><tr style="border-width: 1px 0px 0px;border-right-style: initial;border-bottom-style: initial;border-left-style: initial;border-right-color: initial;border-bottom-color: initial;border-left-color: initial;border-top-style: solid;border-top-color: rgb(204, 204, 204);background-color: white;"><td style="border-color: rgb(204, 204, 204);font-size: 14px;min-width: 85px;">operator、operator-&gt;</td><td style="border-color: rgb(204, 204, 204);font-size: 14px;min-width: 85px;">const</td></tr><tr style="border-width: 1px 0px 0px;border-right-style: initial;border-bottom-style: initial;border-left-style: initial;border-right-color: initial;border-bottom-color: initial;border-left-color: initial;border-top-style: solid;border-top-color: rgb(204, 204, 204);background-color: rgb(248, 248, 248);"><td style="border-color: rgb(204, 204, 204);font-size: 14px;min-width: 85px;">operator</td><td style="border-color: rgb(204, 204, 204);font-size: 14px;min-width: 85px;">const</td></tr><tr style="border-width: 1px 0px 0px;border-right-style: initial;border-bottom-style: initial;border-left-style: initial;border-right-color: initial;border-bottom-color: initial;border-left-color: initial;border-top-style: solid;border-top-color: rgb(204, 204, 204);background-color: white;"><td style="border-color: rgb(204, 204, 204);font-size: 14px;min-width: 85px;">use_count</td><td style="border-color: rgb(204, 204, 204);font-size: 14px;min-width: 85px;">const</td></tr><tr style="border-width: 1px 0px 0px;border-right-style: initial;border-bottom-style: initial;border-left-style: initial;border-right-color: initial;border-bottom-color: initial;border-left-color: initial;border-top-style: solid;border-top-color: rgb(204, 204, 204);background-color: rgb(248, 248, 248);"><td style="border-color: rgb(204, 204, 204);font-size: 14px;min-width: 85px;">operator bool</td><td style="border-color: rgb(204, 204, 204);font-size: 14px;min-width: 85px;">const</td></tr><tr style="border-width: 1px 0px 0px;border-right-style: initial;border-bottom-style: initial;border-left-style: initial;border-right-color: initial;border-bottom-color: initial;border-left-color: initial;border-top-style: solid;border-top-color: rgb(204, 204, 204);background-color: white;"><td style="border-color: rgb(204, 204, 204);font-size: 14px;min-width: 85px;">unique</td><td style="border-color: rgb(204, 204, 204);font-size: 14px;min-width: 85px;">const</td></tr></tbody></table>

讲了这么多，来个栗子实践下：

```cpp
ant::Promise<JsAPIResultCode, CefRefPtr<CefDictionaryValue>>
XXXHandler::OnOpenSelectContactH5(const JsAPIContext& context, std::shared_ptr<RequestType> arguments) {
 ant::Promise<JsAPIResultCode, CefRefPtr<CefDictionaryValue>> promise;
 base::GetUIThread()->PostTask(weak_lambda(this, [this, promise, context, arguments]() {

  auto b_executed_flag = std::make_shared<std::atomic_bool>(false);
  auto ext_param = xx::OpenWebViewWindow::OpenURLExtParam();
  // ...
  // SelectCorpGroupContact jsapi的回调
  ext_param.select_group_contact_callback = [promise, b_executed_flag](
   JsAPIResultCode resCode, CefRefPtr<CefDictionaryValue> res) mutable {
    *b_executed_flag = true;
    base::GetUIThread()->PostTask([promise, resCode, res]() {
     promise.resolve(resCode, res);
     });
  };
  // 窗口关闭回调
  ext_param.dismiss_callback = [promise, b_executed_flag]() {
   if (*b_executed_flag) {
    return;
   }
   promise.resolve(JSAPI_RESULT_CANCEL, CefDictionaryValue::Create());
  };
  // ...
  xx::OpenWebViewWindow::OpenURL(nullptr, url, false, ext_param);
 }));
 return promise;
}
```

该段代码场景是一个Jsapi接口，在接口中打开另一个webview的选人窗口，选人窗口操作后或者关闭时都需要回调下，将结果返回jsapi。选人完毕确认后会回调`select_group_contact_callback`，同时关闭webview窗口还会回调`dismiss_callback`，这俩回调里面都会回包，这里还涉及多线程调用。这俩回调只能调用一个，为了能简单达到这种效果，作者用`std::shared_ptrstd::atomic_bool b_executed_flag`来处理多线程同步，如果一个回调已执行就标记下，`shared_ptr`本身对引用计数的操作是线程安全的，通过原子变量`std::atomic_bool`来保证其管理的对象的线程安全。

## std::map

```cpp
// 定义数据缓存类  
class DataCache {  
private:  
  std::map<std::string, std::string> cache;  
public:  
  void addData(const std::string& key, const std::string& value) {  
      cache[key] = value;  
  }  
  std::string getData(const std::string& key) {  
      return cache[key];  
  }  
};  
```

在上述示例中，简单定义了个数据缓存类，使用 std::map作为数据缓存，然后提供addData添加数据到缓存，getData从map缓存中获取数据。一切看起来毫无违和感，代码跑起来也没什么问题，但是如果使用没有缓存的key去getData, 发现会往缓存里面新插入一条value为默认值的记录。

需要注意的是，如果我们使用 `[]` 运算符访问一个不存在的键，并且在插入新键值对时没有指定默认值，那么新键值对的值将是未定义的。因此，在使用 `[]` 运算符访问 std::map 中的元素时，应该始终确保该键已经存在或者在插入新键值对时指定了默认值。

```cpp
void addData(const std::string& key, const std::string& value) {  
  if(key.empty()) return;  
  cache[key] = value;  
}  

std::string getData(const std::string& key) {  
  const auto iter = cache.find(key);  
  return iter != cache.end() ? iter->second : "";  
}  
```

## sizeof & strlen

相信大家都有过这样的经历，在项目中使用系统API或者与某些公共库编写逻辑时，需要C++与C字符串混写甚至转换，在处理字符串结构体的时候就免不了使用sizeof和strlen，这俩看着都有计算size的能力，有时候很容易搞混淆或者出错。

**sizeof** 是个操作符，可用于任何类型或变量，包括数组、结构体、指针等, 返回的是一个类型或变量所占用的字节数; 在编译时求值，不会对表达式进行求值。

**strlen** 是个函数，只能用于以 null 字符结尾的字符串，返回的是一个以 null 字符（'\0'）结尾的字符串的长度(不包括 null 字符本身)，且在运行时才会计算字符串的长度。

需要注意的是，使用 sizeof 操作符计算数组长度时需要注意数组元素类型的大小。例如，对于一个 int 类型的数组，使用 sizeof 操作符计算其长度应该为 `sizeof(array) / sizeof(int)`。而对于一个字符数组，使用strlen函数计算其长度应该为 strlen(array)。

```cpp
char str[] = "hello";  
char *p = str;  
```

此时，用`sizeof(str)`得到的是6，因为hello是5个字符，系统储存的时候会在hello的末尾加上结束标识`\0`，一共为6个字符；

而`sizeof(p)`得到的却是4，它求得的是指针变量p的长度，在32位机器上，一个地址都是32位，即4个字节。

用`sizeof(_p)`得到的是1，因为`_p`定义为char,相当于一个字符，所以只占一个字节。

用`strlen(str)`，得到的会是5，因为strlen求得的长度不包括最后的`\0`。

用`strlen(p)`，得到的是5，与`strlen(str)`等价。

上面的是sizeof和strlen的区别，也是指针字符串和数组字符串的区别。

```cpp
const char* src = "hello world";  
char* dest = NULL;  
int len = strlen(src); // 这里很容易出错，写成sizeof(src)就是求指针的长度，即4  
dest = (char*)malloc(len + 1); // 这里很容易出错，写成len  
char* d = dest;  
const char* s = &src[len - 1]; // 这里很容易出错，写成len  
while (len-- != 0) {  
   *d++ = *s--;  
}  
*d = '\0'; // 这句很容易漏写  
printf("%sIn", dest);  
free(dest);  
```

## std::async真的异步吗?

std::async是C++11开始支持多线程时加入的同步多线程构造函数，其弥补了std::thread没有返回值的问题，并加入了更多的特性，使得多线程更加灵活。

顾名思义，std::async是一个函数模板，它将函数或函数对象作为参数(称为回调)并异步运行它们，最终返回一个std::future，它存储std::async()执行的函数对象返回的值，为了从中获取值，程序员需要调用其成员 future::get.

那std::async一定是异步执行吗？先来看段代码：

```cpp
int calculate_sum(const std::vector<int>& numbers) {  
  std::cout << "Start Calculate..." << std::endl; // (4)  
  int sum = 0;  
  for (int num : numbers) {  
      sum += num;  
  }  
  return sum;  
}  

int main() {  
  std::vector<int> numbers = { 88, 101, 56, 203, 72, 135 };  
  std::future<int> future_sum = std::async(calculate_sum, numbers);  
  std::cout << "Other operations are in progress..." << std::endl; // (1)  
  int counter = 1;  
  while (counter <= 1000000000) {  
      counter++;  
  }  
  std::cout << "Other operations are completed." << std::endl; // (2)  
  // 等待异步任务完成并获取结果  
  int sum = future_sum.get();  
  std::cout << "The calculation result is:" << sum << std::endl; // (3)  
  return 0;  
}  
```

直接运行上面的代码，输出结果如下：

```cpp
Other operations are in progress...  
Start Calculate...  
Other operations are completed.  
The calculation result is:655  

执行完(1) 就去执行(4), 然后再(2)(3)，说明这里是异步执行的。那可以认为async一定是异步的吗？  

如果改成std::async(std::launch::deferred, calculate_sum, numbers); 运行结果如下：

Other operations are in progress...  
Other operations are completed.  
Start Calculate...  
The calculation result is:655  
```

执行完(1) (2), 然后再(4)(3), 说明是真正调用`std::future<>::get()`才去执行的，如果没有调用get，那么就一直不会执行。

std::async是否异步受参数控制的，其第一个参数是启动策略，它控制 std::async 的异步行为。可以使用 3 种不同的启动策略创建std::async ，即：

  * **std::launch::async** 它保证异步行为，即传递的函数将在单独的线程中执行
  * **std::launch::deferred** 非异步行为，即当其他线程将来调用get()来访问共享状态时，将调用函数
  * **std::launch::async | std::launch::deferred** 它是默认行为。使用此启动策略，它可以异步运行或不异步运行，具体取决于系统上的负载，但我们无法控制它

如果我们不指定启动策略，其行为类似于**std::launch::async | std::launch::deferred.** 也就是不一定是异步的。

Effective Modern C++ 里面也提到了，如果异步执行是必须的，则指定**std::launch::async**策略。

## 内存泄漏?

对于这样的一个函数：

```cpp
void processwidget(std::shared_ptrpw, int);
```

如果使用以下方式调用，会有什么问题吗？

```cpp
processwidget(std::shared_ptr(new Widget), priority());
```

一眼看上去觉得没啥问题，甚至可能新手C++开发者也会这么写，其实上面调用可能会存在内存泄漏。

编译器在生成对processWidget函数的调用之前，必须先解析其中的参数。processWidget函数接收两个参数，分别是智能指针的构造函数和整型的函数priority()。在调用智能指针构造函数之前，编译器必须先解析其中的new Widget语句。因此，解析该函数的参数分为三步:

(1) 调用priority();

(2) 执行new Widget.

(3) 调用`std:shared_ptr`构造函数

C++编译器以什么样的固定顺序去完成上面的这些事情是未知的，不同的编译器是有差异的。在C++中可以确定(2)一定先于(3)执行，因为new Widoet还要被传递作为`std::shared_ptr`构造函数的一个实参。然而，对于priority()的调用可以在第(1)、(2)、(3)步执行，假设编译器选择以(2)执行它，最终的操作次序如下: (1) 执行new Widget; (2) 调用priority(): (3)调用`std::shared_ptr`构造函数。但是，如果priority()函数抛出了异常，经由new Widget返回的指针尚未被智能指针管理，将会遗失导致内存泄漏。

解决方法: 使用一个单独的语句来创建智能指针对象。

```cpp
std::shared ptr<Widget> pw(new widget); // 放在单独的语句中  
processwidget(pw, priority()):  
// or  
processwidget(std::make_shared<Widget>(), priority());  
```

编译器是逐语句编译的，通过使用一个单独的语句来构造智能指针对象，编译器就不会随意改动解析顺序，保证了生成的机器代码顺序是异常安全的。

总结：尤其是在跨平台开发的时候更加要注意这类隐晦的异常问题，Effective C++中也提到了，要以独立语句将new对象存储于智能指针内。如果不这样做，一旦异常被抛出，有可能导致难以察觉的内存泄漏。

## const/constexpr

如果C++11中引入的新词要评一个"最令人困惑"奖，那么constexprhen很有可能获此殊荣。当它应用于对象时，其实就是一个加强版的const，但应用于函数时，却有着相当不同的意义。在使用 C++ const和consterpx的时候，可能都会犯晕乎，那constexpr和const都有什么区别，这节简单梳理下。

**const**

const一般的用法就是修饰变量、引用、指针，修饰之后它们就变成了常量，需要注意的是const并未区分出编译期常量和运行期常量，并且const只保证了运行时不直接被修改。

一般的情况，const 也就简单这么用一下，const 放在左边，表示常量：

```cpp
const int x = 100; // 常量

const int& rx = x; // 常量引用

const int* px = &x; // 常量指针
```

给变量加上const之后就成了“常量”，只能读、不能修改，编译器会检查出所有对它的修改操作，发出警告，在编译阶段防止有意或者无意的修改。这样一来，const常量用起来就相对安全一点。在设计函数的时候，将参数用 const 修饰的话，可以保证效率和安全。

除此之外，const 还能声明在成员函数上，const 被放在了函数的后面，表示这个函数是一个“常量”，函数的执行过程是 const 的，不会修改成员变量。

此外，const还有下面这种与指针结合的比较绕的用法：

```cpp
int a = 1;  
const int b = 2;  
const int* p = &a;  
int const* p1 = &a;  

// *p = 2; // error C3892: “p”: 不能给常量赋值  
p = &b;  
// *p1 = 3; // error C3892: “p1”: 不能给常量赋值  
p1 = &b;  

int* const p2 = &a;  
//p2 = &b; // error C2440: “=”: 无法从“const int *”转换为“int *const ”  
*p2 = 5;  
const int* const p3 = &a;  
```

`const int` 与 `int const`并无很大区别，都表示： 指向常量的指针，可以修改指针本身，但不能通过指针修改所指向的值。

而对于`int *const`，则是表示：一个常量指针，可以修改所指向的值，但不能修改指针本身。

`const int* const` 表示一个不可修改的指针，既不能修改指针本身，也不能通过指针修改所指向的值。

总之，const默认与其左边结合，当左边没有任何东西则与右边结合。

**constexpr**

表面上看，constexpr不仅是const，而且在编译期间就已知，这种说法并不全面，当它应用在函数上时，就跟它名字有点不一样了。使用constexpr关键字可以将对象或函数定义为在编译期间可求值的常量，这样可以在编译期间进行计算，避免了运行时的开销。

**constexpr对象** 必须在编译时就能确定其值，并且通常用于基本数据类型。例如：

`constexpr int MAX_SIZE = 100;` // 定义一个编译时整型常量

`constexpr double PI = 3.14159;` // 定义一个编译时双精度浮点型常量

const和constexpr变量之间的主要区别在于变量的初始化，const可以推迟到运行时，constexpr变量必须在编译时初始化。const 并未区分出编译期常量和运行期常量，并且const只保证了运行时不直接被修改，而constexpr是限定在了编译期常量。简而言之，所有constexpr对象都是const对象，而并非所有的const对象都是constexpr对象。

● 当变量具有字面型别(literal type)(这样的型别能够持有编译期可以决议的值)并已初始化时，可以使用constexpr来声明该变量。如果初始化由构造函数执行，则必须将构造函数声明为constexpr.

● 当满足这两个条件时，可以声明引用constexpr：引用的对象由常量表达式初始化，并且在初始化期间调用的任何隐式转换也是常量表达式。

● constexpr变量或函数的所有声明都必须具有constexpr说明符。

```cpp
constexpr float x = 42.0;  
constexpr float y{108};  
constexpr float z = exp(5, 3);  
constexpr int i; // Error! Not initialized  
int j = 0;  
constexpr int k = j + 1; //Error! j not a constant expression  
```

**constexpr函数** 是指能够在编译期间计算结果的函数。它们的参数和返回值类型必须是字面值类型，并且函数体必须由单个返回语句组成。例如：

```cpp
constexpr int square(int x) {  
    return x * x;  
}  

constexpr int result = square(5); // 在编译期间计算结果，result 的值为 25
```

使用 constexpr 可以提高程序的性能和效率，因为它允许在编译期间进行计算，避免了运行时的计算开销。同时，constexpr 还可以用于指定数组的大小、模板参数等场景，提供更灵活的编程方式。

对constexpr函数的理解：

1. constexpr函数可以用在要求编译器常量的语境中。在这样的语境中，如果你传给constexpr函数的实参值是在编译期已知的，则结果也会在编译期间
计算出来。如果任何一个实参值在编译期间未知，则代码将无法通过编译。

2. 在调用constexpr函数时，若传入的值有一个或多个在编译期间未知，则它的运作方式和普通函数无异，也就是它也是在运行期执行结果的计算。也就是说，如果一个函数执行的是同样的操作，仅仅应用语境一个是要求编译期常量，一个是用于所有其他值的话，那就不必写两个函数。constexpr函数就可以同时满足需求。

```cpp
constexpr float exp(float x, int n) {  
  return n == 0 ? 1 :  
      n % 2 == 0 ? exp(x * x, n / 2) :  
      exp(x * x, (n - 1) / 2) * x;  
} 

constexpr auto x = 5;  
constexpr auto n = 3;  
constexpr int result = exp(x, n); // ok, 前面加上constexpr，进行编译期间求值，单步调试根本进不去  

int xx = 4;  
int nn = 3;  
//constexpr int result2 = exp(xx, nn); // error C2131: 表达式的计算结果不是常数  
int result3 = exp(xx, nn); // ok, 这里作为普通函数来使用  
```

比起非constexpr对象或constexpr函数而言，constexpr对象或是constexpr函数可以用在一个作用域更广的语境中。只要有可能使用constexpr，就使用它吧。

## 最后

欢迎C++大佬们一起交流经验，站在巨人的肩膀上，写的有问题的地方欢迎拍砖补充。

* [万字避坑指南！C++的缺陷与思考（下） - 知乎](https://zhuanlan.zhihu.com/p/593044308)
* [智能指针-使用、避坑和实现](https://mp.weixin.qq.com/s?__biz=Mzk0MzI4OTI1Ng==&mid=2247487474&idx=1&sn=e29d0178bfd4139313c44139e1cb3899&chksm=c3376935f440e023b96e9f8feeb34e4e22fbb74f00ca345a2b867edfd4c088bc595821fe878e&mpshare=1&scene=21&srcid=1129M6x6MCo6B28Lau7T09bf&sharer_shareinfo=98f5817f268cfb504cfababfb43529c6&sharer_shareinfo_first=98f5817f268cfb504cfababfb43529c6&from=industrynews&version=4.1.13.1096&platform=win#wechat_redirect)
* [c++ - What's the difference between constexpr and const? - Stack Overflow](https://stackoverflow.com/questions/14116003/whats-the-difference-between-constexpr-and-const)
* <https://stackoverflow.com/questions/402283/stdwstring-vs-stdstring>

