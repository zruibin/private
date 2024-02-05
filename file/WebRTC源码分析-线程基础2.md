
<!--BEGIN_DATA
{
    "create_date": "2020-09-12 23:00", 
    "modify_date": "2020-09-12 23:00", 
    "is_top": "0", 
    "summary": "WebRTC源码分析-线程基础之MessageQueueManager<br/>WebRTC源码分析-线程基础之Message && MessageData && MessageHandler<br/>WebRTC源码分析-线程基础之MessageQueue", 
    "tags": "WebRTC、C/C++", 
    "file_name": "WebRTC源码分析-线程基础2.md"
}
END_DATA-->

#### <p>原文出处：<a href='https://blog.csdn.net/ice_ly000/article/details/103178701' target='blank'>WebRTC源码分析-线程基础之MessageQueueManager</a></p>

### 前言

正如其名，MessageQueueManager类(后续简写为MQM)提供了MessageQueue(简写为MQ)的管理功能。在之前的文章中已经分析过，MQ在构建时会调用MQ.DoInit()方法，该方法将MQ添加到MQM的内部std::Vector<MessageQueue*>成员中。  

MQM类的声明和定义分别在`rtc_base/message_queue.h`以及`rtc_base/message_queue.cc`中，其定义如下所示


```cpp
// MessageQueueManager does cleanup of of message queues
class MessageQueueManager {
 public:
  static void Add(MessageQueue* message_queue);
  static void Remove(MessageQueue* message_queue);
  static void Clear(MessageHandler* handler);
 
  // TODO(nisse): Delete alias, as soon as downstream code is updated.
  static void ProcessAllMessageQueues() { ProcessAllMessageQueuesForTesting(); }
 
  // For testing purposes, for use with a simulated clock.
  // Ensures that all message queues have processed delayed messages
  // up until the current point in time.
  static void ProcessAllMessageQueuesForTesting();
 
 private:
  static MessageQueueManager* Instance();
  MessageQueueManager();
  ~MessageQueueManager();
 
  void AddInternal(MessageQueue* message_queue);
  void RemoveInternal(MessageQueue* message_queue);
  void ClearInternal(MessageHandler* handler);
  void ProcessAllMessageQueuesInternal();
 
  // This list contains all live MessageQueues.
  std::vector<MessageQueue*> message_queues_ RTC_GUARDED_BY(crit_);
 
  // Methods that don't modify the list of message queues may be called in a
  // re-entrant fashion. "processing_" keeps track of the depth of re-entrant
  // calls.
  CriticalSection crit_;
  size_t processing_ RTC_GUARDED_BY(crit_);
};
```

### MessageQueueManager的构造

MessageQueueManager的构造方式与ThreadManager一样，都是单例模式，都是非安全的。之前分析过ThreadManager为什么能够安全的构造，MessageQueueManager原理一样，并且MessageQueueManager对象的创建先于第一个MessageQueue对象。


```cpp
MessageQueueManager* MessageQueueManager::Instance() {
  static MessageQueueManager* const instance = new MessageQueueManager;
  return instance;
}

MessageQueueManager::MessageQueueManager() : processing_(0) {}
MessageQueueManager::~MessageQueueManager() {}
```

### MessageQueue的添加与移除

MessageQueueManager提供了Add与Remove的静态函数来往单例的管理类中添加和删除MQ，具体如下源码所示：


```cpp
void MessageQueueManager::Add(MessageQueue* message_queue) {
  return Instance()->AddInternal(message_queue);
}
void MessageQueueManager::AddInternal(MessageQueue* message_queue) {
  CritScope cs(&crit_);
  // Prevent changes while the list of message queues is processed.
  RTC_DCHECK_EQ(processing_, 0);
  message_queues_.push_back(message_queue);
}
 
void MessageQueueManager::Remove(MessageQueue* message_queue) {
  return Instance()->RemoveInternal(message_queue);
}
void MessageQueueManager::RemoveInternal(MessageQueue* message_queue) {
  {
    CritScope cs(&crit_);
    // Prevent changes while the list of message queues is processed.
    RTC_DCHECK_EQ(processing_, 0);
    std::vector<MessageQueue*>::iterator iter;
    iter = std::find(message_queues_.begin(), message_queues_.end(),
                     message_queue);
    if (iter != message_queues_.end()) {
      message_queues_.erase(iter);
    }
  }
}
```

添加和删除方法对外都是以静态方法提供，通过调用MQM的单实例的对应的私有方法来实现往向量Vector中添加和删除MQ，需要说明的注意点有以下几个：

1）成员`crit_`是临界区类CriticalSection的对象，该成员保证多线程环境下`MQM.message_queues_`以及`MQM.processing_`访问安全，正如上面两个函数所示，函数开头创建`CritScope cs(&crit_)`; 在cs的构造函数中调用`crit_->Enter()`表示进入临界区，相当于上锁。利用函数结束后cs对象的析构中调用`crit_->Leave()`表示离开临界区，相当于解锁。

