<!--BEGIN_DATA
{
    "create_date": "2016-06-14 10:27", 
    "modify_date": "2016-06-14 10:27", 
    "is_top": "0", 
    "summary": "GCD(Grand Central Dispatch)教程", 
    "tags": "iOS", 
    "file_name": "GCD(Grand Central Dispatch)教程.md"
}
END_DATA-->

####<p>原文出处：<a href='http://www.dreamingwish.com/article/gcdgrand-central-dispatch-jiao-cheng.html' target='blank'>GCD(Grand Central Dispatch)教程</a></p>

#GCD入门（一）: 基本概念和Dispatch Queue


**什么是GCD？**

Grand Central Dispatch或者GCD，是一套低层API，提供了一种新的方法来进行并发程序编写。从基本功能上讲，GCD有点像NSOperat
ionQueue，他们都允许程序将任务切分为多个单一任务然后提交至工作队列来并发地或者串行地执行。GCD比之NSOpertionQueue更底层更高效，并且
它不是Cocoa框架的一部分。

除了代码的平行执行能力，GCD还提供高度集成的事件控制系统。可以设置句柄来响应文件描述符、mach ports（_Mach port_ 用于 OS
X上的进程间通讯）、进程、计时器、信号、用户生成事件。这些句柄通过GCD来并发执行。

GCD的API很大程度上基于block，当然，GCD也可以脱离block来使用，比如使用传统c机制提供函数指针和上下文指针。实践证明，当配合block使用时
，GCD非常简单易用且能发挥其最大能力。

你可以在Mac上敲命令“man dispatch”来获取GCD的文档。

**为何使用?**

GCD提供很多超越传统多线程编程的优势：

  1. **易用:** GCD比之thread跟简单易用。由于GCD基于work unit而非像thread那样基于运算，所以GCD可以控制诸如_等待任务结束_、_监视文件描述符_、_周期执行代码以及工作挂起_等任务。基于block的血统导致它能极为简单得在不同代码作用域之间传递上下文。
  2. **效率:** GCD被实现得如此轻量和优雅，使得它在很多地方比之专门创建消耗资源的线程更实用且快速。这关系到易用性：导致GCD易用的原因有一部分在于你可以不用担心太多的效率问题而仅仅使用它就行了。
  3. **性能:** GCD自动根据系统负载来增减线程数量，这就减少了上下文切换以及增加了计算效率。

**Dispatch Objects**

尽管GCD是纯c语言的，但它被组建成面向对象的风格。GCD对象被称为dispatch object。Dispatch
object像Cocoa对象一样是引用计数的。使用dispatch_release和dispatch_retain函数来操作dispatch
object的引用计数来进行内存管理。但主意不像Cocoa对象，dispatch
object并不参与垃圾回收系统，所以即使开启了GC，你也必须手动管理GCD对象的内存。

Dispatch queues 和 dispatch
sources（后面会介绍到）可以被挂起和恢复，可以有一个相关联的任意上下文指针，可以有一个相关联的任务完成触发函数。可以查阅“man
dispatch_object”来获取这些功能的更多信息。

**Dispatch Queues**

GCD的基本概念就是dispatch queue。dispatch queue是一个对象，它可以接受任务，并将任务以先到先执行的顺序来执行。dispatch
queue可以是并发的或串行的。并发任务会像NSOperationQueue那样基于系统负载来合适地并发进行，串行队列同一时间只执行单一任务。

GCD中有三种队列类型：

  1. **The main queue:** 与主线程功能相同。实际上，提交至main queue的任务会在主线程中执行。main queue可以调用dispatch_get_main_queue()来获得。因为main queue是与主线程相关的，所以这是一个串行队列。
  2. **Global queues:** 全局队列是并发队列，并由整个进程共享。进程中存在三个全局队列：高、中（默认）、低三个优先级队列。可以调用dispatch_get_global_queue函数传入优先级来访问队列。
  3. **用户队列:** 用户队列 (GCD并不这样称呼这种队列, 但是没有一个特定的名字来形容这种队列，所以我们称其为用户队列) 是用函数 `dispatch_queue_create` 创建的队列. 这些队列是串行的。正因为如此，它们可以用来完成同步机制, 有点像传统线程中的mutex。

**创建队列**

要使用用户队列，我们首先得创建一个。调用函数dispatch_queue_create就行了。函数的第一个参数是一个标签，这纯是为了debug。Apple建
议我们使用倒置域名来命名队列，比如“com.dreamingwish.subsystem.task”。这些名字会在崩溃日志中被显示出来，也可以被调试器调用，
这在调试中会很有用。第二个参数目前还不支持，传入NULL就行了。

**提交 Job**

向一个队列提交Job很简单：调用dispatch_async函数，传入一个队列和一个block。队列会在轮到这个block执行时执行这个block的代码。下
面的例子是一个在后台执行一个巨长的任务：

    
    
     dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
            [self goDoSomethingLongAndInvolved];
            NSLog(@"Done doing something long and involved");
    });

`dispatch_async` 函数会立即返回, block会在后台异步执行。

当然，通常，任务完成时简单地NSLog个消息不是个事儿。在典型的Cocoa程序中，你很有可能希望在任务完成时更新界面，这就意味着需要在主线程中执行一些代码。
你可以简单地完成这个任务——使用嵌套的dispatch，在外层中执行后台任务，在内层中将任务dispatch到main queue：

    
    
    dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
            [self goDoSomethingLongAndInvolved];
            dispatch_async(dispatch_get_main_queue(), ^{
                [textField setStringValue:@"Done doing something long and involved"];
            });
    });

还有一个函数叫dispatch_sync，它干的事儿和dispatch_async相同，但是它会等待block中的代码执行完成并返回。结合 __block类
型修饰符，可以用来从执行中的block获取一个值。例如，你可能有一段代码在后台执行，而它需要从界面控制层获取一个值。那么你可以使用dispatch_sync
简单办到：

    
    
    __block NSString *stringValue;
    dispatch_sync(dispatch_get_main_queue(), ^{
            // __block variables aren't automatically retained
            // so we'd better make sure we have a reference we can keep
            stringValue = [[textField stringValue] copy];
    });
    [stringValue autorelease];
    // use stringValue in the background now

我们还可以使用更好的方法来完成这件事——使用更“异步”的风格。不同于取界面层的值时要阻塞后台线程，你可以使用嵌套的block来中止后台线程，然后从主线程中获
取值，然后再将后期处理提交至后台线程：

    
    
        dispatch_queue_t bgQueue = myQueue;
        dispatch_async(dispatch_get_main_queue(), ^{
            NSString *stringValue = [[[textField stringValue] copy] autorelease];
            dispatch_async(bgQueue, ^{
                // use stringValue in the background now
            });
        });

取决于你的需求，myQueue可以是用户队列也可以使全局队列。



**不再使用锁（Lock）**

用户队列可以用于替代锁来完成同步机制。在传统多线程编程中，你可能有一个对象要被多个线程使用，你需要一个锁来保护这个对象：

    
    
        NSLock *lock;
    

访问代码会像这样：

    
    
        - (id)something
        {
            id localSomething;
            [lock lock];
            localSomething = [[something retain] autorelease];
            [lock unlock];
            return localSomething;
        }
        - (void)setSomething:(id)newSomething
        {
            [lock lock];
            if(newSomething != something)
            {
                [something release];
                something = [newSomething retain];
                [self updateSomethingCaches];
            }
            [lock unlock];
        }

使用GCD，可以使用queue来替代：

    
    
        dispatch_queue_t queue;

要用于同步机制，queue必须是一个用户队列(从OS X v10.7和iOS 4.3开始，还必须指定为DISPATCH_QUEUE_SERIAL)，而非全局
队列，所以使用`dispatch_queue_create`初始化一个。然后可以用`dispatch_async` 或者
`dispatch_sync`将共享数据的访问代码封装起来：

    
    
        - (id)something
        {
            __block id localSomething;
            dispatch_sync(queue, ^{
                localSomething = [something retain];
            });
            return [localSomething autorelease];
        }
        - (void)setSomething:(id)newSomething
        {
            dispatch_async(queue, ^{
                if(newSomething != something)
                {
                    [something release];
                    something = [newSomething retain];
                    [self updateSomethingCaches];
                }
            });
        }

 值得注意的是dispatch queue是非常轻量级的，所以你可以大用特用，就像你以前使用lock一样。

现在你可能要问：“这样很好，但是有意思吗？我就是换了点代码办到了同一件事儿。”

实际上，使用GCD途径有几个好处：

  1. **平行计算:** 注意在第二个版本的代码中， `-setSomething:是怎么使用dispatch_async的。调用 `-setSomething:会立即返回，然后这一大堆工作会在后台执行。如果updateSomethingCaches是一个很费时费力的任务，且调用者将要进行一项处理器高负荷任务，那么这样做会很棒。``
  2. **安全:** 使用GCD，我们就不可能意外写出具有不成对Lock的代码。在常规Lock代码中，我们很可能在解锁之前让代码返回了。使用GCD，队列通常持续运行，你必将归还控制权。
  3. **控制:** 使用GCD我们可以挂起和恢复dispatch queue，而这是基于锁的方法所不能实现的。我们还可以将一个用户队列指向另一个dspatch queue，使得这个用户队列继承那个dispatch queue的属性。使用这种方法，队列的优先级可以被调整——通过将该队列指向一个不同的全局队列，若有必要的话，这个队列甚至可以被用来在主线程上执行代码。
  4. **集成:** GCD的事件系统与dispatch queue相集成。对象需要使用的任何事件或者计时器都可以从该对象的队列中指向，使得这些句柄可以自动在该队列上执行，从而使得句柄可以与对象自动同步。

**总结**

现在你已经知道了GCD的基本概念、怎样创建dispatch queue、怎样提交Job至dispatch
queue以及怎样将队列用作线程同步。接下来我会向你展示如何使用GCD来编写平行执行代码来充分利用多核系统的性能^
^。我还会讨论GCD更深层的东西，包括事件系统和queue targeting。


<hr>


#GCD入门（二）: 多核心的性能


**概念**

为了在单一进程中充分发挥多核的优势，我们有必要使用多线程技术（我们没必要去提多进程，这玩意儿和GCD没关系）。在低层，GCD全局dispatch queue
仅仅是工作线程池的抽象。这些队列中的Block一旦可用，就会被dispatch到工作线程中。提交至用户队列的Block最终也会通过全局队列进入相同的工作线程
池（除非你的用户队列的目标是主线程，但是为了提高运行速度，我们绝不会这么干）。

