 
<!--BEGIN_DATA
{
    "create_date": "2022-02-24 14:40", 
    "modify_date": "2022-02-24 14:40", 
    "is_top": "0", 
    "summary": "WebRTC Pacing之IntervalBudget分析<br/>WebRTC Pacing之RoundRobinPacketQueue分析<br/>WebRTC Pacing模块", 
    "tags": "WebRTC", 
    "file_name": "WebRTC Pacing.md"
}
END_DATA-->

#### <p>原文出处：<a href='https://zhuanlan.zhihu.com/p/184944074' target='blank'>WebRTC Pacing之IntervalBudget分析</a></p>

WebRTC中Pacing等模块需要按照指定的码率发送报文，保证码率稳定，会用到`IntervalBudget`这个类，这个类是控制码率平稳的核心。本篇将介绍`IntervalBudget`这个类。

## 1. IntervalBudget原理

`IntervalBudget`顾名思义，就是一段时间内的发送码率预算。 `IntervalBudget`根据时间流逝增加budget，报文发送后减少budget，每次发送报文前判断剩余budget是否足够，如果不足则取消本次发送。

举个例子 :

  * 当前目标码率设置为1000kbps，剩余预算100bytes。
  * 距离上次更新相隔50ms，那么budget就多了`1000kbps*50/8=600bytes`， 剩余`100+600=700bytes`；
  * 如果当前发送一个1000bytes的报文，先判断是否有剩余budget，当前700bytes肯定有剩余，因此可以发送，并减少budget，剩余`700-1000=-300bytes`。

`IntervalBudget`这个类比较小，因此这里直接贴上其声明：

```cpp
class IntervalBudget {
 public:
  explicit IntervalBudget(int initial_target_rate_kbps);
  IntervalBudget(int initial_target_rate_kbps, bool can_build_up_underuse);
  // 设置目标发送码率
  void set_target_rate_kbps(int target_rate_kbps);

  // 时间流逝后增加budget
  void IncreaseBudget(int64_t delta_time_ms);
  // 发送数据后减少budget
  void UseBudget(size_t bytes);

  // 剩余budget
  size_t bytes_remaining() const;
  // 剩余budget占当前窗口数据量比例
  double budget_ratio() const;
  // 目标发送码率
  int target_rate_kbps() const;

 private:
  // 设置的目标码率，按照这个码率控制数据发送
  int target_rate_kbps_;
  // 窗口内（500ms）对应的最大字节数=窗口大小*target_rate_kbps_/8
  int64_t max_bytes_in_budget_;
  // 剩余可发送字节数，限制范围:[-max_bytes_in_budget_, max_bytes_in_budget_]
  int64_t bytes_remaining_;
  // 上个周期underuse，本周期是否可以借用上个周期的剩余量
  bool can_build_up_underuse_;
};
```

## 2. budget增加

如果距离上次更新时间相隔`delta_time_ms`，那么随着时间流逝，那么这段时间增长的budget为`delta_time_ms * target_rate_kbps_`：

```cpp
void IntervalBudget::IncreaseBudget(int64_t delta_time_ms) {
  int64_t bytes = target_rate_kbps_ * delta_time_ms / 8;
  // 一般来说，can_build_up_underuse_都会关闭，关于这个开关的介绍见最后一部分介绍
  if (bytes_remaining_ < 0 || can_build_up_underuse_) {
    // We overused last interval, compensate this interval.
    // 如果上次发送的过多（bytes_remaining_ < 0），那么本次发送的数据量会变少
    // 如果开启can_build_up_underuse_，则表明可以累积之前没有用完的预算
    bytes_remaining_ = std::min(bytes_remaining_ + bytes, max_bytes_in_budget_);
  } else {
    // If we underused last interval we can't use it this interval.
    // 1） 如果上次的budget没有用完（bytes_remaining_ > 0），如果没有设置can_build_up_underuse_
    // 不会对上次的补偿，直接清空所有预算，开始新的一轮

    // 2） 如果设置了can_build_up_underuse_标志，那意味着要考虑上次的underuse，
    // 如果上次没有发送完，则本次需要补偿，见上面if逻辑
    bytes_remaining_ = std::min(bytes, max_bytes_in_budget_);
  }
}
```

## 3. 减少budget

发送了数据后需要减少budget，直接减去发送字节数即可：

```cpp
void IntervalBudget::UseBudget(size_t bytes) {
  bytes_remaining_ = std::max(bytes_remaining_ - static_cast<int>(bytes),
                              -max_bytes_in_budget_);
}
```

## 4. 谈谈IntervalBudget窗口大小

