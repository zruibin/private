 
<!--BEGIN_DATA
{
    "create_date": "2016-08-05 17:53", 
    "modify_date": "2016-08-05 17:53", 
    "is_top": "0", 
    "summary": "iOS Interview Questions", 
    "tags": "iOS", 
    "file_name": "iOS Interview Questions.md"
}
END_DATA-->

####<p>原文出处：<a href='https://www.raywenderlich.com/53962/ios-interview-questions' target='blank'> iOS Interview Questions</a></p>


Explain method swizzling. When you would use it? — I like this question because it’s deep language. Most people will never need to use swizzling. The developer’s answer to this question also shows me how much restraint s/he has when implementing complex code. An answer of “I swizzle everything” is much scarier than someone saying they have never worked with it.

请解释下method swizzling，并说出你一般什么时候会用到它？- 我喜欢问这个问题因为这属于较为深层次的语法。大多数人都没有使用swizzling的需求（言外之意会用到swizzling的一般开发过一些核心的内容了）。而且通过开发者关于这个问题的回答，我还可以了解他们对复杂代码的执行有多大程度上的约束。一个人如果说他 swizzle所有的代码，那比那些说从来没用过swizzle的人更可怕。（译者注：了解更多 method swizzling）


Take three objects: a grandparent, parent and child. The grandparent retains the parent, the parent retains the child and the child retains the parent. The grandparent releases the parent. Explain what happens. — Even with ARC, I like to ask a lot of memory-related questions, as it shows that someone has been around for a while and has core knowledge about how things work.

（补译）有三个对象，一个父类的父类，一个父类和一个子类。父类的父类持有父类的引用（retain），父类持有子类的引用（retain），子类持有父类的引用（retain）。父类的父类释放（release）父类，解释下会发生什么。 - 即使有ARC，我依然喜欢问一些内存相关的问题，这显示了这个人已经开发了有一段时间而且明白核心的框架是如何运作的（断句）。

校对版：假设有三个对象，一个父类的父类，一个父类和一个子类。父类的父类持有父类的引用（retain），父类持有子类的引用（retain），子类持有父类的引用（retain）。父类的父类释放（release）父类，解释下会发生什么。 - 即使有ARC，我依然喜欢问一些内存相关的问题，这显示了这个人有一定时间的开发经验，而且明白核心的框架是如何运作的。

What happens when you invoke a method on a nil pointer? — Basic Objective-C handling is important and it’s shocking how many times I have heard wrong answers to questions like this.

给一个空指针（nil pointer）调用了一个方法会发生什么？ - 基础的Object-C的相关处理是很重要的，有好多次我都听到了错误的回答，这很令我震惊。


校对版：当一个空指针（nil pointer）调用了一个方法会发生什么？了解处理基础的Objective-C相关问题是很重要的，有好多次我都听到了错误的回答，这很令我震惊。

Give two separate and independent reasons why retainCount should never be used in shipping code. — This question has two benefits: to make sure someone isn’t using retainCount and to see if they understand why they shouldn’t use it.

为什么retainCount绝对不能用在发布（的）代码中？请给出两个相对独立的解释。—— 考察这个问题会有两个好处:可以了解面试者目前确实没有使用retainCount，并且看看他们是否知道为什么他们不应该使用。

校对版：为什么retainCount绝对不能用在发布的代码中？请给出两个相对独立的解释。—— 考察这个问题会有两个好处:一是可以确定面试者目前确实没有使用retainCount，并且看看他们是否知道为什么他们不应该使用。


Explain your process for tracing and fixing a memory leak. — This dives into the applicant’s knowledge of memory, instruments and the debugging process. Sometimes I hear things like “start commenting out code until it is fixed,” which is slightly terrifying.

解释下你查找或者解决内存泄露的处理过程。 - 这个可以深入了解面试者对内存管理方面的知识，instruments的运用及其调试的处理过程。有时候我会听到一些可怕的回答：“注释掉部分代码直到内存泄露问题被修复”。

校对版：请说明一下你查找或者解决内存泄露的处理过程。这个可以深入了解面试者对内存管理方面的知识，instruments的运用及其调试的处理过程。有时候我会听到一些可怕的回答：“注释掉部分代码直到内存泄露问题被修复”。



Explain how an autorelease pool works at the runtime level. — These types of questions go beyond the basics a programmer will learn from a couple of books and investigates his or her knowledge of how things actually work.

解释下自动回收池(autorelease pool)在程序运行时是如何运作的。 - 这类型的问题已经超出代码基础了，一个程序员只有阅读过一部分开发类书籍才能学到这些内容。这些问题也同样能考察他对程序底层代码运作的了解程度。


When dealing with property declarations, what is the difference between atomic and non-atomic? — Once again, it is shocking how many people don’t know the answer to this question. Many just declare properties a certain way because it’s what they’ve seen others do. Questions like these expose those issues.

当处理属性申明的时候，原子（atomic）跟 非原子（non-atomic）属性有什么区别？- 好多人都不知道这个问题的答案，我又一次震惊了。很多人他们都是看别人是怎么声明的，他们就怎么来声明。类似这种的题目会暴漏出来很多问题。

In C, how would you reverse a string as quickly as possible? — I don’t like to dive too deeply into computer science, but this question lets me know how someone thinks about performance as well as about his or her background in C. I have also been known to dig into big O notation.

在C语言中，你如何能用尽可能短的时间来倒转一个字符串？- 我不大喜欢深入问计算机的核心内容， 但是通过这个问题可以让我了解到他们是如何思考的，同样也可以了解到他们的C语言背景。深入询问时间复杂度（big O notation）也能让我了解面试者的水平。

Which is faster: to iterate through an NSArray or an NSSet? — Another deep dive. Sometimes just because a class solves a problem doesn’t mean it’s the one you should be using.

遍历一个NSArray和一个NSSet，哪一个更快？ - 另一个深入的提问。有时候一个类解决了问题并不能代表你就应该用这个类。

Explain how code signing works. — A lot of applicants have no idea how code signing works and then complain because they are having code signing issues.

解释代码签名（code signing）是如何运作的。 - 很多候选人都完全不了解代码签名是如何运作的，然后抱怨说他们一直被一些代码签名的一些问题所困扰。

What is posing in Objective-C? — Posing is a little-used feature of Objective-C. Like the swizzling question, this gives me an indication of how deep someone has dived into the language.

Objective-C中的posing指的是什么？ - Posing是一个Object-C的小众语法特性。像 swizzling那个问题一样，这个问题可以让我了解面试者对语言的深入程度。 


List six instruments that are part of the standard. — This question gives me a general idea of how much time someone has spent in instruments. Hint: It should be at least 10% of your coding time, if not more.

列举标准Xcode版本中的6个工具。 - 通过这个问题我可以大致的了解到面试者会在这些工具上花费多少时间。提示：如果你没有更多的时间来使用这些工具，那你至少得用10%的写代码的时间来用这些工具。


校对版：列举标准Xcode版本中的6个工具。 - 通过这个问题我可以大致的了解到面试者会在这些工具上花费多少时间。提示：至少得用10%的写代码的时间来用这些工具。

What are the differences between copy and retain? — Memory questions reveal a lot about a developer’s knowledge, especially since many people are leaning on ARC these days.

copy跟retain有什么区别？ - 最近好多开发者都开始用ARC了，内存方面的问题就更能反映出一个开发者的知识水平了。

What is the difference between frames and bounds? — I don’t ask a lot of GUI-type questions and I probably should ask more, but this one gives me an idea of how much layout work a developer has done.

frames跟bounds有哪些区别？ - 我不会问很多界面相关 （GUI-type）的问题，我应该问的多一些，不过通过这个问题我差不多能了解到一个开发者做了多少界面工作。

What happens when the following code executes? Ball *ball = [[[[Ball alloc] init] autorelease] autorelease]; — Another memory question. The answer I am looking for here is not just that it will crash, which it will – I want to know why and when.

执行如下的代码会发生什么情况？
Ball *ball = [[[[Ball alloc] init] autorelease] autorelease];
另一个内存相关的问题，这个问题的答案不能单用会崩溃来回答，我想要知道为什么崩溃，何时会崩溃。

List the five iOS app states. — Almost no one gets this question right. Normally I have to give an example, such as background state, for them to know what I am talking about.

列举5个iOS app的状态。- 几乎没有人能正确的回答出这个问题，通常我会给出一个例子，诸如后台运行的状态（background state），这样他们就知道我在说的是那块儿内容了。

Do you think this interview was a good representation of your skills as a developer? — Some people test well and some don’t. I like to give people the option to explain their results a little. Confidence is important and the answer to this question can reveal a lot about a person’s confidence.

