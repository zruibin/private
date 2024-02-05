 
<!--BEGIN_DATA
{
    "create_date": "2020-10-13 16:39", 
    "modify_date": "2020-10-13 16:39", 
    "is_top": "0", 
    "summary": "编写安全C++代码杂谈", 
    "tags": "C/C++", 
    "file_name": "编写安全C++代码杂谈.md"
}
END_DATA-->

#### <p>原文出处：<a href='http://purecpp.org/detail?id=2189' target='blank'>编写安全C++代码杂谈</a></p>

编写安全的代码是一件不容易的事情，需要从多角度，多维度去考虑代码的安全性，采用多种方法去保证代码安全。现代C++提供了很多保证安全性的方法和特性，为了让大家能深入了解如何编写安全性代码，我将通过一个经典的案例给大家展示一些代码安全性的问题以及用现代C++编写安全代码的一些思想和方法。

# 从一个对象池开始

## 什么是对象池

对象池模式是一个经典的设计模式，在实际开发中会、经常用到，比如数据库连接池、资源池、线程池等等都是对象池模式的应用。

对象池解决的问题是避免重复创建“昂贵”的对象，比如数据库连接。创建数据库连接和关闭连接都是比较慢的，如果每一次访问都需要创建和关闭连接会影响应用的并发性能，因此我们一般会采用数据库连接池来优化性能。

数据库连接池的实现思路很简单，一开始初始化的时候创建数十个甚至上百个连接，当用户来请求数据库的时候就从连接池中返回一个已经创建好的连接对象给用户，当用户使用完之后再返回给连接池，这个连接无需关闭，对象池回收这个连接供下一次复用，这样避免了频繁的创建和关闭连接。

## 一个简单的对象池实现

根据对象池的实现思想，我们可以很容易用C++写一个对象池。我先用C++98/03标准来写一个简单的对象池（代码为了便于讲解，代码尽可能简化，不考虑对象的初始化），后面再用现代C++一步一步改进，给大家展示如何用C++编写安全的代码。

    
```c++
#pragma once
#include <string>
#include <deque>

struct connection {
    std::string id;
    //...other fields
};

class simple_pool {
public:
    simple_pool(size_t init_size) {
        for (size_t i = 0; i < init_size; i++) {
            pool_.push_back(new connection());
        }
    }

    ~simple_pool() {
        for (std::deque<connection*>::iterator it = pool_.begin(); it != pool_.end(); it++) {
            connection* p = *it;
            delete p;
        }
    }

    connection* acquire() {
        if (empty()) {
            return NULL;
        }
        connection* res = pool_.front();
        pool_.pop_front();
        return res;
    }

    void release(connection* p) {
        pool_.push_back(p);
    }

    bool empty() const {
        return pool_.empty();
    }

    size_t size() const {
        return pool_.size();
    }
private:
    std::deque<connection*> pool_;
};
```

这个代码很简单，内部使用一个队列来保存连接对象，提供了最基本的获取连接和回收连接的接口：acquire和release。

接下来我们写一个单元测试来测试这个连接池。

    
```c++
TEST_CASE("test acquire and release") {
    simple_pool pool(10);
    CHECK(pool.size() == 10);
    connection* conn = pool.acquire();
    CHECK(pool.size() == 9);
    connection* conn1 = pool.acquire();
    CHECK(pool.size() == 8);
    pool.release(conn);
    CHECK(pool.size() == 9);
    pool.release(conn1);
    CHECK(pool.size() == 10);
}

===============================================================================
[doctest] test cases:      1 |      1 passed |      0 failed |      0 skipped
[doctest] assertions:      5 |      5 passed |      0 failed |
[doctest] Status: SUCCESS!
```

这个测试用例测试通过，说明基本的功能是可用的，到这里我们似乎已经完成了一个对象池的代码了，能用了。

然而，实际上这个对象池的代码**没有一个函数是安全的！**

这个代码存在很多安全性的问题，让我们一个一个来看看这些函数到底有哪些安全性的问题。

