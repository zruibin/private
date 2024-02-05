 
<!--BEGIN_DATA
{
    "create_date": "2017-01-09 16:37", 
    "modify_date": "2017-01-09 16:37", 
    "is_top": "0", 
    "summary": "译文：理解Java中的弱引用", 
    "tags": "Android", 
    "file_name": "译文：理解Java中的弱引用.md"
}
END_DATA-->

####<p>原文出处：<a href='http://droidyue.com/blog/2014/10/12/understanding-weakreference-in-java/' target='blank'>译文：理解Java中的弱引用</a></p>

不久之前，我面试了一些求职Java高级开发工程师的应聘者。我常常会面试他说，“你能给我介绍一些Java中得弱引用吗？”，如果面试者这样说，“嗯，是不是垃圾回收有关的？”，我就会基本满意了，我并不期待回答是一篇诘究本末的论文描述。

然而事与愿违，我很吃惊的发现，在将近20多个有着平均5年开发经验和高学历背景的应聘者中，居然只有两个人知道弱引用的存在，但是在这两个人之中只有一个人真正了解这方面的知识。在面试过程中，我还尝试提示一些东西，来看看有没有人突然说一声“原来是这个啊”，结果很是让我失望。我开始困惑，为什么这块的知识如此不被重视，毕竟弱引用是一个很有用途的特性，况且这个特性已经在7年前 Java 1.2发布时便引入了。

好吧，这里我不期待你看完本文之后成为一个弱引用方面的专家，但是我认为至少你应该了解什么是弱引用，如何使用它们，并且什么场景使用。既然它们是一些不知名的概念，我简单就着前面的三个问题来说明一下。

###强引用(Strong Reference)

强引用就是我们经常使用的引用，其写法如下

    
    StringBuffer buffer = new StringBuffer();
    

上面创建了一个StringBuffer对象，并将这个对象的（强）引用存到变量buffer中。是的，就是这个小儿科的操作（请原谅我这样的说法）。强引用最重要的就是它能够让引用变得强（Strong），这就决定了它和垃圾回收器的交互。具体来说，如果一个对象通过一串强引用链接可到达(Strongly reachable)，它是不会被回收的。如果你不想让你正在使用的对象被回收，这就正是你所需要的。

####但是强引用如此之强

在一个程序里，将一个类设置成不可被扩展是有点不太常见的，当然这个完全可以通过类标记成final实现。或者也可以更加复杂一些，就是通过内部包含了未知数量具体实
现的工厂方法返回一个接口(Interface)。举个例子，我们想要使用一个叫做Widget的类，但是这个类不能被继承，所以无法增加新的功能。

但是我们如果想追踪Widget对象的额外信息，我们该怎么办？ 假设我们需要记录每个对象的序列号，但是由于Widget类并不包含这个属性，而且也不能扩展导致我们也不能增加这个属性。其实一点问题也没有，HashMap完全可以解决上述的问题。

    
    serialNumberMap.put(widget, widgetSerialNumber);
    

这表面看上去没有问题，但是widget对象的强引用很有可能会引发问题。我们可以确信当一个widget序列号不需要时，我们应该将这个条目从map中移除。如果我们没有移除的话，可能会导致内存泄露，亦或者我们手动移除时删除了我们正在使用的widgets，会导致有效数据的丢失。其实这些问题很类似，这就是没有垃圾回收机制的语言管理内存时常遇到的问题。但是我们不用去担心这个问题，因为我们使用的时具有垃圾回收机制的Java语言。

另一个强引用可能带来的问题就是缓存,尤其是像图片这样的大文件的缓存。假设你有一个程序需要处理用户提供的图片，通常的做法就是做图片数据缓存，因为从磁盘加载图片代价很大，并且同时我们也想避免在内存中同时存在两份一样的图片数据。

缓存被设计的目的就是避免我们去再次加载哪些不需要的文件。你会很快发现在缓存中会一直包含一个到已经指向内存中图片数据的引用。使用强引用会强制图片数据留在内存，这就需要你来决定什么时候图片数据不需要并且手动从缓存中移除，进而可以让垃圾回收器回收。因此你再一次被强制做垃圾回收器该做的工作，并且人为决定是该清理到哪一个对象。

