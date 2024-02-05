 
<!--BEGIN_DATA
{
    "create_date": "2020-01-10 11:30", 
    "modify_date": "2020-01-10 11:30", 
    "is_top": "0", 
    "summary": "Linux内核编程规范与代码风格", 
    "tags": "Linux", 
    "file_name": "Linux内核编程规范与代码风格.md"
}
END_DATA-->

####<p>原文出处：<a href='https://www.cnblogs.com/trav/p/10356415.html' target='blank'>Linux内核编程规范与代码风格</a></p>

>source: https://www.kernel.org/doc/html/latest/process/coding-style.html  
>translated by trav, travmymail@gmail.com

这是一篇阐述Linux内核编程代码风格的文档，译者以学习为目的进行翻译。

####1 缩进

Tab的宽度是八个字符，因此缩进的宽度也是八个字符。有些异教徒想让缩进变成四个字符，甚至是两个字符的宽度，这些人和那些把 PI 定义为 3的人是一个路子的。

注意：缩进的全部意义在于清晰地定义语句块的开始与结束，特别是当你盯着屏幕20个小时之后，你会发现长的缩进宽度的作用。

现在有些人说八个字符的宽度太宽了，这会让代码往右移很远，在一块八十字符宽的屏幕上，这样的代码会很难阅读。对此的回答是，如果你写的代码需要超过三层的缩进，那么你把一切都搞砸了，你应该修复你的程序。

简而言之，八个字符宽度的缩进让代码更容易阅读，并且额外的好处就是提醒你，不要在一个函数里写太多层的嵌套逻辑。请记住这个警示。

switch语句的缩进方式是让case与switch对齐：

    
    switch (suffix) {
    case 'G':
    case 'g':
            mem <<= 30;
            break;
    case 'M':
    case 'm':
            mem <<= 20;
            break;
    case 'K':
    case 'k':
            mem <<= 10;
            /* fall through */
    default:
            break;
    }


不要在单独一行里写多个语句，除非你想干什么不为人知的事：

    
    if (condition) do_this;
        do_something_everytime;


对了，不要把多个赋值语句放在同一行，内核的代码风格是十分简洁的，请尽量避免使用复杂的表达式。

除了在注释、文档和Kconfig中，永远不要使用空格作为缩进，上面的例子是故意犯的错误。

找一个像样的编辑器，不要在行末留有空格。

####2 换行

规范代码风格的目的是提高代码的可读性和维护性。

单行的宽度限制为八十列，这是强烈推荐的设置。

任何一行超过八十列宽度的语句都应该拆分成多个行，除非超过八十列的部分可以提高可读性且不会隐藏信息。拆分出来的子句长度总是应该比其主句要短，并且应该尽量靠右。这条法则同样适用于一个有很长的参数列表的函数头。然而，千万不要把用户可见的字符串，比如 printk 的信息，拆分成多行，因为这样会导致使用 grep 的时候找不到这些信息。

####3 括号与空格

另一个关于 C 代码风格的议题就是大括号的位置。这个问题不像缩进那么具有技术性，我们并不能说某一种风格要在技术上优于另一种风格。但是我们更推荐的，就是有远见的 Kernighan 和 Ritchie 展示的方式，把左括号放在行末，把右括号放在行首：

    
    if (x is true) {
            we do y
    }


这同样适用于其他非函数的语句块 (if, switch, for, while, do) ：

    
    switch (action) {
    case KOBJ_ADD:
            return "add";
    case KOBJ_REMOVE:
            return "remove";
    case KOBJ_CHANGE:
            return "change";
    default:
            return NULL;
    }


然而，有一个特殊的例子，就是函数：函数的左括号应该放在行首：

    
    int function(int x)
    {
            body of function
    }


异教徒们会认为这样的风格是不一致的，但是所有有脑子的人都知道尽管是 K&R 也是不一致的(译者注：K&R这本书的第一版和第二版有不一致的地方)。除此之外，我们知道函数是很特殊的，在 C 语言中，你不能有嵌套函数。


注意到，右括号一般是单独成一行的，除非右括号之后紧随着紧密结合的语句，例如 do-while 语句和 if 语句：

    
    do {
            body of do-loop
    } while (condition);


以及

    
    if (x == y) {
            ..
    } else if (x > y) {
            ...
    } else {
            ....
    }


依据：K&R