这里的窗口目前主要是用来控制`can_build_up_underuse_`开关打开下，`build_up`的上限。 考虑到存在这样的情况，随着时间流逝，我们每5ms都有5ms的budget可供使用，但是并不是每一个5ms我们都能够完全使用掉这5ms的budget，这里称作underuse。因此，`can_build
_up_underuse_`开关允许我们将这些没有用完的预算累计起来，以供后续使用。`kWindowMs = 500ms`意味着我们可以累积500ms这么多没有用完的预算。

打开这个开关好处在于某些时刻，我们短时间内可供发送的预算更多，在码率抖动较大的时候，我们可以更快地将数据发送出去。带来的缺陷是，短时间内的码率控制不够平滑，
在一些低带宽场景影响更大。

<hr>

#### <p>原文出处：<a href='https://zhuanlan.zhihu.com/p/185032135' target='blank'>WebRTC Pacing之RoundRobinPacketQueue分析</a></p>

WebRTC中Pacing模块实现了一个优先级队列`RoundRobinPacketQueue`，它可以push不同优先级的报文，然后可以按照优先级pop并发送出去。`RoundRobinPacketQueue`总结来说有几点需要注意：

  1. `RoundRobinPacketQueue `每一路Stream单独调度，每一路stream有不同优先级，由其packet决定，优先级相同时，发送数据量少的stream有更高的调度优先级
  2. Stream的优先级保存在`RoundRobinPacketQueue`中，每次发送报文后都需要更新
  3. 同一个Stream的报文保存在一个优先级队列中，队列中的数据重传包有更高优先级，先插入的数据有更高优先级
  4. 音频报可能不参与调度

## 1. 对外接口以及相关定义

老规矩，了解一个类的功能前，我们先了解其对外接口：

```cpp
class RoundRobinPacketQueue {
 public:
  ...
  // 插入不同优先级的报文
  void Push(int priority,
            Timestamp enqueue_time,
            uint64_t enqueue_order,
            std::unique_ptr<RtpPacketToSend> packet);
  // 弹出一个即将发送的报文
  std::unique_ptr<RtpPacketToSend> Pop();
  // queue是否empty
  bool Empty() const;
  // 报文总数
  size_t SizeInPackets() const;
  // 报文总字节数
  DataSize Size() const;
  // 下一个pop的报文如果是音频包，则返回该包时间戳，非音频包则返回nullopt
  absl::optional<Timestamp> LeadingAudioPacketEnqueueTime() const;

  // 队列中最旧的报文时间戳
  Timestamp OldestEnqueueTime() const;
  // 队列中的报文按照当前码率发送出去所用到的时间
  TimeDelta AverageQueueTime() const;
  // 更新内部状态
  void UpdateQueueTime(Timestamp now);
  // 暂停queue处理
  void SetPauseState(bool paused, Timestamp now);
  // 计算是考虑传输层overhead，默认不考虑
  void SetIncludeOverhead();
  // 设置传输层的overhead大小
  void SetTransportOverhead(DataSize overhead_per_packet);
  ...
};
```

最重要的接口应该数push和pop，从接口上我们大致了解了其功能，但是实际上其内部处理还是要深入到这个函数里面。

**Stream**

`RoundRobinPacketQueue` 中定义了`Stream`来区分不同的流，每一路有自己的一个优先级队列，以及这路流对应的优先级：

```cpp
struct Stream {
  ...
  // 已经发送的报文总大小，发送较少的stream通常会优先调度
  DataSize size;
  // 该路流对应的ssrc
  uint32_t ssrc;
  // 一个根据StreamPrioKey确定优先级的优先队列
  PriorityPacketQueue packet_queue;

  // stream_priorities_的一个iterator，可以理解成一个指针
  std::multimap<StreamPrioKey, uint32_t>::iterator priority_it;
};
```

**StreamPrioKey**

`Stream`之间优先级比较主要是根据优先级以及stream中报文总大小，因此这里增加了一个`StreamPrioKey`来简化优先级比较：

```cpp
struct StreamPrioKey {
  StreamPrioKey(int priority, DataSize size)
      : priority(priority), size(size) {}

  // 优先级不等时比较优先级，优先级相等时，发送过较少的stream优先级更高
  bool operator<(const StreamPrioKey& other) const {
    if (priority != other.priority)
      return priority < other.priority;
    return size < other.size;
  }

  const int priority;
  const DataSize size;
};
```

**PriorityPacketQueue**

`PriorityPacketQueue`是一个继承于`std::priority_queue<QueuedPacket>`的优先队列，不同stream的数据最终是保存在该优先队列中，建议大家先看看标准库里面的优先队列`std::priority_queue`的操作。 该优先队列内的数据比较方法：

```cpp
bool RoundRobinPacketQueue::QueuedPacket::operator<(
    const RoundRobinPacketQueue::QueuedPacket& other) const {
  // 先判断优先级，优先级相等时判断重传，重传包更高优先级，否则判断插入顺序（order）
  if (priority_ != other.priority_)
    return priority_ > other.priority_;
  if (is_retransmission_ != other.is_retransmission_)
    return other.is_retransmission_;

  return enqueue_order_ > other.enqueue_order_;
}
```

