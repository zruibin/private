
<!--BEGIN_DATA
{
    "create_date": "2023-07-12 19:00", 
    "modify_date": "2023-07-12 19:00", 
    "is_top": "0", 
    "summary": "Bazel学习笔记", 
    "tags": "工具", 
    "file_name": "Bazel学习笔记.md"
}
END_DATA-->

#### <p>原文出处：<a href='https://blog.gmem.cc/bazel-study-note' target='blank'>Bazel学习笔记</a></p>

## 简介

Bazel是Google开源的，类似于Make、Maven或Gradle的构建和测试工具。它使用可读性强的、高层次的构建语言，支持多种编程语言，以及为多种平台进行交叉编译。

Bazel的优势：

  1. 高层次的构建语言：更加简单，Bazel抽象出库、二进制、脚本、数据集等概念，不需要编写调用编译器或链接器的脚本
  2. 快而可靠：能够缓存所有已经完成的工作步骤，并且跟踪文件内容、构建命令的变动情况，避免重复构建。此外Bazel还支持高度并行构建、增量构建
  3. 多平台支持：可以在Linux/macOS/Windows上运行，可以构建在桌面/服务器/移动设备上运行的应用程序
  4. 可扩容性：处理10万以上源码文件时仍然能保持速度
  5. 可扩展性：支持Android、C/C++、Java、Objective-C、Protocol Buffer、Python…还支持扩展以支持其它语言

## 如何工作

当运行构建或者测试时，Bazel会：

  1. 加载和目标相关的BUILD文件
  2. 分析输入及其依赖，应用指定的构建规则，产生一个Action图。这个图表示需要构建的目标、目标之间的关系，以及为了构建目标需要执行的动作。Bazel依据此图来跟踪文件变动，并确定哪些目标需要重新构建
  3. 针对输入执行构建动作，直到最终的构建输出产生出来

## 如何使用

当你需要构建或者测试一个项目时，通常执行以下步骤：

  1. 下载并安装Bazel
  2. 创建一个工作空间。Bazel从此工作空间寻找构建输入和BUILD文件，同时也将构建输出存放在（指向）工作空间（的符号链接中）
  3. 编写BUILD文件，以及可选的WORKSPACE文件，告知Bazel需要构建什么，如何构建。此文件基于Starlark这种DSL
  4. 从命令行调用Bazel命令，构建、测试或者运行项目

## 概念和术语

### Workspace

工作空间是一个目录，它包含：

  1. 构建目标所需要的源码文件，以及相应的BUILD文件
  2. 指向构建结果的符号链接
  3. WORKSPACE文件，可以为空，可以包含对外部依赖的引用

### Package

包是工作空间中主要的代码组织单元，其中包含一系列相关的文件（主要是代码）以及描述这些文件之间关系的BUILD文件

包是工作空间的子目录，它的根目录必须包含文件BUILD.bazel或BUILD。除了那些具有BUILD文件的子目录——子包——以外，其它子目录属于包的一部分

### Target

包是一个容器，它的元素定义在BUILD文件中，包括：

  1. 规则（Rule），指定输入集和输出集之间的关系，声明从输入产生输出的必要步骤。一个规则的输出可以是另外一个规则的输入
  2. 文件（File），可以分为两类： 
    1. 源文件
    2. 自动生成的文件（Derived files），由构建工具依据规则生成
  3. 包组：一组包，包组用于限制特定规则的可见性。包组由函数`package_group`定义，参数是包的列表和包组名称。你可以在规则的visibility属性中引用包组，声明那些包组可以引用当前包中的规则

任何包生成的文件都属于当前包，不能为其它包生成文件。但是可以从其它包中读取输入

### Label

引用一个目标时需要使用“标签”。标签的规范化表示： `@project//my/app/main:app_binary`，冒号前面是所属的包名，后面是目标名。如果不指定目标名，则默认以包路径最后一段作为目标名，例如：

```
//my/app
//my/app:app
```

这两者是等价的。在BUILD文件中，引用当前包中目标时，包名部分可以省略，因此下面四种写法都可以等价：


```
## 当前包为my/app
//my/app:app
//my/app
:app
app
```

在BUILD文件中，引用当前包中定义的规则时，冒号不能省略。引用当前包中文件时，冒号可以省略。 例如： generate.cc。

但是，从其它包引用时、从命令行引用时，都必须使用完整的标签： `//my/app:generate.cc`

`@project`这一部分通常不需要使用，引用外部存储库中的目标时，project填写外部存储库的名字。

### Rule

规则指定输入和输出之间的关系，并且说明产生输出的步骤。

规则有很多类型。每个规则都具有一个名称属性，此名称亦即目标名称。对于某些规则，此名称就是产生的输出的文件名。

在BUILD中声明规则的语法时：

```
规则类型(
  name = "...",
  其它属性 = ...
)
```

### BUILD文件

BUILD文件定义了包的所有元数据。其中的语句被从上而下的逐条解释，某些语句的顺序很重要， 例如变量必须先定义后使用，但是规则声明的顺序无所谓。

BUILD文件仅能包含ASCII字符，且不得声明函数、使用for/if语句，你可以在Bazel扩展——扩展名为`.bzl`的文件中声明函数、控制结构。并在BUILD文件中用load语句加载Bazel扩展：

```
load("//foo/bar:file.bzl", "some_library")
```

上面的语句加载`foo/bar/file.bzl`并添加其中定义的符号`some_libraray`到当前环境中，load语句可以用来加载规则、函数、常量（字符串、列表等）。

load语句必须出现在顶级作用域，不能出现在函数中。第一个参数说明扩展的位置，你可以为导入的符号设置别名。

规则的类型，一般以编程语言为前缀，例如cc，java，后缀通常有：

  1. `*_binary` 用于构建目标语言的可执行文件
  2. `*_test` 用于自动化测试，其目标是可执行文件，如果测试通过应该退出0
  3. `*_library` 用于构建目标语言的库 

### Dependency

目标A依赖B，就意味着A在构建或执行期间需要B。所有目标的依赖关系构成非环有向图（DAG）称为依赖图。

距离为1的依赖称为直接依赖，大于1的依赖则称为传递性依赖。

依赖分为以下几种：

  1. srcs依赖：直接被当前规则消费的文件
  2. deps依赖：独立编译的模块，为当前规则提供头文件、符号、库、数据
  3. data依赖：不属于源码，不影响目标如何构建，但是目标在运行时可能依赖之

## 安装

### Bazel

#### Ubuntu

参考下面的步骤安装Bazel：

```
echo "deb [arch=amd64] http://storage.googleapis.com/bazel-apt stable jdk1.8"
| sudo tee /etc/apt/sources.list.d/bazel.list
curl https://bazel.build/bazel-release.pub.gpg | sudo apt-key add -

sudo apt-get update && sudo apt-get install bazel
```

可以用如下命令升级到最新版本的Bazel：

```
sudo apt-get install \--only-upgrade bazel
```

### Bazelisk

这是基于Go语言编写的Bazel启动器，它会为你的工作区下载最适合的Bazel，并且透明的将命令转发给该Bazel。

由于Bazellisk提供了和Bazel一样的接口，因此通常直接将其命名为bazel：

```
sudo wget -O /usr/local/bin/bazel https://github.com/bazelbuild/bazelisk/releases/download/v0.0.8/bazelisk-linux-amd64

sudo chmod +x /usr/local/bin/bazel
```

## 入门

### 构建C++项目

#### 示例项目

执行下面的命令下载示例项目：

Shell

```
git clone https://github.com/bazelbuild/examples/
```

你可以看到stage1、stage2、stage3这几个WORKSPACE：

```
examples
└── cpp-tutorial
    ├──stage1
    │  ├── main
    │  │   ├── BUILD
    │  │   └── hello-world.cc
    │  └── WORKSPACE
    ├──stage2
    │  ├── main
    │  │   ├── BUILD
    │  │   ├── hello-world.cc
    │  │   ├── hello-greet.cc
    │  │   └── hello-greet.h
    │  └── WORKSPACE
    └──stage3
       ├── main
       │   ├── BUILD
       │   ├── hello-world.cc
       │   ├── hello-greet.cc
       │   └── hello-greet.h
       ├── lib
       │   ├── BUILD
       │   ├── hello-time.cc
       │   └── hello-time.h
       └── WORKSPACE
```

本节后续内容会依次使用到这三个WORKSPACE。

#### 通过Bazel构建

第一步是创建工作空间。工作空间中包含以下特殊文件：

  1. WORKSPACE，此文件位于根目录中，将当前目录定义为Bazel工作空间
  2. BUILD，告诉Bazel项目的不同部分如何构建。工作空间中包含BUILD文件的目录称为包

当Bazel构建项目时，所有的输入和依赖都必须位于工作空间中。除非被链接，不同工作空间的文件相互独立没有关系。

每个BUILD文件包含若干Bazel指令，其中最重要的指令类型是构建规则（Build Rule），构建规则说明如何产生期望的输出——例如可执行文件或库。BUILD中的每个构建规则也称为目标（Target），目标指向若干源文件和依赖，也可以指向其它目标。

下面是stage1的BUILD文件：

cpp-tutorial/stage1/main/BUILD

```
cc_binary(
    name = "hello-world",
    srcs = ["hello-world.cc"],
)
```

这里定义了一个名为hello-world的目标，它使用了内置的`cc_binary`规则。该规则告诉Bazel，从源码hello-world.cc构建一个自包含的可执行文件。

执行下面的命令可以触发构建：

```
#   //main: BUILD文件相对于工作空间的位置
#          hello-world 是BUILD文件中定义的目标
bazel build //main:hello-world
```

构建完成后，工作空间根目录会出现bazel-bin等目录，它们都是指向`$HOME/.cache/bazel`某个后代目录的符号链接。执行：

```
bazel-bin/main/hello-world
```

可以运行构建好的二进制文件。

#### 查看依赖图

Bazel会根据BUILD中的声明产生一张依赖图，并根据这个依赖图实现精确的增量构建。

要查看依赖图，先安装：

```
sudo apt install graphviz xdot
```

然后执行：

```
bazel query --nohost_deps --noimplicit_deps 'deps(//main:hello-world)' --output graph | xdot
```

指定多个目标

大型项目通常会划分为多个包、多个目标，以实现更快的增量构建、并行构建。工作空间stage2包含单个包、两个目标：

cpp-tutorial/stage2/main/BUILD

```
# 首先构建hello-greet库，cc_library是内建规则
cc_library(
    name = "hello-greet",
    srcs = ["hello-greet.cc"],
    # 头文件
    hdrs = ["hello-greet.h"],
)
 
# 然后构建hello-world二进制文件
cc_binary(
    name = "hello-world",
    srcs = ["hello-world.cc"],
    deps = [
        # 提示Bazel，需要hello-greet才能构建当前目标
        # 依赖当前包中的hello-greet目标
        ":hello-greet",
    ],
)
```

#### 使用多个包

工作空间stage3更进一步的划分出新的包，提供打印时间的功能：

cpp-tutorial/stage3/lib/BUILD

```
cc_library(
    name = "hello-time",
    srcs = ["hello-time.cc"],
    hdrs = ["hello-time.h"],
    # 让当前目标对于工作空间的main包可见。默认情况下目标仅仅被当前包可见
    visibility = ["//main:__pkg__"],
)
```

cpp-tutorial/stage3/main/BUILD

```
cc_library(
    name = "hello-greet",
    srcs = ["hello-greet.cc"],
    hdrs = ["hello-greet.h"],
)
 
cc_binary(
    name = "hello-world",
    srcs = ["hello-world.cc"],
    deps = [
        # 依赖当前包中的hello-greet目标
        ":hello-greet",
        # 依赖工作空间根目录下的lib包中的hello-time目标
        "//lib:hello-time",
    ],
)
```

#### 如何引用目标

在BUILD文件或者命令行中，你都使用标签（Label）来引用目标，其语法为：

```
//path/to/package:target-name
 
# 当引用当前包中的其它目标时，可以：
//:target-name
# 当引用当前BUILD文件中其它目标时，可以：
:target-name
```

## 目录布局