###弱引用(Weak Reference)

弱引用简单来说就是将对象留在内存的能力不是那么强的引用。使用WeakReference，垃圾回收器会帮你来决定引用的对象何时回收并且将对象从内存移除。创建弱
引用如下

    
    WeakReference<Widget> weakWidget = new WeakReference<Widget>(widget);
    

使用weakWidget.get()就可以得到真实的Widget对象，因为弱引用不能阻挡垃圾回收器对其回收，你会发现（当没有任何强引用到widget对象时）使用get时突然返回null。

解决上述的widget序列数记录的问题，最简单的办法就是使用Java内置的WeakHashMap类。WeakHashMap和HashMap几乎一样，唯一的区别就是它的键（不是值!!!）使用WeakReference引用。当WeakHashMap的键标记为垃圾的时候，这个键对应的条目就会自动被移除。这就避免了上面不需要的Widget对象手动删除的问题。使用WeakHashMap可以很便捷地转为HashMap或者Map。

####引用队列(Reference Queue)

一旦弱引用对象开始返回null，该弱引用指向的对象就被标记成了垃圾。而这个弱引用对象（非其指向的对象）就没有什么用了。通常这时候需要进行一些清理工作。比如WeakHashMap会在这时候移除没用的条目来避免保存无限制增长的没有意义的弱引用。

引用队列可以很容易地实现跟踪不需要的引用。当你在构造WeakReference时传入一个ReferenceQueue对象，当该引用指向的对象被标记为垃圾的时候，这个引用对象会自动地加入到引用队列里面。接下来，你就可以在固定的周期，处理传入的引用队列，比如做一些清理工作来处理这些没有用的引用对象。

###四种引用

Java中实际上有四种强度不同的引用，从强到弱它们分别是，强引用，软引用，弱引用和虚引用。上面部分介绍了强引用和弱引用，下面介绍剩下的两个，软引用和虚引用。

###软引用（Soft Reference）

软引用基本上和弱引用差不多，只是相比弱引用，它阻止垃圾回收期回收其指向的对象的能力强一些。如果一个对象是弱引用可到达，那么这个对象会被垃圾回收器接下来的回收周期销毁。但是如果是软引用可以到达，那么这个对象会停留在内存更时间上长一些。当内存不足时垃圾回收器才会回收这些软引用可到达的对象。

由于软引用可到达的对象比弱引用可达到的对象滞留内存时间会长一些，我们可以利用这个特性来做缓存。这样的话，你就可以节省了很多事情，垃圾回收器会关心当前哪种可到达类型以及内存的消耗程度来进行处理。

###虚引用 （Phantom Reference）

与软引用，弱引用不同，虚引用指向的对象十分脆弱，我们不可以通过get方法来得到其指向的对象。它的唯一作用就是当其指向的对象被回收之后，自己被加入到引用队列，用作记录该引用指向的对象已被销毁。

当弱引用的指向对象变得弱引用可到达，该弱引用就会加入到引用队列。这一操作发生在对象析构或者垃圾回收真正发生之前。理论上，这个即将被回收的对象是可以在一个不符合规范的析构方法里面重新复活。但是这个弱引用会销毁。虚引用只有在其指向的对象从内存中移除掉之后才会加入到引用队列中。其get方法一直返回null就是为了阻止其指向的几乎被销毁的对象重新复活。

虚引用使用场景主要由两个。它允许你知道具体何时其引用的对象从内存中移除。而实际上这是Java中唯一的方式。这一点尤其表现在处理类似图片的大文件的情况。当你确
定一个图片数据对象应该被回收，你可以利用虚引用来判断这个对象回收之后在继续加载下一张图片。这样可以尽可能地避免可怕的内存溢出错误。