最后看看`RoundRobinPacketQueue`几个重要的成员变量：

```cpp
// StreamPrioKey-ssrc map，Stream中有保存该iterator
std::multimap<StreamPrioKey, uint32_t> stream_priorities_;

// SSRC Stream map
std::map<uint32_t, Stream> streams_;

// 报文入队时间，用于找到最老的报文时间
std::multiset<Timestamp> enqueue_times_;

// 存一个报文的queue
absl::optional<QueuedPacket> single_packet_queue_;
```

## 2. Push数据

`RoundRobinPacketQueue`对插入的数据稍微做了一下封装，`QueuedPacket`增加了优先级、入队列时间、次序、是否是重传、入队时间set的iterator，数据存在

```cpp
void RoundRobinPacketQueue::Push(int priority,
                                 Timestamp enqueue_time,
                                 uint64_t enqueue_order,
                                 std::unique_ptr<RtpPacketToSend> packet) {
  // 没有存储任何报文时直接存在single_packet_queue_中，不进队列
  if (size_packets_ == 0) {
    // Single packet fast-path.
    single_packet_queue_.emplace(
        QueuedPacket(priority, enqueue_time, enqueue_order,
                     enqueue_times_.end(), std::move(packet)));
    UpdateQueueTime(enqueue_time);
    single_packet_queue_->SubtractPauseTime(pause_time_sum_);
    size_packets_ = 1;
    size_ += PacketSize(*single_packet_queue_);
  } else {
    // 如果single_packet_queue_有数据，先push到queue中
    MaybePromoteSinglePacketToNormalQueue();
    // 调用另外一个Push函数插入到队列中
    Push(QueuedPacket(priority, enqueue_time, enqueue_order,
                      enqueue_times_.insert(enqueue_time), std::move(packet)));
  }
}
```

Push插入数据逻辑总结来说是：

  * 根据ssrc找到对应stream，没有则创建stream且暂不调度，优先级指向null
  * 根据stream是否被调度，或者stream优先级是否要刷新，重新调度stream
  * 将报文插入队列，报文可能是从`single_packet_queue_`中提升过来的，逻辑稍有不同

```cpp
void RoundRobinPacketQueue::Push(QueuedPacket packet) {
  // 根据报文ssrc找到对应的stream，没有找到则创建一个新的stream
  auto stream_info_it = streams_.find(packet.Ssrc());
  if (stream_info_it == streams_.end()) {
    stream_info_it = streams_.emplace(packet.Ssrc(), Stream()).first;
    // 暂时没有确定该stream的优先级，即没有被调度
    stream_info_it->second.priority_it = stream_priorities_.end();
    stream_info_it->second.ssrc = packet.Ssrc();
  }

  Stream* stream = &stream_info_it->second;

  // 如果该stream没有被调度，则加入到stream_priorities_中
  if (stream->priority_it == stream_priorities_.end()) {
    // If the SSRC is not currently scheduled, add it to |stream_priorities_|.
    RTC_CHECK(!IsSsrcScheduled(stream->ssrc));
    stream->priority_it = stream_priorities_.emplace(
        StreamPrioKey(packet.Priority(), stream->size), packet.Ssrc());
  } else if (packet.Priority() < stream->priority_it->first.priority) {
    // 当前报文优先级比之前的小，说明优先级有变化，需要更新其优先级
    stream_priorities_.erase(stream->priority_it);
    stream->priority_it = stream_priorities_.emplace(
        StreamPrioKey(packet.Priority(), stream->size), packet.Ssrc());
  }
  RTC_CHECK(stream->priority_it != stream_priorities_.end());

  // 还没有入队时间，说明是从single_packe_queue_中提升过来的
  // 注意packet只保存了一个enqueue_times_的iterator
  if (packet.EnqueueTimeIterator() == enqueue_times_.end()) {
    // Promotion from single-packet queue. Just add to enqueue times.
    packet.UpdateEnqueueTimeIterator(
        enqueue_times_.insert(packet.EnqueueTime()));
  } else {
    // In order to figure out how much time a packet has spent in the queue
    // while not in a paused state, we subtract the total amount of time the
    // queue has been paused so far, and when the packet is popped we subtract
    // the total amount of time the queue has been paused at that moment. This
    // way we subtract the total amount of time the packet has spent in the
    // queue while in a paused state.
    UpdateQueueTime(packet.EnqueueTime());
    packet.SubtractPauseTime(pause_time_sum_);
    
    size_packets_ += 1;
    size_ += PacketSize(packet);
  }

  // 插入到stream的queue中
  stream->packet_queue.push(packet);
}
```

## 3. pop数据

