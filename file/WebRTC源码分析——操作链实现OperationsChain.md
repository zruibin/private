<!--BEGIN_DATA
{
    "create_date": "2020-09-13 11:50", 
    "modify_date": "2020-09-13 11:50", 
    "is_top": "0", 
    "summary": "WebRTC源码分析——操作链实现OperationsChain", 
    "tags": "WebRTC、C/C++", 
    "file_name": "WebRTC源码分析——操作链实现OperationsChain.md"
}
END_DATA-->

#### <p>原文出处：<a href='https://blog.csdn.net/ice_ly000/article/details/106756695' target='blank'>WebRTC源码分析——操作链实现OperationsChain</a></p>

## 1. 引言

WebRTC中将CreateOffer、CreateAnswer、SetLocalDescription、SetRemoteDescription、AddIceCandidate这5个与SDP会话相关的API认为是一个Operation，这些Operation必须是挨个执行，不能乱序，不能同时有两个并发、并行执行。因此，设计了一套操作链的接口，由类OperationsChain提供此功能，相关的其他类有Operation、OperationWithFunctor、CallbackHandle。

关于OperationsChain，源码文件中提供了非常详细的英文说明，要点如下：

  * 操作链用于确保异步任务按序执行，并且同时只执行一个任务。操作链相关的观念可以通过链接：<https://w3c.github.io/webrtc-pc/#dfn-operations-chain>来查看。
  * 一个操作（Operation）就是一个异步任务。这个操作始于对应的functor（仿函数）被调用，以传给functor的回调方法callback被调用后而终结。操作的执行必须与入队的顺序一致。因此，操作链以“单线程”的方式执行。但异步操作可能使用任意数量的线程来实现“并行”行为。
  * 当一个操作进入操作链时，将被排队，以FIFO执行。当前一个操作还未执行完成时，后面一个操作是不会得到执行的。操作链将保证：当入队一个操作时，若操作链中没有其他操作，那么刚入队的操作将立即得到执行；若操作链中存在其他操作，则前一个操作完成时，在其回调方法callback中触发后一个操作的执行。
  * 一个操作完成后只能触发一次回调。OperationsChain不支持取消已入队的操作，要实现操作的取消，只能是操作自己内部根据其他状态来终止自己的行为，但是操作完成回调仍然必须得被触发。
  * 通过引用计数来确保操作链中存在操作时，操作链OperationsChain处于keep-live状态（OperationsChain对象不会被析构）。也正由于上述这点，保证了所有入队的操作都将被执行。

## 2. 创建Offer时，操作链调用示例


```cpp
operations_chain_->ChainOperation(
    [this_weak_ptr = weak_ptr_factory_.GetWeakPtr(),
      observer_refptr =
          rtc::scoped_refptr<CreateSessionDescriptionObserver>(observer),
      options](std::function<void()> operations_chain_callback) {
      // Abort early if |this_weak_ptr| is no longer valid.
      if (!this_weak_ptr) {
        observer_refptr->OnFailure(
            RTCError(RTCErrorType::INTERNAL_ERROR,
                      "CreateOffer failed because the session was shut down"));
        operations_chain_callback();
        return;
      }
      // The operation completes asynchronously when the wrapper is invoked.
      rtc::scoped_refptr<CreateSessionDescriptionObserverOperationWrapper>
          observer_wrapper(new rtc::RefCountedObject<
                            CreateSessionDescriptionObserverOperationWrapper>(
              std::move(observer_refptr),
              std::move(operations_chain_callback)));
      this_weak_ptr->DoCreateOffer(options, observer_wrapper);
    });
```

  1. `operations_chain_`是`rtc::scoped_refptr<rtc::OperationsChain> operations_chain_`对象，PeerConnection对象通过其持有OperationsChain对象的引用。
  2. 通过OperationsChain::ChainOperation()来实现操作链调用，该方法的声明为如下。该方法是一个模板方法，参数FunctorT&& functor既可以传入右值，又可以传入左值。

```cpp
template <typename FunctorT>
void ChainOperation(FunctorT&& functor)
```

  3. 虽然FunctorT看上去可以是任意类型，实际上对其是有要求的，否则就不叫FunctorT，而是T了。实际上，要求FunctorT必须是movable，可移动的；必须实现了操作符T operator()(std::function<void()> callback) or T operator()(std::function<void()> callback) const；
  4. 如源码所示，FunctorT 实际是由lambda表达式产生的“闭包类型”，它是一个特殊的、匿名的，带有operator()的类，即C++仿函数。注意，lambda表达式得到的是一个类对象，而非函数。正好满足了3中的要求。
  5. 注意：上述lambda表达式产生了仿函数对象，该对象是一个临时变量，是一个右值。因此，执行ChainOperation(FunctorT&& functor)时，会执行移动语义，而非拷贝语义，使得该仿函数对象被转移到ChainOperation方法内部。至于后续…后续的代码将会看到，该对象会被完美转发到操作Operation的内部，成为操作的成员变量。