# 第一个问题

**参数边界的检查**。

首先来看看release函数。

    
```c++
void release(connection* p) {
    pool_.push_back(p);
}
```

当我返回一个NULL指针的时候会怎么样？我们写一个测试用例来看看：

    
```c++
TEST_CASE("test release") {
    simple_pool pool(1);
    CHECK(pool.size() == 1);

    connection* conn = pool.acquire();
    CHECK(pool.size() == 0);
    delete conn;
    conn = NULL;
    pool.release(conn);
    CHECK(pool.size() == 1);

    connection* conn1 = pool.acquire();
    CHECK(conn1->id.empty());
}
```

由于release没有对conn参数做任何检查，将一个空的指针返回到连接池中了，下一次acquire的时候得到的是一个空指针，后面访问该对象的成员会导致一个访问空指针的错误。

这个错误很容易检查出来，改进一下，在release中对参数做一个检查，对于空指针我们不回收就是了。

## 改进之后的release

改进之后的release函数是这样的。

    
```c++
void release(connection* p) {
    if (p == NULL) {
        p = new connection();
    }
    pool_.push_back(p);
}
```

再运行"test release"测试用例，测试通过。

这个小小的改进似乎让代码变得更安全了，然而并不是，这个改进非但没有让代码变得安全反而变得更危险了！我们再写一个测试用例：

    
```c++
TEST_CASE("test release with deleted connection") {
    simple_pool pool(1);
    CHECK(pool.size() == 1);

    connection* conn = pool.acquire();
    CHECK(pool.size() == 0);
    delete conn;
    pool.release(conn);
    CHECK(pool.size() == 1);

    connection* conn1 = pool.acquire();
    CHECK(conn1->id.empty());
}
```

这个测试用例和"test release"测试用例相比只少了一行代码，少了将删除的conn置为NULL那一行。结果就导致我们将一个“野指针”回收到对象池中了，下次acquire的时候得到的其实是一个“野指针”！你再访问“野指针”的成员是非常危险的，因为编译器优化的原因，当你访问“野指针”成员的时候可能不会报错，导致将问题隐藏起来了。这比空指针还危险，空指针至少会明确产生运行时错误，所以这个看似更安全的改进其实让代码变得更危险了。

这里也许可以争论的是：我们规定这个connection指针不允许在外面删除，就不会出现归还空指针或者“野指针”的问题了。但是这个规定是人为控制的，而删除指针是完全合法的，编译器也不会出现告警，写代码的人总会出现百密一疏的情况，所以这个规定是没有安全性保证的。

既然如此，有什么办法可以来保证这个release的安全性呢？其实这里问题的本质是我们能不能知道这个回收的指针是否被删除过，如果知道了这个指针被删除过那么就好办了。很遗憾C++98/03中并没有直接的特性来检查指针是否被删除过，C语言也一样没有办法检查出来。在C++11中我们就有办法检查指针是否被删除过了，C++11提供了多种类型的智能指针来解决裸指针生命周期的问题，这个会在后面详细讲到。

接下来我们再来看看另外一个参数没有做边界检查的问题。

## 不安全的初始化

对象池的构造函数中我们创建了多个连接并放入到连接池中。

    
```c++
simple_pool(size_t init_size) {
    for (size_t i = 0; i < init_size; i++) {
        pool_.push_back(new connection());
    }
}
```

这里有一个显而易见的问题，我们并没有对init_size做任何检查，如果这个init_size非常大，比如传一个-1进去，由于size_t是unsingned的整形，会发生溢出，对一个32位的整形来说会达到4294967295，这个init_size非常大，这个初始化将会导致我们的程序内存耗尽。

## 改进之后的构造函数

这个问题很明显，稍有经验的开发者都会对这类参数的范围做校验，下面是改进之后的构造函数：

    
```c++
simple_pool(size_t init_size) {
    if (init_size > 500) {
        throw std::out_of_range("init size is out of range");
    }

    for (size_t i = 0; i < init_size; i++) {
        pool_.push_back(new connection());
    }
}
```