有两种途径来通过GCD“榨取”多核心系统的性能：将单一任务或者一组相关任务并发至全局队列中运算；将多个不相关的任务或者关联不紧密的任务并发至用户队列中运算；

**全局队列**

设想下面的循环：

    
    
        for(id obj in array)
            [self doSomethingIntensiveWith:obj];

假定 `-doSomethingIntensiveWith:`
是线程安全的且可以同时执行多个.一个array通常包含多个元素，这样的话，我们可以很简单地使用GCD来平行运算：

    
    
        dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
        for(id obj in array)
            dispatch_async(queue, ^{
                [self doSomethingIntensiveWith:obj];
            });

如此简单，我们已经在多核心上运行这段代码了。

当然这段代码并不完美。有时候我们有一段代码要像这样操作一个数组，但是在操作完成后，我们还需要对操作结果进行其他操作：

    
    
        for(id obj in array)
            [self doSomethingIntensiveWith:obj];
        [self doSomethingWith:array];

这时候使用GCD的 `dispatch_async` 就悲剧了.我们还不能简单地使用`dispatch_sync来解决这个问题`,
因为这将导致每个迭代器阻塞，就完全破坏了平行计算。

解决这个问题的一种方法是使用dispatch group。一个dispatch group可以用来将多个block组成一组以监测这些Block全部完成或者等
待全部完成时发出的消息。使用函数dispatch_group_create来创建，然后使用函数dispatch_group_async来将block提交至一
个dispatch queue，同时将它们添加至一个组。所以我们现在可以重新编码：

    
    
        dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
        dispatch_group_t group = dispatch_group_create();
        for(id obj in array)
            dispatch_group_async(group, queue, ^{
                [self doSomethingIntensiveWith:obj];
            });
        dispatch_group_wait(group, DISPATCH_TIME_FOREVER);
        dispatch_release(group);
        [self doSomethingWith:array];

如果这些工作可以异步执行，那么我们可以更风骚一点，将函数`-doSomethingWith:放在后台执行。我们使用dispatch_group_async函
数建立一个block在组完成后执行：`

    
    
        dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
        dispatch_group_t group = dispatch_group_create();
        for(id obj in array)
            dispatch_group_async(group, queue, ^{
                [self doSomethingIntensiveWith:obj];
            });
        dispatch_group_notify(group, queue, ^{
            [self doSomethingWith:array];
        });
        dispatch_release(group);

不仅所有数组元素都会被平行操作，后续的操作也会异步执行，并且这些异步运算都会将程序的其他部分的负载考虑在内。注意如果`-doSomethingWith:需要
在主线程中执行，比如操作GUI，那么我们只要将main queue而非全局队列传给dispatch_group_notify函数就行了。`



对于同步执行，GCD提供了一个简化方法叫做dispatch_apply。这个函数调用单一block多次，并平行运算，然后等待所有运算结束，就像我们想要的那样
：

    
    
    dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
        dispatch_apply([array count], queue, ^(size_t index){
            [self doSomethingIntensiveWith:[array objectAtIndex:index]];
        });
        [self doSomethingWith:array];

这很棒，但是异步咋办？dispatch_apply函数可是没有异步版本的。但是我们使用的可是一个为异步而生的API啊！所以我们只要用dispatch_asy
nc函数将所有代码推到后台就行了：

    
    
        dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
        dispatch_async(queue, ^{
            dispatch_apply([array count], queue, ^(size_t index){
                [self doSomethingIntensiveWith:[array objectAtIndex:index]];
            });
            [self doSomethingWith:array];
        });

简单的要死！



这种方法的关键在于确定我们的代码是在一次对不同的数据片段进行相似的操作。如果你确定你的任务是线程安全的（不在本篇讨论范围内）那么你可以使用GCD来重写你的循
环了，更平行更风骚。

要看到性能提升，你还得进行一大堆工作。比之线程，GCD是轻量和低负载的，但是将block提交至queue还是很消耗资源的——block需要被拷贝和入队，同时
适当的工作线程需要被通知。不要将一张图片的每个像素作为一个block提交至队列，GCD的优点就半途夭折了。如果你不确定，那么请进行试验。将程序平行计算化是一
种优化措施，在修改代码之前你必须再三思索，确定修改是有益的（还有确保你修改了正确的地方）。

**Subsystem并发运算**

前面的章节我们讨论了在程序的单个subsystem中发挥多核心的优势。下来我们要跨越多个子系统。

例如，设想一个程序要打开一个包含meta信息的文档。文档数据本身需要解析并转换至模型对象来显示，meta信息也需要解析和转换。但是，文档数据和meta信息不
需要交互。我们可以为文档和meta各创建一个dispatch
queue，然后并发执行。文档和meta的解析代码都会各自串行执行，从而不用考虑线程安全（只要没有文档和meta之间共享的数据），但是它们还是并发执行的。

一旦文档打开了，程序需要响应用户操作。例如，可能需要进行拼写检查、代码高亮、字数统计、自动保存或者其他什么。如果每个任务都被实现为在不同的dispatch
queue中执行，那么这些任务会并发执行，并各自将其他任务的运算考虑在内（respect to each other），从而省去了多线程编程的麻烦。

使用dispatch
source（下次我会讲到），我们可以让GCD将事件直接传递给用户队列。例如，程序中监视socket连接的代码可以被置于它自己的dispatch
queue中，这样它会异步执行，并且执行时会将程序其他部分的运算考虑在内。另外，如果使用用户队列的话，这个模块会串行执行，简化程序。

**结论**

我们讨论了如何使用GCD来提升程序性能以及发挥多核系统的优势。尽管我们需要比较谨慎地编写并发程序，GCD还是使得我们能更简单地发挥系统的可用计算资源。

下一篇中，我们将讨论dispatch source，也就是GCD的监视内部、外部事件的机制。


<hr>



#GCD入门（三）: Dispatch Sources


**何为Dispatch Sources**

简单来说，dispatch source是一个监视某些类型事件的对象。当这些事件发生时，它自动将一个block放入一个dispatch
queue的执行例程中。

说的貌似有点不清不楚。我们到底讨论哪些事件类型？

下面是GCD 10.6.0版本支持的事件：

  1. Mach port send right state changes.
  2. Mach port receive right state changes.
  3. External process state change.
  4. File descriptor ready for read.
  5. File descriptor ready for write.
  6. Filesystem node event.
  7. POSIX signal.
  8. Custom timer.
  9. Custom event.

这是一堆很有用的东西，它支持所有kqueue所支持的事件（kqueue是什么？见<http://en.wikipedia.org/wiki/Kqueue>）
以及mach（mach是什么？见<http://en.wikipedia.org/wiki/Mach_(kernel)>）端口、内建计时器支持（这样我们就不
用使用超时参数来创建自己的计时器）和用户事件。



**用户事件**

这些事件里面多数都可以从名字中看出含义，但是你可能想知道啥叫用户事件。简单地说，这种事件是由你调用dispatch_source_merge_data函数来
向自己发出的信号。

这个名字对于一个发出事件信号的函数来说，太怪异了。这个名字的来由是GCD会在事件句柄被执行之前自动将多个事件进行联结。你可以将数据“拼接”至dispatch
source中任意次，并且如果dispatch queue在这期间繁忙的话，GCD只会调用该句柄一次（不要觉得这样会有问题，看完下面的内容你就明白了）。

用户事件有两种： `DISPATCH_SOURCE_TYPE_DATA_ADD` 和
`DISPATCH_SOURCE_TYPE_DATA_OR`.用户事件源有个 `unsigned long data`属性，我们将一个 `unsigned
long`传入 `dispatch_source_merge_data`。当使用 `_ADD`版本时，事件在联结时会把这些数字相加。当使用 `_OR`版本时
，事件在联结时会把这些数字逻辑与运算。当事件句柄执行时，我们可以使用dispatch_source_get_data函数访问当前值，然后这个值会被重置为0。

让我假设一种情况。假设一些异步执行的代码会更新一个进度条。因为主线程只不过是GCD的另一个dispatch queue而已，所以我们可以将GUI更新工作pu
sh到主线程中。然而，这些事件可能会有一大堆，我们不想对GUI进行频繁而累赘的更新，理想的情况是当主线程繁忙时将所有的改变联结起来。

用dispatch source就完美了，使用DISPATCH_SOURCE_TYPE_DATA_ADD，我们可以将工作拼接起来，然后主线程可以知道从上一次
处理完事件到现在一共发生了多少改变，然后将这一整段改变一次更新至进度条。

啥也不说了，上代码：

    
    
        dispatch_source_t source = dispatch_source_create(DISPATCH_SOURCE_TYPE_DATA_ADD, 0, 0, dispatch_get_main_queue());
        dispatch_source_set_event_handler(source, ^{
            [progressIndicator incrementBy:dispatch_source_get_data(source)];
        });
        dispatch_resume(source);
        dispatch_apply([array count], globalQueue, ^(size_t index) {
            // do some work on data at index
            dispatch_source_merge_data(source, 1);
        });

 （对于这段代码，我很想说点什么，我第一次用dispatch source时，我纠结了很久很久，真让人蛋疼：**Dispatch
source启动时默认状态是挂起的，我们创建完毕之后得主动恢复，否则事件不会被传递，也不会被执行**）

假设你已经将进度条的min/max值设置好了，那么这段代码就完美了。数据会被并发处理。当每一段数据完成后，会通知dispatch
source并将dispatch source data加1，这样我们就认为一个单元的工作完成了。事件句柄根据已完成的工作单元来更新进度条。若主线程比较空闲
并且这些工作单元进行的比较慢，那么事件句柄会在每个工作单元完成的时候被调用，实时更新。如果主线程忙于其他工作，或者工作单元完成速度很快，那么完成事件会被联结
起来，导致进度条只在主线程变得可用时才被更新，并且一次将积累的改变更新至GUI。

现在你可能会想，听起来倒是不错，但是要是我不想让事件被联结呢？有时候你可能想让每一次信号都会引起响应，什么后台的智能玩意儿统统不要。啊。。其实很简单的，别把
自己绕进去了。如果你想让每一个信号都得到响应，那使用dispatch_async函数不就行了。实际上，使用的dispatch
source而不使用dispatch_async的唯一原因就是利用联结的优势。

**内建事件**