你认为这次面试能很好的体现出来你作为开发者的能力么？- 一些人说可以测试的很好，但是有些人不这么认为。我倾向于给面试者一些表达他们自己想法的机会。自信是非常重要的品质，而对应这个问题的回答也能很好的反应出一个人的自信程度。






<hr>








####<p>原文出处：<a href='http://www.cnblogs.com/samniu/p/3855167.html' target='blank'>iOS interview questions and Answers</a></p>

**1-How would you create your own custom view?**

> By Subclassing the UIView class.

**2-Whats fast enumeration**?

> Fast enumeration is a language feature that allows you to enumerate over the
contents of a collection. (Your code will also run faster because the internal
implementation reduces  
message send overhead and increases pipelining potential.)

**3-Whats a struct?**

> A struct is a special C data type that encapsulates other pieces of data
into a single cohesive unit. Like an object, but built into C.

**4-**What are mutable and immutable types in Objective C?****

> Mutable means you can change its contents later but when you mark any object
immutable, it means once they are initialized, their values cannot be changed.
For example, NSArray, NSString values cannot be changed after initialized.

**5-Explain retain counts**.

> Retain counts are the way in which memory is managed in Objective-C. When
you create an object, it has a retain count of 1. When you send an object a
retain message, its retain count is incremented by 1. When you send an object
a release message, its retain count is decremented by 1. When you send an
object a autorelease message, its retain count is decremented by 1 at some
stage in the future. If an objectʼs retain count is reduced to 0, it is
deallocated.

**6-Whats the difference between frame and bounds**?

> The frame of a view is the rectangle, expressed as a location (x,y) and size
(width,height) relative to the superview it is contained within. The bounds of
a view is the rectangle, expressed as a location (x,y) and size (width,height)
relative to its own coordinate system (0,0).

**7-Is a delegate retained**?

> No, the delegate is never retained! Ever!

**8-Outline the class hierarchy for a UIButton until NSObject.**

> UIButton inherits from UIControl, UIControl inherits from UIView, UIView
inherits from UIResponder, UIResponder inherits from the root class NSObject

####**9- What is `dynamic`?**

> You use the `@dynamic` keyword to tell the compiler that you will fulfill
the API contract implied by a property either by providing method
implementations directly or at runtime using other mechanisms such as dynamic
loading of code or dynamic method resolution. It suppresses the warnings that
the compiler would otherwise generate if it can't find suitable
implementations. You should use it only if you know that the methods will be
available at runtime

**10-If I call performSelector:withObject:afterDelay: - is the object retained?**

> Yes, the object is retained. It creates a timer that calls a selector on the
current threads run loop. It may not be 100% precise time-wise as it attempts
to dequeue the message from  
the run loop and perform the selector.

**11-Can you explain what happens when you call autorelease on an object?**

> When you send an object a autorelease message, its retain count is
decremented by 1 at some stage in the future. The object is added to an
autorelease pool on the current thread. The main thread loop creates an
autorelease pool at the beginning of the function, and release it at the end.
This establishes a pool for the lifetime of the task. However, this also means
that any autoreleased objects created during the lifetime of the task are not
disposed of until the task completes. This may lead to the taskʼs memory
footprint increasing unnecessarily. You can also consider creating pools with
a narrower scope or use NSOperationQueue with itʼs own autorelease pool. (Also
important - You only release or autorelease objects you own.)

**12-Whats the NSCoder class used for?**

> NSCoder is an abstractClass which represents a stream of data. They are used
in Archiving and Unarchiving objects. NSCoder objects are usually used in a
method that is being implemented so that the class conforms to the protocol.
(which has something like encodeObject and decodeObject methods in them).

**13-Whats an NSOperationQueue and how/would you use it?**

> The NSOperationQueue class regulates the execution of a set of NSOperation
objects. An operation queue is generally used to perform some asynchronous
operations on a background thread so as not to block the main thread.

**14-Explain the correct way to manage Outlets memory**

> Create them as properties in the header that are retained. In the
viewDidUnload set the outlets to nil(i.e self.outlet = nil). Finally in
dealloc make sure to release the outlet.

**15-Is the delegate for a CAAnimation retained?**

> Yes it is!! This is one of the rare exceptions to memory management rules.

**16-What happens when the following code executes?**

**Ball *ball = [[[[Ball alloc] init] autorelease] autorelease];**

> It will crash because itʼs added twice to the autorelease pool and when it
it dequeued the autorelease pool calls release more than once.

**17-Explain the difference between NSOperationQueue concurrent and non-concurrent.**

> In the context of an NSOperation object, which runs in an NSOperationQueue,
the terms concurrent and non-concurrent do not necessarily refer to the side-
by-side execution of threads. Instead, a non-concurrent operation is one that
executes using the environment that is provided for it while a concurrent
operation is responsible for setting up its own execution environment.

**18-Implement your own synthesized methods for the property NSString *title.**

> Well you would want to implement the getter and setter for the title object.
Something like this: view source print?
>
> \- (NSString*) title // Getter method
>
> return title;
>
> \- (void) setTitle: (NSString*) newTitle //Setter method
>
> if (newTitle != title)
>
> [title release];
>
> title = [newTitle retain]; // Or copy, depending on your needs.

**19-Implement the following methods: retain, release, autorelease.**

