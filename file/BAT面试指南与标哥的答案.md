 
<!--BEGIN_DATA
{
    "create_date": "2016-06-27 13:00", 
    "modify_date": "2016-06-27 13:00", 
    "is_top": "0", 
    "summary": "BAT面试指南与标哥的答案", 
    "tags": "其它", 
    "file_name": "BAT面试指南与标哥的答案.md"
}
END_DATA-->

####<p>原文出处：<a href='https://bestswifter.com/bat-interview/' target='blank'>BAT面试指南</a></p>

随着各大公司春招的开始，很多小伙伴都行动起来了，我有幸能够加入百度并和大家分享自己的经验心得。由于我面试的都是比较大的公司，所以自然也是做了这方面的准备，因
此这篇总结并不一定适合想去创业公司的同学。另外，由于经验本来就是主观性极强的东西，加之笔者水平有限，所以如果有不认可的地方，万望诸君呵呵一笑，抛之脑后。

接下来，我就斗胆分享一下自己在准备和参加面试的过程中的收获、对面试的思考，以及一些可能对大家有用的建议。最后附赠一份大礼包，希望能帮助每位读者找到自己心仪的
工作。

##什么是面试

有些人可能会把面试看的太重，觉得面试过了就能进入大厂，技术和财富兼得……

我倒是觉得，面试没有这么夸张（抱歉做了一回标题党），它其实是一次你和面试官互相了解的绝佳机会，借此机会你还可以对未来的工作有初步的了解。

面试本身并不能完全评价一人个的实力。面试通过的人，也许只是恰好在面试时遇到了自己熟悉的问题，面试不通过，也有可能是面试官自身的问题，并非每个面试官都具备客观
评价别人的能力。

换句话说，面试没通过也许是面试官没有发现你的才华，面试通过了也并不代表你就能胜任工作，因为进入企业之后可不是每天负责回答面试题！

所以从这一点来看，面试有点像相亲。你满意我，我满意你，王八对绿豆——看上眼了，那就一拍即合，否则就分道扬镳。我本人非常希望能够多几轮面试（实际并不总是能做到
），这样大家都有充足的时间互相了解，决定去留。

网上某些面经中，介绍了一些“装逼”的方法，还有所谓的“面试技巧”，我是不太认可的。技巧需要有，这是为了让你更好的展示自己，而非坑蒙拐骗，无理取闹，无中生有。
我更想展现一个真实的自己，如果面试官不认可，说明我们没有缘分，或者说自己的能力还不够。

##面试要准备什么

有一位小伙伴面试阿里被拒后，面试官给出了这样的评价：“……计算机基础，以及编程基础能力上都有所欠缺……”。但这种笼统的回答并非是我们希望的答案，所谓的基础到
底指的是什么？

作为一名 iOS 开发者，我所理解的基础是 操作系统、网络和算法这三大块，不同的开发方向可能有不同的侧重，但基础总的来说就是这些。我不推荐通过去网上看教程来
学习这些基础知识，因为能用短短几篇文章讲明白的事情不叫基础，至少我没见过写得这么深入浅出的文章。

不知道有多少读者和我一样有过这样的困扰：“我知道某些东西很重要，所以去百度查了资料，但是查到的文章质量很差，正确率没有保证”。这其实是正常的，优秀的文章一般
都放在优秀的作者的个人博客上，这恰恰是搜索引擎的盲区，所以一般只能搜到 CSDN、博客园这种地方的文章。自然就无法保证文章质量。

出于这种考虑，我在文章最后的复习资料中，提供了用于学习相关基础知识的书籍，如果您恰好是 iOS
开发者，还可以阅读我收集的一些高质量文章，正确性比较有保证（我写的除外）。

