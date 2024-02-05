<!--BEGIN_DATA
{
    "create_date": "2017-04-06 10:54", 
    "modify_date": "2017-04-06 10:54", 
    "is_top": "0", 
    "summary": "Stack and Heap Objects in Objective-C", 
    "tags": "iOS", 
    "file_name": "Stack and Heap Objects in Objective-C.md"
}
END_DATA-->

#### <p>原文出处：<a href='https://mikeash.com/pyblog/friday-qa-2010-01-15-stack-and-heap-objects-in-objective-c.html' target='blank'>Stack and Heap Objects in Objective-C</a></p>


Welcome to another Friday Q&A.; I survived my travel and am (just barely) ready to write another exciting edition. This week's topic comes from [Gwynne](http://www.qmd-lang.org/), who asked why Objective-C only uses heap objects, and no stack objects.

Before we get into that, let's define our terms.

### Stack

The stack is a region of memory which contains storage for local variables, as well as internal temporary values and housekeeping. On a modern system, there is one stack per thread of execution. When a function is called, a _stack frame_ is pushed onto the stack, and function-local data is stored there. When the function returns, its stack frame is destroyed. All of this happens automatically, without the programmer taking any explicit action other than calling a function.

### Heap

The heap is, essentially, everything else in memory. (Yes, there are things other than the stack and heap, but let's ignore that for this discussion.)

Memory can be allocated on the heap at any time, and destroyed at any time.

You have to explicitly request for memory to be allocated from the heap, and if you aren't using garbage collection, explicitly free it as well. This is where you store things that need to outlive the current function call. The heap is what you access when you call `malloc` and `free`.

### Stack vs Heap Objects

Given that, what's a stack object, and what's a heap object?

First, we must understand what an object is in general. In Objective-C (and many other languages), an object is simply a contiguous blob of memory with a particular layout. (If you're interested in just what it contains and how it's laid out, check out my [intro to the Objective-C runtime](friday-qa-2009-03-13-intro-to-the-objective-c-runtime.html).)

The precise location of that memory is less important. As long as you have some memory somewhere with the right contents, it's a working Objective-C object. In Objective-C, objects are usually created on the heap:


```cpp
NSObject *obj = [[NSObject alloc] init];
```

The storage for the `obj` variable itself is on the stack, but the object it points to is in the heap. The `[NSObject alloc]` call allocates a chunk of heap memory, and fills it out to match the layout needed for an `NSObject`.

A stack object is just an object where the memory for that object is allocated on the stack. Objective-C doesn't have any support for this directly, but you can construct one manually without too much trouble:


```cpp
struct {
    Class isa;
} fakeNSObject;

fakeNSObject.isa = [NSObject class];
NSObject *obj = (NSObject *)&fakeNSObject;
NSLog(@"%@", [obj description]);
```

This works fine, although you shouldn't depend on it, as it depends on replicating the internal layout of the class.

### Advantages of Stack Objects

It's obviously possible to have stack objects in general. Aside from the above hack, real languages like C++ have language support for stack objects. In C++, you can create objects on the stack or the heap:


```cpp
std::string stackString;
std::string *heapString = new std::string;
```

**Why allow both?**

Stack objects have two compelling advantages:

  1. **Speed:** Allocating memory on the stack is really fast. All of the bookkeeping is done by the compiler when you build your program. At runtime, the function prolog just carves out the amount of space it needs for all local variables, and the code knows what goes where because it was all computed in advance. Stack allocations are essentially free, whereas heap allocations can be quite expensive. 
  2. **Simplicity:** Stack objects have a defined lifetime. You can never leak one, because it always gets destroyed at the end of the scope where it was declared. 

#### Disadvantages of Stack Objects

The strictly defined lifetime of a stack object is a disadvantage as well, and a major one. In Objective-C (and C++, and many other languages), it is impossible to move an object after it's created. The reason for this is because there may be many pointers to that object, and those pointers are not
tracked. They would all need to be updated to track the move, but there's no way to accomplish this.

(Note: it's not an impossibility in general, and many languages move objects around as a matter of course, often as part of garbage collection schemes. However, this requires more runtime smarts and a stricter type system than you get in Objective-C.)

As used in Cocoa, Objective-C uses a reference counting system for memory management. The advantage of this system is that any single object can have multiple "owners", and the system won't allow the object to be destroyed until all owners have relinquished ownership.

Stack allocated objects inherently have a single owner, the function which created them. If Objective-C had stack objects, what would happen if you passed it to some other code which then tried to keep it around by `retain`ing it? There's no way to prevent the object from being destroyed when the function which created it returns, so the `retain` can't work. The code which
tries to keep the object around will fail, end up with a dangling reference, and will crash.

Another problem is that stack objects are not very flexible. It's not uncommon in Objective-C to implement an initializer which destroys the original object and returns a new one instead. How could you do that with a stack object? You
really couldn't. Much of the runtime flexibility of Objective-C depends on having heap objects.

#### Actual Stack Objects in Objective-C

It turns out that Objective-C does have stack objects, truly and officially,as of 10.6!

Don't get too excited, though. It's only supported for a single kind of object: blocks. When you write a block inside a function using the `^{}` syntax, the result of that expression is a stack object!

But what about those problems I discussed above?

The problem with runtime dynamism doesn't exist with blocks. Blocks have a layout which is fixed by the language, and which can't be changed without destroying binary compatibility. The size of the block object can be computed at compile time, and in fact the whole object is built by compiler-generated code, so the possibility of writing an initializer that does tricky things simply doesn't exist.

The problem of object lifetime _does_ exist with blocks, but is less severe.
The reason for this is simply because blocks are a new kind of object that never existed in the language before, and any code that deals with a block will know that it needs to `copy` a block (which creates a copy on the heap, if it's not there already, and returns a pointer to that), rather than `retain` it, if it wants to keep a reference.

The stack nature of blocks does have some pitfalls, though. For example, this code is broken:


```cpp
void (^block)();
if(x)
{
    block = ^{ printf("x\n"); };
}
else
{
    block = ^{ printf("not x\n"); };
}
block();
```

Block stack objects are only valid through the lifetime of their enclosing scope, and here, their enclosing scopes cease to exist before the call to `block()` at the end. Other gotchas can happen when you pass blocks to code that doesn't know that they're blocks:


```cpp
[dictionary setObject: ^{ printf("hey hey\n"); } forKey: key];
```

The dictionary will `retain` that block object rather than `copy` it, leading to a dangling reference.

The speed and simplicity of stack objects are a great boon for blocks, but it also creates a whole new class of bugs for unwary programmers.

#### Conclusion

That wraps things up for this week. Come back in seven days for another exciting post. Until then, [keep those suggestions coming](mailto:mike@mikeash.com). My material comes from user ideas, so if you have a topic you would like to see discussed here, send it in!

Did you enjoy this article? I'm selling a whole book full of them. It's available for iBooks and Kindle, plus a direct download in PDF and ePub format. It's also available in paper for the old-fashioned. [Click here for more information](/book.html).

### Comments:

**[Psy|](http://remydemarest.wordpress.com/)** `at 2010-01-15 22:37:09:`

I think there is a mistake in here, at the end it's "stack":  
"A stack object is just an object where the memory for that object is
allocated on the heap."  

Otherwise great subject. :P

**[mikeash](http://mikeash.com)** `at 2010-01-15 23:00:54:`

Thanks for that, I've fixed it.

**[Jordy/Jediknil](http://belkadan.com)** `at 2010-01-15 23:48:35:`

As I understand it, a new scope is only created in C when you use `{ }`, and not just arbitrary if/else or (do/)while statements. After all, the body of an if statement in C is a _single_ statement. So the example should probably have braces to be correct.  

That said, both GCC and Clang appear to be forgiving here, even with the braces. That doesn't make it correct, though.

**[mikeash](http://mikeash.com)** `at 2010-01-16 00:03:24:`

It looks like the truth is somewhere in between. You appear to be right about if statements, but loops always create a scope. This code illustrates the problem:  


```cpp
void (^block[10])();  
       
int i = -1;   
while(++i < 10)   
    block[i] = ^{ printf("%d\n", i); };   
for(i = 0; i < 10; i++)   
    block[i]();`   
```

On my computer, this prints out ten 9s. If you copy the block when assigning, it prints out the correct 0-9 sequence.  

I could not make it happen with if statements, though, so it would seem that those are safe, at least.

**[Chris Ryland](http://grafly.com)** `at 2010-01-16 05:12:26:`

Can you expand a little on why that "if (x) ..." example is wrong?  

Those blocks' enclosing scope would be a function body, no? So they'd still be in scope at the call to block()?

**[Chris Ryland](http://grafly.com)** `at 2010-01-16 05:14:10:`

(Sorry, our comments are crossing real-time.)  

I don't think that code illustrates a problem with block scope per se, but with the free variable access.  

The block copy captures the free variable (i) in that case.

**[Jens Ayton](http://jens.ayton.se/blag/)** `at 2010-01-16 11:30:10:`

Chris Ryland: in many languages, e.g. JavaScript, that would indeed be the problem. In C-with-blocks, it isn’t; because i isn’t __block-qualified, it’s a constant copy rather than a capture. Each time the block is set up, the value of i is copied into space in the on-stack block structure.  

However, because of the scoping issue, the same piece of stack is used each time, so each iteration effectively overwrites the previous iteration’s block object. The only difference is the value of i.  

This also explains why copying the block fixes the problem, which it wouldn’t in JS if there was such a thing as copying a closure there.

**[Joachim Bengtsson](http://nevyn.nu/)** `at 2010-01-16 14:10:27:`

This is how I illustrate the problem with incorrect memory management with stack allocated block objects in my guide (<http://thirdcog.eu/pwcblocks/#cblocks-memory>):  

```cpp
// Incorrect:  
typedef void(^BasicBlock)(void);  
void someFunction() {  
    BasicBlock block;   
    if(condition) {   
        block = ^ { ... };   
    } else {   
        block = ^ { ... };   
    }   
    ...   
}  

// Basically equivalent of:  
void someFunction() {  
    BasicBlock block;   
    if(condition) {   
        struct Block_literal_1 blockStorage = ...;   
        block = &blockStorage;   
    } // blockStorage falls off the stack here   
    else   
    {   
        struct Block_literal_1 blockStorage = ...;   
        block = &blockStorage;   
    } // blockStorage falls off the stack here   
    // and block thus points to "non-existing"/invalid memory   
    ...   
}  

// Correct:  
void someFunction() {  
    BasicBlock block;   
    if(condition) {   
        block = Block_copy(^ { ... });   
    } else {   
        block = Block_copy(^ { ... });   
    }   
    ...   
}
```

The realization of how block memory management works came to me when reading Clang's implementation specification for blocks(<http://clang.llvm.org/docs/BlockImplementation.txt>); I had such a hard time understanding the problem before then.  

Jordy: Didn't know about if-without-brackets not creating scopes, thanks!

**[mikeash](http://mikeash.com)** `at 2010-01-16 15:01:55:`

And thus I discover that my comment escaping code didn't handle tabs very well. It's better now. (Still not great: it unconditionally expands them to four spaces no matter where they are, but better.)

**Jason Bogdan** `at 2010-01-16 20:58:50:`

So the reason you *must* keep pointers to Objective-C objects is because they are allocated on the heap, and you can't have static, non-pointer variables (e.g. NSArray array) to objects on the heap?

**[mikeash](http://mikeash.com)** `at 2010-01-16 21:56:20:`

Essentially correct. Technically, something like `NSArray array` can live on the heap too, like if it's an instance variable of an object, but then it's just a part of a larger allocation and this has all of the same problems as stack objects do.

**J Osborne** `at 2010-01-19 01:00:05:`

If Objective-C had stack objects, what would happen if you passed it to some other code which then tried to keep it around by retaining it? There's no way to prevent the object from being destroyed when the function which created it returns, so the retain can't work. The code which tries to keep the object
around will fail, end up with a dangling reference, and will crash.  


Well you could define your way around it. Cause an error when a stack object is retain'ed, but that isn't very useful. You could allow the retain, but cause an error if the retain count is non-zero when the function that created the stack object returns. That would be mostly workable.  

It would fail when you make changes to an existing framework that change an existing code path to one that "retains longer". Then you would need to invent a retain_or_copy method that retains heap objects but does a copy for a stack object.  

That still fails if you want to support init methods that return new objects.  

You could allow stack based declaration of an object, but only pointer based calls, which would encourage "proper" use  

```cpp
Object stackObj;  
Object *sameObj = [&stackObj init];  
```

However people could (incorrectly) call things other then init using the address operator. Maybe if you added a warning when the method doesn't start with init...  

Which is a lot of work...work that _does_ get you a good hook into "this method is called as the enclosing function exits" which is nice to use for resource acquisition (say locks, or many other things). RAII is one of the few C++ things I **really** miss in ObjC...  

**[mikeash](http://mikeash.com)** `at 2010-01-19 01:35:37:`

I don't think that your retain workarounds are practical. The problem is that in Objective-C/Cocoa as it stands now, you're allowed to retain any object at any time (as long as you balance it with a release later, of course). Your proposals, even the "error if retain count is non-zero when you return" one,
would alter this. As a consequence, you either would be unable to pass stack objects to code you didn't control, like Cocoa APIs, or every API would need to be annotated to describe whether it's safe to pass a stack object to it or not.  

I think the retain_or_copy idea would be the way to go. This is essentially how blocks work: copying a block that's already on the heap just retains it.
Howeer, this would require a wholesale reworking of the framework.  

As far as RAII goes, I think you can get pretty much the same benefits using blocks now. Take the typical RAII example of managing a file handle:  

```cpp
file logfile("logfile.txt");  
logfile.write("some log");
```

Using blocks, you can write a method that takes a block and does the same
stuff:  

```cpp
+ (void)useFile: (NSString *)path withBlock: (void (^)(File *))block  
{   
    File *file = [[self alloc] initWithFile: path];   
    @try {   
        block(file);   
    }   
    @finally {   
        [file close];   
        [file release];   
    }   
}   

// to use it   
[File useFile: @"logfile.txt" withBlock: ^(File *file) {   
    [file write: @"some log"];   
}];   
```

This is how Ruby does it, for example.  

I really dislike C++ so I'm probably biased, but I think that closure-based resource management like this is actually better than C++-style RAII. RAII basically takes advantage of one aspect of the language (stack object memory management) to implement a completely unrelated feature (releasing resources when leaving a scope). The whole idea of closures is to be able to pass bits of code around like this, so it fits much better.  

Your mileage, of course, may vary.

**[Uli Kusterer](http://www.zathras.de)** `at 2010-01-22 11:52:49:`

I don't understand the  


```cpp
if( x )  
    block = ...   
else  
    block = ...   
block();  
```

example. That's all the same scope, why is this suddenly a problem with blocks? Did you forget the scope brackets on the "if"s here, to make it like Joachim Bengtsson's example? If you did, could you please fix the articles before everyone googling for blocks on the net learns it wrong?  

If not, could you elaborate on the differences in this regard between blocks and regular code?

**[mikeash](http://mikeash.com)** `at 2010-01-22 20:52:30:`

I've fixed the example. However, I would be extremely wary of writing code without the braces even so. It's bad to write code that will suddenly break mysteriously if you add some braces to a control structure, and it can also give you a bad habit since otherwise identical code with a for or while loop _does_ get an implicit inner scope and will break.

**Jason** `at 2010-01-24 23:17:30:`

Mike, you said:  

```cpp
void (^block[10])();  
       
int i = -1;   
while(++i < 10)   
    block[i] = ^{ printf("%d\n", i); };   
for(i = 0; i < 10; i++)   
    block[i]();   
```

On my computer, this prints out ten 9s. If you copy the block when assigning, it prints out the correct 0-9 sequence. "  

This has more to do with the closure of the 'i' variable than the assignment to block. In C#, the compiler warns against this ("Access to modified closure" - Eric Lippert and Raymond Chen have excellent blog posts about this subject. Try assigning 'i' to a temporary variable so the block grabs a "local copy" of
it:  

```cpp
int i = -1;   
while(++i < 10) {   
    int icopy = i;   
    block[i] = ^{ printf("%d\n", icopy); };   
}   
for(i = 0; i < 10; i++)   
    block[i]();   
```

**[mikeash](http://mikeash.com)** `at 2010-01-25 01:45:47:`

No it doesn't. If that were the case, then the behavior wouldn't change when you copy the block. (Copying the block is _purely_ an act of memory management. In correct code, copying a block will never change behavior.)  

Did you try your proposed modification? It _still_ prints out ten 9s....  

Blocks in Objective-C _always_ grab a "local copy" of all closed-over local variables, unless you explicitly request otherwise by qualifying the declaration with the `__block` qualifier.  

The reason it prints out ten 9s in the first case is quite simple: the block that's created within the loop has a lifetime that's tied to the loop's inner scope. The block is destroyed at the next iteration of the loop, and when leaving the loop. Of course, "destroy" just means that its slot on the stack is available to be overwritten. It just happens that the compiler reuses the same slot each time through the loop, so in the end, the array is filled with identical pointers, and thus you get identical behavior.  

Do not read about how closures behave in other languages and assume that it carries over to Objective-C. Most other languages close over locals as a mutable reference rather than a const copy by default. The only exception to this that I'm aware of is Java, and it requires you to explicitly declare locals as `final` (equivalent to `const`) when closing over them. As far as I'm aware, no other language has Objective-C's behavior of closing over any local or parameter as a const copy, and of allowing explicitly-qualified locals to be closed mutably.

**Jason** `at 2010-01-25 12:33:47:`

Mike,  

Thanks for the clarification. This helps a lot. It may also be helpful to explain (in pseudocode) what exactly the compiler is doing (much like explaining how Obj-C messages get transformed into objc_msgSend calls)..  

Does it essentially take something like this:  

```cpp
void (^block[10])();   

int i = -1;   
while(++i < 10)   
    block[i] = ^{ printf("%d\n", i); };   
for(i = 0; i < 10; i++)   
    block[i]();   
```

And turn it into this:  

```cpp
anonymous_method_1(NSBlock * state)   
{   
    printf("%d\n", state->vars->i);   
}   

NSBlock *block[10];   

int i = -1;   
while(++i < 10) {   
    NSBlock the_block; // stack allocated   
    // ... capture i into the_block   
    the_block.imp = anonymous_method_1;   
    block[i] = &the_block;   
}   
for(i = 0; i < 10; i++)   
    block[i]->imp();   
```

Grossly simplified, of course, but it sounds like this is what happens internally.  


**[mikeash](http://mikeash.com)** `at 2010-01-25 22:52:34:`

Yep, that's pretty much it. Like you say it's grossly simplified, but the essential aspect that it just creates a struct on the stack and fills it out is just what happens in real code.

**[Louis Gerbarg](http://www.devwhy.com/)** `at 2010-01-26 15:39:24:`

If you directly invoke clang-cc you can actually see what the rewritten code looks like. The rewriter actually generates C++ code so that it can directly embed the anon functions inside a struct that represents its scope. Obviously the actual compiler doesn't do it quite that way internally, it is just the most sensible way to emit ASTs with block contexts in them as code that doesn't depend on blocks. For a concrete example:  


```cpp
//With blocks and libdispatch  

#include <stdio.h>  
#include <stdlib.h>  
#include <stdint.h>  
#include <inttypes.h>  

#include <dispatch/dispatch.h>  

//We add a completion handler that gets called when all the work is down,  
//it is just another block  

void call_100_times(void (^callback)(void), void (^completion)(void)) {  
  uint32_t i;  
  dispatch_queue_t queue =
  dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_HIGH, 0);  

  for (i = 0; i < 100; i++) {  
    dispatch_async(queue, callback);   
  }  

  dispatch_async(queue, completion);  
}  

int main(void) {  
  __block volatile uint32_t i = 0;  
  dispatch_queue_t main_queue = dispatch_get_main_queue();  

  call_100_times(^{  
    //Issue an asynch printf from whatever queue we are on to the main queue   
    dispatch_async(main_queue, ^{   
      uint32_t incremented_value = __sync_add_and_fetch(&i, 1);   
      printf("Out: %" PRIu32 "\n", incremented_value - 1);   
    });   
  },  
  ^{  
    //Need to explicitly call exit now that the end of main is never reached   
    //We do it here in the completion block   
    dispatch_async(main_queue, ^{   
      exit(0);   
    });   
  });  

  //Start the dispatcher  
  dispatch_main();  

  //NOT REACHED  
}  

Gets rewritten as:  

#ifndef BLOCK_IMPL  
#define BLOCK_IMPL 

struct __block_impl {  
  void *isa;  
  int Flags;  
  int Size;  
  void *FuncPtr;  
};  

enum {  
  BLOCK_HAS_COPY_DISPOSE = (1<<25),  
  BLOCK_IS_GLOBAL = (1<<28)  
};  

#define __OBJC_RW_EXTERN extern  
// Runtime copy/destroy helper functions  
__OBJC_RW_EXTERN void _Block_copy_assign(void *, void *);  
__OBJC_RW_EXTERN void _Block_byref_assign_copy(void *, void *);  
__OBJC_RW_EXTERN void _Block_destroy(void *);  
__OBJC_RW_EXTERN void _Block_byref_release(void *);  
__OBJC_RW_EXTERN void *_NSConcreteGlobalBlock;  
__OBJC_RW_EXTERN void *_NSConcreteStackBlock;  
#endif  
//With blocks and libdispatch  
```

```cpp
#include <stdio.h>  
#include <stdlib.h>  
#include <stdint.h>  
#include <inttypes.h>  

#include <dispatch/dispatch.h>  

//We add a completion handler that gets called when all the work is down,  
//it is just another block  

void call_100_times(void (*callback)(void), void (^comple*ion)(void)) {  
  uint32_t i;  
  dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_HIGH, 0);  

  for (i = 0; i < 100; i++) {  
    dispatch_async(queue, callback);   
  }  

  dispatch_async(queue, completion);  
}  

struct __main_block_impl_0 {  
  struct __block_impl impl;  
  uint32_t volatile *i; // by ref  
  __main_block_impl_0(void *fp, uint32_t volatile *_i, int flags=0) {  
    impl.isa = 0/*&_NSConcreteStackBlock*/;   
    impl.Size = sizeof(__main_block_impl_0);   
    impl.Flags = flags;   
    impl.FuncPtr = fp;   
    i = _i;   
  }  
};  

static void __main_block_func_0(struct __main_block_impl_0 *__cself) {  
  uint32_t volatile *i = __cself->i; // bound by ref  

  uint32_t incremented_value = __sync_add_and_fetch(&*i, 1);   
  printf("Out: %" PRIu32 "\n", incremented_value - 1);   
} 

struct __main_block_impl_1 {  
  struct __block_impl impl;  
  dispatch_queue_t main_queue;  
  uint32_t volatile *i; // by ref  
  __main_block_impl_1(void *fp, dispatch_queue_t _main_queue, uint32_t
  volatile *_i, int flags=0) 
  {  
    impl.isa = 0/*&_NSConcreteStackBlock*/;   
    impl.Size = sizeof(__main_block_impl_1);   
    impl.Flags = flags;   
    impl.FuncPtr = fp;   
    main_queue = _main_queue;   
    i = _i;   
  }  
};  

static void __main_block_func_1(struct __main_block_impl_1 *__cself) {  
  uint32_t volatile *i = __cself->i; // bound by ref  
  dispatch_queue_t main_queue = __cself->main_queue; // bound by copy  

    //Issue an asynch printf from whatever queue we are on to the main queue   
    dispatch_async(main_queue, (void (*)(void))&__main_block_impl_0((void*)__main_block_func_0,&i));   
  }  
struct __main_block_impl_2 {  
  struct __block_impl impl;  
  __main_block_impl_2(void *fp, int flags=0) {  
    impl.isa = 0/*&_NSConcreteStackBlock*/;   
    impl.Size = sizeof(__main_block_impl_2);   
    impl.Flags = flags;   
    impl.FuncPtr = fp;   
  }  
};  

static void __main_block_func_2(struct __main_block_impl_2 *__cself) {  
  exit(0);   
}

struct __main_block_impl_3 {  
  struct __block_impl impl;  
  dispatch_queue_t main_queue;  
  __main_block_impl_3(void *fp, dispatch_queue_t _main_queue, int flags=0) {  
    impl.isa = 0/*&_NSConcreteStackBlock*/;   
    impl.Size = sizeof(__main_block_impl_3);   
    impl.Flags = flags;   
    impl.FuncPtr = fp;   
    main_queue = _main_queue;   
  }  
}; 

static void __main_block_func_3(struct __main_block_impl_3 *__cself) {  
  dispatch_queue_t main_queue = __cself->main_queue; // bound by copy  

    //Need to explicitly call exit now that the end of main is never reached   
    //We do it here in the completion block   
    dispatch_async(main_queue, (void (*)(void))&__main_block_impl_2((void*)__main_block_func_2));   
  } 

int main(void) {  
  __block volatile uint32_t i = 0;  
  dispatch_queue_t main_queue = dispatch_get_main_queue();  

  call_100_times((void
(*)(void))&__main_block_impl_1((void*)__main_block_func_1,main_queue,&i),  
  (void
(*)(void))&__main_block_impl_3((void*)__main_block_func_3,main_queue));  

  //Start the dispatcher  
  dispatch_main();  

  //NOT REACHED  
}  
```

**[Gabriele](http://stackoverflow.com/questions/11738248/wrap-c-callbacks-by-blocks-bridge-transfer-and-blocks)** `at 2012-07-31 16:57:30:`

Thanks a lot for your post.  
FYI, when using __bridge_retained on blocks that are on the stack, with Xcode 4.4, O3, ARC, the compiler does neither retain nor copy the block... Good source of bugs :-)

**santhosh** `at 2014-02-25 12:01:44:`

Thanks guys. Not only i learned much from the article, but a great deal from comments. I should fix some of my projects.thanks again.

[Comments RSS feed for this page](/commentsrss.py?page=pyblog/friday-qa-2010-01-15-stack-and-heap-objects-in-objective-c.html)

Add your thoughts, post a comment:

Spam and off-topic posts will be deleted without notice. Culprits may be publicly humiliated at my sole discretion.

**JavaScript is required to submit comments** due to anti-spam measures. Please enable JavaScript and reload the page.