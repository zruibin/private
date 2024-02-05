 
<!--BEGIN_DATA
{
    "create_date": "2022-02-26 14:20", 
    "modify_date": "2022-02-26 14:20", 
    "is_top": "0", 
    "summary": "WebRTC GCC代码深度解读(5)基于Loss的带宽估计v1版本<br/>WebRTC GCC代码深度解读(6)基于Loss的带宽估计v2版本<br/>WebRTC GCC代码深度解读(7)InterArrivalDelta<br/>WebRTC GCC代码深度解读(8)TrendlineEstimator", 
    "tags": "WebRTC", 
    "file_name": "WebRTC GCC代码深度解读02.md"
}
END_DATA-->

#### <p>原文出处：<a href='https://zhuanlan.zhihu.com/p/490491574' target='blank'>WebRTC GCC代码深度解读(5)基于Loss的带宽估计v1版本</a></p>

前面一篇，我们介绍过原始版本的丢包估计，有三个版本，一个是`SendSideBandwidthEstimation`，另外两个是`LossBasedBandwidthEstimation`和`LossBasedBweV2`。这一篇，我们介绍下V1版本`LossBasedBandwidthEstimation`。

这只是一个实验版本，大家可以放轻松阅读。

## 1. 主要思想介绍

基于丢包的带宽估计，在最初的版本里面（`SendSideBandwidthEstimation`）是直接和阈值来判断，决定带宽是否增加或者降低。这个版本的也差不多，但是有一些不同的地方，主要在于丢包阈值的选取以及增加/降低的码率不是一个固定的值，而是根据丢包和预期的重传码率来决定的。  
  
这里，我们设置了一个丢包导致N次重传的码率阈值，在阈值选取的时候，我们会保证我们的重传码率控制在这个范围内。

这个实现没有使用固定阈值，存在一定的优势，毕竟固定的阈值不是很合理。但是由于还在实验阶段，并没有太多数据支撑。

## 2. 源码解读

### 2.1 接口定义

```cpp
class LossBasedBandwidthEstimation {
 public:
  // Returns the new estimate.
  // wanted_bitrate： 需求的带宽
  DataRate Update(Timestamp at_time,
                  DataRate min_bitrate,
                  DataRate wanted_bitrate,
                  TimeDelta last_round_trip_time);
  // 输入TCC ACK的码率
  void UpdateAcknowledgedBitrate(DataRate acknowledged_bitrate,
                                 Timestamp at_time);
  // 设置初始码率
  void Initialize(DataRate bitrate);
  // 返回是否开启基于丢包的带宽估计
  bool Enabled() const { return config_.enabled; }
  // Returns true if LossBasedBandwidthEstimation is enabled and have
  // received loss statistics. Ie, this class require transport feedback.
  // 返回是否在使用基于丢包的带宽估计
  // 根据enable标志和loss统计是否存在来判断
  bool InUse() const {
    return Enabled() && last_loss_packet_report_.IsFinite();
  }
  // 输入TCC feedback信息，更新丢包
  void UpdateLossStatistics(const std::vector<PacketResult>& packet_results,
                            Timestamp at_time);
  // 获得估计的码率
  DataRate GetEstimate() const { return loss_based_bitrate_; }

 private:
  friend class GoogCcStatePrinter;
  void Reset(DataRate bitrate);
  // 增加估计带宽时的丢包阈值
  double loss_increase_threshold() const;
  // 降低估计带宽时的丢包阈值
  double loss_decrease_threshold() const;
  // 重置码率为请求码率时候的丢包阈值
  double loss_reset_threshold() const;
  // 降低的码率，ACK码率的0.99倍
  DataRate decreased_bitrate() const;

  const LossBasedControlConfig config_;

  double average_loss_;             // 平均丢包
  double average_loss_max_;         // 最大丢包
  DataRate loss_based_bitrate_;     // 估计的码率
  DataRate acknowledged_bitrate_max_;   // ACK码率的最大值
  Timestamp acknowledged_bitrate_last_update_; // 上次估计的ACK码率
  Timestamp time_last_decrease_;                // 上次降低带宽的时间
  bool has_decreased_since_last_loss_report_;   // 上次loss报告后是否降低带宽
  Timestamp last_loss_packet_report_;           // 上次loss报告时间
  double last_loss_ratio_;                      // 上次的loss ratio，单次统计，没有做过平滑
};
```

### 2.2 丢包更新