上面就是怎样使用用户事件，那么内建事件呢？看看下面这个例子，用GCD读取标准输入：

    
    
        dispatch_queue_t globalQueue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
        dispatch_source_t stdinSource = dispatch_source_create(DISPATCH_SOURCE_TYPE_READ,
                                                               STDIN_FILENO,
                                                               0,
                                                               globalQueue);
        dispatch_source_set_event_handler(stdinSource, ^{
            char buf[1024];
            int len = read(STDIN_FILENO, buf, sizeof(buf));
            if(len > 0)
                NSLog(@"Got data from stdin: %.*s", len, buf);
        });
        dispatch_resume(stdinSource);

 简单的要死！因为我们使用的是全局队列，句柄自动在后台执行，与程序的其他部分并行，这意味着对这种情况的提速：事件进入程序时，程序正在处理其他事务。

这是标准的UNIX方式来处理事务的好处，不用去写loop。如果使用经典的
`read`调用，我们还得万分留神，因为返回的数据可能比请求的少，还得忍受无厘头的“errors”，比如 `EINTR`
(系统调用中断)。使用GCD，我们啥都不用管，就从这些蛋疼的情况里解脱了。如果我们在文件描述符中留下了未读取的数据，GCD会再次调用我们的句柄。

对于标准输入，这没什么问题，但是对于其他文件描述符，我们必须考虑在完成读写之后怎样清除描述符。对于dispatch source还处于活跃状态时，我们决不能
关闭描述符。如果另一个文件描述符被创建了（可能是另一个线程创建的）并且新的描述符刚好被分配了相同的数字，那么你的dispatch
source可能会在不应该的时候突然进入读写状态。de这个bug可不是什么好玩的事儿。

适当的清除方式是使用 `dispatch_source_set_cancel_handler`，并传入一个block来关闭文件描述符。然后我们使用
`dispatch_source_cancel`来取消dispatch source，使得句柄被调用，然后文件描述符被关闭。

使用其他dispatch source类型也差不多。总的来说，你提供一个source（mach
port、文件描述符、进程ID等等）的区分符来作为diapatch source的句柄。mask参数通常不会被使用，但是对于
`DISPATCH_SOURCE_TYPE_PROC`
来说mask指的是我们想要接受哪一种进程事件。然后我们提供一个句柄，然后恢复这个source（前面我加粗字体所说的，得先恢复），搞定。dispatch
source也提供一个特定于source的data，我们使用 `dispatch_source_get_data`函数来访问它。例如，文件描述符会给出大致可
用的字节数。进程source会给出上次调用之后发生的事件的mask。具体每种source给出的data的含义，看man page吧。

**计时器**

计时器事件稍有不同。它们不使用handle/mask参数，计时器事件使用另外一个函数 `dispatch_source_set_timer`
来配置计时器。这个函数使用三个参数来控制计时器触发：

 `start`参数控制计时器第一次触发的时刻。参数类型是 `dispatch_time_t`，这是一个opaque类型，我们不能直接操作它。我们得需要
`dispatch_time` 和  `dispatch_walltime` 函数来创建它们。另外，常量  `DISPATCH_TIME_NOW` 和
`DISPATCH_TIME_FOREVER` 通常很有用。

 `interval`参数没什么好解释的。

 `leeway`参数比较有意思。这个参数告诉系统我们需要计时器触发的精准程度。所有的计时器都不会保证100%精准，这个参数用来告诉系统你希望系统保证精准的
努力程度。如果你希望一个计时器没五秒触发一次，并且越准越好，那么你传递0为参数。另外，如果是一个周期性任务，比如检查email，那么你会希望每十分钟检查一次
，但是不用那么精准。所以你可以传入60ull * NSEC_PER_SEC，告诉系统60秒的误差是可接受的。

这样有什么意义呢？简单来说，就是降低资源消耗。如果系统可以让cpu休息足够长的时间，并在每次醒来的时候执行一个任务集合，而不是不断的醒来睡去以执行任务，那么
系统会更高效。如果传入一个比较大的leeway给你的计时器，意味着你允许系统拖延你的计时器来将计时器任务与其他任务联合起来一起执行。

**总结**

现在你知道怎样使用GCD的dispatch source功能来监视文件描述符、计时器、联结的用户事件以及其他类似的行为。由于dispatch
source完全与dispatch queue相集成，所以你可以使用任意的dispatch queue。你可以将一个dispatch
source的句柄在主线程中执行、在全局队列中并发执行、或者在用户队列中串行执行（执行时会将程序的其他模块的运算考虑在内）。

下一篇我会讨论如何对dispatch queue进行挂起、恢复、重定目标操作；如何使用dispatch
semaphore；如何使用GCD的一次性初始化功能。



<hr>


#GCD入门（四）: 完结


**Dispatch Queue挂起**

dispatch queue可以被挂起和恢复。使用 `dispatch_suspend`函数来挂起，使用  `dispatch_resume`
函数来恢复。这两个函数的行为是如你所愿的。另外，这两个函数也可以用于dispatch source。

一个要注意的地方是，dispatch queue的挂起是block粒度的。换句话说，挂起一个queue并不会将当前正在执行的block挂起。它会允许当前执行
的block执行完毕，然后后续的block不再会被执行，直至queue被恢复。

还有一个注意点：从man页上得来的：如果你挂起了一个queue或者source，那么销毁它之前，必须先对其进行恢复。

**Dispatch Queue目标指定**

所有的用户队列都有一个目标队列概念。从本质上讲，一个用户队列实际上是不执行任何任务的，但是它会将任务传递给它的目标队列来执行。通常，目标队列是默认优先级的全
局队列。

用户队列的目标队列可以用函数 `dispatch_set_target_queue`来修改。我们可以将任意dispatch queue传递给这个函数，甚至可
以是另一个用户队列，只要别构成循环就行。这个函数可以用来设定用户队列的优先级。比如我们可以将用户队列的目标队列设定为低优先级的全局队列，那么我们的用户队列中
的任务都会以低优先级执行。高优先级也是一样道理。

有一个用途，是将用户队列的目标定为main queue。这会导致所有提交到该用户队列的block在主线程中执行。这样做来替代直接在主线程中执行代码的好处在于
，我们的用户队列可以单独地被挂起和恢复，还可以被重定目标至一个全局队列，然后所有的block会变成在全局队列上执行（只要你确保你的代码离开主线程不会有问题）
。

还有一个用途，是将一个用户队列的目标队列指定为另一个用户队列。这样做可以强制多个队列相互协调地串行执行，这样足以构建一组队列，通过挂起和暂停那个目标队列，我
们可以挂起和暂停整个组。想象这样一个程序：它扫描一组目录并且加载目录中的内容。为了避免磁盘竞争，我们要确定在同一个物理磁盘上同时只有一个文件加载任务在执行。
而希望可以同时从不同的物理磁盘上读取多个文件。要实现这个，我们要做的就是创建一个dispatch queue结构，该结构为磁盘结构的镜像。

首先，我们会扫描系统并找到各个磁盘，为每个磁盘创建一个用户队列。然后扫描文件系统，并为每个文件系统创建一个用户队列，将这些用户队列的目标队列指向合适的磁盘用
户队列。最后，每个目录扫描器有自己的队列，其目标队列指向目录所在的文件系统的队列。目录扫描器枚举自己的目录并为每个文件向自己的队列提交一个block。由于整
个系统的建立方式，就使得每个物理磁盘被串行访问，而多个物理磁盘被并行访问。除了队列初始化过程，我们根本不需要手动干预什么东西。

**信号量**

dispatch的信号量是像其他的信号量一样的，如果你熟悉其他多线程系统中的信号量，那么这一节的东西再好理解不过了。

信号量是一个整形值并且具有一个初始计数值，并且支持两个操作：信号通知和等待。当一个信号量被信号通知，其计数会被增加。当一个线程在一个信号量上等待时，线程会被
阻塞（如果有必要的话），直至计数器大于零，然后线程会减少这个计数。

我们使用函数  `dispatch_semaphore_create` 来创建dispatch信号量，使用函数
`dispatch_semaphore_signal` 来信号通知，使用函数 `dispatch_semaphore_wait`
来等待。这些函数的man页有两个很好的例子，展示了怎样使用信号量来同步任务和有限资源访问控制。

**单次初始化**

GCD还提供单词初始化支持，这个与pthread中的函数  `pthread_once`
很相似。GCD提供的方式的优点在于它使用block而非函数指针，这就允许更自然的代码方式：

这个特性的主要用途是惰性单例初始化或者其他的线程安全数据共享。典型的单例初始化技术看起来像这样（线程安全的）：

    
    
        + (id)sharedWhatever
        {
            static Whatever *whatever = nil;
            @synchronized([Whatever class])
            {
                if(!whatever)
                    whatever = [[Whatever alloc] init];
            }
            return whatever;
        }

这挺好的，但是代价比较昂贵；每次调用  `+sharedWhatever`
函数都会付出取锁的代价，即使这个锁只需要进行一次。确实有更风骚的方式来实现这个，使用类似双向锁或者是原子操作的东西，但是这样挺难弄而且容易出错。

使用GCD，我们可以这样重写上面的方法，使用函数 `dispatch_once`：

    
    
        + (id)sharedWhatever
        {
            static dispatch_once_t pred;
            static Whatever *whatever = nil;
            dispatch_once(&pred, ^{
                whatever = [[Whatever alloc] init];
            });
            return whatever;
        }

这个稍微比 `@synchronized`方法简单些，并且GCD确保以更快的方式完成这些检测，它保证block中的代码在任何线程通过
`dispatch_once` 调用之前被执行，但它不会强制每次调用这个函数都让代码进行同步控制。实际上，如果你去看这个函数所在的头文件，你会发现目前它的实
现其实是一个宏，进行了内联的初始化测试，这意味着通常情况下，你不用付出函数调用的负载代价，并且会有更少的同步控制负载。

> 注意：dispatch_once会确保block中的代码只执行一次，这意味着，假如你将whatever指针移到class外，然后写一个叫releaseW
hatever的方法来释放并置nil，然后企图再次调用sharedWhatever来重新生成这个单例，你讲得到nil。

**结论**

这一章，我们介绍了dispatch queue的挂起、恢复和目标重定，以及这些功能的一些用途。另外，我们还介绍了如何使用dispatch
信号量和单次初始化功能。到此，我已经完成了GCD如何运作以及如何使用的介绍。


<hr>


#GCD外传：dispatch_once(上)


相信大家对`dispatch_once`都不陌生了，这一篇我将和大家一起探究`dispatch_once`的更多细节。