改进之后，当传入的正整数大于某个范围的时候我们就抛一个out_of_range的异常出来，从而解决参数范围不合法的问题。

这样改进之后，构造函数的安全性的问题似乎解决了，然而，这仍然不够安全。虽然我们加了运行时判断和抛出异常，但是别忘了，这个参数的检查是发生在运行期，往往到这个时候发现问题已经太晚了！如果能在更早的时候就发现问题，并且是让程序自动去发现问题就完美了。

## 第二次改进之后的构造函数

C++提供了另外的一种保证代码安全性的机制：编译期检查。它可以让我们在编译期的时候就能发现参数范围的问题。我们可以通过C++11的编译期断言来增强代码的安全性。

    
```c++
template<size_t N>
class simple_pool {
public:    
    simple_pool() {
        static_assert(N < 500, "init size is out of range");
        for (size_t i = 0; i < N; i++) {
            pool_.push_back(new connection());
        }
    }
```

现在这个改进之后的构造函数非常安全了，不用担心初始化参数越界的问题了，当传入的参数不合法的时候编译器会自动发现问题，给出断言错误的提示。比如：

    
```c++
simple_pool<-1> pool;//error: init size is out of range
simple_pool<1000> pool;//error: init size is out of range
```

当传入的参数越界的时候，就会产生一个编译期断言错误，这样可以保证在编译期而不是运行期就能捕捉到错误。

# 第二个问题

**内存安全的问题**。

内存安全的问题实际上就是对象生命周期的问题，对象池返回和释放对象都是裸指针，这是不安全的，只要使用裸指针，代码的安全性就无法得到保证!

裸指针最大的两个问题:

  1. 需要手动释放，存在内存泄漏的可能；
  2. 无法可靠的检查指针是否已经被释放；

下面来分别探讨一下这两种裸指针安全性的问题。

## 裸指针内存泄漏的问题

最常见的内存泄漏的例子是忘记释放内存了，更隐蔽的内存泄漏是异常导致的，看一个典型的例子：

    
```c++
void foo(bool check, bool ignor){
    int* p = new int(10);

    if(ignor){
        return;
    }

    if(!check){
        throw std::invalid_argument("");
    }

    delete p;
}

foo(true, true);
foo(false, false);
```

第一个foo调用会产生内存泄漏，因为提前返回了，没有删除指针p，这种代码错误比较容易检查出来。

第二个foo调用也会产生内存泄漏，因为check失败的时候抛异常了，导致程序没有机会执行到删除指针p那里，从而导致了内存泄漏。

我们应该保证无论是提前返回还是发生异常时都会正常释放内存，这称为异常安全。

## 裸指针释放的问题

当返回裸指针给外面使用的时候，外面可能会删掉这个指针，在其他地方再使用这个指针的时候可能是一个“野指针”。也许你可以将删除后的指针设置为NULL来推断指针是否被释放，但这这种安全依赖于写代码的人，安全性是没有可靠保证的。

另外一个问题是裸指针释放时机的问题，当我希望删除某个指针的时候，这个指针可能正在被其他对象所使用，删除会导致不可预测的结果发生。那么怎么知道这个指针是否正在被其对象所使用呢？很遗憾，裸指针无法做到。

## 现代C++解决内存安全的方法

现代C++中不推荐使用裸指针，应该用智能指针来替代裸指针，C++11提供了三种类型的智能指针专门用来解决裸指针的安全性问题，在现代C++中我们应该smart pointer everywhere!

## C++智能指针简介