2）存储MQ的向量声明为：`std::vector<MessageQueue*> message_queues_ RTC_GUARDED_BY(crit_)`; 其中`RTC_GUARDED_BY`宏在clang编译器下展开为`attribute(guarded_by(crit_))`，指示编译器在编译过程中检查代码中所有访问`message_queues_`的各个路径上是否都先获取了锁`crit_`，如果没有就会在编译过程中产生错误或者警告。而对于其他编译器，该宏不起任何作用，意味着不会在编译期进行检查。详见 [Thread Safety Analysis](https://links.jianshu.com/go?to=http%3A%2F%2Fclang.llvm.org%2Fdocs%2FThreadSafetyAnalysis.html)。  

3）成员`processing_`声明为：`size_t processing_ RTC_GUARDED_BY(crit_)`; Add与Remove函数中执行了`RTC_DCHECK_EQ(processing_, 0)`断言，必须确保`processing_`为0。当`processing_`不为0时，要么在执行MQM的Clear()方法，要么在执行ProcessAllMessageQueues()，这些操作此时，是不允许往MQM添加MQ或者删除MQ这种会改变Vector列表的操作，因为前面的两个函数一般都会要遍历Vector。思考一点，不是已经上锁保证线程安全了嘛，为啥还要保证`processing_`为0呢？继续往下看吧~~

### 清理

与Add和Remove方式一摸一样，Clear函数也是以静态方法的形式对外提供。Clear函数的作用是从MQM所管理的所有MQ中删除与入参MessageHandler* handler匹配消息。具体而言就是遍历MQM中的MQ，然后调用MQ本身的Clear()方法，这个方法比较冗长，此处就不展开叙述，将会在介绍MQ的文章中详细描述。


```cpp
void MessageQueueManager::Clear(MessageHandler* handler) {
  return Instance()->ClearInternal(handler);
}

void MessageQueueManager::ClearInternal(MessageHandler* handler) {
  // Deleted objects may cause re-entrant calls to ClearInternal. This is
  // allowed as the list of message queues does not change while queues are
  // cleared.
  MarkProcessingCritScope cs(&crit_, &processing_);
  for (MessageQueue* queue : message_queues_) {
    queue->Clear(handler);
  }
}
```

另外很重要的一点，该方法并没有使用前文所述的`CritScopecs(&crit_)`来实现线程安全，而是使用了一个新的类`MarkProcessingCritScope cs(&crit_, &processing_)`，有什么神奇的地方？且看源码：


```cpp
class RTC_SCOPED_LOCKABLE MarkProcessingCritScope {
 public:
  MarkProcessingCritScope(const CriticalSection* cs, size_t* processing)
      RTC_EXCLUSIVE_LOCK_FUNCTION(cs)
      : cs_(cs), processing_(processing) {
    cs_->Enter();
    *processing_ += 1;
  }
  ~MarkProcessingCritScope() RTC_UNLOCK_FUNCTION() {
    *processing_ -= 1;
    cs_->Leave();
  }
 private:
  const CriticalSection* const cs_;
  size_t* processing_;
  RTC_DISALLOW_COPY_AND_ASSIGN(MarkProcessingCritScope);
};
```

首先要知道CriticalSection是可重入的，也即一个线程上调用`cs_->Enter()`上锁之后，在释放锁之前，同一个线程可以反复调用`cs_->Enter()`而不会阻塞，因此被称为“可重入锁”。同一个线程上锁一次，`processing_`就增1，记录上锁次数，只要`processing_`不为0，表示我正在Clear操作或者后文的Process*方法，这两个方法不会改变MQM中Vector列表，因此，可以在解锁之前，重入进行反复操作，但是不允许Add和Remove操作，因为其会改变Vector，这就是为什么Add和Remove函数中既加锁了，还要断言`processing_`必须为0，否则代码就是写得有Bug了。

### 处理所有MQ中的消息

这个方法目前还没有完全的理解，首先说下我自己的分析。

  * 方法如其名，目标在于使得MQM中管理的MQ中的消息得到处理。
  * 当某个线程调用该方法时，会遍历所有的MQ，然后向MQ中投递一个消息ID为MQID_DISPOSE的延迟消息，其消息数据为ScopedIncrement对象，ScopedIncrement的构造中将`queues_not_done`原子性自增1，表示该消息队列中有消息没有被处理，而该延迟消息时间为0，那么该延迟消息将进入MQ的延迟消息队列的队首(因为MQ的延迟消息队列是以延迟时间排序的优先级队列)。记住，所有的MQ中都会投递一个这样的消息。
  * 方法后续就是获取调用该方法的线程所关联的Thread对象，并通过Thread对象的ProcessMessages方法不断的从当前线程的MQ中取出消息进行处理，直到`queues_not_done`为0，此时，之前投递到消息循环中的`MQID_DISPOSE`类别的消息得到处理，因为该消息在消息循环中被取出后，消息数据ScopedIncrement对象会被直接delete，从而ScopedIncrement析构完成`queues_not_done`原子性自减1。此时，表征着该消息循环中的所有即时消息都得到了处理。
  * 最大的疑惑就是，所有的MQ中都放入了一个MQID_DISPOSE类别的延迟消息，调用该方法的线程会如上所述的方式阻塞地将所有即时消息处理掉，而没有主动调用该方法的线程是如何保证该方法的目标得以实现的，即，使得所有MQ的即时消息都能同步的立马处理？毕竟，对于其他的MQ此处也仅仅是投递了一个`MQID_DISPOSE`类别的延迟消息而已。
    

```cpp
static void ProcessAllMessageQueues() { ProcessAllMessageQueuesForTesting(); }
 
void MessageQueueManager::ProcessAllMessageQueuesForTesting() {
  return Instance()->ProcessAllMessageQueuesInternal();
}
 
void MessageQueueManager::ProcessAllMessageQueuesInternal() {
  // This works by posting a delayed message at the current time and waiting
  // for it to be dispatched on all queues, which will ensure that all messages
  // that came before it were also dispatched.
  volatile int queues_not_done = 0;
 
  // This class is used so that whether the posted message is processed, or the
  // message queue is simply cleared, queues_not_done gets decremented.
  class ScopedIncrement : public MessageData {
   public:
    ScopedIncrement(volatile int* value) : value_(value) {
      AtomicOps::Increment(value_);
    }
    ~ScopedIncrement() override { AtomicOps::Decrement(value_); }
 
   private:
    volatile int* value_;
  };
 
  {
    MarkProcessingCritScope cs(&crit_, &processing_);
    for (MessageQueue* queue : message_queues_) {
      if (!queue->IsProcessingMessagesForTesting()) {
        // If the queue is not processing messages, it can
        // be ignored. If we tried to post a message to it, it would be dropped
        // or ignored.
        continue;
      }
      queue->PostDelayed(RTC_FROM_HERE, 0, nullptr, MQID_DISPOSE,
                         new ScopedIncrement(&queues_not_done));
    }
  }
  rtc::Thread* current = rtc::Thread::Current();
  // Note: One of the message queues may have been on this thread, which is
  // why we can't synchronously wait for queues_not_done to go to 0; we need
  // to process messages as well.
  while (AtomicOps::AcquireLoad(&queues_not_done) > 0) {
    if (current) {
      current->ProcessMessages(0);
    }
  }
}
```

### 总结

  * MessageQueueManager是管理MessageQueue的类，与ThreadManager管理Thread的方式是不同的。MQM内部的向量成员`std::Vector<MessageQueue*> message_queues_`用于存储所有的MQ，时机是在MQ的构造函数中调用MQM的Add静态方法将自身指针放入`message_queues_`中。
  * MQM对外提供了所有方法都是静态方法，这些静态方法均是调用MQM单实例的私有的同名函数来实现添加，删除MQ，清除所有MQ中含有某个MessageHandler的所有消息，处理所有MQ中的消息。
  * 为了线程安全，MQM中的所有操作都由`CriticalSection crit_`来提供上锁的操作，该对象对外暴露的是Windows上临界区概念的API，其提供了Enter()，Leave()等进出临界区的方法。CriticalSection跨平台是如何实现的？请看[WebRTC源码分析-线程安全之CriticalSection](https://www.jianshu.com/p/c7df0bb0727e)。 实践上，在需要上锁的地方创建一个CritScope cs(&crit_)局部对象，这个cs局部对象的构造函数中调用`crit_->Enter()`进行上锁，利用局部对象在{}之后的析构中调用`crit_->Leave()`来解锁。
  * 为了给MQM的Clear和Process* 方法提供可重入访问方法，又需要与Add和Remove方法互斥，因此，在Clear和Procees* 方法中使用MarkProcessingCritScope来提供上锁计数`processing_`，Add和Remove中断言processing_来确保操作安全。
  * 关于Procees* 如何使得所有线程的消息得到处理的疑惑，可能是局限于MQM类的分析无法全局看到实现机制，当前只知道调用该方法的线程是如何达到处理所有即时消息的。而相关的方法本文没有展开来说，会在介绍Thread和MQ的文章中详细阐述。如果谁理解了该函数如何使得其他线程处理所有即时消息的机制，希望留言。


<hr/>


#### <p>原文出处：<a href='https://blog.csdn.net/ice_ly000/article/details/103178700' target='blank'>WebRTC源码分析-线程基础之Message && MessageData && MessageHandler</a></p>

### 前言

本文将介绍消息循环中的消息(Message)，消息中持有的数据(MessageData)，处理消息的Handler(MessageHandler)的基本内容。

其中Message与MessageData相关的结构体位于rtc_base/message_queue.h中，MessageHandler相关的类位于`rtc_base/message_handler.h`中

### 消息Message

WebRTC中消息相关的类分为两种，一种是Message，表征的是即时消息，投放到消息循环中期待能被立马消费；另外一种是DelayedMessage，表征的是延迟消息，投放到消息循环中不会立马被消费，而是延迟一段时间才会被消费。

**Message** 源码如下所示
    
```cpp
struct Message {
  Message()
      : phandler(nullptr), message_id(0), pdata(nullptr), ts_sensitive(0) {}
  inline bool Match(MessageHandler* handler, uint32_t id) const {
    return (handler == nullptr || handler == phandler) &&
            (id == MQID_ANY || id == message_id);
  }
  Location posted_from;             // 消息自哪儿产生
  MessageHandler* phandler;    // 消息如何处理
  uint32_t message_id;              // 消息id
  MessageData* pdata;              // 消息中携带的数据
  int64_t ts_sensitive;                 // 消息产生的时间
};
```

#### Message结构体成员有如下几种：

  * `Location posted_from`： 该成员描述了此消息结构是在哪个函数，哪个文件的哪一行产生的，即消息产生的源头。通常实际使用中使用宏`RTC_FROM_HERE`来产生Location对象，Location类的简单分析见[WebRTC源码分析-定位之Location](https://www.jianshu.com/p/7a981fc548a2)。
  * `MessageHandler* phandler`：该成员持有消息如何被消费的方法，当消息从消息循环中被取出后，将使用 MessageHandler的`OnMessage(Message* msg)`来对消息进行处理。特别的PeerConnection对象也是MessageHandler，实现了OnMessage(Message* msg)方法。
  * `uint32_t message_id`：32位无符号整型的消息`id`。通常有两类特别的消息，使用特殊的消息id来识别，分别是`MQID_ANY(-1)`表示所有的消息；`MQID_DISPOSE(-2)`表示需要丢弃的消息，该消息已经在MQM的分析文章中出现，详见[WebRTC源码分析-线程基础之MessageQueueManager](https://www.jianshu.com/p/f89e3f55bd4f)。当然，还有使用其他id值用以做特殊处理的，比如某个实现了MessageHandler.OnMessage方法的类，可能需要处理好几种不同的消息，那么就可以将不同消息id值当作区分消息类别的标志，从而在OnMessage方法中分门别类处理好几种消息了。
  * `int64_t ts_sensitive`：64位时间戳，单位ms。当不关心消息是否处理过慢时，也即消息时间不敏感时，该值为0；若关心消息是否得到即时处理，一般会设置`ts_sensitive`为消息创建时的时间戳 + kMaxMsgLatency常量(150ms)，当该消息从消息循环中取出被处理时，将会检测当前时间`msCurrent`与`ts_sensitive`的大小，若`msCurrent>ts_sensitive`，则表示该消息并没有得到即时的处理，会打印警告日志。超时时间计算为`msCurrent-ts_sensitive+kMaxMsgLatency`。
  * MessageData* pdata：消息数据。有多个变种，后面详述。

Message结构体还提供了两个方法。

  * 构造函数：没啥好说，Message没有提供析构函数，那么Message持有的消息处理器phandler以及消息数据pdata何时被销毁就非常值得注意了。
  * 匹配函数：该函数在MQ清理消息时，用于评判哪些消息是满足条件的，即匹配上了。看源码可知，只要handler为空或者相等 **并且** 消息id为MQID_ANY或者相等，就被认为是找到了满足条件的消息。

**DelayedMessage**源码如下
    
```cpp
// DelayedMessage goes into a priority queue, sorted by trigger time.  Messages
// with the same trigger time are processed in num_ (FIFO) order.
class DelayedMessage {
  public:
  DelayedMessage(int64_t delay,
                  int64_t trigger,
                  uint32_t num,
                  const Message& msg)
      : cmsDelay_(delay), msTrigger_(trigger), num_(num), msg_(msg) {}

  bool operator<(const DelayedMessage& dmsg) const {
    return (dmsg.msTrigger_ < msTrigger_) ||
            ((dmsg.msTrigger_ == msTrigger_) && (dmsg.num_ < num_));
  }

  int64_t cmsDelay_;  // for debugging
  int64_t msTrigger_;
  uint32_t num_;
  Message msg_;
};
```

DelayedMessage与Message并非是继承is-a关系，而是has-a的关系。提供了除`Message msg_`成员之外的另几个成员：

  * `int64_t cmsDelay_`：延迟时间，消息延迟多长时间后需要被处理，单位ms
  * `int64_t msTrigger_`：触发时间，消息需要被处理的时间戳，为消息创建时的时间戳+`cmsDelay_`，单位ms
  * `uint32_t num_`：消息的序号，在某个MQ中延迟消息的`num_`单调递增。

由于DelayedMessage在MQ中会放至于专门的优先级队列中，优先级如何确定？DelayedMessage重载了小于"<"运算符以确定排序，先按消息需要被处理的触发时间戳`msTrigger_`排序；若触发时间相同，则按消息序号排序。当某个延迟消息要投放到延迟队列中时，该优先级队列会根据“<”运算符去比较这个延迟消息与队列中的消息以确定应在队列的哪个位置插入该消息。

**MessageList**被定义为std::list<Message>， MessageQueue中的即时消息就存储于MessageList类别的列表中，按照先入先出的方式挨个进行处理。
    
```cpp
typedef std::list<Message> MessageList;
```

### 消息MessgeData

**MessgeData** 消息数据基类，其析构函数被定义为virtual类型，以防内存泄漏
    
```cpp
class MessageData {
  public:
  MessageData() {}
  virtual ~MessageData() {}
};
```

**TypedMessageData** 使用模板定义的MessageData 的一个子类，便于扩展。
    
```cpp
template <class T>
class TypedMessageData : public MessageData {
  public:
  explicit TypedMessageData(const T& data) : data_(data) {}
  const T& data() const { return data_; }
  T& data() { return data_; }
  private:
  T data_;
};
```

**ScopedMessageData** 类似于 TypedMessageData，用于指针类型。在析构函数中，自动对该指针调用 delete。
    
```cpp
// Like TypedMessageData, but for pointers that require a delete.
template <class T>
class ScopedMessageData : public MessageData {
 public:
  explicit ScopedMessageData(std::unique_ptr<T> data)
      : data_(std::move(data)) {}
  // Deprecated.
  // TODO(deadbeef): Remove this once downstream applications stop using it.
  explicit ScopedMessageData(T* data) : data_(data) {}
  // Deprecated.
  // TODO(deadbeef): Returning a reference to a unique ptr? Why. Get rid of
  // this once downstream applications stop using it, then rename inner_data to
  // just data.
  const std::unique_ptr<T>& data() const { return data_; }
  std::unique_ptr<T>& data() { return data_; }
 
  const T& inner_data() const { return *data_; }
  T& inner_data() { return *data_; }
 
 private:
  std::unique_ptr<T> data_;
};
```

**ScopedRefMessageData** 类似于ScopedMessageData，用于引用计数的指针类型。
    
```cpp
// Like ScopedMessageData, but for reference counted pointers.
template <class T>
class ScopedRefMessageData : public MessageData {
  public:
  explicit ScopedRefMessageData(T* data) : data_(data) {}
  const scoped_refptr<T>& data() const { return data_; }
  scoped_refptr<T>& data() { return data_; }

  private:
  scoped_refptr<T> data_;
};
```

**DisposeData** 这个值得注意下，和前面几个MessageData子类不一样，该对象并没有提供其内部数据`data_`的方法，那么该对象正如其名，持有需要进行销毁的数据。在哪些场景下使用？

  * 有些函数不便在当前函数范围内销毁对象，那么就可以将需要销毁的对象封装到DisposeData中，并进一步封装成消息并投递到消息队列中，等待线程的消息循环取出消息并进行销毁时将该对象销毁。见范例 HttpServer::Connection::~Connection；这里类似于QT中QObject的deletelater()方法的作用，起到延迟销毁的作用。
  * 某对象属于某一线程，因此销毁操作应该交给所有者线程。这个可以通过调用对应线程对象Thread的MessageQueue的Dispose(T* doomed)来实现。在介绍MessageQueue的文章中会详述。
    

```cpp
template <class T>
class DisposeData : public MessageData {
 public:
  explicit DisposeData(T* data) : data_(data) {}
  virtual ~DisposeData() { delete data_; }

 private:
  T* data_;
};
```

**WrapMessageData && UseMessageData** 两个模板方法，分别用来将数据封装成MessageData以及取出对应的数据，封装拆箱操作。
    

```cpp
template <class T>
inline MessageData* WrapMessageData(const T& data) {
  return new TypedMessageData<T>(data);
}

template <class T>
inline const T& UseMessageData(MessageData* data) {
  return static_cast<TypedMessageData<T>*>(data)->data();
}
```

### 消息处理器MessageHandler

**MessageHandler** 消息处理器的基类，子类在继承了该类之后要重载 OnMessage 函数，在其中实现消息响应的逻辑。
    
```cpp
class MessageHandler {
 public:
  virtual ~MessageHandler();
  virtual void OnMessage(Message* msg) = 0;
 protected:
  MessageHandler() {}
 private:
  RTC_DISALLOW_COPY_AND_ASSIGN(MessageHandler);
};
```

**FunctorMessageHandler** MessageHandler的模板子类，用于帮助实现阻塞地跨线程在指定线程上执行某个方法，并可获取执行结果。Thread的Invoke()方法使用该类。该类的构造函数中使用了C++11的右值引用，转发语义std::forward，以及转移语义std::move。详见博客[C++11 std::move和std::forward](https://www.jianshu.com/p/b90d1091a4ff)
    

```cpp
// Helper class to facilitate executing a functor on a thread.
template <class ReturnT, class FunctorT>
class FunctorMessageHandler : public MessageHandler {
  public:
  explicit FunctorMessageHandler(FunctorT&& functor)
      : functor_(std::forward<FunctorT>(functor)) {}
  virtual void OnMessage(Message* msg) { result_ = functor_(); }
  const ReturnT& result() const { return result_; }
  // Returns moved result. Should not call result() or MoveResult() again
  // after this.
  ReturnT MoveResult() { return std::move(result_); }
  private:
  FunctorT functor_;
  ReturnT result_;
};
```

**无返回值特例FunctorMessageHandler** 返回值类型为 void 的函数的FunctorMessageHandler特化版本
    

```cpp
// Specialization for ReturnT of void.
template <class FunctorT>
class FunctorMessageHandler<void, FunctorT> : public MessageHandler {
  public:
  explicit FunctorMessageHandler(FunctorT&& functor)
      : functor_(std::forward<FunctorT>(functor)) {}
  virtual void OnMessage(Message* msg) { functor_(); }
  void result() const {}
  void MoveResult() {}
  private:
  FunctorT functor_;
};
```

### 总结

至此，基本上将MQ相关的“边角料”介绍完毕了，重点的知识再回顾下：

  * WebRTC中有两类消息需要在消息循环中得以处理，即时消息Message以及延迟消息DelayedMessage。他们被投递进入消息循环时，分别进入不同的队列，即时消息Message进入MessageLits类别的即时消息队列，该队列是先入先出的对列，这类消息期待得到立即的处理；延迟消息DelayedMessage进入PriorityQueue类别的延迟消息队列，该队列是优先级队列，根据延迟消息本身的触发时间以及消息序号进行排序，越早触发的消息将越早得以处理。如果再算上线程上同步发送消息，同步阻塞执行方法的话还有另外一个SendList，当然，这不是本文需要说明的内容了。
  * 消息数据的类别有好多种，各自起到不同的作用，尤其要注意DisposeData用来利用消息循环处理消息的功能来自然而然地销毁某个类别的数据。
  * 消息处理器最重要的就是其OnMessage方法，该方法是消息最终得以处理的地方。WebRTC中的很多重要的类就是MessageHandler的子类，比如PeerConnection；
  * 消息处理器的子类FunctorMessageHandler为跨线程执行方法提供了便利，后续会在线程相关的文章中重点阐述。

<hr/>


#### <p>原文出处：<a href='https://blog.csdn.net/ice_ly000/article/details/103178697' target='blank'>WebRTC源码分析-线程基础之MessageQueue</a></p>

### 前言

MessageQueue提供了两方面的功能，消息循环中的消息队列功能以及通过持有SocketServer对象带来的IO多路复用功能。在MessageQueue内部这两部分功能不是完全孤立的，而是相互配合在一起使用。尤其是在MessageQueue的核心方法Get()中体现得淋漓尽致。

MessageQueue的实现位于`rtc_base/message_queue.h`以及`rtc_base/message_queue.cc`中，其声明如下：


```cpp
class MessageQueue {
 public:
  static const int kForever = -1;
 
  MessageQueue(SocketServer* ss, bool init_queue);
  MessageQueue(std::unique_ptr<SocketServer> ss, bool init_queue);
  virtual ~MessageQueue();
 
  SocketServer* socketserver();
 
  virtual void Quit();
  virtual bool IsQuitting();
  virtual void Restart();
  virtual bool IsProcessingMessagesForTesting();
 
  virtual bool Get(Message* pmsg, int cmsWait = kForever, bool process_io = true);
  virtual bool Peek(Message* pmsg, int cmsWait = 0);
  virtual void Post(const Location& posted_from, MessageHandler* phandler,
                    uint32_t id = 0, MessageData* pdata = nullptr, bool time_sensitive = false);
  virtual void PostDelayed(const Location& posted_from, int cmsDelay,
                           MessageHandler* phandler, uint32_t id = 0, MessageData* pdata = nullptr);
  virtual void PostAt(const Location& posted_from, int64_t tstamp,
                      MessageHandler* phandler, uint32_t id = 0, MessageData* pdata = nullptr);
  // TODO(honghaiz): Remove this when all the dependencies are removed.
  virtual void PostAt(const Location& posted_from, uint32_t tstamp,
                      MessageHandler* phandler, uint32_t id = 0, MessageData* pdata = nullptr);
  virtual void Clear(MessageHandler* phandler, uint32_t id = MQID_ANY,
                              MessageList* removed = nullptr);
  virtual void Dispatch(Message* pmsg);
  virtual void ReceiveSends();
 
  // Amount of time until the next message can be retrieved
  virtual int GetDelay();
 
  bool empty() const { return size() == 0u; }
  size_t size() const {
    CritScope cs(&crit_);  // msgq_.size() is not thread safe.
    return msgq_.size() + dmsgq_.size() + (fPeekKeep_ ? 1u : 0u);
  }
 
  // Internally posts a message which causes the doomed object to be deleted
  template <class T>
  void Dispose(T* doomed) {
    if (doomed) {
      Post(RTC_FROM_HERE, nullptr, MQID_DISPOSE, new DisposeData<T>(doomed));
    }
  }
 
  sigslot::signal0<> SignalQueueDestroyed;
 
 protected:
  class PriorityQueue : public std::priority_queue<DelayedMessage> {
   public:
    container_type& container() { return c; }
    void reheap() { make_heap(c.begin(), c.end(), comp); }
  };
 
  void DoDelayPost(const Location& posted_from, int64_t cmsDelay, int64_t tstamp, 
                   MessageHandler* phandler, uint32_t id, MessageData* pdata);
 
  void DoInit();
 
  void ClearInternal(MessageHandler* phandler, uint32_t id,
                     MessageList* removed) RTC_EXCLUSIVE_LOCKS_REQUIRED(&crit_);
 
  void DoDestroy() RTC_EXCLUSIVE_LOCKS_REQUIRED(&crit_);
 
  void WakeUpSocketServer();
 
  bool fPeekKeep_;
  Message msgPeek_;
  MessageList msgq_ RTC_GUARDED_BY(crit_);
  PriorityQueue dmsgq_ RTC_GUARDED_BY(crit_);
  uint32_t dmsgq_next_num_ RTC_GUARDED_BY(crit_);
  CriticalSection crit_;
  bool fInitialized_;
  bool fDestroyed_;
 
 private:
  volatile int stop_;
  SocketServer* const ss_;
  std::unique_ptr<SocketServer> own_ss_;
 
  RTC_DISALLOW_IMPLICIT_CONSTRUCTORS(MessageQueue);
};
```

### MQ的基本成员

根据功能划分，可以将MQ的基本成员分为三类  

MQ状态指示：

  * `bool fInitialized_`：指示MQ已经被初始化，即已经被添加到MQM的管理队列中；
  * `bool fDestroyed_`：指示MQ已经被销毁，即已经被MQM移除，并且MQ将立马被析构；
  * `volatile int stop_`：指示MQ是否已经Quit，即停止工作，不继续接受处理消息；

消息循环相关：MQ中有3个地方存储了消息：`msgPeek_`，`msgq_`，`dmsgq_`。

  * `MessageList msgq_ RTC_GUARDED_BY(crit_)`：即时消息列表，存储即时消息，先入先出；
  * `PriorityQueue dmsgq_ RTC_GUARDED_BY(crit_)`：延迟消息列表，存储延迟消息，按触发时间排序；
  * `uint32_t dmsgq_next_num_ RTC_GUARDED_BY(crit_)`：下一个延迟消息的序号，单调递增；
  * `Message msgPeek_`：存储被Peek出来的一个即时消息；
  * `bool fPeekKeep_`：指示是否存在一个被Peek出来的消息；

IO多路复用相关：

  * `SocketServer* const ss_`：持有的SocketServer类，用以完成IO多路复用操作；
  * `std::unique_ptr<SocketServer> own_ss_`： 与`ss_`一样，只是经过转移语句，使得该SocketServer对象只由该MQ持有。

### MQ的构造及析构

**构造** 做了这么几件事：初始化所有的成员；断言ss不能传空指针，将MQ的指针传递给ss使得二者相互持有相互访问；将MQ加入到MQM的管理指针，`fInitialized_`标志置为true，指示该MQ已经初始化完成。
    

```cpp
MessageQueue::MessageQueue(SocketServer* ss, bool init_queue)
    : fPeekKeep_(false), dmsgq_next_num_(0), fInitialized_(false),
      fDestroyed_(false), stop_(0), ss_(ss) {
  RTC_DCHECK(ss);
  ss_->SetMessageQueue(this);
  if (init_queue) {
    DoInit();
  }
}
 
MessageQueue::MessageQueue(std::unique_ptr<SocketServer> ss, bool init_queue)
    : MessageQueue(ss.get(), init_queue) {
  own_ss_ = std::move(ss);
}
 
void MessageQueue::DoInit() {
  if (fInitialized_) {
    return;
  }
  fInitialized_ = true;
  MessageQueueManager::Add(this);
}
```

**析构** 基本上是构造的逆操作：设置fDestroyed_为true，表示MQ被销毁；发送信号SignalQueueDestroyed()告知关注了MQ的对象不要再访问该MQ了；从MQM中移除自己；清理MQ中的所有消息；从ss中移除MQ的指针。
    

```cpp
MessageQueue::~MessageQueue() {
  DoDestroy();
}
 
void MessageQueue::DoDestroy() {
  if (fDestroyed_) {
    return;
  }
  fDestroyed_ = true;
  // The signal is done from here to ensure
  // that it always gets called when the queue
  // is going away.
  SignalQueueDestroyed();
  MessageQueueManager::Remove(this);
  ClearInternal(nullptr, MQID_ANY, nullptr);
 
  if (ss_) {
    ss_->SetMessageQueue(nullptr);
  }
}
```

### MQ的Size

由于MQ有3个地方存储了消息，一个是Peek消息`msgPeek_`，一个即时消息队列`msgq_`，一个是延迟消息队列`dmsgq_`。那么计算MQ中存储的消息个数时，这三个地方都得算上。


```cpp
bool empty() const { return size() == 0u; }

size_t size() const {
  CritScope cs(&crit_);  // msgq_.size() is not thread safe.
  return msgq_.size() + dmsgq_.size() + (fPeekKeep_ ? 1u : 0u);
}
```

### MQ的运行状态

MQ的运行状态由成员volatile int stop_来指示，相关的函数有以下几个，如源码所示。方法都非常简单，无非就是对`stop_`变量进行原子性的置1和置0，本身就是线程安全的，所有并没有上锁。另外需要知道的几点如下：

  * 当MQ停止运行后，MQ将不再接受处理Send，Post消息；
  * 当MQ停止运行时，已经成功投递的消息仍将会被处理；
  * 为了确保上述这点，MessageHandler的销毁和MessageQueue的销毁是独立，分开的；
  * 并非所有的MQ都会处理消息，比如SignalThread线程。在这种情况下，为了确定投递的消息是否会被处理，应该使用IsProcessingMessagesForTesting()探知下。
    

```cpp
void MessageQueue::Quit() {
  AtomicOps::ReleaseStore(&stop_, 1);
  WakeUpSocketServer();
}
 
bool MessageQueue::IsQuitting() {
  return AtomicOps::AcquireLoad(&stop_) != 0;
}
 
bool MessageQueue::IsProcessingMessagesForTesting() {
  return !IsQuitting();
}
 
void MessageQueue::Restart() {
  AtomicOps::ReleaseStore(&stop_, 0);
}
```

### 消息获取

MQ中消息获取相关的函数有两个，Peek()与Get()，其中Get()是核心内容，再看Get()方法之前，先看看Peek()方法干了啥~~

**Peek()：** 简而言之就是查看之前是否已经Peek过一个MSG到成员`msgPeek_`中，若已经Peek过一个则直接将该消息返回；若没有，则通过Get()方法从消息队列中取出一个消息，成功则将该消息交给`msgPeek_`成员，并将`fPeekKeep_`标志置为true。
    

```cpp
bool MessageQueue::Peek(Message* pmsg, int cmsWait) {
  // fPeekKeep_为真，表示已经Peek过一个MSG到msgPeek_
  // 直接将该MSG返回
  if (fPeekKeep_) {
    *pmsg = msgPeek_;
    return true;
  }
  // 若没有之前没有Peek过一个MSG
  if (!Get(pmsg, cmsWait))
    return false;
  //将Get到的消息放在msgPeek_中保存，并设置标志位
  msgPeek_ = *pmsg;
  fPeekKeep_ = true;
  return true;
}
```

**Get()：**方法的声明如下所示，注释说明了Get()方法的内部算法的流程，Get()方法会阻塞的处理IO，直到有消息可以处理 或者 cmsWait时间已经过去 或者 Stop()方法被调用。
    

```cpp
// Get() will process I/O until:
//  1) A message is available (returns true)
//  2) cmsWait seconds have elapsed (returns false)
//  3) Stop() is called (returns false)
virtual bool Get(Message* pmsg,
                  int cmsWait = kForever,
                  bool process_io = true);
```

源码如下：


```cpp
bool MessageQueue::Get(Message* pmsg, int cmsWait, bool process_io) {
  // 是否存在一个Peek过的消息没有被处理？
  // 优先处理该消息                                                                     // 步骤1
  if (fPeekKeep_) {                                                                              
    *pmsg = msgPeek_;
    fPeekKeep_ = false;
    return true;
  }
 
  int64_t cmsTotal = cmsWait;
  int64_t cmsElapsed = 0;
  int64_t msStart = TimeMillis();
  int64_t msCurrent = msStart;
  while (true) {
    // 检查是否有send消息，若存在，先阻塞处理send消息                                     // 步骤2      
    ReceiveSends();                                                                              
 
    // 检查所有post消息(即时消息+延迟消息)
    int64_t cmsDelayNext = kForever;
    bool first_pass = true;
    while (true) {
       // 上锁进行消息队列的访问
      {
        CritScope cs(&crit_);
        // 内部第一次循环，先检查延迟消息队列                                           // 步骤3
        if (first_pass) {                                                                        
          first_pass = false;
          // 将延迟消息队列dmsgq_中已经超过触发时间的消息全部取出放入到即时消息队列msgq_中
          // 计算当前时间距离下一个最早将要到达触发时间的消息还有多长时间cmsDelayNext。
          while (!dmsgq_.empty()) {
            if (msCurrent < dmsgq_.top().msTrigger_) {
              cmsDelayNext = TimeDiff(dmsgq_.top().msTrigger_, msCurrent);
              break;
            }
            msgq_.push_back(dmsgq_.top().msg_);
            dmsgq_.pop();
          }
        }
        // 从即时消息队列msgq_队首取出第一个消息                                     // 步骤4
        if (msgq_.empty()) {                                                                  
          break;
        } else {
          *pmsg = msgq_.front();
          msgq_.pop_front();
        }
      }  // crit_ is released here.
 
      // 如果消息对时间敏感，那么如果超过了最大忍耐时间kMaxMsgLatency才被处理
      // 则打印警告日志
      if (pmsg->ts_sensitive) {
        int64_t delay = TimeDiff(msCurrent, pmsg->ts_sensitive);
        if (delay > 0) {
          RTC_LOG_F(LS_WARNING)
              << "id: " << pmsg->message_id
              << "  delay: " << (delay + kMaxMsgLatency) << "ms";
        }
      }
      // 如果取出是需要销毁的消息，则销毁该消息，继续取下一个消息。
      if (MQID_DISPOSE == pmsg->message_id) {
        RTC_DCHECK(nullptr == pmsg->phandler);
        delete pmsg->pdata;
        *pmsg = Message();
        continue;
      }
      return true;
    }
    
    // 走到这，说明当前没有消息要处理，很可能是处于Quit状态了，先判断一下
    if (IsQuitting())
      break;
    
    // 计算留给IO处理的时间                                                       // 步骤5
    int64_t cmsNext;                                                                           
    if (cmsWait == kForever) {    //Get无限期，那么距离下个延迟消息的时间就作为本次IO处理时间
      cmsNext = cmsDelayNext;
    } else {      // Get有超时时间，计算本次IO处理时间
      cmsNext = std::max<int64_t>(0, cmsTotal - cmsElapsed);   // 总体来说还剩多少时间
      if ((cmsDelayNext != kForever) && (cmsDelayNext < cmsNext))  // 总体剩余时间和下一个延迟消息触发时间谁先到达？取其短者
        cmsNext = cmsDelayNext;
    }
 
    {
      // 阻塞处理IO多路复用                                                     // 步骤6
      if (!ss_->Wait(static_cast<int>(cmsNext), process_io))                  
        return false;
    }
 
    // 计算是否所有时间都已耗尽，是否进入下一个大循环                             // 步骤7
    msCurrent = TimeMillis();                                    
    cmsElapsed = TimeDiff(msCurrent, msStart);
    if (cmsWait != kForever) {
      if (cmsElapsed >= cmsWait)
        return false;
    }
  }
  return false;
}
```

上述算法过程是整个消息循环的核心内容，如上注释，大概可以分为7个步骤：

  1. **检查Peek消息。**先检查之前是否已经Peek过一个消息到`msgPeek_`还未被处理，若有，当前就处理该消息吧，函数返回~ 若无，继续处理其他消息。
  2. **通过执行 ReceiveSends() 方法来处理所有Send消息。**在MQ中该方法为virtual方法，啥也不干，Thread类继承MQ后会实现该方法，在此方法中处理所有Send消息。因此，消息循环中其实优先，阻塞地先处理所有Send消息，实现跨线程的Send消息方法。
  3. **处理Post消息中的延迟消息。**从延迟消息队列`dmsgq_`中取出所有已经到达触发时间点的延迟消息，并塞入即时消息队列`msgq_`的队尾。同时计算下一个延迟消息还过多久将被触发（如果延迟消息队列中还有未超时的消息），这个时间可能会被作为后续IO多路复用处理的超时时间。这点在redis，nginx上理念一致。
  4. **处理即时消息。**取出即时消息队列`msgq_`的队首消息。若该消息是个要销毁的消息，那么销毁该消息，并取下一个即时消息；若取到一个非要销毁的即时消息，那么就先处理该即时消息吧，函数返回；若本步骤没有取到即时消息，表示当前没有消息要处理，那干点啥好呢~处理网络IO吧
  5. **计算留给网络IO的时间。**消息处理才是迫切的，网络IO嘛，看我能给你分配多少时间吧~~ 分两种情形来对待：

1）若外部Get方法无限期，那么下一个延迟消息触发时间到来之前我都可以用来处理IO；若是延迟队列中没有延迟消息呢？也就是消息循环队列中没有任何要处理的消息了，那当然我就可以无限期地，阻塞地将时间都用来处理IO了，直到有消息进入消息队列，将消息循环从IO处理中唤醒为止，继续处理消息。  
2）若外部Get方法是有超时时间的，那么我们有必要先计算下已经花费了多长时间，到此刻，我们总共最多还剩多长时间留给IO处理。将总剩余时间跟下一个延迟消息触发时间做个比较，哪个小取哪个作为IO处理的时间；若是延迟队列中没有延迟消息呢？那就将剩下的所有时间都交给IO处理咯，反正也没有消息要处理~

  6. **IO多路复用处理。** 阻塞地花费上述计算好的时间进行IO处理。过程中要是处理出错，则函数返回；若是处理时间耗完或者时间没有耗完，但是有新消息进入循环了使得阻塞式的IO处理被唤醒，那么进入下个步骤。
  7. **计算剩余时间。**既然消息已经被处理完过一次，IO也处理完了，先计算下是不是所有时间都已经耗尽？耗尽时间了，我还没找到可用的即时消息，sorry~函数返回false；没有耗尽的话，那么我们计算下剩余的时间，并将剩余的时间把2-7过程再来一遍吧：处理Send消息，检查延迟消息，检查并返回即时消息，再次计算IO处理时间，IO处理，再次计算剩余时间。什么？为什么没有重复步骤1检查Peek消息？同一个线程中我既然在执行Get，怎么可能Peek嘛，怎么可能又蹦跶出一个Peek消息呢？

### 消息投递

MQ中消息投递相关的函数有这么几个：Post()，PostDelayed()，两个PostAt()，DoDelayPost()。其中Post()用于投递即时消息；PostDelayed()，两个PostAt()用于投递延迟消息，内部都是调用DoDelayPost()来实现。

**Post()：** 即时消息的投递，源码如下。主要就是将函数的入参封装成一个即时消息Message对象，然后放置到即时队列`msgq_`的队尾。需要注意的有四点：

  * 如果消息循环已经处理停止状态，即stop_状态值不为0，那么消息循环拒绝消息入队，消息数据会被释放掉。此时，投递消息者是不知情的。
  * 如果消息对时间敏感，即想知道该消息是否即时被处理了，最大延迟不超过kMaxMsgLatency 150ms；
  * 为了线程安全，队列的入队操作是需要加锁的，`CritScope cs(&crit_)`对象的构造和析构确保了这点；
  * 消息入队后，由于处理消息是首要任务，因此，需要调用WakeUpSocketServer()使得IO多路复用的处理赶紧返回，即调用`ss_->WakeUp()`方法实现。由于这块儿是IO多路复用实现内容，后续会专门写文章分析，此处只要知道该方法能够使得阻塞式的IO多路复用能结束阻塞，回到消息处理上来即可。
    
```cpp
void MessageQueue::Post(const Location& posted_from, MessageHandler* phandler,
                        uint32_t id,  MessageData* pdata,  bool time_sensitive) {
  if (IsQuitting()) {
    delete pdata;
    return;
  }
  {
    CritScope cs(&crit_);
    Message msg;
    msg.posted_from = posted_from;
    msg.phandler = phandler;
    msg.message_id = id;
    msg.pdata = pdata;
    if (time_sensitive) {
      msg.ts_sensitive = TimeMillis() + kMaxMsgLatency;
    }
    msgq_.push_back(msg);
  }
  WakeUpSocketServer();
}
 
void MessageQueue::WakeUpSocketServer() {
  ss_->WakeUp();
}
```

**PostDelayed()，PostAt()，DoDelayPost()：** 延迟消息的投递，源码如下。PostDelayed()，PostAt()均是将各自的入参稍作转换后，再调用DoDelayPost()方法，将入参封装成延迟消息DelayedMesssage，然后加入到延迟消息队列dmsgq_中，并从IO多路复用的阻塞中唤醒来处理消息。与Post()方法中的做法并无二致。需要额外注意的地方有这么几点：

  * 延迟消息的序号计算，成员`dmsgq_next_num_`是一个`uint32_t`类型的数据，也即处理4,294,967,296条消息后会溢出回归到0，此时，优先级队里中消息的排序可能会受到影响。但是考虑到一点，正如源码注释上解释的那样：优先级队里中的消息会优先按照触发时间排序，那么最多影响到的不过是那些触发时间相同的消息而已。即便是影响到了部分触发时间相同的消息，那也不过是很短的时间，并不会造成很大的影响。
  * 一点疑惑：任然是延迟消息序号的问题，源码上使用了`RTC_DCHECK_NE(0, dmsgq_next_num_)`，在debug模式下进行断言。当`dmsgq_next_num_`溢出回归为0时，必将触发断言，那么debug模式下，只让每个消息循环处理这么多条消息？
    

```cpp
void MessageQueue::PostDelayed(const Location& posted_from, int cmsDelay,
                               MessageHandler* phandler, uint32_t id, MessageData* pdata) {
  return DoDelayPost(posted_from, cmsDelay, TimeAfter(cmsDelay), phandler, id,
                     pdata);
}

void MessageQueue::PostAt(const Location& posted_from, uint32_t tstamp,
                          MessageHandler* phandler, uint32_t id, MessageData* pdata) {
  // This should work even if it is used (unexpectedly).
  int64_t delay = static_cast<uint32_t>(TimeMillis()) - tstamp;
  return DoDelayPost(posted_from, delay, tstamp, phandler, id, pdata);
}

void MessageQueue::PostAt(const Location& posted_from, int64_t tstamp,
                          MessageHandler* phandler, uint32_t id, MessageData* pdata) {
  return DoDelayPost(posted_from, TimeUntil(tstamp), tstamp, phandler, id,
                     pdata);
}

void MessageQueue::DoDelayPost(const Location& posted_from, int64_t cmsDelay, int64_t tstamp,
                               MessageHandler* phandler, uint32_t id, MessageData* pdata) {
  if (IsQuitting()) {
    delete pdata;
    return;
  }
 
  {
    CritScope cs(&crit_);
    Message msg;
    msg.posted_from = posted_from;
    msg.phandler = phandler;
    msg.message_id = id;
    msg.pdata = pdata;
    DelayedMessage dmsg(cmsDelay, tstamp, dmsgq_next_num_, msg);
    dmsgq_.push(dmsg);
    // If this message queue processes 1 message every millisecond for 50 days,
    // we will wrap this number.  Even then, only messages with identical times
    // will be misordered, and then only briefly.  This is probably ok.
    ++dmsgq_next_num_;
    RTC_DCHECK_NE(0, dmsgq_next_num_);
  }
  WakeUpSocketServer();
}
```

### 消息处理

**Dispatch()：**方法内容一目了然，先打印一条trace日志；然后记录消息处理的开始时间`start_time`；调用消息的MessageHandler的OnMessage方法进行消息处理；记录消息处理的结束时间`end_time`；计算消息处理花费了多长时间diff，如果消息花费时间过程，超过kSlowDispatchLoggingThreshold（50ms），则打印一条警告日志，告知从哪儿构建的消息花费了多长时间才消费完。
    

```cpp
void MessageQueue::Dispatch(Message* pmsg) {
  TRACE_EVENT2("webrtc", "MessageQueue::Dispatch", "src_file_and_line",
                pmsg->posted_from.file_and_line(), "src_func",
                pmsg->posted_from.function_name());
  int64_t start_time = TimeMillis();
  pmsg->phandler->OnMessage(pmsg);
  int64_t end_time = TimeMillis();
  int64_t diff = TimeDiff(end_time, start_time);
  if (diff >= kSlowDispatchLoggingThreshold) {
    RTC_LOG(LS_INFO) << "Message took " << diff
                      << "ms to dispatch. Posted from: "
                      << pmsg->posted_from.ToString();
  }
}
```

### 消息清理

**Clear()：** 清理函数逻辑也相当简单，目标也相当明确，就是要讲满足条件的消息从MQ中删除。需要注意的点有以下几个：

  * 线程安全，上锁处理；
  * MQ中消息可能存在的位置有3个：Peek消息`msgPeek_`，即时消息队列`msgq_`，延迟消息队列`dmsgq_`；因此，需要从这3个地方去挨个查找能匹配的消息。
  * 如果Clear()方法传入了一个MessageList* removed，匹配的消息都会进入该list；若是没有传入这样一个list，那么消息数据都将会立马销毁。
    
```cpp
void MessageQueue::Clear(MessageHandler* phandler, uint32_t id, MessageList* removed) {
  CritScope cs(&crit_);
  ClearInternal(phandler, id, removed);
}
 
void MessageQueue::ClearInternal(MessageHandler* phandler, uint32_t id, MessageList* removed) {
  // Remove messages with phandler
  if (fPeekKeep_ && msgPeek_.Match(phandler, id)) {
    if (removed) {
      removed->push_back(msgPeek_);
    } else {
      delete msgPeek_.pdata;
    }
    fPeekKeep_ = false;
  }
 
  // Remove from ordered message queue
  for (MessageList::iterator it = msgq_.begin(); it != msgq_.end();) {
    if (it->Match(phandler, id)) {
      if (removed) {
        removed->push_back(*it);
      } else {
        delete it->pdata;
      }
      it = msgq_.erase(it);
    } else {
      ++it;
    }
  }
 
  // Remove from priority queue. Not directly iterable, so use this approach
  PriorityQueue::container_type::iterator new_end = dmsgq_.container().begin();
  for (PriorityQueue::container_type::iterator it = new_end;
       it != dmsgq_.container().end(); ++it) {
    if (it->msg_.Match(phandler, id)) {
      if (removed) {
        removed->push_back(it->msg_);
      } else {
        delete it->msg_.pdata;
      }
    } else {
      *new_end++ = *it;
    }
  }
  dmsgq_.container().erase(new_end, dmsgq_.container().end());
  dmsgq_.reheap();
}
```

### 销毁消息

**Dispose()：** 之前在[WebRTC源码分析-线程基础之Message && MessageData && MessageHandler](https://www.jianshu.com/p/f0dca647c4fa)中对DisposeData消息数据专门进行过阐述。再配合之前Get()方法中对DisposeData消息数据的处理方式，我们很容易理解该函数的作用：如果想要销毁某个对象，而不方便立马销毁，那么就可以将调用消息循环的Dispose()方法让消息循环帮忙进行数据销毁。
    

```cpp
// Internally posts a message which causes the doomed object to be deleted
template <class T>
void Dispose(T* doomed) {
  if (doomed) {
    Post(RTC_FROM_HERE, nullptr, MQID_DISPOSE, new DisposeData<T>(doomed));
  }
}
```