`dispatch_once`的作用正如其名：对于某个任务执行一次，且只执行一次。
`dispatch_once`函数有两个参数，第一个参数`predicate`用来保证执行一次，第二个参数是要执行一次的任务block。

    
    
    static dispatch_once_t predicate;
    dispatch_once(&predicate, ^{
        // some one-time task
    });
    

`dispatch_once`被广泛使用在单例、缓存等代码中，用以保证在初始化时执行一次某任务。

`dispatch_once`在单线程程序中毫无意义，但在多线程程序中，其低负载、高可依赖性、接口简单等特性，赢得了广大消费者的一致五星好评。

## 本系列中我将和大家一起一步步分析`dispatch_once`的低负载特性。

要讨论`dispatch_once`的低负载性，我们要讨论三种场景：

  1. 第一次执行，block需要被调用，调用结束后需要置标记变量
  2. 非第一次执行，而此时#1尚未完成，线程需要等待#1完成
  3. 非第一次执行，而此时#1已经完成，线程直接跳过block而进行后续任务

 对于场景#1，整体任务的效率瓶颈完全不在于`dispatch_once`，而在于block本身占用的cpu时间，并且也只会发生一次。

对于场景#2，发生的次数并不会很多，甚至很多时候一次都不会发生，假如发生了，那么也只是一个符合预期的行为：后来的线程需要等待第一线程完成。即使你写一个受虐型
的单元测试来故意模拟场景#2，也不能说明什么问题，得不到的永远在骚动，被偏爱的都有恃无恐。

对于场景#3，在程序进行过程中，可能发生成千上万次或者天文数字次，这才是效率提升的关键之处，下面我将细细道来。

### 一、需求的初衷

`dispatch_once`本来是被用作第一次的执行保护，等第一次执行完毕之后，其职责就完成了，作为程序设计者，当然希望它对后续执行没有任何影响，但这是做
不到的，所以只能寄希望于尽量降低后续调用的负载。

负载的Benchmark

对于后续调用的负载，到底要降低到什么程度，需要一个基准值，负荷最低的空白对照就是非线程安全的纯if判断语句了，在我的电脑上，一次包含if判断语句的函数单例返
回大概在0.5纳秒左右，而`dispatch_once`确实做到了接近这个数值，有兴趣可以亲自写一段测试代码来试试。

    
    
    //dispatch_once
    static id object;
    static dispatch_once_t predicate;
    dispatch_once(&predicate, ^{
        object = ...;
    });
    return object;
    //if判断
    static id object = nil;
    if (!object)
    {
        object = ...;
    }
    return object;
    

### 二、负载的探究：重实现`dispatch_once`

#### 线程锁

使用`pthread_mutex_lock`是我首先想到的实现方式：

    
    
    void DWDispatchOnce(dispatch_once_t *predicate, dispatch_block_t block) {
        static pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
        pthread_mutex_lock(&mutex);
        if(!*predicate) {
            block();
            *predicate = 1;
        }
        pthread_mutex_unlock(&mutex);
    }
    

这样的实现确实是线程安全的，但是`pthread_mutex_lock`的效率太低了，后续调用负载是两次锁操作（加锁解锁），在我的macbookpro上，这
个函数需要30ns，这战斗力太渣了，抛弃。

#### 自旋锁

自旋锁比之互斥锁，其优势在于某些情况下负载更低，然后，我来改一下我的函数实现：

    
    
    void DWDispatchOnce(dispatch_once_t *predicate, dispatch_block_t block) {
        static OSSpinLock lock = OS_SPINLOCK_INIT;
        OSSpinLockLock(&lock);
        if(!*predicate) {
            block();
            *predicate = 1;
        }
        OSSpinLockUnlock(&lock);
    }

嗯，提升很不错，这次提升到了6.5ns，自旋锁在低碰撞情况下，效率果然不是盖的，不过对于`dispatch_once`来说，还是太渣了，6ns实在是太龟速了
。

#### 原子操作

原子操作是低级CPU操作，不用锁也是线程安全的（实际上，原子操作使用硬件级别的锁），原子操作使得自己实现软件级别锁成为可能。当锁负载太高时，可以直接使用原子
操作来替代锁。

> 以原子操作来替代锁的编程方式很取巧，比较容易出现问题。bug很难找，使用需谨慎。

我们使用“原子比较交换函数” `__sync_bool_compare_and_swap`来实现新的`DWDispatchOnce`，`__sync_boo
l_compare_and_swap`的作用大概等同于：

    
    
    BOOL DWCompareAndSwap(long *ptr, long testValue, long newValue) {
        if(*ptr == testValue) {
            *ptr = newValue;
            return YES;
        }
        return NO;
    }

不同的是，`__sync_bool_compare_and_swap`是一个被实现为cpu原子操作的函数，所以比较和交换操作是一个整体操作并且是线程安全的。

所以新的实现就成为：

    
    
    
    void DWDispatchOnce(dispatch_once_t *predicate, dispatch_block_t block)
    {
        if(*predicate == 2)
        {
            __sync_synchronize();
            return;
        }
        volatile dispatch_once_t *volatilePredicate = predicate;
        if(__sync_bool_compare_and_swap(volatilePredicate, 0, 1)) {
            block();
            __sync_synchronize();
            *volatilePredicate = 2;
        } else {
            while(*volatilePredicate != 2)
                ;//注意这里没有循环体
            __sync_synchronize();
        }
    }
    