Pop数据的逻辑大致如下：

  * 如果`single_packet_queue_`中有数据，则直接返回该数据，否则
  * 返回优先级最高的stream，获取最前面的数据
  * 更新stream发送字节数、优先级等

```cpp
std::unique_ptr<RtpPacketToSend> RoundRobinPacketQueue::Pop() {
  // 如果single_packe_queue_中有数据，则直接从single_packet_queue_中返回数据
  if (single_packet_queue_.has_value()) {
    RTC_DCHECK(stream_priorities_.empty());
    std::unique_ptr<RtpPacketToSend> rtp_packet(
        single_packet_queue_->RtpPacket());
    single_packet_queue_.reset();
    queue_time_sum_ = TimeDelta::Zero();
    size_packets_ = 0;
    size_ = DataSize::Zero();
    return rtp_packet;
  }

  RTC_DCHECK(!Empty());
  // 每次都是返回优先级最高的stream的报文
  Stream* stream = GetHighestPriorityStream();
  const QueuedPacket& queued_packet = stream->packet_queue.top();

  // 因为有弹出报文，优先级需要更新，更新部分见最后
  stream_priorities_.erase(stream->priority_it);

  // 计算报文在queue中的时间
  TimeDelta time_in_non_paused_state =
      time_last_updated_ - queued_packet.EnqueueTime() - pause_time_sum_;
  queue_time_sum_ -= time_in_non_paused_state;

  // 删除该报文的queue time
  RTC_CHECK(queued_packet.EnqueueTimeIterator() != enqueue_times_.end());
  enqueue_times_.erase(queued_packet.EnqueueTimeIterator());

  // 报文发送后，更新stream发送的报文字节数，发送较少的stream应该有更高的调度优先级
  // 为了避免发送码率较低的stream一致处于较高优先级发送过多，限制了最低发送字节数
  DataSize packet_size = PacketSize(queued_packet);
  stream->size =
      std::max(stream->size + packet_size, max_size_ - kMaxLeadingSize);
  max_size_ = std::max(max_size_, stream->size);

  size_ -= packet_size;
  size_packets_ -= 1;
  RTC_CHECK(size_packets_ > 0 || queue_time_sum_ == TimeDelta::Zero());

  std::unique_ptr<RtpPacketToSend> rtp_packet(queued_packet.RtpPacket());
  stream->packet_queue.pop();

  // 如果剩余报文需要发送，更新调度优先级
  RTC_CHECK(!IsSsrcScheduled(stream->ssrc));
  if (stream->packet_queue.empty()) {
    stream->priority_it = stream_priorities_.end();
  } else {
    int priority = stream->packet_queue.top().Priority();
    stream->priority_it = stream_priorities_.emplace(
        StreamPrioKey(priority, stream->size), stream->ssrc);
  }

  return rtp_packet;
}
```

<hr>

#### <p>原文出处：<a href='https://zhuanlan.zhihu.com/p/184924220' target='blank'>WebRTC Pacing模块</a></p>

今天聊一下WebRTC中的Pacing模块，它的代码位于webrtc源码的`src/modules/pacing`目录，请结合源码阅读本文，加深对pacing的理解。

pacing、pacer、pace，顾名思义，有节奏、按照节奏发送报文的含义，一般我们也称作`平滑发送`。 pacing是拥塞控制中重要的一个环节，它受拥塞控制输出的估计带宽、拥塞窗口大小控制，按照节奏（一般是5ms）保证报文匀速地发送到网络中，可以避免短时间大量报文造成网络情况恶化。

本文将带着大家通过读代码方式深入pacing模块，了解pacing原理。

## 1. 为什么需要pacing

pacing和拥塞控制紧密相关，我们经常需要面对发送超过网络实际带宽出现拥塞的情况。

  * 避免突发流量对网络造成冲击

我们知道视频编码经过压缩后，随着画面复杂性变化，帧大小差异较大从几十k到几M都有（4k桌面共享可能会到几M）。如果将2M的视频编码输出数据在1ms内全部发送到网络中，对于很多网络会造成较大冲击。首先是客户端的socket buffer的输入远远大于输出，socket buffer满了后就会出现丢包；网络中路由器可能无法处理超过的突发流量，会造成网络拥塞甚至是突发的百分之几十的大丢包。

  * 良好的拥塞控制机制依赖pacing

突发流量对网络的冲击造成的拥塞会造成发送端的评估带宽降低，会压制编码码率造成视频质量下降。一般来说，gcc的带宽估计机制也需要依赖pacing，如probing，一些机制可能会将发送码率hold在目标探测带宽，这需要依赖pacing来做到。

如果当前网络带宽存在瓶颈，我们必须要保证当前的发送码率不超过瓶颈，避免发送过多数据造成瞬间的拥塞。pacing可以将瞬间的码率（如1ms）平滑到长窗口中，牺牲发送时间换不拥塞。

  * pacing控制发送优先级