```
workspace-name>/                          # 工作空间根目录
  bazel-my-project => <...my-project>     # execRoot的符号链接，所有构建动作在此目录下执行
  bazel-out => <...bin>                   # outputPath的符号链接
  bazel-bin => <...bin>                   # 最近一次写入的二进制目录的符号链接，即$(BINDIR)
  bazel-genfiles => <...genfiles>         # 最近一次写入的genfiles目录的符号链接，即$(GENDIR)
 
 
 
/home/user/.cache/bazel/                  # outputRoot，所有工作空间的Bazel输出的根目录
  _bazel_$USER/                           # outputUserRoot，当前用户的Bazel输出的根目录
    install/
      fba9a2c87ee9589d72889caf082f1029/   # installBase，Bazel安装清单的哈希值
        _embedded_binaries/               # 第一次运行时从Bazel可执行文件的数据段解开的可执行文件或脚本
    7ffd56a6e4cb724ea575aba15733d113/     # outputBase，某个工作空间根目录的哈希值
      action_cache/                       # Action cache目录层次
      action_outs/                        # Action output目录
      command.log                         # 最近一次Bazel命令的stdout/stderr输出
      external/                           # 远程存储库被下载、链接到此目录
      server/                             # Bazel服务器将所有服务器有关的文件存放在此
        jvm.out                           # Bazel服务器的调试输出
      execroot/                           # 所有Bazel Action的工作目录
        <workspace-name>/                 # Bazel构建的工作树
          _bin/                           # 助手工具链接或者拷贝到此
          bazel-out/                      # outputPath，构建的实际输出目录
            local_linux-fastbuild/        # 每个独特的BuildConfiguration实例对应一个子目录
              bin/                        # 单个构建配置二进制输出目录，$(BINDIR)
                foo/bar/_objs/baz/        # 命名为//foo/bar:baz的cc_*规则的Object文件所在目录
                  foo/bar/baz1.o          # //foo/bar:baz1.cc对应的Object文件
                  other_package/other.o   # //other_package:other.cc对应的Object文件
                foo/bar/baz               # //foo/bar:baz这一cc_binary生成的构件
                foo/bar/baz.runfiles/     # //foo/bar:baz生成的二进制构件的runfiles目录
                  MANIFEST
                  <workspace-name>/
                    ...
              genfiles/                   # 单个构建配置生成的源文件目录，$(GENDIR)
              testlogs/                   # Bazel的内部测试运行器将日志文件存放在此
              include/                    # 按需生成的include符号链接树，符号链接bazel-include指向这里
            host/                         # 本机的BuildConfiguration
        <packages>/                       # 构建引用的包，对于此包来说，它就像一个正常的WORKSPACE 
```

## Starlark

Bazel配置文件使用Starlark（原先叫Skylark）语言，具有短小、简单、线程安全的特点。

这种语言的语法和Python很类似，Starlark是Python2/Python3的子集。不支持的Python特性包括：

<table>
<thead>
<tr>
<td style="text-align: center;">不支持的特性</td>
<td style="text-align: center;">说明</td>
</tr>
</thead>
<tbody>
<tr>
<td>隐含字符串连接</td>
<td>需要明确使用 + 操作符</td>
</tr>
<tr>
<td>链式比较操作符</td>
<td>例如：1 &lt; x &lt; 5</td>
</tr>
<tr>
<td>class</td>
<td>使用struct函数</td>
</tr>
<tr>
<td>import</td>
<td>使用load语句</td>
</tr>
<tr>
<td>is</td>
<td>使用==代替</td>
</tr>
<tr>
<td colspan="2">以下关键字：while、yield、try、raise、except、finally 、global、nonlocal</td>
</tr>
<tr>
<td colspan="2">以下数据类型：float、set</td>
</tr>
<tr>
<td colspan="2">生成器、生成器表达式</td>
</tr>
<tr>
<td colspan="2">lambda以及嵌套函数</td>
</tr>
<tr>
<td colspan="2">绝大多数内置函数、方法</td>
</tr>
</tbody>
</table>

### 数据类型

Starlark支持的数据类型包括：None、bool、dict、function、int、list、string，以及两种Bazel特有的类型：depset、struct。

### 代码示例

```python
# 定义一个数字
number = 18
 
# 定义一个字典
people = {
    "Alice": 22,
    "Bob": 40,
    "Charlie": 55,
    "Dave": 14,
}
 
names = ", ".join(people.keys())
 
# 定义一个函数
def greet(name):
  """Return a greeting."""
  return "Hello {}!".format(name)
# 调用函数
greeting = greet(names)
 
 
def fizz_buzz(n):
  """Print Fizz Buzz numbers from 1 to n."""
  # 循环结构
  for i in range(1, n + 1):
    s = ""
    # 分支结构
    if i % 3 == 0:
      s += "Fizz"
    if i % 5 == 0:
      s += "Buzz"
    print(s if s else i)
```

### 变量

你可以在BUILD文件中声明和使用变量。使用变量可以减少重复的代码：

```python
COPTS = ["-DVERSION=5"]
 
cc_library(
  name = "foo",
  copts = COPTS,
  srcs = ["foo.cc"],
)
 
cc_library(
  name = "bar",
  copts = COPTS,
  srcs = ["bar.cc"],
  deps = [":foo"],
)
```

### 跨BUILD变量

如果要声明跨越多个BUILD文件共享的变量，必须把变量放入.bzl文件中，然后通过load加载bzl文件。

### Make变量

所谓Make变量，是一类特殊的、可展开的字符串变量，这种变量类似Shell中变量替换那样的展开。

Bazel提供了：

  1. 预定义变量，可以在任何规则中使用
  2. 自定义变量，在规则中定义。仅仅在依赖该规则的那些规则中，可以使用这些变量

#### 使用Make变量

仅仅那些标记为Subject to 'Make variable' substitution的规则属性，才可以使用Make变量。例如：

```
# 使用Make变量FOO
my_attr = "prefix $(FOO) suffix"
# 如果变量FOO的值为bar，则实际my_attr的值为prefix bar suffix
```

## 如果变量FOO的值为bar，则实际my_attr的值为prefix bar suffix

如果要使用`$`字符，需要用`$$`代替。

#### 一般预定义变量

执行命令： `bazel info --show_make_env [build options]`可以查看所有预定义变量的列表。

任何规则可以使用以下变量：

<table>
<thead>
<tr>
<td style="width: 180px; text-align: center;">变量</td>
<td style="text-align: center;">说明</td>
</tr>
</thead>
<tbody>
<tr>
<td>COMPILATION_MODE</td>
<td>编译模式：fastbuild、dbg、opt</td>
</tr>
<tr>
<td>BINDIR</td>
<td>目标体系结构的二进制树的根目录</td>
</tr>
<tr>
<td>GENDIR</td>
<td>目标体系结构的生成代码树的根目录</td>
</tr>
<tr>
<td>TARGET_CPU</td>
<td>目标体系结构的CPU</td>
</tr>
</tbody>
</table>

#### genrule预定义变量

下表中的变量可以在genrule规则的cmd属性中使用：

<table class="full-width fixed-word-wrap">
<thead>
<tr>
<td style="width: 180px; text-align: center;">变量</td>
<td style="text-align: center;">说明</td>
</tr>
</thead>
<tbody>
<tr>
<td>OUTS</td>
<td>genrule的outs列表，如果只有一个输出文件，可以用
      <span id="crayon-64af88248811f971931131" class="crayon-syntax crayon-syntax-inline  crayon-theme-gmem-github crayon-theme-gmem-github-inline crayon-font-consolas" style="font-size: 15px !important; line-height: 20px !important;font-size: 15px !important;"><span class="crayon-pre crayon-code" style="font-size: 15px !important; line-height: 20px !important;font-size: 15px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;"><span class="crayon-sy">$</span><span class="crayon-sy">@</span></span></span></td>
</tr>
<tr>
<td>SRCS</td>
<td>genrule的srcs列表，如果只有一个输入文件，可以用
      <span id="crayon-64af882488122443771536" class="crayon-syntax crayon-syntax-inline  crayon-theme-gmem-github crayon-theme-gmem-github-inline crayon-font-consolas" style="font-size: 15px !important; line-height: 20px !important;font-size: 15px !important;"><span class="crayon-pre crayon-code" style="font-size: 15px !important; line-height: 20px !important;font-size: 15px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;"><span class="crayon-sy">$</span><span class="crayon-o">&lt;</span></span></span></td>
</tr>
<tr>
<td>@D</td>
<td>
<p>输出目录，如果：</p>
<ol>
<li>outs仅仅包含一个文件名，则展开为包含该文件的目录</li>
<li>outs包含多个文件，则此变量展开为在genfiles树中，当前包的根目录</li>
</ol>
</td>
</tr>
</tbody>
</table>

#### 输入输出路径变量

下表中的变量以Bazel的Label为参数，获取包的某类输入/输出路径：

<table class="full-width fixed-word-wrap">
<thead>
<tr>
<td style="width: 180px; text-align: center;">变量</td>
<td style="text-align: center;">说明</td>
</tr>
</thead>
<tbody>
<tr>
<td>execpath</td>
<td rowspan="2">
<p>获取指定标签对应的规则（此规则必须仅仅输出单个文件）或文件（必须是单个文件），位于execroot下的对应路径</p>
<p>对于项目myproject，<span style="background-color: #c0c0c0;">所有构建动作</span>在工作空间根目录下的符号链接bazel-myproject对应的目录下执行，此目录即execroot。源码empty.source被链接到bazel-myproject/testapp/empty.source，因此其execpath为testapp/empty.source</p>
<p>对于目标：</p>
      <div>
        <table class="crayon-table" style="">
          <tbody>
            <td class="crayon-code"><div class="crayon-pre" style="font-size: 15px !important; line-height: 20px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;"><div class="crayon-line" id="crayon-64af882488124327035788-1"><span class="crayon-e">cc_binary</span><span class="crayon-sy">(</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af882488124327035788-2"><span class="crayon-h">&nbsp;&nbsp;</span><span class="crayon-v">name</span><span class="crayon-h"> </span><span class="crayon-o">=</span><span class="crayon-h"> </span><span class="crayon-s">"app"</span><span class="crayon-sy">,</span></div><div class="crayon-line" id="crayon-64af882488124327035788-3"><span class="crayon-h">&nbsp;&nbsp;</span><span class="crayon-v">srcs</span><span class="crayon-h"> </span><span class="crayon-o">=</span><span class="crayon-h"> </span><span class="crayon-sy">[</span><span class="crayon-s">"app.cc"</span><span class="crayon-sy">]</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af882488124327035788-4"><span class="crayon-sy">)</span></div></div></td>
          </tr>
        </tbody></table>
      </div>
<p>执行构建：
      <span id="crayon-64af882488126154689972" class="crayon-syntax crayon-syntax-inline  crayon-theme-gmem-github crayon-theme-gmem-github-inline crayon-font-consolas" style="font-size: 15px !important; line-height: 20px !important;font-size: 15px !important;"><span class="crayon-pre crayon-code" style="font-size: 15px !important; line-height: 20px !important;font-size: 15px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;"><span class="crayon-e">bazel </span><span class="crayon-v">build</span><span class="crayon-h"> </span><span class="crayon-c">//testapp:app</span></span></span>时：&nbsp;</p>
      <div>
        <table class="crayon-table" style="">
          <tbody><tr class="crayon-row">
            <td class="crayon-code"><div class="crayon-pre" style="font-size: 15px !important; line-height: 20px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;"><div class="crayon-line" id="crayon-64af882488128577208850-1"><span class="crayon-sy">$</span><span class="crayon-sy">(</span><span class="crayon-v">execpath</span><span class="crayon-h"> </span><span class="crayon-o">:</span><span class="crayon-v">app</span><span class="crayon-sy">)</span><span class="crayon-h">&nbsp;&nbsp;</span><span class="crayon-c"># bazel-out/host/bin/testapp/app</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af882488128577208850-2"><span class="crayon-sy">$</span><span class="crayon-sy">(</span><span class="crayon-e">execpath </span><span class="crayon-v">empty</span><span class="crayon-e">.source</span><span class="crayon-sy">)</span><span class="crayon-h"> </span><span class="crayon-c"># testapp/empty.source&nbsp;</span></div></div></td>
          </tr>
        </tbody></table>
      </div>
</td>
</tr>
<tr>
<td>execpaths</td>
</tr>
<tr>
<td>rootpath</td>
<td rowspan="2">
<p>获取runfiles路径，二进制文件通过此路径在运行时寻找其依赖
</p><p>对于上面的//testapp:app目标：</p>
    <div >
        <table class="crayon-table" style="">
          <tbody><tr class="crayon-row">
            <td class="crayon-code"><div class="crayon-pre" style="font-size: 15px !important; line-height: 20px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;"><div class="crayon-line" id="crayon-64af88248812a429539185-1"><span class="crayon-sy">$</span><span class="crayon-sy">(</span><span class="crayon-v">rootpath</span><span class="crayon-h"> </span><span class="crayon-o">:</span><span class="crayon-v">app</span><span class="crayon-sy">)</span><span class="crayon-h">&nbsp;&nbsp;</span><span class="crayon-c"># testapp/app</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af88248812a429539185-2"><span class="crayon-sy">$</span><span class="crayon-sy">(</span><span class="crayon-e">rootpath </span><span class="crayon-v">empty</span><span class="crayon-e">.source</span><span class="crayon-sy">)</span><span class="crayon-h">&nbsp;&nbsp;</span><span class="crayon-c"># testapp/empty.source&nbsp;</span></div></div></td>
          </tr>
        </tbody></table>
      </div>