在介绍智能指针如何保证内存安全之前我们对它们做一个简要的介绍。用C++14写几个简单的测试用例。

    
```c++
#include <memory>

TEST_CASE("test shared pointer") {
    std::shared_ptr<connection> conn = nullptr;

    {
        conn = std::make_shared<connection>();
        std::shared_ptr<connection> conn1 = conn;
        CHECK(conn.use_count() == 2);
        CHECK(conn1.use_count() == 2);

        conn.reset();
    }
    CHECK(conn == nullptr);
}

TEST_CASE("test unique pointer") {
    std::unique_ptr<connection> conn = std::make_unique<connection>();
    std::unique_ptr<connection> conn1 = std::move(conn);
    CHECK(conn == nullptr);
    CHECK(conn1);
}

TEST_CASE("test weak pointer") {
    std::shared_ptr<connection> conn = nullptr;
    std::weak_ptr<connection> weak;
    {
        std::shared_ptr<connection> conn = std::make_shared<connection>();
        weak = conn;
        CHECK(conn.use_count() == 1);
        std::shared_ptr<connection> sp = weak.lock();
        CHECK(conn.use_count() == 2);
    }

    CHECK(conn == nullptr);

    //weak.lock() will return nullptr if conn was deleted.
    std::shared_ptr<connection> sp = weak.lock();
    CHECK(sp == nullptr);
}
```

现代C++中提供了三种智能指针：

  1. std::shared_ptr

共享的智能指针，通过引用计数机制来保证自动释放原始指针。

  2. std::unique_ptr

独占的智能指针，永远只允许一个智能指针拥有资源，只可以move，不可以拷贝， RAII机制保证自动释放原始指针。

  3. std::weak_ptr

弱引用的智能指针，它用来监视shared_ptr的生命周期，可以用来检查指针是否已经被释放。

有了这几种智能指针之后，再也不用担心内存安全性的问题了。

## 用智能指针保证异常安全

我们对之前的foo函数做一个改进，让它变成类型安全的函数。

    
```c++
    void foo(bool check, bool ignor){
        std::shared_ptr<int> p = std::shared_ptr<int>(10);
        if(ignor){
            return;
        }
        if(!check){
            throw std::invalid_argument("");
        }
    }

    foo(true, true);
    foo(false, false);
```

仅仅是将裸指针改成智能指针，这个代码就不用再担心提前返回或者抛异常导致的内存泄漏的问题了。

接下来我们用C++11把之前用裸指针实现的对象池改进一下，改成共享智能指针的对象池，让它变得更安全。

    
```c++
template<size_t N>
class shared_pool {
public:
    shared_pool() {
        static_assert(N < 500, "init size is out of range");
        for (size_t i = 0; i < N; i++) {
            pool_.push_back(new connection());
        }
    }

    std::shared_ptr<connection> acquire() {
        if (empty()) {
            return nullptr;
        }
        std::shared_ptr<connection> res = pool_.front();
        pool_.pop_front();
        return res;
    }

    void release(std::shared_ptr<connection> p) {
        if (p == nullptr) {
            p = std::make_shared<connection>();
        }

        pool_.push_back(p);
    }

    bool empty() const {
        return pool_.empty();
    }

    size_t size() const {
        return pool_.size();
    }
private:
    std::deque<std::shared_ptr<connection>> pool_;
};
```

这个C++11实现的对象池代码比C++98/03实现的版本更少了，同时也更安全了。首先原始指针的释放无需专门写一个析构函数去释放了，让shared_ptr自动释放即可；其次release的时候可以根据shared_ptr轻易知道连接在外面有没有被释放。你也可以根据需要把shared_ptr改成unique_ptr。

虽然这个C++11版本的对象池相比C++98版本的对象池来说安全多了，但是，这个代码仍然不够安全，**仍然存在安全性问题！**

# 第三个问题

对象池的基本思想就是“有借有还，再借不难”，不怕借，就怕不还。前面C++11版本的对象池需要依赖一个release接口来归还资源，这是不安全的，因为存在忘记归还的可能，手动去归还资源永远是不安全的！

既然如此，有没有可能实现一个能自动归还的对象池呢？如果能实现自动归还那就完美了。

要实现一个自动归还的对象池也不难，我们只要在智能指针释放的时候做一点文章就行了。std::shared_ptr支持用户自定义的释放函数，因此我们写一个自定义的释放函数，在释放函数中将对象归还到对象池中，这样就避免了手动回收对象存在“有借无还”的可能了！

