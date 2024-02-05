 
<!--BEGIN_DATA
{
    "create_date": "2016-09-02 12:07", 
    "modify_date": "2016-09-02 12:07", 
    "is_top": "0", 
    "summary": "HTTP", 
    "tags": "Web、网络", 
    "file_name": "HTTP.md"
}
END_DATA-->


- [HTTP](#http)
  - [URL](#url)
  - [消息格式](#%E6%B6%88%E6%81%AF%E6%A0%BC%E5%BC%8F)
  - [Reference](#reference)
    - [Tutorials & Docs](#tutorials-&-docs)
    - [Books & Tools](#books-&-tools)
- [HTTP 前世今生](#http-%E5%89%8D%E4%B8%96%E4%BB%8A%E7%94%9F)
  - [HTTP 0.9](#http-09)
  - [HTTP 1.0](#http-10)
    - [短暂连接的缺陷](#%E7%9F%AD%E6%9A%82%E8%BF%9E%E6%8E%A5%E7%9A%84%E7%BC%BA%E9%99%B7)
  - [HTTP 1.1](#http-11)
    - [持久连接](#%E6%8C%81%E4%B9%85%E8%BF%9E%E6%8E%A5)
    - [管道机制](#%E7%AE%A1%E9%81%93%E6%9C%BA%E5%88%B6)
    - [分块传输编码](#%E5%88%86%E5%9D%97%E4%BC%A0%E8%BE%93%E7%BC%96%E7%A0%81)
  - [HTTP 2](#http-2)
    - [二进制协议支持](#%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%8D%8F%E8%AE%AE%E6%94%AF%E6%8C%81)
    - [多工复用](#%E5%A4%9A%E5%B7%A5%E5%A4%8D%E7%94%A8)
    - [数据流](#%E6%95%B0%E6%8D%AE%E6%B5%81)
    - [头信息压缩](#%E5%A4%B4%E4%BF%A1%E6%81%AF%E5%8E%8B%E7%BC%A9)
    - [服务器推送](#%E6%9C%8D%E5%8A%A1%E5%99%A8%E6%8E%A8%E9%80%81)
- [HTTP General Header:HTTP 通用头](#http-general-headerhttp-%E9%80%9A%E7%94%A8%E5%A4%B4)
  - [Date](#date)
  - [Pragma](#pragma)
  - [Entity](#entity)
  - [Content-Type](#content-type)
  - [Content-Length](#content-length)
  - [Content-Encoding](#content-encoding)
- [HTTP Lint](#http-lint)


> 本文从属于笔者的[HTTP 理解与实践](HTTPs://github.com/wxyyxc1992/infrastructure-handbook#HTTP)系列文章，对于HTTP的学习主要包含[HTTP 基础](HTTPs://github.com/wxyyxc1992/infrastructure-handbook/blob/master/Network/Protocol/HTTP/HTTP.md)、[HTTP 请求头与请求体](HTTPs://github.com/wxyyxc1992/infrastructure-handbook/blob/master/Network/Protocol/HTTP/HTTP-request.md)、[HTTP 响应头与状态码](HTTPs://github.com/wxyyxc1992/infrastructure-handbook/blob/master/Network/Protocol/HTTP/HTTP-response.md)、[HTTP 缓存](HTTPs://github.com/wxyyxc1992/infrastructure-handbook/blob/master/Network/Protocol/HTTP/HTTP-cache.md)这四个部分，而对于HTTP相关的扩展与引申，我们还需要了解[HTTPS 理解与实践 ](HTTPs://github.com/wxyyxc1992/infrastructure-handbook/blob/master/Network/Protocol/HTTPS/HTTPS.md)、[HTTP/2 基础](HTTPs://github.com/wxyyxc1992/infrastructure-handbook/blob/master/Network/Protocol/HTTP2/HTTP2.md)、[WebSocket 基础](HTTPs://github.com/wxyyxc1992/infrastructure-handbook/blob/master/Network/Protocol/WebSocket/WebSocket.md)这些部分。本部分知识点同时也归纳于笔者的[我的校招准备之路:从Web前端到服务端应用架构](HTTPs://github.com/wxyyxc1992/Coder-Knowledge-Graph/blob/master/interview/my-frontend-backend-interview.md)这篇综述。

# HTTP

HTTP（HyperTextTransferProtocol）是超文本传输协议的缩写，它用于传送WWW方式的数据，关于HTTP 协议的详细内容请参考RFC2616。HTTP协议采用了请求/响应模型。客户端向服务器发送一个请求，请求头包含请求的方法、URI、协议版本、以及包含请求修饰符、客户 信息和内容的类似于MIME的消息结构。服务器以一个状态行作为响应，相应的内容包括消息协议的版本，成功或者错误编码加上包含服务器信息、实体元信息以及可能的实体内容。 
HTTP是一种无状态性的协议。这是因为此种协议不要求浏览器在每次请求中标明它自己的身份，并且浏览器以及服务器之间并没有保持一个持久性的连接用于多个页面之间的访问。当一个用户访问一个站点的时候，用户的浏览器发送一个HTTP请求到服务器，服务器返回给浏览器一个HTTP响应。其实很简单的一个概念，客户端一个请求，服务器端一个回复，这就是整个基于HTTP协议的通讯过程。

## URL
在WWW上，每一信息资源都有统一的且在网上唯一的地址，该地址就叫URL（Uniform Resource Locator,统一资源定位符），它是WWW的统一资源定位标志。URL分为绝对URL与相对URL两种。绝对URL和访问时的状态完全无关。与之相对应的是省略了部分信息的相对（relative）URL，如../file.php?text=hello+world，它需要根据当前浏览所在上下文环境里的基准URL，才能确定完整的URL地址。

![](http://7xlgth.com1.z0.glb.clouddn.com/fafasfasfdsfads%E5%9B%BE%E7%89%871.png)

URL由三部分组成：资源类型、存放资源的主机域名、资源文件名。URL的一般语法格式为：(带方括号[]的为可选项)：protocol :// hostname[:port] / path / [;parameters][?query]#fragment

## 消息格式

通常HTTP消息包括客户机向服务器的请求消息和服务器向客户机的响应消息。这两种类型的消息由一个起始行，一个或者多个头域，一个只是头域结束的空行和可选的消息体组成。HTTP的头域包括**通用头，请求头，响应头和实体头**四个部分。每个头域由一个域名，冒号（:）和域值三部分组成。域名是大小写无关的，域值前可以添加任何数量的空格符，头域可以被扩展为多行，在每行开始处，使用至少一个空格或制表符。

当用户访问HTTP://example.com这个域名的时候，浏览器就会自动和服务器建立tcp/ip连接，然后发送HTTP请求到example.com的服务器的80端口。该个请求的语法如下所示：

``` 
GET / HTTP/1.1
Host: example.org
```

以上第一行叫做请求行，第二个参数(一个反斜线在这个例子中)表示所请求资源的路径。反斜线代表了根目录;服务器会转换这个根目录为服务器文件系统中的一个具体目录。

Apache的用户常用DocumentRoot这个命令来设置这个文档根路径。如果请求的url是HTTP://example.org/path/to/script.php,那么请求的路径就是/path/to/script.php。假如document root 被定义为usr/lcoal/apache/htdocs的话,整个请求的资源路径就是/usr/local/apache/htdocs/path/to/script.php。

第二行描述的是HTTP头部的语法。在这个例子中的头部是Host, 它标识了浏览器希望获取资源的域名主机。还有很多其它的请求头部可以包含在HTTP请求中，比如user-Agent头部，在php可以通过$_SERVER['HTTP_USER_AGENT']获取请求中所携带的这个头部信息。

## Reference

### Tutorials & Docs

- [全栈工程师眼中的HTTP](HTTP://www.epubit.com.cn/article/378)
- [阮一峰——HTTP协议入门](HTTP://www.ruanyifeng.com/blog/2016/08/HTTP.html?hmsr=toutiao.io&utm_medium=toutiao.io&utm_source=toutiao.io)

### Books & Tools

- [High Performance Browser Networking](HTTP://chimera.labs.oreilly.com/books/1230000000545/index.html)

# HTTP 前世今生

## HTTP 0.9

最早版本是1991年发布的0.9版。该版本极其简单，只有一个命令`GET`。
```
GET /index.html
```
上面命令表示，TCP 连接（connection）建立后，客户端向服务器请求（request）网页`index.html`。协议规定，服务器只能回应HTML格式的字符串，不能回应别的格式。

```
<html>
  <body>Hello World</body>
 </html>
```
服务器发送完毕，就关闭TCP连接。

## HTTP 1.0
1996年5月，HTTP/1.0 版本发布，内容大大增加。首先，任何格式的内容都可以发送。这使得互联网不仅可以传输文字，还能传输图像、视频、二进制文件。这为互联网的大发展奠定了基础。其次，除了`GET`命令，还引入了`POST`命令和`HEAD`命令，丰富了浏览器与服务器的互动手段。再次，HTTP请求和回应的格式也变了。除了数据部分，每次通信都必须包括头信息（HTTP header），用来描述一些元数据。其他的新增功能还包括状态码（status code）、多字符集支持、多部分发送（multi-part type）、权限（authorization）、缓存（cache）、内容编码（content encoding）等。

### 短暂连接的缺陷
HTTP 1.0规定浏览器与服务器只保持短暂的连接，浏览器的每次请求都需要与服务器建立一个TCP连接，服务器完成请求处理后立即断开TCP连接，服务器不跟踪每个客户也不记录过去的请求。但是，这也造成了一些性能上的缺陷，例如，一个包含有许多图像的网页文件中并没有包含真正的图像数据内容，而只是指明了这些图像的URL地址，当WEB浏览器访问这个网页文件时，浏览器首先要发出针对该网页文件的请求，当浏览器解析WEB服务器返回的该网页文档中的HTML内容时，发现其中的<img>图像标签后，浏览器将根据<img>标签中的src属性所指定的URL地址再次向服务器发出下载图像数据的请求：
![](http://p.blog.csdn.net/images/p_blog_csdn_net/zhangxiaoxiang/i5.jpg)
显然，访问一个包含有许多图像的网页文件的整个过程包含了多次请求和响应，每次请求和响应都需要建立一个单独的连接，每次连接只是传输一个文档和图像，上一 次和下一次请求完全分离。即使图像文件都很小，但是客户端和服务器端每次建立和关闭连接却是一个相对比较费时的过程，并且会严重影响客户机和服务器的性 能。当一个网页文件中包含Applet，JavaScript文件，CSS文件等内容时，也会出现类似上述的情况。

## HTTP 1.1
### 持久连接
在HTTP1.0中，每对Request/Response都使用一个新的连接。HTTP 1.1则支持持久连接Persistent Connection, 并且默认使用persistent  connection. 在同一个tcp的连接中可以传送多个HTTP请求和响应. 多个请求和响应可以重叠，多个请求和响应可以同时进行. 更加多的请求头和响应头(比如HTTP1.0没有host的字段).HTTP 1.1的持续连接，也需要增加新的请求头来帮助实现，例如，Connection请求头的值为Keep-Alive时，客户端通知服务器返回本次请求结果后保持连接；Connection请求头的值为close时，客户端通知服务器返回本次请求结果后关闭连接。HTTP 1.1还提供了与身份认证、状态管理和Cache缓存等机制相关的请求头和响应头。HTTP 1.0规定浏览器与服务器只保持短暂的连接，浏览器的每次请求都需要与服务器建立一个TCP连接，服务器完成请求处理后立即断开TCP连接，服务器不跟踪 每个客户也不记录过去的请求。此外，由于大多数网页的流量都比较小，一次TCP连接很少能通过slow-start区，不利于提高带宽利用率。
![](http://p.blog.csdn.net/images/p_blog_csdn_net/zhangxiaoxiang/i6.jpg)


### 管道机制
1.1 版还引入了管道机制（pipelining），即在同一个TCP连接里面，客户端可以同时发送多个请求。这样就进一步改进了HTTP协议的效率。举例来说，客户端需要请求两个资源。以前的做法是，在同一个TCP连接里面，先发送A请求，然后等待服务器做出回应，收到后再发出B请求。管道机制则是允许浏览器同时发出A请求和B请求，但是服务器还是按照顺序，先回应A请求，完成后再回应B请求。

### 分块传输编码
**分块传输编码**（**Chunked transfer encoding**）是超文本传输协议（HTTP）中的一种数据传输机制，允许HTTP由应用服务器发送给客户端应用（ 通常是网页浏览器）的数据可以分成多个部分。分块传输编码只在HTTP协议1.1版本（HTTP/1.1）中提供。通常，HTTP应答消息中发送的数据是整个发送的，Content-Length消息头字段表示数据的长度。数据的长度很重要，因为客户端需要知道哪里是应答消息的结束，以及后续应答消息的开始。然而，使用分块传输编码，数据分解成一系列数据块，并以一个或多个块发送，这样服务器可以发送数据而不需要预先知道发送内容的总大小。通常数据块的大小是一致的，但也不总是这种情况。

HTTP 1.1引入分块传输编码提供了以下几点好处：

1. HTTP分块传输编码允许服务器为动态生成的内容维持HTTP持久连接。通常，持久链接需要服务器在开始发送消息体前发送Content-Length消息头字段，但是对于动态生成的内容来说，在内容创建完之前是不可知的。**[动态内容，content-length无法预知]**
2. 分块传输编码允许服务器在最后发送消息头字段。对于那些头字段值在内容被生成之前无法知道的情形非常重要，例如消息的内容要使用散列进行签名，散列的结果通过HTTP消息头字段进行传输。没有分块传输编码时，服务器必须缓冲内容直到完成后计算头字段的值并在发送内容前发送这些头字段的值。**[散列签名，需缓冲完成才能计算]**
3. HTTP服务器有时使用压缩 （gzip或deflate）以缩短传输花费的时间。分块传输编码可以用来分隔压缩对象的多个部分。在这种情况下，块不是分别压缩的，而是整个负载进行压缩，压缩的输出使用本文描述的方案进行分块传输。在压缩的情形中，分块编码有利于一边进行压缩一边发送数据，而不是先完成压缩过程以得知压缩后数据的大小。**[gzip压缩，压缩与传输同时进行]**

一般情况HTTP的Header包含Content-Length域来指明报文体的长度。有时候服务生成HTTP回应是无法确定消息大小的，比如大文件的下载，或者后台需要复杂的逻辑才能全部处理页面的请求，这时用需要实时生成消息长度，服务器一般使用chunked编码。在进行Chunked编码传输时，在回复消息的Headers有transfer-coding域值为chunked，表示将用chunked编码传输内容。使用chunked编码的Headers如下（可以利用FireFox的FireBug插件或HttpWatch查看Headers信息）：
```
  　　Chunked-Body=*chunk   
  　　　　　　　　　"0"CRLF   
  　　　　　　　　　footer   
  　　　　　　　　　CRLF   
  　　chunk=chunk-size[chunk-ext]CRLF   
  　　　　　　chunk-dataCRLF   
    
  　　hex-no-zero=<HEXexcluding"0">   
    
  　　chunk-size=hex-no-zero*HEX   
  　　chunk-ext=*(";"chunk-ext-name["="chunk-ext-value])   
  　　chunk-ext-name=token   
  　　chunk-ext-val=token|quoted-string   
  　　chunk-data=chunk-size(OCTET)   
    

  　　footer=*entity-header 
```
编码使用若干个Chunk组成，由一个标明长度为0的chunk结束，每个Chunk有两部分组成，第一部分是该Chunk的长度和长度单位（一般不 写），第二部分就是指定长度的内容，每个部分用CRLF隔开。在最后一个长度为0的Chunk中的内容是称为footer的内容，是一些没有写的头部内容。下面给出一个Chunked的解码过程（RFC文档中有）：
```
  　　length:=0   
  　　readchunk-size,chunk-ext(ifany)andCRLF   
  　　while(chunk-size>0){   
  　　readchunk-dataandCRLF   
  　　appendchunk-datatoentity-body   
  　　length:=length+chunk-size   
  　　readchunk-sizeandCRLF   
  　　}   
  　　readentity-header   
  　　while(entity-headernotempty){   
  　　appendentity-headertoexistingheaderfields   
  　　readentity-header   
  　　}   
  　　Content-Length:=length   
  　　Remove"chunked"fromTransfer-Encoding
```
## HTTP 2
### 二进制协议支持
HTTP/1.1 版的头信息肯定是文本（ASCII编码），数据体可以是文本，也可以是二进制。HTTP/2 则是一个彻底的二进制协议，头信息和数据体都是二进制，并且统称为"帧"（frame）：头信息帧和数据帧。二进制协议的一个好处是，可以定义额外的帧。HTTP/2 定义了近十种帧，为将来的高级应用打好了基础。如果使用文本实现这种功能，解析数据将会变得非常麻烦，二进制解析则方便得多。

### 多工复用
HTTP/2 复用TCP连接，在一个连接里，客户端和浏览器都可以同时发送多个请求或回应，而且不用按照顺序一一对应，这样就避免了"队头堵塞"。举例来说，在一个TCP连接里面，服务器同时收到了A请求和B请求，于是先回应A请求，结果发现处理过程非常耗时，于是就发送A请求已经处理好的部分， 接着回应B请求，完成后，再发送A请求剩下的部分。这样双向的、实时的通信，就叫做多工（Multiplexing）。

### 数据流
因为 HTTP/2 的数据包是不按顺序发送的，同一个连接里面连续的数据包，可能属于不同的回应。因此，必须要对数据包做标记，指出它属于哪个回应。HTTP/2 将每个请求或回应的所有数据包，称为一个数据流（stream）。每个数据流都有一个独一无二的编号。数据包发送的时候，都必须标记数据流ID，用来区分它属于哪个数据流。另外还规定，客户端发出的数据流，ID一律为奇数，服务器发出的，ID为偶数。数据流发送到一半的时候，客户端和服务器都可以发送信号（RST_STREAM帧），取消这个数据流。1.1版取消数据流的唯一方法，就是关闭TCP连接。这就是说，HTTP/2 可以取消某一次请求，同时保证TCP连接还打开着，可以被其他请求使用。客户端还可以指定数据流的优先级。优先级越高，服务器就会越早回应。

### 头信息压缩
HTTP 协议不带有状态，每次请求都必须附上所有信息。所以，请求的很多字段都是重复的，比如Cookie和User Agent，一模一样的内容，每次请求都必须附带，这会浪费很多带宽，也影响速度。HTTP/2 对这一点做了优化，引入了头信息压缩机制（header compression）。一方面，头信息使用gzip或compress压缩后再发送；另一方面，客户端和服务器同时维护一张头信息表，所有字段都会存入这个表，生成一个索引号，以后就不发送同样字段了，只发送索引号，这样就提高速度了。

### 服务器推送
HTTP/2 允许服务器未经请求，主动向客户端发送资源，这叫做服务器推送（server push）。常见场景是客户端请求一个网页，这个网页里面包含很多静态资源。正常情况下，客户端必须收到网页后，解析HTML源码，发现有静态资源，再发出静态资源请求。其实，服务器可以预期到客户端请求网页后，很可能会再请求静态资源，所以就主动把这些静态资源随着网页一起发给客户端了。


# HTTP General Header:HTTP 通用头

就整个网络资源传输而言，包括message-header和message-body两部分。首先传递message-header，即**HTTP** **header**消息。HTTP header 消息通常被分为4个部分：general  header, request header, response header, entity header。但是这种分法就理解而言，感觉界限不太明确。根据维基百科对HTTP header内容的组织形式，大体分为Request和Response两部分。笔者在这里只是对于常见的协议头内容做一个列举，不同的设置会有不同的功能效果，会在下文中详细说明。本部分只介绍请求头的通用构成，具体的请求与响应参考各自章节。
> **注意每个Header的冒号后面有个空格**

通用头域包含请求和响应消息都支持的头域，通用头域包含Cache-Control、 Connection、Date、Pragma、Transfer-Encoding、Upgrade、Via。对通用头域的扩展要求通讯双方都支持此扩展，如果存在不支持的通用头域，一般将会作为实体头域处理。

## Date
Date头域表示消息发送的时间，时间的描述格式由rfc822定义。例如，Date:Mon,31Dec200104:25:57GMT。Date描述的时间表示世界标准时，换算成本地时间，需要知道用户所在的时区。

## Pragma

Pragma头域用来包含实现特定的指令，最常用的是Pragma:no-cache。在HTTP/1.1协议中，它的含义和Cache-Control:no-cache相同。 

## Entity

请求消息和响应消息都可以包含实体信息，实体信息一般由实体头域和实体组成。实体头域包含关于实体的原信息，实体头包括Allow、Content- Base、Content-Encoding、Content-Language、 Content-Length、Content-Location、Content-MD5、Content-Range、Content-Type、 Etag、Expires、Last-Modified、extension-header。extension-header允许客户端定义新的实体 头，但是这些域可能无法未接受方识别。实体可以是一个经过编码的字节流，它的编码方式由Content-Encoding或Content-Type定 义，它的长度由Content-Length或Content-Range定义。 

## Content-Type

Content-Type实体头用于向接收方指示实体的介质类型，指定HEAD方法送到接收方的实体介质类型，或GET方法发送的请求介质类型Content-Range实体头。关于字符的编码，1.0版规定，头信息必须是 ASCII 码，后面的数据可以是任何格式。因此，服务器回应的时候，必须告诉客户端，数据是什么格式。Content-Range实体头用于指定整个实体中的一部分的插入位置，他也指示了整个实体的长度。在服务器向客户返回一个部分响应，它必须描述响应覆盖的范围和整个实体长度。一般格式：
```
Content-Range:bytes-unitSPfirst-byte-pos-last-byte-pos/entity-legth
```
Content-Type表明信息类型，缺省值为" text/plain"。它包含了主要类型（primary type）和次要类型（subtype）两个部分，两者之间用"/"分割。主要类型有9种，分别是application、audio、example、image、message、model、multipart、text、video。每一种主要类型下面又有许多种次要类型，常见的有：
- text/plain：纯文本，文件扩展名.txt
- text/html：HTML文本，文件扩展名.htm和.html
- image/jpeg：jpeg格式的图片，文件扩展名.jpg
- image/gif：GIF格式的图片，文件扩展名.gif
- audio/x-wave：WAVE格式的音频，文件扩展名.wav
- audio/mpeg：MP3格式的音频，文件扩展名.mp3
- video/mpeg：MPEG格式的视频，文件扩展名.mpg
- application/zip：PK-ZIP格式的压缩文件，文件扩展名.zip

## Content-Length 
TCP 1.0中允许单个TCP连接可以传送多个回应，势必就要有一种机制，区分数据包是属于哪一个回应的。这就是Content-length字段的作用，声明本次回应的数据长度。只有当浏览器使用持久HTTP连接时才需要这个数据。如果你想要利用持久连接的优势，可以把输出文档写入ByteArrayOutputStram，完成后查看其大小，然后把该值放入Content-Length头，最后通过 byteArrayStream.writeTo(response.getOutputStream()发送内容。

## Content-Encoding
由于发送的数据可以是任何格式，因此可以把数据压缩后再发送。`Content-Encoding`字段说明数据的压缩方法。

> ```
> Content-Encoding: gzip
> Content-Encoding: compress
> Content-Encoding: deflate
> ```

客户端在请求时，用`Accept-Encoding`字段说明自己可以接受哪些压缩方法。

```
Accept-Encoding: gzip, deflate
```

# HTTP Lint

> - [Lint for HTTP:HTTPolice](HTTP://www.tuicool.com/articles/yuaeyuj)

HTTPolice是一个简单的基于命令行的对于HTTP请求格式规范进行检测的工具，可以直接使用`pip`命令进行安装:
```
pip install HTTPolice
```
当我们使用Google Chrome、Firefox或者Microsoft Edge进行网络访问时，可以使用开发者工具导出某个HAR文件，这也就是HTTP Lint工具可以用来解析的文件。使用如下命令进行分析:
```
$ httpolice -i har /path/to/file.har
------------ request: GET /1441/25776044114_0e5b9879a0_z.jpg------------ response: 200 OKC 1277 Obsolete 'X-' prefix in X-Photo-FarmC 1277 Obsolete 'X-' prefix in X-Photo-OriginE 1000 Malformed Expires headerE 1241 Date + Age is in the future
```
默认的HTTPolice以文本形式输出报告文本，如下所示
```
------------ request: PUT /articles/109226/
E 1000 Malformed If-Match header
C 1093 User-Agent contains no actual product
------------ response: 204 No Content
C 1110 204 response with no Date header
E 1221 Strict-Transport-Security without TLS
------------ request: POST /articles/109226/comments/
...
```
纯文本的方式可能比较难以理解，我们可以使用`-o html`选项来设置更详细的基于HTML风格的输出，譬如:
```
$ httpolice -i har -o html /path/to/file.har >report.html
```

![](https://coding.net/u/hoteam/p/Cache/git/raw/master/2016/8/2/6BF80CC5-C64A-4753-8EBA-FDDEA87C0297.png)


![](http://153.3.251.190:11900/HTTP)


<hr>





> 本文从属于笔者的[HTTP 理解与实践](https://github.com/wxyyxc1992/infrastructure-handbook#HTTP)系列文章，对于HTTP的学习主要包含[HTTP 基础](https://github.com/wxyyxc1992/infrastructure-handbook/blob/master/Network/Protocol/HTTP/http.md)、[HTTP 请求头与请求体](https://github.com/wxyyxc1992/infrastructure-handbook/blob/master/Network/Protocol/HTTP/http-request.md)、[HTTP 响应头与状态码](https://github.com/wxyyxc1992/infrastructure-handbook/blob/master/Network/Protocol/HTTP/http-response.md)、[HTTP 缓存](https://github.com/wxyyxc1992/infrastructure-handbook/blob/master/Network/Protocol/HTTP/http-cache.md)这四个部分，而对于HTTP相关的扩展与引申，我们还需要了解[HTTPS 理解与实践 ](https://github.com/wxyyxc1992/infrastructure-handbook/blob/master/Network/Protocol/HTTP/HTTPS/HTTPS.md)、[HTTP/2 基础](https://github.com/wxyyxc1992/infrastructure-handbook/blob/master/Network/Protocol/HTTP/HTTP2/HTTP2.md)、[WebSocket 基础](https://github.com/wxyyxc1992/infrastructure-handbook/blob/master/Network/Protocol/WebSocket/WebSocket.md)这些部分。本部分知识点同时也归纳于笔者的[我的校招准备之路:从Web前端到服务端应用架构](https://github.com/wxyyxc1992/Coder-Knowledge-Graph/blob/master/interview/my-frontend-backend-interview.md)这篇综述。

#HTTP Request
HTTP 的请求报文分为三个部分 请求行、请求头和请求体，格式如图：
![](http://upload-images.jianshu.io/upload_images/1724103-c43900117e983241.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
一个典型的请求消息头域，如下所示：

``` 
　　POST/GET http://download.microtool.de:80/somedata.exe 
　　Host: download.microtool.de 
　　Accept:*/* 
　　Pragma: no-cache 
　　Cache-Control: no-cache 
　　Referer: http://download.microtool.de/ 
　　User-Agent:Mozilla/4.04[en](Win95;I;Nav) 
　　Range:bytes=554554- 
```
# Request Line:请求行
请求行（Request Line）分为三个部分：请求方法、请求地址和协议及版本，以CRLF(\r\n)结束。
HTTP/1.1 定义的请求方法有8种：GET、POST、PUT、DELETE、PATCH、HEAD、OPTIONS、TRACE,最常的两种GET和POST，如果是RESTful接口的话一般会用到GET、POST、DELETE、PUT。
## Request Methods
注意，仅有POST、PUT以及PATCH这三个动词时会包含请求体，而GET、HEAD、DELETE、CONNECT、TRACE、OPTIONS这几个动词时不包含请求体。

# Header:请求头
| Header              | 解释                                       | 示例                                       |
| ------------------- | ---------------------------------------- | ---------------------------------------- |
| Accept              | 指定客户端能够接收的内容类型                           | Accept: text/plain, text/html,application/json |
| Accept-Charset      | 浏览器可以接受的字符编码集。                           | Accept-Charset: iso-8859-5               |
| Accept-Encoding     | 指定浏览器可以支持的web服务器返回内容压缩编码类型。              | Accept-Encoding: compress, gzip          |
| Accept-Language     | 浏览器可接受的语言                                | Accept-Language: en,zh                   |
| Accept-Ranges       | 可以请求网页实体的一个或者多个子范围字段                     | Accept-Ranges: bytes                     |
| Authorization       | HTTP授权的授权证书                              | Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ== |
| Cache-Control       | 指定请求和响应遵循的缓存机制                           | Cache-Control: no-cache                  |
| Connection          | 表示是否需要持久连接。（HTTP 1.1默认进行持久连接）            | Connection: close                        |
| Cookie              | HTTP请求发送时，会把保存在该请求域名下的所有cookie值一起发送给web服务器。 | Cookie: $Version=1; Skin=new;            |
| Content-Length      | 请求的内容长度                                  | Content-Length: 348                      |
| Content-Type        | 请求的与实体对应的MIME信息                          | Content-Type: application/x-www-form-urlencoded |
| Date                | 请求发送的日期和时间                               | Date: Tue, 15 Nov 2010 08:12:31 GMT      |
| Expect              | 请求的特定的服务器行为                              | Expect: 100-continue                     |
| From                | 发出请求的用户的Email                            | From: user@email.com                     |
| Host                | 指定请求的服务器的域名和端口号                          | Host: www.zcmhi.com                      |
| If-Match            | 只有请求内容与实体相匹配才有效                          | If-Match: “737060cd8c284d8af7ad3082f209582d” |
| If-Modified-Since   | 如果请求的部分在指定时间之后被修改则请求成功，未被修改则返回304代码      | If-Modified-Since: Sat, 29 Oct 2010 19:43:31 GMT |
| If-None-Match       | 如果内容未改变返回304代码，参数为服务器先前发送的Etag，与服务器回应的Etag比较判断是否改变 | If-None-Match: “737060cd8c284d8af7ad3082f209582d” |
| If-Range            | 如果实体未改变，服务器发送客户端丢失的部分，否则发送整个实体。参数也为Etag  | If-Range: “737060cd8c284d8af7ad3082f209582d” |
| If-Unmodified-Since | 只在实体在指定时间之后未被修改才请求成功                     | If-Unmodified-Since: Sat, 29 Oct 2010 19:43:31 GMT |
| Max-Forwards        | 限制信息通过代理和网关传送的时间                         | Max-Forwards: 10                         |
| Pragma              | 用来包含实现特定的指令                              | Pragma: no-cache                         |
| Proxy-Authorization | 连接到代理的授权证书                               | Proxy-Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ== |
| Range               | 只请求实体的一部分，指定范围                           | Range: bytes=500-999                     |
| Referer             | 先前网页的地址，当前请求网页紧随其后,即来路                   | Referer: http://www.zcmhi.com/archives/71.html |
| TE                  | 客户端愿意接受的传输编码，并通知服务器接受接受尾加头信息             | TE: trailers,deflate;q=0.5               |
| Upgrade             | 向服务器指定某种传输协议以便服务器进行转换（如果支持）              | Upgrade: HTTP/2.0, SHTTP/1.3, IRC/6.9, RTA/x11 |
| User-Agent          | User-Agent的内容包含发出请求的用户信息                 | User-Agent: Mozilla/5.0 (Linux; X11)     |
| Via                 | 通知中间网关或代理服务器地址，通信协议                      | Via: 1.0 fred, 1.1 nowhere.com (Apache/1.1) |
| Warning             | 关于消息实体的警告信息                              | Warn: 199 Miscellaneous warning          |

# Request Body:请求体
## Types
根据应用场景的不同，HTTP请求的请求体有三种不同的形式。
### 任意类型
移动开发者常见的，请求体是任意类型，服务器不会解析请求体，请求体的处理需要自己解析，如 POST JSON时候就是这类。
![](http://upload-images.jianshu.io/upload_images/1724103-ebe4ae9308d92ca0.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
#### application/json
application/json 这个 Content-Type 作为响应头大家肯定不陌生。实际上，现在越来越多的人把它作为请求头，用来告诉服务端消息主体是序列化后的 JSON 字符串。由于 JSON 规范的流行，除了低版本 IE 之外的各大浏览器都原生支持 JSON.stringify，服务端语言也都有处理 JSON 的函数，使用 JSON 不会遇上什么麻烦。

JSON 格式支持比键值对复杂得多的结构化数据，这一点也很有用。记得我几年前做一个项目时，需要提交的数据层次非常深，我就是把数据 JSON 序列化之后来提交的。不过当时我是把 JSON 字符串作为 val，仍然放在键值对里，以 x-www-form-urlencoded 方式提交。

Google 的 [AngularJS](http://angularjs.org/) 中的 Ajax 功能，默认就是提交 JSON 字符串。例如下面这段代码：

```
JSvar data = {'title':'test', 'sub' : [1,2,3]};
$http.post(url, data).success(function(result) {
    ...
});

```

最终发送的请求是：

```
BASHPOST http://www.example.com HTTP/1.1 
Content-Type: application/json;charset=utf-8

{"title":"test","sub":[1,2,3]}

```

这种方案，可以方便的提交复杂的结构化数据，特别适合 RESTful 的接口。各大抓包工具如 Chrome 自带的开发者工具、Firebug、Fiddler，都会以树形结构展示 JSON 数据，非常友好。但也有些服务端语言还没有支持这种方式，例如 php 就无法通过 $_POST 对象从上面的请求中获得内容。这时候，需要自己动手处理下：在请求头中 Content-Type 为 application/json 时，从 `php://input` 里获得原始输入流，再 `json_decode` 成对象。一些 php 框架已经开始这么做了。

当然 AngularJS 也可以配置为使用 x-www-form-urlencoded 方式提交数据。如有需要，可以参考[这篇文章](http://victorblog.com/2012/12/20/make-angularjs-http-service-behave-like-jquery-ajax/)。
#### text/xml
我的博客之前[提到过 XML-RPC](http://www.imququ.com/post/64.html)（XML Remote Procedure Call）。它是一种使用 HTTP 作为传输协议，XML 作为编码方式的远程调用规范。典型的 XML-RPC 请求是这样的：

```
HTMLPOST http://www.example.com HTTP/1.1 
Content-Type: text/xml

<?xml version="1.0"?>
<methodCall>
    <methodName>examples.getStateName</methodName>
    <params>
        <param>
            <value><i4>41</i4></value>
        </param>
    </params>
</methodCall>

```

XML-RPC 协议简单、功能够用，各种语言的实现都有。它的使用也很广泛，如 WordPress 的 [XML-RPC Api](http://codex.wordpress.org/XML-RPC_WordPress_API)，搜索引擎的 [ping 服务](http://help.baidu.com/question?prod_en=master&class=476&id=1000423)等等。JavaScript 中，也有[现成的库](http://plugins.jquery.com/xmlrpc/)支持以这种方式进行数据交互，能很好的支持已有的 XML-RPC 服务。不过，我个人觉得 XML 结构还是过于臃肿，一般场景用 JSON 会更灵活方便。
### Query String:application/x-www-form-urlencoded
这算是最常见的 POST 提交数据的方式了。浏览器的原生 <form> 表单，如果不设置 enctype 属性，那么最终就会以 application/x-www-form-urlencoded 方式提交数据。请求类似于下面这样（无关的请求头在本文中都省略掉了）：
> POST http://www.example.com HTTP/1.1
> Content-Type: application/x-www-form-urlencoded;charset=utf-8
> title=test&sub%5B%5D=1&sub%5B%5D=2&sub%5B%5D=3

首先，Content-Type 被指定为 application/x-www-form-urlencoded；这里的格式要求就是URL中Query String的格式要求：多个键值对之间用&连接，键与值之前用=连接，且只能用ASCII字符，非ASCII字符需使用UrlEncode编码。大部分服务端语言都对这种方式有很好的支持。例如 PHP 中，$_POST['title'] 可以获取到 title 的值，$_POST['sub'] 可以得到 sub 数组。
![](http://upload-images.jianshu.io/upload_images/1724103-18847d9a34c50bdd.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

### 文件分割
第三种请求体的请求体被分成为多个部分，文件上传时会被使用，这种格式最先应该是被用于邮件传输中，每个字段/文件都被boundary（Content-Type中指定）分成单独的段，每段以-- 加 boundary开头，然后是该段的描述头，描述头之后空一行接内容，请求结束的标制为boundary后面加--，结构见下图：
![](http://upload-images.jianshu.io/upload_images/1724103-f764903c4ae2408a.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
区分是否被当成文件的关键是Content-Disposition是否包含filename，因为文件有不同的类型，所以还要使用Content-Type指示文件的类型，如果不知道是什么类型取值可以为application/octet-stream表示该文件是个二进制文件，如果不是文件则Content-Type可以省略。
我们使用表单上传文件时，必须让 <form> 表单的 `enctyped` 等于 multipart/form-data。直接来看一个请求示例：

```
BASHPOST http://www.example.com HTTP/1.1
Content-Type:multipart/form-data; boundary=----WebKitFormBoundaryrGKCBY7qhFd3TrwA

------WebKitFormBoundaryrGKCBY7qhFd3TrwA
Content-Disposition: form-data; name="text"

title
------WebKitFormBoundaryrGKCBY7qhFd3TrwA
Content-Disposition: form-data; name="file"; filename="chrome.png"
Content-Type: image/png

PNG ... content of chrome.png ...
------WebKitFormBoundaryrGKCBY7qhFd3TrwA--

```

这个例子稍微复杂点。首先生成了一个 boundary 用于分割不同的字段，为了避免与正文内容重复，boundary 很长很复杂。然后 Content-Type 里指明了数据是以 multipart/form-data 来编码，本次请求的 boundary 是什么内容。消息主体里按照字段个数又分为多个结构类似的部分，每部分都是以 `--boundary` 开始，紧接着是内容描述信息，然后是回车，最后是字段具体内容（文本或二进制）。如果传输的是文件，还要包含文件名和文件类型信息。消息主体最后以 `--boundary--` 标示结束。关于 multipart/form-data 的详细定义，请前往 [rfc1867](http://www.ietf.org/rfc/rfc1867.txt) 查看。

这种方式一般用来上传文件，各大服务端语言对它也有着良好的支持。

上面提到的这两种 POST 数据的方式，都是浏览器原生支持的，而且现阶段标准中原生 <form> 表单也[只支持这两种方式](http://www.w3.org/TR/html401/interact/forms.html#h-17.13.4)（通过 <form> 元素的`enctype` 属性指定，默认为 `application/x-www-form-urlencoded`。其实 `enctype` 还支持 `text/plain`，不过用得非常少）。

随着越来越多的 Web 站点，尤其是 WebApp，全部使用 Ajax 进行数据交互之后，我们完全可以定义新的数据提交方式，给开发带来更多便利。




## Encoding:编码

网页中的表单使用POST方法提交时，数据内容的类型是 application/x-www-form-urlencoded，这种类型会：

　　1.字符"a"-"z"，"A"-"Z"，"0"-"9"，"."，"-"，"*"，和"_" 都不会被编码;

　　2.将空格转换为加号 (+) 

　　3.将非文本内容转换成"%xy"的形式,xy是两位16进制的数值;

　　4.在每个 name=value 对之间放置 & 符号。

web设计者面临的众多难题之一便是怎样处理不同操作系统间的差异性。这些差异性能引起URL方面的问题：例如，一些操作系统允许文件名中含有空格符，有些又不允许。大多数操作系统不会认为文件名中含有符号“#”会有什么特殊含义;但是在一个URL中，符号“#”表示该文件名已经结束，后面会紧跟一个fragment(部分)标识符。其他的特殊字符，非字母数字字符集，它们在URL或另一个操作系统上都有其特殊的含义，表述着相似的问题。为了解决这些问题，我们在URL中使用的字符就必须是一个ASCII字符集的固定字集中的元素，具体如下：

　　1.大写字母A-Z

　　2.小写字母a-z

　　3.数字 0-9

　　4.标点符 - _ . ! ~ * ' (和 ,)

　　诸如字符: / & ? @ #  $ + = 和 %也可以被使用，但是它们各有其特殊的用途，如果一个文件名包括了这些字符( / & ? @ #  $ + = %)，这些字符和所有其他字符就应该被编码。

　　编码过程非常简单，任何字符只要不是ASCII码数字，字母，或者前面提到的标点符，它们都将被转换成字节形式，每个字节都写成这种形式：一个“%”后面跟着两位16进制的数值。空格是一个特殊情况，因为它们太平常了。它除了被编码成“%20”以外，还能编码为一个“+”。加号(+)本身被编码为%2B。当/ # = & 和?作为名字的一部分来使用时，而不是作为URL部分之间的分隔符来使用时，它们都应该被编码。

　　WARNING这种策略在存在大量字符集的异构环境中效果不甚理想。例如：在U.S. Windows 系统中, é 被编码为 %E9. 在 U.S. Mac中被编码为%8E。这种不确定性的存在是现存的URI的一个明显的不足。所以在将来URI的规范当中应该通过国际资源标识符(IRIs)进行改善。

　　类URL并不自动执行编码或解码工作。你能生成一个URL对象，它可以包括非法的ASCII和非ASCII字符和/或%xx。当用方法getPath() 和toExternalForm( ) 作为输出方法时，这种字符和转移符不会自动编码或解码。你应对被用来生成一个URL对象的字符串对象负责，确保所有字符都会被恰当地编码。

![](http://153.3.251.190:11900/HTTP-Request)


<hr>




- [Header](#header)
- [StatusCode](#statuscode)
  - [1XX](#1xx)
  - [2XX/3XX](#2xx3xx)
  - [4XX](#4xx)
  - [5XX](#5xx)


> 本文从属于笔者的[HTTP 理解与实践](https://github.com/wxyyxc1992/infrastructure-handbook#HTTP)系列文章，对于HTTP的学习主要包含[HTTP 基础](https://github.com/wxyyxc1992/infrastructure-handbook/blob/master/Network/Protocol/HTTP/http.md)、[HTTP 请求头与请求体](https://github.com/wxyyxc1992/infrastructure-handbook/blob/master/Network/Protocol/HTTP/http-request.md)、[HTTP 响应头与状态码](https://github.com/wxyyxc1992/infrastructure-handbook/blob/master/Network/Protocol/HTTP/http-response.md)、[HTTP 缓存](https://github.com/wxyyxc1992/infrastructure-handbook/blob/master/Network/Protocol/HTTP/http-cache.md)这四个部分，而对于HTTP相关的扩展与引申，我们还需要了解[HTTPS 理解与实践 ](https://github.com/wxyyxc1992/infrastructure-handbook/blob/master/Network/Protocol/HTTP/HTTPS/HTTPS.md)、[HTTP/2 基础](https://github.com/wxyyxc1992/infrastructure-handbook/blob/master/Network/Protocol/HTTP/HTTP2/HTTP2.md)、[WebSocket 基础](https://github.com/wxyyxc1992/infrastructure-handbook/blob/master/Network/Protocol/WebSocket/WebSocket.md)这些部分。本部分知识点同时也归纳于笔者的[我的校招准备之路:从Web前端到服务端应用架构](https://github.com/wxyyxc1992/Coder-Knowledge-Graph/blob/master/interview/my-frontend-backend-interview.md)这篇综述。

#HTTP Response
![](http://upload-images.jianshu.io/upload_images/1724103-e8ebcab6c80b9044.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

# Header
响应头域允许服务器传递不能放在状态行的附加信息，这些域主要描述服务器的信息和 Request-URI进一步的信息。响应头域包含Age、Location、Proxy-Authenticate、Public、Retry- After、Server、Vary、Warning、WWW-Authenticate。对响应头域的扩展要求通讯双方都支持，如果存在不支持的响应头 域，一般将会作为实体头域处理。

| Header             | 解释                                       | 示例                                       |
| ------------------ | ---------------------------------------- | ---------------------------------------- |
| Accept-Ranges      | 表明服务器是否支持指定范围请求及哪种类型的分段请求                | Accept-Ranges: bytes                     |
| Age                | 从原始服务器到代理缓存形成的估算时间（以秒计，非负）               | Age: 12                                  |
| Allow              | 对某网络资源的有效的请求行为，不允许则返回405                 | Allow: GET, HEAD                         |
| Cache-Control      | 告诉所有的缓存机制是否可以缓存及哪种类型                     | Cache-Control: no-cache                  |
| Content-Encoding   | web服务器支持的返回内容压缩编码类型。                     | Content-Encoding: gzip                   |
| Content-Language   | 响应体的语言                                   | Content-Language: en,zh                  |
| Content-Length     | 响应体的长度                                   | Content-Length: 348                      |
| Content-Location   | 请求资源可替代的备用的另一地址                          | Content-Location: /index.htm             |
| Content-MD5        | 返回资源的MD5校验值                              | Content-MD5: Q2hlY2sgSW50ZWdyaXR5IQ==    |
| Content-Range      | 在整个返回体中本部分的字节位置                          | Content-Range: bytes 21010-47021/47022   |
| Content-Type       | 返回内容的MIME类型                              | Content-Type: text/html; charset=utf-8   |
| Date               | 原始服务器消息发出的时间                             | Date: Tue, 15 Nov 2010 08:12:31 GMT      |
| ETag               | 请求变量的实体标签的当前值                            | ETag: “737060cd8c284d8af7ad3082f209582d” |
| Expires            | 响应过期的日期和时间                               | Expires: Thu, 01 Dec 2010 16:00:00 GMT   |
| Last-Modified      | 请求资源的最后修改时间                              | Last-Modified: Tue, 15 Nov 2010 12:45:26 GMT |
| Location           | 用来重定向接收方到非请求URL的位置来完成请求或标识新的资源           | Location: http://www.zcmhi.com/archives/94.html |
| Pragma             | 包括实现特定的指令，它可应用到响应链上的任何接收方                | Pragma: no-cache                         |
| Proxy-Authenticate | 它指出认证方案和可应用到代理的该URL上的参数                  | Proxy-Authenticate: Basic                |
| refresh            | 应用于重定向或一个新的资源被创造，在5秒之后重定向（由网景提出，被大部分浏览器支持） | Refresh: 5; url=http://www.zcmhi.com/archives/94.html |
| Retry-After        | 如果实体暂时不可取，通知客户端在指定时间之后再次尝试               | Retry-After: 120                         |
| Server             | web服务器软件名称                               | Server: Apache/1.3.27 (Unix) (Red-Hat/Linux) |
| Set-Cookie         | 设置Http Cookie                            | Set-Cookie: UserID=JohnDoe; Max-Age=3600; Version=1 |
| Trailer            | 指出头域在分块传输编码的尾部存在                         | Trailer: Max-Forwards                    |
| Transfer-Encoding  | 文件传输编码                                   | Transfer-Encoding:chunked                |
| Vary               | 告诉下游代理是使用缓存响应还是从原始服务器请求                  | Vary: *                                  |
| Via                | 告知代理客户端响应是通过哪里发送的                        | Via: 1.0 fred, 1.1 nowhere.com (Apache/1.1) |
| Warning            | 警告实体可能存在的问题                              | Warning: 199 Miscellaneous warning       |
| WWW-Authenticate   | 表明客户端请求实体应该使用的授权方案                       | WWW-Authenticate: Basic                  |

# StatusCode
> - [how-to-choose-http-status-code](http://www.infoq.com/cn/news/2015/12/how-to-choose-http-status-code/)

众所周知，每一个HTTP响应都会带有一个状态码，不过对于很多开发者来说，平时使用最多的几个状态码无外乎就是200、400、404、500等。那其 他众多状态码该应用在何种场景中，什么时候应该使用哪些状态码就成为一个值得我们深入思考的问题了。即便在Facebook这样的公司中，那些聪明的开发者所构建的API也可能只返回200。对于目前的绝大部分服务端接口层设计都会遵循REST规范，而REST规范中推荐选用标准的HTTP 状态码作为返回值。在笔者的[来自微软的接口设计指南](https://segmentfault.com/a/1190000006037478)与[来自于PayPal的RESTful API标准 ](https://segmentfault.com/a/1190000005924733)这两篇来自于PayPal与Microsoft的REST设计规范中都建议了部分合适的返回值，而在本文这部分主要是对于通用的HTTP状态码选择进行一些讨论。目前HTTP状态码主要分为如下几类:
- 1xx:信息响应类，表示接收到请求并且继续处理 
- 2xx:处理成功响应类，表示动作被成功接收、理解和接受 
- 3xx:重定向响应类，为了完成指定的动作，必须接受进一步处理 
- 4xx:客户端错误，客户请求包含语法错误或者是不能正确执行 
- 5xx:服务端错误，服务器不能正确执行一个正确的请求 

![](https://coding.net/u/hoteam/p/Cache/git/raw/master/2016/7/3/CDBA2E18-FCDB-439A-AD3F-0340E8056795.png)

## 1XX
| 状态码  | 含义                                       |
| ---- | ---------------------------------------- |
| 100  | 客户端应当继续发送请求。这个临时响应是用来通知客户端它的部分请求已经被服务器接收，且仍未被拒绝。客户端应当继续发送请求的剩余部分，或者如果请求已经完成，忽略这个响应。服务器必须在请求完成后向客户端发送一个最终响应。 |
| 101  | 服务器已经理解了客户端的请求，并将通过Upgrade 消息头通知客户端采用不同的协议来完成这个请求。在发送完这个响应最后的空行后，服务器将会切换到在Upgrade 消息头中定义的那些协议。　　只有在切换新的协议更有好处的时候才应该采取类似措施。例如，切换到新的HTTP 版本比旧版本更有优势，或者切换到一个实时且同步的协议以传送利用此类特性的资源。 |
| 102  | 由WebDAV（RFC 2518）扩展的状态码，代表处理将被继续执行。      |
## 2XX/3XX
![](https://coding.net/u/hoteam/p/Cache/git/raw/master/2016/7/3/dadasdsadasxascas.png)

| 状态码  | 含义                                       |
| ---- | ---------------------------------------- |
| 200  | 请求已成功，请求所希望的响应头或数据体将随此响应返回。              |
| 201  | 请求已经被实现，而且有一个新的资源已经依据请求的需要而建立，且其 URI 已经随Location 头信息返回。假如需要的资源无法及时建立的话，应当返回 '202 Accepted'。 |
| 202  | 服务器已接受请求，但尚未处理。正如它可能被拒绝一样，最终该请求可能会也可能不会被执行。在异步操作的场合下，没有比发送这个状态码更方便的做法了。　　返回202状态码的响应的目的是允许服务器接受其他过程的请求（例如某个每天只执行一次的基于批处理的操作），而不必让客户端一直保持与服务器的连接直到批处理操作全部完成。在接受请求处理并返回202状态码的响应应当在返回的实体中包含一些指示处理当前状态的信息，以及指向处理状态监视器或状态预测的指针，以便用户能够估计操作是否已经完成。 |
| 203  | 服务器已成功处理了请求，但返回的实体头部元信息不是在原始服务器上有效的确定集合，而是来自本地或者第三方的拷贝。当前的信息可能是原始版本的子集或者超集。例如，包含资源的元数据可能导致原始服务器知道元信息的超级。使用此状态码不是必须的，而且只有在响应不使用此状态码便会返回200 OK的情况下才是合适的。 |
| 204  | 服务器成功处理了请求，但不需要返回任何实体内容，并且希望返回更新了的元信息。响应可能通过实体头部的形式，返回新的或更新后的元信息。如果存在这些头部信息，则应当与所请求的变量相呼应。　　如果客户端是浏览器的话，那么用户浏览器应保留发送了该请求的页面，而不产生任何文档视图上的变化，即使按照规范新的或更新后的元信息应当被应用到用户浏览器活动视图中的文档。　　由于204响应被禁止包含任何消息体，因此它始终以消息头后的第一个空行结尾。 |
| 205  | 服务器成功处理了请求，且没有返回任何内容。但是与204响应不同，返回此状态码的响应要求请求者重置文档视图。该响应主要是被用于接受用户输入后，立即重置表单，以便用户能够轻松地开始另一次输入。　　与204响应一样，该响应也被禁止包含任何消息体，且以消息头后的第一个空行结束。 |
| 206  | 服务器已经成功处理了部分 GET 请求。类似于 FlashGet 或者迅雷这类的 HTTP 下载工具都是使用此类响应实现断点续传或者将一个大文档分解为多个下载段同时下载。　　该请求必须包含 Range 头信息来指示客户端希望得到的内容范围，并且可能包含 If-Range 来作为请求条件。　　响应必须包含如下的头部域：　　Content-Range 用以指示本次响应中返回的内容的范围；如果是 Content-Type 为 multipart/byteranges 的多段下载，则每一 multipart 段中都应包含 Content-Range 域用以指示本段的内容范围。假如响应中包含 Content-Length，那么它的数值必须匹配它返回的内容范围的真实字节数。　　Date　　ETag 和/或 Content-Location，假如同样的请求本应该返回200响应。　　Expires, Cache-Control，和/或 Vary，假如其值可能与之前相同变量的其他响应对应的值不同的话。　　假如本响应请求使用了 If-Range 强缓存验证，那么本次响应不应该包含其他实体头；假如本响应的请求使用了 If-Range 弱缓存验证，那么本次响应禁止包含其他实体头；这避免了缓存的实体内容和更新了的实体头信息之间的不一致。否则，本响应就应当包含所有本应该返回200响应中应当返回的所有实体头部域。　　假如 ETag 或 Last-Modified 头部不能精确匹配的话，则客户端缓存应禁止将206响应返回的内容与之前任何缓存过的内容组合在一起。　　任何不支持 Range 以及 Content-Range 头的缓存都禁止缓存206响应返回的内容。 |
| 207  | 由WebDAV(RFC 2518)扩展的状态码，代表之后的消息体将是一个XML消息，并且可能依照之前子请求数量的不同，包含一系列独立的响应代码。 |
| 300  | 被请求的资源有一系列可供选择的回馈信息，每个都有自己特定的地址和浏览器驱动的商议信息。用户或浏览器能够自行选择一个首选的地址进行重定向。　　除非这是一个 HEAD 请求，否则该响应应当包括一个资源特性及地址的列表的实体，以便用户或浏览器从中选择最合适的重定向地址。这个实体的格式由 Content-Type 定义的格式所决定。浏览器可能根据响应的格式以及浏览器自身能力，自动作出最合适的选择。当然，RFC 2616规范并没有规定这样的自动选择该如何进行。　　如果服务器本身已经有了首选的回馈选择，那么在 Location 中应当指明这个回馈的 URI；浏览器可能会将这个 Location 值作为自动重定向的地址。此外，除非额外指定，否则这个响应也是可缓存的。 |
| 301  | 被请求的资源已永久移动到新位置，并且将来任何对此资源的引用都应该使用本响应返回的若干个 URI 之一。如果可能，拥有链接编辑功能的客户端应当自动把请求的地址修改为从服务器反馈回来的地址。除非额外指定，否则这个响应也是可缓存的。　　新的永久性的 URI 应当在响应的 Location 域中返回。除非这是一个 HEAD 请求，否则响应的实体中应当包含指向新的 URI 的超链接及简短说明。　　如果这不是一个 GET 或者 HEAD 请求，因此浏览器禁止自动进行重定向，除非得到用户的确认，因为请求的条件可能因此发生变化。　　注意：对于某些使用 HTTP/1.0 协议的浏览器，当它们发送的 POST 请求得到了一个301响应的话，接下来的重定向请求将会变成 GET 方式。 |
| 302  | 请求的资源现在临时从不同的 URI 响应请求。由于这样的重定向是临时的，客户端应当继续向原有地址发送以后的请求。只有在Cache-Control或Expires中进行了指定的情况下，这个响应才是可缓存的。　　新的临时性的 URI 应当在响应的 Location 域中返回。除非这是一个 HEAD 请求，否则响应的实体中应当包含指向新的 URI 的超链接及简短说明。　　如果这不是一个 GET 或者 HEAD 请求，那么浏览器禁止自动进行重定向，除非得到用户的确认，因为请求的条件可能因此发生变化。　　注意：虽然RFC 1945和RFC 2068规范不允许客户端在重定向时改变请求的方法，但是很多现存的浏览器将302响应视作为303响应，并且使用 GET 方式访问在 Location 中规定的 URI，而无视原先请求的方法。状态码303和307被添加了进来，用以明确服务器期待客户端进行何种反应。 |
| 303  | 对应当前请求的响应可以在另一个 URI 上被找到，而且客户端应当采用 GET 的方式访问那个资源。这个方法的存在主要是为了允许由脚本激活的POST请求输出重定向到一个新的资源。这个新的 URI 不是原始资源的替代引用。同时，303响应禁止被缓存。当然，第二个请求（重定向）可能被缓存。　　新的 URI 应当在响应的 Location 域中返回。除非这是一个 HEAD 请求，否则响应的实体中应当包含指向新的 URI 的超链接及简短说明。　　注意：许多 HTTP/1.1 版以前的 浏览器不能正确理解303状态。如果需要考虑与这些浏览器之间的互动，302状态码应该可以胜任，因为大多数的浏览器处理302响应时的方式恰恰就是上述规范要求客户端处理303响应时应当做的。 |
| 304  | 如果客户端发送了一个带条件的 GET 请求且该请求已被允许，而文档的内容（自上次访问以来或者根据请求的条件）并没有改变，则服务器应当返回这个状态码。304响应禁止包含消息体，因此始终以消息头后的第一个空行结尾。　　该响应必须包含以下的头信息：　　Date，除非这个服务器没有时钟。假如没有时钟的服务器也遵守这些规则，那么代理服务器以及客户端可以自行将 Date 字段添加到接收到的响应头中去（正如RFC 2068中规定的一样），缓存机制将会正常工作。　　ETag 和/或 Content-Location，假如同样的请求本应返回200响应。　　Expires, Cache-Control，和/或Vary，假如其值可能与之前相同变量的其他响应对应的值不同的话。　　假如本响应请求使用了强缓存验证，那么本次响应不应该包含其他实体头；否则（例如，某个带条件的 GET 请求使用了弱缓存验证），本次响应禁止包含其他实体头；这避免了缓存了的实体内容和更新了的实体头信息之间的不一致。　　假如某个304响应指明了当前某个实体没有缓存，那么缓存系统必须忽视这个响应，并且重复发送不包含限制条件的请求。　　假如接收到一个要求更新某个缓存条目的304响应，那么缓存系统必须更新整个条目以反映所有在响应中被更新的字段的值。 |
| 305  | 被请求的资源必须通过指定的代理才能被访问。Location 域中将给出指定的代理所在的 URI 信息，接收者需要重复发送一个单独的请求，通过这个代理才能访问相应资源。只有原始服务器才能建立305响应。　　注意：RFC 2068中没有明确305响应是为了重定向一个单独的请求，而且只能被原始服务器建立。忽视这些限制可能导致严重的安全后果。 |
| 306  | 在最新版的规范中，306状态码已经不再被使用。                  |
| 307  | 请求的资源现在临时从不同的URI 响应请求。由于这样的重定向是临时的，客户端应当继续向原有地址发送以后的请求。只有在Cache-Control或Expires中进行了指定的情况下，这个响应才是可缓存的。　　新的临时性的URI 应当在响应的 Location 域中返回。除非这是一个HEAD 请求，否则响应的实体中应当包含指向新的URI 的超链接及简短说明。因为部分浏览器不能识别307响应，因此需要添加上述必要信息以便用户能够理解并向新的 URI 发出访问请求。　　如果这不是一个GET 或者 HEAD 请求，那么浏览器禁止自动进行重定向，除非得到用户的确认，因为请求的条件可能因此发生变化。 |
## 4XX
![](https://coding.net/u/hoteam/p/Cache/git/raw/master/2016/7/3/cacasfasfrewcascads.png)

| 状态码  | 含义                                       |
| ---- | ---------------------------------------- |
| 400  | 1、语义有误，当前请求无法被服务器理解。除非进行修改，否则客户端不应该重复提交这个请求。　　2、请求参数有误。 |
| 401  | 当前请求需要用户验证。该响应必须包含一个适用于被请求资源的 WWW-Authenticate 信息头用以询问用户信息。客户端可以重复提交一个包含恰当的 Authorization 头信息的请求。如果当前请求已经包含了 Authorization 证书，那么401响应代表着服务器验证已经拒绝了那些证书。如果401响应包含了与前一个响应相同的身份验证询问，且浏览器已经至少尝试了一次验证，那么浏览器应当向用户展示响应中包含的实体信息，因为这个实体信息中可能包含了相关诊断信息。参见RFC 2617。 |
| 402  | 该状态码是为了将来可能的需求而预留的。                      |
| 403  | 服务器已经理解请求，但是拒绝执行它。与401响应不同的是，身份验证并不能提供任何帮助，而且这个请求也不应该被重复提交。如果这不是一个 HEAD 请求，而且服务器希望能够讲清楚为何请求不能被执行，那么就应该在实体内描述拒绝的原因。当然服务器也可以返回一个404响应，假如它不希望让客户端获得任何信息。 |
| 404  | 请求失败，请求所希望得到的资源未被在服务器上发现。没有信息能够告诉用户这个状况到底是暂时的还是永久的。假如服务器知道情况的话，应当使用410状态码来告知旧资源因为某些内部的配置机制问题，已经永久的不可用，而且没有任何可以跳转的地址。404这个状态码被广泛应用于当服务器不想揭示到底为何请求被拒绝或者没有其他适合的响应可用的情况下。 |
| 405  | 请求行中指定的请求方法不能被用于请求相应的资源。该响应必须返回一个Allow 头信息用以表示出当前资源能够接受的请求方法的列表。　　鉴于 PUT，DELETE 方法会对服务器上的资源进行写操作，因而绝大部分的网页服务器都不支持或者在默认配置下不允许上述请求方法，对于此类请求均会返回405错误。 |
| 406  | 请求的资源的内容特性无法满足请求头中的条件，因而无法生成响应实体。　　除非这是一个 HEAD 请求，否则该响应就应当返回一个包含可以让用户或者浏览器从中选择最合适的实体特性以及地址列表的实体。实体的格式由 Content-Type 头中定义的媒体类型决定。浏览器可以根据格式及自身能力自行作出最佳选择。但是，规范中并没有定义任何作出此类自动选择的标准。 |
| 407  | 与401响应类似，只不过客户端必须在代理服务器上进行身份验证。代理服务器必须返回一个 Proxy-Authenticate 用以进行身份询问。客户端可以返回一个 Proxy-Authorization 信息头用以验证。参见RFC 2617。 |
| 408  | 请求超时。客户端没有在服务器预备等待的时间内完成一个请求的发送。客户端可以随时再次提交这一请求而无需进行任何更改。 |
| 409  | 由于和被请求的资源的当前状态之间存在冲突，请求无法完成。这个代码只允许用在这样的情况下才能被使用：用户被认为能够解决冲突，并且会重新提交新的请求。该响应应当包含足够的信息以便用户发现冲突的源头。　　冲突通常发生于对 PUT 请求的处理中。例如，在采用版本检查的环境下，某次 PUT 提交的对特定资源的修改请求所附带的版本信息与之前的某个（第三方）请求向冲突，那么此时服务器就应该返回一个409错误，告知用户请求无法完成。此时，响应实体中很可能会包含两个冲突版本之间的差异比较，以便用户重新提交归并以后的新版本。 |
| 410  | 被请求的资源在服务器上已经不再可用，而且没有任何已知的转发地址。这样的状况应当被认为是永久性的。如果可能，拥有链接编辑功能的客户端应当在获得用户许可后删除所有指向这个地址的引用。如果服务器不知道或者无法确定这个状况是否是永久的，那么就应该使用404状态码。除非额外说明，否则这个响应是可缓存的。　　410响应的目的主要是帮助网站管理员维护网站，通知用户该资源已经不再可用，并且服务器拥有者希望所有指向这个资源的远端连接也被删除。这类事件在限时、增值服务中很普遍。同样，410响应也被用于通知客户端在当前服务器站点上，原本属于某个个人的资源已经不再可用。当然，是否需要把所有永久不可用的资源标记为'410 Gone'，以及是否需要保持此标记多长时间，完全取决于服务器拥有者。 |
| 411  | 服务器拒绝在没有定义 Content-Length 头的情况下接受请求。在添加了表明请求消息体长度的有效 Content-Length 头之后，客户端可以再次提交该请求。 |
| 412  | 服务器在验证在请求的头字段中给出先决条件时，没能满足其中的一个或多个。这个状态码允许客户端在获取资源时在请求的元信息（请求头字段数据）中设置先决条件，以此避免该请求方法被应用到其希望的内容以外的资源上。 |
| 413  | 服务器拒绝处理当前请求，因为该请求提交的实体数据大小超过了服务器愿意或者能够处理的范围。此种情况下，服务器可以关闭连接以免客户端继续发送此请求。　　如果这个状况是临时的，服务器应当返回一个 Retry-After 的响应头，以告知客户端可以在多少时间以后重新尝试。 |
| 414  | 请求的URI 长度超过了服务器能够解释的长度，因此服务器拒绝对该请求提供服务。这比较少见，通常的情况包括：　　本应使用POST方法的表单提交变成了GET方法，导致查询字符串（Query String）过长。　　重定向URI “黑洞”，例如每次重定向把旧的 URI 作为新的 URI 的一部分，导致在若干次重定向后 URI 超长。　　客户端正在尝试利用某些服务器中存在的安全漏洞攻击服务器。这类服务器使用固定长度的缓冲读取或操作请求的 URI，当 GET 后的参数超过某个数值后，可能会产生缓冲区溢出，导致任意代码被执行[1]。没有此类漏洞的服务器，应当返回414状态码。 |
| 415  | 对于当前请求的方法和所请求的资源，请求中提交的实体并不是服务器中所支持的格式，因此请求被拒绝。 |
| 416  | 如果请求中包含了 Range 请求头，并且 Range 中指定的任何数据范围都与当前资源的可用范围不重合，同时请求中又没有定义 If-Range 请求头，那么服务器就应当返回416状态码。　　假如 Range 使用的是字节范围，那么这种情况就是指请求指定的所有数据范围的首字节位置都超过了当前资源的长度。服务器也应当在返回416状态码的同时，包含一个 Content-Range 实体头，用以指明当前资源的长度。这个响应也被禁止使用 multipart/byteranges 作为其 Content-Type。 |
| 417  | 在请求头 Expect 中指定的预期内容无法被服务器满足，或者这个服务器是一个代理服务器，它有明显的证据证明在当前路由的下一个节点上，Expect 的内容无法被满足。 |
| 421  | 从当前客户端所在的IP地址到服务器的连接数超过了服务器许可的最大范围。通常，这里的IP地址指的是从服务器上看到的客户端地址（比如用户的网关或者代理服务器地址）。在这种情况下，连接数的计算可能涉及到不止一个终端用户。 |
| 422  | 从当前客户端所在的IP地址到服务器的连接数超过了服务器许可的最大范围。通常，这里的IP地址指的是从服务器上看到的客户端地址（比如用户的网关或者代理服务器地址）。在这种情况下，连接数的计算可能涉及到不止一个终端用户。 |
| 422  | 请求格式正确，但是由于含有语义错误，无法响应。（RFC 4918 WebDAV）423 Locked　　当前资源被锁定。（RFC 4918 WebDAV） |
| 424  | 由于之前的某个请求发生的错误，导致当前请求失败，例如 PROPPATCH。（RFC 4918 WebDAV） |
| 425  | 在WebDav Advanced Collections 草案中定义，但是未出现在《WebDAV 顺序集协议》（RFC 3658）中。 |
| 426  | 客户端应当切换到TLS/1.0。（RFC 2817）               |
| 449  | 由微软扩展，代表请求应当在执行完适当的操作后进行重试。              |
## 5XX
![](https://coding.net/u/hoteam/p/Cache/git/raw/master/2016/7/3/0F9F36D4-9A66-4972-85C0-F499B206F594.png)

| 状态码  | 含义                                       |
| ---- | ---------------------------------------- |
| 500  | 服务器遇到了一个未曾预料的状况，导致了它无法完成对请求的处理。一般来说，这个问题都会在服务器的程序码出错时出现。 |
| 501  | 服务器不支持当前请求所需要的某个功能。当服务器无法识别请求的方法，并且无法支持其对任何资源的请求。 |
| 502  | 作为网关或者代理工作的服务器尝试执行请求时，从上游服务器接收到无效的响应。    |
| 503  | 由于临时的服务器维护或者过载，服务器当前无法处理请求。这个状况是临时的，并且将在一段时间以后恢复。如果能够预计延迟时间，那么响应中可以包含一个 Retry-After 头用以标明这个延迟时间。如果没有给出这个 Retry-After 信息，那么客户端应当以处理500响应的方式处理它。　　注意：503状态码的存在并不意味着服务器在过载的时候必须使用它。某些服务器只不过是希望拒绝客户端的连接。 |
| 504  | 作为网关或者代理工作的服务器尝试执行请求时，未能及时从上游服务器（URI标识出的服务器，例如HTTP、FTP、LDAP）或者辅助服务器（例如DNS）收到响应。　　注意：某些代理服务器在DNS查询超时时会返回400或者500错误 |
| 505  | 服务器不支持，或者拒绝支持在请求中使用的 HTTP 版本。这暗示着服务器不能或不愿使用与客户端相同的版本。响应中应当包含一个描述了为何版本不被支持以及服务器支持哪些协议的实体。 |
| 506  | 由《透明内容协商协议》（RFC 2295）扩展，代表服务器存在内部配置错误：被请求的协商变元资源被配置为在透明内容协商中使用自己，因此在一个协商处理中不是一个合适的重点。 |
| 507  | 服务器无法存储完成请求所必须的内容。这个状况被认为是临时的。WebDAV (RFC 4918) |
| 509  | 服务器达到带宽限制。这不是一个官方的状态码，但是仍被广泛使用。          |
| 510  | 获取资源所需要的策略并没有没满足。（RFC 2774）              |


![](http://153.3.251.190:11900/HTTP-Response)



<hr>




- [HTTP Cache](#http-cache)
  - [Header](#header)
  - [Reference](#reference)
- [HTTP 1.0:基于Pragma&Expires的缓存实现](#http-10%E5%9F%BA%E4%BA%8Epragma&expires%E7%9A%84%E7%BC%93%E5%AD%98%E5%AE%9E%E7%8E%B0)
  - [Pragma](#pragma)
  - [Expire](#expire)
- [HTTP 1.1 Cache-Control:相对过期时间](#http-11-cache-control%E7%9B%B8%E5%AF%B9%E8%BF%87%E6%9C%9F%E6%97%B6%E9%97%B4)
- [HTTP 1.1 缓存校验](#http-11-%E7%BC%93%E5%AD%98%E6%A0%A1%E9%AA%8C)
  - [Last-Modified](#last-modified)
  - [ETag](#etag)
- [缓存策略](#%E7%BC%93%E5%AD%98%E7%AD%96%E7%95%A5)
  - [废弃和更新已缓存的响应](#%E5%BA%9F%E5%BC%83%E5%92%8C%E6%9B%B4%E6%96%B0%E5%B7%B2%E7%BC%93%E5%AD%98%E7%9A%84%E5%93%8D%E5%BA%94)
  - [缓存检查表](#%E7%BC%93%E5%AD%98%E6%A3%80%E6%9F%A5%E8%A1%A8)


> 本文从属于笔者的[HTTP 理解与实践](https://github.com/wxyyxc1992/infrastructure-handbook#HTTP)系列文章，对于HTTP的学习主要包含[HTTP 基础](https://github.com/wxyyxc1992/infrastructure-handbook/blob/master/Network/Protocol/HTTP/http.md)、[HTTP 请求头与请求体](https://github.com/wxyyxc1992/infrastructure-handbook/blob/master/Network/Protocol/HTTP/http-request.md)、[HTTP 响应头与状态码](https://github.com/wxyyxc1992/infrastructure-handbook/blob/master/Network/Protocol/HTTP/http-response.md)、[HTTP 缓存](https://github.com/wxyyxc1992/infrastructure-handbook/blob/master/Network/Protocol/HTTP/http-cache.md)这四个部分，而对于HTTP相关的扩展与引申，我们还需要了解[HTTPS 理解与实践 ](https://github.com/wxyyxc1992/infrastructure-handbook/blob/master/Network/Protocol/HTTP/HTTPS/HTTPS.md)、[HTTP/2 基础](https://github.com/wxyyxc1992/infrastructure-handbook/blob/master/Network/Protocol/HTTP/HTTP2/HTTP2.md)、[WebSocket 基础](https://github.com/wxyyxc1992/infrastructure-handbook/blob/master/Network/Protocol/WebSocket/WebSocket.md)这些部分。本部分知识点同时也归纳于笔者的[我的校招准备之路:从Web前端到服务端应用架构](https://github.com/wxyyxc1992/Coder-Knowledge-Graph/blob/master/interview/my-frontend-backend-interview.md)这篇综述。

# HTTP Cache

通过网络获取内容既缓慢，成本又高：大的响应需要在客户端和服务器之间进行多次往返通信，这拖延了浏览器可以使用和处理内容的时间，同时也增加了访问者的数据成本。因此，缓存和重用以前获取的资源的能力成为优化性能很关键的一个方面。每个浏览器都实现了 HTTP 缓存！ 我们所要做的就是，确保每个服务器响应都提供正确的 HTTP 头指令，以指导浏览器何时可以缓存响应以及可以缓存多久。服务器在返回响应时，还会发出一组 HTTP 头，用来描述内容类型、长度、缓存指令、验证令牌等。例如，在下图的交互中，服务器返回了一个 1024 字节的响应，指导客户端缓存响应长达 120 秒，并提供验证令牌（x234dff），在响应过期之后，可以用来验证资源是否被修改。

![](http://o6v08w541.bkt.clouddn.com/http-requestfcafds.png)
我们打开百度首页，可以看下百度的HTTP缓存的实现：
![](http://images2015.cnblogs.com/blog/561179/201603/561179-20160331162129410-1428753698.gif)
发现对于静态资源的访问都是返回的200状态码。

| 头部            | 优势和特点                                    | 劣势和问题                                    |
| ------------- | ---------------------------------------- | ---------------------------------------- |
| Expires       | 1、HTTP 1.0 产物，可以在HTTP 1.0和1.1中使用，简单易用。2、以时刻标识失效时间。 | 1、时间是由服务器发送的(UTC)，如果服务器时间和客户端时间存在不一致，可能会出现问题。2、存在版本问题，到期之前的修改客户端是不可知的。 |
| Cache-Control | 1、HTTP 1.1 产物，以时间间隔标识失效时间，解决了Expires服务器和客户端相对时间的问题。2、比Expires多了很多选项设置。 | 1、HTTP 1.1 才有的内容，不适用于HTTP 1.0 。2、存在版本问题，到期之前的修改客户端是不可知的。 |
| Last-Modified | 1、不存在版本问题，每次请求都会去服务器进行校验。服务器对比最后修改时间如果相同则返回304，不同返回200以及资源内容。 | 1、只要资源修改，无论内容是否发生实质性的变化，都会将该资源返回客户端。例如周期性重写，这种情况下该资源包含的数据实际上一样的。2、以时刻作为标识，无法识别一秒内进行多次修改的情况。3、某些服务器不能精确的得到文件的最后修改时间。 |
| ETag          | 1、可以更加精确的判断资源是否被修改，可以识别一秒内多次修改的情况。2、不存在版本问题，每次请求都回去服务器进行校验。 | 1、计算ETag值需要性能损耗。2、分布式服务器存储的情况下，计算ETag的算法如果不一样，会导致浏览器从一台服务器上获得页面内容后到另外一台服务器上进行验证时发现ETag不匹配的情况。 |


## Header
HTTP报文头部中与缓存相关的字段为：
**1. 通用首部字段**（就是请求报文和响应报文都能用上的字段）

![](http://images2015.cnblogs.com/blog/561179/201604/561179-20160401161150504-1030837643.png)

**2. 请求首部字段**

![](http://images2015.cnblogs.com/blog/561179/201604/561179-20160401161240301-2050921595.png)

**3. 响应首部字段**

![](http://images2015.cnblogs.com/blog/561179/201604/561179-20160401161311394-1246877214.png)

**4. 实体首部字段**

![](http://images2015.cnblogs.com/blog/561179/201604/561179-20160401171410441-767100632.png)
## Reference
- [HTTP缓存](https://developers.google.com/web/fundamentals/performance/optimizing-content-efficiency/http-caching?hl=zh-cn#cache-control-)
- [浅谈浏览器http的缓存机制](http://www.cnblogs.com/vajoy/p/5341664.html)
- [HTTP缓存控制小结](http://www.tuicool.com/articles/URJjAb)


# HTTP 1.0:基于Pragma&Expires的缓存实现

在 http1.0 时代，给客户端设定缓存方式可通过两个字段——“Pragma”和“Expires”来规范。虽然这两个字段早可抛弃，但为了做http协议的向下兼容，你还是可以看到很多网站依旧会带上这两个字段。

## Pragma

当该字段值为“no-cache”的时候*（事实上现在RFC中也仅标明该可选值）*，会知会客户端不要对该资源读缓存，即每次都得向服务器发一次请求才行。Pragma属于通用首部字段，在客户端上使用时，常规要求我们往html上加上这段meta元标签（仅对该页面有效，对页面上的资源无效）：
```
<meta http-equiv="Pragma" content="no-cache">
```
它告诉浏览器每次请求页面时都不要读缓存，都得往服务器发一次请求才行。不过这种限制行为在客户端作用有限：
1. 仅有IE才能识别这段meta标签含义，其它主流浏览器仅能识别“Cache-Control: no-store”的meta标签。
2. 在IE中识别到该meta标签含义，并不一定会在请求字段加上Pragma，但的确会让当前页面每次都发新请求（仅限页面，页面上的资源则不受影响）。

另外，需要知道的是，Pragma的优先级是高于Cache-Control 的。譬如在下图这个例子中，我们使用Fiddler为图片资源额外增加以下头部信息:
![](http://img0.tuicool.com/UZFv2mj.png!web)

前者用来设定缓存资源一天，后者禁用缓存，重新访问该页面会发现访问该资源会重新发起一次请求。

## Expire

有了Pragma来禁用缓存，自然也需要有个东西来启用缓存和定义缓存时间，对http1.0而言，Expires就是做这件事的首部字段。Expires的值对应一个GMT（格林尼治时间），比如“Mon, 22 Jul 2002 11:12:01 GMT”来告诉浏览器资源缓存过期时间，如果还没过该时间点则不发请求。在客户端我们同样可以使用meta标签来知会IE（也仅有IE能识别）页面（同样也只对页面有效，对页面上的资源无效）缓存时间：
```
<meta http-equiv="expires" content="mon, 18 apr 2016 14:30:00 GMT">
```
如果希望在IE下页面不走缓存，希望每次刷新页面都能发新请求，那么可以把“content”里的值写为“-1”或“0”。注意的是该方式仅仅作为知会IE缓存时间的标记，你并不能在请求或响应报文中找到Expires字段。如果是在服务端报头返回Expires字段，则在任何浏览器中都能正确设置资源缓存的时间。
![](http://img1.tuicool.com/FjYjYvv.png!web)

需要注意的是，响应报文中Expires所定义的缓存时间是相对服务器上的时间而言的，其定义的是资源“失效时刻”，如果客户端上的时间跟服务器上的时间不一致（特别是用户修改了自己电脑的系统时间），那缓存时间可能就没啥意义了。


# HTTP 1.1 Cache-Control:相对过期时间

针对上述的“Expires时间是相对服务器而言，无法保证和客户端时间统一”的问题，http1.1新增了 Cache-Control 来定义缓存过期时间，若报文中同时出现了Expires 和 Cache-Control，会以 Cache-Control 为准。换言之，这三者的优先级顺序为:Pragma -> Cache-Control -> Expires。Cache-Control也是一个通用首部字段，这意味着它能分别在请求报文和响应报文中使用。在RFC中规范了 Cache-Control 的格式为：
```
"Cache-Control" ":" cache-directive
```
作为请求首部时，cache-directive 的可选值有：

![](http://images2015.cnblogs.com/blog/561179/201604/561179-20160403173213113-100043029.png)

作为响应首部时，cache-directive 的可选值有：

![](http://images2015.cnblogs.com/blog/561179/201604/561179-20160403181549941-1360231582.png)

另外 Cache-Control 允许自由组合可选值，例如：
```
Cache-Control: max-age=3600, must-revalidate
```
它意味着该资源是从原服务器上取得的，且其缓存（新鲜度）的有效时间为一小时，在后续一小时内，用户重新访问该资源则无须发送请求。当然这种组合的方式也会有些限制，比如 no-cache 就不能和 max-age、min-fresh、max-stale 一起搭配使用。组合的形式还能做一些浏览器行为不一致的兼容处理。例如在IE我们可以使用 no-cache 来防止点击“后退”按钮时页面资源从缓存加载，但在 Firefox 中，需要使用 no-store 才能防止历史回退时浏览器不从缓存中去读取数据，故我们在响应报头加上如下组合值即可做兼容处理：

```
Cache-Control: no-cache, no-store
```

# HTTP 1.1 缓存校验

上述的首部字段均能让客户端决定是否向服务器发送请求，比如设置的缓存时间未过期，那么自然直接从本地缓存取数据即可（在chrome下表现为200 from cache），若缓存时间过期了或资源不该直接走缓存，则会发请求到服务器去。我们现在要说的问题是，如果客户端向服务器发了请求，那么是否意味着一定要读取回该资源的整个实体内容呢？我们试着这么想——客户端上某个资源保存的缓存时间过期了，但这时候其实服务器并没有更新过这个资源，如果这个资源数据量很大，客户端要求服务器再把这个东西重新发一遍过来，是否非常浪费带宽和时间呢？答案是肯定的，那么是否有办法让服务器知道客户端现在存有的缓存文件，其实跟自己所有的文件是一致的，然后直接告诉客户端说“这东西你直接用缓存里的就可以了，我这边没更新过呢，就不再传一次过去了”。为了让客户端与服务器之间能实现缓存文件是否更新的验证、提升缓存的复用率，Http1.1新增了几个首部字段来做这件事情。

## Last-Modified

服务器将资源传递给客户端时，会将资源最后更改的时间以“Last-Modified: GMT”的形式加在实体首部上一起返回给客户端。客户端会为资源标记上该信息，下次再次请求时，会把该信息附带在请求报文中一并带给服务器去做检查，若传递的时间值与服务器上该资源最终修改时间是一致的，则说明该资源没有被修改过，直接返回304状态码即可。至于传递标记起来的最终修改时间的请求报文首部字段一共有两个：

**⑴ If-Modified-Since: Last-Modified-value**

```
示例为  If-Modified-Since: Thu, 31 Mar 2016 07:07:52 GMT
```

该请求首部告诉服务器如果客户端传来的最后修改时间与服务器上的一致，则直接回送304 和响应报头即可。当前各浏览器均是使用的该请求首部来向服务器传递保存的 Last-Modified 值。

**⑵ If-Unmodified-Since: Last-Modified-value**

告诉服务器，若Last-Modified没有匹配上*（资源在服务端的最后更新时间改变了）*，则应当返回412(Precondition Failed) 状态码给客户端。

当遇到下面情况时，If-Unmodified-Since 字段会被忽略：

```
1. Last-Modified值对上了（资源在服务端没有新的修改）；
2. 服务端需返回2XX和412之外的状态码；
3. 传来的指定日期不合法
```

Last-Modified 说好却也不是特别好，因为如果在服务器上，一个资源被修改了，但其实际内容根本没发送改变，会因为Last-Modified时间匹配不上而返回了整个实体给客户端*（即使客户端缓存里有个一模一样的资源）*。

![](http://images.cnblogs.com/cnblogs_com/vajoy/558869/o_div.jpg)

## ETag

为了解决上述Last-Modified可能存在的不准确的问题，Http1.1还推出了 ETag 实体首部字段。服务器会通过某种算法，给资源计算得出一个唯一标志符*（比如md5标志）*，在把资源响应给客户端的时候，会在实体首部加上“ETag: 唯一标识符”一起返回给客户端。客户端会保留该 ETag 字段，并在下一次请求时将其一并带过去给服务器。服务器只需要比较客户端传来的ETag跟自己服务器上该资源的ETag是否一致，就能很好地判断资源相对客户端而言是否被修改过了。如果服务器发现ETag匹配不上，那么直接以常规GET 200回包形式将新的资源*（当然也包括了新的ETag）*发给客户端；如果ETag是一致的，则直接返回304知会客户端直接使用本地缓存即可。

那么客户端是如何把标记在资源上的 ETag 传去给服务器的呢？请求报文中有两个首部字段可以带上 ETag 值：

**⑴ If-None-Match: ETag-value**

```
示例为  If-None-Match: "56fcccc8-1699"
```

告诉服务端如果 ETag 没匹配上需要重发资源数据，否则直接回送304和响应报头即可。当前各浏览器均是使用的该请求首部来向服务器传递保存的 ETag 值。

**⑵ If-Match: ETag-value**

告诉服务器如果没有匹配到ETag，或者收到了“*”值而当前并没有该资源实体，则应当返回412(Precondition Failed) 状态码给客户端。否则服务器直接忽略该字段。If-Match 的一个应用场景是，客户端走PUT方法向服务端请求上传/更替资源，这时候可以通过 If-Match 传递资源的ETag。

 

需要注意的是，如果资源是走分布式服务器（比如CDN）存储的情况，需要这些服务器上计算ETag唯一值的算法保持一致，才不会导致明明同一个文件，在服务器A和服务器B上生成的ETag却不一样。

![](http://images.cnblogs.com/cnblogs_com/vajoy/558869/o_div.jpg)

如果 Last-Modified 和 ETag 同时被使用，则要求它们的验证都必须通过才会返回304，若其中某个验证没通过，则服务器会按常规返回资源实体及200状态码。

在较新的 nginx 上默认是同时开启了这两个功能的：

![](http://images2015.cnblogs.com/blog/561179/201604/561179-20160404021556078-697982021.gif)

上图的前三条请求是原始请求，接着的三条请求是刷新页面后的新请求，在发新请求之前我们修改了 reset.css 文件，所以它的 Last-Modified 和 ETag 均发生了改变，服务器因此返回了新的文件给客户端*（状态值为200）*。

而 dog.jpg 我们没有做修改，其Last-Modified 和 ETag在服务端是保持不变的，故服务器直接返回了304状态码让客户端直接使用缓存的 dog.jpg 即可，没有把实体内容返回给客户端*（因为没必要）*。

# 缓存策略
![](http://7xlgth.com1.z0.glb.clouddn.com/http-cache-decision-tree.png)

按照上面的决策树来确定您的应用使用的特定资源或一组资源的最优缓存策略。理想情况下，目标应该是在客户端上缓存尽可能多的响应、缓存尽可能长的时间，并且为每个响应提供验证令牌，以便进行高效的重新验证。

| Cache-Control 指令     | 说明                                       |
| -------------------- | ---------------------------------------- |
| max-age=86400        | 浏览器和任何中继缓存均可以将响应（如果是`public`的）缓存长达一天（60 秒 x 60 分 x 24 小时） |
| private, max-age=600 | 客户端浏览器只能将响应缓存最长 10 分钟（60 秒 x 10 分）       |
| no-store             | 不允许缓存响应，每个请求必须获取完整的响应。                   |

根据 HTTP Archive，在排名最高的 300,000 个网站中（Alexa 排名），[所有下载的响应中，几乎有半数可以由浏览器进行缓存](http://httparchive.org/trends.php#maxage0)，对于重复性网页浏览和访问来说，这是一个巨大的节省！ 当然，这并不意味着特定的应用会有 50% 的资源可以被缓存：有些网站可以缓存 90% 以上的资源， 而有些网站有许多私密的或者时间要求苛刻的数据，根本无法被缓存。
当我们在一个项目上做http缓存的应用时，我们还是会把上述提及的大多数首部字段均使用上，例如使用 Expires 来兼容旧的浏览器，使用 Cache-Control 来更精准地利用缓存，然后开启 ETag 跟 Last-Modified 功能进一步复用缓存减少流量。

那么这里会有一个小问题——Expires 和 Cache-Control 的值应设置为多少合适呢？

答案是不会有过于精准的值，均需要进行按需评估。

例如页面链接的请求常规是无须做长时间缓存的，从而保证回退到页面时能重新发出请求，百度首页是用的 Cache-Control:private，腾讯首页则是设定了60秒的缓存，即 Cache-Control:max-age=60。

而静态资源部分，特别是图片资源，通常会设定一个较长的缓存时间，而且这个时间最好是可以在客户端灵活修改的。以腾讯的某张图片为例：

```
http://i.gtimg.cn/vipstyle/vipportal/v4/img/common/logo.png?max_age=2592000
```

客户端可以通过给图片加上“max_age”的参数来定义服务器返回的缓存时间：

![](http://images2015.cnblogs.com/blog/561179/201604/561179-20160404115556000-838597877.png)

## 废弃和更新已缓存的响应
浏览器发出的所有 HTTP 请求会首先被路由到浏览器的缓存，以查看是否缓存了可以用于实现请求的有效响应。如果有匹配的响应，会直接从缓存中读取响应，这样就避免了网络延迟以及传输产生的数据成本。**然而，如果我们希望更新或废弃已缓存的响应，该怎么办？**

例如，假设我们已经告诉访问者某个 CSS 样式表缓存长达 24 小时 (max-age=86400)，但是设计人员刚刚提交了一个更新，我们希望所有用户都能使用。我们该如何通知所有访问者缓存的 CSS 副本已过时，需要更新缓存？ 这是一个欺骗性的问题 - 实际上，至少在不更改资源网址的情况下，我们做不到。

一旦浏览器缓存了响应，在过期以前，将一直使用缓存的版本，这是由 max-age 或者 expires 指定的，或者直到因为某些原因从缓存中删除，例如用户清除了浏览器缓存。因此，在构建网页时，不同的用户可能使用的是文件的不同版本；刚获取该资源的用户将使用新版本，而缓存过之前副本（但是依然有效）的用户将继续使用旧版本的响应。

**所以，我们如何才能鱼和熊掌兼得：客户端缓存和快速更新？** 很简单，在资源内容更改时，我们可以更改资源的网址，强制用户下载新响应。通常情况下，可以通过在文件名中嵌入文件的指纹码（或版本号）来实现 - 例如 style.**x234dff**.css。

当然这需要有一个前提——静态资源能确保长时间不做改动。如果一个脚本文件响应给客户端并做了长时间的缓存，而服务端在近期修改了该文件的话，缓存了此脚本的客户端将无法及时获得新的数据。

解决该困扰的办法也简单——把服务侧ETag的那一套也搬到前端来用——页面的静态资源以版本形式发布，常用的方法是在文件名或参数带上一串md5或时间标记符：

```
https://hm.baidu.com/hm.js?e23800c454aa573c0ccb16b52665ac26
http://tb1.bdstatic.com/tb/_/tbean_safe_ajax_94e7ca2.js
http://img1.gtimg.com/ninja/2/2016/04/ninja145972803357449.jpg
```

如果文件被修改了，才更改其标记符内容，这样能确保客户端能及时从服务器收取到新修改的文件。

因为能够定义每个资源的缓存策略，所以，我们可以定义’缓存层级’，这样，不但可以控制每个响应的缓存时间，还可以控制访问者看到新版本的速度。例如，我们一起分析一下上面的例子：

- HTML 被标记成`no-cache`，这意味着浏览器在每次请求时都会重新验证文档，如果内容更改，会获取最新版本。同时，在 HTML 标记中，我们在 CSS 和 JavaScript 资源的网址中嵌入指纹码：如果这些文件的内容更改，网页的 HTML 也会随之更改，并将下载 HTML 响应的新副本。
- 允许浏览器和中继缓存（例如 CDN）缓存 CSS，过期时间设置为 1 年。注意，我们可以放心地使用 1 年的’远期过期’，因为我们在文件名中嵌入了文件指纹码：如果 CSS 更新，网址也会随之更改。
- JavaScript 过期时间也设置为 1 年，但是被标记为 private，也许是因为包含了 CDN 不应缓存的一些用户私人数据。
- 缓存图片时不包含版本或唯一指纹码，过期时间设置为 1 天。

## 缓存检查表

不存在最佳的缓存策略。根据您的通信模式、提供的数据类型以及应用特定的数据更新要求，必须定义和配置每个资源最适合的设置以及整体的’缓存层级’。

在定义缓存策略时，要记住下列技巧和方法：

1. **使用一致的网址：**如果您在不同的网址上提供相同的内容，将会多次获取和存储该内容。提示：注意，[网址区分大小写](http://www.w3.org/TR/WD-html40-970708/htmlweb.html)！
2. **确保服务器提供验证令牌 (ETag)：**通过验证令牌，如果服务器上的资源未被更改，就不必传输相同的字节。
3. **确定中继缓存可以缓存哪些资源：**对所有用户的响应完全相同的资源很适合由 CDN 或其他中继缓存进行缓存。
4. **确定每个资源的最优缓存周期：**不同的资源可能有不同的更新要求。审查并确定每个资源适合的 max-age。
5. **确定网站的最佳缓存层级：**对 HTML 文档组合使用包含内容指纹码的资源网址以及短时间或 no-cache 的生命周期，可以控制客户端获取更新的速度。
6. **搅动最小化：**有些资源的更新比其他资源频繁。如果资源的特定部分（例如 JavaScript 函数或一组 CSS 样式）会经常更新，应考虑将其代码作为单独的文件提供。这样，每次获取更新时，剩余内容（例如不会频繁更新的库代码）可以从缓存中获取，确保下载的内容量最少。

![](http://153.3.251.190:11900/HTTP-Cache)