</td>
</tr>
<tr>
<td>rootpaths</td>
</tr>
<tr>
<td>location</td>
<td rowspan="2">
<p>根据当前所声明的属性，等价于execpath或rootpath
</p><p>对于上面的//testapp:app目标：</p>
    <div>
        <table class="crayon-table" style="">
          <tbody><tr class="crayon-row">
            <td class="crayon-code"><div class="crayon-pre" style="font-size: 15px !important; line-height: 20px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;"><div class="crayon-line" id="crayon-64af88248812c111896519-1"><span class="crayon-sy">$</span><span class="crayon-sy">(</span><span class="crayon-v">location</span><span class="crayon-h"> </span><span class="crayon-o">:</span><span class="crayon-v">app</span><span class="crayon-sy">)</span><span class="crayon-h"> </span><span class="crayon-c"># bazel-out/host/bin/testapp/app</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af88248812c111896519-2"><span class="crayon-sy">$</span><span class="crayon-sy">(</span><span class="crayon-e">location </span><span class="crayon-v">empty</span><span class="crayon-e">.source</span><span class="crayon-sy">)</span><span class="crayon-h"> </span><span class="crayon-c"># testapp/empty.source&nbsp;</span></div></div></td>
          </tr>
        </tbody></table>
    </div>

</td>
</tr>
<tr>
<td>locations</td>
</tr>
</tbody>
</table>

## 一般规则

### 规则列表

#### filegroup

为一组目标指定一个名字，你可以从其它规则中方便的引用这组目标。

Bazel鼓励使用filegroup，而不是直接引用目录。Bazel构建系统不能完全了解目录中文件的变化情况，因而文件发生变化时，可能不会进行重新构建。而使用filegroup，即使联用glob，目录中所有文件仍然能够被构建系统正确的监控。

示例：

```
filegroup(
    name = "exported_testdata",
    srcs = glob([
        "testdata/*.dat",
        "testdata/logs/**/*.log",
    ]),
)
```

要引用filegroup，只需要使用标签：

```
cc_library(
    name = "my_library",
    srcs = ["foo.cc"],
    data = [
        "//my_package:exported_testdata",
        "//my_package:mygroup",
    ],
)
```

#### test_suite

定义一组测试用例，给出一个有意义的名称，便于在特定时机 —— 例如迁入代码、执行压力测试 —— 时执行这些测试用例。

示例：

```
# 匹配当前包中所有small测试
test_suite(
    name = "small_tests",
    tags = ["small"],
)
# 匹配不包含flaky标记的测试
test_suite(
    name = "non_flaky_test",
    tags = ["-flaky"],
)
# 指定测试列表
test_suite(
    name = "smoke_tests",
    tests = [
        "system_unittest",
        "public_api_unittest",
    ],
)
```

#### alias

为规则设置一个别名：

```
filegroup(
    name = "data",
    srcs = ["data.txt"],
)

# 定义别名
alias(
    name = "other",
    actual = ":data",
)
```

#### config_setting

通过匹配以Bazel标记或平台约束来表达的“配置状态”，`config_setting`能够触发可配置的属性。

下面这个例子，匹配针对ARM平台的构建：

```
config_setting(
    name = "arm_build",
    values = {"cpu": "arm"},
)
```

下面的例子，匹配任何定义了宏FOO=bar的针对X86平台的调试（-c dbg）构建：

```
config_setting(
    name = "x86_debug_build",
    values = {
        "cpu": "x86",
        "compilation_mode": "dbg",
        "define": "FOO=bar"
    },
)
```

下面的库，通过select来声明可配置属性：

```
cc_binary(
    name = "mybinary",
    srcs = ["main.cc"],
    deps = select({
        # 如果config_settings arm_build匹配正在进行的构建，则依赖arm_lib这个目标
        ":arm_build": [":arm_lib"],
        # 如果config_settings x86_debug_build匹配正在进行的构建，则依赖x86_devdbg_lib
        ":x86_debug_build": [":x86_devdbg_lib"],
        # 默认情况下，依赖generic_lib
        "//conditions:default": [":generic_lib"],
    }),
)
```

#### genrule

一般性的规则 —— 使用用户指定的Bash命令，生成一个或多个文件。使用genrule理论上可以实现任何构建行为，例如压缩JavaScript代码。但是在执行C++、Java等构建任务时，最好使用相应的专用规则，更加简单。

不要使用genrule来运行测试，如果需要一般性的测试规则，可以考虑使用sh_test。

genrule在一个Bash shell环境下执行，当任意一个命令或管道失败（set -e -o pipefail），整个规则就失败。你不应该在genrule中访问网络。

示例：

```
genrule(
    name = "foo",
    # 不需要输入
    srcs = [],
    # 生成一个foo.h
    outs = ["foo.h"],
    # 运行当前规则所在包下的一个Perl脚本
    cmd = "./$(location create_foo.pl) > \"$@\"",
    tools = ["create_foo.pl"],
) 
```

## C++规则

### 规则列表

#### cc_binary

隐含输出：

  1. name.stripped，仅仅当显式要求才会构建此输出，针对生成的二进制文件运行strip -g以驱除debug符号。额外的strip选项可以通过命令行--stripopt=-foo传入
  2. name.dwp，仅仅当显式要求才会构建此输出，如果启用了 Fission ，则此文件包含用于远程调试的调试信息，否则是空文件

属性列表：

<table>
<thead>
<tr>
<td style="width: 15%; text-align: center;">属性</td>
<td style="text-align: center;">说明</td>
</tr>
</thead>
<tbody>
<tr>
<td>name</td>
<td>目标的名称</td>
</tr>
<tr>
<td>deps</td>
<td>
<p>需要链接到此二进制目标的其它库的列表，以Label引用</p>
<p>这些库可以是cc_library或objc_library定义的目标</p>
</td>
</tr>
<tr>
<td>srcs</td>
<td>
<p>C/C++源文件列表，以Label引用</p>
<p>这些文件是C/C++源码文件或头文件，可以是自动生成的或人工编写的。</p>
<p>所有cc/c/cpp文件都会被编译。<span style="background-color: #c0c0c0;">如果某个声明的文件在其它规则的outs列表中，则当前规则自动依赖于那个规则</span></p>
<p>所有.h文件都不会被编译，仅仅供源码文件包含之。所有.h/.cc等文件都可以包含<span style="background-color: #c0c0c0;">srcs中声明的</span>、<span style="background-color: #c0c0c0;">deps中声明的目标的hdrs中声明</span>的头文件。也就是说，任何#include的文件要么在此属性中声明，要么在依赖的cc_library的hdrs属性中声明</p>
<p>如果某个规则的名称出现在srcs列表中，则当前规则自动依赖于那个规则：</p>
<ol>
<li>如果那个规则的输出是C/C++源文件，则它们被编译进当前目标</li>
<li>如果那个规则的输出是库文件，则被链接到当前目标</li>
</ol>
<p>允许的文件类型：</p>
<ol>
<li>C/C++源码，扩展名.c, .cc, .cpp, .cxx, .c++, .C</li>
<li>C/C++头文件，扩展名.h, .hh, .hpp, .hxx, .inc</li>
<li>汇编代码，扩展名.S</li>
<li>归档文件，扩展名.a, .pic.a</li>
<li>共享库，扩展名.so, .so.version，version为soname版本号</li>
<li>对象文件，扩展名.o, .pic.o</li>
<li>任何能够产生上述文件的规则</li>
</ol>
</td>
</tr>
<tr>
<td>copts</td>
<td>
<p>字符串列表</p>
<p>为C++编译器提供的选项，在编译目标之前，这些选项按顺序添加到COPTS。这些选项仅仅影响当前目标的编译，而<span style="background-color: #c0c0c0;">不影响其依赖</span>。选项中的任何路径都<span style="background-color: #c0c0c0;">相对于当前工作空间而非当前包</span></p>
<p>也可以在bazel build时通过--copts选项传入，例如：</p>
    <div>
        <table class="crayon-table" style="">
          <tbody><tr class="crayon-row">
            <td class="crayon-code"><div class="crayon-pre" style="font-size: 15px !important; line-height: 20px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;"><div class="crayon-line" id="crayon-64af882488141302082933-1"><span class="crayon-o">--</span><span class="crayon-i">copt</span><span class="crayon-h"> </span><span class="crayon-s">"-DENVOY_IGNORE_GLIBCXX_USE_CXX11_ABI_ERROR=1"</span>&nbsp;</div></div></td>
          </tr>
        </tbody></table>
    </div>
</td>
</tr>
<tr>
<td>defines</td>
<td>
<p>字符串列表
</p><p>为C++编译器传递宏定义，实际上会前缀以-D并添加到COPTS。与copts属性不同，这些宏定义会添加到当前目标，以及<span style="background-color: #c0c0c0;">所有依赖它的目标</span></p>
</td>
</tr>
<tr>
<td>includes</td>
<td>
<p>字符串列表</p>
<p>为C++编译器传递的头文件包含目录，实际上会前缀以-isystem并添加到COPTS。与copts属性不同，这些头文件包含会影响当前目标，以及<span style="background-color: #c0c0c0;">所有依赖它的目标</span></p>
<p>如果不清楚有何副作用，可以<span style="background-color: #c0c0c0;">传递-I到copts</span>，而不是使用当前属性</p>
</td>
</tr>
<tr>
<td>linkopts&nbsp;</td>
<td>
<p>字符串列表</p>
<p>为C++链接器传递选项，在链接二进制文件之前，此属性中的每个字符串被添加到LINKOPTS</p>
<p>此属性列表中，任何不以$和-开头的项，都被认为是deps中声明的<span style="background-color: #c0c0c0;">某个目标的Label，目标产生的文件会添加到链接选项</span>中</p>
</td>
</tr>
<tr>
<td>linkshared</td>
<td>
<p>布尔，默认False。用于创建共享库</p>
<p>要创建共享库，指定属性linkshared = True，对于GCC来说，会添加选项-shared。生成的结果适合被Java这类应用程序加载</p>
<p>需要注意，这里创建的共享库<span style="background-color: #c0c0c0;">绝不会被链接到依赖它的二进制文件</span>，而只适用于被其它程序手工的加载。因此，不能代替cc_library</p>
<p>如果同时指定
      <span id="crayon-64af882488144500631184" class="crayon-syntax crayon-syntax-inline  crayon-theme-gmem-github crayon-theme-gmem-github-inline crayon-font-consolas" style="font-size: 15px !important; line-height: 20px !important;font-size: 15px !important;"><span class="crayon-pre crayon-code" style="font-size: 15px !important; line-height: 20px !important;font-size: 15px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;"><span class="crayon-v">linkopts</span><span class="crayon-o">=</span><span class="crayon-sy">[</span><span class="crayon-s">'-static'</span><span class="crayon-sy">]</span></span></span>和linkshared=True，你会得到一个完全自包含的单元。如果同时指定linkstatic=True和linkshared=True会得到一个基本是完全自包含的单元</p>
</td>
</tr>
<tr>
<td>linkstatic</td>
<td>
<p>布尔，默认True</p>
<p>对于cc_binary和cc_test，以静态形式链接二进制文件。对于cc_binary此选项默认True，其它目标默认False</p>
<p>如果当前目标是binary或test，此选项提示构建工具，<span style="background-color: #c0c0c0;">尽可能链接到用户库的.a版本而非.so</span>版本。某些系统库可能仍然需要动态链接，原因是没有静态库，这导致最终的输出仍然使用动态链接，不是完全静态的</p>
<p>链接一个可执行文件时，实际上有三种方式：</p>
<ol>
<li>STATIC，使用完全静态链接特性。所有依赖都被静态链接，GCC命令示例：<br>
    <div>
        <table class="crayon-table" style="">
          <tbody><tr class="crayon-row">
            <td class="crayon-code"><div class="crayon-pre" style="font-size: 15px !important; line-height: 20px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;"><div class="crayon-line" id="crayon-64af882488146829929649-1"><span class="crayon-v">gcc</span><span class="crayon-h"> </span><span class="crayon-o">-</span><span class="crayon-e">static </span><span class="crayon-v">foo</span><span class="crayon-e">.o</span><span class="crayon-h"> </span><span class="crayon-v">libbar</span><span class="crayon-e">.a</span><span class="crayon-h"> </span><span class="crayon-v">libbaz</span><span class="crayon-e">.a</span><span class="crayon-h"> </span><span class="crayon-o">-</span><span class="crayon-v">lm</span></div></div></td>
          </tr>
        </tbody></table>
    </div>