注意到，这种风格应该在不降低可读性的前提下尽可能减少空行的数量。想一想，在一块只有 25 行的屏幕上，无用的换行少了，那么就有更多的空行来写注释。

当单行语句可以解决的时候，不要使用没必要的括号：

    
    if (condition)
            action();

以及

    
    if (condition)
            do_this();
    else
            do_that();


这一点不适用于只有一个 case 有单行，其他 case 有多行的情况：

    
    if (condition) {
            do_this();
            do_that();
    } else {
            otherwise();
    }


在一个循环中超过一个语句的情况也同样需要使用括号：

    
    while (condition) {
            if (test)
                    do_something();
    }


**3.1 空格**


Linux 内核风格的空格主要用在一些关键字上，即在关键字之后添一个空格。值得关注的例外是一些长得像函数的关键字，比如：**sizeof**,**typeof**, **alignof**, ****attribute****，在 Linux 中，这些关键字的使用都会带上一对括号，尽管在 C 语言的使用上并不需要带上括号。

所以在下面这些关键字之后添加一个空格：


    if, switch, case, for, do, while


但是不要添加在 **sizeof**, **typeof**, **alignof**, ****attribute**** 之后：

    
    s = sizeof(struct file);


不要在括号周围多此一举的添加空格，下面这个例子糟透了：

    
    s = sizeof( struct file );


在声明指针或者返回值为指针的函数时，星号的位置应该紧靠着变量名或函数名，而不是类型名，例如：


    char *linux_banner;
    unsigned long long memparse(char *ptr, char **retptr);
    char *match_strdup(substring_t *s);


在二元操作符和三元操作符周围添加一个空格，例如：

    
    =  +  -  <  >  *  /  %  |  &  ^  <=  >=  ==  !=  ?  :


但是不要在一元操作符之后添加空格：

    
    &  *  +  -  ~  !  sizeof  typeof  alignof  __attribute__  defined


不要在后缀的自增自减一元操作符之前添加空格：
    
    ++  --


不要在前缀的自增自减一元操作符之后添加空格：
    
    ++  --


不要在结构体成员操作符周围添加空格：
    
    .  ->


不要在行末添加多余的空格。一些编辑器的“智能”缩进会帮你在行首添加一些空格，好让你在下一行可以立即写代码。但是某些编辑器不会帮你把多余的空格给删掉，尽管你已经写完了一行代码。比如你只想留一行空行，但是编辑器却“好心”地帮你填上了一些空格。这样一来，你就在行末添加了多余的空格。

Git 通常会警告你，让你除去这些多余的空格，并且可以帮你删掉这些东西。但是，如果你让 Git 一直帮你这样修补你的代码，这很可能导致代码行的上下错乱，之后的自动修补的失败。

####4 命名

C 是一种简洁粗旷的语言，因此，你的命名也应该是简洁的。C 程序员不会像 Modula-2 和 Pascal 程序员那样使用ThisVariableIsATemporaryCounter 这种“可爱”的名字，一个 C 程序员会把这种变量命名为 tmp ，如此简洁易写。

尽管看到一个混合大小写的名字让人皱眉，不过对于全局变量来说，一个具有描述性的名字还是很有必要的。去调用一个名为 foo 的全局函数同样让人难以接受。

全局变量(只有当你真正需要的时候才用它)和全局函数需要使用描述性的名字。如果你有一个计算活跃用户数量的函数，你应该起这样一个名字`count_active_users()` 或者类似的，而不是这样一个名字 `cntusr()` 。

起一个包含函数类型的名字(匈牙利命名法)是摧残大脑的行为，编译器知道函数的类型并且会检查类型，这样的名字不会起到任何帮助，它仅仅会迷惑程序员。所以，也难怪微软做出了那么多充满了 bug 的程序。

局部变量名应该简短，如果你需要写一个循环，定义一个计数器，在不产生歧义的情况下，你大可命名为 i ，命名为 loop_counter 是生产力很低的行为。同样地，tmp 可以是任何类型的临时变量。

如果你担心会弄混变量名，那么你遇到了另一个问题，你患上了函数增长荷尔蒙失调综合症。

####5 Typedefs

请不要使用 `vps_t` 这种东西，这是 typedef 的错误用法，当你看到

    
    vps_t a;


这种写法时，它究竟是个什么东西？相反，如果是这样的写法

    
    struct virtual_container *a;


你就很容易知道 a 代表着什么。

很多人认为 typedef 是用来帮助提高可读性的，但是事实往往不是这样的。typedef 仅仅有如下用处：