```cpp
// 输入TCC feedback，从中获取丢包信息
void LossBasedBandwidthEstimation::UpdateLossStatistics(
    const std::vector<PacketResult>& packet_results,
    Timestamp at_time) {
  if (packet_results.empty()) {
    RTC_NOTREACHED();
    return;
  }

  // 统计丢包个数和丢包率
  int loss_count = 0;
  for (const auto& pkt : packet_results) {
    loss_count += !pkt.IsReceived() ? 1 : 0;
  }
  last_loss_ratio_ = static_cast<double>(loss_count) / packet_results.size();

  // 两次feedback的间隔
  const TimeDelta time_passed = last_loss_packet_report_.IsFinite()
                                    ? at_time - last_loss_packet_report_
                                    : TimeDelta::Seconds(1);
  last_loss_packet_report_ = at_time;
  has_decreased_since_last_loss_report_ = false;

  // 计算平均丢包率，窗口默认800ms，如果间隔低于这个值，那么当前值占比会变低
  average_loss_ += ExponentialUpdate(config_.loss_window, time_passed) *
                   (last_loss_ratio_ - average_loss_);
  // 计算最大平均丢包率
  if (average_loss_ > average_loss_max_) {
    average_loss_max_ = average_loss_;
  } else {
    // 最大值平滑降低
    // 窗口默认800ms
    average_loss_max_ +=
        ExponentialUpdate(config_.loss_max_window, time_passed) *
        (average_loss_ - average_loss_max_);
  }
}

// 平滑系数，根据间隔的大小来决定，间隔越大，那么数据约可靠，占比越高
// 如果两次loss间隔非常短，如0ms，那么最终系数为0，
// 则这次的结果不参与平均和最大平均结果的更新
// 如果interval非常大，则当前这次的数据权重更大
double ExponentialUpdate(TimeDelta window, TimeDelta interval) {
  // Use the convention that exponential window length (which is really
  // infinite) is the time it takes to dampen to 1/e.
  if (window <= TimeDelta::Zero()) {
    RTC_NOTREACHED();
    return 1.0f;
  }
  return 1.0f - exp(interval / window * -1.0);
}
```

### 2.3 ACK码率更新

```cpp
void LossBasedBandwidthEstimation::UpdateAcknowledgedBitrate(
    DataRate acknowledged_bitrate,
    Timestamp at_time) {
  // 两次TCC  ACK码率更新的间隔，默认未1s
  const TimeDelta time_passed =
      acknowledged_bitrate_last_update_.IsFinite()
          ? at_time - acknowledged_bitrate_last_update_
          : TimeDelta::Seconds(1);
  acknowledged_bitrate_last_update_ = at_time;

  // 获取最大ACK码率
  if (acknowledged_bitrate > acknowledged_bitrate_max_) {
    acknowledged_bitrate_max_ = acknowledged_bitrate;
  } else {
    // 如果更新的码率比较小，则最大ACK码率需要缓慢降低
    // 降低的系数也是采用ExponentialUpdate这个指数方式，经历的时间越长，则降低越快
    acknowledged_bitrate_max_ -=
        ExponentialUpdate(config_.acknowledged_rate_max_window, time_passed) *
        (acknowledged_bitrate_max_ - acknowledged_bitrate);
  }
}
```  

### 2.4 更新得到基于丢包的带宽估计