第二点，虚引用可以避免很多析构时的问题。finalize方法可以通过创建强引用指向快被销毁的对象来让这些对象重新复活。然而，一个重写了finalize方法的对象如果想要被回收掉，需要经历两个单独的垃圾收集周期。在第一个周期中，某个对象被标记为可回收，进而才能进行析构。但是因为在析构过程中仍有微弱的可能这个对象会重新复活。这种情况下，在这个对象真实销毁之前，垃圾回收器需要再次运行。因为析构可能并不是很及时，所以在调用对象的析构之前，需要经历数量不确定的垃圾收集周期。
这就意味着在真正清理掉这个对象的时候可能发生很大的延迟。这就是为什么当大部分堆被标记成垃圾时还是会出现烦人的内存溢出错误。

使用虚引用，上述情况将引刃而解，当一个虚引用加入到引用队列时，你绝对没有办法得到一个销毁了的对象。因为这时候，对象已经从内存中销毁了。因为虚引用不能被用作让其指向的对象重生，所以其对象会在垃圾回收的第一个周期就将被清理掉。

显而易见，finalize方法不建议被重写。因为虚引用明显地安全高效，去掉finalize方法可以虚拟机变得明显简单。当然你也可以去重写这个方法来实现更多。
这完全看个人选择。

###总结

我想看到这里，很多人开始发牢骚了，为什么你要讲一个过去十年的老古董API呢，好吧，以我的经验看，很多的Java程序员并不是很了解这个知识，我认为有一些深入的
理解是很必要的，同时我希望大家能从本文中收获一些东西。