后续我们抽丝剥茧，一步步来分析。

## 3. 操作链的实现

操作链相关实现在WebRTC源码的rtc_base模块的operations_chain.h/operations_chain.cc文件中。涉及到的相关类有如下几个：

  * Operation：操作的抽象接口，提供Run方法。
  * OperationWithFunctor：继承Operation，实现Run方法，代表一个真实的操作。注意操作的名称，With Functor，暗示了前面所述lambda表达式所产生的的C++仿函数对象将成为其成员。
  * OperationsChain：操作调用链对象，用于存储、排队Operation。
  * CallbackHandle：承载着操作完成之后，通过回调方式出发下一个Operation的Run。

### 3.1 Operation

没有什么可多说的


```cpp
// Abstract base class for operations on the OperationsChain. Run() must be
// invoked exactly once during the Operation's lifespan.
class Operation {
  public:
  virtual ~Operation() {}
  virtual void Run() = 0;
};
```

### 3.2 OperationWithFunctor


```cpp
template <typename FunctorT>
class OperationWithFunctor final : public Operation {
 public:
  OperationWithFunctor(FunctorT&& functor, std::function<void()> callback)
      : functor_(std::forward<FunctorT>(functor)),
        callback_(std::move(callback)) {}

  ~OperationWithFunctor() override { RTC_DCHECK(has_run_); }

  void Run() override {
    RTC_DCHECK(!has_run_);
#ifdef RTC_DCHECK_IS_ON
    has_run_ = true;
#endif  // RTC_DCHECK_IS_ON
    // The functor being executed may invoke the callback synchronously,
    // marking the operation as complete. As such, |this| OperationWithFunctor
    // object may get deleted here, including destroying |functor_|. To
    // protect the functor from self-destruction while running, it is moved to
    // a local variable.
    auto functor = std::move(functor_);
    functor(std::move(callback_));
    // |this| may now be deleted; don't touch any member variables.
  }

 private:
  typename std::remove_reference<FunctorT>::type functor_;
  std::function<void()> callback_;
#ifdef RTC_DCHECK_IS_ON
  bool has_run_ = false;
#endif  // RTC_DCHECK_IS_ON
};
```

  * OperationWithFunctor构造传入了承载了外部想要被执行代码的C++仿函数对象FunctorT（正如前面CreateOffer示例那样，通过一个lamda表达式，构建了一个FunctorT仿函数对象，该仿函数对象的oprator()方法执行真正的CreateOffer动作），传入了操作结束回调方法。注意，一个是通过完美转发语义std::forward传入，一个是通过转移语义传入。
  * OperationWithFunctor实现了Run方法，并确保Run方法只被执行一次；同时，Run方法里面要做的唯一的事就是通过传入的仿函数执行 “真正的操作”，即`functor(std::move(callback_))`;这条语句所做事情。
  * 也请注意：Run方法中使用了语句`auto functor = std::move(functor_);`，将仿函数对象转移到一个本地变量functor中的原因在于，执行functor()方法时，传入了完成回调，该回调的执行是同步的，回调中会将OperationWithFunctor delete掉。若没有执行移动语义，由于`functor_`是OperationWithFunctor的成员，在OperationWithFunctor析构时，`functor_`也会被析构，这样相当于执行`functor_`对象的Operator()方法时，执行了delete this，会引发异常。因此，就有了上述的神之操作。

### 3.3 OperationsChain


```cpp
class OperationsChain final : public RefCountedObject<RefCountInterface> {
 public:
  static scoped_refptr<OperationsChain> Create();
  ~OperationsChain();
  
  template <typename FunctorT>
  void ChainOperation(FunctorT&& functor) {
    RTC_DCHECK_RUN_ON(&sequence_checker_);
    chained_operations_.push(
        std::make_unique<
            rtc_operations_chain_internal::OperationWithFunctor<FunctorT>>(
            std::forward<FunctorT>(functor), CreateOperationsChainCallback()));

    if (chained_operations_.size() == 1) {
      chained_operations_.front()->Run();
    }
  }

 private:
  OperationsChain();

  std::function<void()> CreateOperationsChainCallback(){
	  return [handle = rtc::scoped_refptr<CallbackHandle>(
	              new CallbackHandle(this))]() { handle->OnOperationComplete(); };
  }
	
  void OnOperationComplete(){
	  RTC_DCHECK_RUN_ON(&sequence_checker_);
	  // The front element is the operation that just completed, remove it.
	  RTC_DCHECK(!chained_operations_.empty());
	  chained_operations_.pop();
	  // If there are any other operations chained, execute the next one.
	  if (!chained_operations_.empty()) {
	    chained_operations_.front()->Run();
	  }
	}

  webrtc::SequenceChecker sequence_checker_;
  // FIFO-list of operations that are chained. An operation that is executing
  // remains on this list until it has completed by invoking the callback passed
  // to it.
  std::queue<std::unique_ptr<rtc_operations_chain_internal::Operation>>
      chained_operations_ RTC_GUARDED_BY(sequence_checker_);

  RTC_DISALLOW_COPY_AND_ASSIGN(OperationsChain);
};
}
```