## 一个自动释放的对象池

由于是自动释放的对象池，我们可以去掉release接口了，只有一个acquire接口了，代码变得更简洁了

    
```c++
template<size_t N>
class object_pool {
public:
    using DeleterType = std::function<void(connection*)>;

    object_pool() {
        static_assert(N < 500, "init size is out of range");
        for (size_t i = 0; i < N; i++) {
            pool_.push_back(std::make_unique<connection>());
        }
    }

    std::unique_ptr<connection, DeleterType> acquire() {
        if (empty()) {
            return nullptr;
        }

        std::unique_ptr<connection, DeleterType> ptr(pool_.front().release(), [this](connection* t) {
            pool_.push_back(std::unique_ptr<connection>(t));
        });

        pool_.pop_front();
        return ptr;
    }

    bool empty() const {
        return pool_.empty();
    }

    size_t size() const {
        return pool_.size();
    }
private:
    std::deque<std::unique_ptr<connection>> pool_;
};
```

我们看看这个自动回收是如何实现的，关键代码在这里：

    
```c++
std::unique_ptr<connection, DeleterType> ptr(pool_.front().release(), [this](connection* t) {
    pool_.push_back(std::unique_ptr<connection>(t));
});
```

acquire的时候，创建了一个自定义删除器的unique_ptr，当这个unique_ptr释放的时候就会去调用这个自定义删除器，在删除器中我们并不会真的去删除指针，而是用它重新构造一个新的unique_ptr放到对象池中，从而实现了自动回收。

我们一步一步不断地解决代码安全性的问题，到目前为止我们实现了一个足够安全的对象池了。然而还存在另外一个安全性问题--线程安全，现在的这个对象池不是线程安全的，如果在多线程环境下使用是不安全的。

# 第四个问题

线程安全。

线程安全问题比较好解决，通过C++11的锁就可以实现线程安全了。以acquire函数为例：

    
```c++
std::unique_ptr<connection, DeleterType> acquire() {
    mtx_.lock();
    if (pool_.empty()) {
        return nullptr;
    }
    std::unique_ptr<connection, DeleterType> ptr(pool_.front().release(), [this](connection* t) {
        pool_.push_back(std::unique_ptr<connection>(t));
    });
    pool_.pop_front();
    mtx_.unlock();
    return ptr;
}

std::mutex mtx_;
```

用C++11的独占锁std::mutex lock/unlock来保证acquire的线程安全，看起来是线程安全的，然而，这个代码并不安全，这个代码会死锁。
当pool为空时提前返回了，无法执行后面的unlock去解锁，所以这个代码不是异常安全的。好在C++11提供了lock guard来保证异常安全。

## 用lock gaurd防止死锁

C++11提供了两种lock guard：std::scope_guard和std::unique_guard, 用它们就是防止死锁了。上面的acquire稍作修改即可。

    
```c++
std::unique_ptr<connection, DeleterType> acquire() {
    std::unique_lock<std::mutex> lock;
    if (pool_.empty()) {
        return nullptr;
    }

    std::unique_ptr<connection, DeleterType> ptr(pool_.front().release(), [this](connection* t) {
        pool_.push_back(std::unique_ptr<connection>(t));
    });

    pool_.pop_front();
    return ptr;
}
```

这个异常安全是依靠C++的RAII机制实现的，当对象出了作用域析构的时候自动去解锁，从解决了手动解锁可能引起的死锁问题。

至此，我们已经实现了一个很安全的对象池了，其实我们还可以继续增强这个对象池的安全性。

# 安全性增强

一个对象池应该是全局唯一的，并且不可拷贝和移动，不可继承的。

既然是对象池，我们希望所有的取和还都是通过同一个对象池，只在一个地方去管理对象有助于增强程序的安全性。

如果对象池允许拷贝，就不能保证全局唯一了，我们应该明确禁止对象池的拷贝。

如果对象池可以被其他对象继承，其他对象可能会覆盖对象池的函数改变对象池的行为，存在安全风险，应该明确禁止继承于对象池。