a. 封装对象(typedef 可以方便的隐藏对象)

例如，`pte_t` 会把对象封装起来，你仅仅只能通过合适的“访问函数”(成员函数)来访问这个对象。

注意：封装和“访问函数”(成员函数)本身就不是好东西，我们使用 `pte_t` 这种东西的理由就是，它指向的对象本身绝对没有东西可以访问(我们压根儿不使用封装和成员函数那一套)。

b. 指明整数类型，这种抽象可以帮助我们避免一些使用 int 和 long 的疑虑

u8/u16/u32 是完美的使用 typedef 的例子。

注意：你必须要有明确的理由来使用这些用法，如果一些地方使用的本身就是 unsigned long ，那么你没有任何理由这样做

    
    typedef unsigned long myflags_t;


但是如果你有明确的理由来解释为什么在某种情况下使用 unsigned int，而在其他情况下使用 unsigned long，那么大可使用typedef。

c. 使用 sparse 去新建一个类型来做类型检查

d. 在某些情况下新建一个与 C99 标准相等的类型

尽管只需要花一小段眼睛和大脑的时间来适应新标准的类型，如 `uint32_t`，但是一些人还是反对使用他们。

因此，你可以使用 Linux 独有的 u8/u16/u32/u64 和他们的有符号版本，也可以使用和他们等价的新标准的类型，他们的使用都不是强制的。

当你所编辑的代码已经使用了某一种版本时，你应该按照原样使用相同的版本。

e. 用户空间中的类型安全

用户空间中的某些特定的结构体中，我们不能使用 C99 定义的新类型以及上述的 u32，取而代之，我们统一使用 `__u32` 之类的类型。

也许还有其他情况，但是基本的规则就是，如果你不能满足上述其中一条情况，你就永远不要使用 typedef。

通常，一个指针或者一个有可访问元素的结构体，都不应该使用 typedef。

####6 函数

函数应该短小精悍，一个函数只干一件事。一个函数的代码两个屏幕就应该装得下(ISO/ANSI标准屏幕大小是80x24)，简单说就是，做一件事并且把它做好。  
数的最大长度与函数的复杂度和缩进程度成反比，所以，如果你有一个简单的函数，函数里面只是需要处理一个又一个的 case，每个 case 只是干一些小事，函数长度长一些也没关系。

然而，如果你的函数十分复杂，你怀疑一个不像你一样天才的高中生看不懂，你应该遵守函数最大的长度的限制，使用一些有描述性名称的辅助函数。如果你认为函数的性能至关重要，你可以让编译器把这些辅助函数编译成内联函数，一般情况下编译器可以比你做得更好。

另一个测量函数的因素是局部变量的数量，他们不应该超出5-10个这个范围，否则你就犯了一些错误。重新思考这个函数，把它拆分成更小的几段。人类的大脑一般只能同时关注七件不同的事，更多需要关注的事情意味着更多的困扰。尽管你认为你是个天才，但是你也希望理解一段你两周之前写的代码。

在源文件中，用一个空行分割不同的函数，如果函数需要导出到外部使用，那么它对应的 EXPORT 宏应当紧随在函数之后，例如：


    
    int system_is_up(void)
    {
            return system_state == SYSTEM_RUNNING;
    }
    EXPORT_SYMBOL(system_is_up);


函数原型中，参数名应该与参数类型引起写出来，尽管 C 语言允许只写上参数类型，但是我们更推荐参数名，因为这是一种为读者提供有价值信息的简单方式。

不要在函数原型之前使用`extern`关键字，因为这是不必要且多余的。

####7 集中函数出口

尽管许多人反对，但是 goto 语句频繁地以无条件跳转的形式被编译器使用。

当函数有多个出口，并且返回之前需要做很多相似的工作时，比如清理空间，这时候 goto 语句是十分方便的。当然了，如果没有类似的清理工作要在返回之前做，那么直接返回即可。

根据 goto 的作用来决定一个 label 的名字，如果 goto 语言要去释放缓存，那么`out_free_buffer:`会是一个好名字。避免使用
GW-BASIC 的命名方式，比如 `err1:` 

`err2:`，因为当你需要新加或者删除某些函数出口时，你就需要重新排列标签数字，这会让代码的正确性难以得到保证。

使用 goto 的理由如下：

无条件跳转易于理解和阅读

可以减少嵌套

可以减少修改个别函数出口代码所造成的错误