```cpp
DataRate LossBasedBandwidthEstimation::Update(Timestamp at_time,
                                              DataRate min_bitrate,
                                              DataRate wanted_bitrate,
                                              TimeDelta last_round_trip_time) {
  // 如果当前没有估计，则直接设置为需求带宽
  // 出现了丢包后再降嘛
  if (loss_based_bitrate_.IsZero()) {
    loss_based_bitrate_ = wanted_bitrate;
  }

  // 这里根据丢包来判断增加或降低带宽，使用的losss不一样
  // 上升我们更谨慎，因此使用最大、平均丢包
  // 降低我们要防抖动，因此使用平均值，同时参考上次丢包去最小。

  // Only increase if loss has been low for some time.
  // 使用丢包最大值来判断是否需要增加估计带宽
  const double loss_estimate_for_increase = average_loss_max_;

  // Avoid multiple decreases from averaging over one loss spike.
  // 使用平均丢包和档次丢包的最小值来判断是否需要降低带宽
  // 这里参考了单次的结果是为了避免单个较大的loss拉高平均值，导致带宽连续地降，参考了单个值可以避免这个问题
  const double loss_estimate_for_decrease =
      std::min(average_loss_, last_loss_ratio_);

  // 这次是否可以降低带宽需要满足几个条件：
  // * 上次反馈丢包时没有降低带宽
  // * 两次降低的间隔需要超过RTT + decrease_interval（默认300ms）
  const bool allow_decrease =
      !has_decreased_since_last_loss_report_ &&
      (at_time - time_last_decrease_ >=
       last_round_trip_time + config_.decrease_interval);

  // If packet lost reports are too old, dont increase bitrate.
  // 上次的TCC loss反馈是否有效：两次TCC 丢包间隔小于6s
  const bool loss_report_valid =
      at_time - last_loss_packet_report_ < 1.2 * kMaxRtcpFeedbackInterval;

  // 丢包足够低（低于reset的阈值），那么认为拥塞已经不存在，这时候直接设置估计的码率为需求带宽
  if (loss_report_valid && config_.allow_resets &&
      loss_estimate_for_increase < loss_reset_threshold()) {
    loss_based_bitrate_ = wanted_bitrate;
  }
  // 丢包较低（低于increase的阈值），这时候需要缓慢增加带宽
  else if (loss_report_valid &&
             loss_estimate_for_increase < loss_increase_threshold()) {
    // Increase bitrate by RTT-adaptive ratio.
    // 根据RTT自适应上升带宽，RTT越大，增加越慢，默认有increase_offset（1k）增加
    DataRate new_increased_bitrate =
        min_bitrate * GetIncreaseFactor(config_, last_round_trip_time) +
        config_.increase_offset;
    
    // The bitrate that would make the loss "just high enough".
    // 增加后bitrate需要保证丢包引入的码率在我们设置的范围内，以此作为上限
    const DataRate new_increased_bitrate_cap = BitrateFromLoss(
        loss_estimate_for_increase, config_.loss_bandwidth_balance_increase,
        config_.loss_bandwidth_balance_exponent);
    new_increased_bitrate =
        std::min(new_increased_bitrate, new_increased_bitrate_cap);
    
    loss_based_bitrate_ = std::max(new_increased_bitrate, loss_based_bitrate_);
  }
  // 如果丢包比较大，超过decrease的阈值，则开始降低带宽
  else if (loss_estimate_for_decrease > loss_decrease_threshold() &&
             allow_decrease) {
    // The bitrate that would make the loss "just acceptable".
    // 降低码率后，由于丢包引入的码率低于我们的预期即可
    const DataRate new_decreased_bitrate_floor = BitrateFromLoss(
        loss_estimate_for_decrease, config_.loss_bandwidth_balance_decrease,
        config_.loss_bandwidth_balance_exponent);
    // decreased_bitrate是最大ACK码率的0.99倍
    // DataRate LossBasedBandwidthEstimation::decreased_bitrate() const {
    //  return config_.decrease_factor * acknowledged_bitrate_max_;
    // }
    // 降低为ACK码率的0.99倍，同时不低于下限
    DataRate new_decreased_bitrate =
        std::max(decreased_bitrate(), new_decreased_bitrate_floor);

    
    if (new_decreased_bitrate < loss_based_bitrate_) {
      time_last_decrease_ = at_time;
      has_decreased_since_last_loss_report_ = true;
      loss_based_bitrate_ = new_decreased_bitrate;
    }
  }
  return loss_based_bitrate_;
}


// Increase slower when RTT is high.
// 根据RTT来决定带宽上升的系数，RTT越大，增加越慢;RTT越小，增加越快。
double GetIncreaseFactor(const LossBasedControlConfig& config, TimeDelta rtt) {
  // Clamp the RTT
  // 限制RTT范围在[increase_low_rtt, increase_high_rtt]
  if (rtt < config.increase_low_rtt) {
    rtt = config.increase_low_rtt;
  } else if (rtt > config.increase_high_rtt) {
    rtt = config.increase_high_rtt;
  }
  auto rtt_range = config.increase_high_rtt.Get() - config.increase_low_rtt;
  
  // 没有设置有效的RTT范围则返回默认系数1.02
  if (rtt_range <= TimeDelta::Zero()) {
    RTC_NOTREACHED();  // Only on misconfiguration.
    return config.min_increase_factor;
  }

  // factor = min_increase_factor +  [1- (rtt - increase_low_rtt) / (increase_high_rtt - increase_low_rtt)] * (max_increase_factor - min_increase_factor)
  // 因此factor在[min_increase_factor, max_increase_factor]之间，RTT越小，增加越多
  auto rtt_offset = rtt - config.increase_low_rtt;
  auto relative_offset = std::max(0.0, std::min(rtt_offset / rtt_range, 1.0));
  auto factor_range = config.max_increase_factor - config.min_increase_factor;
  return config.min_increase_factor + (1 - relative_offset) * factor_range;
}

// 在增加和降低码率的时候，我们使用了这个函数:
// bitrate * bitrate*loss^(1/exponent) = loss_bandwidth_balance
// 这里的思想是：
// 假如重传N次，重传N次只能允许使用的码率为loss_bandwidth_balance
// exponent默认为0.5，1/0.5 = 2，即重传两次的码率
DataRate BitrateFromLoss(double loss,
                         DataRate loss_bandwidth_balance,
                         double exponent) {
  if (exponent <= 0) {
    RTC_NOTREACHED();
    return DataRate::Infinity();
  }
  if (loss < 1e-5)
    return DataRate::Infinity();
  // 在给定的丢包和丢包两次允许的重传码率下，求此时的传输码率。
  // 丢包越小，最终得到的码率越高
  return loss_bandwidth_balance * pow(loss, -1.0 / exponent);
}
```

### 2.5 关于阈值如何确定