> -(id)retain
>
> NSIncrementExtraRefCount(self);
>
> return self;
>
> -(void)release
>
> if(NSDecrementExtraRefCountWasZero(self))
>
> NSDeallocateObject(self);
>
> -(id)autorelease
>
> { // Add the object to the autorelease pool
>
> [NSAutoreleasePool addObject:self];
>
> return self**20-**What are the App states. Explain them?****
>   * **Not running State**: The app has not been launched or was running but
was terminated by the system.
>   * **Inactive state:** The app is running in the foreground but is
currently not receiving events. (It may be executing other code though.) An
app usually stays in this state only briefly as it transitions to a different
state. The only time it stays inactive for any period of time is when the user
locks the screen or the system prompts the user to respond to some event, such
as an incoming phone call or SMS message.
>   * **Active state**: The app is running in the foreground and is receiving
events. This is the normal mode for foreground apps.
>   * **Background state**: The app is in the background and executing code.
Most apps enter this state briefly on their way to being suspended. However,
an app that requests extra execution time may remain in this state for a
period of time. In addition, an app being launched directly into the
background enters this state instead of the inactive state. For information
about how to execute code while in the background, see "Background Execution
and Multitasking."
>   * **Suspended state:**The app is in the background but is not executing
code. The system moves apps to this state automatically and does not notify
them before doing so. While suspended, an app remains in memory but does not
execute any code. When a low-memory condition occurs, the system may purge
suspended apps without notice to make more space for the foreground app.

**21-What is Automatic Reference Counting (ARC) ?**

> ARC is a compiler-level feature that simplifies the process of managing the
lifetimes of Objective-C objects. Instead of you having to remember when to
retain or release an object, ARC evaluates the lifetime requirements of your
objects and automatically inserts the appropriate method calls at compile
time.

**22-Multitasking support is available from which version?**

> iOS 4 and above supports multi-tasking and allows apps to remain in the
background until they are launched again or until they are terminated.

**23-How many bytes we can send to apple push notification server.**

> 256bytes.

**24-What is the difference between retain & assign?**

> **Assign** creates a reference from one object to another without increasing
the source's retain count.
>
> `if (_variable != object)`
>
> `{`
>
> `[_variable release];`
>
> `_variable = nil;`
>
> `_variable = object;`
>
> `}`
>
> **Retain** creates a reference from one object to another and increases the
retain count of the source object.
>
> `if (_variable != object)`
>
> `{ [_variable release];`
>
> `_variable = nil;`
>
> `_variable = [object retain];`
>
> `}`

**25-Why do we need to use @Synthesize?**

> We can use generated code like nonatomic, atmoic, retain without writing any
lines of code. We also have getter and setter methods. To use this, you have 2
other ways: @synthesize or @dynamic: @synthesize, compiler will generate the
getter and setter automatically for you, @dynamic: you have to write them
yourself.@property is really good for memory management, for example:
retain.How can you do retain without @property?
>
> `if (_variable != object)`
>
> `{`
>
> `[_variable release];`
>
> `_variable = nil;`
>
> `_variable = [object retain];`
>
> `}`
>
> How can you use it with @property?`self.variable = object;`When we are
calling the above line, we actually call the setter like [self
setVariable:object] and then the generated setter will do its job

**26-What is categories in iOS?**

> A Category is a feature of the Objective-C language that enables you to add
methods (interface and implementation) to a class without having to make a
subclass. There is no runtime difference--within the scope of your program--
between the original methods of the class and the methods added by the
category. The methods in the category become part of the class type and are
inherited by all the class's subclasses.As with delegation, categories are not
a strict adaptation of the Decorator pattern, fulfilling the intent but taking
a different path to implementing that intent. The behavior added by categories
is a compile-time artifact, and is not something dynamically acquired.
Moreover, categories do not encapsulate an instance of the class being
extended.

**27-What is Delegation in iOS?**

> Delegation is a design pattern in which one object sends messages to another
object--specified as its delegate--to ask for input or to notify it that an
event is occurring. Delegation is often used as an alternative to class
inheritance to extend the functionality of reusable objects. For example,
before a window changes size, it asks its delegate whether the new size is ok.
The delegate replies to the window, telling it that the suggested size is
acceptable or suggesting a better size. (For more details on window resizing,
see the`[windowWillResize:toSize:](https://developer.apple.com/library/mac/doc
umentation/Cocoa/Reference/NSWindowDelegate_Protocol/Reference/Reference.html#
//apple_ref/occ/intfm/NSWindowDelegate/windowWillResize:toSize:)`
message.)Delegate methods are typically grouped into a protocol. A protocol is
basically just a list of methods. The delegate protocol specifies all the
messages an object might send to its delegate. If a class conforms to (or
_adopts_) a protocol, it guarantees that it implements the required methods of
a protocol. (Protocols may also include optional methods).In this application,
the application object tells its delegate that the main startup routines have
finished by sending it the`[applicationDidFinishLaunching:](https://developer.
apple.com/library/mac/documentation/Cocoa/Reference/NSApplicationDelegate_Prot
ocol/Reference/Reference.html#//apple_ref/occ/intfm/NSApplicationDelegate/appl
icationDidFinishLaunching:)` message. The delegate is then able to perform
additional tasks if it wants.

**28-How can we achieve singleton pattern in iOS?**

> The Singleton design pattern ensures a class only has one instance, and
provides a global point of access to it. The class keeps track of its sole
instance and ensures that no other instance can be created. Singleton classes
are appropriate for situations where it makes sense for a single object to
provide access to a global resource.Several Cocoa framework classes are
singletons. They include`[NSFileManager](https://developer.apple.com/library/i
os/documentation/Cocoa/Reference/Foundation/Classes/NSFileManager_Class/Refere
nce/Reference.html#//apple_ref/occ/cl/NSFileManager)`, `NSWorkspace`,
`NSApplication`, and, in UIKit,`[UIApplication](https://developer.apple.com/li
brary/ios/documentation/UIKit/Reference/UIApplication_Class/Reference/Referenc
e.html#//apple_ref/occ/cl/UIApplication)`. A process is limited to one
instance of these classes. When a client asks the class for an instance, it
gets a shared instance, which is lazily created upon the first request.

**29-What is delegate pattern in iOS?**

> Delegation is a mechanism by which a host object embeds a weak reference
(weak in the sense that it's a simple pointer reference, unretained) to
another object--its delegate--and periodically sends messages to the delegate
when it requires its input for a task. The host object is generally an "off-
the-shelf" framework object (such as an `NSWindow` or `[NSXMLParser](https://d
eveloper.apple.com/library/ios/documentation/Cocoa/Reference/Foundation/Classe
s/NSXMLParser_Class/Reference/Reference.html#//apple_ref/occ/cl/NSXMLParser)`o
bject) that is seeking to accomplish something, but can only do so in a
generic fashion. The delegate, which is almost always an instance of a custom
class, acts in coordination with the host object, supplying program-specific
behavior at certain points in the task (see Figure 4-3). Thus delegation makes
it possible to modify or extend the behavior of another object without the
need for subclassing.Refer: delegate pattern

**30-What are all the difference between categories and subclasses?Why should we go to subclasses?**

> Category is a feature of the Objective-C language that enables you to add
methods (interface and implementation) to a class without having to make a
subclass. There is no runtime difference--within the scope of your program--
between the original methods of the class and the methods added by the
category. The methods in the category become part of the class type and are
inherited by all the class's subclasses.As with delegation, categories are not
a strict adaptation of the Decorator pattern, fulfilling the intent but taking
a different path to implementing that intent. The behavior added by categories
is a compile-time artifact, and is not something dynamically acquired.
Moreover, categories do not encapsulate an instance of the class being
extended.The Cocoa frameworks define numerous categories, most of them
informal protocols . Often they use categories to group related methods. You
may implement categories in your code to extend classes without subclassing or
to group related methods. However, you should be aware of these caveats:
>
>   * You cannot add instance variables to the class.
>   * If you override existing methods of the class, your application may
behave unpredictably.

**31-What is notification in iOS?**

> The notification mechanism of Cocoa implements one-to-many broadcast of
messages based on the Observer pattern. Objects in a program add themselves or
other objects to a list of observers of one or more notifications, each of
which is identified by a global string (the notification name). The object
that wants to notify other objects--the observed object--creates a
notification object and posts it to a notification center. The notification
center determines the observers of a particular notification and sends the
notification to them via a message. The methods invoked by the notification
message must conform to a certain single-parameter signature. The parameter of
the method is the notification object, which contains the notification name,
the observed object, and a dictionary containing any supplemental
information.Posting a notification is a synchronous procedure. The posting
object doesn't regain control until the notification center has broadcast the
notification to all observers. For asynchronous behavior, you can put the
notification in a notification queue; control returns immediately to the
posting object and the notification center broadcasts the notification when it
reaches the top of the queue.Regular notifications--that is, those broadcast
by the notification center--are intraprocess only. If you want to broadcast
notifications to other processes, you can use the istributed notification
center and its related API.

**32-What is the difference between delegates and notifications?**

> We can use notifications for a variety of reasons. For example, you could
broadcast a notification to change how user-interface elements display
information based on a certain event elsewhere in the program. Or you could
use notifications as a way to ensure that objects in a document save their
state before the document window is closed. The general purpose of
notifications is to inform other objects of program events so they can respond
appropriately.But objects receiving notifications can react only after the
event has occurred. This is a significant difference from delegation. The
delegate is given a chance to reject or modify the operation proposed by the
delegating object. Observing objects, on the other hand, cannot directly
affect an impending operation.

**33-What is posing in iOS?**

> Objective-C permits a class to **entirely replace another class** within an
application. The replacing class is said to "pose as" the target class. All
messages sent to the target class are then instead received by the posing
class. There are some restrictions on which classes can pose:
>
>   * A class may only pose as one of its direct or indirect superclasses
>   * The posing class must not define any new instance variables which are
absent from the target class (though it may define or override methods).
>   * No messages must have been sent to the target class prior to the posing.
>
> Posing, similarly to categories, allows **globally augmenting existing
classes**. Posing permits two features absent from categories:
>
>   * A posing class can call overridden methods through super, thus
incorporating the implementation of the target class.
>   * A posing class can override methods defined in categories.

**34-What is atomic and nonatomic? Which one is safer? Which one is default?**

> You can use this attribute to specify that accessor methods are not atomic.
(There is no keyword to denote atomic.)
>
> **`nonatomic`**
>     Specifies that accessors are nonatomic. _By default, accessors are
atomic._
>
> Properties are atomic by default so that synthesized accessors provide
robust access to properties in a multithreaded environment--that is, the value
returned from the getter or set via the setter is always fully retrieved or
set regardless of what other threads are executing concurrently.
>
> If you specify `strong`, `copy`, or `retain` and do not specify`nonatomic`,
then in a reference-counted environment, a synthesized get accessor for an
object property uses a lock and retains and autoreleases the returned value--
the implementation will be similar to the following:
>  
>  
>     [_internal lock]; // lock using an object-level lock
>  
>  
>     id result = [[value retain] autorelease];
>  
>  
>     [_internal unlock];
>  
>  
>     return result;
>
> If you specify `nonatomic`, a synthesized accessor for an object property
simply returns the value directly.

**35-**Where can you test Apple iPhone apps if you don't have the device?****

> iOS Simulator can be used to test mobile applications. Xcode tool that comes
along with iOS SDK includes Xcode IDE as well as the iOS Simulator. Xcode also
includes all required tools and frameworks for building iOS apps. However, it
is strongly recommended to test the app on the real device before publishing
it.

**36-Which JSON framework is supported by iOS?**

> SBJson framework is supported by iOS. It is a JSON parser and generator for
Objective-C. SBJson provides flexible APIs and additional control that makes
JSON handling easier.

**37-What are the tools required to develop iOS applications?**

> iOS development requires Intel-based Macintosh computer and iOS SDK.

**38- Name the framework that is used to construct application's user interface for iOS.**

> A. The UIKit framework is used to develop application's user interface for
iOS. UIKit framework provides event handling, drawing model, windows, views,
and controls specifically designed for a touch screen interface.

**39-Name the application thread from where UIKit classes should be used?**

> UIKit classes should be used only from an application's main thread. Note:
The derived classes of UIResponder and the classes which manipulate
application's user interface should be used from application's main thread.

**40- Which API is used to write test scripts that help in exercising the application's user interface elements?**

> UI Automation API is used to automate test procedures. Tests scripts are
written in JavaScript to the UI Automation API. This in turn simulates user
interaction with the application and returns log information to the host
computer.

**41-Why an app on iOS device behaves differently when running in foreground than in background?**

> An application behaves differently when running in foreground than in
background because of the limitation of resources on iOS devices.

**42- How can an operating system improve battery life while running an app?**

> An app is notified whenever the operating system moves the apps between
foreground and background. The operating system improves battery life while it
bounds what your app can do in the background. This also improves the user
experience with foreground app.

**43-Which framework delivers event to custom object when app is in foreground?**

> The UIKit infrastructure takes care of delivering events to custom objects.
As an app developer, you have to override methods in the appropriate objects
to process those events.

**44-When an app is said to be in not running state?**

> An app is said to be in 'not running' state when:  
\- it is not launched.  
\- it gets terminated by the system during running.

**45-Assume that your app is running in the foreground but is currently not receiving events. In which sate it would be in?**

> An app will be in InActive state if it is running in the foreground but is
currently not receiving events. An app stays in InActive state only briefly as
it transitions to a different state.

**46- Give example scenarios when an application goes into InActive state?**

> An app can get into InActive state when the user locks the screen or the
system prompts the user to respond to some event e.g. SMS message, incoming
call etc.

**47-When an app is said to be in active state?**

> An app is said to be in active state when it is running in foreground and is
receiving events.

**48-Name the app sate which it reaches briefly on its way to being suspended**

> An app enters background state briefly on its way to being suspended.

**49- Assume that an app is not in foreground but is still executing code. In which state will it be in?**

> Background state.

**50-An app is loaded into memory but is not executing any code. In which state will it be in?**

> An app is said to be in suspended state when it is still in memory but is
not executing any code.

**51-Assume that system is running low on memory. What can system do for suspended apps?**

> In case system is running low on memory, the system may purge suspended apps
without notice.

**52- How can you respond to state transitions on your app?**

> On state transitions can be responded to state changes in an appropriate way
by calling corresponding methods on app's delegate object.
>
> For example: applicationDidBecomeActive method can be used to prepare to run
as the foreground app.  
applicationDidEnterBackground method can be used to execute some code when app
is running in the background and may be suspended at any time.  
applicationWillEnterForeground method can be used to execute some code when
your app is moving out of the background  
applicationWillTerminate method is called when your app is being terminated.

**53-List down app's state transitions when it gets launched.**

> Before the launch of an app, it is said to be in not running state.  
When an app is launched, it moves to the active or background state, after
transitioning briefly through the inactive state.

**54-Who calls the main function of you app during the app launch cycle?**

> During app launching, the system creates a main thread for the app and calls
the app's main function on that main thread. The Xcode project's default main
function hands over control to the UIKit framework, which takes care of
initializing the app before it is run.

**55-What is the use of controller object UIApplication?**

> Controller object UIApplication is used without subclassing to manage the
application event loop.  
It coordinates other high-level app behaviors.  
It works along with the app delegate object which contains app-level logic.

**56-Which object is create by UIApplicationMain function at app launch time?**

> The app delegate object is created by UIApplicationMain function at app
launch time. The app delegate object's main job is to handle state transitions
within the app.

**57- How is the app delegate is declared by Xcode project templates?**

> App delegate is declared as a subclass of UIResponder by Xcode project
templates.

**58-What happens if IApplication object does not handle an event?**

> In such case the event will be dispatched to your app delegate for
processing.

**59- Which app specific objects store the app's content?**

> Data model objects are app specific objects and store app's content. Apps
can also use document objects to manage some or all of their data model
objects.

**60-Are document objects required for an application? What does they offer?**

> Document objects are not required but are very useful in grouping data that
belongs in a single file or file package.

**61- Which object manage the presentation of app's content on the screen?**

> View controller objects takes care of the presentation of app's content on
the screen. A view controller is used to manage a single view along with the
collection of subviews. It makes its views visible by installing them in the
app's window.

**62- Which is the super class of all view controller objects?**

> UIViewController class. The functionality for loading views, presenting
them, rotating them in response to device rotations, and several other
standard system behaviors are provided by UIViewController class.

**63-What is the purpose of UIWindow object?**

> The presentation of one or more views on a screen is coordinated by UIWindow
object.

**64-How do you change the content of your app in order to change the views displayed in the corresponding window?**

> To change the content of your app, you use a view controller to change the
views displayed in the corresponding window. Remember, window itself is never
replaced.

**65-Define view object.**

> Views along with controls are used to provide visual representation of the
app content. View is an object that draws content in a designated rectangular
area and it responds to events within that area.

**66-**Apart from incorporating views and controls, what else an app can incorporate?****

> Apart from incorporating views and controls, an app can also incorporate
Core Animation layers into its view and control hierarchies.

**67- What are layer objects and what do they represent?**

> Layer objects are data objects which represent visual content. Layer objects
are used by views to render their content. Custom layer objects can also be
added to the interface to implement complex animations and other types of
sophisticated visual effects.

####**68-What is App Bundle?**

> When you build your iOS app, Xcode packages it as a bundle. A**bundle** is a
directory in the file system that groups related resources together in one
place. An iOS app bundle contains the app executable file and supporting
resource files such as app icons, image files, and localized content.

**69-Define property?**

> It is used to access instance variables outside of class.

**70-Why synthesized is used?**

> After declaring property we will have to tell compiler instantly by using
synthesize directive. This tells the compiler to generate setter and getter
methods.

**71-What is retaining?**

> It is reference count for an object.

**72- What is webservice?**

> To get data in form of xml ,by using this we can get data from a server.

**73-What is parsing?**

> To get data from web service we use parsing.

**74-which xml parser we use on iphone?**

> "NSXML" Parser.

**75-Which type of parse does iphone support?**

> "SAX" parser.

**76-.Name those classes used to establish connection b/w application to webserver?**

> (a)NSURL (b)NSURL REQUEST (c)NSURL CONNECTION.

**77-Tell the difference between DOM and SAX Parser?**

> (a)Dom is "documents based parser".  
b)SAX is a event driven parser