除了准备通用的基础知识以外，简历也是一个很重要的环节。一直很仰慕唐巧老师的猿题库，无奈简历太差，都没有收到面试邀请。后来好好改了简历以后，就没有这种问题了。
关于简历的书写，推荐两篇文章：[如何写面向互联网公司的求职简历](http://blog.devtang.com/2013/12/22/how-to-write-resume-for-it-company/)、[程序猿简历模板](https:/github.com/geekcompanyResumeSample)。你也可以参考[我的简历](https://github.com/bestswifter/MySampleCode/blob/master/BATInterview/%E5%BC%A0%E6%98%9F%E5%AE%87-%E4%B8%9C%E5%8C%97%E5%A4%A7%E5%AD%A6-iOS%E5%BC%80%E5%8F%91.pdf)，没有亮点，就当是抛砖引玉。

最后，当然是准备好相关岗位的基础知识了。作为 iOS 开发者，虽然 Swift 已经发布了快两年，但是大公司转向 Swift 的动作还不明显，所以
Objective-C 几乎是必备项，Swift 都不一定能算是加分项。iOS 方面的知识也必不可少，虽然招聘信息上写着如果基础扎实，零 iOS
基础也可以，但是现实往往是比较残酷的。

##我的面试经历

扯了这么多，终于进入正题了，分享一下我的面试经历。题目如下，**破折线后面是简单的解决思路**。

###百度

####一面：约 1.5 小时

首先是四个算法题：

  1. 不用临时变量怎么实现 swap(a, b)——用加法或者异或都可以 
  2. 二维有序数组查找数字——剑指 offer 第 3题 
  3. 亿级日志中，查找登陆次数最多的十个用户——（不确定对不对，我的思路是）先用哈希表保存登陆次数和ID，然后用红黑树保存最大的十个数。剑指 offer 第 30题 
  4. 简述排序算法——快排，`partion` 函数的原理，堆排（不稳定），归并排序，基数排序。

然后有一个[智力题](http://zhidao.baidu.com/question/232978955.html?qbl=relate_question_0&word=%C1%D4%C8%CB%2C%C4%D0%C8%CB%2C%C5%AE%C8%CB%2C%C0%C7%2C%BA%A2%D7%D3)，没完
整的答出来，好像影响不是很大。

最后是 iOS 相关，面试官问的很开放，都是谈谈自己的理解：

  1. 说说你对 OC 中 `load` 方法和 `initialize` 方法的异同。——主要说一下执行时间，各自用途，没实现子类的方法会不会调用父类的？ 
  2. 说说你对 block 的理解。—— 三种 block，栈上的自动复制到堆上，block 的属性修饰符是 copy，循环引用的原理和解决方案。 
  3. 说说你对 runtime 的理解。——主要是方法调用时如何查找缓存，如何找到方法，找不到方法时怎么转发，对象的内存布局。 
  4. 说说你对 MVC 和 MVVM 的理解。—— MVC 的 C 太臃肿，可以和 V 合并，变成 MVVM 中的 V，而 VM 用来将 M 转化成 V 能用的数据。 
  5. 说说 UITableView 的调优。——一方面是通过 instruments 检查影响性能的地方，另一方面是估算高度并在 runloop 空闲时缓存。 
  6. 谈谈你对 ARC 的理解。ARC 是编译器完成的，依靠引用计数，谈谈几个属性修饰符的内存管理策略，什么情况下会内存泄露。

一面的问题非常基础，主要是算法和 Objective-C，因为准备比较充分，基本上答出来 80% 吧。大约一周后突然二面。

####二面：约 0.5 小时

二面比较突然，显示简单的自我介绍，然后问了三个问题：

  1. 野指针是什么，iOS 开发中什么情况下会有野指针？——野指针是不为 nil，但是指向已经被释放的内存的指针，不知道什么时候会有，如果有知道的读者还望提醒。 
  2. 介绍 block。—— (接第一问) 我让面试官提示我一下什么时候会有野指针，他说用 block 时，我表示还是不知道，只知道 block 会有循环引用。于是就扯回了一面的问题。 
  3. 说说你是怎么优化 UITableView 的。——还是一面的问题。。。。。。。。。。。

虽然通过了，但是几乎又问了一遍一面的问题让我感觉对方不太认真。

####三面：北京 onsite，约 2.5 小时

首先是给一个小时，手写算法：

首先是给一个小时，手写算法两个算法题。接下来问了 TCP 握手相关的。最后问了 OC 的一些细节问题。

###网易

####笔试

主要是计算机方面的大杂烩，涉及操作系统，网络，移动开发，算法等。难度不大，目测是为了淘汰浑水摸鱼的人，就不列出题目了，算法有三题，直接在线写（木有 IDE
表示很忧伤）：

  1. 很长一道题，读了很久才读懂，目测是 DFS，但是最后没时间了，写了个思路。 
  2. 把 "www.zhidao.baidu.com" 这样的字符串改成 "com/baidu/zhidao/www"。——老题目了，剑指 offer 的，两次逆序排列即可。 
  3. 求数组中和为某个值的所有子数组，比如数组是 `[5,5,10,2,3]` 一共有四个子数组的和是 15，比如 `[5,10]`，`[5,10]`，`[10,2,3]`，`[5,5,2,3]`。这个就是简单的递归了，分两种情况，当前位置的数字在子数组中，以及不在子数组中。

####一面

全部是 iOS 题，可能是觉得算法已经面过了：

  1. 介绍 block。——我提到栈上的 block 在 ARC 下会自动复制到堆上，面试官问我从 iOS 4 还是 5 开始支持这一特性，表示不知道，我又不是学 OC 历史的，后来想想可能是公司内部老项目有这个坑。 
  2. ARC 会对代码做什么优化？——比如 `NSString *s2 = s1; s2 = nil` 这样的语句，可能就不会有 `retain` 和 `release` 方法了。 
  3. 介绍一下 MVVM 和 RAC。——可能是我简历的某个角落写了用过 RAC，被挖出来了，大概谈了一下，结果面试官问我数据的双向绑定怎么做，`bind` 函数了解过么，果断说已经忘了😂😂😂 
  4. 介绍自己用过哪些开源库。——Masonry 和 SnapKit，AFNetWorking，MKNetworkKit，Alamofire，Mantle，SDWebImage 
  5. 如果让你写，你能实现么？——当然不能，不然还要实习？ 
  6. 读过某个库的源码么？——扯了一点 SDWebImage，后来被告知这个库用了 runloop 来保证滑动是加载数据的流畅性，自己看了源码后表示没有发现，唯一用到 runloop 地方是保证后台线程一直跑，也有可能是我理解错了，如果错误欢迎指正。 
  7. SDWebImage 下载了图片后为什么要解码？——当时蒙住了，面试官很 nice 的解释了一下，说是要把 png 文件建立一个什么内存映射，目前还不太懂，有空研究一下。

本来以为面的这么差肯定是挂了，没想到还是过了一面。过了不到一个小时，HR 电话打过来，约了两天后二面。

####二面

纯数学和算法：

  1. 下面这段代码的输出结果是：

`c int main() { int a[5]={1,2,3,4,5}; int *ptr=(int *)(&a+1);  
printf(“%d,%d”,*(a+1),*(ptr-1)); } `

答案是 2 和 5。`a` 是指向数组开头元素的指针，`a + 1` 就是指向下一个元素的指针，所以星号求值以后是 2。`&a` 相当于是数组的指针，`&a
+ 1` 是数组后面一个数组的指针，然后转换成`int *`类型是 5 这个数字后面的一个数字的指针。再减一就是指向 5 的指针，所以星号求值以后是 5。

  2. 某个地方天气有如下规律：如果第一天和第二天都不下雨，则第三天下雨的概率为30%；如果第一天和第二天中有任 意一天下雨,则第三天下雨的概率为60%。问如果周一周二都没下雨，那么周四下雨的概率为___。 

简单的概率题，答案是：`30% * 60% + 70% * 30% = 39%`

  3. 某痴迷扑克的小团体喜欢用23456789TJQKA来计数，A后面是22,23,...,2A,32,...,AA,222,... 依次类推。   
请用C/C++或Java写个程序，将用字符串表示这种计数法转换成字符串表示的10进制整数。其中，该计数法的2就对应于十进制的2，之后依次递增。C/C++函数
接口： char* pokToDec(char *)

我的解决思路是进制转换，类似于 16 进制转换 10 进制这种，最后再把数字转成 `char *` 类型。

然后好像没结果了，可能是编程实现太渣了？

###其他我知道的面试题

####阿里一面：

  1. `MVC` 具有什么样的优势，各个模块之间怎么通信，比如点击 Button 后 怎么通知 Model？ 
  2. 两个无限长度链表（也就是可能有环） 判断有没有交点 
  3. `UITableView` 的相关优化 
  4. `KVO`、`Notification`、`delegate` 各自的优缺点，效率还有使用场景 
  5. 如何手动通知 `KVO`
  6. Objective-C 中的 `copy` 方法 
  7. runtime 中，`SEL` 和 `IMP` 的区别 
  8. `autoreleasepool` 的使用场景和原理 
  9. `RunLoop` 的实现原理和数据结构，什么时候会用到 
  10. `block` 为什么会有循环引用 
  11. 使用 `GCD` 如何实现这个需求：A、B、C 三个任务并发，完成后执行任务 D。 
  12. `NSOperation` 和 `GCD` 的区别 
  13. `CoreData` 的使用，如何处理多线程问题 
  14. 如何设计图片缓存？ 
  15. 有没有自己设计过网络控件？

####阿里二面：

  1. 怎么判断某个 `cell` 是否显示在屏幕上 
  2. 进程和线程的区别 
  3. `TCP` 与 `UDP` 区别 
  4. `TCP` 流量控制 
  5. 数组和链表的区别 
  6. `UIView` 生命周期 
  7. 如果页面 A 跳转到 页面 B，A 的 `viewDidDisappear` 方法和 B 的 `viewDidAppear` 方法哪个先调用？ 
  8. `block` 循环引用问题 
  9. `ARC` 的本质 
  10. `RunLoop` 的基本概念，它是怎么休眠的？ 
  11. `Autoreleasepool` 什么时候释放，在什么场景下使用？ 
  12. 如何找到字符串中第一个不重复的字符 
  13. 哈希表如何处理冲突

##面试收获

####1\. 算法题怎么答

面试官可能会问到你闻所未闻的算法，这时候你不应该自己瞎想，而是先和面试官把问题讨论清楚。要知道，通过沟通弄明白复杂的问题也是一种能力，在和面试官交流的过程中
，不仅仅可以搞清楚题目真正的意思是什么，还可以展现自己良好的交流沟通能力。所以千万不要因为紧张或者害羞而浪费这次大好的机会。

有些题目似曾相识，但是暂时没有思路。这时候不妨告诉面试官，给我一些时间思考这个题。然后不要急，不要慌，就当他不存在，拿出纸和笔慢慢算（这充分说明了面试戴耳机
的重要性）。你一定要坚定一个信念：“任何一道稍微有难度的算法题，除非做过，否则一定是需要时间想的”。所以，合理的安排思考时间吧。如果十几分钟都想不出来，可以
直接放弃。

有时候面试官会要求在线编程，相信我，他不会无聊到盯着你的代码看的，面试官一般都很忙，他也有自己的工作要完成，所以你就当是用自己的 IDE 就好。在线编程往往
是一个中等难度的问题，所以不要自己吓唬自己。同时要注意代码格式的规范，适当的注释，提前编写好测试用例等，即使没有解决问题，也至少要把自己良好的编程习惯展示给
面试官。

####2\. 遇到不会的问题怎么处理

这个问题有可能是面试官故意说得含糊不清，考察你的交流能力，也有可能是无意的，或者是你的理解方式出现了偏差。不管是以上哪种问题，你都应该先和面试官交流，直到你
搞懂了面试官要问你什么，而不是按照自己的理解说了一堆无用的东西。

举个例子，面试官可能会问了一道算法题：“如何判断两个无限长度的链表是否有交点？”。对于“无限长度”可以有不同的理解，如果真的是有无穷多个节点，那显然这个问题
是无法解决的。但如果链表仅仅是有环，那么还是可以解决的。如果面试官的本意是链表有环，但你错误的理解成了无穷多个节点，那么必然会导致无法回答这个问题。而且这并
非能力不足，而是属于交流沟通方面的失误，这也正是我想分享的“技巧”。

还有一些问题，虽然你没有接触过，但是由于对类似的问题或者情况有过思考，所以可以合理假设。比如面试官问 “ARC 会对代码做什么样的优化？”。我们知道 ARC
的本质就是在合适的地方插入 `retain` 和 `release` 等方法，那么就应该从这个角度出发去思考问题。

显然分别执行 `retain` 和 `release` 操作是没有必要的，那么就可以构造出相应的例子：

    
    
    NSString *s1 = @"hello";  
    NSString *s2 = s1;  
    NSString *s2 = nil;  
    

由于这种问题我们没有真正实践过，所以可以委婉的告诉面试官：“根据我的推理，可能会有……”。

####3\. 遇到真的不会的问题怎么处理

遇到不会的问题果断承认啊。如果是基本问题，比如问你哈希表怎么实现，你说不会，那么这次面试可能就悬了。如果是有一定难度的问题，那么你承认不会，也是一种明智之举
，毕竟人无完人，一个问题不会并不能全盘否定一个人的能力。

但是比较糟糕的一种情况是，面试者由于过分紧张，担心答不上面试官的问题会有严重后果，所以尝试着去敷衍面试官。比如：“我猜是 xxx 吧”，“我觉得可能是
……”，更有甚者直接装逼：“这个我试过，不就是 xxx
么”。要知道，此时的你，由于紧张，在心态上已经输给了面试官，更何况面试官问你的问题一定是他有把握的，你觉得这时候你负隅顽抗会有几成胜算呢？

所以，面试官问我“堆排序”的细节时，由于我当时忘了堆排序是怎么实现的，所以我直接告诉他我记不清了。另一个主动认输的例子是面试官问我 RAC
如何实现双向绑定，我告诉他这个是我当时学习的时候写过的 demo，因为不常用，已经只记得一些简单的概念了。

最后，还需要保持一个平稳的心态：“面试时尽力就好，遇到自己不会的问题也是正常情况”。如果面试者顺利答对了所有问题，难免会让面试官感到一丝尴尬，面试者也有可能
会产生一些别的情绪。所以，我们要做的只是把自己的能力展示给面试官，做到不骄不躁。

####4\. 准备杀手锏

除了能够回答上面试官的问题以外，我建议自己准备一两个杀手锏级别的话题。所谓的杀手锏，至少具备以下几个特征：

  * 你亲自动手试验过。所谓实践是检验真理的唯一标准，数据是不会说谎的。
  * 问题有足够的深度。一面的面试官可能是你的直接上司，二面一般就是更改级别的。你的深度一定要**远超**其他面试者，让一面面试官觉得自己没有十足把握，让二面面试官觉得这是一个好话题，自己的手下都不一定能有这么独到深刻的见解。
  * 你对这个问题理解的足够深入，无论是广度还是深度都达到一定水平。

以 iOS 中的 `UITableView` 的调优为例，我自认为对它有一定的理解，同为 iOS
开发者的读者可以阅读这篇文章：[UIKit性能调优实战讲解](https://bestswifter.com/uikitxing-neng-diao-
you-shi-zhan-jiang-jie/)，同时我还仔细研究了 sunnyxx 大神的
[优化UITableViewCell高度计算的那些事](http://blog.sunnyxx.com/2015/05/17/cell-height-
calculation/)。

这一类的话题通常需要仔细研究官方文档，iOS 开发者还可以观看 WWDC 视频，然后花上充足的时间去总结。比如我写
[iOS自定义转场动画实战讲解](https://bestswifter.com/custom-transition-animation/)
这篇文章就花了至少三天时间，包括大年初一一整天。

由于此类话题数量不多，所以准备一个或数个即可，面试时可以有意识的将面试官引导到这些话题上去，从而充分的展示自己。

####5\. 心态

通常情况下，面试结果都会在 1 - 3 天内知道。有的面试官会当场告诉你通过了，有的公司面试结束后几个小时就能出结果。

但有些时候，由于某些原因（我也不清楚。。。。可能是比较忙？），你迟迟无法获知面试结果。这时候你可以选择耐心等待，获知直接给 HR or
内推者发送邮件。一般来说面试结束后三天还没收到通知，你可以发送邮件询问或者再等等。

##复习资料

对于读到这一段的读者，为了感谢你耐心的听我废话了这么久，送上一波精心整理的干货和资料。不敢说完全没有错，但是应该比自己去查要靠谱得多。主要涉及算法、网络、操
作系统、Objective-C 和 iOS 五个方面。如果你不是 iOS 开发者，相信前三部分的资料也或多或少能够帮上你。

####算法

这一部分的内容主要分为以下几个部分：字符串、数组与查找、链表、树以及其他基础问题。

总的来说，算法问题可以分为以下三类：

  1. 基础问题：即使是新手，一眼看过去就有思路，只是实现的时候需要注意细节。 
  2. 普通问题：这些问题通常属于以上分类中的某一类，需要面试者掌握一些常见的思路，比如递归、动态规划、BFS/DFS、双指针、二分搜索 等。或者是直接考察数据结构的使用，如：哈希、栈和队列、链表等，如果具备了这些基础知识，此类题目通常能够比较快速的解决。 
  3. 进阶问题：这些题的解题思路和普通问题相似，但是需要你事先有对应的知识积累，否则难以直接看出问题的本质。 
  4. 疑难杂题：这类问题比较奇怪，解决它以后并不能给别的题目太多帮助，如果时间紧张可以暂时放弃。

一般来说，一类问题难度不大，面试前简单复习一下，面试时小心仔细，全面思考即可。二三类问题是面试重点，需要提前准备。第四类问题通常出现较少，即使不会做，对最终
评价的负面影响也不会有前三类那么大。

如果时间充裕，我建议阅读**《剑指 Offer》**这本书并配合
**[Leetcode**](https://leetcode.com/problemset/algorithms/) 来巩固知识，在我的面试过程中，出现很
多书上的原题或者变体，我自认为没有因为算法而影响任何一次面试的成绩。如果时间紧张，你也可以只完成我列出的一些经典题目，在“【】”中标记了我对此题类型的分类，
**如果加星号表示此题在实际面试中出现过**。

> PS:
最近有小伙伴被问到了哈希表的实现。这可以理解为算法，也可以归类为计算机基础知识。总的来说你至少需要明白哈希值的特点和两种解决冲突的方式：拉链式和开放寻址。

**字符串**

  1. [【3】最长回文子串](https://leetcode.com/problems/longest-palindromic-substring/)
  2. [【3】最长无重复子串](https://leetcode.com/problems/longest-substring-without-repeating-characters/)
  3. [【1*】字符串转数字](https://leetcode.com/problems/string-to-integer-atoi/)
  4. 【4】KMP 算法 
  5. [【2】字符串全排列](http://blog.csdn.net/morewindows/article/details/7370155)
  6. [【2*】翻转字符串](https://leetcode.com/problems/reverse-words-in-a-string/)

**动态规划**

  1. [【2】背包问题](http://baike.baidu.com/link?url=rhsiQhWz0xoYrm265bZQfow1IePC8X_MVUUlw9V9Ymu9g4Cwoqu-fjZIGOJZqe_V4ONMJlXug1IN0Cj_g0O3Ya)
  2. [【3】连续子数组的最大和](https://leetcode.com/problems/maximum-subarray/)
  3. [【4】实现简单的正则表达式匹配](https://leetcode.com/problems/regular-expression-matching/)

**数组**

  1. 【3】求两个等长、有序数组的中位数（二分法） 
  2. [【4】求两个不等长、有序数组的中位数](https://leetcode.com/problems/median-of-two-sorted-arrays/)
  3. [【3】旋转数组求最小值](https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/)、[【3】旋转数组求查找某个值是否存在](https://leetcode.com/problems/search-in-rotated-sorted-array/)（二分法） 
  4. 【4*】每行从左到右，每列从上到下递增的二维数组中，判断某个数是否存在（剑指 offer 第 3 题） 
  5. [【3*】数组中出现次数超过一半的数字](https://bestswifter.com/arrayoccurmorethanhalf/)
  6. [【3*】第 k 大的数](https://leetcode.com/problems/kth-largest-element-in-an-array/)（拓展：最大的 k 个数） 
  7. 【3*】有序数组中某个数字出现的次数（提示：利用二分搜索）

**链表**

  1. [【2】反转链表](https://leetcode.com/problems/reverse-linked-list/)（使用递归和迭代两种解法，了解头插法） 
  2. [【3】删除链表的当前节点](https://leetcode.com/problems/delete-node-in-a-linked-list/)
  3. [【3】删除倒数第 k 个节点](https://leetcode.com/problems/remove-nth-node-from-end-of-list/)
  4. [【1】两个有序链表合并](https://leetcode.com/problems/merge-two-sorted-lists/)
  5. [【4】复杂链表的复制](https://leetcode.com/problems/copy-list-with-random-pointer/)
  6. [【2*】判断链表是否有环](https://leetcode.com/problems/linked-list-cycle-ii/)
  7. [【3*】两个链表的第一个公共节点](http://blog.csdn.net/zzran/article/details/7984870)（提示：考虑链表有环的情况） 
  8. [【3】删除链表中重复节点](https://leetcode.com/problems/remove-duplicates-from-sorted-list/)

**树**

  1. [【3】根据中序和后序遍历结果重建二叉树](https://leetcode.com/problems/construct-binary-tree-from-inorder-and-postorder-traversal/)、[【3】根据中序和前序遍历结果重建二叉树](https://leetcode.com/problems/construct-binary-tree-from-preorder-and-inorder-traversal/)
  2. [【2】翻转二叉树](https://leetcode.com/problems/invert-binary-tree/)
  3. [【2】从上往下打印二叉树](https://leetcode.com/problems/binary-tree-level-order-traversal-ii/) (BFS 的思想) 
  4. 【3】判断某个数组是不是二叉树的后序遍历结果 (剑指 offer 第 24 题) 
  5. [【3】二叉树中和为某个值的路径](https://leetcode.com/problems/path-sum-ii/)
  6. 【3*】二叉树中某个节点的下一个节点 (强烈推荐准备一下，剑指 offer 第 58 题)

**栈**

  1. [【2】用两个栈实现队列](https://leetcode.com/problems/implement-queue-using-stacks/)、[【2】用两个队列实现栈](https://leetcode.com/problems/implement-stack-using-queues/)
  2. [【2】实现一个栈，可以用常数级时间找出栈中的最小值](https://leetcode.com/problems/min-stack/)
  3. 【3】判断栈的压栈、弹栈序列是否合法（剑指offer 第 22 题）

**排序**

了解以下排序的时间、空间复杂度，是否稳定，实现原理

  1. [归并排序](http://baike.baidu.com/link?url=awQj_m-d5Lf_g5TglfU3uN55-0Dt2SmFv3IZx6-Ia86dOyyBoxkJhDyc2oFAzlUXFIXhs2dGehbHAHDqr1DuAK)、拓展：求数组中的逆序对个数 
  2. [快速排序](http://baike.baidu.com/link?url=_sdhFCTSDKNM6wA5OCgqHTJc9kLWjiQBPLzO9-Cw_bYh4vZ7ofkBqySVw-MQDsJfOO9g9SJb2OCuL3yAmHIPWvv_sSPOsf-JZfKOU8QV3HrhInkkfGJ6j5Li4u3nWwiZkQlOUlGEZI-gLIyObuEM7bqwZPR8gLyVEiqutVr8pIDa6gF7cB8eixeQyur2yUt7) 重点：`partion` 函数的实现 
  3. [堆排序](http://baike.baidu.com/link?url=eioUPqfLTP0mqIOIuJdH0tp9m3ihgtx2rjcFMDpKhNXcjRidBGuk-XuQtM2Zl0z6J43yKq8VTDfFRzCsN4zj3_)
  4. 数组元素值域已知时，考虑 [基数排序](http://baike.baidu.com/view/1170573.htm) 和 [桶排序](http://baike.baidu.com/view/1784217.htm)

**位运算**

  1. [【2】给一个十进制数字，求它的二进制表示中，有多少个 1](https://leetcode.com/problems/number-of-1-bits/) (n &= n - 1) 
  2. [【3】给一个数组，所有数字都出现了偶数次，只有一个出现了一次，找出这个数](https://leetcode.com/problems/single-number/)
  3. [【4】给一个数组，所有数字都出现了三次，只有一个出现了一次，找出这个数](https://leetcode.com/problems/single-number-ii/)
  4. [【3】给一个数组，所有数组都出现了偶数次，只有两个数字出现了一次，找出这两个数](https://leetcode.com/problems/single-number-iii/)

####网络层

根据不同的面试岗位，侧重点略有不同。对 iOS 和 Android 开发者来说，HTTP 考的略少，以 TCP 和 UDP 为主。其实 UDP
基本上只会考察和 TCP 的区别。

当然还有一些常见的基础问题，比如 Cookie 和 Session 的考察，POST 和 GET 的考察，HTTPS
的简单了解等。这些问题在我的博客中都有简单的总结。

总结了一些资料，数字序号越大的资料表示篇幅更长，耗时更久，难度更大，讲解更细致。破折线后表示预计需要多久可以读完。

  1. [【博客】我的六篇总结](http://www.jianshu.com/notebooks/3276500/latest)————不到一周 
  2. [【书】图解 TCP/IP](http://item.jd.com/11253710.html)————半个月 
  3. [【书】TCP/IP 详解](http://item.jd.com/11182320.html)————没读过，感觉至少需要一个月 
  4. [【书】TCP/IP 协议簇](http://item.jd.com/10485475.html)————没读过，感觉至少需要一个月

光读书是没有用的，一问到实际问题很容易懵逼，以下是我总结的一些问题：

  1. 简介 TCP 和 UDP 区别，他们位于哪一层？ 
  2. 路由器和交换机的工作原理大概是什么，他们分别用到什么协议，位于哪一层？ 
  3. 描述TCP 协议三次握手，四次释放的过程。 
  4. TCP 协议是如何进行流量控制，拥塞控制的？ 
  5. 为什么建立连接时是三次握手，两次行不行？如果第三次握手失败了怎么处理 
  6. 关闭连接时，第四次握手失败怎么处理？ 
  7. 你怎么理解分层和协议？ 
  8. HTTP 请求中的 [GET 和 POST 的区别](\(http://www.w3school.com.cn/tags/html_ref_httpmethods.asp\))，Session 和 Cookie 的区别。 
  9. 谈谈你对 HTTP 1.1，2.0 和 HTTPS 的理解。

####操作系统与编译

我被问到的操作系统问题很少，所以仅仅总结了一些自认为比较重要的问题。关于这一部分的知识，推荐阅读**《程序员的自我修养》**，如果时间有限，你可以阅读我的*
*[《程序员的自我修养读书笔记》](https://bestswifter.com/cheng-xu-yuan-de-zi-wo-xiu-yang-du-shu-bi-ji/)**，并思考这些问题：

  1. 源代码是怎么变成可执行文件的，每一步的作用是什么？（预编译，词法分析，语法分析，语义分析，中间语言生成目标代码生成，汇编，链接） 
  2. 应用层、API、运行库、系统调用、操作系统内核之间的关系是什么？ 
  3. 虚拟内存空间是什么，为什么要有虚拟内存空间。 
  4. 静态链接和动态链接分别表示什么，大概是怎么实现的？ 
  5. 可执行文件的结构如何？（分为哪些段） 
  6. 它是怎么装载进内存的，为什么要分段，分页，页错误是什么？ 
  7. 进程的内存格局是怎样的？（堆、栈、全局/静态区，代码区，常量区） 
  8. 堆和栈的区别，函数调用和栈的关系 
  9. 进程和线程的区别 
  10. 异步和同步，串行，并发，并行的区别 
  11. 多并发任务，仅多线程能加快速度么（不能，会变慢，有线程切换的开销） 
  12. 多个线程之间可以共享那些数据 
  13. 进程之间如何通信 
  14. 介绍几种锁，他们的用途和区别

关于多线程相关的，推荐阅读这篇文章的前面一小部分——**《[iOS多线程编程——GCD与NSOperation总结](https://bestswifter.com/multithreadconclusion/)》**

关于操作系统和编译方面的文章，除了读原书和我的读书笔记外，还可以参考这篇文章——**《[修改一个数字破解Mac上的应用](https://bestswifter.com/app-crack/)》**

####OC

首先两本必备的神书一定是要读完的。一本是讲 OC 的《Effective Objective-C 2.0》，中文名叫：“编写高质量 iOS 与 OS X
代码的 52 个有效方法”。另一本书叫：《Objective-C 高级编程》。前者讲解 OC 中各种细节，后者主要讲了 ARC、Block 和 GCD。

光是读书，思考不够，很容易在面试时被问懵逼，所以建议一遍尝试回答面试真题，一边阅读以下总结性的文章，重要性不分先后：

  1. [检测内存泄露](http://wereadteam.github.io/2016/02/22/MLeaksFinder/?from=singlemessage&isappinstalled=0)
  2. [KVO与KVC原理](http://www.jianshu.com/p/f1393d10109d)、[KVO、Notification、Delegate优缺点](http://www.tuicool.com/articles/mUVJVb)、[最推荐的官方文档](https://developer.apple.com/library/ios/documentation/Cocoa/Conceptual/KeyValueObserving/KeyValueObserving.html#//apple_ref/doc/uid/10000177-BCICJDHA)
  3. [GCD 与 NSOperation](https://bestswifter.com/multithreadconclusion/)
  4. [Runtime](http://www.ianisme.com/ios/2019.html)
  5. [block](http://blog.ibireme.com/2013/11/27/objc-block/)
  6. [atomic 线程安全](http://www.cocoachina.com/bbs/read.php?tid-301674.html)、[@synchronized](http://www.cnblogs.com/wendingding/p/3805841.html)
  7. [对象的深浅复制](https://bestswifter.com/differenceofcopybettenswiftandoc/)
  8. [招聘一个靠谱的iOS](https://github.com/ChenYilong/iOSInterviewQuestions/tree/master/01%E3%80%8A%E6%8B%9B%E8%81%98%E4%B8%80%E4%B8%AA%E9%9D%A0%E8%B0%B1%E7%9A%84iOS%E3%80%8B%E9%9D%A2%E8%AF%95%E9%A2%98%E5%8F%82%E8%80%83%E7%AD%94%E6%A1%88)
  9. [消息传递机制](http://objccn.io/issue-7-4/)
  10. [深入理解Objective-C：Category](http://tech.meituan.com/DiveIntoCategory.html)

**强烈推荐第八篇文章，做完这上面的题目基本上可以应付大多数 OC 方面的问题了。**

####iOS 开发

  1. [RunLoop](http://blog.ibireme.com/2015/05/18/runloop/)
  2. [Cell 图片异步加载优化](http://www.jianshu.com/p/02ab2b74c451)
  3. [iOS 函数式编程的实现 && 响应式编程概念](http://www.cocoachina.com/ios/20160307/15585.html)
  4. [内存恶鬼drawRect](http://bihongbo.com/2016/01/03/memoryGhostdrawRect/)
  5. [UIKit 性能调优(主要是UITableView)](https://bestswifter.com/uikitxing-neng-diao-you-shi-zhan-jiang-jie/)
  6. [优化UITableViewCell高度计算的那些事](http://blog.sunnyxx.com/2015/05/17/cell-height-calculation/)
  7. [高性能图片架构与设计](http://zhuanlan.zhihu.com/magilu/20273299)
  8. [轻量化视图控制器](http://objccn.io/issue-1-1/)
  9. [UIView的生命周期](https://bestswifter.com/uiviewlifetime/)
  10. [高效设置圆角](https://bestswifter.com/efficient-rounded-corner/)
  11. [事件的传递和响应机制](http://www.jianshu.com/p/2e074db792ba)
  12. [ReactiveCocoa 和 MVVM 入门](http://yulingtianxia.com/blog/2015/05/21/ReactiveCocoa-and-MVVM-an-Introduction/)

**其中需要重点了解 `runloop`，它不仅仅是简单的“跑圈”的 概念，很多问题其实都与它有关，建议认真阅读 ibireme 大神的总结**

####其他面经

1. [我是如何同时拿到阿里和腾讯offer的](https://segmentfault.com/a/1190000002627927#articleHeader5)
2. [大三学生拿到阿里,百度实习offer面试经验分享](http://www.wtoutiao.com/p/e2fwlu.html)
3. [2016年1月TX电面题](http://blog.csdn.net/xieyupeng520/article/details/50681147)


<hr>





####<p>原文出处：<a href='http://101.200.209.244/bat-interview-first/' target='blank'>BAT面试指南试答百度一面</a></p>

目前正在离职中（裸辞），准备离开北京了，自然也需要做一些求职的准备。大深圳等我太久了，决定回深圳先玩半个月，再好好找工作。

今天看到了bestswifter的一篇BAT面试指南，决定试答一下。算起来我的面试经历并不丰富，倒是当过面试官面过不少同学，将下来换成我当求职者了，心态需要
做一下下转变。如果本篇文章中的答案，与您的想法有出入，不如提出来一起聊聊！

**郑重声明内容来源：**所有题目来源于[BAT 面试指南](http://www.tuicool.com/articles/quuUJvM#0-tsina-1-4272-397232819ff9a47a7b7e80a40613cfe1)

##一面四个算法题：

不管怎么说，当年大学毕业的时候，百度一面通过了，二面的时候被算法题给刷了。记得当年我面试的是深圳C++算法工程师，一面的算法题我答得挺好的，但是到二面的时候
，是一个年轻的小伙子面试的我，刚开始问的链表的常用操作、栈等相关的算法还是答得可以的，可是到后面让我手写堆排序，只好老实说不会（大学只讲了数据结构书中堆排序
的皮毛，10分钟就带过了），后来又问什么操作系统内存碎片是如何处理的，采用什么样的算法。。。至今还不懂！

言归正传，这次若是有机会再去百度面试，我不会再像刚毕业那时紧张了。下面的四道算法题，尝试做一做！

###1.1、不用临时变量怎么实现swap(a, b)

解决的办法可能有很多种，不过这里提供两种方式来实现。

####1.1.1 位运算实现交换

通过位运算实现交换，首先将a = a ^ b，再执行第二条b = a ^ b就可以得到b = a，但是此时a还不是了，再执行a = a ^
b，那么a就变成b了（这种方式是我最熟悉的）：

```
NSInteger a = 19;
NSInteger b = 99;


a = a ^ b;
b = a ^ b;
a = a ^ b;


// a = 99, b = 19
NSLog(@"a = %ld, b = %ld", a, b);
```


####1.1.2 算术运算实现交换

实现原理：将a、b看作数轴上的两个点，利用差值来计算两者的距离并保存到其中一个变量中，再利用这个距离与a、b的差值或者和计算出交换后的a、b值：

```
NSInteger a = -1;
NSInteger b = 1;

a = a + b;
b = a - b;
a = a - b;

NSLog(@"a = %ld, b = %ld", a, b);
```


这种方式也不需要借助临时变量，但是这种方式有很大的局限性，比如 a、b本是不溢出的，但是a+b后可能会溢出。

###1.2、二维有序数组查找数字

题目明确告诉我们：数组是二维的，而且是有序的，目标是查找数字。题目没有明确说明如何查找，我想可能是希望求职者以尽可能高效的算法来查找数字。

其实我个人看到题目第一反映就是折半查找算法了，但是好像遇到使用折半查找算法的都是一维有序数组吧？假设下面是二维数组：

```
[
  [1,   3,  5,  7],
  [10, 11, 16, 20],
  [23, 30, 34, 50]
]
```

这其实是一个三行四列的矩阵，如何才能高效地查找某个值的位置呢？如果我们采用最常规的双重遍历，那出这道题就没有意义了。

下面，我们一起来分析一下，如何查找才快一些呢。当然我的想法不是最高效的，只是比双重遍历要快一些而已，但是我相信对于面试官而言，这已经足够了。面试官决不是必须
要你实现出最高效的算法，只是希望求职者能够认真地分析并以自己的想法描述出一种比常规算法要高效一点点的就可以了。

假设，我们查找数字34，那么我们可以这么找：

  1. 先查找第一行最后一个元素，若等于34，则查找成功；若>34，则必定就是这一行或者不存在；若<34，则说明必定是后面的行中或者根本不存在。
  2. 若第一步最后一个元素>34，则可以采用折半查找这一行。
  3. 若第一步最后一个元素<34，则说明不在第一行，则继续查找下一行最后一个元素，直到找到>34为止或者直接查找结束。
  4. 当查找到最后一个元素>34的行时，折半查找这一行即可。

时间复杂度分析：我们查找第一行最后一个元素，最坏情况下是column次，而折半查找是log2n ，那么最终时间复杂度为：column * log2n

下面是我写的一部分代码，没有写成函数，只是直接写来测试一下我的算法：

```

const int rows = 3;
const int cols = 4;
int array[rows][cols] = {{1, 3, 5, 7}, {10, 11, 16, 20}, {23, 30, 34, 50}};
int searchNum = 34;
// 是否查找成功
int found = 0;


// 查找第一行最后一个元素

for (int i = 0; i < rows; ++i) {
  int last = array[i][cols - 1];
  if (last == searchNum) {
    NSLog(@"找到了，位置为：(%d, %d)", i, cols - 1);
    break;
  }

  // 说明待查找的元素就在这一行，或者根本不存在
  else if (last > searchNum) {
    int mid = 0;
    int low = 0;
    int high = cols - 1;

    while (low <= high) {

      mid = (low + high) / 2;

      if (array[i][mid] == searchNum) {
        found = YES;
        NSLog(@"找到了，位置为：(%d, %d)", i, cols - 1);
        return;
      } else if (array[i][mid] > searchNum) {
        high = mid - 1;
      } else {
        low = mid + 1;
      }

    }

    if (!found) {
      NSLog(@"查找失败了，元素并不在二维数组中");
    }
  }

}
```


我相信还有更高效的算法，不过在面试时能想到这种方式，我觉得还算可以的了。如果我们查找最后一个元素，修改成采用折半查找每行最后一个元素，那么效率是不是又提高了
？相当于做两次折半查找，便可查找成功或者不存在。

###1.3、亿级日志中，查找登陆次数最多的十个用户

假设只有一亿级日志，每条日志占用255字节，那么1亿就有1.0/4K *10000 * 10000 == 2500 * 10000M=>2.44 *
10000M == 24400M ~= 23.8G，可想而知是不能同时放入内存中的。

  1. 我们可以通过分割成很多份，通过hash(key)对1024取模，分成1024个份，每份占用约23.8M，完全可以放内存中。
  2. 然后分别对每一份操作，以登录次数作为hash的key，若key存在，则只是使key加1，若不存在则key值设置为1，只保留key值最大的10条记录，其余都丢掉（释放内存）
  3. 当执行完毕后，内存中共有10 * 1024条记录，共10 * 0.25K * 1024 = 2.5M，因此内存使用上没有问题
  4. 对这10 * 1024条记录排序，采用最小堆排序，或者采用红黑树（平衡二叉树）排序，提取前值最大的10条。

以上纯属个人想法，每条日志大小255字节也是假设值。

###1.4、简述排序算法

  * [快速排序](http://101.200.209.244/quick-sort/)：利用分而治之的思想，每一趟比较中保证左边的比基准数小，右边的都比基准数大。每一趟排序时，需要划分出基准数，通过partition函数来划分，得到基准后，再递归排序基准数左边的部分，递归排序基准数右边的部分。
  * [堆排序](http://101.200.209.244/heap-sort/)：堆分为最大堆和最小堆。最大堆是每次调整堆后，保证堆顶元素是最大元素，然后将当前未有序的元素中的最后一个元素与之交换，保证右边不断有序，而左边无序元素越来越少，因此最大堆排序后是升序序列；最小堆是每次调整堆后，保证堆顶元素是最小元素，然后将当前未有序的元素中的最后一个元素与之交换，保证右边不断有序，而左边无序元素越来越少，因此最小堆排序后得到的是降序序列。
  * [归并排序](http://101.200.209.244/mergesort/)：采用分治法，通过将序列中分成子序列，递归归并成有序的若干个子序列，然后再二路归并成各个更大的子序列，最后再二路归并成最终序列。
  * [冒泡排序](http://101.200.209.244/bubble-sort/)：所谓冒泡，就像水中冒泡一样，将值小的不断将上浮，值大的不断往下沉。每一趟都将值最大的交换到这一趟的最后，保证待查找序列部分最后一个元素是最大值。
  * [插入排序](http://101.200.209.244/insert-sort/) 插入排序分为直接插入排序和折半插入排序。对于直接插入排序，每一趟都寻找a[i-1] > a[i]的，说明这时候是无序的，记录待排序值a[i]，然后将前面已有序的部分，移动位置，使a[i]值插入后，已有序部分依然有序；对于折半插入排序，每一趟都通过折半查找的方式来查找元素，然后移动位置，将之插入，使之有序，不过折半插入排序需要一个哨兵位置a[0]。

##小结

本篇文章只是bestswifter文中的一面部分内部，**下一篇**继续整理其所提到的**二面**内容。通过一面，看起来一面的算法题并不算复杂，但愿待我有机
会面试的时候也是差不多难度的！


<hr>




####<p>原文出处：<a href='http://101.200.209.244/bat-interview-baidu-second/' target='blank'>BAT面试指南试答百度二面</a></p>

本篇文章是继[BAT面试指南试答百度一面](http://101.200.209.244/bat-interview-
first/)部分而试答，一面中只写了算法部分，将一面中的iOS部分移到本篇来写。

由于二面部分只有几道iOS题，因此就干脆将一面的iOS部分放到本篇一起来答。

**郑重声明：**题目来源于[BAT 面试指南](https://bestswifter.com/bat-interview/)百度一面iOS部分和二面iOS部分题目。

##一面iOS部分

###1.1 说说OC中load方法和initialize方法的异同。

**对于load方法，官方的文档说明如下：**

>Invoked whenever a class or category is added to the Objective-C runtime;
implement this method to perform class-specific behavior upon loading. The
load message is sent to classes and categories that are both dynamically
loaded and statically linked, but only if the newly loaded class or category
implements a method that can respond.
>
>The order of initialization is as follows: * All initializers in any framework
you link to. * All +load methods in your image. * All C++ static initializers
and C/C++ __attribute__(constructor) functions in your image. * All
initializers in frameworks that link to you.
>
>In addition: * A class’s +load method is called after all of its superclasses’
+load methods. * A category +load method is called after the class’s own +load
method.
>
>In a custom implementation of load you can therefore safely message other
unrelated classes from the same image, but any load methods implemented by
those classes may not have run yet.

文档也说清楚了，**对于load方法，只要文件被引用就会被调用。load方法调用顺序是父类的load方法优先调用于子类的load方法，而本类的load方法优
先于category调用。**

**对于+initialize方法，官方的文档说明如下：**

>Initializes the class before it receives its first message.
>
>The runtime sends initialize to each class in a program just before the class,
or any class that inherits from it, is sent its first message from within the
program. The runtime sends the initialize message to classes in a thread-safe
manner. Superclasses receive this message before their subclasses. The
superclass implementation may be called multiple times if subclasses do not
implement initialize—the runtime will call the inherited implementation—or if
subclasses explicitly call [super initialize]. If you want to protect yourself
from being run multiple times, you can structure your implementation along
these lines:

```
+ (void)initialize {

  if (self == [ClassName self]) {

    // ... do the initialization ...

  }

}
```


>Because initialize is called in a **thread-safe** manner and the order of
initialize being called on different classes is not guaranteed, it’s important
to do the minimum amount of work necessary in initialize methods.
>
>Specifically, any code that takes locks that might be required by other
classes in their initialize methods is liable to lead to **deadlocks**.
>
>Therefore you should not rely on initialize for complex initialization, and
should instead limit it to straightforward, class local initialization.
initialize is invoked **only once per class**. If you want to perform
independent initialization for the class and for categories of the class, you
should implement load methods.

**文档也很明确的说明了：**文件被引用并不代表initialize就会被调用，只有类或者子类中第一次有函数调用时，都会调用initialize。initialize是线程安全的，我们不能在initialize方法中加锁，这有可能导致死锁。我们也不应该在函数中实现复杂的代码。initialize只会被调用一次。

**+load和+initialize共同点：**

  * 在不考虑开发者主动使用的情况下，系统最多会调用一次
  * 如果父类和子类都被调用，父类的调用一定在子类之前
  * 这两个方法不适合做复杂的操作，应该是足够简单
  * 在使用时都不要过重地依赖于这两个方法，除非真正必要。在使用时一定要注意防止死锁！
  * 都不需要调用[super load]、[super initialize]

**+load和+initialize不同点：**

  * load方法没有自动释放池，如果做数据处理，需要释放内存，则开发者得自己添加autoreleasepool来管理内存的释放。
  * 和load不同，即使子类不实现initialize方法，也会把父类的实现继承过来调用一遍。注意的是在此之前，父类的方法已经被执行过一次了，同样不需要super调用。

###1.2 说说你对block的理解。

题目问得太简单太宽泛了，作为求职者，不防反问面试官想听听哪些方面的。比如，我们可以反问是想问有哪些block类型？还是block的应用或是block循环引用
问题及解决方案？

对于block类型有哪些，看看唐巧的技术博客中的一篇[谈Objective-Cblock的实现](http://blog.devtang.com/2013/07/28/a-look-inside-blocks/)，里面讲到Block分
为三种，分别是全局block、栈block和堆block。ARC之后，我们并不需要手动copy到堆上，通常都已经交给编译器来完成了。

如果是想问block循环引用的问题及解决方案，大家可以阅读笔者之前所写的一篇如何分析循环引用及如何解决[iOSBlock循环引用精讲](http://101.200.209.244/ios-block-memory-cycle/)

如果是想问block的应用，那么应用场景就太多了。比如GCD+block就非常多，而我的项目中除了老代码没有修改成block版本，新的代码都是能block来
实现的。

###1.3 说说你对runtime的理解

这个问题与第三个问题一样，都过于宽泛了。还是反问面试官以确定面试官想知道什么吧。

**1、消息是如何转发的？**

这里有一篇文章讲的就是[Runtime Message Forwarding](http://101.200.209.244/runtime-message-forwarding/)，我认为只有讲讲消息转发的流程就可以了。动态解析过程大致是这样的：通过resolveInstanceMethod允许开发者决定是否动态添加方法，若返回NO，就直接进入doesNotRecognizeSelector，流程结束，否则需要通过class_addMethod动态添加方法并返回YES并进入下一步。forwardingTargetForSelector是第二步，允许开发者决定将由哪个对象响应这个selector，如果返回nil，则直接进入doesNotRecognizeSelector，流程结束，否则需要返回一个对象，但不能是self。进入第三步指定方法签名methodSignatureForSelector，若返回nil，则直接进入doesNotRecognizeSelector且流程结束，否则指定签名，并进入下一步forwardInvocation。forwardInvocation允许开发者修改响应者、方法实现等。若没有实现forwardInvocation，则直接进入doesNotRecognizeSelector，流程结束。

**2、方法调用会被缓存吗？如何缓存过，又是如何查找的呢？**

方法是会缓存进来了，不然下次再调用又要重新查一次，效率是不高的。采用散列（哈希）的方式来缓存，查询的效率是比较高的，因此内部会采用散列缓存起来。

**3、对象的内存是如何布局的？**

成员变量（包括父类）都保存在对象本身的存储空间内；本类的实例方法保存在类对象中，本类的类方法保存在元类对象中；父类的实例方法保存在各级super
class中，父类的类方法保存在各级super meta class中。

不知道这个答案是否合适！

**4、runtime有哪些应用场景？**

关于runtime的应用是很广泛的，日常开发中所用过的场景：

  * 给category添加属性
  * Method-Swizzling hook方法，然后交换方法实现来达到调用系统方法之前先做一些额外的处理
  * 埋点处理
  * 字典与模型互转
  * 模型自动获取所有属性并转换成SQL语句操作数据库

想到的也就这么些，大家可以补充！

###1.4 说说你对MVC和MVVM的理解。

MVC是出现比较早的架构设计模式，而且到现在已经是很成熟了。出现MVVM的原因是MVC中的V越来越复杂，于是才有人想要给V瘦身。

本人在公司的项目中并没有使用过MVVM架构设计模式，一直都是使用MVC的。但是项目比较大，有多个团队同时迭代。我也看了看别的团队的人写的代码，发现他们在网上
看过MVVM，于是在项目中纷纷采用MVVM的思想，一个页面分为头、中、尾三个部分，结果他们把这三个部分建立成三个view类，然后写了一堆的delegate回
调到V。当我看到这些代码的时候，我还是庆幸的，他们不是我团队的人，代码也不需要我们来维护。

我并不否定MVVM，但是MVVM若配上RAC后，对于代码review没有做好的项目，那是可以害死很多人的，特别是新手接过来之后，什么都不懂，也不会修改他人的
代码。我所接触到过的MVVM项目，都是别人的项目，看到很多项目的源代码，包括帮别人改bug的时候，发现调用层次太深，查问题也困难了很多。

其实，采用MVC的项目中，我发现很多人并不充分利用M的作用。我看过很多项目的源代码，M只是添加个属性，并没有做数据处理，而是放在V中处理的。笔者对于可以放在
M中处理的数据，是不会交给V做的。比如接口返回来的字段是标识状态的，但是最终要根据状态展示对应的文案，则笔者会增加辅助字段处理，交给M处理。

因此，我个人认为不管是MVC还是MVVM，都有其优缺点，不要过分依赖，也不要理所当然，而应该明确自己的团队是什么样类型的团队。如果都是高级开发者，采用哪种都
没有什么问题的；如果基本是初中级，别整什么MVVM了，还是使用传统的MVC吧，谁都可以读懂！

###1.5 说说UITableView的调优

通常来说，在开发中注意以下问题，可以使列表滚动比较流畅，但是对于特别复杂的列表就需要做额外的优化处理：

  * 重用cell，设置好cellIdentifier
  * 重用header、footer view，设置好identifier
  * 若高度固定，直接使用rowHight；若不固定则使用heightForRowAtIndexPath代理方法
  * 缓存cell的高度、header/footer view的高度
  * 不要修改view的opaque，默认就是YES,表示不透明度
  * 不要动态添加子view到cell上，直接在初始时创建，然后做显示与隐藏操作
  * 尽量不要直接使用cornerRadius，采用镂空图或者Core Graphics API来绘制
  * 将I/O操作、复杂运算放到子线程中处理，再回到主线程更新UI

如果列表比较复杂，对于上面的做好后，还是不够流畅，就需要通过Instruments工具来检测哪些地方可以优化了。笔者开源过一个自动计算行高的库，对于一般的a
pp，其性能是可以了：[开源HYBMasonryAutoCellHeight自动计算行高](http://101.200.209.244/masonry-cell-height-auto-calculate/)，带有高度缓存，对于不同状态下也是会缓存的。

###1.6 谈谈你对ARC的理解。

ARC是编译器帮我们完成的，我们不再手动添加retain、relase、autorelease，而且在运行期还会帮助我们优化。但是ARC并不是万能的，它并不
能自我理解循环引用问题，依然需要我们手动解决循环引用的问题。

ARC管理都会放到自动释放池中，如果我们需要做一些循环操作，生成大量的临时变量，我们还是需要加一下autoreleasepool，以及时地释放内存。

ARC下对于属性修饰符不同，其内存管理策略也不一样：

  * strong：强引用，引用计数加1
  * weak：弱引用，引用计数没有加1
  * copy：强引用，引用计数加1

ARC下还是有可能出现内存泄露的，内存得不到释放，特别是使用block的时候，一定要学会分析是否形成循环引用。看看如何分析循环引用[iOSBlock循环引用精讲](http://101.200.209.244/ios-block-memory-cycle/)。

##二面iOS题

###2.1 野指针是什么，iOS开发中什么情况下会有野指针？

所谓野指针，是指指向内存已经被释放的内存区的指针。

在iOS开发中，在iOS7下遇到一个bug：当进入播放页面时马上又返回上一个页面，偶尔出现闪退，原因就是出现了野指针（访问了已释放的对象内存区）。当进入播放
页面时，就会立刻去解析视频数据，内部是FFMPEG操作，当快速返回上一个页面时，FFMPEG还在操作中，导致访问了已释放的对象。内存这个问题是SDK内部的问
题，我们也不能解决，只能抛给SDK提供者来解决。

还有就是在使用block时，不小心也会出现野指针。

###2.2 介绍block

这与一面中的谈谈对block的理解差不多的，好像二面的面试官有点着急着结束面试。这与一面的问题可以说差不多一样的答案。

###2.3 说说你是怎么优化UITableView的。

这道题与一面的说说UITableView的调优是一样的！如果说如何优化，那就是讲讲在项目中做过哪些优化了。

##小结

这一篇文章下来，自我感觉百度的iOS面试题并不怎么难，要答个7788应该没有什么大的问题。好了，百度一面和二面的iOS题就这么过了，下一篇就是三面的手写算法
题了啊！


<hr>





####<p>原文出处：<a href='http://101.200.209.244/baidu-ios-interview-third/' target='blank'>BAT面试指南试答百度三面</a></p>

本篇文章是继[BAT面试指南试答百度一面](http://101.200.209.244/bat-interview-
first/)和[BAT面试指南试答百度二面](http://101.200.209.244/bat-interview-baidu-
second/)部分而试答，一面中只写了算法部分，将一面中的iOS部分移到二面中写，本篇完全是手写算法的三面题。

**郑重声明：**题目来源于[BAT 面试指南](https://bestswifter.com/bat-interview/)百度三面手写算法题。

##三面手写算法题

下面是随手想而写下的算法，效率可能不高，也可能会出错，大家可以根据自己的想法评论！

###3.1 给一个字符串，如何判断它是否是合法的IP地址，比如 192.168.1.1 就是合法的。

首先，我们需要明确一个合法的IP格式应该是怎么样的，每个值是1-255，因此，我们可以通过字符串分割后，分别判断值是否在1-255即可。

####3.1.1 Objective-C实现

```
/**
*  Judge whether the specified string is a valid form of IP or not.
*
*  @param ipString The specified string to be checked.
*
*  @return YES if is a valid form of IP, otherwise NO.
*/

- (BOOL)isValidIP:(NSString *)ipString {
  if (ipString.length <= 0) {
    return NO;
  }

  NSArray *tempArray = [ipString componentsSeparatedByString:@"."];
  if (tempArray.count != 4) {
    return NO;
  }

  __block BOOL isValid = YES;

  [tempArray enumerateObjectsUsingBlock:^(NSString *_Nonnull obj, NSUInteger
idx, BOOL * _Nonnull stop) {
    if (obj.integerValue < 1 || obj.integerValue > 255) {
      isValid = NO;
      *stop = YES;
    }
  }];

  return isValid;
}
```

####3.1.2 C语言实现

```
/**
*  Input：a string，judge whether it is a valid form of IP string
*
*  @param ipString
*
*  @return 1 if it is a valid form of IP string, otherwise 0
*/

int isValidIP(char *ipString) {
  int len = (int)strlen(ipString);
  
  if (len < 7 || len > 15) {
    return 0;
  }

  int itemValue = 0;
  int index = 1;
  for (int i = len - 1; i >= 0; \--i) {
    char ch = ipString[i];
    
    if (ch >= '0' && ch <= '9') {
      itemValue += (ch - '0') * pow(10, index - 1);
      index++;
    } else if (ch == '.') {
      index = 1;
      if (itemValue < 1 || itemValue > 255) {
        return 0;
      }
      
      itemValue = 0;
    } else {
      return 0;
    }
  }

  if (itemValue < 1 || itemValue > 255) {
    return 0;
  }

  return 1;
}
```


C语言实现的话，就需要遍历了。我们是从后往前遍历的，就可以一将遍历判断完成。

###3.2 说说大数相加的思路，动手写代码实现。

大学的时候搞ACM就已经实现过大数相加了，也写过算法。大数相加的关键点是通过字符串来实现相加，以串最长的作为基准，将串短的高位补0，然后对位相加，并做好进位
处理。

大学的时候已经研究过这个算法了，因此现在手写起来还是挺顺的。记得最后还可能有进位哦，需要将进位处理一下。我们这里是先低位相加，不断往高位方向移动做加法，借助
临时数组，将计算结果逆序存放。大数相加和相减都是挺简单的，大数相乘就难度大多一点点。

```
/**
 *  做两个超大数相加算法，采用0补高位的方式再做加法运算
 *
 *  @param lhsSource    大数1
 *  @param rhsSource    大数2
 *  @param result       接收结果，确保长度足够
 */
void addBigNumbers(char *lhsSource, char *rhsSource, char *result) {
  int lhsLen = (int)strlen(lhsSource);
  int rhsLen = (int)strlen(rhsSource);
  int len = lhsLen > rhsLen ? lhsLen : rhsLen;
  
  char *temp = malloc(sizeof(char *) * (len + 2));
  int i = lhsLen - 1;
  int j = rhsLen - 1;
  int k = 0;
  char lhsChar = '0';
  char rhsChar = '0';
  
  // 进位
  int carryBit = 0;
  int z = 0;
  
  while (i >= 0 || j >= 0) {
    // 串短的就以'0'补位，用于做加法运算
    if (i < 0) {
      lhsChar = '0';
    } else {
      lhsChar = lhsSource[i];
    }
    
    // 串短的就以'0'补位，用于做加法运算
    if (j < 0) {
      rhsChar = '0';
    } else {
      rhsChar = rhsSource[j];
    }
    
    // 对位相加，再加上进位值
    z = lhsChar - '0' + rhsChar - '0' + carryBit;
    // 有可能>=10，需要取做进位处理
    temp[k++] = z % 10 + '0';
    // 更新进位
    carryBit = z / 10;
    
    i--;
    j--;
  }
  
  // 全部相加完之后，有可能还有进位，需要将进位顶到高位
  while (carryBit > 0) {
    temp[k++] = carryBit % 10 + '0';
    carryBit /= 10;
  }
  
  // 我们借助了临时字符数组来存储计算结果，但是计算结果是倒序的，
  // 我们需要将计算结果变成正序
  k--;
  i = 0;
  while (k >= 0) {
    result[i++] = temp[k--];
  }
  
  // 别忘了添加上字符串结束标记符
  result[i] = '\0';
  
  // temp是自己在堆上申请的内存，记得释放
  free(temp);
}
```


随手写两个字符串相加：

```
char *lhsSource = "12368102369126318236218391231231232132132";
char *rhsSource = "9999999999999991232399999999999999999999999";
char result[100];
addBigNumbers(lhsSource, rhsSource, result);
NSLog(@"result = %s", result);
 
// print
// result = 10012368102369117550636218391231231232132131
```


###3.3 简述TCP建立和关闭连接时，握手的过程。为什么前者是三次握手，后者需要四次？

以下是百度了一下相关文章，在阅读完之后才明白为什么后者需要4次。其实，我想大家跟笔者一样，若没有搞过TCP相关的项目，怎么会记得那么多，只是记得大学教科书里
说过的三次握手。

TCP建立连接时，握手的过程大概如下：

  * 客户端发送SYN到服务端
  * 服务端发布SYN/ACK到客户端，此时开始建立连接
  * 客户端发布ACK到服务端，此时正式建立好连接

客户端发送SYN到服务端，而服务端返回了客户端发过来的SYN，同时也返回ACK，那么客户端接收到之后，就可以确定服务端收到了SYN信号，而客户端接收到服务端
返回来的ACK信号后，再将ACK信号发送到服务端，服务端就明确客户端收到了服务端发过去的信号。因此，这三次握手就可以确定了双方的身份。

TCP关闭连接时，握手的过程大致如下：

  * 客户端发送FIN包到服务端：此时客户端进入FIN_WAIT_1等待对方确认状态
  * 服务端返回ACK包到客户端：此时客户端结束FIN_WAIT_1状态，并进入FIN_WAIT_2状态，等待服务端的发过来的关闭请求
  * 服务端发送FIN包到客户端：此时服务端进入CLOSE_WAIT状态，等待客户端确认关闭请求
  * 客户端返回ACK包到服务端：此时服务端正式关闭，结束CLOSE_WAIT状夶

TCP关闭连接之所以需要四次握手，是因为TCP连接是全双工，是双向的。

更详细地部分，大家可以阅读[TCP连接建立、关闭的握手过程](http://blog.chinaunix.net/uid-25018796-id-94900
.html)这篇文章。

###3.4 假设有10W条电话号码，如何通过输入电话号码的某一段内容，快速搜索出来。比如输入234，以下两个号码都会显示在搜索结果中：

``
123456789000
188888823400
```


其实最简单的解决方案是遍历所有字符串，然后用KMP算法。但是这样的问题是需要遍历 10W
个元素，效率比较低。我想到的是办法是使用索引。建立100个索引（00 到 99），比如输入 234
时只需要在索引23对应的区域查找即可，可以加快100倍速度。但是缺点是插入数据时，需要更新多个索引，数据量会是原来的10倍。

我能想到的也是建立索引，几乎所有大批量数据中查找信息，应该都需要建立索引的。索引如何建立才能查找快，这是也需要分析的。我想公司里面的数据，也是建立好索引来检
索的，至于更新、插入操作，应该不会马上去更新索引吧，可以通过定时脚本来更新索引。比如夜黑风高的时候再跑一下脚本更新一下索引库~

###3.5 OC的数组中，添加nil对象会有什么问题。

这个问题自己问过自己，平时开发中就遇到过不少崩溃是由于插入nil对象引起的。其实字典也是一样的，插入nil对象都会引起崩溃。

比如，我们下面这么写就会引起崩溃：

```
NSMutableArray *array = [[NSMutableArray alloc] init];
 
//  -[__NSArrayM insertObject:atIndex:]: object cannot be nil'
[array addObject:nil];
```


这是很常见的崩溃打印信息吧？但是，如果我们在初始化时，通过下面的API来添加nil，是不会有事的，只是表示结束而已。

```
 
NSArray *array = [[NSArray alloc] initWithObjects:@"sss", nil, @"sfsdf"];
// 结果只有sss，后面的因为中间有nil而被过滤了
NSLog(@"%@", array);
```



##小结

百度三面题目到此结束，所答不代表一定正确，所写的算法也不确定足够健壮。好好准备一番，但愿能有机会去百度面一面！

对于3.4题，大家有什么好的算法解决吗？可以在评论中指出哦！

