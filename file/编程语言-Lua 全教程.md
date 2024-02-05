
<!--BEGIN_DATA
{
    "create_date": "2017-12-27 19:52", 
    "modify_date": "2017-12-27 19:52", 
    "is_top": "0", 
    "summary": "编程语言 - Lua 全教程", 
    "tags": "Lua", 
    "file_name": "编程语言-Lua 全教程.md"
}
END_DATA-->

#### <p>原文出处：<a href='http://ialloc.org/posts/2017/11/17/programming-in-lua/' target='blank'>编程语言 - Lua 全教程</a></p>

```lua
#!/usr/bin/env lua
print("Hello World!")
```

Lua (LOO-ah) 是一种可嵌入、轻量、快速、功能强大的脚本语言。它支持过程式编程、 面向对象编程、函数式编程、数据驱动编程和数据描述（data description）。

Lua 将简洁的过程式语法和基于关联数组、可扩展语义的数据描述语法结构结合了起来。 Lua 是动态类型的语言，它使用基于寄存器的虚拟机解释和运行字节码（bytecode），并 使用增量垃级回收（incremental garbage collection）机制自动管理内存。这些特点使 得 Lua 很适合用于配置、脚本化和快速构造原型的场景。

Lua 是第一个由第三世界国家（巴西）开发者开发的流行度很高的语言（and the leading scripting language in games）。

Lua 解释器只有 2w+ 多行 ANSI C/C++ 代码， 可执行文件 200+ KB 大小。