算是帮助编译器做了一些优化的工作

    
    int fun(int a)
    {
            int result = 0;
            char *buffer;
            buffer = kmalloc(SIZE, GFP_KERNEL);
            if (!buffer)
                    return -ENOMEM;
            if (condition1) {
                    while (loop1) {
                            ...
                    }
                    result = 1;
                    goto out_free_buffer;
            }
            ...
    out_free_buffer:
            kfree(buffer);
            return result;
    }


一个常见的 bug 被称作 one err bug，它长得像这样：
    
    err:
            kfree(foo->bar);
            kfree(foo);
            return ret;


bug 在于某些 goto 语句跳转到此时，foo 仍然是 NULL，修复此 bug 的简单方式就是将一个 label
拆分成两个，`err_free_bar:` 和 `err_free_foo:`：


    err_free_bar:
            kfree(foo->bar);
    err_free_foo:
            kfree(foo);
            return ret;


事实上，你应该进行测试，模拟错误情况的发生，测试所有的出口代码。

####8 注释

注释是好的，但是要避免过分注释。永远不要去尝试解释你的代码如何工作，而是花时间在写出好的代码来，解释一段烂代码是浪费时间。

一般来说，你应该去说明你的代码做了什么，而不是怎么做。同样地，尽量避免在函数体内写注释，如果你的函数如此复杂，以致于你需要在函数体内分几段注释来解释，那么你应该回到第六节去看看。你可以写一小段的注释来标记或者提醒大家哪些地方写得真聪明(或者真烂)，但是不要做得太过分。除此之外，你应该把注释写在函数开头，告诉人们这个函数干了什么，为什么要这样干。


当你给 kernel API 进行注释的时候，请你使用 kernel-doc 的格式。具体参见
https://www.kernel.org/doc/html/latest/doc-guide/index.html#doc-guide


多行注释推荐的格式如下：

    
    /*
    * This is the preferred style for multi-line
    * comments in the Linux kernel source code.
    * Please use it consistently.
    *
    * Description:  A column of asterisks on the left side,
    * with beginning and ending almost-blank lines.
    */


对于在 net/ 和 drivers/net/ 中的文件，推荐的多行注释格式如下：

    
    /* The preferred comment style for files in net/ and drivers/net
    * looks like this.
    *
    * It is nearly the same as the generally preferred comment style,
    * but there is no initial almost-blank line.
    */


对一些数据和变量进行注释也是必要的，无论他们是基本类型的还是派生类型的。为了进行注释，你应该在一行内只声明一个变量，不要使用逗号进行多个声明，这让你有地方对每一个变量进行注释。

####9 你已经弄得一团糟

没关系，我们都犯过错。你的那些 Unix 的老手朋友们可能会告诉你，GNU emacs 能帮你自动地对 C 代码进行排版，你也注意到它确实可以。但是它默认的排版方式真的很糟糕，事实上，即便是在键盘上乱敲也比它来的好看。相信我，无数的猴子在 GNU emacs 上乱敲是不会做出好的程序的。

因此，你可以选择直接把 GNU emacs 给删了，或者修一修它，让它恢复正常。如果你选择了后者，那么请把下面的东西拷贝到你的 .emacs 文件中：

    
    (defun c-lineup-arglist-tabs-only (ignored)
        "Line up argument lists by tabs, not spaces"
        (let* ((anchor (c-langelem-pos c-syntactic-element))
            (column (c-langelem-2nd-pos c-syntactic-element))
            (offset (- (1+ column) anchor))
            (steps (floor offset c-basic-offset)))
        (* (max steps 1)
            c-basic-offset)))
    (add-hook 'c-mode-common-hook
                (lambda ()
                ;; Add kernel style
                (c-add-style
                "linux-tabs-only"
                '("linux" (c-offsets-alist
                            (arglist-cont-nonempty
                            c-lineup-gcc-asm-reg
                            c-lineup-arglist-tabs-only))))))
    (add-hook 'c-mode-hook
                (lambda ()
                (let ((filename (buffer-file-name)))
                    ;; Enable kernel mode for the appropriate files
                    (when (and filename
                            (string-match (expand-file-name "~/src/linux-trees")
                                            filename))
                    (setq indent-tabs-mode t)
                    (setq show-trailing-whitespace t)
                    (c-set-style "linux-tabs-only")))))


这会让你的 emacs 更好地满足内核的代码风格。