</li>
<li>STATIC，所有用户库静态链接（如果存在静态库版本），但是系统库（除去C/C++运行时库）动态链接，GCC命令示例：<br>
    <div>
        <table class="crayon-table" style="">
          <tbody><tr class="crayon-row">
            <td class="crayon-code"><div class="crayon-pre" style="font-size: 15px !important; line-height: 20px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;"><div class="crayon-line" id="crayon-64af882488148730987593-1"><span class="crayon-c"># 此方式可以由linkstatic=True 启用</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af882488148730987593-2"><span class="crayon-e">gcc </span><span class="crayon-v">foo</span><span class="crayon-e">.o</span><span class="crayon-h"> </span><span class="crayon-v">libfoo</span><span class="crayon-e">.a</span><span class="crayon-h"> </span><span class="crayon-v">libbaz</span><span class="crayon-e">.a</span><span class="crayon-h"> </span><span class="crayon-o">-</span><span class="crayon-i">lm</span>&nbsp;</div></div></td>
          </tr>
        </tbody></table>
    </div>
</li>
<li>DYNAMIC，所有依赖被动态链接（如果存在动态库版本），GCC命令示例：<br>
    <div>
        <table class="crayon-table" style="">
          <tbody><tr class="crayon-row">
            <td class="crayon-code"><div class="crayon-pre" style="font-size: 15px !important; line-height: 20px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;"><div class="crayon-line" id="crayon-64af88248814a691260547-1"><span class="crayon-c"># 此方式可以由linkstatic=False 启用</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af88248814a691260547-2"><span class="crayon-e">gcc </span><span class="crayon-v">foo</span><span class="crayon-e">.o</span><span class="crayon-h"> </span><span class="crayon-v">libfoo</span><span class="crayon-e">.so</span><span class="crayon-h"> </span><span class="crayon-v">libbaz</span><span class="crayon-e">.so</span><span class="crayon-h"> </span><span class="crayon-o">-</span><span class="crayon-i">lm</span>&nbsp;</div></div></td>
          </tr>
        </tbody></table>
    </div>
</li>
</ol>
<p>对于cc_library来说，linkstatic属性的含义不同。对于C++库来说：</p>
<ol>
<li>linkstatic=True表示仅仅允许静态链接，也就是不产生.so文件</li>
<li>linkstatic=False表示允许动态链接，同时产生.a和.so文件</li>
</ol>
</td>
</tr>
<tr>
<td>malloc&nbsp;</td>
<td>
<p>指向标签，默认@bazel_tools//tools/cpp:malloc</p>
<p>覆盖默认的malloc依赖，默认情况下C++二进制文件链接到//tools/cpp:malloc，这是一个空库，这导致实际上链接到libc的malloc</p>
</td>
</tr>
<tr>
<td>nocopts</td>
<td>
<p>字符串</p>
<p>从C++编译命令中移除匹配的选项，此属性的值是正则式，任何匹配正则式的、已经存在的COPTS被移除&nbsp;</p>
</td>
</tr>
<tr>
<td>stamp&nbsp;</td>
<td>
<p>整数，默认-1</p>
<p>用于将构建信息嵌入到二进制文件中，可选值：</p>
<ol>
<li>stamp = 1，将构建信息嵌入，目标二进制仅仅在其依赖变化时重新构建</li>
<li>stamp = 0，总是将构建信息替换为常量值，有利于构建结果缓存</li>
<li>stamp = -1 ，由--[no]stamp标记控制是否嵌入</li>
</ol>
</td>
</tr>
<tr>
<td>toolchains&nbsp;</td>
<td>
<p>标签列表</p>
<p>提供构建变量（Make variables，这些变量可以被当前目标使用）的工具链的标签列表&nbsp;</p>
</td>
</tr>
<tr>
<td>win_def_file</td>
<td>
<p>标签</p>
<p>传递给链接器的Windows DEF文件。在Windows上，此属性可以在链接共享库时导出符号&nbsp;</p>
</td>
</tr>
</tbody>
</table>

#### cc_import

导入预编译好的C/C++库。

属性列表：

<table>
<thead>
<tr>
<td style="width: 15%; text-align: center;">属性</td>
<td style="text-align: center;">说明</td>
</tr>
</thead>
<tbody>
<tr>
<td>hdrs</td>
<td>此预编译库对外发布的头文件列表，依赖此库的规则（dependent rule）会直接将这些头文件包含在源码列表中</td>
</tr>
<tr>
<td>alwayslink</td>
<td>
<p>布尔，默认False</p>
<p>如果为True，则依赖此库的二进制文件会将此静态库归档中的对象文件链接进去，就算某些对象文件中的符号并没有被二进制文件使用</p>
</td>
</tr>
<tr>
<td>interface_library</td>
<td>用于链接共享库时使用的接口（导入）库</td>
</tr>
<tr>
<td>shared_library</td>
<td>共享库，Bazel保证在运行时可以访问到共享库</td>
</tr>
<tr>
<td>static_library</td>
<td>静态库</td>
</tr>
<tr>
<td>system_provided</td>
<td>提示运行时所需的共享库由操作系统提供，如果为True则应该指定interface_library，shared_library应该为空</td>
</tr>
</tbody>
</table>

#### cc_library

对于所有`cc_*`规则来说，构建所需的任何头文件都要在hdrs或srcs中声明。

对于`cc_library`规则，在hdrs声明的头文件构成库的公共接口。这些头文件可以被当前库的`hdrs/srcs`中的文件直接包含，也可以被依赖（deps）当前库的其它`cc_*`的`hdrs/srcs`直接包含。位于srcs中的头文件，则仅仅能被当前库的hdrs/srcs包含。

`cc_binary`和`cc_test`不会暴露接口，因此它们没有hdrs属性。

属性列表：

<table class="full-width fixed-word-wrap">
<thead>
<tr>
<td style="width: 15%; text-align: center;">属性</td>
<td style="text-align: center;">说明</td>
</tr>
</thead>
<tbody>
<tr>
<td>name</td>
<td>库的名称</td>
</tr>
<tr>
<td>deps</td>
<td>需要链接到（into）当前库的其它库</td>
</tr>
<tr>
<td>srcs</td>
<td>头文件和源码列表</td>
</tr>
<tr>
<td>hdrs</td>
<td>导出的头文件列表</td>
</tr>
<tr>
<td>copts/nocopts</td>
<td>传递给C++编译命令的参数</td>
</tr>
<tr>
<td>defines</td>
<td>宏定义列表</td>
</tr>
<tr>
<td>include_prefix</td>
<td>hdrs中头文件的路径前缀</td>
</tr>
<tr>
<td>includes</td>
<td>
<p>字符串列表</p>
<p>需要添加到编译命令的包含文件列表</p>
</td>
</tr>
<tr>
<td>linkopts</td>
<td>链接选项</td>
</tr>
<tr>
<td>linkstatic</td>
<td>是否生成动态库</td>
</tr>
<tr>
<td>strip_include_prefix</td>
<td>
<p>字符串</p>
<p>需要脱去的头文件路径前缀，也就是说使用hdrs中头文件时，要把这个前缀去除，路径才匹配</p>
</td>
</tr>
<tr>
<td>textual_hdrs</td>
<td>
<p>标签列表</p>
<p>头文件列表，这些头文件是不能独立编译的。依赖此库的目标，直接以文本形式包含这些头文件到它的源码列表中，这样才能正确编译这些头文件</p>
</td>
</tr>
</tbody>
</table>

### 常见用例

#### 通配符

可以使用Glob语法为目标添加多个文件：

```
cc_library(
    name = "build-all-the-files",
    srcs = glob(["*.cc"]),
    hdrs = glob(["*.h"]),
)
```

#### 传递性依赖

如果源码依赖于某个头文件，则该源码的规则需要dep头文件的库，仅仅直接依赖才需要声明：

```
# 三明治依赖面包
cc_library(
    name = "sandwich",
    srcs = ["sandwich.cc"],
    hdrs = ["sandwich.h"],
    # 声明当前包下的目标为依赖
    deps = [":bread"],
)
# 面包依赖于面粉，三明治间接依赖面粉，因此不需要声明
cc_library(
    name = "bread",
    srcs = ["bread.cc"],
    hdrs = ["bread.h"],
    deps = [":flour"],
)
 
cc_library(
    name = "flour",
    srcs = ["flour.cc"],
    hdrs = ["flour.h"],
)
```

#### 添加头文件路径

有些时候你不愿或不能将头文件放到工作空间的include目录下，现有的库的include目录可能不符合

#### 导入已编译库

导入一个库，用于静态链接：

```
cc_import(
  name = "mylib",
  hdrs = ["mylib.h"],
  static_library = "libmylib.a",
  # 如果为1则libmylib.a总会链接到依赖它的二进制文件
  alwayslink = 1,
)
```

导入一个库，用于共享链接（UNIX）：

```
cc_import(
  name = "mylib",
  hdrs = ["mylib.h"],
  shared_library = "libmylib.so",
)
```

通过接口库（Interface library）链接到共享库（Windows）：

```
cc_import(
  name = "mylib",
  hdrs = ["mylib.h"],
  # mylib.lib是mylib.dll的导入库，此导入库会传递给链接器
  interface_library = "mylib.lib",
  # mylib.dll在运行时需要，链接时不需要
  shared_library = "mylib.dll",
)
```

在二进制目标中选择链接到共享库还是静态库（UNIX）：

```
cc_import(
  name = "mylib",
  hdrs = ["mylib.h"],
  # 同时声明共享库和静态库
  static_library = "libmylib.a",
  shared_library = "libmylib.so",
)
 
# 此二进制目标链接到静态库
cc_binary(
  name = "first",
  srcs = ["first.cc"],
  deps = [":mylib"],
  linkstatic = 1, # default value
)
 
# 此二进制目标链接到共享库
cc_binary(
  name = "second",
  srcs = ["second.cc"],
  deps = [":mylib"],
  linkstatic = 0,
)
```

#### 包含外部库

你可以在WORKSPACE中调用`new_*`存储库函数，来从网络中下载依赖。下面的例子下载Google Test库：

```
# 下载归档文件，并让其在工作空间的存储库中可用
new_http_archive(
    name = "gtest",
    url = "https://github.com/google/googletest/archive/release-1.7.0.zip",
    sha256 = "b58cb7547a28b2c718d1e38aee18a3659c9e3ff52440297e965f5edffe34b6d0",
    # 外部库的构建规则编写在gtest.BUILD
    # 如果此归档文件已经自带了BUILD文件，则可以调用不带new_前缀的函数
    build_file = "gtest.BUILD",
    # 去除路径前缀
    strip_prefix = "googletest-release-1.7.0",
)
```

构建此外部库的规则如下：

gtest.BUILD

```
cc_library(
    name = "main",
    srcs = glob(
        # 前缀去除，原来是googletest-release-1.7.0/src/*.cc
        ["src/*.cc"],
        # 排除此文件
        exclude = ["src/gtest-all.cc"]
    ),
    hdrs = glob([
        # 前缀去除
        "include/**/*.h",
        "src/*.h"
    ]),
    copts = [
        # 前缀去除，原来是external/gtest/googletest-release-1.7.0/include
        "-Iexternal/gtest/include"
    ],
    # 链接到pthread
    linkopts = ["-pthread"],
    visibility = ["//visibility:public"],
)
```

#### 使用外部库

沿用上面的例子，下面的目标使用gtest编写测试代码：

```
cc_test(
    name = "hello-test",
    srcs = ["hello-test.cc"],
    # 前缀去除
    copts = ["-Iexternal/gtest/include"],
    deps = [
        # 依赖gtest存储库的main目标
        "@gtest//:main",
        "//lib:hello-greet",
    ],
)
```

## 外部依赖

Bazel允许依赖其它项目中定义的目标，这些来自其它项目的依赖叫做“外部依赖“。当前工作空间的WORKSPACE文件声明从何处下载外部依赖的源码。