###原文信息

  * 文章出自 [Understanding Weak References](https://weblogs.java.net/blog/enicholas/archive/2006/05/understanding_w.html)
  * 作者为[Ethan Nicholas](https://www.java.net/blogs/enicholas)，Yahoo! Publishing Tools team Leader，Yahoo! SiteBuilder Web程序的早期作者。

###附注信息

本文涉及到很多概念对于初次接触的人相对比较难以理解，建议结合英文原文进行研究。

####Java高阶推荐

  * [Java虚拟机规范(Java SE 7版)](http://www.amazon.cn/gp/product/B00H1FXTNM/ref=as_li_qf_sp_asin_tl?ie=UTF8&camp=536&creative=3200&creativeASIN=B00H1FXTNM&linkCode=as2&tag=droidyue-23)
  * [图灵程序设计丛书:Java性能优化权威指南](http://www.amazon.cn/gp/product/B00IOB0K1Q/ref=as_li_qf_sp_asin_tl?ie=UTF8&camp=536&creative=3200&creativeASIN=B00IOB0K1Q&linkCode=as2&tag=droidyue-23)
  * [深入理解Java虚拟机:JVM高级特性与最佳实践(第2版)](http://www.amazon.cn/gp/product/B00D2ID4PK/ref=as_li_qf_sp_asin_tl?ie=UTF8&camp=536&creative=3200&creativeASIN=B00D2ID4PK&linkCode=as2&tag=droidyue-23)

  

<hr>



如果一个内存中的对象没有任何引用的话，就说明这个对象已经不再被使用了，从而可以成为被垃圾回收的候选。不过由于垃圾回收器的运行时间不确定，可被垃圾回收的对象的实际被回收时间是不确定的。对于一个对象来说，只要有引用的存在，它就会一直存在于内存中。如果这样的对象越来越多，超出了JVM中的内存总数，JVM就会抛出OutOfMemory错误。虽然垃圾回收的具体运行是由JVM来控制的，但是开发人员仍然可以在一定程度上与垃圾回收器进行交互，其目的在于更好的帮助垃圾回收器管理好应用的内存。这种交互方式就是使用JDK 1.2引入的java.lang.ref包。

####1 强引用

强引用是使用最普遍的引用。如果一个对象具有强引用，那垃圾回收器绝不会回收它。当内存空间不足，Java虚拟机宁愿抛出OutOfMemoryError错误，使程序异常终止，也不会靠随意回收具有强引用的对象来解决内存不足的问题。
如Date date = new Date()，date就是一个对象的强引用。对象的强引用可以在程序中到处传递。很多情况下，会同时有多个引用指向同一个对象。强引用的存在限制了对象在内存中的存活时间。假如对象A中包含了一个对象B的强引用，那么一般情况下，对象B的存活时间就不会短于对象A。如果对象A没有显式的把对象B的引用设为null的话，就只有当对象A被垃圾回收之后，对象B才不再有引用指向它，才可能获得被垃圾回收的机会。
实例代码：

	package com.skywang.java;
	 
	public class StrongReferenceTest {
	 
	 public static void main(String[] args) {
	  MyDate date = new MyDate();
	  System.gc();
	 }
	}
	
运行结果：

	<无任何输出>

结果说明：即使显式调用了垃圾回收，但是用于date是强引用，date没有被回收。
除了强引用之外，java.lang.ref包中提供了对一个对象的不同的引用方式。JVM的垃圾回收器对于不同类型的引用有不同的处理方式。

####2 软引用

如果一个对象只具有软引用，则内存空间足够，垃圾回收器就不会回收它；如果内存空间不足了，就会回收这些对象的内存。只要垃圾回收器没有回收它，该对象就可以被程序使用。软引用可用来实现内存敏感的高速缓存。

软引用可以和一个引用队列（ReferenceQueue）联合使用，如果软引用所引用的对象被垃圾回收器回收，Java虚拟机就会把这个软引用加入到与之关联的引用队列中。

软引用（soft reference）在强度上弱于强引用，通过类SoftReference来表示。它的作用是告诉垃圾回收器，程序中的哪些对象是不那么重要，当内存不足的时候是可以被暂时回收的。当JVM中的内存不足的时候，垃圾回收器会释放那些只被软引用所指向的对象。如果全部释放完这些对象之后，内存还不足，才会抛出OutOfMemory错误。

软引用非常适合于创建缓存。当系统内存不足的时候，缓存中的内容是可以被释放的。比如考虑一个图像编辑器的程序。该程序会把图像文件的全部内容都读取到内存中，以方便进行处理。而用户也可以同时打开多个文件。当同时打开的文件过多的时候，就可能造成内存不足。如果使用软引用来指向图像文件内容的话，垃圾回收器就可以在必要的时候回收掉这些内存。   
  
实例代码：


	package com.skywang.java;
	 
	import java.lang.ref.SoftReference;
	 
	public class SoftReferenceTest {
	 
	 public static void main(String[] args) {
	  SoftReference ref = new SoftReference(new MyDate());
	  ReferenceTest.drainMemory();
	 }
	}
	
运行结果：

	<无任何输出>
	
结果说明：在内存不足时，软引用被终止。软引用被禁止时，

	SoftReference ref = new SoftReference(new MyDate());
	ReferenceTest.drainMemory();

等价于

	MyDate date = new MyDate();
	 
	// 由JVM决定运行
	if(JVM.内存不足()) {
	 date = null;
	 System.gc();
	}
	
####3 弱引用

弱引用（weak reference）在强度上弱于软引用，通过类WeakReference来表示。它的作用是引用一个对象，但是并不阻止该对象被回收。如果使用一个强引用的话，只要该引用存在，那么被引用的对象是不能被回收的。弱引用则没有这个问题。在垃圾回收器运行的时候，如果一个对象的所有引用都是弱引用的话，该对象会被回收。弱引用的作用在于解决强引用所带来的对象之间在存活时间上的耦合关系。弱引用最常见的用处是在集合类中，尤其在哈希表中。哈希表的接口允许使用任何Java对象作为键来使用。当一个键值对被放入到哈希表中之后，哈希表对象本身就有了对这些键和值对象的引用。如果这种引用是强引用的话，那么只要哈希表对象本身还存活，其中所包含的键和值对象是不会被回收的。如果某个存活时间很长的哈希表中包含的键值对很多，最终就有可能消耗掉JVM中全部的内存。

对于这种情况的解决办法就是使用弱引用来引用这些对象，这样哈希表中的键和值对象都能被垃圾回收。Java中提供了WeakHashMap来满足这一常见需求。

示例代码：

	package com.skywang.java;
	 
	import java.lang.ref.WeakReference;
	 
	public class WeakReferenceTest {
	 
	 public static void main(String[] args) {
	  WeakReference ref = new WeakReference(new MyDate());
	  System.gc(); 
	 }
	}
	
运行结果：

	obj [Date: 1372142034360] is gc
	
结果说明：在JVM垃圾回收运行时，弱引用被终止.

	WeakReference ref = new WeakReference(new MyDate());
	System.gc();
	
等同于：

	MyDate date = new MyDate();
	 
	// 垃圾回收
	if(JVM.内存不足()) {
	 date = null;
	 System.gc();
	}
	
弱引用与软引用的区别在于：只具有弱引用的对象拥有更短暂的生命周期。在垃圾回收器线程扫描它所管辖的内存区域的过程中，一旦发现了只具有弱引用的对象，不管当前内存空间足够与否，都会回收它的内存。不过，由于垃圾回收器是一个优先级很低的线程，因此不一定会很快发现那些只具有弱引用的对象。

弱引用可以和一个引用队列（ReferenceQueue）联合使用，如果弱引用所引用的对象被垃圾回收，Java虚拟机就会把这个弱引用加入到与之关联的引用队列中。

####4 假象引用

又叫幽灵引用~在介绍幽灵引用之前，要先介绍Java提供的对象终止化机制（finalization）。在Object类里面有个finalize方法，其设计的初衷是在一个对象被真正回收之前，可以用来执行一些清理的工作。因为Java并没有提供类似C++的析构函数一样的机制，就通过 finalize方法来实现。但是问题在于垃圾回收器的运行时间是不固定的，所以这些清理工作的实际运行时间也是不能预知的。幽灵引用（phantom reference）可以解决这个问题。在创建幽灵引用PhantomReference的时候必须要指定一个引用队列。当一个对象的finalize方法已经被调用了之后，这个对象的幽灵引用会被加入到队列中。通过检查该队列里面的内容就知道一个对象是不是已经准备要被回收了。

幽灵引用及其队列的使用情况并不多见，主要用来实现比较精细的内存使用控制，这对于移动设备来说是很有意义的。程序可以在确定一个对象要被回收之后，再申请内存创建新的对象。通过这种方式可以使得程序所消耗的内存维持在一个相对较低的数量。
 
比如下面的代码给出了一个缓冲区的实现示例。

	
	public class PhantomBuffer {
	 private byte[] data = new byte[0];
	 private ReferenceQueue<byte[]> queue = new ReferenceQueue<byte[]>();
	 private PhantomReference<byte[]> ref = new PhantomReference<byte[]>(data, queue);
	 public byte[] get(int size) {
	  if (size <= 0) {
	   throw new IllegalArgumentException("Wrong buffer size");
	  }
	  if (data.length < size) {
	   data = null;
	   System.gc(); //强制运行垃圾回收器
	    try {
	    queue.remove(); //该方法会阻塞直到队列非空
	    ref.clear(); //幽灵引用不会自动清空，要手动运行
	    ref = null;
	    data = new byte[size];
	    ref = new PhantomReference<byte[]>(data, queue);
	   } catch (InterruptedException e) {
	    e.printStackTrace();
	   }
	  }
	  return data;
	 }
	}
	
在上面的代码中，每次申请新的缓冲区的时候，都首先确保之前的缓冲区的字节数组已经被成功回收。引用队列的remove方法会阻塞直到新的幽灵引用被加入到队列中。不过需要注意的是，这种做法会导致垃圾回收器被运行的次数过多，可能会造成程序的吞吐量过低。

示例代码：
	
	package com.skywang.java;
	 
	import java.lang.ref.ReferenceQueue;
	import java.lang.ref.PhantomReference;
	 
	public class PhantomReferenceTest {
	 
	 public static void main(String[] args) {
	  ReferenceQueue queue = new ReferenceQueue();
	  PhantomReference ref = new PhantomReference(new MyDate(), queue);
	  System.gc();
	 }
	}
运行结果：

	obj [Date: 1372142282558] is gc
	
结果说明：假象引用，在实例化后，就被终止了。

	ReferenceQueue queue = new ReferenceQueue();
	PhantomReference ref = new PhantomReference(new MyDate(), queue);
	System.gc();

等同于：

	MyDate date = new MyDate();
	date = null;