**78-Name three method of NSXML parser.**

> (1)did start element (2)did end element (3)found character.

**79-Tell methods used in NSURLConnection**

> (1)Connection did receive Response  
(2)Connection did recevice Datat  
(3)Connection fail with error  
(4)Connection did finish loading.

**80-.What is json-parser?**

> JSON(Java script object notation)is a parser used to get data from web
Server.

**81-.By default which things are in the application?**

> iPhone applications by default have 3 things  
1.main: entry point of application.  
2.Appdelegate: perform basic application and functionality.  
3.Window: provide uiinterface.

**82-Tell me about tab bar controller?**

> It is used to display the data on the view.

**83-Which are the protocols used in table view?**

> Table view contain two delegate protocols  
(1) Uitable view data source  
(2).Uitable view delegate.  
ui view table view data source three method namely  
(1)No of sections.  
(2)No of rows in sections.  
(3)Cell for row index path row.  
In ui table view delegate contain  
(1)Did select row at index path row

**84-Name data base used in iphone?**

> (1)Sql lite (2)Plist 3)Xml (4)Core Data

**85-Tell four frameworks used in iphone?**

> (1)Ui kit framework  
(2)Map kit framework  
(3)ADI kit framework  
(4)Core data framework  
(5)core foundation framework

**86-Tell me about single inheritance in objective-c?**

> Objective c subclass can derived from a single parent class.It is called
"single inheritance".

**87-Tell me about the MVC architecture?**

> M-model, V-view, C-controller
>
> Main advantage of MVC architecture is to provide "reusability and security"
by separating the layer by using MVC architecture.
>
> **Model:** it is a class model is interact with database.
>
> **Controller:** controller is used for by getting the data from model and
controls the views.
>
> Display the information in views. : View

**88-What is the instance methods?**

> Instance methods are essentially code routines that perform tasks so
instances of clases we create methods to get and set the instance variables
and to display the current values of these variables.
>
> Declaration of instance method :
>
> - (void)click me: (id)sender;
>
> Void is return type which does not giving any thing here.
>
> Click me is method name.
>
> Id is data type which returns any type of object.

**89-What is the class method?**

> Class methods work at the class level and are common to all instance of a
class these methods are specific to the class overall as opposed to working on
different instance data encapsulated in each class instance.
>
> @interface class name :ns object
>
> +(class name *)new alloc:
>
> -(int)total open

