<!--BEGIN_DATA
{
    "create_date": "2024-01-01 15:00", 
    "modify_date": "2024-01-01 15:00", 
    "is_top": "0", 
    "summary": "Understanding Symmetric Transfer<br/>Understanding the Compiler Transform<br/>", 
    "tags": "C/C++", 
    "file_name": "C++ Coroutines 02.md"
}
END_DATA-->


#### <p>原文出处：<a href='https://lewissbaker.github.io/2020/05/11/understanding_symmetric_transfer' target='blank'>Understanding Symmetric Transfer</a></p>

The Coroutines TS provided a wonderful way to write asynchronous code as if you
were writing synchronous code. You just need to sprinkle `co_await` at appropriate
points and the compiler takes care of suspending the coroutine, preserving state
across suspend-points and resuming execution of the coroutine later when the
operation completes.

However, the Coroutines TS, as it was originally specified, had a nasty limitation
that could easily lead to stack-overflow if you weren't careful. And if you wanted
to avoid this stack-overflow then you had to introduce extra synchronisation
overhead to safely guard against this in your `task<T>` type.

Thankfully, a tweak was made to the design of coroutines in 2018 to add a capability
called "symmetric transfer" which allows you to suspend one coroutine and resume
another coroutine without consuming any additional stack-space. The addition of this
capability lifted a key limitation of the Coroutines TS and allows for much simpler
and more efficient implementation of async coroutine types without sacrificing any
of the safety aspects needed to guard against stack-overflow.

In this post I will attempt to explain the stack-overflow problem and how the addition
of this key "symmetric transfer" capability lets us solve this problem.

## First some background on how a task coroutine works

Consider the following coroutines:

```cpp
task foo() {
  co_return;
}

task bar() {
  co_await foo();
}
```

Assume we have a simple `task` type that lazily executes the body when another coroutine awaits it.
This particular `task` type does not support returning a value.

Let's unpack what's happening here when `bar()` evaluates `co_await foo()`.

* The `bar()` coroutine calls the `foo()` function.
  Note that from the caller's perspective a coroutine is just an ordinary function.
* The invocation of `foo()` performs a few steps:
  * Allocates storage for a coroutine frame (typically on the heap)
  * Copies parameters into the coroutine frame (in this case there are no parameters so this is a no-op).
  * Constructs the promise object in the coroutine frame
  * Calls `promise.get_return_object()` to get the return-value for `foo()`.
    This produces the `task` object that will be returned, initialising it with a
    `std::coroutine_handle` that refers to the coroutine frame that was just created.
  * Suspends execution of the coroutine at the initial-suspend point (ie. the open curly brace)
  * Returns the `task` object back to `bar()`.
* Next the `bar()` coroutine evaluates the `co_await` expression on the `task` returned from `foo()`.
  * The `bar()` coroutine suspends and then calls the `await_suspend()` method on the returned task,
    passing it the `std::coroutine_handle` that refers to `bar()`'s coroutine frame.
  * The `await_suspend()` method then stores `bar()`'s `std::coroutine_handle` in `foo()`'s promise object
    and then resumes the `foo()` coroutine by calling `.resume()` on `foo()`'s `std::coroutine_handle`.
* The `foo()` coroutine executes and runs to completion synchronously.
* The `foo()` coroutine suspends at the final-suspend point (ie. the closing curly brace)
  and then resumes the coroutine identified by the `std::coroutine_handle` that was stored
  in its promise object before it was started. ie. `bar()`'s coroutine.
* The `bar()` coroutine resumes and continues executing and eventually reaches the
  end of the statement containing the `co_await` expression at which point it calls
  the destructor of the temporary `task` object returned from `foo()`.
* The `task` destructor then calls the `.destroy()` method on `foo()`'s coroutine
  handle which then destroys the coroutine frame along with the promise object
  and copies of any arguments.

Ok, so that seems like a lot of steps for a simple call.