OperationsChain实际上有个内部类CallbackHandle，为了去除干扰，上述源码中先屏蔽了这部分代码。OperationsChain有三个重要的方法：

  * **ChainOperation**：做了两件事：一是通过外部传入的C++仿函数（注意使用了std::forward完美转发，结合之前分析的该构造函数内部也使用了完美转发，这样外部传入的仿函数对象会被一路完美转发到OperationWithFunctor的成员functor_中） + CreateOperationsChainCallback创建的回调方法 来创建操作对象OperationWithFunctor，将该对象push进入FIFO队列。二是判断了FIFO队列中OperationWithFunctor个数，若是只有一个，也即刚入队的这个操作，那么直接执行该操作的Run方法。
  * **CreateOperationsChainCallback**：该方法通过lambda表达式返回了一个C++仿函数临时对象，由于C++11中 std::function 可以用来存储C++仿函数对象，并且时movable的，因此，该仿函数对象会执行移动语义，将临时对象转移出来。并且，该仿函数所执行的操作是：捕获了一个CallbackHandle对象（该对象持有OperationsChain地址），函数体中执行其CallbackHandle::OnOperationComplete方法。往后看CallbackHandle的源码可知，实际上CallbackHandle::OnOperationComplete调用了ChainOperation::OnOperationComplete方法。
  * **OnOperationComplete**：做了两件事，一件是将当前操作从FIFO队列中移除；另外一件是检查是否还有其它操作在FIFO中，如果存在，则调用队头的操作的Run方法。

**PS: 问题：为什么CreateOperationsChainCallback方法中要创建一个CallbackHandle变量，通过该变量的OnOperationComplete方法去调用OperationsChain的OnOperationComplete去完成回调呢？这种方式太绕了，为何不是直接调用OperationsChain的OnOperationComplete方法呢？**

### 3.4 CallbackHandle

CallbackHandle类声明在OperationsChain内部，并且是OperationsChain的friend class。


```cpp
class CallbackHandle final : public RefCountedObject<RefCountInterface> {
  public:
  explicit CallbackHandle(scoped_refptr<OperationsChain> operations_chain): operations_chain_(std::move(operations_chain)) {}
  ~CallbackHandle() {
    RTC_DCHECK(has_run_);
}

  void OnOperationComplete() {
    RTC_DCHECK(!has_run_);
  #ifdef RTC_DCHECK_IS_ON
    has_run_ = true;
  #endif  // RTC_DCHECK_IS_ON
    operations_chain_->OnOperationComplete();
    // We have no reason to keep the |operations_chain_| alive through reference
    // counting anymore.
    operations_chain_ = nullptr;
}

  private:
  scoped_refptr<OperationsChain> operations_chain_;
#ifdef RTC_DCHECK_IS_ON
  bool has_run_ = false;
#endif  // RTC_DCHECK_IS_ON

  RTC_DISALLOW_COPY_AND_ASSIGN(CallbackHandle);
};
```

回答下为什么需要有CallbackHandle这个辅助对象的原因：对象CallbackHandle通过其构造函数持有了OperationsChain的共享指针，这样可以保证CallbackHandle的OnOperationComplete方法在被调用前，OperationsChain还是“活着的”。这样就能保证操作的回调会被执行，从而操作可以从FIFO中出队，并且下一个操作也必然得到执行，也即所有的操作都会在OperationsChain生命周期结束前得到执行。

## 4. 总结

行文至此，操作链实现的细节就交代完毕了。实际上操作链的实现逻辑是简单而清晰的，不过上述分析过程中涉及到了C++11中的一些特性：std::move、std::forwad、std::function、lambda表达式。这些特性的使用使得操作链实现非常高效，避免了很多拷贝工作。但是如果不熟悉这些特性的情况下，可能会有些晕乎，上述分析过程中也说了一堆关于这些特性的东西，可能更让人不明所以了。但绕过这些特性，实际上操作链的实现逻辑理解起来是比较简单的，只是无法透彻理解它的实现细节而已。