**90-What is data encapsulation?**

> Data is contained within objects and is not accessible by any other than via
methods defined on the class is called data encapsulation.

**91-What is accessor methods?**

> Accessor methods are methods belonging to a class that allow to get and set
the values of instance valuables contained within the class.

**92-What is synthesized accessor methods?**

> Objective-c provides a mechanism that automates the creation of accessor
methods that are called synthesized accessor methods that are implemented
through use of the @property and @synthesized.

**93-How to access the encapsulated data in objective-c?**

> (a)Data encapsulation encourages the use of methods to +get and set the
values of instance variables in a class.
>
> (b)But the developer to want to directly access an instance variable without
having to go through an accessor method.
>
> (c) In objective-c syntax for an instance variable is as follow [class
instance variable name]

**94-What is dot notation?**

> Dot notation features introduced into version 2.0 of objective-c. Dot
notation involves accessing an instance variable by specifying a class
"instance" followed by a "dot" followed in turn by the name of instance
variable or property to be accessed.

**95-Difference between shallow copy and deep copy?**

> Shallow copy is also known as address copy. In this process you only copy
address not actual data while in deep copy you copy data.
>
> Suppose there are two objects A and B. A is pointing to a different array
while B is pointing to different array. Now what I will do is following to do
shallow copy. Char *A = {'a','b','c'}; Char *B = {'x','y','z'}; B = A; Now B
is pointing is at same location where A pointer is pointing.Both A and B in
this case sharing same data. if change is made both will get altered value of
data.Advantage is that coping process is very fast and is independent of size
of array.
>
> while in deep copy data is also copied. This process is slow but Both A and
B have their own copies and changes made to any copy, other will copy will not
be affected.

**96-Difference between categories and extensions?**

> Class extensions are similar to categories. The main difference is that with
an extension, the compiler will expect you to implement the methods within
your main @implementation, whereas with a category you have a separate
@implementation block. So you should pretty much only use an extension at the
top of your main .m file (the only place you should care about ivars,
incidentally) -- it's meant to be just that, an extension.

**97-What are KVO and KVC?**

> **KVC:**Normally instance variables are accessed through properties or
accessors but KVC gives another way to access variables in form of strings. In
this way your class acts like a dictionary and your property name for example
"age" becomes key and value that property holds becomes value for that key.
For example, you have employee class with name property.
>
> You access property like
>
> NSString age = emp.age;
>
> setting property value.
>
> emp.age = @"20″;
>
> Now how KVC works is like this
>
> [emp valueForKey:@"age"];
>
> [emp setValue:@"25" forKey:@"age"];
>
> **KVO :**The mechanism through which objects are notified when there is
change in any of property is called KVO.
>
> For example, person object is interested in getting notification when
accountBalance property is changed in BankAccount object.To achieve this,
Person Object must register as an observer of the BankAccount's accountBalance
property by sending an addObserver:forKeyPath:options:context: message.

**98-Can we use two tableview controllers on one view controller?**

> Yes, we can use two tableviews on the same view controllers and you can
differentiate between two by assigning them tags…or you can also check them by
comparing their memory addresses.

**99-Swap the two variable values without taking third variable?**

> int x=10; int y=5; x=x+y; NSLog(@"x==> %d",x);
>
> y=x-y; NSLog(@"Y Value==> %d",y);
>
> x=x-y; NSLog(@"x Value==> %d",x);

**100-**What is push notification?****

> Imagine, you are looking for a job. You go to software company daily and ask
sir "is there any job for me" and they keep on saying no. Your time and money
is wasted on each trip.(Pull Request mechanism)
>
> So, one day owner says, if there is any suitable job for you, I will let you
know. In this mechanism, your time and money is not wasted. (Push Mechanism)

**How it works?**

> This service is provided by Apple in which rather than pinging server after
specific interval for data which is also called pull mechanism, server will
send notification to your device that there is new piece of information for
you. Request is initiated by server not the device or client.

**Flow of push notification**

> Your web server sends message (device token + payload) to Apple push
notification service (APNS) , then APNS routes this message to device whose
device token specified in notification.

**101-What is polymorphism?**

> This is very famous question and every interviewer asks this. Few people say
polymorphism means multiple forms and they start giving example of draw
function which is right to some extent but interviewer is looking for more
detailed answer.
>
> Ability of base class pointer to call function from derived class at runtime
is called polymorphism.
>
> For example, there is super class human and there are two subclasses
software engineer and hardware engineer. Now super class human can hold
reference to any of subclass because software engineer is kind of human.
Suppose there is speak function in super class and every subclass has also
speak function. So at runtime, super class reference is pointing to whatever
subclass, speak function will be called of that class. I hope I am able to
make you understand.

**101-What is responder chain?**

> Suppose you have a hierarchy of views such like there is superview A which
have subview B and B has a subview C. Now you touch on inner most view C. The
system will send touch event to subview C for handling this event. If C View
does not want to handle this event, this event will be passed to its superview
B (next responder). If B also does not want to handle this touch event it will
pass on to superview A. All the view which can respond to touch events are
called responder chain. A view can also pass its events to uiviewcontroller.
If view controller also does not want to respond to touch event, it is passed
to application object which discards this event.

**102-Can we use one tableview with two different datasources? How you will achieve this?**

> Yes. We can conditionally bind tableviews with two different data sources.

**103-What is a protocol?**

> A protocol is a language feature in objective C which provides multiple
inheritance in a single inheritance language. Objective C supports two types
of protocols:
>
>   * Ad hoc protocols called informal protocol
>   * Compiler protocols called formal protocols
>
> You must create your own autorelease pool as soon as the thread begins
executing; otherwise, your application will leak objects

**104-Three occasions when you might use your own autorelease pools:**

>   1. If you are writing a program that is not based on a UI framework, such
as a command-line tool.
>   2. If you write a loop that creates many temporary objects.You may create
an autorelease pool inside the loop to dispose of those objects before the
next iteration. Using an autorelease pool in the loop helps to reduce the
maximum memory footprint of the application.
>   3. If you spawn a secondary thread.

**105- InApp purchase product type**

>   1. **Consumable** products must be purchased each time the user needs that
item. For example, one-time services are commonly implemented as consumable
products.
>   2. **Non-consumable** products are purchased only once by a particular
user. Once a non-consumable product is purchased, it is provided to all
devices associated with that user's iTunes account. Store Kit provides built-
in support to restore non-consumable products on multiple devices.
>   3. **Auto-renewable subscriptions **are delivered to all of a user's
devices in the same way as non-consumable products. However, auto-renewable
subscriptions differ in other ways. When you create an auto-renewable
subscription in iTunes Connect, you choose the duration of the subscription.
The App Store automatically renews the subscription each time its term
expires. If the user chooses to not allow the subscription to be renewed, the
user's access to the subscription is revoked after the subscription expires.
Your application is responsible for validating whether a subscription is
currently active and can also receive an updated receipt for the most recent
transaction.
>   4. **Free subscriptions** are a way for you to put free subscription
content in Newsstand. Once a user signs up for a free subscription, the
content is available on all devices associated with the user's Apple ID. Free
subscriptions do not expire and can only be offered in Newsstand-enabled apps

**106-the advantages and disadvantages about synchronous versus asynchronous connections.**

> That's it, pretty fast and easy, but there are a lot of caveats :
>
> • The most important problem is that the thread which called this method
will be blocked until the connection finish or timeout, so we surely don't
want to start the connection on the main thread to avoid freezing the UI. That
means we need to create a new thread to handle the connection, and all
programmers know that threading is hard.
>
> • Cancellation, it's not possible to cancel a synchronous connection, which
is bad because users like to have the choice to cancel an operation if they
think it takes too much time to execute.
>
> • Authentication, there is no way to deal with authentication challenges.
>
> • It's impossible to parse data on the fly.
>
> So let's put it up straight, avoid using synchronous_NSURLConnection_, there
is absolutely no benefit of using it.
>
> It's clear that **asynchronous connections** give us more control :
>
> • You don't have to create a new thread for the connection because your main
thread will not be blocked.
>
> • You can easily cancel the connection just by calling the _cancel_method.
>
> • If you need authentication just implement the required delegate methods.
>
> • Parsing data on the fly is easy.
>
> So clearly we have a lot of more control with this, and the code is really
not difficult.
>
> Even better, we don't have to handle the creation of a new thread, which is
a good thing, because you know, threading is hard.
>
> Well, if you read me until here, you should be convinced to use asynchronous
connections, and forget about synchronous ones. They clearly give us more
control and possibilities and, in some case can spare us to create new thread.
>
> So I encourage you to move away from synchronous connections, just think of
them as evil.