```cpp
// 根据当前码率获取loss阈值，不妨把下面的计算转换下，就可以得到:
// bitrate*loss^(1/exponent) = loss_bandwidth_balance
// 这里的思想是：
// 假如重传N次，重传N次只能允许使用的码率为loss_bandwidth_balance
// exponent默认为0.5，1/0.5 = 2，即重传两次的码率
double LossFromBitrate(DataRate bitrate,
                       DataRate loss_bandwidth_balance,
                       double exponent) {
  if (loss_bandwidth_balance >= bitrate)
    return 1.0;
  return pow(loss_bandwidth_balance / bitrate, exponent);
}

double LossBasedBandwidthEstimation::loss_reset_threshold() const {
  // 给定重传两次的码率为0.1kbps，那么此时的丢包为：
  return LossFromBitrate(loss_based_bitrate_,
                         config_.loss_bandwidth_balance_reset,
                         config_.loss_bandwidth_balance_exponent);
}

double LossBasedBandwidthEstimation::loss_increase_threshold() const {
  // 给定重传两次的码率为0.5kbps，那么此时的丢包为：
  return LossFromBitrate(loss_based_bitrate_,
                         config_.loss_bandwidth_balance_increase,
                         config_.loss_bandwidth_balance_exponent);
}

double LossBasedBandwidthEstimation::loss_decrease_threshold() const {
  // 给定重传两次的码率为4kbps，那么此时的丢包为：
  return LossFromBitrate(loss_based_bitrate_,
                         config_.loss_bandwidth_balance_decrease,
                         config_.loss_bandwidth_balance_exponent);
}
```

## 3. 总结

这个实现提供了一个另外的思路，根据设置的重传码率来设置丢包阈值以及估计码率。思路比较奇特。至于是否好用，这里不是很好说。

<hr>

#### <p>原文出处：<a href='https://zhuanlan.zhihu.com/p/490526586' target='blank'>WebRTC GCC代码深度解读(6)基于Loss的带宽估计v2版本</a></p>

## 1. 介绍

前面我们介绍过最原始的基于丢包的带宽估计，以及丢包动态阈值的V1版本，这一篇我们介绍下使用最大似然模型的V2版本。关于前面两种方法可以见之前的两篇：

https://zhuanlan.zhihu.com/p/490481512
https://zhuanlan.zhihu.com/p/490491574

由于这个版本也是近期才加入的，所以大家可以带着好奇的心去看看即可，可以从中吸取一些思想。因为没有做过太多实验，因此效果也没法去完全确认。这个功能可以可选打开的。

## 2. 原理

**先占坑，后面再补。**

<hr>

#### <p>原文出处：<a href='https://zhuanlan.zhihu.com/p/490528187' target='blank'>WebRTC GCC代码深度解读(7)InterArrivalDelta</a></p>

## 1. 介绍

前面我们讲过基于丢包的延迟估计，现在是时候介绍基于延迟的估计了。延迟估计的一个重点是单向延迟的估计，也就是这里的`InterArrivalDelta`。`InterArrivalDelta`这个类是源于`modules/remote_bitrate_estimator/inter_arrival`，因为我们这里是使用TCC，需要在发送端做带宽估计，因此inter_arrival的计算也需要放到发送端。  
  
我们知道，基于延迟的拥塞控制核心在于，拥塞会导致报文之间的间隔逐渐增大。因此我们会利用这个现象来判断当前是否进入拥塞状态。`InterArrivalDelta`用来计算两次突发的发送之间存在的相对延迟，如果没有拥塞，那么发送的报文到达接收端都是均匀的，如果有拥塞那么就会存在一定的延迟趋势。`InterArrivalDelta`只返回包组的发送时间差、接收时间差、字节差等，并不会得出是否拥塞的结果。拥塞的判断需要借助于其他类，后面我们将会介绍。  
  
下面我们就从代码角度来理解这个类。  

## 2. 源码解读

### 2.1 对外接口

主要的对外接口是`ComputeDeltas`，基于TCC feedback获取报文发送时间、接收时间、报文大小，输出包组的发送时间差、接收时间差、字节数差，返回值用来指示当前是否计算返回delta结果。返回的结果用于后续的单向延迟是否存在增加的的判断。见`DelayIncreaseDetectorInterface`接口。

```cpp
bool ComputeDeltas(Timestamp send_time,
 Timestamp arrival_time,
 Timestamp system_time,
 size_t packet_size,
 TimeDelta* send_time_delta,
 TimeDelta* arrival_time_delta,
 int* packet_size_delta);
```

### 2.2 以group方式计算相对延迟

我们可以以包方式来计算相对延迟，但是这会存在很大误差，为什么呢？主要有几个原因：

  * pacer调度通常是以5ms突发发送一系列报文，因此这些在瞬间发送出去的报文一般接收延迟基本相同，没有所谓的相对延迟
  * 对于wifi来说，其转发通常也会存在这样的突发  
  
这些突发导致直接使用包与包之间的相对延迟不是很准确。因此这里采用了包组的方式，即根据报文的发送接收时间的聚集性，将这些包分为一组，然后计算包组与包组之间的相对延迟，这个方式会更加准确。  

包组的定义如下：

```cpp
struct SendTimeGroup {
  SendTimeGroup()
      : size(0),
          first_send_time(Timestamp::MinusInfinity()),
          send_time(Timestamp::MinusInfinity()),
          first_arrival(Timestamp::MinusInfinity()),
          complete_time(Timestamp::MinusInfinity()),
          last_system_time(Timestamp::MinusInfinity()) {}

  bool IsFirstPacket() const { return complete_time.IsInfinite(); }

  size_t size;  // 包组的总字节数
  Timestamp first_send_time;  // 包组的第一个包发送时间
  Timestamp send_time;  // 包组当前最后一个报文发送时间
  Timestamp first_arrival;  // 包组第一个到达时间
  Timestamp complete_time;  // 包组完成时间（最后一个包接收时间）
  Timestamp last_system_time; // 最后的系统时间
};
```

