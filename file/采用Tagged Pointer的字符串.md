 
<!--BEGIN_DATA
{
    "create_date": "2018-06-06 09:13", 
    "modify_date": "2018-06-06 09:13", 
    "is_top": "0", 
    "summary": "采用Tagged Pointer的字符串", 
    "tags": "iOS、C/C++、系统", 
    "file_name": "采用Tagged Pointer的字符串.md"
}
END_DATA-->

####<p>原文出处：<a href='http://www.cocoachina.com/ios/20150918/13449.html' target='blank'>采用Tagged Pointer的字符串</a></p>

本文由CocoaChina译者[@ALEX吴浩文](http://www.weibo.com/alexwuhw)翻译  
作者：[Mike Ash](https://mikeash.com/)  
原文：[Friday Q&A; 2015-07-31: Tagged Pointer Strings](https://mikeash.com/pyblog/friday-qa-2015-07-31-tagged-pointer-strings.html)  

* * *

[Tagged Pointer](https://mikeash.com/pyblog/friday-qa-2012-07-27-lets-build-tagged-pointers.html)是一个能够提升性能、节省内存的有趣的技术。在OS X 10.10中，NSString就采用了这项技术，现在让我们来看看该技术的实现过程。本话题由Ken Ferry提出。

 **回顾**

对象在内存中是对齐的，它们的地址总是指针大小的整数倍，通常为16的倍数。对象指针是一个64位的整数，而为了对齐，一些位将永远是零。

Tagged Pointer利用了这一现状，它使对象指针中非零位有了特殊的含义。在苹果的64位Objective-C实现中，若对象指针的最低有效位为1(即奇数)，则该指针为Tagged Pointer。这种指针不通过解引用isa来获取其所属类，而是通过接下来三位的一个类表的索引。该索引是用来查找所属类是采用Tagged
Pointer的哪个类。剩下的60位则留给类来使用。

Tagged Pointer有一个简单的应用，那就是NSNumber。它使用60位来存储数值。最低位置1。剩下3位为NSNumber的标志。在这个例子中，就可以存储任何所需内存小于60位的数值。

从外部看，Tagged Pointer很像一个对象。它能够响应消息，因为objc_msgSend可以识别Tagged Pointer。假设你调用integerValue，它将从那60位中提取数值并返回。这样，每访问一个对象，就省下了一次真正对象的内存分配，省下了一次间接取值的时间。同时引用计数可以是空指令，因为没有内存需要释放。对于常用的类，这将是一个巨大的性能提升。

NSString似乎并不适合Tagged Pointer，因为它的长度即可变，又可远远超过60位。然而，Tagged Pointer是可以与普通类共存的，即对一些值使用Tagged Pointer，另一些则使用一般的指针。例如，对于NSNumber，大于2^60-1的整数就不能采用Tagged Pointer来存储，而需要在内存中分配一个NSNumber的对象来存储。只要创建对象的代码编写正确，就没有问题。

NSString也是如此。对于那些所需内存小于60位的字符串，它可以创建一个Tagged Pointer。其余的则被放置在真正的NSString对象里。这使得常用的短字符串的性能得到明显的提升。实际代码就是如此吗？似乎Apple是这么认为的，因为他们这么做了并实现了它。

**可能的实现方法**

在看Apple的实现之前，让我们花点时间想想我们自己会如何实现这种字符串。最初想法很简单：置最低位为1，剩下的3位作为类的标志，60位为真正的数据。如何使用这60位是一个大问题。我们想要最大限度地利用这60位。

一个Cocoa字符串在概念上是一系列的Unicode字符。一共有1,112,064个有效的Unicode字符，所以需要21位代表一个字符。这意味着我们可以放两个字符在这60位里，浪费掉了18位。我们可以用一些额外的位来存储长度。所以一个采用Tagged Pointer的字符串可以是零个、一个或两个字符。然而被限制为只有两个字符的字符串似乎并没什么用。

NSString API实际上是基于UTF-16的实现，而不是直接基于Unicode。UTF-
16用16位的序列值来表示Unicode。最常见的基本多文种平面（Basic Multilingual Plane，BMP）字符需要16位，字符编码超过65,535的则需要两个。我们可以放三个16位进60位，剩下12位。再借用一些表示长度的位，这将允许我们表示0-3个UTF-16字符。这将允许三个BMP字符，且其中一个字符可以超出BMP的范围。被限制为三个字符的字符串的使用仍然有限。

大多数APP里的字符串是ASCII。即使APP本地化到非ASCII语言，字符串也远远不止用于显示UI。它们用于URL组件、文件扩展名、对象键、属性列表值等等。UTF-8编码是一种ASCII兼容的编码，它将每一个ASCII字符编码为一个字节，用四字节编码其他Unicode字符。我们可以在60位里放七个字节，剩下的4位表示长度。这样这种字符串可以存储七个ASCII字符，或者少一些的非ASCII字符，这取决于这些字符是什么。

如果我们要优化ASCII，我们不妨放弃对Unicode的完整支持。毕竟包含非ASCII字符的字符串可以使用真正的NSString对象。ASCII是一个七位编码，如果我们给每个字符只分配7位会发生什么？让我们存储八个ASCII字符在这60位里，再用剩下的4位存储长度。这听起来很有用。在一个APP里可能有大量的字符串是纯ASCII并且只包含8个字符或更少。

接着往下想，完整的ASCII里有很多不常用的东西。比如一堆控制字符和不常用的符号。字母和数字才是最常使用的。我们能不能把编码缩短到6位？

6位可以存储64个不同的值。ASCII里有26个字母，算上大写小写则有52个，再加上数字0-9则多达62个。如果说有两个地方需要节省，那就是空间和时间。可能有很多只包含这些字符的字符串。每6位1个字节，我们可以在60位里存储十个字符！等等！我们没有剩余空间存储长度。所以要么我们存储9个字符加长度，要么在那64个不同值里删除一个(我认为可以删除空格)，然后对于那些小于10个字符的字符串使用零作为结束符。

如果是5位呢？这不是完全荒谬的。可能有很多只存在小写字符的字符串。例如，5位可以存储32个不同的值。算上整个小写字母，也还有6个额外的值，你可以再分配一些更常见的大写字母、符号、数字或组合。如果你发现其中的一些情况更常见，你甚至可以删除一些不太常见的小写字母，例如q。如果我们省下存储长度的空间，5位编码我们可以存储十一个字符，如果我们借一个符号位并使用一个结束符则可以存储十二个字符。

接着往下想，作为一个合理的编码，5位已经尽可能的短了。你可以用一个可变长度的编码，如[霍夫曼编码](https://en.wikipedia.org/wiki/Huffman_coding)。常见的，这将允许字母e比起字母q有更短的编码。这将可能允许最短1位来编码一个字符，在一些极端的情况下假如你的字符串全部都是e。这样也将导致更复杂的空间开销，编码也可能更慢。

Apple采用了哪一种方法？让我们找出答案。

 **运用 Tagged String**

这里有一段代码，它创建了一个这种字符串并输出它的指针。

    NSString *a = @"a";
    NSString *b = [[a mutableCopy] copy];
    NSLog(@"%p %p %@", a, b, object_getClass(b));

mutableCopy/copy是必要的。原因有两个。首先，尽管像@"a"这样的字符串可以存储为一个Tagged Pointer，但是字符串常量却从不存储为Tagged Pointer。字符串常量必须在不同的操作系统版本下保持二进制兼容，而Tagged
Pointer的内部细节是没有保证的。其能使用的前提是Tagged Pointer在运行时总是由Apple的代码生成，如果编译器把它们嵌入二进制里，那么前提就被打破了（字符串常量就是这样）。因此我们需要copy常量字符串来获取Tagged
Pointer。

mutableCopy是必要的，因为NSString太聪明，而且也知道一个不可变字符串的副本是一个毫无意义的操作，所以它会返回原字符串的当作“copy”。字符串常量是不可变的，所以[a copy]结果只是a。一个可变量的副本强迫它产生真正副本，这样一个可变量副本的不可变的副本足以让系统给我们产生一个采用Tagged Pointer的字符串。

注意不要在你自己的代码里依赖这些细节！这是NSString的当前情况，它随时可能改变。如果你的代码某种程度上依赖于此，那么代码最终将失效。幸运的是，只有非正常的代码才会这样。所有正常、合理的代码都没有问题，傻傻的不知道任何Tagged Pointer而幸福着吧。

以下是上面代码在我电脑上的输出。  

    0x10ba41038 0x6115 NSTaggedPointerString

首先你可以看到原始指针，一个真正的对象指针。副本是第二个值，非常清楚，这是一个奇数，这意味着它不是一个有效的对象指针。这也是一个较小的数，在未映射且不可映射的4GB零页的64位Mac地址空间的开头里，这使它更加不可能是一个对象指针。

我们从这个0x6115中可以推断出什么？我们知道，Tagged Pointer的最低4位是其机制本身的一部分。最低半字节5的二进制是0101。最低位表示它是一个Tagged Pointer。接下来的3位表示其所属类。010，表明字符串类在类表中的索引为2。这些信息并不是很有用。

开头的61是有启发性的。61在十六进制里正好是小写字母a的ASCII编码，这正是字符串的值。看来是直接的ASCII编码。方便！

类名告诉了我们这个类的用途，并是一个很好的去考虑其真正的代码实现的入手点。我们会很快谈到它，但是先让我们再做一些外部检查。

以下是一个循环，构建了许多形如abcdef……的字符串，并一个接一个输出，直到停止产生Tagged Pointer。

    
    NSMutableString *mutable = [NSMutableString string];
    NSString *immutable;
    char c = 'a';
    do {
        [mutable appendFormat: @"%c", c++];
        immutable = [mutable copy];
        NSLog(@"0x6lx %@ %@", immutable, immutable, object_getClass(immutable));
    } while(((uintptr_t)immutable & 1) == 1);

第一个输出：

    0x0000000000006115 a NSTaggedPointerString

上面我们看到的这个匹配值。请注意，我输出了包含所有前导零得完整指针，这样能更清楚与后续输出值比较。让我们再看看第二个输出:

    0x0000000000626125 ab NSTaggedPointerString

正如我们所想的那样，最低的四位并没有改变。即那个5将保持不变，表明这是一个NSTaggedPointerString类型的Tagged Pointer。

前面的61没变，并加入了62。62显然是b的ASCII编码。所以我们可以看到，这是一个八位的ASCII编码。5之前的值从1变到2，表明这可能是长度。后续的输出证实了这一点：

    0x0000000063626135 abc NSTaggedPointerString
    0x0000006463626145 abcd NSTaggedPointerString
    0x0000656463626155 abcde NSTaggedPointerString
    0x0066656463626165 abcdef NSTaggedPointerString
    0x6766656463626175 abcdefg NSTaggedPointerString

大概就到这里了。Tagged Pointer已满，下一次迭代将分配一个真正的NSString对象并终止循环。对吗？错了！

    0x0022038a01169585 abcdefgh NSTaggedPointerString
    0x0880e28045a54195 abcdefghi NSTaggedPointerString
    0x00007fd275800030 abcdefghij __NSCFString

循环还经过两次迭代之后才停止。数据部分继续增长，其余部分变成乱码。发生了什么？让我们看看其具体实现。

 **反编译**

NSTaggedPointer类在CoreFoundation框架里，似它乎应该在Foundation框架里，但是最近很多核心Objective-C类已经搬到CoreFoundation里了，Apple正在慢慢放弃让CoreFoundation成功一个独立的实体。

让我们先看看 -[NSTaggedPointerString length] 的实现：

    push       rbp
    mov        rbp, rsp
    shr        rdi, 0x4
    and        rdi, 0xf
    mov        rax, rdi
    pop        rbp
    ret

用Hopper进行反编译
    
    unsigned long long -[NSTaggedPointerString length](void * self, void * _cmd) {
        rax = self >> 0x4 & 0xf;
        return rax;
    }

简而言之，为了得到长度，提取4-7位并返回。这证实了我们之前的想法。

另一个NSString的原始方法是characterAtIndex:。我将跳过冗长的反编译，以下是Hopper的反编译输出，已经相当可读了：
    
    
    unsigned short -[NSTaggedPointerString characterAtIndex:](void * self, void * _cmd, unsigned long long arg2) {
        rsi = _cmd;
        rdi = self;
        r13 = arg2;
        r8 = ___stack_chk_guard;
        var_30 = *r8;
        r12 = rdi >> 0x4 & 0xf;
        if (r12 >= 0x8) {
                rbx = rdi >> 0x8;
                rcx = "eilotrm.apdnsIc ufkMShjTRxgC4013bDNvwyUL2O856P-B79AFKEWV_zGJ/HYX";
                rdx = r12;
                if (r12 < 0xa) {
                        do {
                                *(int8_t *)(rbp + rdx + 0xffffffffffffffbf) = *(int8_t *)((rbx & 0x3f) + rcx);
                                rdx = rdx - 0x1;
                                rbx = rbx >> 0x6;
                        } while (rdx != 0x0);
                }
                else {
                        do {
                                *(int8_t *)(rbp + rdx + 0xffffffffffffffbf) = *(int8_t *)((rbx & 0x1f) + rcx);
                                rdx = rdx - 0x1;
                                rbx = rbx >> 0x5;
                        } while (rdx != 0x0);
                }
        }
        if (r12 <= r13) {
                rbx = r8;
                ___CFExceptionProem(rdi, rsi);
                [NSException raise:@"NSRangeException" format:@"%@: Index %lu out of bounds; string length %lu"];
                r8 = rbx;
        }
        rax = *(int8_t *)(rbp + r13 + 0xffffffffffffffc0) & 0xff;
        if (*r8 != var_30) {
                rax = __stack_chk_fail();
        }
        return rax;
    }

让我们整理一下。前三行只是Hopper告诉我们哪些寄存器获取哪些参数。让我们用_cmd替换rsi，用self替换rdi。因为arg2实际上就是index，所以让我们用index替换r13。让我们去掉所有__stack_chk，因为它只是用于加强安全性，和方法的具体实现无关。这样整理后变成：

    
    unsigned short -[NSTaggedPointerString characterAtIndex:](void * self, void * _cmd, unsigned long long index) {
        r12 = self >> 0x4 & 0xf;
        if (r12 >= 0x8) {
                rbx = self >> 0x8;
                rcx = "eilotrm.apdnsIc ufkMShjTRxgC4013bDNvwyUL2O856P-B79AFKEWV_zGJ/HYX";
                rdx = r12;
                if (r12 < 0xa) {
                        do {
                                *(int8_t *)(rbp + rdx + 0xffffffffffffffbf) = *(int8_t *)((rbx & 0x3f) + rcx);
                                rdx = rdx - 0x1;
                                rbx = rbx >> 0x6;
                        } while (rdx != 0x0);
                }
                else {
                        do {
                                *(int8_t *)(rbp + rdx + 0xffffffffffffffbf) = *(int8_t *)((rbx & 0x1f) + rcx);
                                rdx = rdx - 0x1;
                                rbx = rbx >> 0x5;
                        } while (rdx != 0x0);
                }
        }
        if (r12 <= index) {
                rbx = r8;
                ___CFExceptionProem(self, _cmd);
                [NSException raise:@"NSRangeException" format:@"%@: Index %lu out of bounds; string length %lu"];
                r8 = rbx;
        }
        rax = *(int8_t *)(rbp + index + 0xffffffffffffffc0) & 0xff;
        return rax;
    }

在第一个if语句之前有这一行： 
    
    r12 = self >> 0x4 & 0xf

这正是之前看到的提取长度的代码。让我们用length替换r12：

    
    
    unsigned short -[NSTaggedPointerString characterAtIndex:](void * self, void * _cmd, unsigned long long index) {
        length = self >> 0x4 & 0xf;
        if (length >= 0x8) {
                rbx = self >> 0x8;
                rcx = "eilotrm.apdnsIc ufkMShjTRxgC4013bDNvwyUL2O856P-B79AFKEWV_zGJ/HYX";
                rdx = length;
                if (length < 0xa) {
                        do {
                                *(int8_t *)(rbp + rdx + 0xffffffffffffffbf) = *(int8_t *)((rbx & 0x3f) + rcx);
                                rdx = rdx - 0x1;
                                rbx = rbx >> 0x6;
                        } while (rdx != 0x0);
                }
                else {
                        do {
                                *(int8_t *)(rbp + rdx + 0xffffffffffffffbf) = *(int8_t *)((rbx & 0x1f) + rcx);
                                rdx = rdx - 0x1;
                                rbx = rbx >> 0x5;
                        } while (rdx != 0x0);
                }
        }
        if (length <= index) {
                rbx = r8;
                ___CFExceptionProem(self, _cmd);
                [NSException raise:@"NSRangeException" format:@"%@: Index %lu out of bounds; string length %lu"];
                r8 = rbx;
        }
        rax = *(int8_t *)(rbp + index + 0xffffffffffffffc0) & 0xff;
        return rax;
    }

在if语句的内部，第一行把self右移了8位。这8位记录的是：Tagged
Pointer标记和字符串长度。其余部分，就是我们认为的真正的数据。让我们用stringData替换rbx使代码更加清晰。下一行似乎是把某种查询表赋给rcx，所以让我们用table替换rcx。最后，length的副本被赋给rdx。看来将被用作某种游标，让我们用cursor替换rdx。现在我们的代码长这样：

    
    unsigned short -[NSTaggedPointerString characterAtIndex:](void * self, void * _cmd, unsigned long long index) {
        length = self >> 0x4 & 0xf;
        if (length >= 0x8) {
                stringData = self >> 0x8;
                table = "eilotrm.apdnsIc ufkMShjTRxgC4013bDNvwyUL2O856P-B79AFKEWV_zGJ/HYX";
                cursor = length;
                if (length < 0xa) {
                        do {
                                *(int8_t *)(rbp + cursor + 0xffffffffffffffbf) = *(int8_t *)((stringData & 0x3f) + table);
                                cursor = cursor - 0x1;
                                stringData = stringData >> 0x6;
                        } while (cursor != 0x0);
                }
                else {
                        do {
                                *(int8_t *)(rbp + cursor + 0xffffffffffffffbf) = *(int8_t *)((stringData & 0x1f) + table);
                                cursor = cursor - 0x1;
                                stringData = stringData >> 0x5;
                        } while (cursor != 0x0);
                }
        }
        if (length <= index) {
                rbx = r8;
                ___CFExceptionProem(self, _cmd);
                [NSException raise:@"NSRangeException" format:@"%@: Index %lu out of bounds; string length %lu"];
                r8 = rbx;
        }
        rax = *(int8_t *)(rbp + index + 0xffffffffffffffc0) & 0xff;
        return rax;
    }

这几乎是所有的变量。剩下一个原始寄存器名：rbp。这实际上是帧指针，所以编译器直接从帧指针做一些索引。加一个0xffffffffffffffbf常数是二进制补码中“一切都是一个无符号整数（everything is ultimately an unsigned
integer）”减去65的方法。然后，它减去64。这在堆栈上可能都是相同的局部变量。鉴于按字节索引，这可能是一个放在堆栈种的缓冲。奇怪的是，其实有一个方法能够直接读取缓冲区而无需专门编写。发生了什么？

原来Hopper忘了反编译在if外的else的部分。整合在一起变成了这样：

    mov        rax, rdi
    shr        rax, 0x8
    mov        qword [ss:rbp+var_40], rax

var_40在Hopper的反编译中表示的偏移量64。(40是64的十六进制版本)让我们调用这个指向位置缓冲区的指针。这个错失部分的C版本看起来是这样：

    *(uint64_t *)buffer = self >> 8

让我们继续并插入这句代码，并用buffer替换rbp，这使得代码更加可读。另外添加一个缓冲区的声明来提醒我们：
    

    unsigned short -[NSTaggedPointerString characterAtIndex:](void * self, void * _cmd, unsigned long long index) {
        int8_t buffer[11];
        length = self >> 0x4 & 0xf;
        if (length >= 0x8) {
                stringData = self >> 0x8;
                table = "eilotrm.apdnsIc ufkMShjTRxgC4013bDNvwyUL2O856P-B79AFKEWV_zGJ/HYX";
                cursor = length;
                if (length < 0xa) {
                        do {
                                *(int8_t *)(buffer + cursor - 1) = *(int8_t *)((stringData & 0x3f) + table);
                                cursor = cursor - 0x1;
                                stringData = stringData >> 0x6;
                        } while (cursor != 0x0);
                }
                else {
                        do {
                                *(int8_t *)(buffer + cursor - 1) = *(int8_t *)((stringData & 0x1f) + table);
                                cursor = cursor - 0x1;
                                stringData = stringData >> 0x5;
                        } while (cursor != 0x0);
                }
        } else {
            *(uint64_t *)buffer = self >> 8;
        }
        if (length <= index) {
                rbx = r8;
                ___CFExceptionProem(self, _cmd);
                [NSException raise:@"NSRangeException" format:@"%@: Index %lu out of bounds; string length %lu"];
                r8 = rbx;
        }
        rax = *(int8_t *)(buffer + index) & 0xff;
        return rax;
    }

好多了。虽然有些疯狂的指针操作语句有点难读，但是他们只是数组索引。让我们解决这个问题：

   
    unsigned short -[NSTaggedPointerString characterAtIndex:](void * self, void * _cmd, unsigned long long index) {
        int8_t buffer[11];
        length = self >> 0x4 & 0xf;
        if (length >= 0x8) {
                stringData = self >> 0x8;
                table = "eilotrm.apdnsIc ufkMShjTRxgC4013bDNvwyUL2O856P-B79AFKEWV_zGJ/HYX";
                cursor = length;
                if (length < 0xa) {
                        do {
                                buffer[cursor - 1] = table[stringData & 0x3f];
                                cursor = cursor - 0x1;
                                stringData = stringData >> 0x6;
                        } while (cursor != 0x0);
                }
                else {
                        do {
                                buffer[cursor - 1] = table[stringData & 0x1f];
                                cursor = cursor - 0x1;
                                stringData = stringData >> 0x5;
                        } while (cursor != 0x0);
                }
        } else {
            *(uint64_t *)buffer = self >> 8;
        }
        if (length <= index) {
                rbx = r8;
                ___CFExceptionProem(self, _cmd);
                [NSException raise:@"NSRangeException" format:@"%@: Index %lu out of bounds; string length %lu"];
                r8 = rbx;
        }
        rax = buffer[index];
        return rax;
    }

现在我们已经取得了一些进展。

我们可以看到根据不同的长度分为三种情况。长度值小于8走错失的else分支，只是取值，移位，放到缓冲区。这是纯ASCII的情况。在这里，index是用来索引self的值并提取指定的字节，然后返回给调用者。既然ASCII编码在ASCII范围内匹配Unicode编码，也就无需额外的操作来读出正确的值。我们之前猜测纯ASCII的字符串是以这种方式存储，这里证实了这种猜测。

如果长度是8或者更长呢？如果长度是8或者更长但比10（0xa）小，代码进入一个循环。这个循环取低6位的stringData，当作一个表的索引，然后将该值复制到缓冲区。然后把stringData右移6位并循环，直到它遍历整个字符串。这是六位编码，先把六位编码映射到ASCII字符再存储在表中。在缓冲区建立临时字符串，然后在索引操作结束时从中提取所要求的字符。

如果长度是10或者更长呢？代码几乎相同，除了它是五位循环一次，而不是六位。这是一个更紧凑的编码，使字符串能存储11字符，但使用一个只有32个值的编码表。这将使用六位编码表的前半个表作为编码表。

因此我们可以看到采用Tagged Pointer的字符串的结构是:

1：如果长度介于0到7，直接用八位编码存储字符串。

2：如果长度是8或9，用六位编码存储字符串，使用编码表“eilotrm.apdnsIc ufkMShjTRxgC4013bDNvwyUL2O856P-
B79AFKEWV_zGJ/HYX”。

3：如果长度是10或11，用五位编码存储字符串,使用编码表“eilotrm.apdnsIc ufkMShjTRxgC4013”

让我们与之前输出的数据对比一下：

    0x0000000000006115 a NSTaggedPointerString
    0x0000000000626125 ab NSTaggedPointerString
    0x0000000063626135 abc NSTaggedPointerString
    0x0000006463626145 abcd NSTaggedPointerString
    0x0000656463626155 abcde NSTaggedPointerString
    0x0066656463626165 abcdef NSTaggedPointerString
    0x6766656463626175 abcdefg NSTaggedPointerString
    0x0022038a01169585 abcdefgh NSTaggedPointerString
    0x0880e28045a54195 abcdefghi NSTaggedPointerString
    0x00007fbad9512010 abcdefghij __NSCFString

二进制0x0022038a01169585去掉末尾8位再分割成一个个6位的块变成：

    001000 100000 001110 001010 000000 010001 011010 010101

用这些索引去编码表中获取值，我们可以看到，这确实拼出“abcdefgh”。

同样，二进制of0x0880e28045a54195去掉末尾8位再分割成一个个6位的块变成：

    001000 100000 001110 001010 000000 010001 011010 010101 000001

我们可以看到前面是相同的，不过末尾加上i。

但接下来就离奇了。接下来，它本应该用五位编码返回两个字符串，然而它却开始生成长度为10的对象。到底发生了什么？

五位编码表是非常有限了，但不包括字母b！在神圣的五位编码表里，那个字母肯定不是常见到足以留下。让我们从c开始再试试。以下是输出：

    0x0000000000006315 c NSTaggedPointerString
    0x0000000000646325 cd NSTaggedPointerString
    0x0000000065646335 cde NSTaggedPointerString
    0x0000006665646345 cdef NSTaggedPointerString
    0x0000676665646355 cdefg NSTaggedPointerString
    0x0068676665646365 cdefgh NSTaggedPointerString
    0x6968676665646375 cdefghi NSTaggedPointerString
    0x0038a01169505685 cdefghij NSTaggedPointerString
    0x0e28045a54159295 cdefghijk NSTaggedPointerString
    0x01ca047550da42a5 cdefghijkl NSTaggedPointerString
    0x39408eaa1b4846b5 cdefghijklm NSTaggedPointerString
    0x00007fbd6a511760 cdefghijklmn __NSCFString

我们现在有长度为11的采用Tagged Pointer的字符串。最后两个字符串的二进制是：

    01110 01010 00000 10001 11010 10101 00001 10110 10010 00010
    01110 01010 00000 10001 11010 10101 00001 10110 10010 00010 00110

正如我们所想的那样。

 **创建采用Tagged Pointer的字符串**

既然我们已经知道这种字符串如何编码，我就不在创建它们的代码中涉及具体细节。我们发现了一个叫__CFStringCreateImmutableFunnel3的私有方法，这个巨大的方法处理了所有情况下的字符串创建。这个函数包含在CoreFoundation的开源版本里，在[opensource.apple.com](http://opensource.apple.com/)上。但别激动：采用Tagged Pointer的字符串并不包括在开源版本里。

这里的代码基本上和上面的相反。如果字符串的长度和内容适合Tagged Pointer，它构建一个Tagged Pointer，包含ASCII、六位编码或五位编码。其中有一个逆查询表。这个表视为一个全局的字符串常量称为sixBitToCharLookup，并有相应的称为charToSixBitLookup的表在方法Funnel3里。

 **神秘的表**

完整的六位编码表是：

    eilotrm.apdnsIc ufkMShjTRxgC4013bDNvwyUL2O856P-B79AFKEWV_zGJ/HYX

一个显然的问题是：为什么这个指令这么奇怪?

因为这个表同时用于六位编码和五位编码，它不完全按字母顺序排列是有意义的。最常使用的字符应该是上半部分，而较少使用的字符应该在下半部分。这可以确保尽可能多的长字符串可以使用五位编码。

然而，这种分为两个部分的分割，每个部分内的顺序并不重要。每个部分内本身是可以按照字母表顺序排列的，然而实际上没有这样。

表中前几个字母与字母出现在英语里的频率相似。最常见的英文字母是E，然后是T，A，O，I，N，S。E作为表的开头是正确的，其他的则靠近开头。表似乎是按使用频率排序。与英语的差异可能是因为Cocoa APP中的短字符串并不是一个从英语散文中随机选择的单词，而是更专业的语言。

我推测Apple最初想使用一个更漂亮的变长编码，可能基于[霍夫曼编码](https://en.wikipedia.org/wiki/Huffman_coding)。但是太困难，或者不值得，或者他们时间不够了，所以他们退而求其次推出一个如上所述的不那么雄心勃勃的版本，字符串使用定长的八位，六位，或五位编码。奇怪的表是当前版本的一个残留物，也是一个起点，如果他们决定在未来去采用变长编码。这是纯粹的猜测，它看起来更像是我会做的事。

 **结论**

Tagged
Pointer是一个很棒的技术，能把它运用在字符串上很不寻常。显然Apple花了很多心思在这上面，他们必须要看到一个显著的好处。看他们如何把这些技术融合在一起，看他们如何在非常有限的空间里面尽可能的存储信息，实在有趣。