**107-What is the navigation controller?**

> Navigation controller contains the stack of controllers every navigation
controller  
must be having root view controller by default these controllers contain 2
method  
(a) push view (b) pop view  
By default navigation controller contain "table view".

**108- What is the split view controller?**

> This control is used for ipad application and it contain proper controllers
by default  
split view controller contain root view controller and detail view controller.

**109-Cocoa.**

> Cocoa is an application environment for both the Mac OS X operating system
and iOS. It consists of a suite of object-oriented software libraries, a
runtime system, and an integrated development environment. Carbon is an
alternative environment in Mac OS X, but it is a compatibility framework with
procedural programmatic interfaces intended to support existing Mac OS X code
bases.

**110- Frameworks that make Cocoa.**

> Appkit (Application Kit)
>
> Foundation

**111- Objective-C.**

> Objective-C is a very dynamic language. Its dynamism frees a program from
compile-time and link-time constraints and shifts much of the responsibility
for symbol resolution to runtime, when the user is in control. Objective-C is
more dynamic than other programming languages because its dynamism springs
from three sources:
>
> Dynamic typing--determining the class of an object at runtime
>
> Dynamic binding--determining the method to invoke at runtime
>
> Dynamic loading--adding new modules to a program at runtime

**112- Objective-C vs C/C++.**

> * The Objective-C class allows a method and a variable with the exact same
name. In C++, they must be different.
>
> * Objective-C does not have a constructor or destructor. Instead it has init
and dealloc methods, which must be called explicitly.
>
> * Objective-C uses + and - to differentiate between factory and instance
methods, C++ uses static to specify a factory method.
>
> * Multiple inheritance is not allowed in Obj-C, however we can use protocol
to some extent.
>
> * Obj-C has runtime binding leading to dynamic linking.
>
> * Obj-C has got categories.
>
> * Objective-C has a work-around for method overloading, but none for
operator overloading.
>
> * Objective-C also does not allow stack based objects. Each object must be a
pointer to a block of memory.
>
> * In Objective-C the message overloading is faked by naming the parameters.
C++ actually does the same thing but the compiler does the name mangling for
us. In Objective-C, we have to mangle the names manually.
>
> * One of C++'s advantages and disadvantages is automatic type coercion.
>
> * Another feature C++ has that is missing in Objective-C is references.
Because pointers can be used wherever a reference is used, there isn't much
need for references in general.
>
> * Templates are another feature that C++ has that Objective-C doesn't.
Templates are needed because C++ has strong typing and static binding that
prevent generic classes, such as List and Array.

**113-Appilcation Kit/App kit.**

> The Application Kit is a framework containing all the objects you need to
implement your graphical, event-driven user interface: windows, panels,
buttons, menus, scrollers, and text fields. The Application Kit handles all
the details for you as it efficiently draws on the screen, communicates with
hardware devices and screen buffers, clears areas of the screen before
drawing, and clips views.
>
> You also have the choice at which level you use the Application Kit:
>
> * Use Interface Builder to create connections from user interface objects to
your application objects.
>
> * Control the user interface programmatically, which requires more
familiarity with AppKit classes and protocols.
>
> * Implement your own objects by subclassing NSView or other classes.

**114-Foundation Kit.**

> The Foundation framework defines a base layer of Objective-C classes. In
addition to providing a set of useful primitive object classes, it introduces
several paradigms that define functionality not covered by the Objective-C
language. The Foundation framework is designed with these goals in mind:
>
> * Provide a small set of basic utility classes.
>
> * Make software development easier by introducing consistent conventions for
things such as deallocation.
>
> * Support Unicode strings, object persistence, and object distribution.
>
> * Provide a level of OS independence, to enhance portability.

**115-Dynamic and Static Typing.**

> Static typed languages are those in which type checking is done at compile-
time, whereas dynamic typed languages are those in which type checking is done
at run-time.
>
> Objective-C is a dynamically-typed language, meaning that you don't have to
tell the compiler what type of object you're working with at compile time.
Declaring a type for a varible is merely a promise which can be broken at
runtime if the code leaves room for such a thing. You can declare your
variables as type id, which is suitable for any Objective-C object.

**116-Selectors**

> In Objective-C, selector has two meanings. It can be used to refer simply to
the name of a method when it's used in a source-code message to an object. It
also, though, refers to the unique identifier that replaces the name when the
source code is compiled. Compiled selectors are of type SEL. All methods with
the same name have the same selector. You can use a selector to invoke a
method on an object--this provides the basis for the implementation of the
target-action design pattern in Cocoa.
>
> [friend performSelector:@selector(gossipAbout:) withObject:aNeighbor];
>
> is equivalent to:
>
> [friend gossipAbout:aNeighbor];

**117-Class Introspection**

> * Determine whether an objective-C object is an instance of a class
>
> [obj isMemberOfClass:someClass];
>
> * Determine whether an objective-C object is an instance of a class or its
descendants
>
> [obj isKindOfClass:someClass];
>
> * The version of a class
>
> [MyString version]
>
> * Find the class of an Objective-C object
>
> Class c = [obj1 class]; Class c = [NSString class];
>
> * Verify 2 Objective-C objects are of the same class
>
> [obj1 class] == [obj2 class]

**118- Proxy**

> As long as there aren't any extra instance variables, any subclass can proxy
itself as its superclass with a single call. Each class that inherits from the
superclass, no matter where it comes from, will now inherit from the proxied
subclass. Calling a method in the superclass will actually call the method in
the subclass. For libraries where many objects inherit from a base class,
proxying the superclass can be all that is needed.

**119- Why category is better than inheritance?**

> If category is used, you can use same class, no need to remember a new
class-name. Category created on a base class is available on sub classes.

**120-Formal Protocols**

> Formal Protocols allow us to define the interface for a set of methods, but
implementation is not done. Formal Protocols are useful when you are using
DistributedObjects, because they allow you to define a protocol for
communication between objects, so that the DO system doesn't have to
constantly check whether or not a certain method is implemented by the distant
object.

**121- Formal vs informal protocol.**

> In addition to formal protocols, you can also define an informal protocol by
grouping the methods in a category declaration:
>
> @interface NSObject (MyProtocol)
>
> //someMethod();
>
> Informal protocols are typically declared as categories of the NSObject
class, because that broadly associates the method names with any class that
inherits from NSObject. Because all classes inherit from the root class, the
methods aren't restricted to any part of the inheritance hierarchy. (It is
also possible to declare an informal protocol as a category of another class
to limit it to a certain branch of the inheritance hierarchy, but there is
little reason to do so.)
>
> When used to declare a protocol, a category interface doesn't have a
corresponding implementation. Instead, classes that implement the protocol
declare the methods again in their own interface files and define them along
with other methods in their implementation files.
>
> An informal protocol bends the rules of category declarations to list a
group of methods but not associate them with any particular class or
implementation.
>
> Being informal, protocols declared in categories don't receive much language
support. There's no type checking at compile time nor a check at runtime to
see whether an object conforms to the protocol. To get these benefits, you
must use a formal protocol. An informal protocol may be useful when all the
methods are optional, such as for a delegate, but (in Mac OS X v10.5 and
later) it is typically better to use a formal protocol with optional methods.

**122- Optional vs required**

> Protocol methods can be marked as optional using the @optional keyword.
Corresponding to the @optional modal keyword, there is a @required keyword to
formally denote the semantics of the default behavior. You can use @optional
and @required to partition your protocol into sections as you see fit. If you
do not specify any keyword, the default is @required.
>
> @protocol MyProtocol
>
> @optional
>
> -(void) optionalMethod;
>
> @required
>
> -(void) requiredMethod;

**123- Memory Management**

> If you alloc, retain, or copy/mutablecopy it, it's your job to release it.
Otherwise it isn't.

**124-Copy vs assign vs retain**