在带宽不够的时候，我们可以在pacing中对报文根据优先级排队，优先保证重要的媒体流。

## 2. 阅读代码前

pacing模块涉及到几个比较独立的类，控制发送码率的`IntervalBudget` 、一个优先队列`RoundRobinPacketQueue`，在深入pacing模块时，在了解pacing大致流程后可以深入了解下这两个类，可以了解更精细的算法：

[言剑：WebRTC IntervalBudget](https://zhuanlan.zhihu.com/p/184944074)

[言剑：WebRTC RoundRobinPacketQueue](https://zhuanlan.zhihu.com/p/185032135)

新的代码里面， 有两种处理模式，周期调度方式（kPeriodic）、动态调度（kDynamic）。

```cpp
// Periodic mode uses the IntervalBudget class for tracking bitrate
// budgets, and expected ProcessPackets() to be called a fixed rate,
// e.g. every 5ms as implemented by PacedSender.
// Dynamic mode allows for arbitrary time delta between calls to
// ProcessPackets.
enum class ProcessMode { kPeriodic, kDynamic };
```

比较传统的是继承Module，周期调用方式来调度；新的代码支持动态调度。最新的的代码Pacer有两个实现：

  * `PacedSender`，支持Module方式的周期调度（如5ms）以及自定义`ProcessThread` 的调度方式（可以动态调度）；
  * `TaskQueuePacedSender`，只支持动态调度 。

以下介绍先不介绍`TaskQueuePacedSender`这种新的Pacer，只关注传统的`PacedSender`周期调度方式。所以，后面涉及到`kDynamic`动态方式的代码都跳过了。

## 3. pacing模块对外接口

pacing模块接收输入的报文（继承`RtpPacketSender`）以及受目标码率控制（`RtpPacketPacer`），经过调度后输出要发送的报文（入参`PacketRouter`）。因此，`PacedSender`的实现如下：

```cpp
class PacedSender : public Module,
                    public RtpPacketPacer,
                    public RtpPacketSender {
    PacedSender(Clock* clock,
        PacketRouter* packet_router,
        RtcEventLog* event_log,
        const WebRtcKeyValueConfig* field_trials = nullptr,
        ProcessThread* process_thread = nullptr);
    ... 
}
```

PacedSender实现了三个接口：

  * `Module`，表明`PacedSender`作为一个模块，实现Process等接口，按照周期处理，后续可能要去掉Module实现，用入参ProcessThread来代替Module的线程处理功能。
  * `RtpPacketPacer`，作为一个Pacer需要实现的接口，主要包括拥塞窗口、pacing rate设置等
  * `RTPPacketSender`，目前只有一个函数`EnqueuePackets`，输入rtp packet

`PacedSender`其参数`PacketRouter`，可以将pacing后的rtp报文路由到不同模块去做实际发送。`PacketRouter`实际上是继承了`PacingController::PacketSender`。

## 4. pacing工作流程

我们从一个包插入pacing后的处理看一下pacing的工作流程。该部分主要包含`PacedSender`、`PacingController`等类的处理，随着代码变迁，`PacedSender`基本包含什么逻辑，都直接通过`PacingController`中处理了， 因此一下重点关注这个类。

### 4.1 输入报文：PacedSender::EnqueuePackets

`EnquuePackts`也是直接把报文交给`PacingController::EnqueuePacket`处理。

```cpp
void PacedSender::EnqueuePackets(
    std::vector<std::unique_ptr<RtpPacketToSend>> packets) {
  {
    rtc::CritScope cs(&critsect_);
    for (auto& packet : packets) {
      pacing_controller_.EnqueuePacket(std::move(packet));
    }
  }
  MaybeWakupProcessThread();
}
```

### 4.2 决策优先级并插入queue：PacingController::EnqueuePacket

`PacingController::EnqueuePacket`中会根据报文类型，给报文赋予发送优先级，并进行后续处理。

```cpp
void PacingController::EnqueuePacket(std::unique_ptr<RtpPacketToSend> packet) {
  // Get priority first and store in temporary, to avoid chance of object being
  // moved before GetPriorityForType() being called.
  const int priority = GetPriorityForType(*packet->packet_type());
  EnqueuePacketInternal(std::move(packet), priority);
}
```

优先级的处理也比较简单：

  * 音频总是第一优先级，通话中音频关注度更高，优先级很高这个很好理解；
  * 重传包优先级为2，因为如果重传耗时太长，重传就失去其效果，所以优先级比较高；
  * 视频包和FEC报文优先级为3；
  * 无关紧要的padding优先级最低。

```cpp
int GetPriorityForType(RtpPacketMediaType type) {
  // Lower number takes priority over higher.
  switch (type) {
    case RtpPacketMediaType::kAudio:
      // Audio is always prioritized over other packet types.
      return kFirstPriority + 1;
    case RtpPacketMediaType::kRetransmission:
      // Send retransmissions before new media.
      return kFirstPriority + 2;
    case RtpPacketMediaType::kVideo:
    case RtpPacketMediaType::kForwardErrorCorrection:
      // Video has "normal" priority, in the old speak.
      // Send redundancy concurrently to video. If it is delayed it might have a
      // lower chance of being useful.
      return kFirstPriority + 3;
    case RtpPacketMediaType::kPadding:
      // Packets that are in themselves likely useless, only sent to keep the
      // BWE high.
      return kFirstPriority + 4;
  }
}
```

最终通过`PacingController::EnqueuePacketInternal`插入queue。在插入queue之前先需要做probing相关处理（probing、和padding功能暂且按下不表），以及会根据Pacing的处理模式（动态和周期两种模式）做budget的更新。

```cpp
void PacingController::EnqueuePacketInternal(
    std::unique_ptr<RtpPacketToSend> packet,
    int priority) {
  prober_.OnIncomingPacket(DataSize::Bytes(packet->payload_size()));
  // TODO(sprang): Make sure tests respect this, replace with DCHECK.
  Timestamp now = CurrentTime();
  if (packet->capture_time_ms() < 0) {
    packet->set_capture_time_ms(now.ms());
  }

  ...
  // 直接插入优先队列中
  packet_queue_.Push(priority, now, packet_counter_++, std::move(packet));
}
```

### 4.3 Pacing模式以及budget处理

插入到queue中，报文插入就告一段落，pacing是另外一个线程中处理。 周期处理方式中用到两个budget来分配media和padding的带宽：

```cpp
IntervalBudget media_budget_;
IntervalBudget padding_budget_;
```

关于IntervalBudget可以参考另一篇：

[言剑：WebRTC IntervalBudget](https://zhuanlan.zhihu.com/p/184944074)

从上面的IntervalBudget介绍可以知道，随着时间流逝，budget增加；报文发送后budget减少。pacing根据是否有budget剩余决定是否可以发送，如果有的话从`RoundRobinQueue`中取最高优先级的报文发送，通过这种方式可以控制发送码率为设置的码率。

budget如何控制：

  * 设置目标码率：`IntervalBudget::set_target_rate_kbps`
  * 获取需要发送的报文：`GetPendingPacket` ，先判断budget是否足够，足够则调用`RoundRobinPacketQueue::Pop`得到需要发送的报文
  * 随着时间流逝（如设置拥塞窗口、插入报文、发送报文时检测），增加窗口`UpdateBudgetWithElapsedTime`->`IntervalBudget::IncreaseBudget`。 
  * 报文发送完成后，需要减少budget：`UpdateBudgetWithSentData`->`IntervalBudget::UseBudget `。 

### 4.4 pacing核心逻辑：PacingController::ProcessPackets

报文插入到queue中，pacer需要周期调度，在budget足够的时候，从queue中取出报文发送，处理逻辑主要看`PacingController::ProcessPackets`，函数比较长，这里带着大家啃下来。至于怎么从queue取出报文，先发送哪个可以看`RoundRobinPacketQueue`介绍：

[言剑：WebRTC RoundRobinPacketQueue](https://zhuanlan.zhihu.com/p/185032135)

删除了动态处理的代码后如下，主要逻辑可以总结为：根据拥塞状态以及budget是否足够，从queue中获取需要发送的报文，可以发送则发送媒体报文，否则判断是否发送padding；如果队列中数据过多，可能需要增大码率做排空处理；

```cpp
void PacingController::ProcessPackets() {
  Timestamp now = CurrentTime();
  Timestamp target_send_time = now;
  ...
  
  Timestamp previous_process_time = last_process_time_;
  // 距离上次处理的时间，限制不超过2s
  TimeDelta elapsed_time = UpdateTimeAndGetElapsed(now);

  // 1） 保活，没啥好讲的
  if (ShouldSendKeepalive(now)) {
    // We can not send padding unless a normal packet has first been sent. If
    // we do, timestamps get messed up.
    if (packet_counter_ == 0) {
      last_send_time_ = now;
    } else {
      DataSize keepalive_data_sent = DataSize::Zero();
      std::vector<std::unique_ptr<RtpPacketToSend>> keepalive_packets =
          packet_sender_->GeneratePadding(DataSize::Bytes(1));
      for (auto& packet : keepalive_packets) {
        keepalive_data_sent +=
            DataSize::Bytes(packet->payload_size() + packet->padding_size());
        packet_sender_->SendPacket(std::move(packet), PacedPacketInfo());
      }
      OnPaddingSent(keepalive_data_sent);
    }
  }

  if (paused_) {
    return;
  }

  // 2） 如果开启了drain_large_queues_，queue中的数据难以以当前速率在剩余时间内发送出去
  // 则适当提高当前发送码率（通过修改budget）
  if (elapsed_time > TimeDelta::Zero()) {
    DataRate target_rate = pacing_bitrate_;
    DataSize queue_size_data = packet_queue_.Size();
    if (queue_size_data > DataSize::Zero()) {
      // Assuming equal size packets and input/output rate, the average packet
      // has avg_time_left_ms left to get queue_size_bytes out of the queue, if
      // time constraint shall be met. Determine bitrate needed for that.
      packet_queue_.UpdateQueueTime(now);
      if (drain_large_queues_) {
        TimeDelta avg_time_left =
            std::max(TimeDelta::Millis(1),
                     queue_time_limit - packet_queue_.AverageQueueTime());
        DataRate min_rate_needed = queue_size_data / avg_time_left;
        if (min_rate_needed > target_rate) {
          target_rate = min_rate_needed;
          RTC_LOG(LS_VERBOSE) << "bwe:large_pacing_queue pacing_rate_kbps="
                              << target_rate.kbps();
        }
      }
    }
    
    // 提高当前budget，用于尽快排空
    if (mode_ == ProcessMode::kPeriodic) {
      // In periodic processing mode, the IntevalBudget allows positive budget
      // up to (process interval duration) * (target rate), so we only need to
      // update it once before the packet sending loop.
      media_budget_.set_target_rate_kbps(target_rate.kbps());
      UpdateBudgetWithElapsedTime(elapsed_time);
    } else {
      media_rate_ = target_rate;
    }
  }

  // 3） 获取probing大小
  bool first_packet_in_probe = false;
  bool is_probing = prober_.is_probing();
  PacedPacketInfo pacing_info;
  absl::optional<DataSize> recommended_probe_size;
  if (is_probing) {
    pacing_info = prober_.CurrentCluster();
    first_packet_in_probe = pacing_info.probe_cluster_bytes_sent == 0;
    recommended_probe_size = DataSize::Bytes(prober_.RecommendedMinProbeSize());
  }

  DataSize data_sent = DataSize::Zero();

  // The paused state is checked in the loop since it leaves the critical
  // section allowing the paused state to be changed from other code.
  while (!paused_) {
    
    // 4） 第一次probing，padding包比较小，更可靠的探测
    if (small_first_probe_packet_ && first_packet_in_probe) {
      // If first packet in probe, insert a small padding packet so we have a
      // more reliable start window for the rate estimation.
      auto padding = packet_sender_->GeneratePadding(DataSize::Bytes(1));
      // If no RTP modules sending media are registered, we may not get a
      // padding packet back.
      if (!padding.empty()) {
        // Insert with high priority so larger media packets don't preempt it.
        EnqueuePacketInternal(std::move(padding[0]), kFirstPriority);
        // We should never get more than one padding packets with a requested
        // size of 1 byte.
        RTC_DCHECK_EQ(padding.size(), 1u);
      }
      first_packet_in_probe = false;
    }

    ...

    // 5） 获取需要发送的报文，需要检查是否拥塞、budget是否足够
    // Fetch the next packet, so long as queue is not empty or budget is not
    // exhausted.
    std::unique_ptr<RtpPacketToSend> rtp_packet =
        GetPendingPacket(pacing_info, target_send_time, now);

    // 6） 当前无法发送媒体包，检查是否发送padding
    if (rtp_packet == nullptr) {
      // No packet available to send, check if we should send padding.
      DataSize padding_to_add = PaddingToAdd(recommended_probe_size, data_sent);
      if (padding_to_add > DataSize::Zero()) {
        std::vector<std::unique_ptr<RtpPacketToSend>> padding_packets =
            packet_sender_->GeneratePadding(padding_to_add);
        if (padding_packets.empty()) {
          // No padding packets were generated, quite send loop.
          break;
        }
        for (auto& packet : padding_packets) {
          EnqueuePacket(std::move(packet));
        }
        // Continue loop to send the padding that was just added.
        continue;
      }

      // Can't fetch new packet and no padding to send, exit send loop.
      break;
    }

    // 7） 封装发送报文，通过回调发送报文
    const RtpPacketMediaType packet_type = *rtp_packet->packet_type();
    DataSize packet_size = DataSize::Bytes(rtp_packet->payload_size() +
                                           rtp_packet->padding_size());

    if (include_overhead_) {
      packet_size += DataSize::Bytes(rtp_packet->headers_size()) +
                     transport_overhead_per_packet_;
    }
    packet_sender_->SendPacket(std::move(rtp_packet), pacing_info);

    data_sent += packet_size;

    //  8） 发送完成后，更新一些统计以及budget
    // Send done, update send/process time to the target send time.
    OnPacketSent(packet_type, packet_size, target_send_time);
    if (recommended_probe_size && data_sent > *recommended_probe_size)
      break;
  }

  last_process_time_ = std::max(last_process_time_, previous_process_time);

  // 9） 更新probing状态
  if (is_probing) {
    probing_send_failure_ = data_sent == DataSize::Zero();
    if (!probing_send_failure_) {
      prober_.ProbeSent(CurrentTime(), data_sent.bytes());
    }
  }
}
```

细细啃下来，其实逻辑并不复杂。后面关注一下其他细节，比如拥塞窗口、probing等。

## 5. 拥塞窗口

在决定是否发送报文的时候（`GetPendingPacket`），我们发现有判断是否拥塞，因此有必要讲解下拥塞窗口：

**发送报文过多会导致拥塞**，这句话其实已经给了我们答案。一下代码里面的`outstanding_data_`就是正在网络中正在发送的报文， `congestion_window_size_`是一个阈值，如果正在网络中发送的报文超过这个阈值就认为是会导致拥塞： 

```cpp
bool PacingController::Congested() const {
  if (congestion_window_size_.IsFinite()) {
    return outstanding_data_ >= congestion_window_size_;
  }
  return false;
}
```

`outstanding_data_`在发送报文的时候增加，当对端收到通过FeedBack Ack后， `outstanding_data_`减小。而 `congestion_window_size_`是拥塞控制模块决策出来的一个阈值，此处先不深入挖掘。

## 6. Probing

Pacing模块里面有一个绕不开的功能是probing，对应bitrate_prober.h文件里面定义的`BitrateProber`。probing和带宽探测部分是紧密相关的，用于在发送带宽比较低的时候，可以探测到一个比较高的带宽。probing功能通过`PacedSender::CreateProbeCluster`暴露出去， pacing模块会根据当前probing状态，发送合适的padding包，达到目标探测码率。

关于probing的功能，后续会有一个专题专门介绍，此处不多介绍。

## 7. Packet发送

最后就剩下报文发送，我们知道pacing模块只保存了报文信息，真正的报文发送还需要通过上层模块完成。曾几何时，引入了`PacketRouter`这个，pacing模块调用`PacketRouter::SendPacket`完成报文发送。

大致看下这个函数，主要完成TransportSequenceNumber自增，通过报文ssrc找到合适的RtpRtcp模块去做进一步发送处理。

```cpp
void PacketRouter::SendPacket(std::unique_ptr<RtpPacketToSend> packet,
                              const PacedPacketInfo& cluster_info) {
  MutexLock lock(&modules_mutex_);
  // Transport Sequence Number是在这个地方赋值的！！
  if (packet->HasExtension<TransportSequenceNumber>()) {
    packet->SetExtension<TransportSequenceNumber>((++transport_seq_) & 0xFFFF);
  }

  // 找到对应的模块去发送
  uint32_t ssrc = packet->Ssrc();
  auto kv = send_modules_map_.find(ssrc);
  if (kv == send_modules_map_.end()) {
    RTC_LOG(LS_WARNING)
        << "Failed to send packet, matching RTP module not found "
           "or transport error. SSRC = "
        << packet->Ssrc() << ", sequence number " << packet->SequenceNumber();
    return;
  }

  RtpRtcpInterface* rtp_module = kv->second;
  if (!rtp_module->TrySendPacket(packet.get(), cluster_info)) {
    RTC_LOG(LS_WARNING) << "Failed to send packet, rejected by RTP module.";
    return;
  }

  if (rtp_module->SupportsRtxPayloadPadding()) {
    // This is now the last module to send media, and has the desired
    // properties needed for payload based padding. Cache it for later use.
    last_send_module_ = rtp_module;
  }
}
```

`PacketRouter`提供了RtpRtcp模块的注册：

```cpp
void AddSendRtpModule(RtpRtcpInterface* rtp_module, bool remb_candidate);
void RemoveSendRtpModule(RtpRtcpInterface* rtp_module);
void AddReceiveRtpModule(RtcpFeedbackSenderInterface* rtcp_sender,
                         bool remb_candidate);
void RemoveReceiveRtpModule(RtcpFeedbackSenderInterface* rtcp_sender);
```

`PacketRouter`是`RtpTransportControllerSend`的一个成员，通过参数方式传入`PacedSender`。这个类也比较简单，想深入了解报文发送，可以结合文件分析下。

## 8. 写在最后

pacing模块算是啃完了，内容比较多，因此最后总结下，pacing模块的重点。

  * 报文插入队列、弹出队列的线程；
  * 报文队列的实现，`RoundRobinPacketQueue`，不同stream报文有不同优先级，重传包和普通包有不同优先级，它的实现决定了哪个报文先发送；
  * 发送budget是外部设置，发送需要判断budget是否足够、是否出现拥塞；
  * pacing模块需要收到外部控制probing，需要probing的时候可以发送padding数据；
  * pacing之后的报文发送通过`PacketRouter`，它通过参数传入pacing模块，需要了解报文后续处理可以通过这个类跟踪。 



