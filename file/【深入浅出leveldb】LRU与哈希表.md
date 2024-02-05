 
<!--BEGIN_DATA
{
    "create_date": "2022-03-26 08:30", 
    "modify_date": "2022-03-26 08:30", 
    "is_top": "0", 
    "summary": "【深入浅出leveldb】LRU与哈希表", 
    "tags": "C/C++、数据库", 
    "file_name": "【深入浅出leveldb】LRU与哈希表.md"
}
END_DATA-->

#### <p>原文出处：<a href='https://mp.weixin.qq.com/s/nPGT8J-MX6aZ0YjnarEaTw' target='blank'></a></p>

## 【深入浅出leveldb】LRU与哈希表

### 1.LRUHandle

`LRUHandle`内部存储了如下东西：

  * Key:value对
  * LRU链表
  * HashTable bucket的链表
  * 引用计数及清理

```cpp
struct LRUHandle {  
  // value  
  void* value;  
  // 当refs为0时，应该清理  
  void (*deleter)(const Slice&, void* value);  
  LRUHandle* next_hash; // HashTable hash冲突时指向 下一个LRUHandle  
  LRUHandle* next;      // LRU链表下一个指针  
  LRUHandle* prev;      // LRU链表前一个指针  

  // 计算LRUCache容量  
  size_t charge;  // TODO(opt): Only allow uint32_t?  
  size_t key_length; // key长度  
  bool in_cache;     // 是否在LRUCache in_user_链表  
  uint32_t refs;     // 引用计数，用于删除数据  
  uint32_t hash;     // key 对应的 hash值  
  char key_data[1];  // 占位符，结构体末尾，通过key_length获取真正的key  

  Slice key() const {  
    assert(next != this);  
    return Slice(key_data, key_length);  
  }  
};  
```

注意：当`refs`为0时，需要调用`deleter`清理函数，类似于`shared_ptr`。

### 2.HandleTable

HandleTable即哈希表，根据注释leveldb的哈希表实现要比g++要快很多。

下面来看基本结构，成员、构造、析构都比较好理解，这里使用了Resize函数，桶的大小初始化为4的倍数，例如：4、8、16等等。

Resize函数保证桶的个数大于元素个数，将旧桶数据拷贝到新桶当中。

```cpp
class HandleTable {  
 public:  
  HandleTable() : length_(0), elems_(0), list_(nullptr) { Resize(); }  
  ~HandleTable() { delete[] list_; }  

 private:  
  uint32_t length_;    // list_数组长度  
  uint32_t elems_;     // handle数量  
  LRUHandle** list_;   // 哈希桶  

  // 初始化大小  
  void Resize() {  
    uint32_t new_length = 4;  
    while (new_length < elems_) {  
      new_length *= 2;  
    }  

    LRUHandle** new_list = new LRUHandle*[new_length];  
    memset(new_list, 0, sizeof(new_list[0]) * new_length);  
    uint32_t count = 0;  
    for (uint32_t i = 0; i < length_; i++) {  
      LRUHandle* h = list_[i];  
      while (h != nullptr) {  
        LRUHandle* next = h->next_hash;  
        uint32_t hash = h->hash;  
        LRUHandle** ptr = &new_list[hash & (new_length - 1)];  
        h->next_hash = *ptr;  
        *ptr = h;  
        h = next;  
        count++;  
      }  
    }  

    assert(elems_ == count);  
    delete[] list_;  
    list_ = new_list;  
    length_ = new_length;  
  }  
};  
```

  * 查询操作

哈希表查询根据key与hash查询并返回LRUHandle*，在FindPointer函数中，首先根据hash值确定在哪个桶，然后在该桶中进行单链表遍历，查找到满足key与hash的节点。

```cpp
// 哈希表查询  
LRUHandle* Lookup(const Slice& key, uint32_t hash) {  
  return *FindPointer(key, hash);  
} 

// 根据key与hash查询 并返回LRUHandle*  
LRUHandle** FindPointer(const Slice& key, uint32_t hash) {  
  LRUHandle** ptr = &list_[hash & (length_ - 1)];  
  while (*ptr != nullptr && ((*ptr)->hash != hash || key != (*ptr)->key())) {  
    ptr = &(*ptr)->next_hash;  
  }  
  return ptr;  
}  
```

  * 插入操作