> * Assign is for primitive values like BOOL, NSInteger or double. For objects
use retain or copy, depending on if you want to keep a reference to the
original object or make a copy of it.
>
> * **assign**: In your setter method for the property, there is a simple
assignment of your instance variable to the new value, eg:
>
> (void)setString:(NSString*)newString{
>
> string = newString;
>
> This can cause problems since Objective-C objects use reference counting,
and therefore by not retaining the object, there is a chance that the string
could be deallocated whilst you are still using it.
>
> * **retain**: this _retains_ the new value in your setter method. For
example:
>
> This is safer, since you explicitly state that you want to maintain a
reference of the object, and you must release it before it will be
deallocated.
>
> (void)setString:(NSString*)newString{
>
> [newString retain];
>
> [string release];
>
> string = newString;
>
> * **copy**: this makes a copy of the string in your setter method:
>
> This is often used with strings, since making a copy of the original object
ensures that it is not changed whilst you are using it.
>
> (void)setString:(NSString*)newString{
>
> if(string!=newString){
>
> [string release];
>
> string = [newString copy];

**125- alloc vs new**

> "alloc" creates a new memory location but doesn't initializes it as compared
to "new".

**126- release vs pool drain**

> "release" frees a memory. "drain" releases the NSAutoreleasePool itself.

**127- NSAutoReleasePool : release vs drain**

> Strictly speaking, from the big picture perspective drain is not equivalent
to release:
>
> In a reference-counted environment, drain does perform the same operations
as release, so the two are in that sense equivalent. To emphasise, this means
you do not leak a pool if you use drain rather than release.
>
> In a garbage-collected environment, release is a no-op. Thus it has no
effect. drain, on the other hand, contains a hint to the collector that it
should "collect if needed". Thus in a garbage-collected environment, using
drain helps the system balance collection sweeps.

**128-autorelease vs release**

> Autorelase: By sending an object an autorelease message, it is added to the
local AutoReleasePool, and you no longer have to worry about it, because when
the AutoReleasePool is destroyed (as happens in the course of event processing
by the system) the object will receive a release message, its RetainCount will
be decremented, and the GarbageCollection system will destroy the object if
the RetainCount is zero.
>
> Release: retain count is decremented at this point.

**129- Autorelease Pool**

> Autorelease pools provide a mechanism whereby you can send an object a
"deferred" release message. This is useful in situations where you want to
relinquish ownership of an object, but want to avoid the possibility of it
being deallocated immediately (such as when you return an object from a
method). Typically, you don't need to create your own autorelease pools, but
there are some situations in which either you must or it is beneficial to do
so.

**130- How autorelease pool is managed.**

> Every time -autorelease is sent to an object, it is added to the inner-most
autorelease pool. When the pool is drained, it simply sends -release to all
the objects in the pool.

>

> Autorelease pools are simply a convenience that allows you to defer sending
-release until "later". That "later" can happen in several places, but the
most common in Cocoa GUI apps is at the end of the current run loop cycle.

**131-Memory Leak**

> If RetainingAndReleasing are not properly used then RetainCount for AnObject
doesn't reach 0. It doesn't crash the application.

**132- Event Loop**

> In a Cocoa application, user activities result in events. These might be
mouse clicks or drags, typing on the keyboard, choosing a menu item, and so
on. Other events can be generated automatically, for example a timer firing
periodically, or something coming in over the network. For each event, Cocoa
expects there to be an object or group of objects ready to handle that event
appropriately. The event loop is where such events are detected and routed off
to the appropriate place. Whenever Cocoa is not doing anything else, it is
sitting in the event loop waiting for an event to arrive. (In fact, Cocoa
doesn't poll for events as suggested, but instead its main thread goes to
sleep. When an event arrives, the OS wakes up the thread and event processing
resumes. This is much more efficient than polling and allows other
applications to run more smoothly).
>
> Each event is handled as an individual thing, then the event loop gets the
next event, and so on. If an event causes an update to be required, this is
checked at the end of the event and if needed, and window refreshes are
carried out.

**133-Differnce between boxName and self.boxName.**

> boxName: Accessing directly.
>
> self. boxName: Accessing boxName through accessors. If property/synthesize
is not there it will throw error.

**134-What it does "@synthesize boxDescription=boxName;" ?**

> Here you can use boxName or self.boxName. We cant use boxDescription.

**135-Collection**

> In Cocoa and Cocoa Touch, a collection is a Foundation framework class used
for storing and managing groups of objects. Its primary role is to store
objects in the form of either an array, a dictionary, or a set.

**136-Threads and how to use**

> Use this class when you want to have an Objective-C method run in its own
thread of execution. Threads are especially useful when you need to perform a
lengthy task, but don't want it to block the execution of the rest of the
application. In particular, you can use threads to avoid blocking the main
thread of the application, which handles user interface and event-related
actions. Threads can also be used to divide a large job into several smaller
jobs, which can lead to performance increases on multi-core computers.
>
> Two ways to create threads…
>
> * detachNewThreadSelector:toTarget:withObject:
>
> * Create instances of NSThread and start them at a later time using the
"start" method.
>
> NSThread is not as capable as Java's Thread class, it lacks
>
> * Built-in communication system.
>
> * An equivalent of "join()"

**137-Threadsafe**

> When it comes to threaded applications, nothing causes more fear or
confusion than the issue of handling signals. Signals are a low-level BSD
mechanism that can be used to deliver information to a process or manipulate
it in some way. Some programs use signals to detect certain events, such as
the death of a child process. The system uses signals to terminate runaway
processes and communicate other types of information.
>
> The problem with signals is not what they do, but their behavior when your
application has multiple threads. In a single-threaded application, all signal
handlers run on the main thread. In a multithreaded application, signals that
are not tied to a specific hardware error (such as an illegal instruction) are
delivered to whichever thread happens to be running at the time. If multiple
threads are running simultaneously, the signal is delivered to whichever one
the system happens to pick. In other words, signals can be delivered to any
thread of your application.
>
> The first rule for implementing signal handlers in applications is to avoid
assumptions about which thread is handling the signal. If a specific thread
wants to handle a given signal, you need to work out some way of notifying
that thread when the signal arrives. You cannot just assume that installation
of a signal handler from that thread will result in the signal being delivered
to the same thread.

**138-Notification and Observers**

> A notification is a message sent to one or more observing objects to inform
them of an event in a program. The notification mechanism of Cocoa follows a
**broadcast** model. It is a way for an object that initiates or handles a
program event to communicate with any number of objects that want to know
about that event. These recipients of the notification, known as observers,
can adjust their own appearance, behavior, and state in response to the event.
The object sending (or posting) the notification doesn't have to know what
those observers are. Notification is thus a powerful mechanism for attaining
coordination and cohesion in a program. It reduces the need for strong
dependencies between objects in a program (such dependencies would reduce the
reusability of those objects). Many classes of the Foundation, AppKit, and
other Objective-C frameworks define notifications that your program can
register to observe.
>
> The centerpiece of the notification mechanism is a per-process singleton
object known as the notification center (**NSNotificationCenter**). When an
object posts a notification, it goes to the notification center, which acts as
a kind of clearing house and broadcast center for notifications. Objects that
need to know about an event elsewhere in the application register with the
notification center to let it know they want to be notified when that event
happens. Although the notification center delivers a notification to its
observers synchronously, you can post notifications asynchronously using a
notification queue (NSNotificationQueue).

**139-Delegate vs Notification**

> * The concept of notification differs from delegation in that it allows a
message to be sent to more than one object. It is more like a broadcast rather
than a straight communication between two objects. It removes dependencies
between the sending and receiving object(s) by using a notification center to
manage the sending and receiving of notifications. The sender does not need to
know if there are any receivers registered with the notification center. There
can be one, many or even no receivers of the notification registered with the
notification center. Simply, Delegate is 1-to-1 object and Notification can be
*-to-* objects.
>
> * The other difference between notifications and delegates is that there is
no possibility for the receiver of a notification to return a value to the
sender.
>
> * Typical uses of notifications might be to allow different objects with an
application to be informed of an event such as a file download completing or a
user changing an application preference. The receiver of the notification
might then perform additional actions such as processing the downloaded file
or updating the display.

**140-Plist**

> Property lists organize data into named values and lists of values using
several object types. These types give you the means to produce data that is
meaningfully structured, transportable, storable, and accessible, but still as
efficient as possible. Property lists are frequently used by applications
running on both Mac OS X and iOS. The property-list programming interfaces for
Cocoa and Core Foundation allow you to convert hierarchically structured
combinations of these basic types of objects to and from standard XML. You can
save the XML data to disk and later use it to reconstruct the original
objects.
>
> The user defaults system, which you programmatically access through the
NSUserDefaults class, uses property lists to store objects representing user
preferences. This limitation would seem to exclude many kinds of objects, such
as NSColor and NSFont objects, from the user default system. But if objects
conform to the NSCoding protocol they can be archived to NSData objects, which
are property list-compatible objects

**141-Helper Objects**

> Helper Objects are used throughout Cocoa and CocoaTouch, and usually take
the form of a delegate or dataSource. They are commonly used to add
functionality to an existing class without having to subclass it.

**142-Cluster Class**

> Class clusters are a design pattern that the Foundation framework makes
extensive use of. Class clusters group a number of private concrete subclasses
under a public abstract superclass. The grouping of classes in this way
simplifies the publicly visible architecture of an object-oriented framework
without reducing its functional richness.

**143-Differentiate Foundation vs Core Foundation**

> CoreFoundation is a general-purpose C framework whereas Foundation is a
general-purpose Objective-C framework. Both provide collection classes, run
loops, etc, and many of the Foundation classes are wrappers around the CF
equivalents. CF is mostly open-source , and Foundation is closed-source.
>
> **Core Foundation** is the C-level API, which provides CFString,
CFDictionary and the like.**Foundation** is Objective-C, which provides
NSString, NSDictionary, etc. CoreFoundation is written in C while Foundation
is written in Objective-C. Foundation has _a lot_ more classes CoreFoundation
is the common base of Foundation and Carbon.

**144-Difference between coreData and Database**

> **Database**
> **Core Data**
> Primary function is storing and fetching data
> Primary function is graph management (although reading and writing to disk
is an important supporting feature)
> Operates on data stored on disk (or minimally and incrementally loaded)
> Operates on objects stored in memory (although they can be lazily loaded
from disk)
> Stores "dumb" data
> Works with fully-fledged objects that self-manage a lot of their behavior
and can be subclassed and customized for further behaviors
> Can be transactional, thread-safe, multi-user
> Non-transactional, single threaded, single user (unless you create an entire
abstraction around Core Data which provides these things)
> Can drop tables and edit data without loading into memory
> Only operates in memory
> Perpetually saved to disk (and often crash resilient)
> Requires a save process
> Can be slow to create millions of new rows
> Can create millions of new objects in-memory very quickly (although saving
these objects will be slow)
> Offers data constraints like "unique" keys
> Leaves data constraints to the business logic side of the program

**145- Core data vs sqlite.**

> Core data is an object graph management framework. It manages a potentially
very large graph of object instances, allowing an app to work with a graph
that would not entirely fit into memory by faulting objects in and out of
memory as necessary. Core Data also manages constraints on properties and
relationships and maintains reference integrity (e.g. keeping forward and
backwards links consistent when objects are added/removed to/from a
relationship). Core Data is thus an ideal framework for building the "model"
component of an MVC architecture.
>
> To implement its graph management, Core Data _happens_ to use sqlite as a
disk store. It_could_ have been implemented using a different relational
database or even a non-relational database such as CouchDB. As others have
pointed out, Core Data can also use XML or a binary format or a user-written
atomic format as a backend (though these options require that the entire
object graph fit into memory).

**146-Retain cycle or Retain loop.**

> When object A retains object B, and object B retains A. Then Retain cycle
happens. To overcome this use "close" method.
>
> Objective-C's garbage collector (when enabled) can also delete retain-loop
groups but this is not relevant on the iPhone, where Objective-C garbage
collection is not supported.

**147-What is unnamed category.**

> A named category -- **@interface Foo(FooCategory)** -- is generally used to:
>
> i. Extend an existing class by adding functionality.
>
> ii. Declare a set of methods that might or might not be implemented by a
delegate.
>
> Unnamed Categories has fallen out of favor now that @protocol has been
extended to support @optional methods.
>
> A class extension -- **@interface Foo()** -- is designed to allow you to
declare additional private API -- SPI or System Programming Interface -- that
is used to implement the class innards. This typically appears at the top of
the .m file. Any methods / properties declared in the class extension must be
implemented in the @implementation, just like the methods/properties found in
the public @interface.
>
> Class extensions can also be used to redeclare a publicly readonly @property
as readwrite prior to @synthesize'ing the accessors.
>
> Example:
>
> **Foo.h**
>
> @interface Foo:NSObject
>
> @property(readonly, copy) NSString *bar;
>
> -(void) publicSaucing;
>
> **Foo.m**
>
> @interface Foo()
>
> @property(readwrite, copy) NSString *bar;
>
> - (void) superSecretInternalSaucing;
>
> @implementation Foo
>
> @synthesize bar;
>
> …. must implement the two methods or compiler will warn ….

**148-Copy vs mutableCopy.**

> copy always creates an immutable copy.
>
> mutableCopy always creates a mutable copy.

**149- Strong vs Weak**

> The strong and weak are new ARC types replacing retain and assign
respectively.
>
> Delegates and outlets should be weak.
>
> A **strong reference** is a reference to an object that stops it from being
deallocated. In other words it creates a owner relationship.
>
> A **weak reference** is a reference to an object that does not stop it from
being deallocated. In other words, it does not create an owner relationship.

**150-__strong, __weak, __unsafe_unretained, __autoreleasing.**

> Generally speaking, these extra qualifiers don't need to be used very often.
You might first encounter these qualifiers and others when using the migration
tool. For new projects however, you generally you won't need them and will
mostly use strong/weak with your declared properties.
>
> **__strong** - is the default so you don't need to type it. This means any
object created using alloc/init is retained for the lifetime of its current
scope. The "current scope" usually means the braces in which the variable is
declared
>
> **__weak** - means the object can be destroyed at anytime. This is only
useful if the object is somehow strongly referenced somewhere else. When
destroyed, a variable with __weak is set to nil.
>
> **__unsafe_unretained** - is just like __weak but the pointer is not set to
nil when the object is deallocated. Instead the pointer is left dangling.
>
> **__autoreleasing**, not to be confused with calling autorelease on an
object before returning it from a method, this is used for passing objects by
reference, for example when passing NSError objects by reference such as
[myObject performOperationWithError:&tmp];

**151-Types of NSTableView**

> Cell based and View based. In view based we can put multiple objects.

**152-Abstract class in cocoa.**

> Cocoa doesn't provide anything called abstract. We can create a class
abstract which gets check only at runtime, compile time this is not checked.
>
> @interface AbstractClass : NSObject
>
> @implementation AbstractClass
>
> \+ (id)alloc{
>
> if (self == [AbstractClass class]) {
>
> NSLog(@"Abstract Class cant be used");
>
> return [super alloc];

**153- Difference between HTTP and HTTPS.**

> * HTTP stands for
[HyperText](http://www.blogger.com/blogger.g?blogID=2378569646178591916)
Transfer
[Protocol](http://www.blogger.com/blogger.g?blogID=2378569646178591916),
whereas, HTTPS is HyperText Transfer Protocol
[Secure](http://www.blogger.com/blogger.g?blogID=2378569646178591916).
>
> * HTTP transmits everything as plan text, while HTTPS provides encrypted
communication, so that only the recipient can decrypt and read the
information. Basically, HTTPS is a combination of HTTP
and[SSL](http://www.blogger.com/blogger.g?blogID=2378569646178591916) (Secure
Sockets Layer). This SSL is that protocol which encrypts the data.
>
> * HTTP is fast and cheap, where HTTPS is slow and expensive.
>
> As, HTTPS is safe it's widely used during payment transactions or any
sensitive transactions over the internet. On the other hand, HTTP is used most
of the sites over the net, even this blogspot sites also use HTTP.
>
> * HTTP URLs starts with "http:// " and use
[port](http://www.blogger.com/blogger.g?blogID=2378569646178591916) 80 by
default, while HTTPS URLs stars with "https:// " and use port 443.
>
> * HTTP is unsafe from attacks like [man-in-the-
middle](http://en.support.wordpress.com/affiliate-links/) and eavesdropping,
but HTTPS is secure from these sorts of attacks.

**154-GCD**

> Grand Central Dispatch is not just a new abstraction around what we've
already been using, it's an entire new underlying mechanism that makes
multithreading easier and makes it easy to be as concurrent as your code can
be without worrying about the variables like how much work your CPU cores are
doing, how many CPU cores you have and how much threads you should spawn in
response. You just use the Grand Central Dispatch API's and it handles the
work of doing the appropriate amount of work. This is also not just in Cocoa,
anything running on Mac OS X 10.6 Snow Leopard can take advantage of Grand
Central Dispatch ( libdispatch ) because it's included in libSystem.dylib and
all you need to do is include #import <dispatch/dispatch.h> in your app and
you'll be able to take advantage of Grand Central Dispatch.

**155-How you attain the backward compatibility?**

  1. > Set the Base SDK to Current version of Mac (ex. 10.7)

  2. > Set the Deployment SDK to older version (ex.1.4)

**156-Call Back.**

> Synchronous operations are ones that happen in step with your calling code.
Most of Cocoa works this way: you send a message to an object, say to format a
string, etc, and by the time that line of code is "done", the operation is
complete.
>
> But in the real world, some operations take longer than "instantaneous"
(some intensive graphics work, but mainly high or variably latency things like
disk I/O or worse, network connectivity). These operations are unpredictable,
and if the code were to block until finish, it might block indefinitely or
forever, and that's no good.
>
> So the way we handle this is to set up "callbacks"- you say "go off and do
this operation, and when you're done, call this other function". Then inside
that "callback" function, you start the second operation that depends on the
first. In this way, you're not spinning in circles waiting, you just get
called "asynchronously" when each task is done.