### 2.3 是否需要开始新的group

我们需要根据发送时间和接收时间来判断，是否需要结束当前的group，开始一个新的group。一般来说，距离当前group的最小发送时间超过5ms就需要开始新的group，5ms恰好也是pacer的调度时间（5ms一次突发，burst）。这个5ms阈值也比较合理。

```cpp
// Assumes that `timestamp` is not reordered compared to
// `current_timestamp_group_`.
bool InterArrivalDelta::NewTimestampGroup(Timestamp arrival_time,
                                          Timestamp send_time) const {
  // 新的group条件：
  if (current_timestamp_group_.IsFirstPacket()) {
    // 当前group没有任何报文，不需要重新开始新的group
    return false;
  } else if (BelongsToBurst(arrival_time, send_time)) {
    // 和当前group同属于一个突发（burst），那么还要放到当前group里面
    return false;
  } else {
    // 发送时间超过阈值（默认为pacer的调度周期5ms），那么要开始一次新的group
    return send_time - current_timestamp_group_.first_send_time >
           send_time_group_length_;
  }
}
```

### 2.4 如何判断当前报文是否和当前group一起突发的

判断是否突发，只需要和最后一个包做比较，任意条件满足：

  * 与最后一个包一起发送，你们肯定是突发
  * 接收时间差-发送时间差小于0，且在和最后一个包间隔在5ms内，与第一个包间隔不超过100ms，则认为是突发  
  
第二个条件一般在拥塞缓解的时候出现较多，100ms以内间隔发送的报文，在网络中缓存然后突发全部到达。

```cpp
// 如何判断一个包是不是属于当前group一同burst的？
bool InterArrivalDelta::BelongsToBurst(Timestamp arrival_time,
                                       Timestamp send_time) const {
  RTC_DCHECK(current_timestamp_group_.complete_time.IsFinite());
  TimeDelta arrival_time_delta =
      arrival_time - current_timestamp_group_.complete_time;
  TimeDelta send_time_delta = send_time - current_timestamp_group_.send_time;
  if (send_time_delta.IsZero())
    return true;
  TimeDelta propagation_delta = arrival_time_delta - send_time_delta;
  if (propagation_delta < TimeDelta::Zero() &&
      arrival_time_delta <= kBurstDeltaThreshold &&
      arrival_time - current_timestamp_group_.first_arrival < kMaxBurstDuration)
    return true;
  return false;
}
```

### 2.5 相对延迟的计算核心代码

```cpp
bool InterArrivalDelta::ComputeDeltas(Timestamp send_time,
                                      Timestamp arrival_time,
                                      Timestamp system_time,
                                      size_t packet_size,
                                      TimeDelta* send_time_delta,
                                      TimeDelta* arrival_time_delta,
                                      int* packet_size_delta) {
  bool calculated_deltas = false;
  
  if (current_timestamp_group_.IsFirstPacket()) {
    // 当前包组的第一个包
    // We don't have enough data to update the filter, so we store it until we
    // have two frames of data to process.
    current_timestamp_group_.send_time = send_time;
    current_timestamp_group_.first_send_time = send_time;
    current_timestamp_group_.first_arrival = arrival_time;
  } else if (current_timestamp_group_.first_send_time > send_time) {
    // 存在乱序，直接丢弃当前的包
    // Reordered packet.
    return false;
  } else if (NewTimestampGroup(arrival_time, send_time)) {
    // 当前包不属于当前group，需要创建一个新的group

    // First packet of a later send burst, the previous packets sample is ready.
    // 存在两个包组（pre，current），就可以计算结果了
    if (prev_timestamp_group_.complete_time.IsFinite()) {
      // 包组间的发送时间差，以最后发送时间为准
      *send_time_delta =
          current_timestamp_group_.send_time - prev_timestamp_group_.send_time;
      // 包组间的接收时间差，以最后接收时间为准
      *arrival_time_delta = current_timestamp_group_.complete_time -
                            prev_timestamp_group_.complete_time;

      // 两次系统时间差，如果两个group跨度超过3s，需要重置
      TimeDelta system_time_delta = current_timestamp_group_.last_system_time -
                                    prev_timestamp_group_.last_system_time;
      if (*arrival_time_delta - system_time_delta >=
          kArrivalTimeOffsetThreshold) {
        Reset();
        return false;
      }
      // 如果系统时间存在乱序，需要重置（基本发生）
      if (*arrival_time_delta < TimeDelta::Zero()) {
        // The group of packets has been reordered since receiving its local
        // arrival timestamp.
        ++num_consecutive_reordered_packets_;
        if (num_consecutive_reordered_packets_ >= kReorderedResetThreshold) {
          Reset();
        }
        return false;
      } else {
        num_consecutive_reordered_packets_ = 0;
      }

      // 两个包组的字节数之差
      *packet_size_delta = static_cast<int>(current_timestamp_group_.size) -
                           static_cast<int>(prev_timestamp_group_.size);
      calculated_deltas = true;
    }

    // 更新两个group
    prev_timestamp_group_ = current_timestamp_group_;
    // The new timestamp is now the current frame.
    current_timestamp_group_.first_send_time = send_time;
    current_timestamp_group_.send_time = send_time;
    current_timestamp_group_.first_arrival = arrival_time;
    current_timestamp_group_.size = 0;
  } else {
    // 还是老的分组，更新发送时间
    current_timestamp_group_.send_time =
        std::max(current_timestamp_group_.send_time, send_time);
  }

  // 更新当前分组
  // Accumulate the frame size.
  current_timestamp_group_.size += packet_size;
  current_timestamp_group_.complete_time = arrival_time;
  current_timestamp_group_.last_system_time = system_time;

  return calculated_deltas;
}
```