但是即使你不能让你的 emacs 恢复正常，也有解救方法：使用 indent 。

同样的问题出现了，GNU indent 和 GNU emacs 有同样的问题，因此你需要一些命令行选项来进行配置。但是事情也没那么糟，因为 GNU
indent 的制造者承认 K&R 的权威性，所以你只需要添加命令行参数 -kr -i8 (表示 K&R，8个字符宽的缩进)，或者使用 scripts/Lindent 也可以。

indent 有很多命令行选项，特别是注释的格式化方面，你可以通过 man 帮助页面来查看，不过请记住：indent 不是用来修复烂程序的。

注意：你也可以使用 clang-format 来完成这些格式化的工作，具体参见
https://www.kernel.org/doc/html/latest/process/clang-format.html#clangformat


####10 Kconfig 配置文件

对于 Linux 中的 Kconfig 配置文件，他们的缩进是有所不同的。在 config 定义下的缩进是一个 tab，而里面的 help 文本是两个空格，例如：


    
    config AUDIT
            bool "Auditing support"
            depends on NET
            help
            Enable auditing infrastructure that can be used with another
            kernel subsystem, such as SELinux (which requires this for
            logging of avc messages output).  Does not do system-call
            auditing without CONFIG_AUDITSYSCALL.


而对于有可能导致危险的动作(比如特定文件系统的写支持)，你应该在提示文本中直接指出：

    
    config ADFS_FS_RW
            bool "ADFS write support (DANGEROUS)"
            depends on ADFS_FS
            ...


具体细节参见 Documentation/kbuild/kconfig-language.txt


####11 数据结构


对于单线程环境里创建和销毁的一些数据结构，如果他们对于线程外是可见的，那么总是应该有引用计数。在内核里，垃圾收集器(GC)是不存在的，这意味着你必须对你使用过的数据进行引用计数。

进行引用计数意味着你可以避免死锁，允许多个用户并行访问数据，并且不用担心数据因为睡眠或者其他原因而找不到。

注意，锁不是引用计数的替代品。锁是为了保持数据的一致性，而引用计数是一种内存管理计数。通常这两种技术都是需要的，我们不要把他们搞混。

当有多个不同类的使用者时，很多数据结构会使用二级引用计数。第二级的引用计数会统计第二级使用者的数量，只有当第二级引用计数递减至零时，全局的第一级引用计数才会减一。

这种多级引用计数在内存管理`(struct mm_struct: mm_users and mm_count)`和文件系统`(struct super_block: s_count and s_active)`中都有使用。

记住，如果其他线程可以发现并使用你的数据结构，而你却没有引用计数，那么这基本就是一个 bug。

####12 宏、枚举与RTL(Real Time Linux)

常量宏和枚举的命名都是大写的。

    
    #define CONSTANT 0x12345


当定义一些有关联的常量时，使用枚举是一个很好的选择。

定义宏一般都使用大写，但是函数宏可以使用小写。

通常，我们更推荐把内联函数定义为宏。

包含多条语句的宏应该包含在一个 do-while 循环体中：

    
    #define macrofun(a, b, c)                       \
            do {                                    \
                    if (a == 5)                     \
                            do_this(b, c);          \
            } while (0)


使用宏时应该避免的情况：

1) 影响程序控制流的宏

    
    #define FOO(x)                                  \
            do {                                    \
                    if (blah(x) < 0)                \
                            return -EBUGGERED;      \
            } while (0)


这是一个非常坏的坏主意。它看起来像个函数，然而却会导致调用者返回到上一层。宏的设计不要打断程序的控制流。

2) 依赖局部变量的宏

    
    #define FOO(val) bar(index, val)


这看起来像个好东西，但其实糟透了，并且容易让人困扰。当其他人阅读这段代码时，他一个细微的改动可能导致严重的危害。

3) 带参数的宏当作左值

    
    FOO(x) = y;


如果有人把 FOO 变成内联函数，那么这段代码就错了。

4) 忘了优先级

    
    #define CONSTANT 0x4000
    #define CONSTEXP (CONSTANT | 3)


用宏来定义常量的时候，必须要括上括号，带有参数的宏也要注意。

5) 在定义宏函数时发生命名冲突

    
    #define FOO(x)                          \
    ({                                      \
            typeof(x) ret;                  \
            ret = calc_ret(x);              \
            (ret);                          \
    })


ret 是一个很容易和局部变量发生冲突的名字，而 `__foo_ret` 这样的名字则很少会发生冲突。