新的实现首先检查`predicate`是否为2，假如为2，则调用`__sync_synchronize`这个builtin函数并返回，调用此函数会产生一个m
emory barrier，用以保证cpu读写顺序严格按照程序的编写顺序来进行，关于memory
barrier的更多信息，还是查[wiki](http://en.wikipedia.org/wiki/Memory_barrier)吧。

紧接着是一个`volatile`修饰符修饰的指针临时变量，如此编译器就会假定此指针指向的值可能会随时被其它线程改变，从而防止编译器对此指针指向的值的读写进行
优化，比如cache，reorder等。

然后进行“原子比较交换”，如果`predicate`为0，则将`predicate`置为1，表示正在执行block，并返回true，如此便进入了block执
行分支，在block执行完毕之后，我们依旧需要一个memory
barrier，最后我们将`predicate`置为2，表示执行已经完成，后续调用应该直接返回。

当某个线程A正在执行block时，任何线程B再进入此函数，便会进入else分支，然后在此分支中进行等待，直至线程A将`predicate`置为2，然后调用`
__sync_synchronize`并返回

这个实现是线程安全的，并且是无锁的，但是，依旧需要消耗11.5ns来执行，比自旋锁都慢，实际上memory
barrier是很慢的。至于为什么比自旋锁还慢，memory barrier有好几种，`__sync_synchronize`产生的是`mfence`CPU
指令，是最蛋疼的一种，跟那蛋疼到忧伤的SSE4指令集是一路货。但不管怎么样，我想说的是，memory barrier是有不小的开销的。

假如去除掉memory barrier会如何呢？

    
    
    
    void DWDispatchOnce(dispatch_once_t *predicate, dispatch_block_t block) {
        if(*predicate == 2)
            return;
        volatile dispatch_once_t *volatilePredicate = predicate;
        if(__sync_bool_compare_and_swap(volatilePredicate, 0, 1)) {
            block();
            *volatilePredicate = 2;
        } else {
            while(*volatilePredicate != 2)
                ;
            }
    }
    

这其实是一个不线程安全的实现，现代的CPU都是异步的，为了满足用户“又想马儿好，又想马儿不吃草”的奢望，CPU厂商堪称无所不用其极，所以现代的CPU在提升速
度上有很多优化，其中之一就是流水线特性，当执行一条cpu指令时，发生了如下事情：

    
    
    1.从内存加载指令
    2.指令解码（解析指令是什么，操作是什么）
    3.加载输入数据
    4.执行操作
    5.保存输出数据

在古董级cpu上面，cpu是这样干活的：

    
    
    加载指令
    解码
    加载数据
    执行
    保存输出数据
    加载指令
    解码
    加载数据
    执行
    保存输出数据
    加载指令
    解码
    加载数据
    执行
    保存输出数据
    ...

在现代CPU上，cpu是这样干活的：

    
    
    加载指令                     ...
    解码            加载指令
    加载数据         解码
    执行            加载数据
    保存输出数据     执行
                   保存输出数据
    ...
    

这可就快得多了，cpu会将其认为可以同时执行的指令并行执行，并根据优化速度的需要来调整执行顺序，比如：

    
    
        x = 1;
        y = 2;
    

cpu可能会先执行y=2，另外，编译器也可能为了优化而为你生成一个先执行y=2的代码，即使关闭编译器优化，cpu还是可能会先执行y=2，在多核处理器中，其它
的cpu就会看到这个两个赋值操作顺序颠倒了，即使赋值操作没有颠倒，其它cpu也可能颠倒读取顺序，最后导致的结果可能是另一个线程在读取到y为2时，却发现x还没
被赋值为1。

解决这种问题的方法就是加入memory barrier，但是memory barrier的目的就在于防止cpu“跑太快”，所以，开销的惩罚那是大大的。

所以，对于`dispatch_once`：

    
    
    static SomeClass *obj;
    static dispatch_once_t predicate;
    dispatch_once(&predicate, ^{ obj = [[SomeClass alloc] init]; });
    [obj doSomething];

假如`obj`在`predicate`之前被读取，那一个线程可能另一个线程执行完block之前就取得了一个nil值；假如`predicate`被读取为“已完
成”，并且此时另一个线程正在初始化这个`obj`，那么接下来调用函数可能会导致程序崩溃。

所以，`dispatch_once`需要memory barrier或者类似的东西，但是它肯定没有使用memory barrier，因为memory
barrier实在是很慢。要明白`dispatch_once`如何避免memory barrier，先要了解cpu的分支预测和预执行。

#### cpu的分支预测和预执行

流水线特性使得CPU能更快地执行线性指令序列，但是当遇到条件判断分支时，麻烦来了，在判定语句返回结果之前，cpu不知道该执行哪个分支，那就得等着（术语叫做p
ipeline stall），这怎么能行呢，所以，CPU会进行预执行，cpu先猜测一个可能的分支，然后开始执行分支中的指令。现代CPU一般都能做到超过90%
的猜测命中率，这可比NBA选手发球命中率高多了。然后当判定语句返回，加入cpu猜错分支，那么之前进行的执行都会被抛弃，然后从正确的分支重新开始执行。

在`dispatch_once`中，唯一一个判断分支就是`predicate`，`dispatch_once`会让CPU预执行条件不成立的分支，这样可以大大
提升函数执行速度。但是这样的预执行导致的结果是使用了未初始化的`obj`并将函数返回，这显然不是预期结果。

#### 不对称barrier

编写barrier时，应该是对称的，在写入端，要有一个barrier来保证顺序写入，同时，在读取端，也要有一个barrier来保证顺序读取。但是，我们的`d
ispatch_once`实现要求写入端快不快无所谓，而读取端尽可能的快。所以，我们要解决前述的预执行引起的问题。

当一个预执行最终被发现是错误的猜测时，所有的预执行状态以及结果都会被清除，然后cpu会从判断分支处重新执行正确的分支，也就意味着被读取的未初始化的`obj`
也会被抛弃，然后读取。假如`dispatch_once`能做到在执行完block并正确赋值给`obj`后，告诉其它cpu核心：你们这群无知的cpu啊，你们刚
才都猜错了！然后这群“无知的cpu”就会重新从分支处开始执行，进而获取正确的`obj`值并返回。

从最早的预执行到条件判断语句最终结果被计算出来，这之间有很长时间（记作Ta），具体多长取决于cpu的设计，但是不论如何，这个时间最多几十圈cpu时钟时间，假
如写入端能在【初始化并写入`obj`】与【置`predicate`值】之间等待足够长的时间Tb使得Tb大于等于Ta，那问题就都解决了。

> 如果觉得这个”解决”难以理解，那么反过来思考，假如Tb小于Ta，那么Tb就有可能被Ta完全包含，也就是说，另一个线程B（耗时为Ta）在预执行读取了未初始
化的`obj`值之后，回过头来确认猜测正确性时，`predicate可能`被执行block的线程A置为了“完成”，这就导致线程B认为自己的预执行有效（实际上
它读取了未初始化的值）。而假如Tb大于等于Ta，任何读取了未初始化的`obj`值的预执行都会被判定为未命中，从而进入内层`dispatch_once`而进行
等待。

要保证足够的等待时间，需要一些trick。在intel的CPU上，`dispatch_once`动用了`cpuid`指令来达成这个目的。`cpuid`本来是
用作取得cpu的信息，但是这个指令也同时强制将指令流串行化，并且这个指令是需要比较长的执行时间的（在某些cpu上，甚至需要几百圈cpu时钟），这个时间Tc足
够超过Ta了。

查看`dispatch_once`读取端的实现：

    
    
    
    DISPATCH_INLINE DISPATCH_ALWAYS_INLINE DISPATCH_NONNULL_ALL DISPATCH_NOTHROW
    void
    _dispatch_once(dispatch_once_t *predicate, dispatch_block_t block)
    {
        if (DISPATCH_EXPECT(*predicate, ~0l) != ~0l) {
            dispatch_once(predicate, block);
        }
    }
    #define dispatch_once _dispatch_once

没有barrier，并且这个代码是在头文件中的，是强制inline的，`DISPATCH_EXPECT`是用来告诉cpu `*predicate`等于`~0
l`是更有可能的判定结果，这就使得cpu能猜测到更正确的分支，并提高效率，最重要的是，这一句是个简单的if判定语句，负载无限接近benchmark。

在写入端，`dispatch_once`在执行了block之后，会调用`dispatch_atomic_maximally_synchronizing_ba
rrier()`;宏函数，在intel处理器上，这个函数编译出的是`cpuid`指令，在其他厂商处理器上，这个宏函数编译出的是合适的其它指令。

如此一来，`dispatch_once`就保证了场景#3的执行速度无限接近benchmark，实现了写入端的最低负载。

下一篇，我将和大家一起探究`dispatch_once`写入端的实现，并讨论使用非static predicate的可能性


<hr>


#GCD外传：dispatch_once(中)


本篇，我将和大家一起探究`dispatch_once`写入端的实现

让我们先看看`dispatch_once`的实现（Grand Central
Dispatch是开源的，大家可以到git://git.macosforge.org/libdispatch.git克隆源码）

    
    
    struct _dispatch_once_waiter_s {
    	volatile struct _dispatch_once_waiter_s *volatile dow_next;
    	_dispatch_thread_semaphore_t dow_sema;
    };
    #define DISPATCH_ONCE_DONE ((struct _dispatch_once_waiter_s *)~0l)
    #ifdef __BLOCKS__
    void
    dispatch_once(dispatch_once_t *val, dispatch_block_t block)
    {
    	struct Block_basic *bb = (void *)block;
    	dispatch_once_f(val, block, (void *)bb->Block_invoke);
    }
    #endif
    DISPATCH_NOINLINE
    void
    dispatch_once_f(dispatch_once_t *val, void *ctxt, dispatch_function_t func)
    {
    	struct _dispatch_once_waiter_s * volatile *vval = (struct _dispatch_once_waiter_s**)val;
    	struct _dispatch_once_waiter_s dow = { NULL, 0 };
    	struct _dispatch_once_waiter_s *tail, *tmp;
    	_dispatch_thread_semaphore_t sema;
    	if (dispatch_atomic_cmpxchg(vval, NULL, &dow)) {
    		dispatch_atomic_acquire_barrier();//这是一个空的宏函数，什么也不做
    		_dispatch_client_callout(ctxt, func);
    		dispatch_atomic_maximally_synchronizing_barrier();
    		//dispatch_atomic_release_barrier(); // assumed contained in above
    		tmp = dispatch_atomic_xchg(vval, DISPATCH_ONCE_DONE);
    		tail = &dow;
    		while (tail != tmp) {
    			while (!tmp->dow_next) {
    				_dispatch_hardware_pause();
    			}
    			sema = tmp->dow_sema;
    			tmp = (struct _dispatch_once_waiter_s*)tmp->dow_next;
    			_dispatch_thread_semaphore_signal(sema);
    		}
    	} else {
    		dow.dow_sema = _dispatch_get_thread_semaphore();
    		for (;;) {
    			tmp = *vval;
    			if (tmp == DISPATCH_ONCE_DONE) {
    				break;
    			}
    			dispatch_atomic_store_barrier();
    			if (dispatch_atomic_cmpxchg(vval, tmp, &dow)) {
    				dow.dow_next = tmp;
    				_dispatch_thread_semaphore_wait(dow.dow_sema);
    			}
    		}
    		_dispatch_put_thread_semaphore(dow.dow_sema);
    	}
    }

一堆宏函数加一堆让人头大的线程同步代码。一步一步看：

`dispatch_once`内部其实是调用了`dispatch_once_f`，f指的是调用c函数（没有f指的是调用block），实际上执行block最终
也是调用c函数（详见我的《[Block非官方编程指南](/article/block教程系列.html)》）。当`dispatch_once_f`被调用时，
`val`是外部传入的`predicate`，`ctxt`传入的是Block的指针，`func`指的是Block内部的执行体函数，执行它就是执行block。

接下来是声明了一堆变量，`vval`是volatile标记过的`val`，volatile修饰符的作用上一篇已经介绍过，告诉编译器此指针指向的值随时可能被其
他线程改变，从而使得编译器不对此指针进行代码编译优化。

> dow意为dispatch_once wait

`dispatch_atomic_cmpxchg`是上一篇我们讲过的“原子比较交换函数”`__sync_bool_compare_and_swap`的宏替换
，接下来进入分支：

1.执行block的分支

当`dispatch_once`第一次执行时，`predicate`也即`val`为0，那么此“原子比较交换函数”将返回true并将`vval`指向值赋值为
`&dow`，即为“等待中”，`_dispatch_client_callout`其内部做了一些判定，但实际上是调用了`func`而已。到此，block中的
用户代码执行完毕。

接下来就是上篇提及的`cpuid`指令等待，使得其他线程的【读取到未初始化值的】_预执行_能被判定为猜测未命中，从而使得这些线程能够进入`dispatch_
once_f`里的另一个分支从而进行等待。

`cpuid`指令完毕后，调用`dispatch_atomic_xchg`进行赋值，置其为DISPATCH_ONCE_DONE，即“完成”，这里`dispa
tch_atomic_xchg`是内建“原子交换函数”`__sync_swap`的优化版宏替换，其将第二个参数的值赋给第一个参数（解引用指针），然后返回第一
个参数被赋值前的解引用值，其原型为：

    
    
    type __sync_swap(type *ptr, type value, ...)
    

接下来是对信号量链的处理：

  1. 在block执行过程中，没有其他线程进入本函数来等待，则`vval`指向值保持为`&dow`，即`tmp`被赋值为`&dow`，即下方while循环不会被执行，此分支结束。
  2. 在block执行过程中，有其他线程进入本函数来等待，那么会构造一个信号量链表（`vval`指向值变为信号量链的头部，链表的尾部为`&dow`），此时就会进入while循环，在此while循环中，遍历链表，逐个signal每个信号量，然后结束循环。

> `while (!tmp->dow_next)`此循环是等待在&dow上，因为线程等待分支#2会中途将`val`赋值为`&dow`，然后为`->dow_
next`赋值，这期间`->dow_next`值为NULL，需要等待，详见下面线程等待分支#2的描述

> `_dispatch_hardware_pause`此句是为了提示cpu减少额外处理，提升性能，节省电力。

2.线程等待分支

当_执行block分支#1_未完成，且有线程再进入本函数时，将进入线程等待分支：

先调用`_dispatch_get_thread_semaphore`创建一个信号量，此信号量被赋值给`dow`.`dow_sema`。

然后进入一个无限for循环，假如发现`vval`的指向值已经为`DISPATCH_ONCE_DONE`，即“完成”，则直接break，然后调用`_dispa
tch_put_thread_semaphore`函数销毁信号量并退出函数。``

> `_dispatch_get_thread_semaphore`内部使用的是“有即取用，无即创建”策略来获取信号量。

>

> `_dispatch_put_thread_semaphore`内部使用的是“销毁旧的，存储新的”策略来缓存信号量。

假如`vval`的解引用值并非`DISPATCH_ONCE_DONE`，则进行一个“原子比较并交换”操作（此操作可以避免两个等待线程同时操作链表带来的问题）
，假如此时`vval`指向值已不再是`tmp`（这种情况发生在多个线程同时进入线程等待分支#2，并交错修改链表）则for循环重新开始，再尝试重新获取一次vv
al来进行同样的操作；若指向值还是tmp，则将`vval`的指向值赋值为`&dow`，此时`val->dow_next`值为NULL，可能会使得block执
行分支#1进行while等待（如前述），紧接着执行`dow.dow_next = tmp`这句来增加链表节点（同时也使得block执行分支#1的while等
待结束），然后等待在信号量上，当block执行分支#1完成并遍历链表来signal时，唤醒、释放信号量，然后一切就完成了。

#### 小结

综上所述，dispatch_once的主要处理的情况如下：

  1. 线程A执行Block时，任何其它线程都需要等待。
  2. 线程A执行完Block应该立即标记任务完成状态，然后遍历信号量链来唤醒所有等待线程。
  3. 线程A遍历信号量链来signal时，任何其他新进入函数的线程都应该直接返回而无需等待。
  4. 线程A遍历信号量链来signal时，若有其它等待线程B仍在更新或试图更新信号量链，应该保证此线程B能正确完成其任务：a.直接返回 b.等待在信号量上并很快又被唤醒。
  5. 线程B构造信号量时，应该考虑线程A随时可能改变状态（“等待”、“完成”、“遍历信号量链”）。
  6. 线程B构造信号量时，应该考虑到另一个线程C也可能正在更新或试图更新信号量链，应该保证B、C都能正常完成其任务：a.增加链节并等待在信号量上 b.发现线程A已经标记“完成”然后直接销毁信号量并退出函数。

#### 总结

无锁的线程同步编程非常精巧，为了提升效率，每一处线程竞争都必须被考虑到并妥善处理。但这种编程方式又极其令人神往，原子操作的魅力便在于此，它就像是一个精密的钟
表，每一处接合都如此巧妙。

下一篇，我们将一起研究使用非static的predicate的可能性。


<hr>


#GCD外传：dispatch_once(下)


> 注意，本篇所讨论的使用方式（动态predicate）并不提倡用于实际项目，仅作为深入探究和学习dispatch_once的一种方法，讨论的范围也在官方文
档定义之外，其可靠性不能被保证。

在本系列前两篇文章中，我们一起学习了dispatch_once的作用、工作原理以及效率研究：

dispatch_once使得block中的代码执行且只执行一次，在多线程竞态时，使其他线程进入等待状态直至block执行完毕，并且还保证无竞态时执行效率与
非线程安全的if语句效率相当。

dispatch_once内部使用了大量的原子操作来替代锁与信号量，这使得其效率大大提升，但带来的是维护和阅读性的降低。

dispatch_once被大量使用在构建单例上，apple也推荐如此。

但是我们可能会有两个疑问：

  1. 使用dispatch_once实现的单例，在初始化后，难以简单做到反初始化或者重初始化，如何解决？
  2. 使用dispatch_once时，static predicate一定程度限制了dispatch_once的使用场景，又如何解决。



本篇我们一起探究使用非static predicate的可能性，在后续系列文章中，我还将和大家一起探讨如何安全地重置predicate。

#### 一、文档参考

如果查阅dispatch_once函数文档，对于predicate，文档有如下说明：

> The predicate must point to a variable stored in global or static scope. The
result of using a predicate with automatic or dynamic storage (including
Objective-C instance variables) is undefined.

再查阅dispatch_once_t的头文件注释，得如下说明：

> A predicate for use with dispatch_once(). It must be initialized to zero.  
Note: static and global variables default to zero.

dispatch_once函数文档告诉我们：不要使用动态分配的predicate；

而dispatch_once_t的头文件注释告诉我们，predicate需要先初始化为0，并且提醒我们，static和global变量创建出来即有默认值0，
但没有指明不可以动态分配。

#### 二、先进行简单的分析

1.从程序设计角度

我们知道一个单例一般是从程序第一次调用它的get方法或者类似的生成方法时，惰性加载的，一旦加载，大多数情况下会一直为其它模块服务。

有时候我们可能需要重置这些单例，比如某个用户点击了reset按钮，或者选择了注销账号等等操作，这时候程序中某些一直活跃的相关单例就需要进行重置。

最简单的重置设计就是析构这些单例，然后重新创建，使其能够将创建过程中的所有逻辑重新运行一次，得到重置的效果。

这时候我们有两种选择，一种是使用常规的静态变量保护措施来保证单例，当我们需要reset时，重置这些变量，然后析构单例即可：

    
    
    static id gSharedInstance;
    + (instancetype)sharedInstance
    {
        if (!gSharedInstance)
        {
            gSharedInstance = [[self alloc] init];
        }
        return gSharedInstance;
    }
    + (void)destorySharedInstance
    {
        if (gSharedInstance)
        {
            [gSharedInstance release];
            gSharedInstance = nil;
        }
    }

但是使用常规的静态变量方式显然没有dispatch_once那么高端大气上档次，或者说没有那么高效、简洁、线程安全，那么我们可能想要采取的方式就是重置dis
patch_once的predicate。

然而，如果可重置的单例被设计为需要重新创建这些单例，则显得很生硬（尽管有时候会让人感觉很方便），从程序设计角度来讲，更优雅的方式是让这些单例具有可重置的入口
，甚至可以单独地重置这些单例的子模块：

    
    
    + (instancetype)sharedInstance
    {
        static id sharedInstance;
        static dispatch_once_t onceToken;
        dispatch_once(&onceToken, ^{
            sharedInstance = [[self alloc] init];
        });
        return sharedInstance;
    }
    - (void)resetSubmoduleA
    {
    }
    - (void)resetSubmoduleB
    {
    }
    - (void)reset
    {
        [self resetSubmoduleA];
        [self resetSubmoduleB];
    }

如此可以从程序设计层面避免重新创建单例，模块也变得更清晰。

按照这样的设计方式，甚至可以在内存吃紧时，释放不必要的cache或者submodule资源等。

尽管我并不提倡这么做，但本篇旨在讨论使用动态分配的predicate的可能性，所以我们还是继续下一环节的分析。

2.从代码编写角度

我们知道通常来说，一个变量在内存空间中有三种存储方式：堆、栈、全局区（这里我们略过memmap区等一些不常用或者不可用的内存区），那么动态分配，就是堆与栈变
量了。

在栈上分配predicate几乎没什么意义，所以我们直接研究堆上的predicate。

我们先编写一个简单的范例：

    
    
    @interface ClassA : NSObject
    {
        dispatch_once_t _onceToken;
        int _bar;
    }
    @end
    @implementation ClassA
    - (instancetype)init
    {
        if (self = [super init]) {
            //_onceToken = 0;
        }
        return self;
    }
    - (int)foo
    {
        dispatch_once(&_onceToken, ^{
            _bar = 999;
        });
        return _bar;
    }
    @end

这段代码使用了堆上的predicate，当ClassA被实例化为InstanceA时，_onceToken被一起创建，但是值得注意的是，一个Objectiv
eC对象被alloc时，其内存布局的剩余区域会被填充为0，也就是说，也就是说，当ClassA被创建后，其成员_onceToken的值已经为0（我们暂不讨论C
PU的内存读写操作的[弱一致性](http://en.wikipedia.org/wiki/Weak_consistency)，放在后续段落中讨论）。



在上一篇中，我们已经剖析过dispatch_once的内部实现（写入端代码），我们发现dispatch_once_t实际上是一个long类型，也就是等同于一
个指针类型，而dispatch_once函数内部确实是将predicate转换为一个指针来使用，并在不同的逻辑阶段用其指向不同的struct。

那么一个long类型变量是static还是dynamic有什么区别？一般来说，有两方面：

  1. static long具有固定的内存地址，在整个程序的生命周期中，它的值都不会改变；而相反的，dynamic分配的long，其内存地址很有可能发生变化，比如其所处的内存块被realloc等等。
  2. static long的值从程序load开始就已经初始化为0了，也就是说它“从未非零”过，而dynamic分配的long其在内存真正被置0之前，值是任意的。

对于第一种情况，我们的InstanceA可以保证在自身的生命周期中，其成员变量_onceToken不会改变，可以排除。

而对于第二种情况，一个变量曾经不为0会导致出错的情况，更多地是在讨论CPU内存读写操作的弱一致性。回顾dispatch_once源码，我们会发现，在if条件
判定predicate值之前，并没有出现能够同步硬件内存读写的barrier（因为dispatch_once要保证在没有碰撞的情况下执行效率无限接近非线程安
全的纯if语句）。

CPU的乱序执行是一个太过复杂的话题，为了彻底避免这一可能性带来的影响，我们可以在init中引入一个memory barrier：

    
    
    @interface ClassA : NSObject
    {
        dispatch_once_t _onceToken;
        int _bar;
    }
    @end
    @implementation ClassA
    - (instancetype)init
    {
        if (self = [super init]) {
            //_onceToken = 0;
            OSMemoryBarrier();
        }
        return self;
    }
    - (int)foo
    {
        dispatch_once(&_onceToken, ^{
            _bar = 999;
        });
        return _bar;
    }
    @end

如此一来，只要我们取得了InstanceA的句柄（也就是其指针），其成员_onceToken的值在被读取时，一定会先通过memory barrier的同步，
从而保证读取到的一定是初始化为0后的值，如此一来，其从前的值是否为0，就没有影响了，但如此一来，我们付出的代价是内存屏障带来的性能降低，初始化Instanc
eA将需要更多时间。

到了这一步，那么我们可以放心的使用_onceToken这个成员变量作为predicate了？

还不够，我们知道，ClassA的实例InstanceA是一个动态分配的实例（当然，ObjectiveC并不支持静态分配实例），其生命周期是有限的，一旦Ins
tanceA在某种的情况下被析构，_onceToken将立即成为一个无效内存，如果此时dispatch_once正处于内部逻辑的某个中间状态（参考[上一篇教
程](/article/gcd-guide-dispatch-once-2.html)对其内部逻辑各个状态的剖析），那么将发生无法评估的错乱，这应该也正是A
pple明确在文档中标出不要使用ObjectiveC成员变量作为predicate的原因之一。

对于这种情况，我们要做的是，保证使用_onceToken的dispatch_once调用都处于InstanceA的生命周期之内。但是这个保证是在不同的Cla
ss中需要的做法都不同，我们并不能总结出一个一劳永逸的方法。但没关系，无论如何，我们总结和猜测出了各种可能的情况，并尽量避免之，接下来让我们使用Demo来测
试。

#### 三、使用Demo来测试

我们使用50个并发来测试:)

    
    
    void testClassA()
    {
        ClassA *a = [[[ClassA alloc] init] autorelease];
        void(^ bgFoo)() = ^{
            int f = [a foo];
            NSLog(@"bgFoo f:%i", f);
        };
        for (int i = 0; i < 50; i++)
        {
            dispatch_async(dispatch_get_global_queue(0, 0), bgFoo);
        };
        for (int i = 0; i < 50; i++)
        {
            int f = [a foo];
            NSLog(@"foo f:%i", f);
        }
    }

在我的MacbookAir上，其打印结果为：

    
    
    ...
    2015-06-28 21:41:46.464 testgcd[4623:663776] bgFoo f:999
    2015-06-28 21:41:46.466 testgcd[4623:663653] foo f:999
    2015-06-28 21:41:46.466 testgcd[4623:663653] foo f:999
    2015-06-28 21:41:46.465 testgcd[4623:663795] bgFoo f:999
    2015-06-28 21:41:46.466 testgcd[4623:663653] foo f:999
    2015-06-28 21:41:46.466 testgcd[4623:663795] bgFoo f:999
    ...

额，简直太长了，我只截取了一部分log，我检查了所有100条log，每一个返回值都是999。

#### 四、可靠吗？

对于这种使用方式的可靠性，我们不能保证，但是可以肯定的一点是，越能保证避免前文中猜测的问题，可靠性越高。但是这种使用方式应该极力避免。或者可以在你项目的“实
验室版”中加以使用，并结合错误日志来长期验证？

在后面的教程中，我会和大家一起研究重置predicate使得dispatch_once重新执行的方法。


<hr>


#GCD实战练习：使用串行队列实现简单的预加载


正如使用其它多线程api一样，使用GCD也可以用于预加载。

本篇使用一个非常简单的例子来描述怎样做到预加载一个ViewController，其主要思路是使用gcd在子线程中创建并初始化一个ViewController
，在其加载完毕后，将其push入navigation controller中

简要代码如下：

    
    
    @implementation DWClassA
    {
        dispatch_queue_t _serialQueue;
        UINavigationController *_navController;
    }
    - (dispatch_queue_t)serialQueue
    {
        if (!_serialQueue) {
            _serialQueue = dispatch_queue_create("serialQueue", DISPATCH_QUEUE_SERIAL);//创建串行队列
        }
        return _serialQueue;
    }
    - (void)prepareViewController
    {
        dispatch_async([self serialQueue], ^{//把block中的任务放入串行队列中执行，这是第一个任务
            self.viewController = [[[DWViewController alloc] init] autorelease];
            sleep(2);//假装这个viewController创建起来很花时间。。其实view都还没加载，根本不花时间。
            NSLog(@"prepared");
        });
    }
    - (void)goToViewController
    {
        dispatch_async([self serialQueue], ^{//第二个任务，推入viewController
            NSLog(@"go");
            dispatch_async(dispatch_get_main_queue(), ^{//涉及UI更新的操作，放入主线程中
                [_navController pushViewController:self.viewController animated:YES];
            });
        });
    }
    - (void)dealloc
    {
        _serialQueue && dispatch_release(_serialQueue);
        [_navController release];
        [_viewController release];
        [super dealloc];
    }
    @end
    

首先我们创建了一个串行队列（使用DISPATCH_QUEUE_SERIAL作为参数），我们知道，将多个任务dispatch至一个串行队列，可以达到线程同步的
效果，并且可以避免编写Lock相关的代码。我们使用一个方法来封装这个串行队列的创建，使得后续操作都能取得这个串行队列

紧接着我们在prepare函数中，将创建并初始化ViewController的任务dispatch至串行队列中，一旦dispatch，任务将立即开始执行，这
里我使用sleep函数来模拟一个需要较长时间来初始化的viewcontroller，并且sleep了夸张的两秒钟。

然后我们在goTo函数中，将push任务dispatch至前述的串行队列中，当初始化完成后，会自动接着执行push任务，当然，如果dispatch这个pus
h任务时，如果前述的初始化任务早已完成，那么push任务将被立即执行。值得注意的是，在Cocoa开发中，我们必须将涉及UI更新的操作（即使这个操作不会被立即
显示在屏幕中）放在主线程中执行，这是Apple在文档中规定的。

> 实际上Apple规定UIKit的方法都必须放在主线程中调用，事实证明，确实很多不涉及UI操作的UIKit方法都不能在子线程中调用，甚至一些文件加载的函数
。而其根本原因是UIKit的这些方法都在内部调用了一些可能产生竞态的资源（很多方法会调用render context来进行中间转换等操作），而一些UIKit
方法被验证确实能放在子线程中调用（虽然不推荐这么做，因为这么做不稳定，你不能确定某一天Apple会修改这些方法的内部实现而导致其只能在主线程中执行）也印证了
这一点。

最后我们在dealloc函数中释放应该释放的资源，注意dispatch_release方法不可以传入一个NULL指针，这将导致崩溃。

> 在GCD的头文件中我们会发现这句注释：The result of passing NULL in this parameter is undefined
.也就是说，不像free函数那样（free函数由POSIX定义传入NULL则什么都不干），dispatch_release是不能接受空指针的。


<hr>


#GCD实战练习：安全地dispatch_sync任务


有时候，我们不得不将一个任务sync至另一个queue中，但sync操作是一个具有潜在危险的操作：不当的sync会导致进程被锁死。

比如一个queue A，将任务T sync至queue B，而任务T中又将一个子任务 S sync至queue A中，这将必然导致A和B都锁死。

你也许会问，设计任务T时，本身就应该避免其子任务再次sync回A，但在实际工程中，更可能是现象是：任务T的子任务S又调用另外一个任务R，以此类推直至某个任务
M，M会将子任务N sync至queue A，这样的深入嵌套往往难以被任务T的开发者考虑到，甚至对任务M全然不知晓。

    
    
    dispatch_queue_t queueA;
    dispatch_queue_t queueB;
    void taskR()
    {
        printf("this is task R, do you copy?");
    }
    void taskS()
    {
        dispatch_sync(queueA, ^{
            taskR();
        });
    }
    void taskT()
    {
        dispatch_sync(queueB, ^{
            taskS();
        });
    }
    int foo()
    {
        queueA = dispatch_queue_create("queueA", 0);
        queueB = dispatch_queue_create("queueB", 0);
        dispatch_sync(queueA, ^{
            taskT();
        });
        dispatch_release(queueA);
        dispatch_release(queueB);
        return 0;
    }

所以我们可以编写出一种封装的sync函数（这里以objective-c示例），来保护这种卡死的现象，一旦检测到了卡死，可以打印一些debug消息来警告调用者
，在开发环境中可以尽情的使用此函数，而在生产环境中，继续使用此函数也不会有什么问题。

函数如下：

    
    
    + (void)scheduleTask01:(void(^)())task targetQueue:(dispatch_queue_t)queue timeOut:(float)seconds
    {
        (seconds < 0.0) && (seconds = 0.0);
        dispatch_semaphore_t sem = dispatch_semaphore_create(0);
        dispatch_async(queue, ^{
            task();
            dispatch_semaphore_signal(sem);
        });
        if (dispatch_semaphore_wait(sem, dispatch_time(DISPATCH_TIME_NOW, (int64_t)(seconds * NSEC_PER_SEC))) != 0)
        {
            NSLog(@"dispatch timeout sync: time out!");
        }
        dispatch_release(sem);
    }

使用async dispatch配合dispatch_semaphore来模拟sync dispatch，使得设置超时时间成为可能。


<hr>


#GCD实战练习：资源竞争

**概述**

我将分四步来带大家研究研究程序的并发计算。第一步是基本的串行程序，然后使用GCD把它并行计算化。

**原始程序**

我们的程序只是简单地遍历~/Pictures然后生成缩略图。这个程序是个命令行程序，没有图形界面（尽管是使用Cocoa开发库的），主函数如下：

    
    
        int main(int argc, char **argv)
        {
            NSAutoreleasePool *outerPool = [NSAutoreleasePool new];
            NSApplicationLoad();
            NSString *destination = @"/tmp/imagegcd";
            [[NSFileManager defaultManager] removeItemAtPath: destination error: NULL];
            [[NSFileManager defaultManager] createDirectoryAtPath: destination
                                            withIntermediateDirectories: YES
                                            attributes: nil
                                            error: NULL];
            Start();
            NSString *dir = [@"~/Pictures" stringByExpandingTildeInPath];
            NSDirectoryEnumerator *enumerator = [[NSFileManager defaultManager] enumeratorAtPath: dir];
            int count = 0;
            for(NSString *path in enumerator)
            {
                NSAutoreleasePool *innerPool = [NSAutoreleasePool new];
                if([[[path pathExtension] lowercaseString] isEqual: @"jpg"])
                {
                    path = [dir stringByAppendingPathComponent: path];
                    NSData *data = [NSData dataWithContentsOfFile: path];
                    if(data)
                    {
                        NSData *thumbnailData = ThumbnailDataForData(data);
                        if(thumbnailData)
                        {
                            NSString *thumbnailName = [NSString stringWithFormat: @"%d.jpg", count++];
                            NSString *thumbnailPath = [destination stringByAppendingPathComponent: thumbnailName];
                            [thumbnailData writeToFile: thumbnailPath atomically: NO];
                        }
                    }
                }
                [innerPool release];
            }
            End();
            [outerPool release];
        }
    
    
     

当前这个程序是imagegcd1.m。程序中重要的部分都在这里了。. `Start` 函数和 `End` 函数只是简单的计时函数（内部实现是使用的`gett
imeofday函数`）。ThumbnailDataForData函数使用Cocoa库来加载图片数据生成Image对象，然后将图片缩小到320x320大小，
最后将其编码为JPEG格式。



**简单而天真的并发**

乍一看，我们感觉将这个程序并发计算化，很容易。循环中的每个迭代器都可以放入GCD global queue中。我们可以使用dispatch
queue来等待它们完成。为了保证每次迭代都会得到唯一的文件名数字，我们使用OSAtomicIncrement32来原子操作级别的增加count数：

    
    
        dispatch_queue_t globalQueue = dispatch_get_global_queue(0, 0);
        dispatch_group_t group = dispatch_group_create();
        __block uint32_t count = -1;
        for(NSString *path in enumerator)
        {
            dispatch_group_async(group, globalQueue, BlockWithAutoreleasePool(^{
                if([[[path pathExtension] lowercaseString] isEqual: @"jpg"])
                {
                    NSString *fullPath = [dir stringByAppendingPathComponent: path];
                    NSData *data = [NSData dataWithContentsOfFile: fullPath];
                    if(data)
                    {
                        NSData *thumbnailData = ThumbnailDataForData(data);
                        if(thumbnailData)
                        {
                            NSString *thumbnailName = [NSString stringWithFormat: @"%d.jpg",
                                                       OSAtomicIncrement32(&count;)];
                            NSString *thumbnailPath = [destination stringByAppendingPathComponent: thumbnailName];
                            [thumbnailData writeToFile: thumbnailPath atomically: NO];
                        }
                    }
                }
            });
        }
        dispatch_group_wait(group, DISPATCH_TIME_FOREVER);

这个就是imagegcd2.m，但是，注意，别运行这个程序，有很大的问题。

如果你无视我的警告还是运行这个imagegcd2.m了，你现在很有可能是在重启了电脑后，又打开了我的页面。。如果你乖乖地没有运行这个程序的话，运行这个程序发
生的情况就是（如果你有很多很多图片在~/Pictures中）：电脑没反应，好久好久都不动，假死了。。



**问题在哪**

问题出在哪？就在于GCD的智能上。GCD将任务放到全局线程池中运行，这个线程池的大小根据系统负载来随时改变。例如，我的电脑有四核，所以如果我使用GCD加载任
务，GCD会为我每个cpu核创建一个线程，也就是四个线程。如果电脑上其他任务需要进行的话，GCD会减少线程数来使其他任务得以占用cpu资源来完成。

但是，GCD也可以增加活动线程数。它会在其他某个线程阻塞时增加活动线程数。假设现在有四个线程正在运行，突然某个线程要做一个操作，比如，读文件，这个线程就会等
待磁盘响应，此时cpu核心会处于未充分利用的状态。这是GCD就会发现这个状态，然后创建另一个线程来填补这个资源浪费空缺。

现在，想想上面的程序发生了啥？主线程非常迅速地将任务不断放入global
queue中。GCD以一个少量工作线程的状态开始，然后开始执行任务。这些任务执行了一些很轻量的工作后，就开始等待磁盘资源，慢得不像话的磁盘资源。

我们别忘记磁盘资源的特性，除非你使用的是SSD或者牛逼的RAID，否则磁盘资源会在竞争的时候变得异常的慢。。

刚开始的四个任务很轻松地就同时访问到了磁盘资源，然后开始等待磁盘资源返回。这时GCD发现CPU开始空闲了，它继续增加工作线程。然后，这些线程执行更多的磁盘读
取任务，然后GCD再创建更多的工资线程。。。

可能在某个时间文件读取任务有完成的了。现在，线程池中可不止有四个线程，相反，有成百上千个。。。GCD又会尝试将工作线程减少（太多使用CPU资源的线程），但是
减少线程是由条件的，GCD不可以将一个正在执行任务的线程杀掉，并且也不能将这样的任务暂停。它必须等待这个任务完成。所有这些情况都导致GCD无法减少工作线程数
。

然后所有这上百个线程开始一个个完成了他们的磁盘读取工作。它们开始竞争CPU资源，当然CPU在处理竞争上比磁盘先进多了。问题在于，这些线程读完文件后开始编码这
些图片，如果你有很多很多图片，那么你的内存将开始爆仓。。然后内存耗尽咋办？虚拟内存啊，虚拟内存是啥，磁盘资源啊。Oh shit！~

然后进入了一个恶性循环，磁盘资源竞争导致更多的线程被创建，这些线程导致更多的内存使用，然后内存爆仓导致虚拟内存交换，直至GCD创建了系统规定的线程数上限（可
能是512个），而这些线程又没法被杀掉或暂停。。。

这就是使用GCD时，要注意的。GCD能智能地根据CPU情况来调整工作线程数，但是它却无法监视其他类型的资源状况。如果你的任务牵涉大量IO或者其他会导致线程b
lock的东西，你需要把握好这个问题。



**修正**  
问题的根源来自于磁盘IO，然后导致恶性循环。解决了磁盘资源碰撞，就解决了这个问题。

GCD的custom queue使得这个问题易于解决。Custom queue是串行的。如果我们创建一个custom
queue然后将所有的文件读写任务放入这个队列，磁盘资源的同时访问数会大大降低，资源访问碰撞就避免了。

虾米是我们修正后的代码，使用IO queue（也就是我们创建的custom queue专门用来读写磁盘）：

    
    
        dispatch_queue_t globalQueue = dispatch_get_global_queue(0, 0);
        dispatch_queue_t ioQueue = dispatch_queue_create("com.dreamingwish.imagegcd.io", NULL);
        dispatch_group_t group = dispatch_group_create();
        __block uint32_t count = -1;
        for(NSString *path in enumerator)
        {
            if([[[path pathExtension] lowercaseString] isEqual: @"jpg"])
            {
                NSString *fullPath = [dir stringByAppendingPathComponent: path];
                dispatch_group_async(group, ioQueue, BlockWithAutoreleasePool(^{
                    NSData *data = [NSData dataWithContentsOfFile: fullPath];
                    if(data)
                        dispatch_group_async(group, globalQueue, BlockWithAutoreleasePool(^{
                            NSData *thumbnailData = ThumbnailDataForData(data);
                            if(thumbnailData)
                            {
                                NSString *thumbnailName = [NSString stringWithFormat: @"%d.jpg",
                                                           OSAtomicIncrement32(&count;)];
                                NSString *thumbnailPath = [destination stringByAppendingPathComponent: thumbnailName];
                                dispatch_group_async(group, ioQueue, BlockWithAutoreleasePool(^{
                                    [thumbnailData writeToFile: thumbnailPath atomically: NO];
                                }));
                            }
                        }));
                }));
            }
        }
        dispatch_group_wait(group, DISPATCH_TIME_FOREVER);

 这个就是我们的 `imagegcd3.m`.

GCD使得我们很容易就将任务的不同部分放入相同的队列中去（简单地嵌套一下dispatch）。这次我们的程序将会表现地很好。。。我是说多数情况。。。。

问题在于任务中的不同部分不是同步的，导致了整个程序的不稳定。我们的新程序的整个流程如下：

    
    
        Main Thread          IO Queue            Concurrent Queue
        find paths  ------>  read  ----------->  process
                                                 ...
                             write <-----------  process
    

图中的箭头是非阻塞的，并且会简单地将内存中的对象进行缓冲。



 现在假设一个机器的磁盘足够快，快到比CPU处理任务（也就是图片处理）要快。其实不难想象：虽然CPU的动作很快，但是它的工作更繁重，解码、压缩、编码。从磁盘
读取的数据开始填满IO queue，数据会占用内存，很可能越占越多（如果你的~/Pictures中有很多很多图片的话）。

然后你就会内存爆仓，然后开始虚拟内存交换。。。又来了。。

这就会像第一次一样导致恶性循环。一旦任何东西导致工作线程阻塞，GCD就会创建更多的线程，这个线程执行的任务又会占用内存（从磁盘读取的数据），然后又开始交换内
存。。

结果：这个程序要么就是运行地很顺畅，要么就是很低效。

注意如果磁盘速度比较慢的话，这个问题依旧会出现，因为缩略图会被缓冲在内存里，不过这个问题导致的低效比较不容易出现，因为缩略图占的内存少得多。



**真正的修复**

由于上一次我们的尝试出现的问题在于没有同步不同部分的操作，所以让我写出同步的代码。最简单的方法就是使用信号量来限制同时执行的任务数量。

那么，我们需要限制为多少呢？

显然我们需要根据CPU的核数来限制这个量，我们又想马儿好又想马儿不吃草，我们就设置为cpu核数的两倍吧。不过这里只是简单地这样处理，GCD的作用之一就是让我
们不用关心操作系统的内部信息（比如cpu数），现在又来读取cpu核数，确实不太妙。也许我们在实际应用中，可以根据其他需求来定义这个限制量。

现在我们的主循环代码就是这样了：

    
    
        dispatch_queue_t ioQueue = dispatch_queue_create("com.dreamingwish.imagegcd.io", NULL);
        int cpuCount = [[NSProcessInfo processInfo] processorCount];
        dispatch_semaphore_t jobSemaphore = dispatch_semaphore_create(cpuCount * 2);
        dispatch_group_t group = dispatch_group_create();
        __block uint32_t count = -1;
        for(NSString *path in enumerator)
        {
            WithAutoreleasePool(^{
                if([[[path pathExtension] lowercaseString] isEqual: @"jpg"])
                {
                    NSString *fullPath = [dir stringByAppendingPathComponent: path];
                    dispatch_semaphore_wait(jobSemaphore, DISPATCH_TIME_FOREVER);
                    dispatch_group_async(group, ioQueue, BlockWithAutoreleasePool(^{
                        NSData *data = [NSData dataWithContentsOfFile: fullPath];
                        dispatch_group_async(group, globalQueue, BlockWithAutoreleasePool(^{
                            NSData *thumbnailData = ThumbnailDataForData(data);
                            if(thumbnailData)
                            {
                                NSString *thumbnailName = [NSString stringWithFormat: @"%d.jpg",
                                                           OSAtomicIncrement32(&count;)];
                                NSString *thumbnailPath = [destination stringByAppendingPathComponent: thumbnailName];
                                dispatch_group_async(group, ioQueue, BlockWithAutoreleasePool(^{
                                    [thumbnailData writeToFile: thumbnailPath atomically: NO];
                                    dispatch_semaphore_signal(jobSemaphore);
                                }));
                            }
                            else
                                dispatch_semaphore_signal(jobSemaphore);
                        }));
                    }));
                }
            });
        }
        dispatch_group_wait(group, DISPATCH_TIME_FOREVER);

最终我们写出了一个能平滑运行且又快速处理的程序。



**基准测试**

我测试了一些运行时间，对7913张图片：



**程序****处理时间 (秒)**

`imagegcd1.m`

984

`imagegcd2.m`

没运行，这个还是别运行了

`imagegcd3.m`

300

`imagegcd4.m`

279





注意，因为我比较懒。所以我在运行这些测试的时候，没有关闭电脑上的其他程序。。。严格的进行对照的话，实在是太蛋疼了。。

所以这个数值我们只是参考一下。

比较有意思的是，3和4的执行状况差不多，大概是因为我电脑有15g可用内存吧。。。内存比较小的话，这个imagegcd3应该跑的很吃力，因为我发现它使用最多的
时候，占用了10g内存。而4的话，没有占多少内存。

**结论**

GCD是个比较范特西的技术，可以办到很多事儿，但是它不能为你办所有的事儿。所以，对于进行IO操作并且可能会使用大量内存的任务，我们必须仔细斟酌。当然，即使这样，GCD还是为我们提供了简单有效的方法来进行并发计算。