外部依赖可以有自己的1-N个BUILD文件，其中定义自己的目标。当前项目可以使用这些目标。例如下面的两个项目结构：

```
/
  home/
    user/
      project1/
        WORKSPACE
        BUILD
        srcs/
          ...
      project2/
        WORKSPACE
        BUILD
        my-libs/
```

如果project1需要依赖定义在project2/BUILD中的目标:foo，则可以在其WORKSPACE中声明一个存储库（repository），名字为project2，位于/home/user/project2。然后，可以在BUILD中通过标签@project2//:foo引用目标foo。

除了依赖来自文件系统其它部分的目标、下载自互联网的目标以外，用户还可以编写自己的存储库规则（repository rules ）以实现更复杂的行为。

WORKSPACE的语法格式和BUILD相同，但是允许使用[不同的规则集](https://docs.bazel.build/versions/master/be/workspace.html)。

Bazel会把外部依赖下载到 `$(bazel info output_base)/external` 目录中，要删除掉外部依赖，执行：

```
bazel clean --expunge
```

### 外部依赖类型

#### Bazel项目

可以使用local_repository、git_repository或者http_archive这几个规则来引用。

引用本地Bazel项目的例子：

my_project/WORKSPACE

```
local_repository(
    name = "coworkers_project",
    path = "/path/to/coworkers-project",
)
```

在BUILD中，引用`coworkers_project`中的目标//foo:bar时，使用标签@coworkers_project//foo:bar

#### 非Bazel项目

可以使用`new_local_repository`、`new_git_repository`或者`new_http_archive`这几个规则来引用。你需要自己编写BUILD文件来构建这些项目。

引用本地非Bazel项目的例子：

```
new_local_repository(
    name = "coworkers_project",
    path = "/path/to/coworkers-project",
    build_file = "coworker.BUILD",
)
```

coworker.BUILD

```
cc_library(
    name = "some-lib",
    srcs = glob(["**"]),
    visibility = ["//visibility:public"],
)
```

在BUILD文件中，使用标签`@coworkers_project//:some-lib`引用上面的库。

#### 外部包

对于Maven仓库，可以使用规则`maven_jar/maven_server`来下载JAR包，并将其作为Java依赖。

### 依赖拉取

默认情况下，执行bazel Build时会按需自动拉取依赖，你也可以禁用此特性，并使用bazel fetch预先手工拉取依赖。

### 使用代理

Bazel可以使用`HTTPS_PROXY`或`HTTP_PROXY`定义的代理地址。

### 依赖缓存

Bazel会缓存外部依赖，当WORKSPACE改变时，会重新下载或更新这些依赖。

## .bazelrc

Bazel命令接收大量的参数，其中一部分很少变化，这些不变的配置项可以存放在.bazelrc中。

### 位置

Bazel按以下顺序寻找.bazelrc文件：

  1. 除非指定--nosystem_rc，否则寻找/etc/bazel.bazelrc
  2. 除非指定--noworkspace_rc，否则寻找工作空间根目录的.bazelrc
  3. 除非指定--nohome_rc，否则寻找当前用户的$HOME/.bazelrc

### 语法

<table class="full-width fixed-word-wrap">
<thead>
<tr>
<td style="width: 20%; text-align: center;">元素</td>
<td style="text-align: center;">说明</td>
</tr>
</thead>
<tbody>
<tr>
<td>import</td>
<td>导入其它bazelrc文件，例如：
      <span id="crayon-64af882488170788411260" class="crayon-syntax crayon-syntax-inline  crayon-theme-gmem-github crayon-theme-gmem-github-inline crayon-font-consolas" style="font-size: 15px !important; line-height: 20px !important;font-size: 15px !important;"><span class="crayon-pre crayon-code" style="font-size: 15px !important; line-height: 20px !important;font-size: 15px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;"><span class="crayon-v">import</span><span class="crayon-h"> </span><span class="crayon-o">%</span><span class="crayon-v">workspace</span><span class="crayon-o">%</span><span class="crayon-o">/</span><span class="crayon-v">tools</span><span class="crayon-o">/</span><span class="crayon-v">bazel</span><span class="crayon-sy">.</span><span class="crayon-v">rc</span></span></span></td>
</tr>
<tr>
<td>默认参数</td>
<td>
<p>可以提供以下行：</p>
<p>startup ... 启动参数<br>common... 适用于所有命令的参数<br><em>command</em>...为某个子命令指定参数，例如buildquery、</p>
<p>以上三类行，都可以出现多次</p>
</td>
</tr>
<tr>
<td>
<p>--config</p>
</td>
<td>
<p>用于定义一组参数的组合，在调用bazel命令时指定--config=memcheck，可以引用名为memcheck的参数组。此参数组的定义示例：</p>
    <div>
        <table class="crayon-table" style="">
          <tbody><tr class="crayon-row">
            <td class="crayon-code"><div class="crayon-pre" style="font-size: 15px !important; line-height: 20px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;"><div class="crayon-line" id="crayon-64af882488173158985852-1"><span class="crayon-v">build</span><span class="crayon-o">:</span><span class="crayon-v">memcheck</span><span class="crayon-h"> </span><span class="crayon-o">--</span><span class="crayon-r">strip</span><span class="crayon-o">=</span><span class="crayon-v">never</span><span class="crayon-h"> </span><span class="crayon-o">--</span><span class="crayon-v">test_timeout</span><span class="crayon-o">=</span><span class="crayon-cn">3600</span></div></div></td>
          </tr>
        </tbody></table>
    </div>
</td>
</tr>
</tbody>
</table>

## 扩展

所谓Bazel扩展，是扩展名为.bzl的文件。你可以使用load语句加载扩展中定义的符号到BUILD中。

### 构建阶段

一次Bazel构建包含三个阶段：

  1. 加载阶段：加载、eval本次构建需要的所有扩展、所有BUILD文件。宏在此阶段执行，规则被实例化。BUILD文件中调用的宏/函数，在此阶段执行函数体，其结果是宏里面实例化的规则被填充到BUILD文件中
  2. 分析阶段：规则的代码——也就是它的implementation函数被执行，导致规则的Action被实例化，Action描述如何从输入产生输出
  3. 执行阶段：执行Action，产生输出，测试也在此阶段执行

Bazel会并行的读取/解析/eval BUILD文件和.bzl文件。每个文件在每次构建最多被读取一次，eval的结果被缓存并重用。每个文件在它的全部依赖被解析之后才eval。加载一个.bzl文件没有副作用，仅仅是定义值和函数

### 宏

宏（Macro）是一种函数，用来实例化（instantiates）规则。如果BUILD文件太过重复或复杂，可以考虑使用宏，以便减少代码。宏的函数在BUILD文件被读取时就立即执行。BUILD被读取（eval）之后，宏被替换为它生成的规则。bazel query只会列出生成的规则而非宏。

编写宏时需要注意：

  1. 所有实例化规则的公共函数，都必须具有一个无默认值的name参数
  2. 公共函数应当具有docstring
  3. 在BUILD文件中，调用宏时name参数必须是关键字参数
  4. 宏所生成的规则的name属性，必须以调用宏的name参数作为后缀
  5. 大部分情况下，可选参数应该具有默认值None
  6. 应当具有可选的visibility参数

#### 示例

要在宏中实例化原生规则（Native rules，不需要load即可使用的那些规则），可以使用native模块：

path/generator

```
# 该宏实例化一个genrule规则
def file_generator(name, arg, visibility=None):
  // 生成一个genrule规则
  native.genrule(
    name = name,
    outs = [name + ".txt"],
    cmd = "$(location generator) %s > $@" % arg,
    tools = ["//test:generator"],
    visibility = visibility,
  )
```

使用上述宏的BUILD文件：

BUILD

```
load("//path:generator.bzl", "file_generator")
 
file_generator(
    name = "file",
    arg = "some_arg",
)
```

执行下面的命令查看宏展开后的情况：

```
# bazel query --output=build //label
 
genrule(
  name = "file",
  tools = ["//test:generator"],
  outs = ["//test:file.txt"],
  cmd = "$(location generator) some_arg > $@",
)
```

### 规则

[规则（Rule）](https://docs.bazel.build/versions/master/skylark/rules.html)比宏更强大，能够对Bazel内部特性进行访问，并可以完全控制Bazel。

规则定义了为了产生输出，需要在输入上执行的一系列动作。例如，C++二进制文件规则以一系列.cpp文件为输入，针对输入调用g++，输出一个可执行文件。注意，从Bazel的角度来说，不但cpp文件是输入，g++、C++库也是输入。当编写自定义规则时，你需要注意，将执行Action所需的库、工具作为输入看待。

Bazel内置了一些规则，这些规则叫原生规则，例如cc_library、cc_library，对一些语言提供了基础的支持。通过编写自定义规则，你可以实现对任何语言的支持。

定义在.bzl中的规则，用起来就像原生规则一样 —— 规则的目标具有标签、可以出现在bazel query。

规则在分析阶段的行为，由它的implementation函数决定。此函数不得调用任何外部工具，它只是注册在执行阶段需要的Action。

#### 自定义规则

在.bzl文件中，你可以调用rule创建自定义规则，并将其保存到全局变量：

```
def _empty_impl(ctx):
    # 分析阶段此函数被执行
    print("This rule does nothing")
 
empty = rule(implementation = _empty_impl)
```

然后，规则可以通过load加载到BUILD文件：

```
load("//empty:empty.bzl", "empty")
 
# 实例化规则
empty(name = "nothing")
```

#### 规则属性

属性即实例化规则时需要提供的参数，例如srcs、deps。在自定义规则的时候，你可以列出所有属性的名字和Schema：

```
sum = rule(
    implementation = _impl,
    attrs = {
        # 定义一个整数属性，一个列表属性
        "number": attr.int(default = 1),
        "deps": attr.label_list(),
    },
)
```

实例化规则的时候，你需要以参数的形式指定属性：

```
sum(
    name = "my-target",
    deps = [":other-target"],
)
 
sum(
    name = "other-target",
)
```

如果实例化规则的时候，没有指定某个属性的值（且没指定默认值），规则的实现函数会在ctx.attr中看到一个占位符，此占位符的值取决于属性的类型。

使用default为属性指定默认值，使用 mandatory=True 声明属性必须提供。

#### 默认属性

任何规则自动具有以下属性：deprecation, features, name, tags, testonly, visibility。

任何测试规则具有以下额外属性：args, flaky, local, shard_count, size, timeout。

#### 特殊属性

有两类特殊属性需要注意：

  1. 依赖属性：例如`attr.label、attr.label_list`，用于声明拥有此属性的目标所依赖的其它目标
  2. 输出属性：例如`attr.output、attr.output_list`，声明目标的输出文件，较少使用

上面两类属性的值都是Label类型。

#### 隐含依赖

具有默认值的依赖属性，称为隐含依赖（implicit dependency）。如果要硬编码规则和工具（例如编译器）之间的关系，可通过隐含依赖。从规则的角度来看，这些工具仍然属于输入，就像源代码一样。

#### 私有属性

某些情况下，我们会为规则添加具有默认值的属性，同时还想禁止用户修改属性值，这种情况下可以使用私有属性。

私有属性以下划线 `_` 开头，必须具有默认值。

#### 目标

实例化规则不会返回值，但是会定义一个新的目标。

#### 规则实现

任何规则都需要提供一个实现函数。提供在分析阶段需要严格执行的逻辑。此函数不能有任何读写行为，仅仅用于注册Action。

实现函数具有唯一性入参 —— [规则上下文](https://docs.bazel.build/versions/master/skylark/lib/ctx.html)，通常将其命名为ctx。通过规则上下文你可以：

  1. 访问规则属性
  2. 获得输入输出文件的handle
  3. 创建Actions
  4. 通过providers向依赖于当前规则的其它规则传递信息

#### ctx

规则上下文对象的具有以下主要方法或属性：

<table>
<thead>
<tr>
<td style="width: 20%; text-align: center;">方法/属性</td>
<td style="text-align: center;">说明</td>
</tr>
</thead>
<tbody>
<tr>
<td>action</td>
<td>废弃，使用ctx.actions.run()或ctx.actions.run_shell()代替</td>
</tr>
<tr>
<td>actions.run</td>
<td>
<p>创建一个调用可执行文件的Action，参数：Bazel加载阶段</p>
<p>outputs 此动作的输出文件列表<br>inputs 此动作输入文件的列表/depset<br>executable&nbsp;执行此动作需要调用的可执行文件<br>tools 执行此动作需要的工具的列表/depset<br>arguments 传递给可执行文件的参数列表<br>mnemonic 动作的描述<br>progress_message 动作执行时，显示给用户的信息<br>use_default_shell_env 是否在内建Shell环境下运行可执行文件<br>env 环境变量字典<br>execution_requirements 调度此动作需要的信息<br>input_manifests 输入runfiles元数据，通常由resolve_command生成</p>
<p>示例：</p>
    <div>
        <table class="crayon-table" style="">
          <tbody><tr class="crayon-row">
            <td class="crayon-code"><div class="crayon-pre" style="font-size: 15px !important; line-height: 20px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;"><div class="crayon-line" id="crayon-64af882488186987827972-1"><span class="crayon-r">def</span><span class="crayon-h"> </span><span class="crayon-e">_impl</span><span class="crayon-sy">(</span><span class="crayon-v">ctx</span><span class="crayon-sy">)</span><span class="crayon-o">:</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af882488186987827972-2"><span class="crayon-h">&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="crayon-c"># The list of arguments we pass to the script.</span></div><div class="crayon-line" id="crayon-64af882488186987827972-3"><span class="crayon-h">&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="crayon-v">args</span><span class="crayon-h"> </span><span class="crayon-o">=</span><span class="crayon-h"> </span><span class="crayon-sy">[</span><span class="crayon-v">ctx</span><span class="crayon-sy">.</span><span class="crayon-v">outputs</span><span class="crayon-sy">.</span><span class="crayon-v">out</span><span class="crayon-sy">.</span><span class="crayon-v">path</span><span class="crayon-sy">]</span><span class="crayon-h"> </span><span class="crayon-o">+</span><span class="crayon-h"> </span><span class="crayon-sy">[</span><span class="crayon-v">f</span><span class="crayon-sy">.</span><span class="crayon-e">path </span><span class="crayon-st">for</span><span class="crayon-h"> </span><span class="crayon-i">f</span><span class="crayon-h"> </span><span class="crayon-st">in</span><span class="crayon-h"> </span><span class="crayon-v">ctx</span><span class="crayon-sy">.</span><span class="crayon-v">files</span><span class="crayon-sy">.</span><span class="crayon-v">chunks</span><span class="crayon-sy">]</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af882488186987827972-4">&nbsp;</div><div class="crayon-line" id="crayon-64af882488186987827972-5"><span class="crayon-h">&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="crayon-c"># 调用可执行文件</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af882488186987827972-6"><span class="crayon-h">&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="crayon-v">ctx</span><span class="crayon-sy">.</span><span class="crayon-v">actions</span><span class="crayon-sy">.</span><span class="crayon-e">run</span><span class="crayon-sy">(</span></div><div class="crayon-line" id="crayon-64af882488186987827972-7"><span class="crayon-h">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="crayon-v">inputs</span><span class="crayon-h"> </span><span class="crayon-o">=</span><span class="crayon-h"> </span><span class="crayon-v">ctx</span><span class="crayon-sy">.</span><span class="crayon-v">files</span><span class="crayon-sy">.</span><span class="crayon-v">chunks</span><span class="crayon-sy">,</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af882488186987827972-8"><span class="crayon-h">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="crayon-v">outputs</span><span class="crayon-h"> </span><span class="crayon-o">=</span><span class="crayon-h"> </span><span class="crayon-sy">[</span><span class="crayon-v">ctx</span><span class="crayon-sy">.</span><span class="crayon-v">outputs</span><span class="crayon-sy">.</span><span class="crayon-v">out</span><span class="crayon-sy">]</span><span class="crayon-sy">,</span></div><div class="crayon-line" id="crayon-64af882488186987827972-9"><span class="crayon-h">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="crayon-v">arguments</span><span class="crayon-h"> </span><span class="crayon-o">=</span><span class="crayon-h"> </span><span class="crayon-v">args</span><span class="crayon-sy">,</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af882488186987827972-10"><span class="crayon-h">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="crayon-v">progress_message</span><span class="crayon-h"> </span><span class="crayon-o">=</span><span class="crayon-h"> </span><span class="crayon-s">"Merging into %s"</span><span class="crayon-h"> </span><span class="crayon-o">%</span><span class="crayon-h"> </span><span class="crayon-v">ctx</span><span class="crayon-sy">.</span><span class="crayon-v">outputs</span><span class="crayon-sy">.</span><span class="crayon-v">out</span><span class="crayon-sy">.</span><span class="crayon-v">short_path</span><span class="crayon-sy">,</span></div><div class="crayon-line" id="crayon-64af882488186987827972-11"><span class="crayon-h">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="crayon-v">executable</span><span class="crayon-h"> </span><span class="crayon-o">=</span><span class="crayon-h"> </span><span class="crayon-v">ctx</span><span class="crayon-sy">.</span><span class="crayon-v">executable</span><span class="crayon-sy">.</span><span class="crayon-v">_merge_tool</span><span class="crayon-sy">,</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af882488186987827972-12"><span class="crayon-h">&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="crayon-sy">)</span></div><div class="crayon-line" id="crayon-64af882488186987827972-13"><span class="crayon-o">/</span><span class="crayon-o">/</span><span class="crayon-h"> </span>规则定义</div><div class="crayon-line crayon-striped-line" id="crayon-64af882488186987827972-14"><span class="crayon-v">concat</span><span class="crayon-h"> </span><span class="crayon-o">=</span><span class="crayon-h"> </span><span class="crayon-e">rule</span><span class="crayon-sy">(</span></div><div class="crayon-line" id="crayon-64af882488186987827972-15"><span class="crayon-h">&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="crayon-v">implementation</span><span class="crayon-h"> </span><span class="crayon-o">=</span><span class="crayon-h"> </span><span class="crayon-v">_impl</span><span class="crayon-sy">,</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af882488186987827972-16"><span class="crayon-h">&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="crayon-v">attrs</span><span class="crayon-h"> </span><span class="crayon-o">=</span><span class="crayon-h"> </span><span class="crayon-sy">{</span></div><div class="crayon-line" id="crayon-64af882488186987827972-17"><span class="crayon-h">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="crayon-s">"chunks"</span><span class="crayon-o">:</span><span class="crayon-h"> </span><span class="crayon-v">attr</span><span class="crayon-sy">.</span><span class="crayon-e">label_list</span><span class="crayon-sy">(</span><span class="crayon-v">allow_files</span><span class="crayon-h"> </span><span class="crayon-o">=</span><span class="crayon-h"> </span><span class="crayon-t">True</span><span class="crayon-sy">)</span><span class="crayon-sy">,</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af882488186987827972-18"><span class="crayon-h">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="crayon-s">"out"</span><span class="crayon-o">:</span><span class="crayon-h"> </span><span class="crayon-v">attr</span><span class="crayon-sy">.</span><span class="crayon-e">output</span><span class="crayon-sy">(</span><span class="crayon-v">mandatory</span><span class="crayon-h"> </span><span class="crayon-o">=</span><span class="crayon-h"> </span><span class="crayon-t">True</span><span class="crayon-sy">)</span><span class="crayon-sy">,</span></div><div class="crayon-line" id="crayon-64af882488186987827972-19"><span class="crayon-h">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="crayon-s">"_merge_tool"</span><span class="crayon-o">:</span><span class="crayon-h"> </span><span class="crayon-v">attr</span><span class="crayon-sy">.</span><span class="crayon-e">label</span><span class="crayon-sy">(</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af882488186987827972-20"><span class="crayon-h">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="crayon-v">executable</span><span class="crayon-h"> </span><span class="crayon-o">=</span><span class="crayon-h"> </span><span class="crayon-t">True</span><span class="crayon-sy">,</span></div><div class="crayon-line" id="crayon-64af882488186987827972-21"><span class="crayon-h">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="crayon-v">cfg</span><span class="crayon-h"> </span><span class="crayon-o">=</span><span class="crayon-h"> </span><span class="crayon-s">"host"</span><span class="crayon-sy">,</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af882488186987827972-22"><span class="crayon-h">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="crayon-v">allow_files</span><span class="crayon-h"> </span><span class="crayon-o">=</span><span class="crayon-h"> </span><span class="crayon-t">True</span><span class="crayon-sy">,</span></div><div class="crayon-line" id="crayon-64af882488186987827972-23"><span class="crayon-h">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="crayon-v">default</span><span class="crayon-h"> </span><span class="crayon-o">=</span><span class="crayon-h"> </span><span class="crayon-e">Label</span><span class="crayon-sy">(</span><span class="crayon-s">"//actions_run:merge"</span><span class="crayon-sy">)</span><span class="crayon-sy">,</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af882488186987827972-24"><span class="crayon-h">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="crayon-sy">)</span><span class="crayon-sy">,</span></div><div class="crayon-line" id="crayon-64af882488186987827972-25"><span class="crayon-h">&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="crayon-sy">}</span><span class="crayon-sy">,</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af882488186987827972-26"><span class="crayon-sy">)</span>&nbsp;</div></div></td>
          </tr>
        </tbody></table>
    </div>
</td>
</tr>
<tr>
<td>actions.run_shell</td>
<td>
<p>创建一个执行Shell脚本的Action
</p><p>示例：</p>
<div>
        <table class="crayon-table" style="">
          <tbody><tr class="crayon-row">
            <td class="crayon-code"><div class="crayon-pre" style="font-size: 15px !important; line-height: 20px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;"><div class="crayon-line" id="crayon-64af882488189295782718-1"><span class="crayon-r">def</span><span class="crayon-h"> </span><span class="crayon-e">_impl</span><span class="crayon-sy">(</span><span class="crayon-v">ctx</span><span class="crayon-sy">)</span><span class="crayon-o">:</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af882488189295782718-2"><span class="crayon-h">&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="crayon-v">output</span><span class="crayon-h"> </span><span class="crayon-o">=</span><span class="crayon-h"> </span><span class="crayon-v">ctx</span><span class="crayon-sy">.</span><span class="crayon-v">outputs</span><span class="crayon-sy">.</span><span class="crayon-e">out</span></div><div class="crayon-line" id="crayon-64af882488189295782718-3"><span class="crayon-e">&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="crayon-k ">input</span><span class="crayon-h"> </span><span class="crayon-o">=</span><span class="crayon-h"> </span><span class="crayon-v">ctx</span><span class="crayon-sy">.</span><span class="crayon-k ">file</span><span class="crayon-sy">.</span><span class="crayon-k ">file</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af882488189295782718-4">&nbsp;</div><div class="crayon-line" id="crayon-64af882488189295782718-5"><span class="crayon-h">&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="crayon-c"># 访问inputs中声明的文件</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af882488189295782718-6"><span class="crayon-h">&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="crayon-v">ctx</span><span class="crayon-sy">.</span><span class="crayon-v">actions</span><span class="crayon-sy">.</span><span class="crayon-e">run_shell</span><span class="crayon-sy">(</span></div><div class="crayon-line" id="crayon-64af882488189295782718-7"><span class="crayon-h">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="crayon-v">inputs</span><span class="crayon-h"> </span><span class="crayon-o">=</span><span class="crayon-h"> </span><span class="crayon-sy">[</span><span class="crayon-k ">input</span><span class="crayon-sy">]</span><span class="crayon-sy">,</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af882488189295782718-8"><span class="crayon-h">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="crayon-v">outputs</span><span class="crayon-h"> </span><span class="crayon-o">=</span><span class="crayon-h"> </span><span class="crayon-sy">[</span><span class="crayon-v">output</span><span class="crayon-sy">]</span><span class="crayon-sy">,</span></div><div class="crayon-line" id="crayon-64af882488189295782718-9"><span class="crayon-h">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="crayon-v">progress_message</span><span class="crayon-h"> </span><span class="crayon-o">=</span><span class="crayon-h"> </span><span class="crayon-s">"Getting size of %s"</span><span class="crayon-h"> </span><span class="crayon-o">%</span><span class="crayon-h"> </span><span class="crayon-k ">input</span><span class="crayon-sy">.</span><span class="crayon-v">short_path</span><span class="crayon-sy">,</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af882488189295782718-10"><span class="crayon-h">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="crayon-v">command</span><span class="crayon-h"> </span><span class="crayon-o">=</span><span class="crayon-h"> </span><span class="crayon-s">"stat -L -c%%s '%s' &gt; '%s'"</span><span class="crayon-h"> </span><span class="crayon-o">%</span><span class="crayon-h"> </span><span class="crayon-sy">(</span><span class="crayon-k ">input</span><span class="crayon-sy">.</span><span class="crayon-v">path</span><span class="crayon-sy">,</span><span class="crayon-h"> </span><span class="crayon-v">output</span><span class="crayon-sy">.</span><span class="crayon-v">path</span><span class="crayon-sy">)</span><span class="crayon-sy">,</span></div><div class="crayon-line" id="crayon-64af882488189295782718-11"><span class="crayon-h">&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="crayon-sy">)</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af882488189295782718-12">&nbsp;</div><div class="crayon-line" id="crayon-64af882488189295782718-13"><span class="crayon-c"># 规则定义</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af882488189295782718-14"><span class="crayon-v">size</span><span class="crayon-h"> </span><span class="crayon-o">=</span><span class="crayon-h"> </span><span class="crayon-e">rule</span><span class="crayon-sy">(</span></div><div class="crayon-line" id="crayon-64af882488189295782718-15"><span class="crayon-h">&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="crayon-v">implementation</span><span class="crayon-h"> </span><span class="crayon-o">=</span><span class="crayon-h"> </span><span class="crayon-v">_impl</span><span class="crayon-sy">,</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af882488189295782718-16"><span class="crayon-h">&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="crayon-v">attrs</span><span class="crayon-h"> </span><span class="crayon-o">=</span><span class="crayon-h"> </span><span class="crayon-sy">{</span><span class="crayon-s">"file"</span><span class="crayon-o">:</span><span class="crayon-h"> </span><span class="crayon-v">attr</span><span class="crayon-sy">.</span><span class="crayon-e">label</span><span class="crayon-sy">(</span><span class="crayon-v">mandatory</span><span class="crayon-h"> </span><span class="crayon-o">=</span><span class="crayon-h"> </span><span class="crayon-t">True</span><span class="crayon-sy">,</span><span class="crayon-h"> </span><span class="crayon-v">allow_single_file</span><span class="crayon-h"> </span><span class="crayon-o">=</span><span class="crayon-h"> </span><span class="crayon-t">True</span><span class="crayon-sy">)</span><span class="crayon-sy">}</span><span class="crayon-sy">,</span></div><div class="crayon-line" id="crayon-64af882488189295782718-17"><span class="crayon-h">&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="crayon-v">outputs</span><span class="crayon-h"> </span><span class="crayon-o">=</span><span class="crayon-h"> </span><span class="crayon-sy">{</span><span class="crayon-s">"out"</span><span class="crayon-o">:</span><span class="crayon-h"> </span><span class="crayon-s">"%{name}.size"</span><span class="crayon-sy">}</span><span class="crayon-sy">,</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af882488189295782718-18"><span class="crayon-sy">)</span></div></div></td>
          </tr>
        </tbody></table>
    </div>
</td>
</tr>
<tr>
<td>actions.write</td>
<td>此Action写入内容到文件</td>
</tr>
<tr>
<td>actions.declare_file</td>
<td>此Action创建新的文件</td>
</tr>
<tr>
<td>actions.do_nothing</td>
<td>不做任何事情的Action</td>
</tr>
<tr>
<td>ctx.attr</td>
<td>用于访问属性值的结构&nbsp;</td>
</tr>
<tr>
<td>bin_dir</td>
<td>二进制目录的根</td>
</tr>
<tr>
<td>genfiles_dir</td>
<td>genfiles目录的根</td>
</tr>
<tr>
<td>build_file_path</td>
<td>相对于源码目录根的，当前BUILD文件的路径</td>
</tr>
<tr>
<td>executable&nbsp;</td>
<td>一个结构，可以引用任何通过
      <span id="crayon-64af88248818b526037004" class="crayon-syntax crayon-syntax-inline  crayon-theme-gmem-github crayon-theme-gmem-github-inline crayon-font-consolas" style="font-size: 15px !important; line-height: 20px !important;font-size: 15px !important;"><span class="crayon-pre crayon-code" style="font-size: 15px !important; line-height: 20px !important;font-size: 15px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;"><span class="crayon-v">attr</span><span class="crayon-sy">.</span><span class="crayon-e">label</span><span class="crayon-sy">(</span><span class="crayon-v">executable</span><span class="crayon-o">=</span><span class="crayon-t">True</span><span class="crayon-sy">)</span></span></span>定义的规则属性</td>
</tr>
<tr>
<td>expand_location&nbsp;</td>
<td>
<p>展开input中定义的所有$(location //x)为目标x的真实路径。仅仅对当前规则的直接依赖、明确列在targets属性中的目标使用</p>
<div>
        <table class="crayon-table" style="">
          <tbody><tr class="crayon-row">
            <td class="crayon-code"><div class="crayon-pre" style="font-size: 15px !important; line-height: 20px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;"><div class="crayon-line" id="crayon-64af88248818e345483297-1"><span class="crayon-k ">string</span><span class="crayon-h"> </span><span class="crayon-v">ctx</span><span class="crayon-sy">.</span><span class="crayon-e">expand_location</span><span class="crayon-sy">(</span><span class="crayon-k ">input</span><span class="crayon-sy">,</span><span class="crayon-h"> </span><span class="crayon-v">targets</span><span class="crayon-o">=</span><span class="crayon-sy">[</span><span class="crayon-sy">]</span><span class="crayon-sy">)</span></div></div></td>
          </tr>
        </tbody></table>
    </div>
</td>
</tr>
<tr>
<td>features</td>
<td>列出此规则明确启用的特性列表&nbsp;</td>
</tr>
<tr>
<td>file</td>
<td>
<p>此结构包含任何通过
      <span id="crayon-64af882488190193270594" class="crayon-syntax crayon-syntax-inline  crayon-theme-gmem-github crayon-theme-gmem-github-inline crayon-font-consolas" style="font-size: 15px !important; line-height: 20px !important;font-size: 15px !important;"><span class="crayon-pre crayon-code" style="font-size: 15px !important; line-height: 20px !important;font-size: 15px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;"><span class="crayon-v">attr</span><span class="crayon-sy">.</span><span class="crayon-e">labe</span><span class="crayon-sy">(</span><span class="crayon-v">allow_single_file</span><span class="crayon-o">=</span><span class="crayon-t">True</span><span class="crayon-sy">)</span></span></span>定义的属性所指向的文件。此结构的字段名即文件属性名，结构字段值是file或Node类型</p>
<p>此结构是表达式
      <span id="crayon-64af882488192172302955" class="crayon-syntax crayon-syntax-inline  crayon-theme-gmem-github crayon-theme-gmem-github-inline crayon-font-consolas" style="font-size: 15px !important; line-height: 20px !important;font-size: 15px !important;"><span class="crayon-pre crayon-code" style="font-size: 15px !important; line-height: 20px !important;font-size: 15px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;"><span class="crayon-e">list</span><span class="crayon-sy">(</span><span class="crayon-v">ctx</span><span class="crayon-sy">.</span><span class="crayon-v">attr</span><span class="crayon-sy">.</span><span class="crayon-o">&lt;</span><span class="crayon-v">ATTR</span><span class="crayon-o">&gt;</span><span class="crayon-sy">.</span><span class="crayon-v">files</span><span class="crayon-sy">)</span><span class="crayon-sy">[</span><span class="crayon-cn">0</span><span class="crayon-sy">]</span></span></span>的快捷方式</p>
</td>
</tr>
<tr>
<td>fragments</td>
<td>用于访问目标配置中的配置片断（configuration fragments ）&nbsp;</td>
</tr>
<tr>
<td>host_configuration</td>
<td>返回主机配置的configuration对象。configuration包含构建所在的运行环境信息&nbsp;</td>
</tr>
<tr>
<td>host_fragments&nbsp;</td>
<td>用于访问host配置中的配置片断（configuration fragments ） &nbsp;</td>
</tr>
<tr>
<td>label</td>
<td>当前正在分析的目标的标签&nbsp;</td>
</tr>
<tr>
<td>outputs</td>
<td>一个包含所有预声明的输出文件的伪结构&nbsp;</td>
</tr>
<tr>
<td>resolve_command</td>
<td>
<p>解析一个命令，返回(inputs, command, input_manifests)元组：</p>
<p>inputs，表示解析后的输入列表<br>command，解析后的命令的argv列表<br>input_manifests，执行命令需要的runfiles元数据</p>
</td>
</tr>
<tr>
<td>resolve_tools&nbsp;</td>
<td>解析工具，返回(inputs, input_manifests)元组&nbsp;</td>
</tr>
<tr>
<td>runfiles&nbsp;</td>
<td>创建一个Runfiles</td>
</tr>
<tr>
<td>toolchains</td>
<td>此规则需要的工具链&nbsp;</td>
</tr>
<tr>
<td>var&nbsp;</td>
<td>配置变量的字典</td>
</tr>
<tr>
<td>workspace_name&nbsp;</td>
<td>当前工作空间的名称&nbsp;</td>
</tr>
</tbody>
</table>

#### 存储库规则

存储库规则用于定义外部存储库。外部存储库是一种规则，这种规则只能用在WORKSPACE文件中，可以在Bazel加载阶段启用非封闭性（ non-hermetic，所谓封闭是指自包含，不依赖于外部环境）操作。每个外部存储库都创建自己的WORKSPACE，具有自己的BUILD文件和构件。

外部存储库可以用来：

  1. 加载第三方依赖，例如Maven打包的库
  2. 为运行构件的主机生成特化的BUILD文件

在bzl文件中，调用repository_rule函数可以创建一个存储库规则，你需要将其存放在全局变量中：

```
local_repository = repository_rule(
    # 实现函数
    implementation=_impl,
    local=True,
    # 属性列表
    attrs={"path": attr.string(mandatory=True)}) 
```

每个存储库规则都必须提供实现函数，其中包含在Bazel加载阶段需要执行的严格的逻辑。该函数具有唯一的入参`repository_ctx`：

```
def _impl(repository_ctx):
  # 你可以通过repository_ctx访问属性值、调用非密封性函数（例如查找、执行二进制文件，创建或下载文件到存储库）
  repository_ctx.symlink(repository_ctx.attr.path, "") 
```

引用存储库中规则时，可以使用 `@REPO_NAMAE//package:target`这样的标签。

#### repository_ctx

存储库规则上下文对象的具有以下主要方法或属性：

<table class="full-width fixed-word-wrap">
<thead>
<tr>
<td style="width: 20%; text-align: center;">方法/属性</td>
<td style="text-align: center;">说明</td>
</tr>
</thead>
<tbody>
<tr>
<td>attr</td>
<td>用于访问所有属性的结构</td>
</tr>
<tr>
<td>download</td>
<td>
<div>
        <table class="crayon-table" style="">
          <tbody><tr class="crayon-row">
            <td class="crayon-code"><div class="crayon-pre" style="font-size: 15px !important; line-height: 20px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;"><div class="crayon-line" id="crayon-64af88248819b117875036-1"><span class="crayon-k ">struct</span><span class="crayon-h"> </span><span class="crayon-v">repository_ctx</span><span class="crayon-sy">.</span><span class="crayon-e">download</span><span class="crayon-sy">(</span><span class="crayon-v">url</span><span class="crayon-sy">,</span><span class="crayon-h"> </span><span class="crayon-v">output</span><span class="crayon-o">=</span><span class="crayon-s">''</span><span class="crayon-sy">,</span><span class="crayon-h"> </span><span class="crayon-v">sha256</span><span class="crayon-o">=</span><span class="crayon-s">''</span><span class="crayon-sy">,</span><span class="crayon-h"> </span><span class="crayon-v">executable</span><span class="crayon-o">=</span><span class="crayon-t">False</span><span class="crayon-sy">)</span></div></div></td>
          </tr>
        </tbody></table>
    </div>
<p></p>
<p>&nbsp;下载文件到输出路径，返回包含字段sha256的结构</p>
</td>
</tr>
<tr>
<td>download_and_extract</td>
<td>下载并解压</td>
</tr>
<tr>
<td>execute</td>
<td>执行指定的命令</td>
</tr>
<tr>
<td>file</td>
<td>以指定的内容在存储库目录下生成文件</td>
</tr>
<tr>
<td>name</td>
<td>此规则生成的外部存储库的名称</td>
</tr>
<tr>
<td>path</td>
<td>返回字符串/路径/标签对应的实际路径</td>
</tr>
<tr>
<td>symlink</td>
<td>在文件系统中创建符号链接<br>
    <div>
        <table class="crayon-table" style="">
          <tbody><tr class="crayon-row">
            <td class="crayon-code"><div class="crayon-pre" style="font-size: 15px !important; line-height: 20px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;"><div class="crayon-line" id="crayon-64af88248819d264992696-1"><span class="crayon-c"># from 符号链接的源，string/Label/path类型</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af88248819d264992696-2"><span class="crayon-c"># to 相对于存储库目录的符号链接文件的路径</span></div><div class="crayon-line" id="crayon-64af88248819d264992696-3"><span class="crayon-t">None</span><span class="crayon-h"> </span><span class="crayon-v">repository_ctx</span><span class="crayon-sy">.</span><span class="crayon-e">symlink</span><span class="crayon-sy">(</span><span class="crayon-st">from</span><span class="crayon-sy">,</span><span class="crayon-h"> </span><span class="crayon-v">to</span><span class="crayon-sy">)</span></div></div></td>
          </tr>
        </tbody></table>
    </div>

</td>
</tr>
<tr>
<td>template</td>
<td>使用模板创建文件</td>
</tr>
<tr>
<td>which</td>
<td>返回指定程序的路径</td>
</tr>
</tbody>
</table>

## 命令

### bazel

子命令

<table class="full-width fixed-word-wrap">
<thead>
<tr>
<td style="width: 15%; text-align: center;">子命令</td>
<td style="text-align: center;">说明</td>
</tr>
</thead>
<tbody>
<tr>
<td class="blog_h3" header-level="3" header-index="12.1.1" header-title="analyze-profile">analyze-profile</td>
<td>分析构建配置数据（build profile data）</td>
</tr>
<tr>
<td class="blog_h3" header-level="3" header-index="12.1.2" header-title="aquery">aquery</td>
<td>针对post-analysis操作图执行查询</td>
</tr>
<tr>
<td class="blog_h3" header-level="3" header-index="12.1.3" header-title="build">build</td>
<td>构建指定的目标：<br>
<div>
        <table class="crayon-table" style="">
          <tbody><tr class="crayon-row">
            <td class="crayon-code"><div class="crayon-pre" style="font-size: 15px !important; line-height: 20px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;"><div class="crayon-line" id="crayon-64af8824881a0338461466-1"><span class="crayon-c"># 构建foo/bar包中的wiz目标</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af8824881a0338461466-2"><span class="crayon-e">bazel </span><span class="crayon-v">build</span><span class="crayon-h"> </span><span class="crayon-o">/</span><span class="crayon-o">/</span><span class="crayon-v">foo</span><span class="crayon-o">/</span><span class="crayon-v">bar</span><span class="crayon-o">:</span><span class="crayon-v">wiz</span></div><div class="crayon-line" id="crayon-64af8824881a0338461466-3"><span class="crayon-c"># 构建foo/bar包中的bar目标</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af8824881a0338461466-4"><span class="crayon-e">bazel </span><span class="crayon-v">build</span><span class="crayon-h"> </span><span class="crayon-o">/</span><span class="crayon-o">/</span><span class="crayon-v">foo</span><span class="crayon-o">/</span><span class="crayon-v">bar</span></div><div class="crayon-line" id="crayon-64af8824881a0338461466-5"><span class="crayon-c"># 构建foo/bar包中的所有规则</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af8824881a0338461466-6"><span class="crayon-e">bazel </span><span class="crayon-v">build</span><span class="crayon-h"> </span><span class="crayon-o">/</span><span class="crayon-o">/</span><span class="crayon-v">foo</span><span class="crayon-o">/</span><span class="crayon-v">bar</span><span class="crayon-o">:</span><span class="crayon-v">all</span></div><div class="crayon-line" id="crayon-64af8824881a0338461466-7"><span class="crayon-c"># 构建foo目录下所有子代包的所有规则</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af8824881a0338461466-8"><span class="crayon-e">bazel </span><span class="crayon-v">build</span><span class="crayon-h"> </span><span class="crayon-o">/</span><span class="crayon-o">/</span><span class="crayon-v">foo</span><span class="crayon-o">/</span><span class="crayon-sy">.</span><span class="crayon-sy">.</span><span class="crayon-sy">.</span></div><div class="crayon-line" id="crayon-64af8824881a0338461466-9"><span class="crayon-e">bazel </span><span class="crayon-v">build</span><span class="crayon-h"> </span><span class="crayon-o">/</span><span class="crayon-o">/</span><span class="crayon-v">foo</span><span class="crayon-o">/</span><span class="crayon-sy">.</span><span class="crayon-sy">.</span><span class="crayon-sy">.</span><span class="crayon-o">:</span><span class="crayon-v">all</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af8824881a0338461466-10"><span class="crayon-c"># 构建foo目录下所有子代包的所有目标（规则和文件）</span></div><div class="crayon-line" id="crayon-64af8824881a0338461466-11"><span class="crayon-e">bazel </span><span class="crayon-v">build</span><span class="crayon-h"> </span><span class="crayon-o">/</span><span class="crayon-o">/</span><span class="crayon-v">foo</span><span class="crayon-o">/</span><span class="crayon-sy">.</span><span class="crayon-sy">.</span><span class="crayon-sy">.</span><span class="crayon-o">:</span><span class="crayon-o">*</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af8824881a0338461466-12"><span class="crayon-e">bazel </span><span class="crayon-v">build</span><span class="crayon-h"> </span><span class="crayon-o">/</span><span class="crayon-o">/</span><span class="crayon-v">foo</span><span class="crayon-o">/</span><span class="crayon-sy">.</span><span class="crayon-sy">.</span><span class="crayon-sy">.</span><span class="crayon-o">:</span><span class="crayon-v">all</span><span class="crayon-o">-</span><span class="crayon-v">targets</span></div></div></td>
          </tr>
        </tbody></table>
    </div>
<p></p>
<p>如果目标标签不以
      <span id="crayon-64af8824881a2656949573" class="crayon-syntax crayon-syntax-inline  crayon-theme-gmem-github crayon-theme-gmem-github-inline crayon-font-consolas" style="font-size: 15px !important; line-height: 20px !important;font-size: 15px !important;"><span class="crayon-pre crayon-code" style="font-size: 15px !important; line-height: 20px !important;font-size: 15px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;"><span class="crayon-c">//</span></span></span>开头，则相对于当前目录。如果当前目录是foo则bar:wiz等价于//foo/bar:wiz</p>
<p>Bazel支持通过符号链接来寻找子包，除了：</p>
<ol>
<li>那些指向输出目录的子目录的符号链接，例如bazel-bin</li>
<li>包含了名为DONT_FOLLOW_SYMLINKS_WHEN_TRAVERSING_THIS_DIRECTORY_VIA_A_RECURSIVE_TARGET_PATTERN文件的目录</li>
</ol>
<p>指定了
      <span id="crayon-64af8824881a4349304066" class="crayon-syntax crayon-syntax-inline  crayon-theme-gmem-github crayon-theme-gmem-github-inline crayon-font-consolas" style="font-size: 15px !important; line-height: 20px !important;font-size: 15px !important;"><span class="crayon-pre crayon-code" style="font-size: 15px !important; line-height: 20px !important;font-size: 15px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;"><span class="crayon-v">tags</span><span class="crayon-h"> </span><span class="crayon-o">=</span><span class="crayon-h"> </span><span class="crayon-sy">[</span><span class="crayon-s">"manual"</span><span class="crayon-sy">]</span></span></span>的目标必须手工构建，无法通过...、:*、:all等自动构建</p>
<p>常用选项：</p>
<p style="padding-left: 30px;">--loading_phase_threads &nbsp; 加载阶段使用的线程数量，可以防止并发太多导致下载缓慢，进而超时</p>
</td>
</tr>
<tr>
<td class="blog_h3" header-level="3" header-index="12.1.4" header-title="canonicalize-flags">canonicalize-flags</td>
<td>规范化Bazel标记</td>
</tr>
<tr>
<td class="blog_h3" header-level="3" header-index="12.1.5" header-title="clean">clean</td>
<td>清除输出文件，可选的停止服务器</td>
</tr>
<tr>
<td class="blog_h3" header-level="3" header-index="12.1.6" header-title="cquery">cquery</td>
<td>针对post-analysis依赖图查询</td>
</tr>
<tr>
<td class="blog_h3" header-level="3" header-index="12.1.7" header-title="dump">dump</td>
<td>输出Bazel服务器的内部状态</td>
</tr>
<tr>
<td class="blog_h3" header-level="3" header-index="12.1.8" header-title="info">info</td>
<td>输出Bazel服务器的运行时信息</td>
</tr>
<tr>
<td class="blog_h3" header-level="3" header-index="12.1.9" header-title="fetch">fetch</td>
<td>
<p>拉取某个目标的外部依赖</p>
<p>使用
      <span id="crayon-64af8824881a6913556394" class="crayon-syntax crayon-syntax-inline  crayon-theme-gmem-github crayon-theme-gmem-github-inline crayon-font-consolas" style="font-size: 15px !important; line-height: 20px !important;font-size: 15px !important;"><span class="crayon-pre crayon-code" style="font-size: 15px !important; line-height: 20px !important;font-size: 15px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;"><span class="crayon-o">--</span><span class="crayon-v">fetch</span><span class="crayon-o">=</span><span class="crayon-t">false</span></span></span>标记可以禁止在构建时进行自动的外部依赖（本地系统依赖除外）抓取，通过local_repository、new_local_repository声明的“本地”外部存储库，总是会抓取</p>
<p>如果禁用了自动抓取，你需要在以下时机手工抓取：</p>
<ol>
<li>第一次构建之前</li>
<li>每当新增了外部依赖之后</li>
</ol>
<p>示例：</p>
<div>
        <table class="crayon-table" style="">
          <tbody><tr class="crayon-row">
            <td class="crayon-code"><div class="crayon-pre" style="font-size: 15px !important; line-height: 20px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;"><div class="crayon-line" id="crayon-64af8824881a8494773474-1"><span class="crayon-c"># 抓取两个外部依赖</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af8824881a8494773474-2"><span class="crayon-e">bazel </span><span class="crayon-v">fetch</span><span class="crayon-h"> </span><span class="crayon-o">/</span><span class="crayon-o">/</span><span class="crayon-v">foo</span><span class="crayon-o">:</span><span class="crayon-v">bar</span><span class="crayon-h"> </span><span class="crayon-o">/</span><span class="crayon-o">/</span><span class="crayon-v">bar</span><span class="crayon-o">:</span><span class="crayon-v">baz</span></div><div class="crayon-line" id="crayon-64af8824881a8494773474-3"><span class="crayon-c"># 抓取工作空间的全部外部依赖</span></div><div class="crayon-line crayon-striped-line" id="crayon-64af8824881a8494773474-4"><span class="crayon-e">bazel </span><span class="crayon-v">fetch</span><span class="crayon-h"> </span><span class="crayon-o">/</span><span class="crayon-o">/</span><span class="crayon-sy">.</span><span class="crayon-sy">.</span><span class="crayon-sy">.</span></div></div></td>
          </tr>
        </tbody></table>
    </div>

<p><strong><span style="background-color: #c0c0c0;">存储库缓存</span></strong></p>
<p>Bazel会避免反复抓取同一个文件，即使：</p>
<ol>
<li>多个工作空间使用同一外部依赖</li>
<li>外部存储库的定义改变了，但是需要下载的还是那个文件</li>
</ol>
<p>Bazel在本地文件系统维护外部存储库的缓存，默认位置在~/.cache/bazel/_bazel_$USER/cache/repos/v1/。可以使用选项--repository_cache指定不同的缓存位置。缓存可以被所有命名空间、所有Bazel版本共享</p>
<p><strong><span style="background-color: #c0c0c0;">避免下载</span></strong></p>
<p>你可以指定--distdir选项，其值是一个只读的目录，bazel会在目录中寻找文件，而非去网络上下载。匹配方式是URL中的Basename + 文件哈希。如果不指定哈希值，则Bazel不会去--distdir寻找文件</p>
</td>
</tr>
<tr>
<td class="blog_h3" header-level="3" header-index="12.1.10" header-title="mobile-install">mobile-install</td>
<td>在移动设备上安装目标</td>
</tr>
<tr>
<td class="blog_h3" header-level="3" header-index="12.1.11" header-title="query">query</td>
<td>执行依赖图查询</td>
</tr>
<tr>
<td class="blog_h3" header-level="3" header-index="12.1.12" header-title="run">run</td>
<td>运行指定的目标</td>
</tr>
<tr>
<td class="blog_h3" header-level="3" header-index="12.1.13" header-title="shutdown">shutdown</td>
<td>关闭Bazel服务器</td>
</tr>
<tr>
<td class="blog_h3" header-level="3" header-index="12.1.14" header-title="test">test</td>
<td>构建并运行指定的测试目标</td>
</tr>
</tbody>
</table>