下面是几个嵌入了 Lua 解释器，可以使用 Lua 扩展功能的知名应用程序：

  * World of Warcraft
  * Angry Birds
  * Redis
  * Wireshark
  * Wrk
  * Nmap
  * MySQL Workbench
  * VLC
  * [其它工业级应用](https://en.wikipedia.org/wiki/Category:Lua-scriptable_software)

## Lua 版本

Lua 官方于 2011 年发布的 5.2 和 2015 年发布了 5.3 版本，和用户规模很大的 2006 年发布的 5.1 相比，改动很大，在 Lua 语法和 C API 方面都互不兼容。OpenResty 和 LuaJIT 对于这两个最新版本的支持存在难度:

```
https://openresty.org/en/faq.html
Lua 5.2+ are incompatible with Lua 5.1 on both the C API land and the Lua
land (including various language semantics)...Lua 5.2+ are essentially
incompatible different languages.
Supporting Lua 5.2+ requires nontrivial architectural changes in ngx_lua's
basic infrastructure. The most troublesome thing is the quite different
"environments" model in Lua 5.2+. At this point, we would hold back ading
suport for Lua 5.2+ to ngx_lua.
https://www.reddit.com/r/lua/comments/2zutj8/mike_pall_luajit_dislikes_lua_53
Mike Pall (LuaJIT) dislikes Lua 5.3
```

总而言之，Lua 语言像 Python 一样甩开了「向前兼容」的包袱，大跨步向前发展。这对
语言本身来讲，是件好事儿，但是对使用者来讲，短期内是件痛苦的事儿。

由于我们本次学习 Lua 的目的是为 OpenResty 开发做准备，所以，本文概念和示例主要 围绕 Lua 5.1 展示。

## Lua 环境

### 开发工具

  * Vim + Syntastic
  * ZeroBrane Studio
  * Decoda (Windows only)
  * Lua for IntelliJ IDEA
  * Babelua for Visual Studio
  * lua-checker/LuaInspect
  * LuaDoc
  * And more <http://lua-users.org/wiki/LuaIntegratedDevelopmentEnvironments>

### 软件包管理

  * LuaRocks

### 分析和调试

  * `print()`, and `tracing`:
    
    [Wikipedia](https://en.wikipedia.org/wiki/Tracing_(software))
    
	  Tracing involves a specialized use of logging to record information to record information about a program's execution. This information is typically used by programmers for debugging purposes.
	    
	  Logging - error reporting.
	    
	  Tracing - following your program flow and data to find out where the performance bottlenecks are and even more important when an error occurs you have a chance to find out how you did get there. In an ideal world every function would have some tracing enabled with the function duration, passed parameters and how far you did get in your function.

  * **luatrace** - Toolset for tracing/analyzing/profiling script execution and generating detailed reports.

  * **luaprofiler** - Time profiler for the Lua programming language.

  * **StackTracePlus** - Drop-in upgrade to Lua's stack traces which adds local context and improves readability.

  * **MobDebug** - Powerful remote debugger with breakpoints and stack inspection. Used by ZeroBraneStudio.

  * Debug interface `debug` provided by Lua itself.

更多工具参见：<http://lua-users.org/wiki/ProgramAnalysis>

## 基础概念

### 常量和标识符

* 语言关键字
  
```lua
and, break, do, else, elseif, end, false, for, function, if, in, local, nil, not, or, repeat, return, then, true, until, while
```

* 其它标识符

```lua
/ % ^ ##== ~= <= >= < > = ( ) { } [ ] ; : , . .. ... -- ',' is not an operator in Lua, but only a delimiter
```

* 常量字符串使用 `'` 或 `"` 分隔，其中可以使用类似 C 语言的转义字符序列：    

```lua
\a, \b, \f, \n, \r, \t, \v, \\, \", \ddd, \0
```

* 作为惯例，Lua 把以 `_` 字符开始全部使用大写字母的变量名，保留为内部全局变量；  

```lua
_VERSION
```

* 常量字符串可以使用 _long brackets_ 语法表示：
  * `[[` 为 _opening bracket_ ， `]]` 为 _closing bracket_ 。可以使用 `=` 表示层级，例如， `[[` 表示第 0 层级， `[====[` 表示第 4 层级；
  * 若其中含有转义序列，该转义序列不会被 Lua 转义；
  * _opening brackets_ 后面紧跟的换行会被 Lua 忽略；
  * _opening brackets_ 会和第一次出现的同一层级的 _closing brackets_ 匹配；

    ```lua
    a = [=[
    abc
    xyz]=]
    ```

* Lua 使用双精度浮点数表示数字常量，数据常量可以使用十六进制或科学计数法： 

```lua
3, 3.0, 3.1416, 314.16e-2, 0xff, 0x56
```

* Lua 注释有短注释和长注释两种注释方式：

```lua
-- short comment
--[[
    this is a very loooooooooooooong
    comment
]]
--[=[
    Same scheme used with long string.
]=]
```

### 变量和数据类型

* Lua 是一个动态类型语言，也就是说：

  * 「变量」没有类型信息，但是「值」有类型信息；
  * 代码中没有类型定义语句，类型信息由「值」携带；
  * 所有的「值」都是 first-class 的，它们可以存储在变量中、作为参数传递给其它函 数或者作为函数的返回值；

* Lua 提供了 8 种基础类型：

  * `nil` - 此类型下定义的值只有 `nil` ，它的主要属性就是：和其它值不一 样。通常， `nil` 用在其它有意义的值缺失的场景。
  * `boolean` - 此类型下定义的值有 `false` 和 `true` 。 在 Lua 的条件 表达式里， 除了 `nil` 和 `false` 为「假值」外，其它类型都是「真值」（比 如， `0` 和 `''` 在 Lua 中都是 「真」值）。
  * `number` - Lua 默认使用双精度浮点型存储该类型的值。
  * `string` - 此类型的值可以由任何 8-bit 字符组成。Lua 在内存中为相同的字符 串保留一份数据（ _interning_ ），同时，Lua 不允许对字符串常量进行修改 （immutable）。
  * `function` - 此类型的值是使用 Lua 或者 C 编写的函数。
  * `userdata` - 此类型的值是 C 语言数据，从 Lua 的角度看，这些值对应一块无 预定义行为的裸内存。Lua 不允许使用 Lua 代码创建或者修改 `userdata` ，但 是允许使用 C API 实现这样的功能。另外，用户可以为 `userdata` 设定 _metatable_ ，定义更多可以在它上面执行的操作。
  * `thread` - 此类型的值是 Lua 线程，Lua 通过它实现协程功能。
  * `table` - 此类型的值是关联数组（associative array），该类型有数组部分和字 典部分组成。数组部分保存索引为整数，并且从 1 开始连续的数据；字典部分保存剩 余其它数据（包括索引是整数，但是不在 `[1, #table]` 的数据）。

    * `table` 是 Lua 提供的仅有的数据结构构造机制：它可以用来表示 _array_, _symbol table_, _set_, _record_, _graph_, _tree_ 等等数据结构；
    * `nil` 不能作用 `table` 的索引（ `error: table index is nil` ）；
    * `nil` 不是有效的 `table` 元素值，如果将 `nil` 赋值给某个元素时， 相当于从 `table` 中删除了该元素；
    * Lua 提供了下面几种创建 `table` 的方法：
      
      ```lua
      -- A field of the form `name = exp` is equivalent to
      -- `["name"] = exp`; A field of form `exp` is equivalent to
      -- `[i] = exp`, where `i` are consecutive numerical integers,
      -- starting with 1.
      a = { ["name"]= "dhb"; "male", [10]= 25, addr= "beijing",
          job= "code monkey"; }
      -- or
      a = {}
      a["name"] = "dhb"
      a[1] = "male"
      a[10] = 25
      a["addr"] = "beijing"
      a.job = "code monkey"
      a.removed = nil       -- this field will be removed by gc
      ```

 * Lua 为 `a["name"]` 的使用形式提供了语法糖： `a.name` ；

* `table`, `function`, `thread` 和 `userdata` 类型的值在赋值、参数 传递、函数返回值等操作中，使用对它们引用，而非拷贝；
* 可以使用 `type()` 函数得到描述值类型的字符串；
* 在运行时，Lua 会自动根据上下文对 `string` 和 `number` 类型值互相转换 类型（作为强类型语言，Lua 只支持如下隐式转换）：

 * 在 **算术运算** 中，将 `string` 类型转换为 `number` 类型；
    ```lua
    10 + "10"
    ```

 * 当 `number` 类型用于需要 `string` 类型 (where a string is expected) 参与的场合时，将 `number` 类型转换为 `string`；
    ```lua
    -- valid
    10 .. " boxes"
    -- invalid
    10 == "10"
    ```
* Lua 语言有三种类型的变量：全局变量，局部变量和 `table` 字段：

  * 变量默认是全局变量 [3]；
  * 函数参数是局部变量；
  * 使用 `local` 定义的变量是局部变量，并且 Lua 为其使用 词法作用域（ lexically scoped, or statically scoped） [1]；
  
      ```lua
      function foo()
          function b() print(type(a), a) end
          local a = 10
          function f() print(type(a), a) end
          b(); f()
      end
      foo()
      ```
    * Local variables have their scope limited to the _block_ where they are declared: The scope of a local variable begins at the first statement after its declaration and lasts until the last non-void statement of the innermost _block_ that includes the declaration.
  
        ```lua
        -- example.lua
        local a = 10
        b = 10
        print(_G.g, _G.h)     -- nil, 10
        ```

    * A _block_ is a list of statements; syntactically, a block is the same as a chunk:
      
        ```lua
        A chunk is an outermost block which you feed to "load()"
        -- Roberto
        ```

    * Lua handles a chunk as the body of an anonymous function with a variable number of arguments. As such, chunks can define local variables, receive arguments, and return values.
    * Explicit blocks are useful to control the scope of variable declarations. Explicit blocks are sometimes used to add a `return` or `break` statement in the middle of another block.
  
        ```lua
        -- explicit block
        do
          local a = 10
          print(type(a), a)
        end
        print(type(a), a)
        
        -- control structure
        if true then
          local a = 10
          print(type(a), a)
        end
        print(type(a), a)
        ```

* 在局部变量作用域内定义的内部函数可以使用该局部变量，对内部函数来说，这个 局部变量被称为 _upvalue_ ，或者 _external local variable_ ；
  
  ```lua
  do
    local a = 10
    function bar()
      print(a)      -- `a` is called upvalue for `bar`
    end
  end
  ```

* 每次使用 `local` 语句，都会创建一个新的局部变量；
  
  ```lua
  a = {}                -- global variable
  local x = 20
  for i = 1, 10 do
    	local y = 0
    	a[i] = function () y = y + 1; return x + y end
  end
  ```

* 未赋值的变量默认值是 `nil` ，所以，变量最好在使用前进行定义（下文 「惯用法」一节提供了几种检测代码里使用未定义变量的方式）；

  ```lua
  -- error in Lua
  function foo()
      local function bar() zog() end
      local function zog() print "Zog!" end
    	bar()
  end

  ##valid in Python
  def foo():
      def bar():
        zog()
      def zog():
        print "Zog!"
  bar()
  ```

* Lua 使用 `table` 保存所有的全局变量，这个 `table` 被称为 _environment table_ ，或 _environment_ 。

    * 每个函数都拥有一份对 _environment table_ 的引用，这样一来，在函数中对全 局变量的查找都通过它完成；
    * 函数创建时，它会从创建者继承 _environment_ ；
    * 在函数中，可以通过 `getfenv()` 显式获取对它使用的 _environment_ 的引 用；也可以通过 `setfenv()` 使用新的 _environment_ 替换原来的 _environment_ ；

### 表达式（expression）

  * 运算符：arithmetic operator, relational operators, logical operators, concatenation operator, unary minus, unary `not`, unary _length_ operator.
    * 逻辑 `not` 运算符的结果是 `true` 或者 `false` ；逻辑 `and` 和 `or` 运算符具有「短路」特征，它们的运算结果是第一个操作数或者第二个操作 数；
      
      ```lua
      a = 10 and nil or 11
      ```
      
    * 长度运算符 `#` 可以用于获取常量字符串的字节个数，和 `table` 数组部分 元素的个数：
      ```lua
      #"abcd"                     -- 4
      #{1, 2, 3}                  -- 3
      #{[0]= 0, [1]= 1, [2]= 2}   -- ?
      #{[2]= 2, [3]= 3, [4]= 4}   -- ?
      #{[1]= 1, name= "dhb"}      -- ?
      ```
      
    * 除了 `..` 和 `^` 是右结合（right associative）外，其它运算符都是左 结合（left associative）；
      
      ```lua
      From Wikipedia:
      The associativity of an operator is a property that determines how operators of the same precedence are grouped in the absence of parentheses. If an operand is both preceded and followed by operators, and those operators have equal precedence, then the operand may be used as input to two different operations. The choice of which operations to apply the operand to, is determined by the "associativity" of the operators.
	  ```
	    * Left-associative - the operations are grouped from the left.
        * Right-associative - the operations are grouped from the right.
	
	* 运算符优先级参见 [2]
    ```lua
    6 + 2 - 7 ^ 2 ^ 2          -- ?
    ```
    
    * Lua 提供了专用的字符串连接操作符 `..` ；
      
      ```lua
      Overloading `+` to mean string concatenation is a long tradition. But concatenation is not addition, and it is useful to keep the concepts separate, In Lua, strings can convert into numbers when appropriate (e.g 10 + "20") and numbers can convert into strings (e.g 10 ..  "hello"). Having separate operators means that there is no confusion, as famously happens in JavaScript.
      ```
    
  * 表达式：常量表达式，算术表达式，关系表达式，逻辑表达式，连接表达式，Vararg 表达式，函数调用表达式，函数声明， `table` 构造表达式等等；
    
    * 几个关系表达式的例子：

      ```lua
      local t1, t2 = {}, {}
      print(t1 == t2)         -- false. Tables are never compared "element by
      -- element".
      local s1, s2 = "abc", "abc"
      print(s1 == s2)         -- true. There is only ever one instance of any
      						-- particular string stored in memory, so
      						-- comparison is very quick (interning). And
      						-- strings are "immutable", there is no way in
      						-- Lua to modify the contents of a string
      			          	-- directly
      ```

    * 函数定义是一种可执行的表达式，它的返回结果是 `function` 类型的值：
      
      ```lua
      function f() body end               -- equivalent to
      f = function () body end
      function a.b.c.f() body end         -- equivalent to
      a.b.c.f = function () body end
      local function f() body end         -- equivalent to
      local f; f = function () body end
      ```

      * 函数定义可以通过 _varargs_ 表达式支持可变参数。_varargs_ 表达式出现在函数 参数列表的最后，它会接收多出的参数，以便在函数体中使用。由于 _varargs_ 也 会返回多个值，Lua 对它的返回值的处理方式和函数调用类似。
        
        ```lua
        function foo(...)
            -- The expression `...` behaves like a multiple return function
            -- returning all varargs of the current function.
            local a, b, c = ...
            -- ...
            -- The expression `{...}` results in a array with all collected
            -- arguments.
            for i, v in ipairs{...} do
                -- ...
            end
            -- ...
            -- Whe the varargs list may contain valid `nil`s, we can use the
            -- `select` function to get specific arguments.
            local args = {n= select("#", ...), ...}
            for i = 1, args.n do
                print(args[i])
            end
        end
        ```

    * 函数调用表达式语法和其它语言类似，参数中的表达式在函数调用发生之前求值。 同时，Lua 在此基础上提供了两个语法糖：
    * 
      * `v:name(args)` 是 `v.name(v, args)` 的语法糖，同时，也隐式指明， `v` 对象会被传递给 `name` 函数的第一个参数 `self` ；
      * 如果参数只有一个并且其类型是 `string` 时，可以使用 `f"string"` 的形式调 用函数；如果参数只有一个并且其类型是 `table` 时，可以使用 `f{fields}` 的形式调用函数；

### 语句（statement）

* 赋值语句
  
  ```lua
  i = 3
  i, a[i] = i + 1, 20
  x, y, z = y, z, x
  -- and cannot do following because it's a statement
  a = b = 1
  if (a = 1) then ... end
  ```

  * Lua 会将赋值语句两侧包含的表达式求值后，才真正进行赋值操作；
  
  * 在赋值语句执行前，Lua 会根据左侧的变量数据调整右侧的值列表：如果右侧的值 个数大于左侧的变量个数，超出的部分会被丢弃；如果右侧的值个数小于左侧的变 量个数，Lua 会使用 `nil` 补充值列表；如果右侧最后一个为函数调用，函数 所有的返回值都被补充到值列表中；
    
    ```lua
    -- in Lua
    x, y = {1, 2}       -- maybe `unpack` is needed
    
    ##in Python
    x, y = (1, 2)
    ```

  * 函数调用时的参数值传递规则和赋值语句一致；而对于函数返回值的处理，Lua 还 有如下规则：
  
    * 如果函数调用作用单独语句使用时，Lua 默认丢弃所有返回值；
      
      ```lua  
  		foo()
      ```

    * `(` 和 `)` 括起起来的表达式，包括函数调用，Lua 保留第一个返回值作为 整个表达式的值；

      ```lua
  		function foo() return 1, 2, 3 end
  		x, y, z = (foo())
      ```

    * 函数调用作为表达式的一部分使用时，Lua 保留其第一个返回值；
      
      ```lua
			function foo() return 1, 2, 3 end
			print(foo())
			print(1 + foo())
      ```

    * 除了上面描述过的，函数调用出现在赋值语句值列表的最后位置或函数调用参数 列表的最后位值，Lua 将其所有返回值补充到值列表外，在 `table` 构造列表 和 `return` 语句返回值列表的最后位置，Lua 都会使用它的所有返回值；

      ```lua   
  		function foo() return 1, 2, 3 end
  		t1 = {foo()}
  		t2 = {4, foo()}
  		t3 = {foo(), 5}
      ```

    * 和 Python 的区别
      
      ```lua
      -- in Lua
      x, y = foo()
         
      ##in Python
      x, y = foo()      ##a tuple and implicit unpack involved
      ```

* 控制结构
  
  ```lua
  while exp do block end
  repeat block until exp
  
  if exp then block {elseif exp then block} [else block] end
  -- numeric ``for``
  for var = exp, exp [, exp] do block end
  -- generic ``for``
  for var [, var...] in explist do block end
  -- ``explist`` is evaluated only once. Its results are an *iterator*
  -- function, a *state*, and an initial value for the first *iterator*
  -- variable
  break
  return
  -- but no ``continue``
  ```

* 其它语句
  
  ```lua
  -- Function calls as statements
  foo()
  -- Local declaration
  local var
  ```

## 惯用法

  The Lua way.

* 内存在没有任何引用时，会自垃圾回收机制自动释放，一般情况下，释放时机由 Lua 解 释器选择。开发者可以通过调用 `collectgarbage("collect")` 强制 Lua 解 释器进行垃圾回收，但是，通常需要连续调用两次；

* 如果想要记录稀疏数组的元素个数，需要使用者自己通过计数器保存和维护元素个数；
  
  ```lua
  local t = {counter= 0}
  t[2] = "dhb"
  t.counter = t.counter + 1
  ```

* Lua 函数的错误信息一般通过返回值返回给调用者，通常做法是：函数的第一个返回值 如果是 `nil` 或者 `false` 时，第二个返回值就是实际的错误信息；

* 在 Lua 中使用 `pcall/xpcall` 调用可以实现其它语言中 `try/catch` 相同的作 用，而 `error` 就是其它语言中用于抛出异常的 `throw` 或者 `raise` ；

  ```lua
  local ok, err = pcall(function()
  t.alpha = 2.0    -- will throw an error if `t` is nil or not a table
  end)
  if not ok then
      print(err)
  end
  ```

* 回调函数:
  
  ```lua
  Callback function is one of the most powerful programming paradigms because
  it enables a general purpose function to do very specific things.
  ```

* Lua 函数定义和函数调用都不支持「有名参数」（named argument），如果有类似的需 要时，可以使用 `table` 保存参数，然后将该 `table` 作为函数的唯一参数；
  
  ```lua
  function foo(args)
      local name = args.name or "anonymous"
      local os = args.os or "Linux"
      local email = args.os or name .. "@" .. os
      ...
  end
  foo{name= "bill", os="windows"}
  ```

* 所有的全局变量都存放于名为 `_G` 的 `table` 中；
  
  ```lua
  a = 10
  print(a, _G.a)
  _G._G == _G
  ```

* 在表示常量字符串时，单线号 `'` 或双引号 `"` 没有任何区别，字符串中都可以 使用转义序列表示特殊字符；

* 打印 `table`
  
  ```lua
  --[[
  This is not very efficient for big tables because of all the string
  concatenations involved, and will freak if you have *circular references
  or 'cycles'
  ]]
  function dumptable(o)
     if type(o) == 'table' then
         local s = "{"
         for k, v in pairs(o) do
             if type(k) ~= 'number' then k = '"' .. k .. '"' end
             s = s .. '[' .. k .. '] = ' .. dumptable(v) .. ','
         end
         return s .. '}'
     else
         return tostring(o)
     end
  end
  -- More options: http://lua-users.org/wiki/TableSerialization
  ```

* 读取文件

  * 使用 `io.lines` 函数读取文件。该函数自动打开和关闭文件：
    
    ```lua
  	for line in io.lines "myfile" do
  	    ...
  	end
    ```

  * 使用 `io.open` 和 `io.close` 显式打开和关闭文件：
    
    ```lua
    local f, err = io.open("myfile")
  	if not f then return print(err) end
  	for line in f:lines() do
  	    ...
  	end
  	f:close()
  	-- alternative reading
  	local line = f:read '*l'
  	while line do
  	    ...
  	    line = f:read '*l'
  	end
  	-- to read the whole file
  	local s = f:read '*a'
    ```
  
* 一些字符串处理的例子 [5]

* 在运行时，Lua 默认会从全局环境或者模块环境中查找未知变量，如果该变量未定义， Lua 将 `nil` 作为它的值返回。在 Lua 中 `nil` 也是合法的变量值，所以，在 运行时，很难区分某个变量的值是 `nil` 还是它未被定义。这种机制对于变量名拼 写错误的情况不是好消息，在 Lua 中，有以下惯用方式用来检测代码中的未定 义（undeclared variables）变量：
  
  > <http://lua-users.org/wiki/DetectingUndefinedVariables>
  >
  > In Lua programs, typos in variable names can be hard to spot because, in general, Lua will not complain that a variable is undefined...If a variable if not recognized by Lua as a local variable (e.g. by static declaration of the variable using a "local" keyword or function parameter definition), the variable is instead intepreted as a global variable...Whether a global varaible is defined is not as easy to determine or describe.

  * 运行时检测
  
    * 通过重载当前函数环境（下面的实现直接针对全局环境）的 _metatable_ 的 `__index` 和 `__newindex` 字段，可以在运行时检测全局未定义变量的读 写操作，并抛出运行时错误。这个方式的缺点是：只能用于运行时；无法检测到 运行时未执行（未覆盖）到的代码中的未定义变量引用；
  
      * `strict` module in the Lua distribution (`etc/strict.lua`);
      * [LuaStrict](http://thomaslauer.com/comp/LuaStrict) by ThomasLauer for an extension of the `strict` approach;

    * Niklas Frykholm 实现了一个用于强制局部变量定义的模块。它要求所有变量必须 使用 `local` 定义为局部变量了未定的变量。这个实现相当于上面方式的扩展 版本，它的用法更优雅，侵入性更低；
      
      ```lua
    	--===================================================
    	--=  Niklas Frykholm
    	-- basically if user tries to create global variable
    	-- the system will not let them!!
    	-- call GLOBAL_lock(_G)
    	--
    	--===================================================
    	function GLOBAL_lock(t)
    	  local mt = getmetatable(t) or {}
    	  mt.__newindex = lock_new_index
    	  setmetatable(t, mt)
    	end
      
    	--===================================================
    	-- call GLOBAL_unlock(_G)
    	-- to change things back to normal.
    	--===================================================
    	function GLOBAL_unlock(t)
    	  local mt = getmetatable(t) or {}
    	  mt.__newindex = unlock_new_index
    	  setmetatable(t, mt)
    	end
      
    	function lock_new_index(t, k, v)
    	  if (k~="_" and string.sub(k,1,2) ~= "__") then
    	    GLOBAL_unlock(_G)
    	    error("GLOBALS are locked -- " .. k ..
    	          " must be declared local or prefix with '__' for globals.", 2)
    	  else
    	    rawset(t, k, v)
    	  end
    	end
      
    	function unlock_new_index(t, k, v)
    	  rawset(t, k, v)
    	end
    	-- Basically anytime you call ``GLOBAL_lock(_G)`` somewhere in your
    	-- code, from that point onwards anytime you try to use a variable
    	-- without explicitly declaring it as 'local', Lua will raise an error.
      ```

  * 静态分析检测 - 除了运行时动态检测，我们还可以在代码运行之前，使用静态分析的方 式检测未定义变量：
  
    * 使用 `luac`

      ```lua 
			##This lists all gets and sets to global variables (both defined and
			##undefined ones).
			% luac -p -l myprogram.lua | grep ETGLOBAL
      ```

    * 其它工具
  
      * [LuaLint](http://lua-users.org/wiki/LuaLint)
      * [lglob](https://github.com/stevedonovan/lglob)
      * [globals-lua](https://github.com/hjelmeland/globals)
      * [LuaInspect](http://lua-users.org/wiki/LuaInspect)
      * [LuaChecker](https://github.com/rjpower/lua-checker)
      * IDEs, etc.

  * 运行时/静态分析混合方式

* `ipairs` 可以用来按索引从小到大的顺序遍历 `table` 中数组部分； `pairs` 可以遍历 `table` 中的所有元素，但是输出结果是无序的；

* 如果需要为常量字符调用字符串处理函数，可以使用 `("string"):method(...)` 的 形式：
  
  ```lua
  ("%s=%d"):format("hello", 42)  -- is equivalent to
  string.format("%s=%d", "hello", 42)
  ```

## 高级特性

### 高级语法结构

#### 元表（metatable）

​    Every value in Lua can have a *metatable*.

Lua 通过 _metatable_ 定义数据（original value）在某些特殊操作下（算术运算、大小比较、连接操作、长度操作和索引操作等）的行为。

我们将 _metatable_ 支持的具体操作称为 _event_ ，操作对应的行为由 _metamethod_ 体现。 _metatable_ 实际上是一个普通的 `table` 。 _event_ 名添加 `__` 下 划线前缀后，作为 _metatable_ 的索引（key），索引对应的值（value）就是 _metamethod_ 。 比如，使用非数字类型的值作为算术加 `+` 的操作数时，Lua 会使用 _metatable_ 中 `__add` 对应的 _metamethod_ 完成算术加运算。

_metatable_ 提供的主要 _event_ 有：

  * `add` - the `+` operation;

  * `sub` - the `-` operation;

  * `mul` - the `*` operation;

  * `div` - the `/` operation;

  * `mod` - the `%` operation;

  * `pow` - the `^` operation;

  * `unm` - the unary `-` operation;

  * `concat` - the `..` operation;

  * `len` - the `#` operation;

  * `eq` - the `==` operation;

    * 可以通过重载 _metatable_ 的 `__eq` 方法重新定义对象的「相等性」规则， 但是需要注意的是， `__eq` 要求参与比较的两个操作数有相同的类型并使用相同 的 `__eq` _metamethod_ ；

  * `lt` - the `<` operation;

  * `le` - the `<=` operation;

  * `index` - The indexing access `table[key]`;
    
    ```lua
    ``__index`` fires when Lua cannot find a key inside a table. ``__index``
    can be set to either a table or to a function; objects are often
    implemented by setting ``__index`` to be the metatable itself, and by
    putting the methods in the metatable. A naive ``Set`` class would put
    some methods in the metatable and store the elements of the set as keys
    in the object itself.
    ```

    * `__index` 的 _metamethod_ 可以是 `table` 或者函数

      ```lua
      -- simulation
      function gettable_event(table, key)
         local h
         if type(table) == "table" then
             local v = rawget(table, key)
             if v ~= nil then return v end
             h = metatable(table).__index
             if h == nil then return nil end
         else
             h = metatable(table).__index
             if h == nil then error(...) end
         end
         if type(h) == "function" then
             return (h(table, key))  -- call the handler
         else
             return h[key]           -- or repeat operation on it
         end
      end
      ```

  * `newindex` - the indexing assignment `table[key] = value`;

  * `call` - called when Lua calls a value;
    
    ```lua
    function function_event(func, ...)
        if type(func) == "function" then
            return func(...) -- primitive call
        else
            local h = metatable(func).__call
            if h then
                return h(func, ...)
            else
                error(...)
            end
        end
    end
    ```

在 Lua 代码中，可以为每个 `table` 和 `userdata` 设置不同的 _metatable_ ， 而其它 6 种数据类型每种类型的值使用相同的 _metatable_ 。在 Lua 代码中，只能 设置和修改 `table` 类型值的 _metatable_，其它类型的 _metatable_ 可以使 用 C API 修改。

`userdata` 由 C API `lua_newuserdata` 创建，它和 `malloc` 创建的内存块有 所不同： `userdata` 占用的内存会被垃圾回收器回收； 可以为 `userdata` 设置 _metatable_ ，定制它的行为。 `userdata` 只支持两种 _event_ ：`__len` 和 `__gc` ，其中， `__gc` 的 _metamethod_ 由垃圾回收环节，由垃圾回收器调用。比如，标准库提供的 `file` 类型的对象，它的 `__gc` _metamethod_ 负责关闭底层文 件句柄。

另外， _metatable_ 可以使用 `__mode` _event_ 将 `table` 定义为 _weak table_ ：

>   To understand weak tables, you need to understand a common problem with garbage collection. The collector must be conservative as possible, so cannot make any assumptions about data; it is not allowed to be pyshic. As soon as objects are kept in a table, they are considered referenced and will not be collected as long as that table is referenced.
>   
>   Objects referenced by a weak table will be collected if there is no other reference to them. Putting a value in a table with weak values is effect telling the garbage collector that this is not an important reference and can be safed collected.
> 
>    A weak table can have weak keys, weak values, or both. A table with weak keys allows the collection of its keys, but prevents the collection of its value. A table with both weak keys and weak values allows the collection of both keys and values. In any case, if either key or the value is collected, the whole pair is removed from the table.

#### 环境（environment）

**environment** 是除了 _metatable_ 外另外一种可以和 `thread` ， `function` ， `userdata` 类型的值相关联的 `table` 。 _environment_ 相当于 命名空间，对象通过它查找可以访问的变量。

对象间可以共享同一个 _environment_ ：

  * 和 `thread` 关联的 _environment_ 称为 _全局 enironment_ ，它们是该线程创建 的其它子 `thread` 和非嵌套 `function` 的默认 _enironment_ ；
  * 和 Lua `function` 关联的 _environment_ 是该 `function` 创建的嵌套 `function` 的默认 _environment_ ；
  * 和 C `function` 关联的 _environment_ 只能在 C 代码中访问，它也会作为该函 数中创建的 `userdata` 的默认 _environment_ ；
  * 和 `userdata` 关联的 _environment_ 对 Lua 代码没有特殊含义，它只是一种为 `userdata` 附带数据的较为方便的方式；

Lua 代码中可以使用 `getfenv` 和 `setfenv` 操作 Lua `function` 和 正在运行的 `thread` 的 _environment_ , 而 C `function` ， `userdata` 和其 它 `thread` 的 _environment_ 只能使用 C API 操作。

#### 闭包（closure）

```lua
function count()
    local i = 0
    return function() i = i + 1 return i end
end

local counter = count()
print(counter())
print(counter())

-- partial function
function bind(val, f)
      return function(...)
              return f(val, ...)
      end
end

prt = bind("hello", print)
prt(10, 20)
```

#### 协程（coroutine）

Lua 原生支持协程，使用 `coroutine` 类型表示。Lua 协程代表有独立执行流程的线 程。协程由 Lua 解释器调度执行，一个协程显式让出执行权后，其它协程才会被调度执 行。

  * `coroutine.create` - 创建协程。该函数接收 `function` 类型参数，作为新 协程的主函数；
  * `coroutine.resume` - 恢复协程执行。对新创建的协程调用该函数后，协程才真正开 始运行， 此时， `coroutine.resume` 的参数会用做协程主函数的参数。协程会一直 运行，直到它调用 `coroutine.yield` 主动让出执行权。 `coroutine.resume` 函 数在协程主函数执行完毕、抛出异常或者主动让出主动权后才会返回：
    * 协程主函数正常退出时， `coroutine.resume` 返回 `true` 和主函数的返回 值；
    * 协程主函数异常退出时， `coroutine.resume` 返回 `false` 和错误信息；
    * 协程调用了 `coroutine.yield` 让出执行权时， `coroutine.resume` 返回 `true` 和 `coroutine.yield` 的调用参数；
  * `coroutine.yield` - 协程让出执行权。使用 `coroutine.resume` 可以恢复主动 让出执行权的协程，从上次中断的地方继续往下执行，此时， `coroutine.resume` 的参数会作为 `coroutine.yield` 的返回值使用。
  * `coroutine.wrap` - 创建协程的另一种方式。这个调用返回一个函数，调用该函数就 相当于显式调用 `coroutine.resume` 。这个函数和 `coroutine.resume` 的区别 是，协程里抛出异常时， 这个函数会将异常再次投递给函数调用者（所以， `coroutine.resume` 函数用来表示协程执行是否成功的第一个返回值，也会被 `coroutine.wrap` 忽略）。
  * `coroutine.running()` - 返回处于运行状态的协程。如果调用者是 _main thread_ 时，它会返回 `nil` ；
  * `coroutine.status()` - 获取协程当前状态，返回值是字符串。协程的状态有： `running`, `suspended`, `normal`, `dead` 。

### 代码组织

#### 模块（module）

Lua 的模块和其它语言作用类似，用于将一组功能相似的函数和常量存放一起，方便用户 共享代码。

> <Programming in Lua 2nd>
> From the user point of view, a *module* is a library that can be loaded
> through ``require`` and that defines one single global name containing a
> table. Everything that the module exports, such as functions and
> constants，it defines inside this table, which works as a namespace. A
> well-behaved module also arrange for ``require`` to return this table.

Lua 语言实现提供了诸如 `math`, `io`, `string` 等等的标准模块，用户可以在 代码中直接使用这些模块提供的功能。同时，Lua 也给用户提供了实现自定义模块的机制 和方法，用户可以使用 Lua 代码或者 C API 开发自定义模块。

##### 定义模块

通常有如下两种使用 Lua 代码定义模块的方法：

  * Lua 5.1 提供的 `module()` 简化了 Lua 标准模块的创建流程。
    
    ``module(name, ...)`` creates a table and sets it as the value of the global ``name`` and the value of ``package.loaded[name]``, so that ``require`` returns it.
    
    * `module()` 函数实际上做了如下几件工作 [4]：
      
      ```lua
			-- testm.lua (somewhere on the Lua path)
			local print = print
			module("testm")
			function export1(s)
			    print(s)
			end
			function export2(s)
			    export1(s)
			end
			-- muser.lua
			local testm = require("testm")
			testm.export2("text")
      ```

      1. 首先， `module` 为其后的函数构造一个 `table` ，这个 `table` 会被 `require` 作为返回值返回给调用者；
      2. 其次，将该 `table` 设为这些函数的 _envrionment_ ：这些该模块内部的函数 调用彼此时，就不需要使用 `testm` 作为前缀；同时，全局环境被该环境覆盖；
      3. 另外，如果使用 `package.seeall` 作为 `module` 的参数时， `module` 将该 `table` 的 _metatable_ 的 `__index` 成员设置为全局环境 `_G` ， 此时该模块中定义的函数就可以访问全局环境的变量或者函数了；
      4. 设置全局变量 `testm` ，的值为新创建的 `table` ；
      5. 设置 `package.loaded["testm"]` 的值为新创建的 `table` ；
    * 如果为 `module` 使用 _varargs_ 表达式，即 `module(...)` 的形式时，Lua 会使用模块所在的文件名，作为模块名，此时模块文件可以方便的移动位置；

    * Lua 5.2+ 不再建议使用 `module` 函数创建模块的方式，它有几个为人所诟病的地 方：

      * `package.seeall` 参数将全局环境暴露在模块环境里，用户可以通过模块来访 问全局环境，比如 `testm.io` ，造成 **leaky encapsulation** 问题；

      * `module` 函数会将它创建的 `table` 放到全局环境中；同时，它会还会自动 向全局环境导入该模块的依赖模块；
            
        > module "hello.world" creates a table ``hello`` (if not already present) and ``world`` as a table within that. If ``hello.world`` requires ``fred`` then ``fred`` becomes automatically available to all users of ``hello.world``, who may come to depend on this implementation detail and get confused if it changed.
        
  * Lua 5.2 建议使用如下方式（Lua 5.1 也支持该方式）创建模块：
    
    ```lua
		-- mod.lua
		local M = {}
		function M.answer()
		    return 42
		end
		function M.show()
		    print (M.answer())
		end
		return M
    ```

##### 使用模块

Lua 提供的内建模块会解释器预加载到全局环境里，在 Lua 代码中可以直接使用或者通 过全局环境引用。

```lua
-- main.lua
for line in io.lines "myfile" do
    ...
end
-- or
for line in _G.io.lines "myfile" do
  ...
end
```

而用户自定义的模块，在使用前需要通过 `require` 函数加载到代码块可以直接访问的 _environment_ 中。

使用 `module` 实现的模块在加载时，会将模块放到全局环境 `_G` 中，加载后的模块 像内建模块一样可以直接调用。

```lua
-- main.lua
require "socket"
socket.connect(...)
```

或者，

```lua
-- main.lua
local socklib = require "socket"
socklib.connect(...)
```

而上面提到的 Lua 5.2 的方法实现的模块，不会在全局环境定义变量。使用这类模块时， 只能通过 `require` 使用该模块：

```lua
-- main.lua
local mymod = require "mymod"
mymod.do_something()
```

总结下来，模块的使用建议如下：

> The ``require "name"`` syntax was the one introduced in Lua 5.1; This call
> does not always return the module, but it was expected a global would be
> created with the name of the library (so, you now have a ``_G.name`` to use
> the library with). In new code, you should use ``local name = require
> "name"`` syntax; it works in the vast majority of cases, but if you're
> working with some older modules. They may not support it, and you'll have
> to just use ``require "module"``.

##### 模块查找

`require` 函数负责查找和加载模块，这个过程大致步骤如下（以 `require "testm"` 为例）：

  1. 根据 `package.preload["testm"]` 的值，判断 `testm` 是否己经加载过：如果 该模块已经加载过， `require` 将 `package.preload["testm"]` 的值返回；如 果该模块未加载过，继续第 2 步；
  2. 逐个调用 `package.loaders` 设置的 _searcher_ 函数，选择一个可以用于加载 `testm` 的 _loader_ 。Lua 默认提供了 4 个 _searcher_ ：

    * A searcher simply looks for a loader in the `package.preload` table.
    * A searcher looks for a loader as a Lua library using `package.path`.
    * A searcher looks for a loader as a C library, using `package.cpath`.
    * A searcher searches the C path for a library for the root name of the given module.

  3. 调用 _loader_ 加载和执行模块代码。如果 _loader_ 有返回值， `require` 将这个返回值赋与 `package.preload["testm"]` ；如果 _loader_ 没有返回 值， `require` 将 `package.loaded["testm"]` 赋值为 `true` ；
  4. `require` 将 `package.loaded["testm"]` 的值返回给调用者；

上述流程的模拟代码如下：

```lua
function require(name)
    if not package.loaded[name] then
        local loader = findloader(name)
        if loader == nil then
            error("unable to load module " .. name)
        end
        package.loaded[name] = true
        local res = loader(name)
        if res ~= nil then
            package.loaded[name] = res
        end
    end
    return package.loaded[name]
end
```

从上面的描述可以看到， `require` 根据 `package.path` 中设置的路径查找 Lua 模块，根据 `package.cpath`中设置的路径模式查找 C 模块。路径模式是包含了 `?` 和 `;` 的字符串，`;` 用于分隔文件系统的路径， `?` 会被 `require` 替换成模块名。例如：

```lua
-- package.path
./?.lua;/usr/share/lua/5.1/?.lua;/usr/share/lua/5.1/?/init.lua
```

执行 `require("testm")` 时， `require` 会依次使用下面路径查找模块代码：

```lua
./testm.lua
/usr/share/lua/5.1/testm.lua
/usr/share/lua/5.1/testm/init.lua
```

#### 包（package）

Lua 允行将模块按照层级结构组织起来，层级之间使用 `.` 分隔。例如， 模块 `mod.sub` 是模块 `mod` 的子模块。 `package` 就是这样按此形式组织起来的 模块的集合，同时，它也是 Lua 中用于代码分发的单元。

和模块类似，例如，使用 `require` 查找和加载子模块 `a.b.c` 时， `require` 通过 `package.loaded["a.b.c"]` 的值判断该子模块是否已经被加载过。和模块不同 的是，如果子模块未被加载过， `require` 先将 `.` 转换成操作系统路径分隔符， 比如，类 UNIX 平台上， `a.b.c` 被转换成 `a/b/c` ，然后使用 `a/b/c` 替换 `package.path` 和 `package.cpath` 中的 `?` 后，查找子模块文件。

`module` 函数也提供了对子模块的支持，例如，上面的子模块可以使用 `module("a.b.c")` 的方式定义。同时， `module` 会定义全局变量 `a.b.c` 引用 子模块：

> ``module`` puts the environment table into variable ``a.b.c``, that is ,
> into a field ``c`` of a table in field ``b`` of a table ``a``. If any of
> these intermediate tables do not exist, ``module`` creates them. Otherwise,
> it reuses them.

需要注意的一点是，同一个 `package` 中的子模块之间，除了上面提到的它们的环境可 能嵌套存放以外，并没有显式的关联。比如， 执行`require("a")` 时，并不会自动加 载它的子模块 `a.b` ；执行了 `require("a.b")` 时，也不会自动加载 `a` 模块；

### 面向对象

Lua 语言并未提供对面向对象编程模型的原生支持，但是它提供的 `table` 类型和 _metatable_ ，_environment_ 等机制，可以用来实现类似的面向对象功能。

下面是摘自 PiL 的代码示例：

```lua
--- A base class
Account = {balance= 0}
-- Lua hide `self` when using *colon operator*, a syntactic sugar

function Account:new(o)
    -- A hidden `self` refers to table `Account`
    o = o or {}
    setmetable(o, self)
    self.__index = self
    return o
end

function Account:deposit(v)
    self.balance = self.balance + v
end

function Account.withdraw(self, v)
    if v > self.balance then error "insufficient funds" end
    self.balance = self.balance - v
end

-- creates an instance of Account
a = Account:new{balance = 0}
a:deposit(100.00)   -- syntactic sugar of `a.deposit(a, 100.00)`

--- Inheritance
-- `SpecialAccount` is just an instance of `Account` up to now.
SpecialAccount = Account:new()
s = SpecialAccount:new{limit=1000.00}   -- `self` refers to `SpecialAcount`

-- the metatable of `s` is `SpecialAcccount`.
-- `s` is a table and Lua cannot find a `deposit` field in it, so it look
-- into `SpecialAccount`; it cannot find a `deposit` field there, too, so
-- it looks into `Account` and there it finds the original implementation
-- for a `deposit`
s:deposit(100.00)

-- What makes a `SpecialAccount` special is that we can redefine any method
-- inherited from its superclass.
function SpecialAccount:withdraw(v)
    if v - self.balance >= self:getLimit() then
        error"insufficient funds"
    end
    self.balance = self.balance - v
end

function SpecialAccount:getLimit()
    return self.limit or 0
end

-- Lua does not go to `Account`, because it finds the new `withdraw` method
-- in `SpecialAccount` first.
s:withdraw(200.00)
```

由于语言所限，使用 Lua 实现的面向对象模拟，并不能提供隐私控制机制。

### 语言互操作

luafaq#T4.4 luafaq#T4.5 luafaq#T7

#### C API

TODO: To be finished.

#### FFI

  * [LuaJIT FFI](http://luajit.org/ext_ffi.html)
  * [luaffi](https://github.com/jmckaskill/luaffi)
  * [Alien](http://alien.luaforge.net/)

## 其它

### 命令行参数

在使用 _lua_ 解释器运行 lua 脚本文件时，Lua 解释器会将所有命令行参数通过全局 `table` 类型数组 `arg` 的方式传递给脚本文件：

如下命令行调用，

```lua
% lua -la b.lua t1 t2
```

Lua 会创建有如下元素的 `arg` 数组：

```
arg = {
  [-2]= "lua", [-1]= "-la",
  [0]= "b.lua", [1]= "t1", [2]= "t2"
}
```

其中，索引值为 0 的元素是脚本的文件名，索引值从 1 开始的元素是在命令中出现的脚 本文件名后面的命令行参数，索引值小于 0 的是出现在脚本文件名前面的命令行参数。

在 Lua 代码中，还可以使用 `...` varargs 表达式获取索引从 1 开始的命令行参数。

不出意外，Lua 并未提供处理命令行参数的标准方式。但是开发者可以参考其它 Lua 程 序，比如 _Luarocks_ ，使用的处理逻辑，或者使用非标准库[lapp](http://lua-users.org/wiki/LappFramework) 。

下面的代码摘自 _Luarocks_ ，它使用 Lua 的字符串匹配函数进行命令行参数解析：

```lua
--- Extract flags from an argument list.
-- Given string arguments, extract flag arguments into a flags set.
-- For example, given "foo", "--tux=beep", "--bla", "bar", "--baz",
-- it would return the following:
-- {["bla"] = true, ["tux"] = "beep", ["baz"] = True}, "foo", "bar".
function parse_flags(...)
    local args = {...}
    local flags = {}
    for i = #args, 1, -1 do
        local flag = args[i]:match("^%-%-(.*)")
        if flag then
            local var, val = flag:match("([a-z_%-]*)=(.*)")
            if val then
                flags[var] = val
            else
                flags[flag] = true
            end
            table.remove(args, i)
        end
    end
    return flags, unpack(args)
end

```

### 装饰器

<http://lua-users.org/wiki/DecoratorsAndDocstrings>

## 优化建议

> The first question is, do you actually have a problem? Is the program not
> *fast enough? Remember the three basic requirements of a sytem: Correct,
> Robust, and Efficient, and the engineering rule of thumb that you may have
> to pick only two.
>   
> Donald Knuth is often quoted about optimisation: "If you optimise
> everything, you will always be unhappy" and "we should forget about small
> efficiencies, say about 97% of the time: premature optimisation is the root
> of all evil."
>   
> Assume a program is correct and (hopefully) robust. There is a definite
> cost in optimising that program, both in programmer time and in code
> readability. If you don't know what the slow bits are, then you will waste
> time making your ugly and maybe a little faster (which is why he says
> unhappy).
>  
> <Lua Performance Tips>
> Nevertheles, we all know that performance is a key ingredient of
> programming. It is not by change that problems with exponential time
> complexity are called *intractable*. A too late result is a useless result.
> So every good programmer should always balance the costs from spending
> resources to optimize a piece of code against the gains of saving resources
> when running that code.
>   
> The first question regarding optimization a good programmer always asks is:
> "Does the program needs to be optimized?" If the answer is positive (but
> only then), the second question should be: "Where?"


所以，优化建议的第一条就是不要轻易尝试优化。如果确实到了非优化不可的地步， 也需要先用工具定位需要优化的地方，比如，代码中会被频繁调用并且性能不佳的函数和内循环里的低效操作等等，对这些地方的优化能用较少的工作量换来整体性能的提升。

[LuaProfiler](http://luaprofiler.luaforge.net/manual.html) 就是一个用于定位代码中低效热点的工具。

我们还可以使用 [LuaJIT](http://luajit.org/) 替代标准 Lua (Vanilla Lua) 运行代 码，它可能会带来[几十倍](http://luajit.org/performance.html) 的性能提升。

CPU 密集型的操作可以放到使用 C API 实现的模块中。如果实现正确的话，整体可以 达到近似原生 C 程序的性能。同时，因为 Lua 语言语法精练，整体代码也更短小，更易 维护。 另外，通过 LuaJIT 提供的 FFI 等类似接口，甚至可以直接访问外部库提供的 C 语言函数和数据结构，这样就省去了使用 C API 编写模块的繁杂工作。

下面是几条可以提高代码性能的 [开发建议](http://lua-users.org/wiki/OptimisationCodingTips) ：

  * Locals are faster than globals.
    
    > Local variables are very fast as they reside in virtual machine registers, and are accessed directly by index. Global variables on the other hand, reside in a lua table and as such are accessed by a hash lookup.
    > -- Thomas Jefferson

    ```lua
		local next = next
		local i, v = next(t, nil)         -- 10% faster
		while i do i, v = next(t, i) end
    ```

  * Memory allocation from the heap -- e.g. repeatedly creating tables or closures -- can slow things down.

  * Multiplication `x*0.5` is faster than division `x/2`; `x*x` is faster than `x^2`;

  * 尽量避免新字符串创建；

  * 尽量重用己有对象；

  * 使用 `table.concat` 替代 `..` 完成字符串拼接；

  * 缓存会被多次使用的中间计算结果（memoizing）；将与循环无关的计算挪到循环外部；
    
    ```lua
		function memoize(f)
		    local mem = {}                    -- memoizing table
		    setmetatable(mem, {__mode= "kv"}) -- make it weak
		    return function(x)                -- new version of 'f', with
		                                      -- memoizing
		        local r = mem[x]
		        if r == nil then              -- no previous result?
		            r = f(x)                  -- calls original function
		            mem[x] = r                -- store result for reuse
		        end
		        return r
		    end
		end
		-- redefine 'loadstring'
		loadstring = memoize(loadstring)
		-- then use new version 'loadstring' as the original one
    ```

  * Lua 代码编译是项比较繁重的工作，所以，尽量避免在运行时编译（比如，调用 `loadstring` ）；

  * Lua `table` 分为数组部分和字典部分两个部分。当 `table` 空间不足时，插入 新元素会触发 `table` 的 _rehash_ 操作，申请更多的内存，重新插入原有元素。 _rehash_ 带来的开销随着插入数据的增加，会变得不那么显著，比如，向空 `table` 中的数组部分插入 3 个元素时，会触发 3 次 _rehash_ ，当插入元素达到百万时，只 需要 20 次 _rehash_ 。但是如果创建了很多元素较少的 `table` 时，这个开销就 很明显了。对 `table` 来说，最直接的优化措施就是按照需要，在表创建时就预先 分配好内存：

    * 可以通过 C API 提供的 `lua_createtable` 函数在表创建时指定需要的空间；
    * 使用占位符： `{true, true, true}` 告诉 Lua 创建可容纳 3 个数组元素的 `table` ； `{x= 1, y= 2, z= 3}` 也有类似的作用。
  
  * 由上面的描述我们知道，Lua 会在 `table` 空间不足并插入新元素时，对该 `table` 进行 _rehash_ 。这意味着，删除 `table` 元素（将元素值置成 `nil` ）并不会立即触发 `table` 内存回收，内存回收会在下一次 _rehash_ 时完 成。所以，想要释放 `table` 占用的内存，最好直接删除 `table` 本身。

  * 根据不同的使用场景，调整垃圾回收器配置参数。
    
    > <Lua Performance Tips>:
    > Most recycling in Lua is done automatically by the garbage collector. Lua uses an incremental garbage collector. That means that the collector performs its task in small steps (incrementally) interleaved with the program execution. The pace of these steops is proportional to memory allocation: for each amount of memory allocated by Lua, the garbage collector does some proportional work. The faster the program consumes memory, the faster the collector tries to recycle it.
    > 
    > Function ``collectgarbage`` provides several functionalities: it may stop and restart the collector, force a full collection cycle, force a collection step, get the total memory in use by Lua, and change two parameters that affect the pace of the collector.
    > 
    >    * ``parse`` - controls how long the collector waits between finishing
    >      a collection cycle and starting the next one.
    >    * ``stepmul`` - controls how much work the collector does in each step.
    
    Roughly, smaller parses and larger step multipliers increase the collector's speed.
    
    * 对于批处理类型的程序，由于进程生存周期短，垃圾回收的必要性就不高，可以将其 关闭；

    * 对于非批处理类型的程序，就不能简单关闭垃圾回收了事了。但是可以在进行时效性 要求较高的逻辑时，暂时停止垃圾回收。在必要时候，可以停掉垃圾回收，并且在合 适的时机显式调用垃圾回收。
      
      > In Lua 5.1, each time you force some collection when the collector is stopped, it automatically restarts. So, to keep it stopped, you must call ``collectgarbage("stop")`` immediately after forcing some collection.
      
    * 根据需求调整垃圾回收器的参数。运行快的垃圾回收逻辑，会消耗更多的 CPU，但是 会降低整体内存使用。

## 常用类库

* [Libraries and Bindings](http://lua-users.org/wiki/LibrariesAndBindings)
* [Kepler Project](https://github.com/keplerproject)
* 纯 Lua 实现的数据处理、函数式编程和操作系统路径操作等等功能类库 [Penlight](https://github.com/stevedonovan/Penlight)
* 兼容 PCRE 的正则库 [lrexlib](http://lrexlib.luaforge.net/)
* 二进制字符串操作库 [struct](http://www.inf.puc-rio.br/~roberto/struct/)
* Socket, HTTP, Mail [LuaSocket](http://w3.impa.br/~diego/software/luasocket/)
* 配置文件解析库 [pl.config](http://stevedonovan.github.io/Penlight/api/libraries/pl.config.html)
* 词法扫描器 [pl.lexer](http://stevedonovan.github.io/Penlight/api/libraries/pl.lexer.html)
* 文件系统操作 [luafilesystem](http://www.keplerproject.org/luafilesystem/)
* 守护进程 [luadaemon](http://lua.net-core.org/sputnik.lua?p=Telesto:About)
* 异步网络库 [copas](keplerproject.github.io/copas)
* 类似 gevent 的异步网络库 [levent](https://github.com/xjdrew/levent)
* Libuv Binding [luv](https://github.com/richardhundt/luv)
* QT Binding [lqt](https://github.com/mkottman/lqt)
* GTK Binding [lua-gtk](http://lua-gtk.luaforge.net/en/index.html)

## 参考资料

* [官方手册](https://www.lua.org/manual/5.1/)
* [Programming in Lua 2nd Edition](http://www.amazon.com/exec/obidos/ASIN/8590379825/lua-pilindex-20)
* [官方 FAQ](https://www.lua.org/faq.html)
* [非官方 FAQ](http://www.luafaq.org)
* [云风的博客](http://blog.codingnow.com)
* [lua-users FAQ](http://lua-users.org/wiki/LuaFaq)
* [lua-users Lua Gotchas](http://www.luafaq.org/gotchas.html)
* [awesome-lua](https://github.com/LewisJEllis/awesome-lua)
* [Learning Lua](http://lua-users.org/wiki/LearningLua)
* [Lua Tutorial](http://lua-users.org/wiki/LuaTutorial)
* [Learn Lua in 15 Minutes](http://tylerneylon.com/a/learn-lua/)
* _Masterminds of Programming: Conversations with the Creators of Major Programming Language_ 一书中有对 Lua 作者的访谈，[云风](http://blog.codingnow.com) 对该访谈进行了 [翻译](http://blog.codingnow.com/2010/06/masterminds_of_programming_7_lua.html) ；