插入操作逻辑比较清晰：就是调用查询操作，查找到对应的key与hash旧节点，更新查找到的节点为传入的新节点(LRUHandle)，如果旧节点不存在，也就是为空，表示在当前桶拉链末尾插入新节点(LRUHandle)，并增加元素个数，如果超过已有的长度，进行Resize操作；否则，直接返回旧节点。

```cpp
LRUHandle* Insert(LRUHandle* h) {  
  // 查找不到对应的key 那么返回的ptr就是末尾的LRUHandle*  
  LRUHandle** ptr = FindPointer(h->key(), h->hash);  
  LRUHandle* old = *ptr;  
  h->next_hash = (old == nullptr ? nullptr : old->next_hash);  
  *ptr = h;  
  if (old == nullptr) {  
    ++elems_;  
    if (elems_ > length_) {  
      // Since each cache entry is fairly large, we aim for a small  
      // average linked list length (<= 1).  
      Resize();  
    }  
  }  
  return old;  
}  
```

  * 删除操作

根据传递的key与hash删除LRUHandle，首先确定要删除的节点，并返回，查找的节点如果不为空，则用链表的后一个节点替换当前节点，并减少元素个数，我想这里返回删除的节点，最终会释放内存。释放节点操作是在`LRUCache::Unref`中进行的。

```cpp
LRUHandle* Remove(const Slice& key, uint32_t hash) {  
  LRUHandle** ptr = FindPointer(key, hash);  
  LRUHandle* result = *ptr;  
  if (result != nullptr) {  
    *ptr = result->next_hash;  
    --elems_;  
  }  
  return result;  
}  
```

### 3.LRUCache

哈希表讲解完毕后，便可以非常快的理解LRUCache。

在cache.h中有Cache抽象类。

```cpp
class LEVELDB_EXPORT Cache {  
};  
```

LRUCache基本结构如下：

```cpp
class LRUCache {  
 public:  
  LRUCache();  
  ~LRUCache();  
  // 设置容量  
  void SetCapacity(size_t capacity) { capacity_ = capacity; }  
 private:  
  // 缓存容量  
  size_t capacity_;  
  // mutex_ protects the following state.  
  mutable port::Mutex mutex_;  
  // 缓存已经使用的容量  
  size_t usage_ GUARDED_BY(mutex_);  
  // 头节点 lru双向循环链表 prev是最先访问 next是最后访问  
  // lru_保存 refs==1并且in_cache==true的handle   
  // lru_是最旧节点  
  LRUHandle lru_ GUARDED_BY(mutex_);  
  // 头节点 保存refs>=2并且 in_cache==true的节点  
  LRUHandle in_use_ GUARDED_BY(mutex_);  
  // 哈希表，用于快读查找  
  HandleTable table_ GUARDED_BY(mutex_);  
};  
```

来了解一下构造与析构：

  * 构造

容量与使用大小均设置为0。

创建空的双向循环链表。

```cpp
LRUCache::LRUCache() : capacity_(0), usage_(0) {  
  // Make empty circular linked lists.  
  lru_.next = &lru_;  
  lru_.prev = &lru_;  
  in_use_.next = &in_use_;  
  in_use_.prev = &in_use_;  
}  
```

  * 析构

首先使用断言检查`in_use_`为空，即：所有节点已经从`in_use`插入到了`lru_`上，由于是循环链表所以判断条件是`e != &lru_`，如果最红回到了头节点，表示循环结束了。在释放节点时，设置节点不在缓存中(in_cache=false)，此时引用计数也必须是1，才会正常释放。

```cpp
LRUCache::~LRUCache() {  
  assert(in_use_.next == &in_use_);  // Error if caller has an unreleased handle  
  for (LRUHandle* e = lru_.next; e != &lru_;) {  
    LRUHandle* next = e->next;  
    assert(e->in_cache);  
    e->in_cache = false;  
    assert(e->refs == 1);  // Invariant of lru_ list.  
    Unref(e);  
    e = next;  
  }  
}  
```