C++ 手册全面地阐述了宏定义的细节，gcc 手册同样也阐述了汇编语言使用的 RTL 规则，具体请自行查看。

####13 打印内核信息

内核开发者喜欢被视为有素养的，好的英文拼写和准确的内核信息能给人留下好的印象，因此，不要使用一些单词的缩写，比如 dont，而是 do not 或者don't。把提示信息写得尽可能准确、清晰、无二义。

内核信息不需要在末尾加上句号

在圆括号中打印数字(%d)没有任何意义，应该避免这样干。

在<linux/device.h>中有许多驱动模型的诊断宏，你应该使用这些宏来确保消息匹配正确的设备和驱动，并正确的标记它们的级别：`dev_err()`,`dev_warn()`, `dev_info()`, and so forth。对于没有关联特定设备的消息，<linux/printk.h>中定义了`pr_notice()`, `pr_info()`, `pr_warn()`, `pr_err()`, etc。

编写好的调试信息是一项巨大的挑战，一旦你完成了，这些信息会对远程调试产生巨大帮助。调试信息与普通信息不同，`pr_XXX()`函数在任何条件下都会进行打印，而 pr_debug() 却不是，这些与调试有关的函数默认都不会被编译，除非你定义了一个 DEBUG 宏或者`CONFIG_DYNAMIC_DEBUG `宏来显式地让编译器编译他们。还有一个惯例就是使用 `VERBOSE_DEBUG` 为那些已经开启 DEBUG 的用户添加 `dev_vdbg()` 消息。

很多子系统在对应的 makefile 里都有 Kconfig 调试选项来打开 -DDEBUG，或者是在文件里定义宏 #define DEBUG。当调试信息可以被无条件打印，或者说已经编译了和调试有关的 #ifdef 段，那么 `printk(KERN_DEBUG ...)` 就可以用来打印调试信息。

####14 分配内存#

内核提供了下面这些通用的内存分配器：kmalloc(), kzalloc(), kmalloc_array(), kcalloc(), vmalloc(), and vzalloc()。具体细节参见 API 文档。

为一个结构体分配内存的形式最好是这样的：

    
    p = kmalloc(sizeof(*p), ...);

另一种写出结构体名字的方式(sizeof(struct name))会破坏可读性并且给 bug 制造了机会：修改结构体名字却忘了修改对于的 sizeof 语句。

另外，在 malloc 之前添加上一个强制的类型转换，把空类型的指针转换为特定类型的指针，这些是多此一举的操作，他们应当交给编译器来干，而不是你。

分配一个数组的形式最好是这样的：

    
    p = kmalloc_array(n, sizeof(...), ...);


分配一个零数组的形式最好是这样的：

    
    p = kcalloc(n, sizeof(...), ...);


两种形式都会检查溢出，并且溢出发生时返回一个空指针 NULL。


####15 内联之灾

一个很常见的误解就是，人们认为 gcc 有一种让他们的程序跑得更快的魔法，就是内联。然而，内联往往也有不合适的用法(例如第十二节提到的替换宏)。inline 关键字的泛滥，会使内核变大，从而使整个系统运行速度变慢，因为大内核会占用更多的CPU高速缓存，同时会导致可用内存页缓存减少。想象一下，一次页缓存未命中就会导致一次磁盘寻址，这至少耗费5毫秒。5毫秒足够CPU运行很多很多的指令。

一个基本的原则就是，如果一个函数有3行以上的代码，就不要把它变成内联函数。有一个例外，若某个参数是一个编译时常数，且你确定因为这个常量，编译器在编译时能优化掉函数的大部分代码，那么加上 inline 关键字。kmalloc() 就是个很好的例子。

人们经常主张可以给只用一次的静态函数加上 inline 关键字，这样不会有任何损失。虽然从技术上来说这样没错，但是实际上 gcc 会自动内联这些函数。

####16 函数返回值与名称

函数可以返回不同种类的值，但是最普遍的就是表示运行成功或失败的值。这样的值可以用预先定义好的错误码表示(-Exxx = failure, 0 = success)，或者一个布尔值(0 = failure, non-zero = success)

混合两种方式会使代码变得复杂，并且很难找到bug。如果C语言能明确区分整型和布尔型，那么编译器会替我们发现这个问题……但是它不会那么做。为了避免这种问题，一定要谨记如下约定：

    
    如果函数名是一个短语，表示的是一个动作，或者一个命令，那么返回值应该使用错误码的方式。
    如果函数名是一句话，表示的是一个断言，那么应该使用布尔值的方式。