## 3. 总结

InterArrivalDelta以包组方式计算一些中间结果，用于后续的基于延迟的拥塞控制。

<hr>

#### <p>原文出处：<a href='https://zhuanlan.zhihu.com/p/490775550' target='blank'>WebRTC GCC代码深度解读(8)TrendlineEstimator</a></p>

## 1. 原理介绍

在GCC算法里面，基于延迟的拥塞控制核心在于估计单向延迟的趋势，如果单向延迟存在增加趋势（trendline)，那么认为进入拥塞状态，就需要通过AIMD方式调整带宽。而`TrendlineEstimator`正是检测单向延迟趋势的一个工具类，它的输入是`InterArrivalDelta`的输出结果。  
  
`TrendlineEstimator`的输出结果有3个(见`BandwidthUsage`)：Normal、Underusing、Overusing。这个输出将会输入到AIMD中做带宽调整。

`InterArrivalDelta`介绍见：

[言剑：WebRTC GCC代码深度解读(7)](https://zhuanlan.zhihu.com/p/490528187)

## 2. 源码分析

这里我们直接从源码角度分析下，TrendlineEstimator是如何根据InterArrivalDelta输出结果检测延迟趋势的吧。

### 2.1 接口

`TrendlineEstimator`实现了`DelayIncreaseDetectorInterface`接口，根据名字，我们也可以知道，这个类的功能就是用来检测延迟增加的趋势的。主要的Update函数输入参数就是InterArrivalDelta的输出。

```cpp
class DelayIncreaseDetectorInterface {
  ...
  virtual void Update(double recv_delta_ms,
                      double send_delta_ms,
                      int64_t send_time_ms,
                      int64_t arrival_time_ms,
                      size_t packet_size,
                      bool calculated_deltas) = 0;
};
```

### 2.2 PacketTiming定义

实现内部使用`PacketTiming`来记录时间，我们需要介绍下这个类成员的含义。后续的拟合正式看`smoothed_delay_ms`是否随到达时间`arrival_time_ms`存在增加趋势，如果有增加了就说明网络队列正在拥堵。

```cpp
struct PacketTiming {
    ...
    // 以某一个包组为基准，后面的包组到达时间与该时间之差
    double arrival_time_ms;
    // 接收时间差 - 发送时间差的平滑结果，反映了网络队列引入的延迟
    double smoothed_delay_ms;
    // 接收时间差 - 发送时间差的累计结果
    double raw_delay_ms;
};
```

### 2.3 最小二乘法拟合延迟趋势

如何知道延迟存在增加趋势呢？可以看随着时间变化，网络队列引入的延迟`smoothed_delay_ms`是否在增加。我们这里假设这个是一个线性关系，这个可以用最小二乘法拟合，x = 时间，y = 队列引入的延迟`smoothed_delay_ms`。关于最小二乘法原理，可以见：

根据公式就可以得到斜率（slope）的计算，这里我们也只需要返回斜率即可，通过斜率我们可以知道延迟增加的趋势大小。

```cpp
absl::optional<double> LinearFitSlope(
    const std::deque<TrendlineEstimator::PacketTiming>& packets) {
  RTC_DCHECK(packets.size() >= 2);
  // Compute the "center of mass".
  double sum_x = 0;
  double sum_y = 0;
  for (const auto& packet : packets) {
    sum_x += packet.arrival_time_ms;
    sum_y += packet.smoothed_delay_ms;
  }
  double x_avg = sum_x / packets.size();
  double y_avg = sum_y / packets.size();
  // Compute the slope k = \sum (x_i-x_avg)(y_i-y_avg) / \sum (x_i-x_avg)^2
  double numerator = 0;
  double denominator = 0;
  for (const auto& packet : packets) {
    double x = packet.arrival_time_ms;
    double y = packet.smoothed_delay_ms;
    numerator += (x - x_avg) * (y - y_avg);
    denominator += (x - x_avg) * (x - x_avg);
  }
  if (denominator == 0)
    return absl::nullopt;
  return numerator / denominator;
}
```

### 2.4 支持自定义实现

这里还支持了使用外部自定义的状态检测器，即自己定义`NetworkStatePredictor`实现，替代`TrendlineEstimator`功能。所以我们可以看到，在Update里面不仅有内部的实现，还可以调用`NetworkStatePredictor`并参考TrendlineEstimator本身的结果（`hypothesis_`）得到另外一个结果（`hypothesis_predicted_`）。一般不用关心这个自定义实现。

```cpp
void TrendlineEstimator::Update(double recv_delta_ms,
                                double send_delta_ms,
                                int64_t send_time_ms,
                                int64_t arrival_time_ms,
                                size_t packet_size,
                                bool calculated_deltas) {
  if (calculated_deltas) {
    UpdateTrendline(recv_delta_ms, send_delta_ms, send_time_ms, arrival_time_ms,
                    packet_size);
  }
  if (network_state_predictor_) {
    hypothesis_predicted_ = network_state_predictor_->Update(
        send_time_ms, arrival_time_ms, hypothesis_);
  }
}
```

### 2.5 trendline更新

输入InterArrivalDelta的结果，估计当前的状态。如果斜率>0，则说明延迟趋势增加，斜率<0，延迟趋势降低。一般我们不会直接和0比较，而是和一个阈值做对比。超过阈值才认为是在增加/降低，认为是overuse/underuse。

同时在这里还会根据样本点，计算一个斜率上限，用在检测overuse的时候，不会超出范围。

```cpp
void TrendlineEstimator::UpdateTrendline(double recv_delta_ms,
                                         double send_delta_ms,
                                         int64_t send_time_ms,
                                         int64_t arrival_time_ms,
                                         size_t packet_size) {
  // 接收时间差 - 发送时间差 反映了网络队列引入的传输延迟（propagation delay）
  const double delta_ms = recv_delta_ms - send_delta_ms;
  ++num_of_deltas_;
  num_of_deltas_ = std::min(num_of_deltas_, kDeltaCounterMax);
  if (first_arrival_time_ms_ == -1)
    first_arrival_time_ms_ = arrival_time_ms;

  // Exponential backoff filter.
  // 指数滤波，得到一个更平滑的smoothed_delay_
  // 滤波参数的更新，见后面部分介绍
  accumulated_delay_ += delta_ms;
  smoothed_delay_ = smoothing_coef_ * smoothed_delay_ +
                    (1 - smoothing_coef_) * accumulated_delay_;

  // Maintain packet window
  // 维护包组历史信息，这里可以对历史信息做一下排序
  // 维护历史信息的原因在于后面要做最小二乘法拟合趋势
  delay_hist_.emplace_back(
      static_cast<double>(arrival_time_ms - first_arrival_time_ms_),
      smoothed_delay_, accumulated_delay_);
  if (settings_.enable_sort) {
    for (size_t i = delay_hist_.size() - 1;
         i > 0 &&
         delay_hist_[i].arrival_time_ms < delay_hist_[i - 1].arrival_time_ms;
         --i) {
      std::swap(delay_hist_[i], delay_hist_[i - 1]);
    }
  }
  // 历史信息保存个数有限，默认20个，拟合的窗口时长选择也比较重要
  if (delay_hist_.size() > settings_.window_size)
    delay_hist_.pop_front();

  // Simple linear regression.
  // 调用LinearFitSlope完成最小二乘法线性回归
  // 这里只需要获取斜率(slop)k，如果k > 0，则说明队列延迟增加，很可能处于overuse状态
  double trend = prev_trend_;
  if (delay_hist_.size() == settings_.window_size) {
    // Update trend_ if it is possible to fit a line to the data. The delay
    // trend can be seen as an estimate of (send_rate - capacity)/capacity.
    // 0 < trend < 1   ->  the delay increases, queues are filling up
    //   trend == 0    ->  the delay does not change
    //   trend < 0     ->  the delay decreases, queues are being emptied
    trend = LinearFitSlope(delay_hist_).value_or(trend);

    // 对于K > 0情况，需要限制k的上限：
    if (settings_.enable_cap) {
      absl::optional<double> cap = ComputeSlopeCap(delay_hist_, settings_);
      // We only use the cap to filter out overuse detections, not
      // to detect additional underuses.
      if (trend >= 0 && cap.has_value() && trend > cap.value()) {
        trend = cap.value();
      }
    }
  }

  // 根据smoothdelay趋势(trend)和其他参数，检测当前状态
  Detect(trend, send_delta_ms, arrival_time_ms);
}
```

在检测趋势的时候，为了避免overuse检测（斜率>0）时检测出现较大偏差，这里会根据当前的数据计算一个斜率上限，用来限制。

```cpp
absl::optional<double> ComputeSlopeCap(
    const std::deque<TrendlineEstimator::PacketTiming>& packets,
    const TrendlineEstimatorSettings& settings) {
  ...
  TrendlineEstimator::PacketTiming early = packets[0];
  // 开始的7个包中最，累计delay最小的包
  for (size_t i = 1; i < settings.beginning_packets; ++i) {
    if (packets[i].raw_delay_ms < early.raw_delay_ms)
      early = packets[i];
  }

  // 最后7个包中，累计delay最小的包
  size_t late_start = packets.size() - settings.end_packets;
  TrendlineEstimator::PacketTiming late = packets[late_start];
  for (size_t i = late_start + 1; i < packets.size(); ++i) {
    if (packets[i].raw_delay_ms < late.raw_delay_ms)
      late = packets[i];
  }
  if (late.arrival_time_ms - early.arrival_time_ms < 1) {
    return absl::nullopt;
  }

  // 根据上面计算得到的early和late，计算得到一个斜率，可以认为是一个最大斜率
  // 我们使用最小二乘法回归的结果不能超过这个范围，这算是一个保护。
  // 增加了一个cap_uncertainty，因为估计结果存在误差。
  return (late.raw_delay_ms - early.raw_delay_ms) /
             (late.arrival_time_ms - early.arrival_time_ms) +
         settings.cap_uncertainty;
}
```

### 2.6 状态检测

状态检测就是拿trend和阈值比较，判断overuse还是underuse，还是normal。需要注意的是，overuse的检测需要持续超过一定的阈值才认为是，使用单个点误差太大。

```cpp
void TrendlineEstimator::Detect(double trend, double ts_delta, int64_t now_ms) {
  // 只输入两个样本，样本太少，默认normal状态
  if (num_of_deltas_ < 2) {
    hypothesis_ = BandwidthUsage::kBwNormal;
    return;
  }

  // 原始的trend太小，区分度不高，做一个增益计算
  const double modified_trend =
      std::min(num_of_deltas_, kMinNumDeltas) * trend * threshold_gain_;
  prev_modified_trend_ = modified_trend;

  // 趋势显著增加，overuse！
  if (modified_trend > threshold_) {
    // overuse时间累计，overuse count增加
    if (time_over_using_ == -1) {
      // Initialize the timer. Assume that we've been
      // over-using half of the time since the previous
      // sample.
      // 第一次采用发送时间的一般作为overuse时间
      time_over_using_ = ts_delta / 2;
    } else {
      // Increment timer
      time_over_using_ += ts_delta;
    }
    overuse_counter_++;
    // overuse超过一定时间才会真正进入overuse状态，阈值初始化默认10ms，后续会动态调整
    if (time_over_using_ > overusing_time_threshold_ && overuse_counter_ > 1) {
      if (trend >= prev_trend_) {
        time_over_using_ = 0;
        overuse_counter_ = 0;
        hypothesis_ = BandwidthUsage::kBwOverusing;
      }
    }
  }

  // 趋势显著降低，直接置为underuse，不需要观察
  else if (modified_trend < -threshold_) {
    time_over_using_ = -1;
    overuse_counter_ = 0;
    hypothesis_ = BandwidthUsage::kBwUnderusing;
  }
  // 否则是normal状态
  else {
    time_over_using_ = -1;
    overuse_counter_ = 0;
    hypothesis_ = BandwidthUsage::kBwNormal;
  }
  prev_trend_ = trend;

  // overuse、underuse阈值的更新
  UpdateThreshold(modified_trend, now_ms);
}
```

### 2.7 阈值更新

为什么需要调整阈值？因为随着trend变化，trendline可能会变化越来越慢，但是仍然存在增加或降低趋势（一些异常点会导致trend偏离0越来越大），这个时候很大可能性不是overuse或者underuse。因此需要自适应调整阈值。

```cpp
void TrendlineEstimator::UpdateThreshold(double modified_trend,
                                         int64_t now_ms) {
  if (last_update_ms_ == -1)
    last_update_ms_ = now_ms;

  // kMaxAdaptOffsetMs: 15ms
  // trend存在较大变化，这个时候不需要调整
  if (fabs(modified_trend) > threshold_ + kMaxAdaptOffsetMs) {
    // Avoid adapting the threshold to big latency spikes, caused e.g.,
    // by a sudden capacity drop.
    last_update_ms_ = now_ms;
    return;
  }

  // 阈值上调和下调快慢不一样，上调默认为0.0087，下调默认为0.039
  // 对于overuse的检测我们需要更晋升
  const double k = fabs(modified_trend) < threshold_ ? k_down_ : k_up_;

  // 单位时间内调整比例为k
  const int64_t kMaxTimeDeltaMs = 100;
  int64_t time_delta_ms = std::min(now_ms - last_update_ms_, kMaxTimeDeltaMs);
  threshold_ += k * (fabs(modified_trend) - threshold_) * time_delta_ms;

  // 阈值限制在6~600之间
  threshold_ = rtc::SafeClamp(threshold_, 6.f, 600.f);
  last_update_ms_ = now_ms;
}
```

## 3. 总结

以上便是根据延迟趋势判断当前状态（overuse/underuse/normal）的逻辑，原理也比较简单。在做完这些检测后，便可以将这些输入到AIMD做带宽的估计了，这是下一个章节的内容。