继续看释放操作Unref函数：释放外部引用计数，根据当前Handle(节点)的引用计数进行判断

  * 是0，调用deleter删除Handle内容，并释放内存。
  * 在缓存中且引用计数是1，`LRU_Remove`删除当前节点，在`lru_`前面插入当前节点。

```cpp
void LRUCache::Unref(LRUHandle* e) {  
  assert(e->refs > 0);  
  e->refs--;  
  if (e->refs == 0) {  // Deallocate.  
    assert(!e->in_cache);  
    (*e->deleter)(e->key(), e->value);  
    free(e);  
  } else if (e->in_cache && e->refs == 1) {  
    // No longer in use; move to lru_ list.  
    LRU_Remove(e);  
    LRU_Append(&lru_, e);    
  }  
}  

// 双向链表删除节点  
void LRUCache::LRU_Remove(LRUHandle* e) {  
  e->next->prev = e->prev;  
  e->prev->next = e->next;  
}  

// 在list之前加入最新节点  
void LRUCache::LRU_Append(LRUHandle* list, LRUHandle* e) {  
  // Make "e" newest entry by inserting just before *list  
  e->next = list;  
  e->prev = list->prev;  
  e->prev->next = e;  
  e->next->prev = e;  
}  
```

LRUCache查询：

直接根据key与hash调用内部哈希表的查询函数。访问了某个节点，需要更新链表中该节点的位置，将其放在`lru_`前面，保证是最新访问的节点，并更新引用计数。

```cpp
Cache::Handle* LRUCache::Lookup(const Slice& key, uint32_t hash) {  
  MutexLock l(&mutex_);  
  LRUHandle* e = table_.Lookup(key, hash);  
  if (e != nullptr) {  
    Ref(e);  
  }  
  return reinterpret_cast<Cache::Handle*>(e);  
}  

void LRUCache::Ref(LRUHandle* e) {  
  if (e->refs == 1 && e->in_cache) {  // If on lru_ list, move to in_use_ list.  
    LRU_Remove(e);  
    LRU_Append(&in_use_, e);  
  }  
  e->refs++;  
}  
```

LRUCache删除：

删除哈希表中节点，前面提到过哈希表删除返回的是待删除节点，那在哪里释放内存呢？便是在这里！我们再来看一下FinishErase函数。可以看到通过`LRU_Remove`删除双向循环链表中目标节点，并通过Unref释放刚刚哈希表待删除节点的内存。

```cpp
void LRUCache::Erase(const Slice& key, uint32_t hash) {  
  MutexLock l(&mutex_);  
  FinishErase(table_.Remove(key, hash));  
}

bool LRUCache::FinishErase(LRUHandle* e) {  
  if (e != nullptr) {  
    assert(e->in_cache);  
    LRU_Remove(e);  
    e->in_cache = false;  
    usage_ -= e->charge;  
    Unref(e);  
  }  
  return e != nullptr;  
}  
```

LRUCache插入：

插入操作传递了一大堆参数，主要是用来构造LRUHandle，初始化时引用计数为1。

当插入时，当起节点便是最新的，那么需要更新引用计数。所以在后面看到引用计数加1不必奇怪。

如果缓存中的容量大于0，增加缓存引用计数、设置在缓存中、添加Handle到`in_user_`链表前面，增加已使用容量，释放旧节点。

如果缓存小于等于0，不进行操作。

如果缓存满了，那就清除掉最旧的节点。