例如，add work 是一个动作，那么 `add_work()` 返回值为0则表示成功，-EBUSY表示失败。PCI device present是一个断言，那么 `pci_dev_present()` 返回值为1表示成功，0表示失败。

可导出(EXPORT)的函数都应该遵守这个约定，私有(static)函数不需要，不过我建议你还是遵守。

如果返回值是一些计算结果，那么当然不需要管这些东西。一般来说，计算结果出错了就表示失败了。典型的例子就是返回一个指针：使用 NULL 或者 `ERR_PTR` 来表示错误。

####17 不要重新发明内核宏

include/linux/kernel.h头文件里定义了一些你可以使用的宏，你应该直接使用他们，而不是重新再定义一些新的宏。例如，如果你需要计算数组长度，使用提供的宏：

    
    #define ARRAY_SIZE(x) (sizeof(x) / sizeof((x)[0]))


同样地，如果你需要计算结构体中某个成员的大小，使用：

    
    #define FIELD_SIZEOF(t, f) (sizeof(((t*)0)->f))


如果需要，里面还有做类型检查的 min() 和 max() 宏。仔细看看头文件中还定义了那些东西，如果里面有了，你就不要在自己的代码中重新定义了。

####18 多此一举的编辑器

有些编辑器可以识别源文件中的配置信息，例如 emacs 可以识别这样的标记：

    
    -*- mode: c -*-


或者这样的：

    
    /*
    Local Variables:
    compile-command: "gcc -DMAGIC_DEBUG_FLAG foo.c"
    End:
    */


Vim 可以识别：

    
    /* vim:set sw=8 noet */


不要在源代码中包含任何类似的内容。每个人都有自己的编辑器配置，你的源文件不应该影响他们。

####19 内联汇编

在写一些与体系结构有关的代码中，你可能需要使用一些内联汇编调用CPU相关的接口或者和平台有关的功能，如果有这种需求，你大可使用汇编。但是如果C语言可以干的事，不要使用汇编。你应该尽可能地使用C语言来控制硬件。

尽可能写一些辅助函数来实现相同的功能，而不是重复地写一些相同的代码，同时记住，内联汇编也可以使用C函数的参数。

大的、重要的汇编函数应该独自写在一个 .S 文件中，并且编写对应的C头文件和函数原型，相应的函数原型应该添加 asmlinkage 关键字。

你也许需要标记某些汇编代码为 volatile，避免 gcc 误把一些汇编移除掉。一般情况下，你不需要这样干，没必要的标记会影响优化。

当一条汇编语句里包含多个指令时，每个指令分行写，并且除了最后一行外，在其他行的行末添加 \n\t 进行缩进和对齐：

    
    asm ("magic %reg1, #42\n\t"
        "more_magic %reg2, %reg3"
        : /* outputs */ : /* inputs */ : /* clobbers */);


####20 条件编译

无论在哪，不要在 .c 文件中使用条件编译命令(#if, #ifdef)，这样干会导致代码可读性降低并且代码逻辑混乱。取而代之，应该在 .c 文件对应的头文件中使用这些条件编译，并且在每个 #else  分支注明对应的版本信息。

把同一个版本的所有函数都写在一个 #ifdef 中，不要在其中写一部分，而又在外部写一部分。

在 #endif 之后写上一个注释，注明这个 #ifdef 块对应的内容：

    
    #ifdef CONFIG_SOMETHING
    ...
    #endif /* CONFIG_SOMETHING */


####References

The C Programming Language, Second Edition by Brian W. Kernighan and Dennis M. Ritchie. Prentice Hall, Inc., 1988. ISBN 0-13-110362-8 (paperback), 0-13-110370-9 (hardback).  
The Practice of Programming by Brian W. Kernighan and Rob Pike. Addison-Wesley, Inc., 1999. ISBN 0-201-61586-X.  
GNU manuals - where in compliance with K&R and this text - for cpp, gcc, gcc internals and indent, all available from http://www.gnu.org/manual/  
WG14 is the international standardization working group for the programming language C, URL: http://www.open-std.org/JTC1/SC22/WG14/  
Kernel process/coding-style.rst, by greg@kroah.com at OLS 2002:http://www.kroah.com/linux/talks/ols_2002_kernel_codingstyle_talk/html/
