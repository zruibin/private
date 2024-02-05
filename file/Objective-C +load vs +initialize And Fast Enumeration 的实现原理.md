 
<!--BEGIN_DATA
{
    "create_date": "2017-08-28 10:32", 
    "modify_date": "2017-08-28 10:32", 
    "is_top": "0", 
    "summary": "Objective-C +load vs +initialize", 
    "tags": "iOS", 
    "file_name": "Objective-C +load vs +initialize And Fast Enumeration 的实现原理.md"
}
END_DATA-->

####<p>原文出处：<a href='http://blog.leichunfeng.com/blog/2015/05/02/objective-c-plus-load-vs-plus-initialize/' target='blank'>Objective-C +load vs +initialize</a></p>

在上一篇博文[《Objective-C对象模型》](http://blog.leichunfeng.com/blog/2015/04/25/objective-c-object-model/)中，我们知道了 Objective-C 中绝大部分的类都继承自 NSObject 类。而在 NSObject 类中有两个非常特殊的类方法
+load 和 +initialize ，用于类的初始化。这两个看似非常简单的类方法在许多方面会让人感到困惑，比如：

  1. 子类、父类、分类中的相应方法什么时候会被调用？
  2. 需不需要在子类的实现中显式地调用父类的实现？
  3. 每个方法到底会被调用多少次？

下面，我们将结合 [runtime](http://opensource.apple.com/tarballs/objc4/)（我下载的是当前的最新版本
`objc4-646.tar.gz`) 的源码，一起来揭开它们的神秘面纱。

###+load

+load 方法是当类或分类被添加到 Objective-C runtime 时被调用的，实现这个方法可以让我们在类加载的时候执行一些类相关的行为。子类的+load 方法会在它的所有父类的 +load 方法之后执行，而分类的 +load 方法会在它的主类的 +load 方法之后执行。但是不同的类之间的
+load 方法的调用顺序是不确定的。

打开 runtime 工程，我们接下来看看与 +load 方法相关的几个关键函数。首先是文件 `objc-runtime-new.mm` 中的 `void
prepare_load_methods(header_info *hi)` 函数：
    
    
    void prepare_load_methods(header_info *hi)
    {
        size_t count, i;
    
        rwlock_assert_writing(&runtimeLock);
    
        classref_t *classlist =
            _getObjc2NonlazyClassList(hi, &count);
        for (i = 0; i < count; i++) {
            schedule_class_load(remapClass(classlist[i]));
        }
    
        category_t **categorylist = _getObjc2NonlazyCategoryList(hi, &count);
        for (i = 0; i < count; i++) {
            category_t *cat = categorylist[i];
            Class cls = remapClass(cat->cls);
            if (!cls) continue;  // category for ignored weak-linked class
            realizeClass(cls);
            assert(cls->ISA()->isRealized());
            add_category_to_loadable_list(cat);
        }
    }
    

顾名思义，这个函数的作用就是提前准备好满足 +load 方法调用条件的类和分类，以供接下来的调用。其中，在处理类时，调用了同文件中的另外一个函数`static void schedule_class_load(Class cls)` 来执行具体的操作。

      
    static void schedule_class_load(Class cls)
    {
        if (!cls) return;
        assert(cls->isRealized());  // _read_images should realize
    
        if (cls->data()->flags & RW_LOADED) return;
    
        // Ensure superclass-first ordering
        schedule_class_load(cls->superclass);
    
        add_class_to_loadable_list(cls);
        cls->setInfo(RW_LOADED);
    }
    

其中，函数第 9 行代码对入参的父类进行了递归调用，以确保父类优先的顺序。`void prepare_load_methods(header_info *hi)` 函数执行完后，当前所有满足 +load 方法调用条件的类和分类就被分别存放在全局变量 `loadable_classes` 和`loadable_categories` 中了。

准备好类和分类后，接下来就是对它们的 +load 方法进行调用了。打开文件 `objc-loadmethod.m` ，找到其中的 `void
call_load_methods(void)` 函数。

    
    
    void call_load_methods(void)
    {
        static BOOL loading = NO;
        BOOL more_categories;
    
        recursive_mutex_assert_locked(&loadMethodLock);
    
        // Re-entrant calls do nothing; the outermost call will finish the job.
        if (loading) return;
        loading = YES;
    
        void *pool = objc_autoreleasePoolPush();
    
        do {
            // 1. Repeatedly call class +loads until there aren't any more
            while (loadable_classes_used > 0) {
                call_class_loads();
            }
    
            // 2. Call category +loads ONCE
            more_categories = call_category_loads();
    
            // 3. Run more +loads if there are classes OR more untried categories
        } while (loadable_classes_used > 0  ||  more_categories);
    
        objc_autoreleasePoolPop(pool);
    
        loading = NO;
    }
    

同样的，这个函数的作用就是调用上一步准备好的类和分类中的 +load 方法，并且确保类优先于分类的顺序。我们继续查看在这个函数中调用的另外两个关键函数`static void call_class_loads(void)` 和 `static BOOL call_category_loads(void)`。由于这两个函数的作用大同小异，下面就以篇幅较小的 `static void call_class_loads(void)` 函数为例进行探讨。

    
    
    
    static void call_class_loads(void)
    {
        int i;
    
        // Detach current loadable list.
        struct loadable_class *classes = loadable_classes;
        int used = loadable_classes_used;
        loadable_classes = nil;
        loadable_classes_allocated = 0;
        loadable_classes_used = 0;
    
        // Call all +loads for the detached list.
        for (i = 0; i < used; i++) {
            Class cls = classes[i].cls;
            load_method_t load_method = (load_method_t)classes[i].method;
            if (!cls) continue;
    
            if (PrintLoading) {
                _objc_inform("LOAD: +[%s load]\n", cls->nameForLogging());
            }
            (*load_method)(cls, SEL_load);
        }
    
        // Destroy the detached list.
        if (classes) _free_internal(classes);
    }
    

这个函数的作用就是真正负责调用类的 +load 方法了。它从全局变量 `loadable_classes` 中取出所有可供调用的类，并进行清零操作。


    
    loadable_classes = nil;
    loadable_classes_allocated = 0;
    loadable_classes_used = 0;
    

其中 `loadable_classes` 指向用于保存类信息的内存的首地址，`loadable_classes_allocated`标识已分配的内存空间大小，`loadable_classes_used` 则标识已使用的内存空间大小。

然后，循环调用所有类的 +load 方法。**注意**，这里是（调用分类的 +load 方法也是如此）直接使用函数内存地址的方式
`(*load_method)(cls, SEL_load);` 对 +load 方法进行调用的，而不是使用发送消息 `objc_msgSend` 的方式。

这样的调用方式就使得 +load 方法拥有了一个非常有趣的特性，那就是子类、父类和分类中的 +load 方法的实现是被区别对待的。也就是说如果子类没有实现
+load 方法，那么当它被加载时 runtime 是不会去调用父类的 +load 方法的。同理，当一个类和它的分类都实现了 +load
方法时，两个方法都会被调用。因此，我们常常可以利用这个特性做一些“邪恶”的事情，比如说方法混淆（[Method
Swizzling](http://nshipster.com/method-swizzling/)）。

###+initialize

+initialize 方法是在类或它的子类收到第一条消息之前被调用的，这里所指的消息包括实例方法和类方法的调用。也就是说 +initialize
方法是以懒加载的方式被调用的，如果程序一直没有给某个类或它的子类发送消息，那么这个类的 +initialize方法是永远不会被调用的。那这样设计有什么好处呢？好处是显而易见的，那就是节省系统资源，避免浪费。

同样的，我们还是结合 runtime 的源码来加深对 +initialize 方法的理解。打开文件 `objc-runtime-new.mm`，找到以下函数：
    
    
    IMP lookUpImpOrForward(Class cls, SEL sel, id inst,
                           bool initialize, bool cache, bool resolver)
    {
        ...
            rwlock_unlock_write(&runtimeLock);
        }
    
        if (initialize  &&  !cls->isInitialized()) {
            _class_initialize (_class_getNonMetaClass(cls, inst));
            // If sel == initialize, _class_initialize will send +initialize and 
            // then the messenger will send +initialize again after this 
            // procedure finishes. Of course, if this is not being called 
            // from the messenger then it won't happen. 2778172
        }
    
        // The lock is held to make method-lookup + cache-fill atomic 
        // with respect to method addition. Otherwise, a category could 
        ...
    }
    

当我们给某个类发送消息时，runtime 会调用这个函数在类中查找相应方法的实现或进行消息转发。从第 8-14 的关键代码我们可以看出，当类没有初始化时runtime 会调用 `void _class_initialize(Class cls)` 函数对该类进行初始化。

    
    
    void _class_initialize(Class cls)
    {
        ...
        Class supercls;
        BOOL reallyInitialize = NO;
    
        // Make sure super is done initializing BEFORE beginning to initialize cls.
        // See note about deadlock above.
        supercls = cls->superclass;
        if (supercls  &&  !supercls->isInitialized()) {
            _class_initialize(supercls);
        }
    
        // Try to atomically set CLS_INITIALIZING.
        monitor_enter(&classInitLock);
        if (!cls->isInitialized() && !cls->isInitializing()) {
            cls->setInitializing();
            reallyInitialize = YES;
        }
        monitor_exit(&classInitLock);
    
        if (reallyInitialize) {
            // We successfully set the CLS_INITIALIZING bit. Initialize the class.
    
            // Record that we're initializing this class so we can message it.
            _setThisThreadIsInitializingClass(cls);
    
            // Send the +initialize message.
            // Note that +initialize is sent to the superclass (again) if 
            // this class doesn't implement +initialize. 2157218
            if (PrintInitializing) {
                _objc_inform("INITIALIZE: calling +[%s initialize]",
                             cls->nameForLogging());
            }
    
            ((void(*)(Class, SEL))objc_msgSend)(cls, SEL_initialize);
    
            if (PrintInitializing) {
                _objc_inform("INITIALIZE: finished +[%s initialize]",
        ...
    }
    

其中，第 7-12 行代码对入参的父类进行了递归调用，以确保父类优先于子类初始化。另外，最关键的是第 36 行代码（暴露了 +initialize
方法的本质），runtime 使用了发送消息 `objc_msgSend` 的方式对 +initialize 方法进行调用。也就是说 +initialize方法的调用与普通方法的调用是一样的，走的都是发送消息的流程。换言之，如果子类没有实现 +initialize方法，那么继承自父类的实现会被调用；如果一个类的分类实现了 +initialize 方法，那么就会对这个类中的实现造成覆盖。

因此，如果一个子类没有实现 +initialize 方法，那么父类的实现是会被执行多次的。有时候，这可能是你想要的；但如果我们想确保自己的
+initialize 方法只执行一次，避免多次执行可能带来的副作用时，我们可以使用下面的代码来实现：
    
    
    + (void)initialize {
      if (self == [ClassName self]) {
        // ... do the initialization ...
      }
    }
    

###总结

通过阅读 runtime 的源码，我们知道了 +load 和 +initialize
方法实现的细节，明白了它们的调用机制和各自的特点。下面我们绘制一张表格，以更加直观的方式来巩固我们对它们的理解：

<table border="1" width="100%">
        <tbody><tr>
            <th></th>        
            <th>+load</th>        
            <th>+initialize</th>        
        </tr>
        <tr>
            <td>调用时机</td>        
            <td>被添加到 runtime 时</td>        
            <td>收到第一条消息前，可能永远不调用</td>        
        </tr>
        <tr>
            <td>调用顺序</td>        
            <td>父类-&gt;子类-&gt;分类</td>        
            <td>父类-&gt;子类</td>        
        </tr>
        <tr>
            <td>调用次数</td>        
            <td>1次</td>        
            <td>多次</td>        
        </tr>
        <tr>
            <td>是否需要显式调用父类实现</td>        
            <td>否</td>        
            <td>否</td>        
        </tr>
        <tr>
            <td>是否沿用父类的实现</td>        
            <td>否</td>        
            <td>是</td>        
        </tr>
        <tr>
            <td>分类中的实现</td>        
            <td>类和分类都执行</td>        
            <td>覆盖类中的方法，只执行分类的实现</td>        
        </tr>
    </tbody></table>




<hr>







####<p>原文出处：<a href='http://blog.leichunfeng.com/blog/2016/06/20/objective-c-fast-enumeration-implementation-principle/' target='blank'>Objective-C Fast Enumeration 的实现原理</a></p>


在 Objective-C 2.0 中提供了快速枚举的语法，它是我们遍历集合元素的首选方法，因为它具有以下优点：

  * 比直接使用 `NSEnumerator` 更高效；
  * 语法非常简洁；
  * 如果集合在遍历的过程中被修改，它会抛出异常；
  * 可以同时执行多个枚举。

那么问题来了，它是如何做到的呢？我想，你应该也跟我一样，对 Objective-C 中快速枚举的实现原理非常感兴趣，事不宜迟，让我们来一探究竟吧。

###解析 NSFastEnumeration 协议

在 Objective-C 中，我们要想实现快速枚举就必须要实现 [NSFastEnumeration](https://developer.apple.com/library/mac/#documentation/Cocoa/Reference/NSFastEnumeration_protocol/Reference/NSFastEnumeration.html) 协议，在这个协议中，只声明了一个必须实现的方法：

       
    
    /**
     Returns by reference a C array of objects over which the sender should iterate, and as the return value the number of objects in the array.
    
     @param state  Context information that is used in the enumeration to, in addition to other possibilities, ensure that the collection has not been mutated.
     @param buffer A C array of objects over which the sender is to iterate.
     @param len    The maximum number of objects to return in stackbuf.
     
     @discussion The state structure is assumed to be of stack local memory, so you can recast the passed in state structure to one more suitable for your iteration.
    
     @return The number of objects returned in stackbuf. Returns 0 when the iteration is finished.
     */
    - (NSUInteger)countByEnumeratingWithState:(NSFastEnumerationState *)state
                                      objects:(id __unsafe_unretained [])stackbuf
                                        count:(NSUInteger)len
    

其中，结构体 `NSFastEnumerationState` 的定义如下：

    
    
    typedef struct {
        unsigned long state;
        id __unsafe_unretained __nullable * __nullable itemsPtr;
        unsigned long * __nullable mutationsPtr;
        unsigned long extra[5];
    } NSFastEnumerationState;
    

说实话，刚开始看到这个方法的时候，其实我是拒绝的，原因你懂的。好吧，先不吐槽了，言归正传，下面，我们将对这个方法进行全方位的剖析：

首先，我们需要了解的最重要的一点，那就是这个方法的目的是什么？概括地说，这个方法就是用于返回一系列的 C 数组，以供调用者进行遍历。为什么是一系列的 C数组呢？因为，在一个 `for/in` 循环中，这个方法其实会被调用多次，每一次调用都会返回一个 C 数组。至于为什么是 C 数组，那当然是为了提高效率了。

既然要返回 C数组，也就意味着我们需要返回一个数组的指针和数组的长度。是的，我想你应该已经猜到了，数组的长度就是通过这个方法的返回值来提供的，而数组的指针则是通过结构体`NSFastEnumerationState` 的 `itemsPtr` 字段进行返回的。所以，这两个值就一起定义了这个方法返回的 C 数组。

通常来说，`NSFastEnumeration`允许我们直接返回一个指向内部存储的指针，但是并非所有的数据结构都能够满足内存连续的要求。因此，`NSFastEnumeration`还为我们提供了另外一种实现方案，我们可以将元素拷贝到调用者提供的一个 C 数组上，即 `stackbuf` ，它的长度由参数 `len` 指定。

在本文的开头，我们提到了如果集合在遍历的过程中被修改的话，`NSFastEnumeration` 就会抛出异常。而这个功能就是通过
`mutationsPtr` 字段来实现的，它指向一个这样的值，这个值在集合被修改时会发现改变。因此，我们就可以利用它来判断集合在遍历的过程中是否被修改。

现在，我们还剩下 `NSFastEnumerationState` 中的 `state` 和 `extra`字段没有进行介绍。实际上，它们是调用者提供给被调用者自由使用的两个字段，调用者根本不关心这两个字段的值。因此，我们可以利用它们来存储任何对自身有用的值。

###揭密快速枚举的内部实现

说了这么多，感觉好像 `NSFastEnumeration`
是你设计的一样，你到底是怎么知道的呢？额，我说我是瞎猜的，你信么？好了，不开玩笑了。接下来，我们就一起来探究一下快速枚举的内部实现。假设，我们有一个`main.m` 文件，其中的代码如下：
    
    
    #import <Foundation/Foundation.h>
    
    int main(int argc, char * argv[]) {
        NSArray *array = @[ @1, @2, @3 ];
        for (NSNumber *number in array) {
            if ([number isEqualToNumber:@1]) {
                continue;
            }
            NSLog(@"%@", number);
            break;
        }
    }
    

接着，我们使用下面的 clang 命令将 `main.m` 文件重写成 C++ 代码：

    
    clang -rewrite-objc main.m
    

得到 `main.cpp` 文件，其中 `main` 函数的代码如下：

   
    
    int main(int argc, char * argv[]) {
        // 创建数组 @[ @1, @2, @3 ]
        NSArray *array = ((NSArray *(*)(Class, SEL, const ObjectType *, NSUInteger))(void *)objc_msgSend)(objc_getClass("NSArray"), sel_registerName("arrayWithObjects:count:"), (const id *)__NSContainer_literal(3U, ((NSNumber *(*)(Class, SEL, int))(void *)objc_msgSend)(objc_getClass("NSNumber"), sel_registerName("numberWithInt:"), 1), ((NSNumber *(*)(Class, SEL, int))(void *)objc_msgSend)(objc_getClass("NSNumber"), sel_registerName("numberWithInt:"), 2), ((NSNumber *(*)(Class, SEL, int))(void *)objc_msgSend)(objc_getClass("NSNumber"), sel_registerName("numberWithInt:"), 3)).arr, 3U);
    
        {
            NSNumber * number;
    
            // 初始化结构体 NSFastEnumerationState
            struct __objcFastEnumerationState enumState = { 0 };
    
            // 初始化数组 stackbuf
            id __rw_items[16];
    
            id l_collection = (id) array;
    
            // 第一次调用 - countByEnumeratingWithState:objects:count: 方法，形参和实参的对应关系如下：
            // state -> &enumState
            // stackbuf -> __rw_items
            // len -> 16
            _WIN_NSUInteger limit =
                ((_WIN_NSUInteger (*) (id, SEL, struct __objcFastEnumerationState *, id *, _WIN_NSUInteger))(void *)objc_msgSend)
                ((id)l_collection,
                sel_registerName("countByEnumeratingWithState:objects:count:"),
                &enumState, (id *)__rw_items, (_WIN_NSUInteger)16);
    
            if (limit) {
                // 获取 mutationsPtr 的初始值
                unsigned long startMutations = *enumState.mutationsPtr;
    
                // 外层的 do/while 循环，用于调用 - countByEnumeratingWithState:objects:count: 方法，获取 C 数组
                do {
                    unsigned long counter = 0;
    
                    // 内层的 do/while 循环，用于遍历获取到的 C 数组
                    do {
                        // 判断 mutationsPtr 的值是否有发生变化，如果有则使用 objc_enumerationMutation 函数抛出异常
                        if (startMutations != *enumState.mutationsPtr) objc_enumerationMutation(l_collection);
    
                        // 使用指针的算术运算获取相应的集合元素，这是快速枚举之所以高效的关键所在
                        number = (NSNumber *)enumState.itemsPtr[counter++];
    
                        {
                            if (((BOOL (*)(id, SEL, NSNumber *))(void *)objc_msgSend)((id)number, sel_registerName("isEqualToNumber:"), ((NSNumber *(*)(Class, SEL, int))(void *)objc_msgSend)(objc_getClass("NSNumber"), sel_registerName("numberWithInt:"), 1))) {
                                // continue 语句的实现，使用 goto 语句无条件转移到内层 do 语句的末尾，跳过中间的所有代码
                                goto __continue_label_1;
                            }
    
                            NSLog((NSString *)&__NSConstantStringImpl__var_folders_cr_xxw2w3rd5_n493ggz9_l4bcw0000gn_T_main_fc7b79_mi_0, number);
    
                            // break 语句的实现，使用 goto 语句无条件转移到最外层 if 语句的末尾，跳出嵌套的两层循环
                            goto __break_label_1;
                        };
    
                        // goto 语句标号，用来实现 continue 语句
                        __continue_label_1: ;
                    } while (counter < limit);
                } while ((limit =
                    ((_WIN_NSUInteger (*) (id, SEL, struct __objcFastEnumerationState *, id *, _WIN_NSUInteger))(void *)objc_msgSend)
                    ((id)l_collection,
                    sel_registerName("countByEnumeratingWithState:objects:count:"),
                    &enumState, (id *)__rw_items, (_WIN_NSUInteger)16)));
    
                number = ((NSNumber *)0);
    
                // goto 语句标号，用来实现 break 语句
                __break_label_1: ;
            } else {
                number = ((NSNumber *)0);
            }
        }
    }
    

如上代码所示，快速枚举其实就是用两层 `do/while` 循环来实现的，外层循环负责调用 `-
countByEnumeratingWithState:objects:count:` 方法，获取 C 数组，而内层循环则负责遍历获取到的 C数组。同时，我想你应该也注意到了它是如何利用 `mutationsPtr` 来检测集合在遍历过程中的突变的，以及使用 [objc_enumerationMutation](https://developer.apple.com/reference/objectivec/1418744-objc_enumerationmutation?language=objc) 函数来抛出异常。

正如我们前面提到的，在快速枚举的实现中，确实没有用到结构体 `NSFastEnumerationState` 中的 `state` 和 `extra`字段，它们只是提供给 `- countByEnumeratingWithState:objects:count:` 方法的实现者自由使用的字段。

值得一提的是，我特意在 `main.m` 中加入了 `continue` 和 `break` 语句。因此，我们有机会看到了在 `for/in`语句中是如何利用 goto 来实现 `continue` 和 `break` 语句的。

###实现 NSFastEnumeration 协议

看到这里，我相信你对 Objective-C 中快速枚举的实现原理已经有了一个比较清晰地认识。下面，我们就一起来动手实现一下`NSFastEnumeration` 协议。

我们前面已经提到了，`NSFastEnumeration` 在设计上允许我们使用两种不同的方式来实现它。如果集合中的元素在内存上是连续的，那么我们可以直接返回这段内存的首地址；如果不连续，比如链表，就只能使用调用者提供的 C 数组 `stackbuf` 了，将我们的元素拷贝到这个 C 数组上。

接下来，我们将通过一个自定义的集合类 `Array` ，来演示这两种不同的实现 `NSFastEnumeration` 协议的方式。**注**：完整的项目代
码可以在[这里](https://github.com/leichunfeng/FastEnumerationSample)找到。

     
    
    @interface Array : NSObject <NSFastEnumeration>
    
    - (instancetype)initWithCapacity:(NSUInteger)numItems;
    
    @end
    
    @implementation Array {
        std::vector<NSNumber *> _list;
    }
    
    - (instancetype)initWithCapacity:(NSUInteger)numItems {
        self = [super init];
        if (self) {
            for (NSUInteger i = 0; i < numItems; i++) {
                _list.push_back(@(random()));
            }
        }
        return self;
    }
    
    #define USE_STACKBUF 1
    
    - (NSUInteger)countByEnumeratingWithState:(NSFastEnumerationState *)state objects:(id __unsafe_unretained [])stackbuf count:(NSUInteger)len {
        // 这个方法的返回值，即我们需要返回的 C 数组的长度
        NSUInteger count = 0;
    
        // 我们前面已经提到了，这个方法是会被多次调用的
        // 因此，我们需要使用 state->state 来保存当前遍历到了 _list 的什么位置
        unsigned long countOfItemsAlreadyEnumerated = state->state;
    
        // 当 countOfItemsAlreadyEnumerated 为 0 时，表示第一次调用这个方法
        // 我们可以在这里做一些初始化的设置
        if (countOfItemsAlreadyEnumerated == 0) {
            // 我们前面已经提到了，state->mutationsPtr 是用来追踪集合在遍历过程中的突变的
            // 它不能为 NULL ，并且也不应该指向 self
            //
            // 这里，因为我们的 Array 类是不可变的，所以我们不需要追踪它的突变
            // 因此，我们的做法是将它指向 state->extra 的其中一个值
            // 因为我们知道 NSFastEnumeration 协议本身并没有用到 state->extra
            //
            // 但是，如果你的集合是可变的，那么你可以考虑将 state->mutationsPtr 指向一个内部变量
            // 而这个内部变量的值会在你的集合突变时发生变化
            state->mutationsPtr = &state->extra[0];
        }
    
    #if USE_STACKBUF
    
        // 判断我们是否已经遍历完 _list
        if (countOfItemsAlreadyEnumerated < _list.size()) {
            // 我们知道 state->itemsPtr 就是这个方法返回的 C 数组指针，它不能为 NULL
            // 在这里，我们将 state->itemsPtr 指向调用者提供的 C 数组 stackbuf
            state->itemsPtr = stackbuf;
    
            // 将 _list 中的元素填充到 stackbuf 中，直到以下两个条件中的任意一个满足时为止
            // 1. 已经遍历完 _list 中的所有元素
            // 2. 已经填充满 stackbuf
            while (countOfItemsAlreadyEnumerated < _list.size() && count < len) {
                // 取出 _list 中的元素填充到 stackbuf 中
                stackbuf[count] = _list[countOfItemsAlreadyEnumerated];
    
                // 更新我们的遍历位置
                countOfItemsAlreadyEnumerated++;
    
                // 更新我们返回的 C 数组的长度，使之与 state->itemsPtr 中的元素个数相匹配
                count++;
            }
        }
    
    #else
    
        // 判断我们是否已经遍历完 _list
        if (countOfItemsAlreadyEnumerated < _list.size()) {
            // 直接将 state->itemsPtr 指向内部的 C 数组指针，因为它的内存地址是连续的
            __unsafe_unretained const id * const_array = _list.data();
            state->itemsPtr = (__typeof__(state->itemsPtr))const_array;
    
            // 因为我们一次性返回了 _list 中的所有元素
            // 所以，countOfItemsAlreadyEnumerated 和 count 的值均为 _list 中的元素个数
            countOfItemsAlreadyEnumerated = _list.size();
            count = _list.size();
        }
    
    #endif
    
        // 将本次调用得到的 countOfItemsAlreadyEnumerated 保存到 state->state 中
        // 因为 NSFastEnumeration 协议本身并没有用到 state->state
        // 所以，我们可以将这个值保留到下一次调用
        state->state = countOfItemsAlreadyEnumerated;
    
        // 返回 C 数组的长度
        return count;
    }
    
    @end
    

我已经在上面的代码中添加了必要的注释，相信你理解起来应该没有什么难度。不过，值得一提的是，在第二种方式的实现中，我们用到了 ARC
下不同所有权对象之间的相互转换，代码如下：

    
    __unsafe_unretained const id * const_array = _list.data();
    state->itemsPtr = (__typeof__(state->itemsPtr))const_array;
    

其实，这里面涉及到两次类型转换，第一次是从 `__strong NSNumber *` 类型转换到 `__unsafe_unretained const
id *` 类型，第二次是从 `__unsafe_unretained const id *` 类型转换到 `id __unsafe_unretained*` 类型，更多信息可以查看 [AutomaticReferenceCounting](http://clang.llvm.org/docs/AutomaticReferenceCounting.html) 中的 4.3.3 小节。

另外，我在前面的文章[《ReactiveCocoa v2.5
源码解析之架构总览》](http://blog.leichunfeng.com/blog/2015/12/25/reactivecocoa-v2-dot-5-yuan-ma-jie-xi-zhi-jia-gou-zong-lan/)中，已经有提到过，[ReactiveCocoa](https://github.com/ReactiveCocoa/ReactiveCocoa/tree/v2.5) 中的 [RACSequence](https://github.com/ReactiveCocoa/ReactiveCocoa/blob/v2.5/ReactiveCocoa/RACSequence.m) 类其实是实现了`NSFastEnumeration` 协议的。因为 `RACSequence`中的元素在内存上并不连续，所以它采用的是第一种实现方式。对此感兴趣的同学，可以去看看它的实现源码，这里不再赘述。

###总结

本文从 `NSFastEnumeration` 协议的定义出发，解析了 `\-
countByEnumeratingWithState:objects:count:` 方法中的返回值以及各个参数的含义；接着，我们使用 `clang -rewrite-objc` 命令探究了快速枚举的内部实现；最后，通过一个自定义的集合类 `Array` 演示了两种实现`NSFastEnumeration` 协议的方式，希望本文能够对你有所帮助。

###参考链接

<https://www.mikeash.com/pyblog/friday-qa-2010-04-16-implementing-fast-enumeration.html> <https://zh.wikipedia.org/wiki/Objective-C#.E5.BF.AB.E9.80.9F.E6.9E.9A.E4.B8.BE> <https://developer.apple.com/library/mac/documentation/Cocoa/Conceptual/Collections/Articles/Enumerators.html#//apple_ref/doc/uid/20000135-SW1>