To help understand this in a bit more depth, let's look at how a naive
implementation of this `task` class would look when implemented using the
the Coroutines TS design (which didn't support symmetric transfer).

## Outline of a `task` implementation

The outline of the class looks something like this:

```cpp
class task {
public:
  class promise_type { /* see below */ };

  task(task&& t) noexcept
  : coro_(std::exchange(t.coro_, {}))
  {}

  ~task() {
    if (coro_)
      coro_.destroy();
  }

  class awaiter { /* see below */ };

  awaiter operator co_await() && noexcept;

private:
  explicit task(std::coroutine_handle<promise_type> h) noexcept
  : coro_(h)
  {}

  std::coroutine_handle<promise_type> coro_;
};
```

A `task` has exclusive ownership of the `std::coroutine_handle` that corresponds
to the coroutine frame created during the invocation of the coroutine.
The `task` object is an RAII object that ensures that `.destroy()` is called
on the `std::coroutine_handle` when the `task` object goes out of scope.

So now let's expand on the `promise_type`.

## Implementing `task::promise_type`

From the [previous post]({{ site.baseurl }}{% link _posts/2018-09-05-understanding-the-promise-type.md %})
we know that the `promise_type` member defines the type of the **Promise** object that
is created within the coroutine frame and that controls the behaviour of the coroutine.

First, we need to implement the `get_return_object()` to construct the `task` object
to return when the coroutine is invoked. This method just needs to initialise the task
with the `std::coroutine_handle` of the newly create coroutine frame.

We can use the `std::coroutine_handle::from_promise()` method to manufacture one of these
handles from the promise object.


```cpp
class task::promise_type {
public:
  task get_return_object() noexcept {
    return task{std::coroutine_handle<promise_type>::from_promise(*this)};
  }
```

Next, we want the coroutine to initially suspend at the open curly brace
so that we can later resume the coroutine from this point when the returned
`task` is awaited.

There are several benefits of starting the coroutine lazily:
1. It means that we can attach the continuation's `std::coroutine_handle` before
  starting execution of the coroutine. This means we don't need to use
  thread-synchronisation to arbitrate the race between attaching the
  continuation later and the coroutine running to completion.
2. It means that the `task` destructor can unconditionally destroy the
  coroutine frame - we don't need to worry about whether the coroutine
  is potentially executing on another thread since the coroutine will
  not start executing until we await it, and while it is executing the
  calling coroutine is suspended and so won't attempt to call the task
  destructor until the coroutine finishes executing.
  This gives the compiler a much better chance at inlining the allocation
  of the coroutine frame into the frame of the caller.
  See [P0981R0](https://wg21.link/P0981R0) to read more about the Heap Allocation eLision Optimisation (HALO).
3. It also improves the exception-safety of your coroutine code. If you don't
  immediately `co_await` the returned `task` and do something else that
  can throw an exception that causes the stack to unwind and the `task` destructor
  to run then we can safely destroy the coroutine since we know it hasn't
  started yet. We aren't left with the difficult choice between detaching,
  potentially leaving dangling references, blocking in the destructor, terminating
  or undefined-behaviour.
  This is something that I cover in a bit more detail in my
  [CppCon 2019 talk on Structured Concurrency](https://www.youtube.com/watch?v=1Wy5sq3s2rg).

To have the coroutine initially suspend at the open curly brace we define an
`initial_suspend()` method that returns the builtin `suspend_always` type.


```cpp
  std::suspend_always initial_suspend() noexcept {
    return {};
  }
```

Next, we need to define the `return_void()` method, called when you
execute `co_return;` or when execution runs off the end of the coroutine.
This method doesn't actually need to do anything, it just needs to exist
so that the compiler knows that `co_return;` is valid within this coroutine
type.


```cpp
  void return_void() noexcept {}
```

We also need to add an `unhandled_exception()` method that is called
if an exception escapes the body of the coroutine. For our purposes we
can just treat the task coroutine bodies as `noexcept` and call
`std::terminate()` if this happens.


```cpp
  void unhandled_exception() noexcept {
    std::terminate();
  }
```

Finally, when the coroutine execution reaches the closing curly brace, we
want the coroutine to suspend at the final-suspend point and then resume
its continuation. ie. the coroutine that is awaiting the completion of this
coroutine.

To support this, we need a data-member in the promise to hold the `std::coroutine_handle`
of the continuation. We also need to define the `final_suspend()` method that
returns an awaitable object that will resume the continuation after the current
coroutine has suspended at the final-suspend point.

It's important to delay resuming the continuation until after the current coroutine
has suspended because the continuation may go on to immediately call the `task`
destructor which will call `.destroy()` on the coroutine frame.
The `.destroy()` method is only valid to call on a suspended coroutine and
so it would be undefined-behaviour to resume the continuation before the current coroutine
has suspended.

The compiler inserts code to evaluate the statement `co_await promise.final_suspend();`
at the closing curly brace.

It's important to note that the coroutine is not yet in a
suspended state when the `final_suspend()` method is invoked.
We need to wait until the `await_suspend()` method on the returned
awaitable is called before the coroutine is suspended.


```cpp
  struct final_awaiter {
    bool await_ready() noexcept {
      return false;
    }

    void await_suspend(std::coroutine_handle<promise_type> h) noexcept {
      // The coroutine is now suspended at the final-suspend point.
      // Lookup its continuation in the promise and resume it.
      h.promise().continuation.resume();
    }

    void await_resume() noexcept {}
  };

  final_awaiter final_suspend() noexcept {
    return {};
  }

  std::coroutine_handle<> continuation;
};
```

Ok, so that's the complete `promise_type`. The final piece we need to implement
is the `task::operator co_await()`.

## Implementing `task::operator co_await()`

You may remember from the [Understanding operator co_await() post]({{ site.baseurl }}{% link _posts/2017-11-17-understanding-operator-co-await.md %})
that when evaluating a `co_await` expression, the compiler will generate a call to
`operator co_await()`, if one is defined, and then the object returned must have the
`await_ready()`, `await_suspend()` and `await_resume()` methods defined.

When a coroutine awaits a `task` we want the awaiting coroutine to always suspend and
then, once it has suspended, store the awaiting coroutine's handle in the promise of
the coroutine we are about to resume and then call `.resume()` on the `task`'s
`std::coroutine_handle` to start executing the task.

Thus the relatively straight forward code:

```cpp
class task::awaiter {
public:
  bool await_ready() noexcept {
    return false;
  }

  void await_suspend(std::coroutine_handle<> continuation) noexcept {
    // Store the continuation in the task's promise so that the final_suspend()
    // knows to resume this coroutine when the task completes.
    coro_.promise().continuation = continuation;

    // Then we resume the task's coroutine, which is currently suspended
    // at the initial-suspend-point (ie. at the open curly brace).
    coro_.resume();
  }

  void await_resume() noexcept {}

private:
  explicit awaiter(std::coroutine_handle<task::promise_type> h) noexcept
  : coro_(h)
  {}

  std::coroutine_handle<task::promise_type> coro_;
};

task::awaiter task::operator co_await() && noexcept {
  return awaiter{coro_};
}
```

And thus completes the code necessary for a functional `task` type.

You can see the complete set of code in Compiler Explorer here: [https://godbolt.org/z/-Kw6Nf](https://godbolt.org/z/-Kw6Nf)

## The stack-overflow problem

The limitation of this implementation arises, however, when you start writing loops
within your coroutines and you `co_await` tasks that can potentially complete synchronously
within the body of that loop.

For example:

```cpp
task completes_synchronously() {
  co_return;
}

task loop_synchronously(int count) {
  for (int i = 0; i < count; ++i) {
    co_await completes_synchronously();
  }
}
```

With the naive `task` implementation described above, the `loop_synchronously()` function
will (probably) work fine when `count` is 10, 1000, or even 100'000. But there will be a value
that you can pass that will eventually cause this coroutine to start crashing.

For example, see: [https://godbolt.org/z/gy5Q8q](https://godbolt.org/z/gy5Q8q) which crashes when `count` is 1'000'000.

The reason that this is crashing is because of stack-overflow.

To understand why this code is causing a stack-overflow we need to take a look at
what is happening when this code is executing. In particular, what is happening to
the stack-frames.

When the `loop_synchronously()` coroutine first starts executing it will be because
some other coroutine `co_await`ed the `task` returned. This will in turn suspend the
awaiting coroutine and call `task::awaiter::await_suspend()` which will call `resume()`
on the task's `std::coroutine_handle`.

Thus the stack will look something like this when `loop_synchronously()` starts:
```
           Stack                                                   Heap
+------------------------------+  <-- top of stack   +--------------------------+
| loop_synchronously$resume    | active coroutine -> | loop_synchronously frame |
+------------------------------+                     | +----------------------+ |
| coroutine_handle::resume     |                     | | task::promise        | |
+------------------------------+                     | | - continuation --.   | |
| task::awaiter::await_suspend |                     | +------------------|---+ |
+------------------------------+                     | ...                |     |
| awaiting_coroutine$resume    |                     +--------------------|-----+
+------------------------------+                                          V
|  ....                        |                     +--------------------------+
+------------------------------+                     | awaiting_coroutine frame |
                                                     |                          |
                                                     +--------------------------+
```

> Note: When a coroutine function is compiled the compiler typically splits it into
two parts:
> 1. the "ramp function" which deals with the construction of the coroutine
frame, parameter copying, promise construction and producing the return-value, and
> 2. the "coroutine body"
which contains the user-authored logic from the body of the coroutine.
>
> I use the `$resume` suffix to refer to the "coroutine body" part of the coroutine.
>
> A later blog post will go into more detail about this split.

Then when `loop_synchronously()` awaits the `task` returned from `completes_synchronously()`
the current coroutine is suspended and calls `task::awaiter::await_suspend()`.
The `await_suspend()` method then calls `.resume()` on the coroutine handle corresponding
to the `completes_synchronously()` coroutine.

This resumes the `completes_synchronously()` coroutine which then runs to completion
synchronously and suspends at the final-suspend point. It then calls
`task::promise::final_awaiter::await_suspend()` which calls `.resume()` on the coroutine
handle corresponding to `loop_synchronously()`.

The net result of all of this is that if we look at the state of the program just after the
`loop_synchronously()` coroutine is resumed and just before the temporary `task` returned by
`completes_synchronously()` is destroyed at the semicolon then the stack/heap should look
something like this:
```
           Stack                                                   Heap
+-------------------------------+ <-- top of stack
| loop_synchronously$resume     | active coroutine -.
+-------------------------------+                   |
| coroutine_handle::resume      |            .------'
+-------------------------------+            |
| final_awaiter::await_suspend  |            |
+-------------------------------+            |  +--------------------------+ <-.
| completes_synchronously$resume|            |  | completes_synchronously  |   |
+-------------------------------+            |  | frame                    |   |
| coroutine_handle::resume      |            |  +--------------------------+   |
+-------------------------------+            '---.                             |
| task::awaiter::await_suspend  |                V                             |
+-------------------------------+ <-- prev top  +--------------------------+   |
| loop_synchronously$resume     |     of stack  | loop_synchronously frame |   |
+-------------------------------+               | +----------------------+ |   |
| coroutine_handle::resume      |               | | task::promise        | |   |
+-------------------------------+               | | - continuation --.   | |   |
| task::awaiter::await_suspend  |               | +------------------|---+ |   |
+-------------------------------+               | - task temporary --|---------'
| awaiting_coroutine$resume     |               +--------------------|-----+
+-------------------------------+                                    V
|  ....                         |               +--------------------------+
+-------------------------------+               | awaiting_coroutine frame |
                                                |                          |
                                                +--------------------------+
```

Then the next thing this will do is call the `task` destructor which will destroy the
`completes_synchronously()` frame. It will then increment the `count` variable and go around
the loop again, creating a new `completes_synchronously()` frame and resuming it.

In effect, what is happening here is that `loop_synchronously()` and `completes_synchronously()`
end up recursively calling each other. Each time this happens we end up consuming a bit more
stack-space, until eventually, after enough iterations, we overflow the stack and end up in
undefined-behaviour land, typically resulting in your program promptly crashing.

Writing loops in coroutines built this way makes it very easy to write functions that
perform unbounded recursion without looking like they are doing any recursion.

So, what would the solution look like under the original Coroutines TS design?

## The Coroutines TS solution

Ok, so what can we do about this to avoid this kind of unbounded recursion?

With the above implementation we are using the variant of `await_suspend()` that returns `void`.
In the Coroutines TS there is also a version of `await_suspend()` that returns `bool` -
if it returns `true` then the coroutine is suspended and execution
returns to the caller of `resume()`, otherwise if it returns `false` then the coroutine
is immediately resumed, but this time without consuming any additional stack-space.

So, to avoid the unbounded mutual recursion what we want to do is make use of the
`bool`-returning version of `await_suspend()` to resume the current coroutine by
returning `false` from the `task::awaiter::await_suspend()` method if the task
completes synchronously instead of resuming the coroutine recursively using
`std::coroutine_handle::resume()`.

To implement a general solution for this there are two parts.

1. Inside the `task::awaiter::await_suspend()` method you can start executing the
coroutine by calling `.resume()`. Then when the call to `.resume()` returns,
check whether the coroutine has run to completion or not. If it has run to completion
then we can return `false`, which indicates the awaiting coroutine should immediately
resume, or we can return `true`, indicating that execution should return to the caller
of `std::coroutine_handle::resume()`.

1. Inside `task::promise_type::final_awaiter::await_suspend()`,
which is run when the coroutine runs to completion, we need to check whether
the awaiting coroutine has (or will) return `true` from `task::awaiter::await_suspend()`
and if so then resume it by calling `.resume()`. Otherwise, we need to avoid resuming
the coroutine and notify `task::awaiter::await_suspend()` that it needs to return
`false`.

There is an added complication, however, in that it's possible for a coroutine to
start executing on the current thread then suspend and later resume and run to completion
on a different thread before the call to `.resume()` returns.
Thus, we need to be able to resolve the potential race between part 1 and part 2 above
happening concurrently.

We will need to use a `std::atomic` value to decide the winner of the race here.


Now for the code. We can make the following modifications:

```cpp
class task::promise_type {
  ...

  std::coroutine_handle<> continuation;
  std::atomic<bool> ready = false;
};

bool task::awaiter::await_suspend(
    std::coroutine_handle<> continuation) noexcept {
  promise_type& promise = coro_.promise();
  promise.continuation = continuation;
  coro_.resume();
  return !promise.ready.exchange(true, std::memory_order_acq_rel);
}

void task::promise_type::final_awaiter::await_suspend(
    std::coroutine_handle<promise_type> h) noexcept {
  promise_type& promise = h.promise();
  if (promise.ready.exchange(true, std::memory_order_acq_rel)) {
    // The coroutine did not complete synchronously, resume it here.
    promise.continuation.resume();
  }
}
```

See the updated example on Compiler Explorer: [https://godbolt.org/z/7fm8Za](https://godbolt.org/z/7fm8Za)
Note how it no longer crashes when executing the `count == 1'000'000` case.

This turns out to be the approach that the `cppcoro::task<T>`
[implementation](https://github.com/lewissbaker/cppcoro/blob/master/include/cppcoro/task.hpp)
took to avoid the unbounded recursion problem (and still does for some platforms)
and it has worked reasonably well.

Woohoo! Problem solved, right? Ship it! Right...?

## The problems

While the above solution does solve the recursion problem it has a couple of drawbacks.

Firstly, it introduces the need for `std::atomic` operations which can be quite costly.
There is an atomic exchange on the caller when suspending the awaiting
coroutine, and another atomic exchange on the callee when it runs to completion.
If your application only ever executes on a single thread then you are paying the
cost of the atomic operations for synchronising threads even though it's never needed.

Secondly, it introduces additional branches. One in the caller, which needs to decide
whether to suspend or immediately resume the coroutine, and one in the callee, which
needs to decide whether to resume the continuation or suspend.

Note that the cost of this extra branch, and possibly even the atomic operations,
would often be dwarfed by the cost of the business logic present in the coroutine.
However, coroutines have been advertised as a zero cost abstraction and there have
even been people using coroutines to suspend execution of a function to avoid
waiting for an L1-cache-miss (see Gor's great
[CppCon talk on nanocoroutines](https://www.youtube.com/watch?v=j9tlJAqMV7U) for
more details on this).

Thirdly, and probably most importantly, it introduces some non-determinism in the
execution-context that the awaiting coroutine resumes on.

Let's say I have the following code:

```cpp
cppcoro::static_thread_pool tp;

task foo()
{
  std::cout << "foo1 " << std::this_thread::get_id() << "\n";
  // Suspend coroutine and reschedule onto thread-pool thread.
  co_await tp.schedule();
  std::cout << "foo2 " << std::this_thread::get_id() << "\n";
}

task bar()
{
  std::cout << "bar1 " << std::this_thread::get_id() << "\n";
  co_await foo();
  std::cout << "bar2" << std::this_thread::get_id() << "\n";
}
```

With the original implementation we were guaranteed that the code that runs after
`co_await foo()` would run inline on the same thread that `foo()` completed on.

For example, one possible output would have been:
```
bar1 1234
foo1 1234
foo2 3456
bar2 3456
```

However, with the changes to use atomics, it's possible the completion of `foo()`
may race with the suspension of `bar()` and this can, in some cases, mean that the
code after `co_await foo()` might run on the original thread that `bar()` started
executing on.

For example, the following output might now also be possible:
```
bar1 1234
foo1 1234
foo2 3456
bar2 1234
```

For many use-cases this behaviour may not make a difference.
However, for algorithms whose purpose is to transition execution context
this can be problematic.

For example, the `via()` algorithm awaits some Awaitable and then produces it
on the specified scheduler's execution context.
A simplified version of this algorithm is shown below.

```cpp
template<typename Awaitable, typename Scheduler>
task<await_result_t<Awaitable>> via(Awaitable a, Scheduler s)
{
  auto result = co_await std::move(a);
  co_await s.schedule();
  co_return result;
}

task<T> get_value();
void consume(const T&);

task<void> consumer(static_thread_pool::scheduler s)
{
  T result = co_await via(get_value(), s);
  consume(result);
}
```

With the original version the call to `consume()` is always guaranteed to be
executed on the thread-pool, `s`. However, with the revised version
that uses atomics it's possible that `consume()` might either be executed on
a thread associated with the scheduler, `s`, or on whatever thread the
`consumer()` coroutine started execution on.

So how do we solve the stack-overflow problem without the overhead of the
atomic operations, extra branches and the non-deterministic resumption
context?

## Enter "symmetric transfer"!

The paper [P0913R0](https://wg21.link/P0913R0) "Add symmetric coroutine control transfer"
by Gor Nishanov (2018) proposed a solution to this problem by providing a facility
which allows one coroutine to suspend and then resume another coroutine symmetrically
without consuming any additional stack-space.

This paper proposed two key changes:
* Allow returning a `std::coroutine_handle<T>` from `await_suspend()` as a way of
  indicating that execution should be symmetrically transferred to the coroutine
  identified by the returned handle.
* Add a `std::experimental::noop_coroutine()` function that returns a special
  `std::coroutine_handle` that can be returned from `await_suspend()` to suspend the
  current coroutine and return from the call to `.resume()` instead of transferring
  execution to another coroutine.

So what do we mean by "symmetric transfer"?

When you resume a coroutine by calling `.resume()` on it's `std::coroutine_handle`
the caller of `.resume()` remains active on the stack while the resumed coroutine
executes. When this coroutine next suspends and the call to `await_suspend()` for
that suspend-point returns either `void` (indicating unconditional suspend) or
`true` (indicating conditional suspend) then call to `.resume()` will return.

This can be thought of as an "asymmetric transfer" of execution to the coroutine and
behaves just like an ordinary function call. The caller of `.resume()` can be any
function (which may or may not be a coroutine). When that coroutine suspends and
returns either `true` or `void` from `await_suspend()` then execution will return
from the call to `.resume()` and 

Every time we resume a coroutine by calling `.resume()` we create a new stack-frame
for the execution of that coroutine.

However, with "symmetric transfer" we are simply suspending one coroutine and resuming
another coroutine. There is no implicit caller/callee relationship between the two
coroutines - when a coroutine suspends it can transfer execution to any suspended
coroutine (including itself) and does not necessarily have to transfer execution back
to the previous coroutine when it next suspends or completes.

Let's look at what the compiler lowers a `co_await` expression to when the awaiter
makes use of symmetric-transfer:


```cpp
{
  decltype(auto) value = <expr>;
  decltype(auto) awaitable =
      get_awaitable(promise, static_cast<decltype(value)&&>(value));
  decltype(auto) awaiter =
      get_awaiter(static_cast<decltype(awaitable)&&>(awaitable));
  if (!awaiter.await_ready())
  {
    using handle_t = std::coroutine_handle<P>;

    //<suspend-coroutine>

    auto h = awaiter.await_suspend(handle_t::from_promise(p));
    h.resume();
    //<return-to-caller-or-resumer>
    
    //<resume-point>
  }

  return awaiter.await_resume();
}
```

Let's zoom in on the key part that differs from other `co_await` forms:

```cpp
auto h = awaiter.await_suspend(handle_t::from_promise(p));
h.resume();
//<return-to-caller-or-resumer>
```

Once the coroutine state-machine is lowered (a topic for another post),
the `<return-to-caller-or-resumer>` part basically becomes a `return;` statement
which causes the call to `.resume()` that last resumed the coroutine to return
to its caller.

This means that we have the situation where we have a call to another function with
the same signature, `std::coroutine_handle::resume()`, followed by a `return;` from the
current function which is itself the body of a `std::coroutine_handle::resume()` call.

Some compilers, when optimisations are enabled, are able to apply an optimisation
that turns calls to other functions the tail-position (ie. just before returning)
into tail-calls as long as some conditions are met.

It just so happens that this kind of tail-call optimisation is exactly the kind
of thing we want to be able to do to avoid the stack-overflow problem we were
encountering before. But instead of being at the mercy of the optimiser as to
whether or not the tail-call transformation is perfromed, we want to be able to
guarantee that the tail-call transformation occurs, even when optimisations are
not enabled.

But first let's dig into what we mean by tail-calls.

### Tail-calls

A tail-call is one where the current stack-frame is popped before the call and
the current function's return address becomes the return-address for the callee.
ie. the callee will return directly the the caller of this function.

On X86/X64 architectures this generally means that the compiler will generate
code that first pops the current stack-frame and then uses a `jmp` instruction
to jump to the called function's entry-point instead of using a `call` instruction
and then popping the current stack-frame after the `call` returns.

This optimisation is generally only possible to do in limited circumstances, however.

In particular, it requires that:
* the calling convention supports tail-calls and is the same for the caller and callee;
* the return-type is the same;
* there are no non-trivial destructors that need to be run after the call before returning to the caller; and
* the call is not inside a try/catch block.

The shape of the symmetric-transfer form of `co_await` has actually been designed specifically
to allow coroutines to satisfy all of these requirements. Let's look at them individually.

**Calling convention**
When the compiler lowers a coroutine into machine code it actually splits
the coroutine up into two parts: the ramp (which allocates and initialises the coroutine frame)
and the body (which contains the state-machine for the user-authored coroutine body).

The function signature of the coroutine (and thus any user-specified calling-convention)
affects only the ramp part, whereas the body part is under the control of the compiler
and is never directly called by any user-code - only by the ramp function and by
`std::coroutine_handle::resume()`.

The calling-convention of the coroutine body part is not user-visible and is
entirely up to the compiler and thus it can choose an appropriate calling convention
that supports tail-calls and that is used by all coroutine bodies.

**Return type is the same**
The return-type for both the source and target coroutine's `.resume()` method is `void`
so this requirement is trivially satisfied.

**No non-trivial destructors**
When performing a tail-call we need to be able to free the current stack-frame before
calling the target function and this requires the lifetime of all stack-allocated
objects to have ended prior to the call.

Normally, this would be problematic as soon as there are any objects with non-trivial
destructors in-scope as the lifetime of those objects would not yet have ended and
those objects would have been allocated on the stack.

However, when a coroutine suspends it does so without exiting any scopes and the
way it achieves this is by placing any objects whose lifetime spans a suspend-point
in the coroutine frame rather than allocating them on the stack.

Local variables with lifetimes that do not span a suspend-point may be allocated on
the stack, but the lifetime of these objects will have already ended and their
destructors will have been called before the coroutine next suspends.

Thus there should be no non-trivial destructors for stack-allocated objects that
need to be run after the return of the tail-call.

**Call not inside a try/catch block**
This one is a little tricker as within every coroutine there is an implicit try/catch
block that encloses the user-authored body of the coroutine.

From the specification, we see that the coroutine is defined as:

```cpp
{
  promise_type promise;
  co_await promise.initial_suspend();
  try { F; }
  catch (...) { promise.unhandled_exception(); }
final_suspend:
  co_await promise.final_suspend();
}
```

Where `F` is the user-authored part of the coroutine body.

Thus every user-authored `co_await` expression (other than initial/final_suspend) exists
within the context of a try/catch block.

However, implementations work around this by actually executing the call to `.resume()`
_outside_ of the context of the try-block.

I hope to be able to go into this aspect in more detail in another blog post that goes into
the details of the lowering of a coroutine to machine-code (this post is already long enough).

> Note, however, that the current wording in the C++ specification is not clear on requiring
> implementations to do this and it is only a non-normative note that hints that this is something
> that might be required. Hopefully we'll be able to fix the specification in the future. 

So we see that coroutines performing a symmetric-transfer generally satisfy all of the requirements
for being able to perform a tail-call. The compiler guarantees that this will always be a tail-call,
regardless of whether optimisations are enabled or not.

This means that by using the `std::coroutine_handle`-returning flavour of `await_suspend()` we can
suspend the current coroutine and transfer execution to another coroutine without consuming
extra stack-space.

This allows us to write coroutines that mutually and recursively resume each other to an
arbitrary depth without fear of overflowing the stack.

This is exactly what we need to fix our `task` implementation.

## `task` revisited

So with the new "symmetric transfer" capability under our belt let's go back and fix
our `task` type implementation.

To do this we need to make changes to the two `await_suspend()` methods in our implementation:
* First so that when we await the task that we perform a symmetric-transfer to resume the task's coroutine.
* Second so that when the task's coroutine completes that it performs a symmetric transfer to resume the awaiting coroutine.

To address the await direction we need to change the `task::awaiter` method from this:

```cpp
void task::awaiter::await_suspend(
    std::coroutine_handle<> continuation) noexcept {
  // Store the continuation in the task's promise so that the final_suspend()
  // knows to resume this coroutine when the task completes.
  coro_.promise().continuation = continuation;

  // Then we resume the task's coroutine, which is currently suspended
  // at the initial-suspend-point (ie. at the open curly brace).
  coro_.resume();
}
```
to this:

```cpp
std::coroutine_handle<> task::awaiter::await_suspend(
    std::coroutine_handle<> continuation) noexcept {
  // Store the continuation in the task's promise so that the final_suspend()
  // knows to resume this coroutine when the task completes.
  coro_.promise().continuation = continuation;

  // Then we tail-resume the task's coroutine, which is currently suspended
  // at the initial-suspend-point (ie. at the open curly brace), by returning
  // its handle from await_suspend().
  return coro_;
}
```

And to address the return-path we need to update the `task::promise_type::final_awaiter` method from this:

```cpp
void task::promise_type::final_awaiter::await_suspend(
    std::coroutine_handle<promise_type> h) noexcept {
  // The coroutine is now suspended at the final-suspend point.
  // Lookup its continuation in the promise and resume it.
  h.promise().continuation.resume();
}
```
to this:

```cpp
std::coroutine_handle<> task::promise_type::final_awaiter::await_suspend(
    std::coroutine_handle<promise_type> h) noexcept {
  // The coroutine is now suspended at the final-suspend point.
  // Lookup its continuation in the promise and resume it symmetrically.
  return h.promise().continuation;
}
```

And now we have a `task` implementation that doesn't suffer from the stack-overflow problem that the
`void`-returning `await_suspend` flavour had and that doesn't have the non-deterministic resumption
context problem of the `bool`-returning `await_suspend` flavour had.


### Visualising the stack

Let's now go back and have a look at our original example:

```cpp
task completes_synchronously() {
  co_return;
}

task loop_synchronously(int count) {
  for (int i = 0; i < count; ++i) {
    co_await completes_synchronously();
  }
}
```

When the `loop_synchronously()` coroutine first starts executing it will be because
some other coroutine `co_await`ed the `task` returned. This will have been launched
by symmetric transfer from some other coroutine, which would have been resumed by
a call to `std::coroutine_handle::resume()`.

Thus the stack will look something like this when `loop_synchronously()` starts:
```
           Stack                                                Heap
+---------------------------+  <-- top of stack   +--------------------------+
| loop_synchronously$resume | active coroutine -> | loop_synchronously frame |
+---------------------------+                     | +----------------------+ |
| coroutine_handle::resume  |                     | | task::promise        | |
+---------------------------+                     | | - continuation --.   | |
|     ...                   |                     | +------------------|---+ |
+---------------------------+                     | ...                |     |
                                                  +--------------------|-----+
                                                                       V
                                                  +--------------------------+
                                                  | awaiting_coroutine frame |
                                                  |                          |
                                                  +--------------------------+
```

Now, when it executes `co_await completes_synchronously()` it will perform a symmetric
transfer to `completes_synchronously` coroutine.

It does this by:
* calling the `task::operator co_await()` which then returns the `task::awaiter` object
* then suspends and calls `task::awaiter::await_suspend()` which then returns the `coroutine_handle` of the `completes_synchronously` coroutine.
* then performs a tail-call / jump to `completes_synchronously` coroutine.
  This pops the `loop_synchronously` frame before activing the `completes_synchronously` frame.

If we now look at the stack just after `completes_synchronously` is resumed it will now
look like this:
```
              Stack                                          Heap
                                            .-> +--------------------------+ <-.
                                            |   | completes_synchronously  |   |
                                            |   | frame                    |   |
                                            |   | +----------------------+ |   |
                                            |   | | task::promise        | |   |
                                            |   | | - continuation --.   | |   |
                                            |   | +------------------|---+ |   |
                                            `-, +--------------------|-----+   |
                                              |                      V         |
+-------------------------------+ <-- top of  | +--------------------------+   |
| completes_synchronously$resume|     stack   | | loop_synchronously frame |   |
+-------------------------------+ active -----' | +----------------------+ |   |
| coroutine_handle::resume      | coroutine     | | task::promise        | |   |
+-------------------------------+               | | - continuation --.   | |   |
|     ...                       |               | +------------------|---+ |   |
+-------------------------------+               | task temporary     |     |   |
                                                | - coro_       -----|---------`
                                                +--------------------|-----+
                                                                     V
                                                +--------------------------+
                                                | awaiting_coroutine frame |
                                                |                          |
                                                +--------------------------+
```

Note that the number of stack-frames has not grown here.

After the `completes_synchronously` coroutine completes and execution reaches the
closing curly brace it will evaluate `co_await promise.final_suspend()`.

This will suspend the coroutine and call `final_awaiter::await_suspend()`
which return the continuation's `std::coroutine_handle` (ie. the handle that
points to the `loop_synchronously` coroutine). This will then do a symmetric
transfer/tail-call to resume the `loop_synchronously` coroutine.

If we look at the stack just after `loop_synchronously` is resumed then it
will look something like this:
```
           Stack                                                   Heap
                                                   +--------------------------+ <-.
                                                   | completes_synchronously  |   |
                                                   | frame                    |   |
                                                   | +----------------------+ |   |
                                                   | | task::promise        | |   |
                                                   | | - continuation --.   | |   |
                                                   | +------------------|---+ |   |
                                                   +--------------------|-----+   |
                                                                        V         |
+----------------------------+  <-- top of stack   +--------------------------+   |
| loop_synchronously$resume  | active coroutine -> | loop_synchronously frame |   |
+----------------------------+                     | +----------------------+ |   |
| coroutine_handle::resume() |                     | | task::promise        | |   |
+----------------------------+                     | | - continuation --.   | |   |
|     ...                    |                     | +------------------|---+ |   |
+----------------------------+                     | task temporary     |     |   |
                                                   | - coro_       -----|---------`
                                                   +--------------------|-----+
                                                                        V
                                                   +--------------------------+
                                                   | awaiting_coroutine frame |
                                                   |                          |
                                                   +--------------------------+
```

The first thing the `loop_synchronously` coroutine is going to do once resumed is to
call the destructor of the temporary `task` that was returned from the call to
`completes_synchronously` when execution reaches the semicolon.
This will destroy the coroutine-frame, freeing its memory
and leaving us with the following sitution:
```
           Stack                                                   Heap
+---------------------------+  <-- top of stack   +--------------------------+
| loop_synchronously$resume | active coroutine -> | loop_synchronously frame |
+---------------------------+                     | +----------------------+ |
| coroutine_handle::resume  |                     | | task::promise        | |
+---------------------------+                     | | - continuation --.   | |
|     ...                   |                     | +------------------|---+ |
+---------------------------+                     | ...                |     |
                                                  +--------------------|-----+
                                                                       V
                                                  +--------------------------+
                                                  | awaiting_coroutine frame |
                                                  |                          |
                                                  +--------------------------+
```

We are now back to executing the `loop_synchronously` coroutine and we now have
the same number of stack-frames and coroutine-frames as we started, and will do
so each time we go around the loop.

Thus we can perform as many iterations of the loop as we want and will only use
a constant amount of storage space.

For a full example of the symmetric-transfer version of the `task` type see the
following Compiler Explorer link: [https://godbolt.org/z/9baieF](https://godbolt.org/z/9baieF).

## Symmetric Transfer as the Universal Form of await_suspend

Now that we see the power and importance of the symmetric-transfer form of the
awaitable concept, I want to show you that this form is actually the universal
form, which can theoretically replace the `void` and `bool`-returning forms of
`await_suspend()`.

But first we need to look at the other piece that the [P0913R0](https://wg21.link/P0913R0)
proposal added to the coroutines design: `std::noop_coroutine()`.

### Terminating the recursion

With the symmetric-transfer form of coroutines, every time the coroutine suspends
it symmetrically resumes another coroutine. This is great as long as you have another
coroutine to resume, but sometimes we don't have another coroutine to execute and
just need to suspend and let execution return to the caller of `std::coroutine_handle::resume()`.

Both the `void`-returning and `bool`-returning flavours of `await_suspend()` allow
a coroutine to suspend and return from `std::coroutine_handle::resume()`, so how do we do
that with the symmetric-transfer flavour?

The answer is by using the special builtin `std::coroutine_handle`, called the
"noop coroutine handle" which is produced by the function `std::noop_coroutine()`.

The "noop coroutine handle" is named as such because its `.resume()` implementation
is such that it just immediately returns. i.e. resuming the coroutine is a no-op.
Typically its implementation contains a single `ret` instruction.

If the `await_suspend()` method returns the `std::noop_coroutine()` handle then
instead of transferring execution to the next coroutine, it transfers execution
back to the caller of `std::coroutine_handle::resume()`.

### Representing the other flavours of `await_suspend()`

With this information in-hand we can now show how to represent the other flavours
of `await_suspend()` using the symmetric-transfer form.

The `void`-returning form

```cpp
void my_awaiter::await_suspend(std::coroutine_handle<> h) {
  this->coro = h;
  enqueue(this);
}
```
can also be written using both the `bool`-returning form:

```cpp
bool my_awaiter::await_suspend(std::coroutine_handle<> h) {
  this->coro = h;
  enqueue(this);
  return true;
}
```
and can be written using the symmetric-transfer form:

```cpp
std::noop_coroutine_handle my_awaiter::await_suspend(
    std::coroutine_handle<> h) {
  this->coro = h;
  enqueue(this);
  return std::noop_coroutine();
}
```

The `bool`-returning form:

```cpp
bool my_awaiter::await_suspend(std::coroutine_handle<> h) {
  this->coro = h;
  if (try_start(this)) {
    // Operation will complete asynchronously.
    // Return true to transfer execution to caller of
    // coroutine_handle::resume().
    return true;
  }

  // Operation completed synchronously.
  // Return false to immediately resume the current coroutine.
  return false;
}
```
can also be written using the symmetric-transfer form:

```cpp
std::coroutine_handle<> my_awaiter::await_suspend(std::coroutine_handle<> h) {
  this->coro = h;
  if (try_start(this)) {
    // Operation will complete asynchronously.
    // Return std::noop_coroutine() to transfer execution to caller of
    // coroutine_handle::resume().
    return std::noop_coroutine();
  }

  // Operation completed synchronously.
  // Return current coroutine's handle to immediately resume
  // the current coroutine.
  return h;
}
```

### Why have all three flavours?

So why do we still have the `void` and `bool`-returning flavours of `await_suspend()`
when we have the symmetric-transfer flavour?

The reason is partly historical, partly pragmatic and partly performance.

The `void`-returning version could be entirely replaced by returning the `std::noop_coroutine_handle`
type from `await_suspend()` as this would be an equivalent signal to the compiler that the coroutine
is unconditionally transfering execution to the caller of `std::coroutine_handle::resume()`.

That it was kept was, IMO, partly because it was already in-use prior to the introduction
of symmetric-transfer and partly because the `void`-form results in less-code/less-typing
for the unconditional suspend case.

The `bool`-returning version, however, can have a slight win in terms of optimisability
in some cases compared to the symmetric-transfer form.

Consider the case where we have a `bool`-returning `await_suspend()` method that is defined
in another translation unit. In this case the compiler can generate code in the awaiting
coroutine that will suspend the current coroutine and then conditionally resume it after
the call to `await_suspend()` returns by just executing the next piece of code. It knows
exactly the piece of code to execute next if `await_suspend()` returns `false`.

With the symmetric-transfer flavour we still need to represent the same outcomes; either
return to the caller/resume or resume the current coroutine.
Instead of returning `true` or `false` we need to return `std::noop_coroutine()` or the
handle to the current coroutine. We can coerce both of these handles into a `std::coroutine_handle<void>`
type and return it.

However, now, because the `await_suspend()` method is defined in another translation unit
the compiler can't see what coroutine the returned handle is referring to and so when it
resumes the coroutine it now has to perform some more expensive indirect calls and possibly
some branches to resume the coroutine, compared to a single branch for the `bool`-returning
case.

Now, it's possible that we might be able to get equivalent performance out of the symmetric
transfer version one day. For example, we could write our code in such a way that `await_suspend()`
is defined inline but calls a `bool`-returning method that is defined out-of-line and then
conditionally returns the appropriate handle.

For example:

```cpp
struct my_awaiter {
  bool await_ready();

  // Compilers should in-theory be able to optimise this to the same
  // as the bool-returning version, but currently don't do this optimisation.
  std::coroutine_handle<> await_suspend(std::coroutine_handle<> h) {
    if (try_start(h)) {
      return std::noop_coroutine();
    } else {
      return h;
    }
  }

  void await_resume();

private:
  // This method is defined out-of-line in a separate translation unit.
  bool try_start(std::coroutine_handle<> h);
}
```

However, current compilers (c. Clang 10) are not currently able to optimise this to
as efficient code as the equivalent `bool`-returning version. Having said that, you're
probably not going to notice the difference unless you're awaiting this in a really tight
loop.


So, for now, the general rule is:
* If you need to unconditionally return to `.resume()` caller, use the `void`-returning flavour.
* If you need to conditionally return to `.resume()` caller or resume current coroutine use the `bool`-returning flavour.
* If you need to resume another coroutine use the symmetric-transfer flavour.

## Rounding out

The new symmetric transfer capability added to coroutines for C++20 makes
it much easier to write coroutines that recursively resume each other without
fear of running into stack-overflow. This capability is key to making efficient
and safe async coroutine types, such as the `task` one presented here.

This ended up being a much longer than expected post on symmetric transfer.
If you made it this far, then thanks for sticking with it! I hope you found it
useful.

In the next post, I'll dive into understanding how the compiler transforms a
coroutine function into a state-machine.

## Thanks

Thanks to Eric Niebler and Corentin Jabot for providing feedback on drafts of this post.

<hr/>

#### <p>原文出处：<a href='https://lewissbaker.github.io/2022/08/27/understanding-the-compiler-transform' target='blank'>Understanding the Compiler Transform</a></p>

## Introduction

Previous blogs in the series on "Understanding C++ Coroutines" talked about the different
kinds of transforms the compiler performs on a coroutine and its `co_await`, `co_yield`
and `co_return` expressions. These posts described how each expression was lowered by
the compiler to calls to various customisation points/methods on user-defined types.

1. [Coroutine Theory](https://lewissbaker.github.io/2017/09/25/coroutine-theory)
2. [C++ Coroutines: Understanding operator co_await](https://lewissbaker.github.io/2017/11/17/understanding-operator-co-await)
3. [C++ Coroutines: Understanding the promise type](https://lewissbaker.github.io/2018/09/05/understanding-the-promise-type)
4. [C++ Coroutines: Understanding Symmetric Transfer](https://lewissbaker.github.io/2020/05/11/understanding_symmetric_transfer)

However, there was one part of these descriptions that may have left you unsatisfied.
The all hand-waved over the concept of a "suspend-point" and said something vague
like "the coroutine suspends here" and "the coroutine resumes here" but didn't really
go into detail about what that actually means or how it might be implemented by the
compiler.

In this post I am going to go a bit deeper to show how all the concepts from
the previous posts come together. I'll show what happens when a coroutine reaches
a suspend-point by walking through the lowering of a coroutine into equivalent
non-coroutine, imperative C++ code.

Note that I am not going to describe exactly how a particular compiler lowers coroutines
into machine code (compilers have extra tricks up their sleeves here), but rather just one
possible lowering of coroutines into portable C++ code.

Warning: This is going to be a fairly deep dive!

## Setting the Scene

For starters, let's assume we have a basic `task` type that acts as both an awaitable
and a coroutine return-type. For the sake of simplicity, let's assume that this coroutine
type allows producing a result of type `int` asynchronously.

In this post we are going to walk through how to lower the following coroutine function
into C++ code that does not contain any of the coroutine keywords `co_await`, `co_return`
so that we can better understand what this means.


```cpp
// Forward declaration of some other function. Its implementation is not relevant.
task f(int x);

// A simple coroutine that we are going to translate to non-C++ code
task g(int x) {
    int fx = co_await f(x);
    co_return fx * fx;
}
```

## Defining the `task` type

To begin, let us first declare the `task` class that we will be working with.

For the purposes of understanding how the coroutine is lowered, we do not need to
know the definitions of the methods for this type. The lowering will just be inserting
calls to them.

The definitions of these methods are not complicated, and I will leave them as an
exercise for the reader as practice for understanding the previous posts.


```cpp
class task {
public:
    struct awaiter;

    class promise_type {
    public:
        promise_type() noexcept;
        ~promise_type();

        struct final_awaiter {
            bool await_ready() noexcept;
            std::coroutine_handle<> await_suspend(
                std::coroutine_handle<promise_type> h) noexcept;
            void await_resume() noexcept;
        };

        task get_return_object() noexcept;
        std::suspend_always initial_suspend() noexcept;
        final_awaiter final_suspend() noexcept;
        void unhandled_exception() noexcept;
        void return_value(int result) noexcept;

    private:
        friend task::awaiter;
        std::coroutine_handle<> continuation_;
        std::variant<std::monostate, int, std::exception_ptr> result_;
    };

    task(task&& t) noexcept;
    ~task();
    task& operator=(task&& t) noexcept;

    struct awaiter {
        explicit awaiter(std::coroutine_handle<promise_type> h) noexcept;
        bool await_ready() noexcept;
        std::coroutine_handle<promise_type> await_suspend(
            std::coroutine_handle<> h) noexcept;
        int await_resume();
    private:
        std::coroutine_handle<promise_type> coro_;
    };

    awaiter operator co_await() && noexcept;

private:
    explicit task(std::coroutine_handle<promise_type> h) noexcept;

    std::coroutine_handle<promise_type> coro_;
};
```

The structure of this task type should be familiar to those that have read the
[C++ Coroutines: Understanding Symmetric Transfer]({{ '/2020/05/11/understanding_symmetric_transfer' | relative_url }}) post.

## Step 1: Determining the promise type


```cpp
task g(int x) {
    int fx = co_await f(x);
    co_return fx * fx;
}
```

When the compiler sees that this function contains one of the three coroutine keywords
(`co_await`, `co_yield` or `co_return`) it starts the coroutine transformation process.

The first step here is determining the `promise_type` to use for this coroutine.

This is determined by substituting the return-type and argument-types of the signature as
template arguments to the `std::coroutine_traits` type.

e.g. For our function, `g`, which has return type `task` and a single argument of type `int`,
the compiler will look this up using `std::coroutine_traits<task, int>::promise_type`.

Let's define an alias so we can refer to this type later:

```cpp
using __g_promise_t = std::coroutine_traits<task, int>::promise_type;
```

**Note: I am using leading double-underscore here to indicate symbols internal to the**
**compiler that the compiler generates. Such symbols are reserved by the implementation**
**and should _not_ be used in your own code.**

Now, as we have not specialised `std::coroutine_traits` this will instantiate the primary template
which just defines the nested `promise_type` as an alias of the nested `promise_type` name of the
return-type. i.e. this should resolve to the type `task::promise_type` in our case.

## Step 2: Creating the coroutine state

A coroutine function needs to preserve the state of the coroutine, parameters and local variables
when it suspends so that they remain available when the coroutine is later resumed.

This state, in C++ standardese, is called the _coroutine state_ and is typically heap allocated.

Let's start by defining a struct for the coroutine-state for the coroutine, `g`.

We don't know what the contents of this type are going to be yet, so let's just 
leave it empty for now.


```cpp
struct __g_state {
  // to be filled out
};
```

The coroutine state contains a number of different things:

* The promise object
* Copies of any function parameters
* Information about the suspend-point that the coroutine is currently suspended at and how to resume/destroy it
* Storage for any local variables / temporaries whose lifetimes span a suspend-point

Let's start by adding storage for the promise object and parameter copies.


```cpp
struct __g_state {
    int x;
    __g_promise_t __promise;

    // to be filled out
};
```

Next we should add a constructor to initialise these data-members.

Recall that the compiler will first attempt to call the promise constructor with lvalue-references to the parameter copies,
if that call is valid, otherwise fall back to calling the default constructor of the promise type.

Let's create a simple helper to assist with this:

```cpp
template<typename Promise, typename... Params>
Promise construct_promise([[maybe_unused]] Params&... params) {
    if constexpr (std::constructible_from<Promise, Params&...>) {
        return Promise(params...);
    } else {
        return Promise();
    }
}
```

Thus the coroutine-state constructor might look something like this:


```cpp
struct __g_state {
    __g_state(int&& x)
    : x(static_cast<int&&>(x))
    , __promise(construct_promise<__g_promise_t>(x))
    {}

    int x;
    __g_promise_t __promise;
    // to be filled out
};
```

Now that we have the beginnings of a type to represent the coroutine-state, let's also start to
stub out the beginnings of the lowered implementation of `g()` by having it heap-allocate
an instance of the `__g_state` type, passing the function parameters so they can be copied/
moved into the coroutine-state.

Some terminology - I use the term "ramp function" to refer to the part of the coroutine
implementation containing the logic that initialises the coroutine state and gets it ready
to start executing the coroutine.
i.e. it is like an on-ramp for entering execution of the coroutine body.


```cpp
task g(int x) {
    auto* state = new __g_state(static_cast<int&&>(x));
    // ... implement rest of the ramp function
}
```

Note that our promise-type does not define its own custom `operator new` overloads,
and so we are just calling global `::operator new` here.

If the promise type _did_ define a custom `operator new` then we'd call that instead of the
global `::operator new`. We would first check whether `operator new` was callable with the
argument list `(size, paramLvalues...)` and if so call it with that argument list. Otherwise,
we'd call it with just the `(size)` argument list. The ability for the `operator new` to get
access to the parameter list of the coroutine function is sometimes called "parameter preview"
and is useful in cases where you want to use an allocator passed as a parameter to allocate
storage for the coroutine-state.

If the compiler found any definition of `__g_promise_t::operator new` then we'd lower to the
following logic instead:

```cpp
template<typename Promise, typename... Args>
void* __promise_allocate(std::size_t size, [[maybe_unused]] Args&... args) {
  if constexpr (requires { Promise::operator new(size, args...); }) {
    return Promise::operator new(size, args...);
  } else {
    return Promise::operator new(size);
  }
}

task g(int x) {
    void* state_mem = __promise_allocate<__g_promise_t>(sizeof(__g_state), x);
    __g_state* state;
    try {
        state = ::new (state_mem) __g_state(static_cast<int&&>(x));
    } catch (...) {
        __g_promise_t::operator delete(state_mem);
        throw;
    }
    // ... implement rest of the ramp function
}
```

Also, this promise-type does not define the `get_return_object_on_allocation_failure()` static
member function. If this function is defined on the promise-type then the allocation here would
instead use the `std::nothrow_t` form of `operator new` and upon returning `nullptr` would then
`return __g_promise_t::get_return_object_on_allocation_failure();`.

i.e. it would look something like this instead:

```cpp
task g(int x) {
    auto* state = ::new (std::nothrow) __g_state(static_cast<int&&>(x));
    if (state == nullptr) {
        return __g_promise_t::get_return_object_on_allocation_failure();
    }
    // ... implement rest of the ramp function
}
```

For simplicity for the rest of the example, we'll just use the simplest form that calls the
global `::operator new` memory allocation function.

## Step 3: Call `get_return_object()`

The next thing the ramp function does is to call the `get_return_object()` method on the promise
object to obtain the return-value of the ramp function.

The return value is stored as a local variable and is returned at the end of the ramp function
(after the other steps have been completed).


```cpp
task g(int x) {
    auto* state = new __g_state(static_cast<int&&>(x));
    decltype(auto) return_value = state->__promise.get_return_object();
    // ... implement rest of ramp function
    return return_value;
}
```

However, now it's possible that the call to `get_return_object()` might throw, and in which
case we want to free the allocated coroutine state. So for good measure, let's give ownership
of the state to a `std::unique_ptr` so that it's freed in case a subsequent operation throws
an exception:


```cpp
task g(int x) {
    std::unique_ptr<__g_state> state(new __g_state(static_cast<int&&>(x)));
    decltype(auto) return_value = state->__promise.get_return_object();
    // ... implement rest of ramp function
    return return_value;
}
```

## Step 4: The initial-suspend point

The next thing the ramp function does after calling `get_return_object()` is to start executing
the body of the coroutine, and the first thing to execute in the body of the coroutine is the
initial suspend-point. i.e. we evaluate `co_await promise.initial_suspend()`.

Now, ideally we'd just treat the coroutine as initially suspended and then just implement the
launching of the coroutine as a resumption of the initially suspended coroutine. However, the
specification of the initial-suspend point has a few quirks with regards to how it handles
exceptions and the lifetime of the coroutine state. This was a late tweak to the semantics
of the initial-suspend point just before C++20 was released to fix some perceived issues here.

Within the evaluation of the initial-suspend-point, if an exception is thrown either from:
* the call to `initial_suspend()`,
* the call to `operator co_await()` on the returned awaitable (if one is defined),
* the call to `await_ready()` on the awaiter, or
* the call to `await_suspend()` on the awaiter

Then the exception propagates back to the caller of the ramp function and the coroutine state is
automatically destroyed.

If an exception is thrown either from:
* the call to `await_resume()`,
* the destructor of the object returned from `operator co_await()` (if applicable), or
* the destructor of the object returned from `initial_suspend()`

Then this exception is caught by the coroutine body and `promise.unhandled_exception()` is called.

This means we need to be a bit careful how we handle transforming this part, as some parts will
need to live in the ramp function and other parts in the coroutine body.

Also, since the objects returned from `initial_suspend()` and (optionally) `operator co_await()`
will have lifetimes that span a suspend-point (they are created before the point at which the
coroutine suspends and are destroyed after it resumes) the storage for those objects will need to be
placed in the coroutine state.

In our particular case, the type returned from `initial_suspend()` is `std::suspend_always`, which
happens to be an empty, trivially constructible type. However, logically we still need to store an
instance of this type in the coroutine state, so we'll add storage for it anyway just to show how
this works.

This object will only be constructed at the point that we call `initial_suspend()`, so we need to
add a data-member of a certain type that that allows us to explicitly control its lifetime.

To support this, let's first define a helper class, `manual_lifetime` that is trivally constructible
and trivially destructible but that lets us explicitly construct/destruct the value stored there
when we need to.


```cpp
template<typename T>
struct manual_lifetime {
    manual_lifetime() noexcept = default;
    ~manual_lifetime() = default;

    // Not copyable/movable
    manual_lifetime(const manual_lifetime&) = delete;
    manual_lifetime(manual_lifetime&&) = delete;
    manual_lifetime& operator=(const manual_lifetime&) = delete;
    manual_lifetime& operator=(manual_lifetime&&) = delete;

    template<typename Factory>
        requires
            std::invocable<Factory&> &&
            std::same_as<std::invoke_result_t<Factory&>, T>
    T& construct_from(Factory factory) noexcept(std::is_nothrow_invocable_v<Factory&>) {
        return *::new (static_cast<void*>(&storage)) T(factory());
    }

    void destroy() noexcept(std::is_nothrow_destructible_v<T>) {
        std::destroy_at(std::launder(reinterpret_cast<T*>(&storage)));
    }

    T& get() & noexcept {
        return *std::launder(reinterpret_cast<T*>(&storage));
    }

private:
    alignas(T) std::byte storage[sizeof(T)];
};
```

Note that the `construct_from()` method is designed to take a lambda here rather than
taking the constructor arguments. This allows us to make use of the guaranteed copy-elision
when initialising a variable with the result of a function-call to construct the object
in-place. If it were instead to take the constructor arguments then we'd end up calling
an extra move-constructor unnecessarily.

Now we can declare a data-member for the temporary returned by `promise.initial_suspend()`
using this `manual_lifetime` structure.


```cpp
struct __g_state {
    __g_state(int&& x);

    int x;
    __g_promise_t __promise;
    manual_lifetime<std::suspend_always> __tmp1;
    // to be filled out
};
```

The `std::suspend_always` type does not have an `operator co_await()` so we do not need to
reserve storage for an extra temporary for the result of that call here.

Once we've constructed this object by calling `intial_suspend()`, we then need to call the
trio of methods to implement the `co_await` expression: `await_ready()`, `await_suspend()`
and `await_resume()`.

When invoking `await_suspend()` we need to pass it a handle to the current coroutine.
For now we can just call `std::coroutine_handle<__g_promise_t>::from_promise()` and pass
a reference to that promise. We'll look at the internals of what this does a little later.

Also, the result of the call to `.await_suspend(handle)` has type `void` and so we do not
need to consider whether to resume this coroutine or another coroutine after calling
`await_suspend()` like we do for the `bool` and `coroutine_handle`-returning flavours.

Finally, as all of the method invocations on the `std::suspend_always` awaiter are declared
`noexcept`, we don't need to worry about exceptions. If they were potentially throwing then
we'd need to add extra code to make sure that the temporary `std::suspend_always` object
was destroyed before the exception propagated out of the ramp function.

Once we get to the point where `await_suspend()` has returned successfully or
where we are about to start executing the coroutine body we enter the phase where we
no longer need to automatically destroy the coroutine-state if an exception is thrown.
So we can call `release()` on the `std::unique_ptr` owning the coroutine state to
prevent it from being destroyed when we return from the function.

So now we can implement the first part of the initial-suspend expression as follows:


```cpp
task g(int x) {
    std::unique_ptr<__g_state> state(new __g_state(static_cast<int&&>(x)));
    decltype(auto) return_value = state->__promise.get_return_object();

    state->__tmp1.construct_from([&]() -> decltype(auto) {
        return state->__promise.initial_suspend();
    });
    if (!state->__tmp1.get().await_ready()) {
        //
        // ... suspend-coroutine here
        //
        state->__tmp1.get().await_suspend(
            std::coroutine_handle<__g_promise_t>::from_promise(state->__promise));

        state.release();

        // fall through to return statement below.
    } else {
        // Coroutine did not suspend.

        state.release();

        //
        // ... start executing the coroutine body
        //
    }
    return __return_val;
}
```

The call to `await_resume()` and the destructor of `__tmp1` will appear in the coroutine
body and so they do not appear in the ramp function.

We now have a (mostly) functional evaluation of the initial-suspend point, but we still
have a couple of TODO's in the code for this ramp function. To be able to resolve these we
will first need to take a detour to look at the strategy for suspending a coroutine and later
resuming it.

## Step 5: Recording the suspend-point

When a coroutine suspends, it needs to make sure it resumes at the same point in the
control flow that it suspended at.

It also needs to keep track of which objects with automatic-storage duration are alive
at each suspend-point so that it knows what needs to be destroyed if the coroutine is
destroyed instead of being resumed.

One way to implement this is to assign each suspend-point in the coroutine a unique number
and then store this in an integer data-member of the coroutine state.

Then whenever a coroutine suspends, it writes the number of the suspend-point at which it is
suspending to the coroutine state, and when it is resumed/destroyed we then inspect
this integer to see which suspend point it was suspended at.

Note that this is not the only way of storing the suspend-point in the coroutine state,
however all 3 major compilers (MSVC, Clang, GCC) use this approach as the time this post
was authored (c. 2022).
Another potential solution is to use separate resume/destroy function-pointers for each
suspend-point, although we will not be exploring this strategy in this post.

So let's extend our coroutine-state with an integer data-member to store the suspend-point
index and initialise it to zero (we'll always use this as the value for the initial-suspend
point).


```cpp
struct __g_state {
    __g_state(int&& x);

    int x;
    __g_promise_t __promise;
    int __suspend_point = 0;  // <-- add the suspend-point index
    manual_lifetime<std::suspend_always> __tmp1;
    // to be filled out
};
```

## Step 6: Implementing `coroutine_handle::resume()` and `coroutine_handle::destroy()`

When a coroutine is resumed by calling `coroutine_handle::resume()` we need this to end up
invoking some function that implements the rest of the body of the suspended coroutine.
The invoked body function can then look up the suspend-point index and jump to the appropriate
point in the control-flow.

We also need to implement the `coroutine_handle::destroy()` function so that it invokes
the appropriate logic to destroy any in-scope objects at the current suspend-point and
we need to implement `coroutine_handle::done()` to query whether the current suspend-point
is a final-suspend-point.

The interface of the `coroutine_handle` methods does not know about the concrete coroutine
state type - the `coroutine_handle<void>` type can point to _any_ coroutine instance.
This means we need to implement them in a way that type-erases the coroutine state type.

We can do this by storing function-pointers to the resume/destroy functions for that coroutine
type and having `coroutine_handle::resume/destroy()` invoke those function-pointers.

The `coroutine_handle` type also needs to be able to be converted to/from a `void*` using the
`coroutine_handle::address()` and `coroutine_handle::from_address()` methods.

Furthermore, the coroutine can be resumed/destroyed from _any_ handle to that coroutine -
not just the handle that was passed to the most recent `await_suspend()` call.

These requirements lead us to define the `coroutine_handle` type so that it only contains a
pointer to the coroutine-state and that we store the resume/destroy function pointers as
data-members of the coroutine state, rather than, say, storing the resume/destroy function
pointers in the `coroutine_handle`.

Also, since we need the `coroutine_handle` to be able to point to an arbitrary coroutine-state
object we need the layout of the function-pointer data-members to be consistent across all
coroutine-state types.

One straight forward way of doing this is having each coroutine-state type inherit from some
base-class that contains these data-members.

e.g. We can define the following type as the base-class for all coroutine-state types

```cpp
struct __coroutine_state {
    using __resume_fn = void(__coroutine_state*);
    using __destroy_fn = void(__coroutine_state*);

    __resume_fn* __resume;
    __destroy_fn* __destroy;
};
```

Then the `coroutine_handle::resume()` method can simply call `__resume()`, passing a
pointer to the `__coroutine_state` object.
Similarly, we can do this for the `coroutine_handle::destroy()` method and the `__destroy` function-pointer.

For the `coroutine_handle::done()` method, we choose to treat a null `__resume` function pointer
as an indication that we are at a final-suspend-point. This is convenient since the final suspend
point does not support `resume()`, only `destroy()`. If someone tries to call `resume()` on a
coroutine suspended at the final-suspend-point (which has undefined-behaviour) then they end up
calling a null function pointer which should fail pretty quickly and point out their error.

Given this, we can implement the `coroutine_handle<void>` type as follows:

```cpp
namespace std
{
    template<typename Promise = void>
    class coroutine_handle;

    template<>
    class coroutine_handle<void> {
    public:
        coroutine_handle() noexcept = default;
        coroutine_handle(const coroutine_handle&) noexcept = default;
        coroutine_handle& operator=(const coroutine_handle&) noexcept = default;

        void* address() const {
            return static_cast<void*>(state_);
        }

        static coroutine_handle from_address(void* ptr) {
            coroutine_handle h;
            h.state_ = static_cast<__coroutine_state*>(ptr);
            return h;
        }

        explicit operator bool() noexcept {
            return state_ != nullptr;
        }
        
        friend bool operator==(coroutine_handle a, coroutine_handle b) noexcept {
            return a.state_ == b.state_;
        }

        void resume() const {
            state_->__resume(state_);
        }
        void destroy() const {
            state_->__destroy(state_);
        }

        bool done() const {
            return state_->__resume == nullptr;
        }

    private:
        __coroutine_state* state_ = nullptr;
    };
}
```

## Step 7: Implementing `coroutine_handle<Promise>::promise()` and `from_promise()`

For the more general `coroutine_handle<Promise>` specialisation, most of the implementations
can just reuse the `coroutine_handle<void>` implementations. However, we also need to be able
to get access to the promise object of the coroutine-state, returned from the `promise()` method,
and also construct a `coroutine_handle` from a reference to the promise-object.

However, again we cannot simply point to the concrete coroutine state type since the
`coroutine_handle<Promise>` type must be able to refer to any coroutine-state whose
promise-type is `Promise`.

We need to define a new coroutine-state base-class that inherits from `__coroutine_state`
and which contains the promise object so we can then define all coroutine-state types that use
a particular promise-type to inherit from this base-class.


```cpp
template<typename Promise>
struct __coroutine_state_with_promise : __coroutine_state {
    __coroutine_state_with_promise() noexcept {}
    ~__coroutine_state_with_promise() {}

    union {
        Promise __promise;
    };
};
```

You might be wondering why we declare the `__promise` member inside an anonymous union here...

The reason for this is that the derived class created for a particular coroutine function
contains the definition for the argument-copy data-members. Data members from derived classes
are by default initialised after data-members of any base-classes, so declaring the promise
object as a normal data-member would mean that the promise object was constructed before the
argument-copy data-members.

However, we need the constructor of the promise to be called _after_ the constructor of the
argument-copies - references to the argument-copies might need to be passed to the promise
constructor.

So we reserve storage for the promise object in this base-class so that it has a consistent
offset from the start of the coroutine-state, but leave the derived class responsible for
calling the constructor/destructor at the appropriate point after the argument-copies have
been initialised. Declaring the `__promise` as a union-member provides this control.

Let's update the `__g_state` class to now inherit from this new base-class.


```cpp
struct __g_state : __coroutine_state_with_promise<__g_promise_t> {
    __g_state(int&& __x)
    : x(static_cast<int&&>(__x)) {
        // Use placement-new to initialise the promise object in the base-class
        ::new ((void*)std::addressof(this->__promise))
            __g_promise_t(construct_promise<__g_promise_t>(x));
    }

    ~__g_state() {
        // Also need to manually call the promise destructor before the
        // argument objects are destroyed.
        this->__promise.~__g_promise_t();
    }

    int __suspend_point = 0;
    int x;
    manual_lifetime<std::suspend_always> __tmp1;
    // to be filled out
};
```

Now that we have defined the promise-base-class we can now implement the `std::coroutine_handle<Promise>` class template.

Most of the implementation should be largely identical to the equivalent methods in `coroutine_handle<void>`
except with a `__coroutine_state_with_promise<Promise>` pointer instead of `__coroutine_state` pointer.

The only new part is the addition of the `promise()` and `from_promise()` functions.

* The `promise()` method is straight-forward - it just returns a reference to the `__promise` member of the coroutine-state.
* The `from_promise()` method requires us to calculate the address of the coroutine-state from the
  address of the promise object. We can do this by just subtracting the offset of the `__promise` member
  from the address of the promise object.

Implementation of `coroutine_handle<Promise>`:

```cpp
namespace std
{
    template<typename Promise>
    class coroutine_handle {
        using state_t = __coroutine_state_with_promise<Promise>;
    public:
        coroutine_handle() noexcept = default;
        coroutine_handle(const coroutine_handle&) noexcept = default;
        coroutine_handle& operator=(const coroutine_handle&) noexcept = default;

        operator coroutine_handle<void>() const noexcept {
            return coroutine_handle<void>::from_address(address());
        }

        explicit operator bool() const noexcept {
            return state_ != nullptr;
        }

        friend bool operator==(coroutine_handle a, coroutine_handle b) noexcept {
            return a.state_ == b.state_;
        }

        void* address() const {
            return static_cast<void*>(static_cast<__coroutine_state*>(state_));
        }

        static coroutine_handle from_address(void* ptr) {
            coroutine_handle h;
            h.state_ = static_cast<state_t*>(static_cast<__coroutine_state*>(ptr));
            return h;
        }

        Promise& promise() const {
            return state_->__promise;
        }

        static coroutine_handle from_promise(Promise& promise) {
            coroutine_handle h;

            // We know the address of the __promise member, so calculate the
            // address of the coroutine-state by subtracting the offset of
            // the __promise field from this address.
            h.state_ = reinterpret_cast<state_t*>(
                reinterpret_cast<unsigned char*>(std::addressof(promise)) -
                offsetof(state_t, __promise));

            return h;
        }

        // Define these in terms of their `coroutine_handle<void>` implementations

        void resume() const {
            static_cast<coroutine_handle<void>>(*this).resume();
        }

        void destroy() const {
            static_cast<coroutine_handle<void>>(*this).destroy();
        }

        bool done() const {
            return static_cast<coroutine_handle<void>>(*this).done();
        }

    private:
        state_t* state_;
    };
}
```

Now that we have defined the mechanism by which coroutines are resumed, we can now
return to our "ramp" function and update it to initialise the new function-pointer
data-members we've added to the coroutine-state.

## Step 8: The beginnings of the coroutine body

Let's now forward-declare resume/destroy functions of the right signature and
update the `__g_state` constructor to initialise the coroutine-state
so that the resume/destroy function-pointers point at them:


```cpp
void __g_resume(__coroutine_state* s);
void __g_destroy(__coroutine_state* s);

struct __g_state : __coroutine_state_with_promise<__g_promise_t> {
    __g_state(int&& __x)
    : x(static_cast<int&&>(__x)) {
        // Initialise the function-pointers used by coroutine_handle methods.
        this->__resume = &__g_resume;
        this->__destroy = &__g_destroy;

        // Use placement-new to initialise the promise object in the base-class
        ::new ((void*)std::addressof(this->__promise))
            __g_promise_t(construct_promise<__g_promise_t>(x));
    }

    // ... rest omitted for brevity
};


task g(int x) {
    std::unique_ptr<__g_state> state(new __g_state(static_cast<int&&>(x)));
    decltype(auto) return_value = state->__promise.get_return_object();

    state->__tmp1.construct_from([&]() -> decltype(auto) {
        return state->__promise.initial_suspend();
    });
    if (!state->__tmp1.get().await_ready()) {
        state->__tmp1.get().await_suspend(
            std::coroutine_handle<__g_promise_t>::from_promise(state->__promise));
        state.release();
        // fall through to return statement below.
    } else {
        // Coroutine did not suspend. Start executing the body immediately.
        __g_resume(state.release());
    }
    return return_value;
}
```

This now completes the ramp function and we can now focus on the resume/destroy functions for `g()`.

Let's start by completing the lowering of the initial-suspend expression.

When `__g_resume()` is called and the `__suspend_point` index is 0 then we need it to
resume by calling `await_resume()` on `__tmp1` and then calling the destructor of `__tmp1`.


```cpp
void __g_resume(__coroutine_state* s) {
    // We know that 's' points to a __g_state.
    auto* state = static_cast<__g_state*>(s);

    // Generate a jump-table to jump to the correct place in the code based
    // on the value of the suspend-point index.
    switch (state->__suspend_point) {
    case 0: goto suspend_point_0;
    default: std::unreachable();
    }

suspend_point_0:
    state->__tmp1.get().await_resume();
    state->__tmp1.destroy();

    // TODO: Implement rest of coroutine body.
    //
    //  int fx = co_await f(x);
    //  co_return fx * fx;
}
```

And when `__g_destroy()` is called and the `__suspend_point` index is 0 then we need it
to just destroy `__tmp1` before then destroying and freeing the coroutine-state.


```cpp
void __g_destroy(__coroutine_state* s) {
    auto* state = static_cast<__g_state*>(s);

    switch (state->__suspend_point) {
    case 0: goto suspend_point_0;
    default: std::unreachable();
    }

suspend_point_0:
    state->__tmp1.destroy();
    goto destroy_state;

    // TODO: Add extra logic for other suspend-points here.

destroy_state:
    delete state;
}
```

## Step 9: Lowering the `co_await` expression

Next, let's take a look at lowering the `co_await f(x)` expression.

First we need to evaluate `f(x)` which returns a temporary `task` object.

As the temporary `task` is not destroyed until the semicolon at the end of the statement and
the statement contains a `co_await` expression, the lifetime of the `task` therefore spans a
suspend-point and so it must be stored in the coroutine-state.

When the `co_await` expression is then evaluated on this temporary `task`, we need to call
the `operator co_await()` method which returns a temporary `awaiter` object. The lifetime of
this object also spans the suspend-point and so must be stored in the coroutine-state.

Let's add the necessary members to the `__g_state` type:

```cpp
struct __g_state : __coroutine_state_with_promise<__g_promise_t> {
    __g_state(int&& __x);
    ~__g_state();

    int __suspend_point = 0;
    int x;
    manual_lifetime<std::suspend_always> __tmp1;
    manual_lifetime<task> __tmp2;
    manual_lifetime<task::awaiter> __tmp3;
};
```

Then we can update the `__g_resume()` function to initialise these temporaries and then evaluate
the 3 `await_ready`, `await_suspend` and `await_resume` calls that comprise the rest of the
`co_await` expression.

Note that the `task::awaiter::await_suspend()` method returns a coroutine-handle so we need to
generate code that resumes the returned handle.

We also need to update the suspend-point index before calling `await_suspend()` (we'll use the
index 1 for this suspend-point) and then add an extra entry to the jump-table to ensure that
we resume back at the right spot.


```cpp
void __g_resume(__coroutine_state* s) {
    // We know that 's' points to a __g_state.
    auto* state = static_cast<__g_state*>(s);

    // Generate a jump-table to jump to the correct place in the code based
    // on the value of the suspend-point index.
    switch (state->__suspend_point) {
    case 0: goto suspend_point_0;
    case 1: goto suspend_point_1; // <-- add new jump-table entry
    default: std::unreachable();
    }

suspend_point_0:
    state->__tmp1.get().await_resume();
    state->__tmp1.destroy();

    //  int fx = co_await f(x);
    state->__tmp2.construct_from([&] {
        return f(state->x);
    });
    state->__tmp3.construct_from([&] {
        return static_cast<task&&>(state->__tmp2.get()).operator co_await();
    });
    if (!state->__tmp3.get().await_ready()) {
        // mark the suspend-point
        state->__suspend_point = 1;

        auto h = state->__tmp3.get().await_suspend(
            std::coroutine_handle<__g_promise_t>::from_promise(state->__promise));
        
        // Resume the returned coroutine-handle before returning.
        h.resume();
        return;
    }

suspend_point_1:
    int fx = state->__tmp3.get().await_resume();
    state->__tmp3.destroy();
    state->__tmp2.destroy();

    // TODO: Implement
    //  co_return fx * fx;
}
```

Note that the `int fx` local variable has a lifetime that does not span a suspend-point and
so it does not need to be stored in the coroutine-state. We can just store it as a normal
local variable in the `__g_resume` function.

We also need to add the necessary entry to the `__g_destroy()` function to handle when
the coroutine is destroyed at this suspend-point.


```cpp
void __g_destroy(__coroutine_state* s) {
    auto* state = static_cast<__g_state*>(s);

    switch (state->__suspend_point) {
    case 0: goto suspend_point_0;
    case 1: goto suspend_point_1; // <-- add new jump-table entry
    default: std::unreachable();
    }

suspend_point_0:
    state->__tmp1.destroy();
    goto destroy_state;

suspend_point_1:
    state->__tmp3.destroy();
    state->__tmp2.destroy();
    goto destroy_state;

    // TODO: Add extra logic for other suspend-points here.

destroy_state:
    delete state;
}
```

So now we have finished implementing the statement:

```cpp
int fx = co_await f(x);
```

However, the function `f(x)` is not marked `noexcept` and so it can potentially throw an exception.
Also, the `awaiter::await_resume()` method is also not marked `noexcept` and can also potentially
throw an exception.

When an exception is thrown from a coroutine-body the compiler generates code to catch the exception
and then invoke `promise.unhandled_exception()` to give the promise an opportunity to do something
with the exception. Let's look at implementing this aspect next.

## Step 10: Implementing `unhandled_exception()`

The specification for coroutine definitions [`[dcl.fct.def.coroutine]`](https://eel.is/c++draft/dcl.fct.def.coroutine)
says that the coroutine behaves as if its function-body were replaced by:


```cpp
{
    promise-type promise promise-constructor-arguments ;
    try {
        co_await promise.initial_suspend() ;
        function-body
    } catch ( ... ) {
        if (!initial-await-resume-called)
            throw ;
        promise.unhandled_exception() ;
    }
final-suspend :
    co_await promise.final_suspend() ;
}
```

We have already handled the `initial-await_resume-called` branch separately in the ramp function,
so we don't need to worry about that here.

Let's adjust the `__g_resume()` function to insert the try/catch block around the body.

Note that we need to be careful to put the `switch` that jumps to the right place inside
the try-block as we are not allowed to enter a try-block using a `goto`.

Also, we need to be careful to call `.resume()` on the coroutine handle returned from
`await_suspend()` outside of the try/catch block. If an exception is thrown from the
call `.resume()` on the returned coroutine then it should not be caught by the current
coroutine, but should instead propagate out of the call to `resume()` that resumed
this coroutine. So we stash the coroutine-handle in a variable declared at the top
of the function and then `goto` a point outside of the try/catch and execute the call
to `.resume()` there.


```cpp
void __g_resume(__coroutine_state* s) {
    auto* state = static_cast<__g_state*>(s);

    std::coroutine_handle<void> coro_to_resume;

    try {
        switch (state->__suspend_point) {
        case 0: goto suspend_point_0;
        case 1: goto suspend_point_1; // <-- add new jump-table entry
        default: std::unreachable();
        }

suspend_point_0:
        state->__tmp1.get().await_resume();
        state->__tmp1.destroy();

        //  int fx = co_await f(x);
        state->__tmp2.construct_from([&] {
            return f(state->x);
        });
        state->__tmp3.construct_from([&] {
            return static_cast<task&&>(state->__tmp2.get()).operator co_await();
        });
        
        if (!state->__tmp3.get().await_ready()) {
            state->__suspend_point = 1;
            coro_to_resume = state->__tmp3.get().await_suspend(
                std::coroutine_handle<__g_promise_t>::from_promise(state->__promise));
            goto resume_coro;
        }

suspend_point_1:
        int fx = state->__tmp3.get().await_resume();
        state->__tmp3.destroy();
        state->__tmp2.destroy();

        // TODO: Implement
        //  co_return fx * fx;
    } catch (...) {
        state->__promise.unhandled_exception();
        goto final_suspend;
    }

final_suspend:
    // TODO: Implement
    // co_await promise.final_suspend();

resume_coro:
    coro_to_resume.resume();
    return;
}
```

There is a bug in the above code, however. In the case that the `__tmp3.get().await_resume()` call
exits with an exception, we would fail to call the destructors of `__tmp3` and `__tmp2` before
catching the exception.

Note that we cannot simply catch the exception, call the destructors and rethrow the exception
here as this would change the behaviour of those destructors if they were to call
`std::unhandled_exceptions()` since the exception would be "handled". However if the
destructor calls this during exception unwind, then call to `std:::unhandled_exceptions()`
should return non-zero.

We can instead define an RAII helper class to ensure that the destructors get called on scope
exit in the case an exception is thrown.


```cpp
template<typename T>
struct destructor_guard {
    explicit destructor_guard(manual_lifetime<T>& obj) noexcept
    : ptr_(std::addressof(obj))
    {}

    // non-movable
    destructor_guard(destructor_guard&&) = delete;
    destructor_guard& operator=(destructor_guard&&) = delete;

    ~destructor_guard() noexcept(std::is_nothrow_destructible_v<T>) {
        if (ptr_ != nullptr) {
            ptr_->destroy();
        }
    }

    void cancel() noexcept { ptr_ = nullptr; }

private:
    manual_lifetime<T>* ptr_;
};

// Partial specialisation for types that don't need their destructors called.
template<typename T>
    requires std::is_trivially_destructible_v<T>
struct destructor_guard<T> {
    explicit destructor_guard(manual_lifetime<T>&) noexcept {}
    void cancel() noexcept {}
};

// Class-template argument deduction to simplify usage
template<typename T>
destructor_guard(manual_lifetime<T>& obj) -> destructor_guard<T>;
```

Using this utility, we can now use this type to ensure that variables stored in the coroutine-state
are destroyed when an exception is thrown.

Let's also use this class to call the destructors of the existing varibles so that it also calls
their destructors when they naturally go out of scope.


```cpp
void __g_resume(__coroutine_state* s) {
    auto* state = static_cast<__g_state*>(s);

    std::coroutine_handle<void> coro_to_resume;

    try {
        switch (state->__suspend_point) {
        case 0: goto suspend_point_0;
        case 1: goto suspend_point_1; // <-- add new jump-table entry
        default: std::unreachable();
        }

suspend_point_0:
        {
            destructor_guard tmp1_dtor{state->__tmp1};
            state->__tmp1.get().await_resume();
        }

        //  int fx = co_await f(x);
        {
            state->__tmp2.construct_from([&] {
                return f(state->x);
            });
            destructor_guard tmp2_dtor{state->__tmp2};

            state->__tmp3.construct_from([&] {
                return static_cast<task&&>(state->__tmp2.get()).operator co_await();
            });
            destructor_guard tmp3_dtor{state->__tmp3};

            if (!state->__tmp3.get().await_ready()) {
                state->__suspend_point = 1;

                coro_to_resume = state->__tmp3.get().await_suspend(
                    std::coroutine_handle<__g_promise_t>::from_promise(state->__promise));

                // A coroutine suspends without exiting scopes.
                // So cancel the destructor-guards.
                tmp3_dtor.cancel();
                tmp2_dtor.cancel();

                goto resume_coro;
            }

            // Don't exit the scope here.
            //
            // We can't 'goto' a label that enters the scope of a variable with a
            // non-trivial destructor. So we have to exit the scope of the destructor
            // guards here without calling the destructors and then recreate them after
            // the `suspend_point_1` label.
            tmp3_dtor.cancel();
            tmp2_dtor.cancel();
        }

suspend_point_1:
        int fx = [&]() -> decltype(auto) {
            destructor_guard tmp2_dtor{state->__tmp2};
            destructor_guard tmp3_dtor{state->__tmp3};
            return state->__tmp3.get().await_resume();
        }();

        // TODO: Implement
        //  co_return fx * fx;
    } catch (...) {
        state->__promise.unhandled_exception();
        goto final_suspend;
    }

final_suspend:
    // TODO: Implement
    // co_await promise.final_suspend();

resume_coro:
    coro_to_resume.resume();
    return;
}
```

Now our coroutine body will now destroy local variables correctly in the presence of any exceptions and
will correctly call `promise.unhandled_exception()` if those exceptions propagate out of the coroutine
body.

It's worth noting here that there can also be special handling needed for the case where the
`promise.unhandled_exception()` method itself exits with an exception (e.g. if it rethrows
the current exception).

In this case, the coroutine would need to catch the exception, mark the coroutine as suspended
at a final-suspend-point, and then rethrow the exception.

For example: The `__g_resume()` function's catch-block would need to look like this:

```cpp
try {
  // ...
} catch (...) {
    try {
        state->__promise.unhandled_exception();
    } catch (...) {
        state->__suspend_point = 2;
        state->__resume = nullptr; // mark as final-suspend-point
        throw;
    }
}
```
and we'd need to add an extra entry to the `__g_destroy` function's jump table:

```cpp
switch (state->__suspend_point) {
case 0: goto suspend_point_0;
case 1: goto suspend_point_1;
case 2: goto destroy_state; // no variables in scope that need to be destroyed
                            // just destroy the coroutine-state object.
}
```

Note that in this case, the final-suspend-point is not necessarily the same suspend-point as the
final-suspend-point as the `co_await promise.final_suspend()` suspend-point.

This is because the `promise.final_suspend()` suspend-point will often have some extra temporary
objects related to the `co_await` expression which need to be destroyed when `coroutine_handle::destroy()`
is called. Whereas, if `promise.unhandled_exception()` exits with an exception then those temporary
objects will not exist and so won't need to be destroyed by `coroutine_handle::destroy()`.

## Step 11: Implementing `co_return`

The next step is to implement the `co_return fx * fx;` statement.

This is relatively straight-forward compared to some of the previous steps.

The `co_return <expr>` statement gets mapped to:

```cpp
promise.return_value(<expr>);
goto final-suspend-point;
```

So we can simply replace the TODO comment with:

```cpp
state->__promise.return_value(fx * fx);
goto final_suspend;
```

Easy.

## Step 12: Implementing `final_suspend()`

The final TODO in the code is now to implement the `co_await promise.final_suspend()` statement.

The `final_suspend()` method returns a temporary `task::promise_type::final_awaiter` type, which will
need to be stored in the coroutine-state and destroyed in `__g_destroy`.

This type does not have its own `operator co_await()`, so we don't need an additional temporary
object for the result of that call.

Like the `task::awaiter` type, this also uses the coroutine-handle-returning form of
`await_suspend()`. So we need to ensure that we call `resume()` on the returned handle.

If the coroutine does not suspend at the final-suspend-point then the coroutine-state is implicitly
destroyed. So we need to delete the state object if execution reaches the end of the coroutine.

Also, as all of the final-suspend logic is required to be noexcept, we don't need to worry about
exceptions being thrown from any of the sub-expressions here.

Let's first add the data-member to the `__g_state` type.

```cpp
struct __g_state : __coroutine_state_with_promise<__g_promise_t> {
    __g_state(int&& __x);
    ~__g_state();

    int __suspend_point = 0;
    int x;
    manual_lifetime<std::suspend_always> __tmp1;
    manual_lifetime<task> __tmp2;
    manual_lifetime<task::awaiter> __tmp3;
    manual_lifetime<task::promise_type::final_awaiter> __tmp4; // <---
};
```

Then we can implement the body of the final-suspend expression as follows:

```cpp
final_suspend:
    // co_await promise.final_suspend
    {
        state->__tmp4.construct_from([&]() noexcept {
            return state->__promise.final_suspend();
        });
        destructor_guard tmp4_dtor{state->__tmp4};

        if (!state->__tmp4.get().await_ready()) {
            state->__suspend_point = 2;
            state->__resume = nullptr; // mark as final suspend-point

            coro_to_resume = state->__tmp4.get().await_suspend(
                std::coroutine_handle<__g_promise_t>::from_promise(state->__promise));

            tmp4_dtor.cancel();
            goto resume_coro;
        }

        state->__tmp4.get().await_resume();
    }

    //  Destroy coroutine-state if execution flows off end of coroutine
    delete state;
    return;
```
 
And now we also need to update the `__g_destroy` function to handle this new suspend-point.

```cpp
void __g_destroy(__coroutine_state* state) {
    auto* state = static_cast<__g_state*>(s);

    switch (state->__suspend_point) {
    case 0: goto suspend_point_0;
    case 1: goto suspend_point_1;
    case 2: goto suspend_point_2;
    default: std::unreachable();
    }

suspend_point_0:
    state->__tmp1.destroy();
    goto destroy_state;

suspend_point_1:
    state->__tmp3.destroy();
    state->__tmp2.destroy();
    goto destroy_state;

suspend_point_2:
    state->__tmp4.destroy();
    goto destroy_state;

destroy_state:
    delete state;
}
```

We now have a fully functional lowering of the `g()` coroutine function.

We're done! That's it!

Or is it....

## Step 13: Implementing symmetric-transfer and the noop-coroutine

It turns out there is actually a problem with the way we have implemented our `__g_resume()` function above.

The problems with this were discussed in more detail in the previous blog post so if you
want to understand the problem more deeply please take a look at the post
[C++ Coroutines: Understanding Symmetric Transfer]({{ '/2020/05/11/understanding_symmetric_transfer' | relative_url }}).

The specification for [\[expr.await\]](https://eel.is/c++draft/expr.await) gives a little hint about
how we should be handling the coroutine-handle-returning flavour of `await_suspend`:

> If the type of `await-suspend` is `std::coroutine_handle<Z>`, `await-suspend.resume()` is evaluated.
> 
> [_Note_ 1: This resumes the coroutine referred to by the result of _await-suspend_.
> Any number of coroutines can be successively resumed in this fashion, eventually returning control
> flow to the current coroutine caller or resumer ([\[dcl.fct.def.coroutine\]](https://eel.is/c++draft/dcl.fct.def.coroutine)). —- _end note_]

The note there, while non-normative and thus non-binding, is strongly encouraging compilers to 
implement this in such a way that it performs a tail-call to resume the next coroutine rather
than resuming the next coroutine recursively. This is because resuming the next coroutine
recursively can easily lead to unbounded stack growth if coroutines resume each other in a loop.

The problem is that we are calling `.resume()` on the next coroutine from within the body of
the `__g_resume()` function and then returning, so the stack space used by the `__g_resume()`
frame is not freed until after the next coroutine suspends and returns.

Compilers are able to do this by implementing the resumption of the next coroutine as a
tail-call. In this way, the compiler generates code that first pops the the current stack
frame, preserving the return-address, and then executes a `jmp` to the next coroutine's
resume-function.

As we don't have a mechanism in C++ to specify that a function-call in the tail-position
should be a tail-call we will need to instead actually return from the resume-function so
that its stack-space can be freed, and then have the caller resume the next coroutine.

As the next coroutine may also need to resume another coroutine when it suspends, and this
may happen indefinitely, the caller will need to resume the coroutines in a loop.

Such a loop is typically called a "trampoline loop" as we return back to the loop from one
coroutine and then "bounce" off the loop back into the next coroutine.

If we modify the signature of the resume-function to return a pointer to the next coroutine's
coroutine-state instead of returning void, then the `coroutine_handle::resume()` function can
then just immediately call the `__resume()` function-pointer for the next coroutine to resume
it.

Let's change the signature of the `__resume_fn` for a `__coroutine_state`:

```cpp
struct __coroutine_state {
    using __resume_fn = __coroutine_state* (__coroutine_state*);
    using __destroy_fn = void (__coroutine_state*);

    __resume_fn* __resume;
    __destroy_fn* __destroy;
};
```

Then we can write the `coroutine_handle::resume()` function something like this:

```cpp
void std::coroutine_handle<void>::resume() const {
    __coroutine_state* s = state_;
    do {
        s = s->__resume(s);
    } while (/* some condition */);
}
```

The next question then becomes: "What should the condition be?"

This is where the `std::noop_coroutine()` helper comes into the picture.

The `std::noop_coroutine()` is a factory function that returns a special coroutine
handle that has a no-op `resume()` and `destroy()` method. If a coroutine suspends
and returns the noop-coroutine-handle from the `await_suspend()` method then this
indicates that there is no more coroutine to resume and that the invocation of
`coroutien_handle::resume()` that resumed this coroutine should return to its caller.

So we need to implement `std::noop_coroutine()` and the condition in `coroutine_handle::resume()`
so that the condition returns false and the loop exits when the `__coroutine_state` pointer
points to the noop-coroutine-state.

One strategy we can use here is to define a static instance of `__coroutine_state` that is
designated as the noop-coroutine-state. The `std::noop_coroutine()` function can return a
coroutine-handle that points to this object, and we can compare the `__coroutine_state`
pointer to the address of that object to see if a particular coroutine handle is the
noop-coroutine.

First let's define this special noop-coroutine-state object:

```cpp
struct __coroutine_state {
    using __resume_fn = __coroutine_state* (__coroutine_state*);
    using __destroy_fn = void (__coroutine_state*);

    __resume_fn* __resume;
    __destroy_fn* __destroy;

    static __coroutine_state* __noop_resume(__coroutine_state* state) noexcept {
        return state;
    }

    static void __noop_destroy(__coroutine_state*) noexcept {}

    static const __coroutine_state __noop_coroutine;
};

inline const __coroutine_state __coroutine_state::__noop_coroutine{
    &__coroutine_state::__noop_resume,
    &__coroutine_state::__noop_destroy
};
```

Then we can implement the `std::coroutine_handle<noop_coroutine_promise>` specialisation.

```cpp
namespace std
{
    struct noop_coroutine_promise {};

    using noop_coroutine_handle = coroutine_handle<noop_coroutine_promise>;

    noop_coroutine_handle noop_coroutine() noexcept;

    template<>
    class coroutine_handle<noop_coroutine_promise> {
    public:
        constexpr coroutine_handle(const coroutine_handle&) noexcept = default;
        constexpr coroutine_handle& operator=(const coroutine_handle&) noexcept = default;

        constexpr explicit operator bool() noexcept { return true; }

        constexpr friend bool operator==(coroutine_handle, coroutine_handle) noexcept {
            return true;
        }

        operator coroutine_handle<void>() const noexcept {
            return coroutine_handle<void>::from_address(address());
        }

        noop_coroutine_promise& promise() const noexcept {
            static noop_coroutine_promise promise;
            return promise;
        }

        constexpr void resume() const noexcept {}
        constexpr void destroy() const noexcept {}
        constexpr bool done() const noexcept { return false; }

        constexpr void* address() const noexcept {
            return const_cast<__coroutine_state*>(&__coroutine_state::__noop_coroutine);
        }
    private:
        constexpr coroutine_handle() noexcept = default;

        friend noop_coroutine_handle noop_coroutine() noexcept {
            return {};
        }
    };
}
```

And we can update `coroutine_handle::resume()` to exit when the noop-coroutine-state
is returned.


```cpp
void std::coroutine_handle<void>::resume() const {
    __coroutine_state* s = state_;
    do {
        s = s->__resume(s);
    } while (s != &__coroutine_state::__noop_coroutine);
}
```

And finally, we can update our `__g_resume()` function to now return the `__coroutine_state*`.

This just involves updating the signature and replacing:

```cpp
coro_to_resume = ...;
goto resume_coro;
```
with

```cpp
auto h = ...;
return static_cast<__coroutine_state*>(h.address());
```

and then at the very end of the function (after the `delete state;` statement) adding

```cpp
return static_cast<__coroutine_state*>(std::noop_coroutine().address());
```

## One last thing

Those with a keen eye may have noticed that the coroutine-state type `__g_state` is actually
larger than it needs to be.

The data-members for the 4 temporary values each reserve storage for their respective values.
However, the lifetimes of some of the temporary values do not overlap and so in theory we can
save space in the coroutine-state by reusing the storage of an object for the next object after
its lifetime has ended.

To be able to take advantage of this we can instead define the data-members in an anonymous
union where appropriate.

Looking at the lifetimes of the temporary varaibles we have:
- `__tmp1` - exists only within `co_await promise.initial_suspend();` statement
- `__tmp2` - exists only within `int fx = co_await f(x);` statement
- `__tmp3` - exists only within `int fx = co_await f(x);` statement - nested inside lifetime of `__tmp2`
- `__tmp4` - exists only within `co_await promise.final_suspend();` statement

Since lifetimes of `__tmp2` and `__tmp3` overlap we must place them in a struct together
as they both need to exist at the same time.

However, the `__tmp1` and `__tmp4` members do not have lifetimes that overlap and so they can
be placed together in an anonymous `union`.

Thus we can change our data-member definition to:

```cpp
struct __g_state : __coroutine_state_with_promise<__g_promise_t> {
    __g_state(int&& x);
    ~__g_state();

    int __suspend_point = 0;
    int x;

    struct __scope1 {
        manual_lifetime<task> __tmp2;
        manual_lifetime<task::awaiter> __tmp3;
    };

    union {
        manual_lifetime<std::suspend_always> __tmp1;
        __scope1 __s1;
        manual_lifetime<task::promise_type::final_awaiter> __tmp4;
    };
};
```

Then, because the `__tmp2` and `__tmp3` variables are now nested inside the `__s1` object,
we need to update references to them to now be e.g. `state->__s1.tmp2`. But otherwise the
rest of the code stays the same.

This should save an additional 16 bytes of the coroutine-state size as we no longer need
extra storage + padding for the `__tmp1` and `__tmp4` data-members - which would otherwise
be padded to the size of a pointer, despite being empty types.

## Tying it all together

Ok, so the final code we have generated for the coroutine function:

```cpp
task g(int x) {
    int fx = co_await f(x);
    co_return fx * fx;
}
```

is the following:

```cpp
/////
// The coroutine promise-type

using __g_promise_t = std::coroutine_traits<task, int>::promise_type;

__coroutine_state* __g_resume(__coroutine_state* s);
void __g_destroy(__coroutine_state* s);

/////
// The coroutine-state definition

struct __g_state : __coroutine_state_with_promise<__g_promise_t> {
    __g_state(int&& x)
    : x(static_cast<int&&>(x)) {
        // Initialise the function-pointers used by coroutine_handle methods.
        this->__resume = &__g_resume;
        this->__destroy = &__g_destroy;

        // Use placement-new to initialise the promise object in the base-class
        // after we've initialised the argument copies.
        ::new ((void*)std::addressof(this->__promise))
            __g_promise_t(construct_promise<__g_promise_t>(this->x));
    }

    ~__g_state() {
        this->__promise.~__g_promise_t();
    }

    int __suspend_point = 0;

    // Argument copies
    int x;

    // Local variables/temporaries
    struct __scope1 {
        manual_lifetime<task> __tmp2;
        manual_lifetime<task::awaiter> __tmp3;
    };

    union {
        manual_lifetime<std::suspend_always> __tmp1;
        __scope1 __s1;
        manual_lifetime<task::promise_type::final_awaiter> __tmp4;
    };
};

/////
// The "ramp" function

task g(int x) {
    std::unique_ptr<__g_state> state(new __g_state(static_cast<int&&>(x)));
    decltype(auto) return_value = state->__promise.get_return_object();

    state->__tmp1.construct_from([&]() -> decltype(auto) {
        return state->__promise.initial_suspend();
    });
    if (!state->__tmp1.get().await_ready()) {
        state->__tmp1.get().await_suspend(
            std::coroutine_handle<__g_promise_t>::from_promise(state->__promise));
        state.release();
        // fall through to return statement below.
    } else {
        // Coroutine did not suspend. Start executing the body immediately.
        __g_resume(state.release());
    }
    return return_value;
}

/////
//  The "resume" function

__coroutine_state* __g_resume(__coroutine_state* s) {
    auto* state = static_cast<__g_state*>(s);

    try {
        switch (state->__suspend_point) {
        case 0: goto suspend_point_0;
        case 1: goto suspend_point_1; // <-- add new jump-table entry
        default: std::unreachable();
        }

suspend_point_0:
        {
            destructor_guard tmp1_dtor{state->__tmp1};
            state->__tmp1.get().await_resume();
        }

        //  int fx = co_await f(x);
        {
            state->__s1.__tmp2.construct_from([&] {
                return f(state->x);
            });
            destructor_guard tmp2_dtor{state->__s1.__tmp2};

            state->__s1.__tmp3.construct_from([&] {
                return static_cast<task&&>(state->__s1.__tmp2.get()).operator co_await();
            });
            destructor_guard tmp3_dtor{state->__s1.__tmp3};

            if (!state->__s1.__tmp3.get().await_ready()) {
                state->__suspend_point = 1;

                auto h = state->__s1.__tmp3.get().await_suspend(
                    std::coroutine_handle<__g_promise_t>::from_promise(state->__promise));

                // A coroutine suspends without exiting scopes.
                // So cancel the destructor-guards.
                tmp3_dtor.cancel();
                tmp2_dtor.cancel();

                return static_cast<__coroutine_state*>(h.address());
            }

            // Don't exit the scope here.
            // We can't 'goto' a label that enters the scope of a variable with a
            // non-trivial destructor. So we have to exit the scope of the destructor
            // guards here without calling the destructors and then recreate them after
            // the `suspend_point_1` label.
            tmp3_dtor.cancel();
            tmp2_dtor.cancel();
        }

suspend_point_1:
        int fx = [&]() -> decltype(auto) {
            destructor_guard tmp2_dtor{state->__s1.__tmp2};
            destructor_guard tmp3_dtor{state->__s1.__tmp3};
            return state->__s1.__tmp3.get().await_resume();
        }();

        //  co_return fx * fx;
        state->__promise.return_value(fx * fx);
        goto final_suspend;
    } catch (...) {
        state->__promise.unhandled_exception();
        goto final_suspend;
    }

final_suspend:
    // co_await promise.final_suspend
    {
        state->__tmp4.construct_from([&]() noexcept {
            return state->__promise.final_suspend();
        });
        destructor_guard tmp4_dtor{state->__tmp4};

        if (!state->__tmp4.get().await_ready()) {
            state->__suspend_point = 2;
            state->__resume = nullptr; // mark as final suspend-point

            auto h = state->__tmp4.get().await_suspend(
                std::coroutine_handle<__g_promise_t>::from_promise(state->__promise));

            tmp4_dtor.cancel();
            return static_cast<__coroutine_state*>(h.address());
        }

        state->__tmp4.get().await_resume();
    }

    //  Destroy coroutine-state if execution flows off end of coroutine
    delete state;

    return static_cast<__coroutine_state*>(std::noop_coroutine().address());
}

/////
// The "destroy" function

void __g_destroy(__coroutine_state* s) {
    auto* state = static_cast<__g_state*>(s);

    switch (state->__suspend_point) {
    case 0: goto suspend_point_0;
    case 1: goto suspend_point_1;
    case 2: goto suspend_point_2;
    default: std::unreachable();
    }

suspend_point_0:
    state->__tmp1.destroy();
    goto destroy_state;

suspend_point_1:
    state->__s1.__tmp3.destroy();
    state->__s1.__tmp2.destroy();
    goto destroy_state;

suspend_point_2:
    state->__tmp4.destroy();
    goto destroy_state;

destroy_state:
    delete state;
}

```

For a fully compilable version of the final code, see:
[https://godbolt.org/z/xaj3Yxabn](https://godbolt.org/z/xaj3Yxabn)

This concludes the 5-part series on understanding the mechanics of C++ coroutines.

This is probably more information than you ever wanted to know about coroutines, but
hopefully it helps you to understand what's going on under the hood and demystifies
them just a bit.

Thanks for making it through to the end!

Until next time, Lewis.