```cpp
ache::Handle* LRUCache::Insert(const Slice& key, uint32_t hash, void* value,  
                                size_t charge,  
                                void (*deleter)(const Slice& key,  
                                                void* value)) {  
  MutexLock l(&mutex_);  
  LRUHandle* e =  
      reinterpret_cast<LRUHandle*>(malloc(sizeof(LRUHandle) - 1 + key.size()));  
  e->value = value;  
  e->deleter = deleter;  
  e->charge = charge;  
  e->key_length = key.size();  
  e->hash = hash;  
  e->in_cache = false;  
  e->refs = 1;  // for the returned handle.  
  std::memcpy(e->key_data, key.data(), key.size());  

  if (capacity_ > 0) {  
    e->refs++;  // for the cache's reference.  
    e->in_cache = true;   // 设置在缓存中  
    LRU_Append(&in_use_, e);   // 将节点e插入到链表in_use_前面  
    usage_ += charge;  // 增加已使用容量  
    FinishErase(table_.Insert(e));  // 插入新节点到哈希表并释放旧节点  
  } else {  // don't cache. (capacity_==0 is supported and turns off caching.)  
    // next is read by key() in an assert, so it must be initialized  
    e->next = nullptr;  
  }  

  // 缓存满了，移除掉最旧的元素  
  while (usage_ > capacity_ && lru_.next != &lru_) {  
    LRUHandle* old = lru_.next;  
    assert(old->refs == 1);  
    bool erased = FinishErase(table_.Remove(old->key(), old->hash));  
    if (!erased) {  // to avoid unused variable when compiled NDEBUG  
      assert(erased);  
    }  
  }  
  return reinterpret_cast<Cache::Handle*>(e);  
}  
```

其他操作：

1）更新缓存中的节点(handle)

```cpp
void LRUCache::Release(Cache::Handle* handle) {  
  MutexLock l(&mutex_);  
  Unref(reinterpret_cast<LRUHandle*>(handle));  
}  
```

  2. 删除`lru_`中所有引用计数为1的节点。

```cpp
void LRUCache::Prune() {  
  MutexLock l(&mutex_);  
  while (lru_.next != &lru_) {  
    LRUHandle* e = lru_.next;  
    assert(e->refs == 1);  
    bool erased = FinishErase(table_.Remove(e->key(), e->hash));  
    if (!erased) {  // to avoid unused variable when compiled NDEBUG  
      assert(erased);  
    }  
  }  
}  
```

小结：

1）插入操作时，会把Handle插入到`in_use_`链表中，引用计数增加，使用完毕后需要手动通过Release函数进行释放(Unref)，使得节点能够进入`lru_`或者释放内存。插入具体过程是：根据容量进行插入，如果容量充足，则插入`in_use_`中，容量刚好为0，表示不操作，使用容量已超过给定容量，则删除`lru_`中的节点。(`lur_`是最后被访问的节点，前面是最近被访问的节点，构成双向链表)，删除时从后面依次删除。

2）查询操作时，会先从哈希表中查询，并返回查询的节点，判断该节点在`lru_`还是`in_use_`，如果在`lru`中，需要将其删除掉并更新到`in_use_`中，引用计数都会增加，使用完毕后需要手动通过Release函数进行释放(Unref)，使得节点能够进入`lru_`或者释放内存。

3）删除操作时，会先从哈希表中删除，并返回待删除的节点，只要返回的节点不为空，说明节点删除成功，那么此时已经从哈希表中删除，此时直接根据双向链表性质，删除该节点，并设置不在缓存中，自动释放(Unref)引用与更新。

### 4.ShardedLRUCache

LRUCache接口都被加锁保护，为了减少锁持有时间，提高缓存命中率，通过ShardedLRUCache管理16个LRUCache。使用hash的方式将一块cache 缓冲区 划分为多个小块的缓冲区。Shard函数用位运算方式拿到取模的结果，返回值总在0～kNumShards区间。

```cpp
static const int kNumShardBits = 4;  
static const int kNumShards = 1 << kNumShardBits;//16，即16个分片，二进制定义的好处是取模时>>  

class ShardedLRUCache : public Cache {  
 private:  
  // 每个LRUCache对象使用自己的锁  
  LRUCache shard_[kNumShards];  
  // 这个锁只保护对应id  
  port::Mutex id_mutex_;  
  uint64_t last_id_;  
  static inline uint32_t HashSlice(const Slice& s) {  
    return Hash(s.data(), s.size(), 0);  
  }  
   
  // 0-kNumShards 刚好取模结果  
  static uint32_t Shard(uint32_t hash) { return hash >> (32 - kNumShardBits); }  

 public:  
  explicit ShardedLRUCache(size_t capacity) : last_id_(0) {  
    // 向上取整，为每个LRUCache 分配容量  
    const size_t per_shard = (capacity + (kNumShards - 1)) / kNumShards;  
    for (int s = 0; s < kNumShards; s++) {  
      shard_[s].SetCapacity(per_shard);  
    }  
  }  
  ~ShardedLRUCache() override {}  
};  
```