因此我们可以在这些方面对安全性做进一步增强，好在C++11在这方面增加了一些新特性来保证安全性。

## 不可拷贝

写一个noncopyable，这个类中的默认构造函数和拷贝构造函数是被删除的，然后对象池再从这个noncopyable继承，这样就可以禁止对象池被拷贝了。当然你还可以禁用移动构造函数和移动赋值函数来禁止对象池被移动。

    
```c++
class noncopyable
{
 public:
  noncopyable(const noncopyable&) = delete;
  void operator=(const noncopyable&) = delete;

 protected:
  noncopyable() = default;
  ~noncopyable() = default;
};

template<size_t N>
class object_pool : noncopyable {

};
```
    

## 不可继承

C++11增加了一个新的关键字final，这个final修饰的类是不可继承的，因此我们只要在类后面加一个final就可以实现该类型不可继承了。

    
```c++
template<size_t N>
class object_pool final {

};
```c++

## 全局唯一

只需要实现一个单例即可，C++11中单例实现非常简单，两行代码就可以了。先把对象的默认构造函数设置为private，再通过一个静态局部变量来保证全局唯一。

    
```c++
template<size_t N>
class object_pool final : noncopyable {
public:
    static object_pool& get() {
        static object_pool<N> pool;
        return pool;
    }

    //...
private:
    object_pool() {
        static_assert(N < 500, "init size is out of range");
        for (size_t i = 0; i < N; i++) {
            pool_.push_back(std::make_unique<connection>());
        }
    }

    std::deque<std::unique_ptr<connection>> pool_;
};

TEST_CASE("test auto return pool") {
    auto& pool = object_pool<10>::get();

    {
        auto conn = pool.acquire();
        CHECK(pool.size() == 9);
    }

    CHECK(pool.size() == 10);

    auto conn = pool.acquire();
    conn.reset();
    CHECK(pool.size() == 10);
}
```

# 总结

我们再回过头来看这个案例，对象池的实现看起来很简单，但是要把它的实现写得很安全并不是一件容易的事情。

我们一步一步解决了4个安全性的问题：编译期检查参数边界、内存安全、异常安全和线程安全等问题，最终实现了一个非常安全的对象池。

从中我们可以得到很多启发，如何编写安全代码总结起来大概有这么几条原则：

## 防患于未然

我们应该尽可能在编译期而不是运行期发现问题，尽可能早地发现问题；尽可能让编译器帮我们发现和解决问题，而不是靠人眼发现问题；比如用static_cast代替c-style的强转， 借助现代C++的编译期断言和type_traits等新特性在编译期做安全性检查等。

## 无为而治

我们写代码要尽可能实现程序自动化的自我管理，尽可能避免手动去管理，比如手动释放内存，手动去解锁，这些需要手动操作的地方越多，代码的安全性就越低，因为人总是会犯错。我们应该借助于C++的RAII机制、智能指针、scope lock等特性，这些特性可以很容易地实现内存的自我管理和异常安全。

不依赖人工而是依赖语言自身特性实现程序的自动化地自我管理--“无为而治”。

## 上善若水

我们应该充分利用语言自身的特性来保障和增强代码的安全性，比如我们用std::shared_ptr的自定义删除器来实现对象的自动归还，彻底消除了“有借无还”的可能；利用final禁止继承，利用noncopyable禁止拷贝等等。这些都是充分利用了语言自身的特性，从而能写出更安全的代码。

## 结束

毫无无疑问的是C++比C更加安全，无论是类型安全、内存安全还是异常安全都做了比C语言多得多的事情。

C++语言博大精深，我也只是通过一个简单的案例来分析来介绍如何用现代C++的一些特性来编写安全代码的一些方法而已，C++还有很多特性对安全性做了保证，如const，override，noexcept，stricter order of expression evaluation，std::array, variant, 一些安全的STL算法...，限于篇幅没有一一展开讨论，本文也只是管中窥豹，姑且做抛砖引玉之用。