其余核心函数，比较好理解，根据key，调用HashSlice生成hash值，直接调用前面的LRUCache方法即可。

```cpp
Handle* Insert(const Slice& key, void* value, size_t charge,  
               void (*deleter)(const Slice& key, void* value)) override {  
  const uint32_t hash = HashSlice(key);  
  return shard_[Shard(hash)].Insert(key, hash, value, charge, deleter);  
}  

Handle* Lookup(const Slice& key) override {  
  const uint32_t hash = HashSlice(key);  
  return shard_[Shard(hash)].Lookup(key, hash);  
}  

void Release(Handle* handle) override {  
  LRUHandle* h = reinterpret_cast<LRUHandle*>(handle);  
  shard_[Shard(h->hash)].Release(handle);  
} 

void Erase(const Slice& key) override {  
  const uint32_t hash = HashSlice(key);  
  shard_[Shard(hash)].Erase(key, hash);  
}  

void* Value(Handle* handle) override {  
  return reinterpret_cast<LRUHandle*>(handle)->value;  
}  

uint64_t NewId() override {  
  MutexLock l(&id_mutex_);  
  return ++(last_id_);  
}  

void Prune() override {  
  for (int s = 0; s < kNumShards; s++) {  
    shard_[s].Prune();  
  }  
} 

size_t TotalCharge() const override {  
  size_t total = 0;  
  for (int s = 0; s < kNumShards; s++) {  
    total += shard_[s].TotalCharge();  
  }  
  return total;  
}  
```

最后便是创建LRUCache。

```cpp
LEVELDB_EXPORT Cache* NewLRUCache(size_t capacity);  
Cache* NewLRUCache(size_t capacity) { return new ShardedLRUCache(capacity); }  
```

### 5.使用

最后给出使用方法，简单的测试一下。

首先插入key:value对，有三对，分别是：hello:100，world:101，test:201。

插入之后所有元素均在`in_use_`链表上，调用Release释放引用，此时都在`lru_`链表上，当我们查看test时，test被放在了`in_use_`链表上，引用计数+1，需要再次调用Release释放引用，此时都在`lru_`链表上，最终调用delete，此时会触发deleter自定义函数。

```cpp
#include "leveldb/cache.h"  
#include <iostream>  
#include <vector>  

void deleter(const leveldb::Slice& key, void* value) {  
  std::cout << "deleter key:" << key.ToString()  
            << " value:" << (*static_cast<int*>(value)) << std::endl;  
}  

int main() {  
  leveldb::Cache* cache = leveldb::NewLRUCache(8);  
  std::vector<std::string> orignal_keys{"hello", "world", "test"};  
  std::vector<int> orignal_values{100, 101, 201};  
  std::vector<leveldb::Cache::Handle*> handles;  
  for (size_t i = 0; i < orignal_keys.size(); ++i) {  
    handles.push_back(cache->Insert(  
        orignal_keys[i], static_cast<void*>(&orignal_values[i]), 1, deleter));  
    std::cout << "Insert key:" << orignal_keys[i]  
              << " value:" << *static_cast<int*>(cache->Value(handles[i]))  
              << std::endl;  
    ;  
  }  

  for (size_t i = 0; i < handles.size(); ++i) {  
    cache->Release(handles[i]);  
  }  

  leveldb::Cache::Handle* handle = cache->Lookup("test");  
  std::cout << "Lookup key:test value:" << *static_cast<int*>(cache->Value(handle))  
            << std::endl;  
  cache->Release(handle);  
  delete cache;  

  return 0;  
}  
```

注：编译源码的代码如下：

```cpp
g++-11 cache_test.cpp -lleveldb -lpthread -I/leveldb/include -L/leveldb/leveldb/build -std=c++11  
```

记得更换自己的目录。
