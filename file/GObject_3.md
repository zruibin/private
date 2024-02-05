 
<!--BEGIN_DATA
{
    "create_date": "2019-02-01 18:40",
    "modify_date": "2019-02-01 18:40",
    "is_top": "0",
    "summary": "GObject 3",
    "tags": "C/C++",
    "file_name": "GObject_3.md"
}
END_DATA-->


####<p>原文出处：<a href='http://garfileo.is-programmer.com/2011/3/21/gobject-signal.25477.html' target='blank'>GObject 的信号机制——概览</a></p>

手册所述，GObject 信号（Gignal）主要用于特定事件与响应者之间的连接，它与操作系统级中的信号没有什么关系。例如，当我向一个文件中写入数据的时候，我期望能够有一个或多个函数响应这个 "向文件写入数据"的事件，这一期望便可基于 GObject 信号予以实现。

为了更好的理解 GObject 信号机制的内幕，我们需要从回调函数开始。

#####基于回调函数与可变参数的事件响应

首先，写出事件的制造者，它是一个向文件写入数据的函数 file\_write：

    
    
    #include <stdio.h>
    void
    file_write (FILE *fp, const char *buffer)
    {
            fprintf (fp, "%s\n", buffer);
    }
    

向文件写入数据完毕之后，我们希望有一个函数能够将文件全部的内容在终端打印出来，所以我们又增加了一个函数 file\_print，并对 file\_write
函数进行一点修改：

    
    
    void
    file_print (FILE *fp)
    {
            char *line = NULL;
            size_t len = 0;
            ssize_t read;
            while ((read = getline(&line, &len, fp)) != -1){
                    printf("%s", line);
            }
            free (line);
    }
    void
    file_write (FILE *fp, const char *buffer)
    {
            fprintf (fp, "%s\n", buffer);
            file_print (fp);
    }
    

但是，作为设计者应当尽可能的考虑更多更复杂的变化。单纯增加一个 file\_print 函数，并在 file\_write 函数中调用，固然可以实现"文件变化时便通知 file\_print 函数去执行打印任务"，但是这只是我们的一厢情愿的想法，也许 file\_write 函数的其他使用者希望在向文件写入数据后能够将文件内容以 XML、TeX 或者别的甚么格式打印出来呢？

为了应对更多的使用者的需求，我们需要使用回调函数来隔离变化，例如：

    
    
    typedef void (*ChangedCallback) (FILE *fp);
    void
    file_write (FILE *fp, const char *buffer, ChangedCallback callback)
    {
            fprintf (fp, "%s\n", buffer);
            callback (fp);
    }
    

这样，如果 file\_write 的使用者仅需要在文件内容发生变动后打印文件的原始数据，那么就可以将前文中的 file\_print 函数作为参数传递于
file\_write 函数。如果 file\_write 的使用者希望在文件内容发生变动后以 XML 格式打印文件，那么他可以写一个 file\_print\_xml 函数并将其传递于 file\_write 函数。

如果进一步考虑更多的变化，例如在 file\_write 向文件写入数据后，我们希望能够一举"通知"文件原始数据打印、XML 格式打印、TeX 格式打印等函数，这应当如何处理？如果使用 C 语言的可变参数功能，这个问题很好解决。例如，可以将 file\_write 函数定义为：

    
    
    void
    file_write (FILE *fp, const char *buffer, ...)
    {
            fprintf (fp, "%s\n", buffer);
            va_list args;
            ChangedCallback callback;
            va_start (args, buffer);
            while (1) {
                    callback = va_arg (args, ChangedCallback);
                    if (!callback)
                            break;
                    callback (fp);
            }
            va_end(args);
    }
    

这样，在使用 file\_write 函数的时候，可传递多个函数供其调用，例如：

    
    
    file_write (fp, "Hello world!", 
                file_print, 
                file_print_xml, 
                file_print_tex, 
                NULL);
    

基于回调函数与可变参数实现特定"事件"的多个"响应"，这种方案是最有效的，但不是最好的。例如，受到函数栈空间的大小限制，可变参数用尽之时。此外，这种方式使用起来也不够直观。

#####基于 GObject 信号的事件响应

对于上一节的示例所解决的问题，基于 GObjet 信号的解决方案大致像下面这样：

    
    
    void
    file_write (File *self, const char *buffer)
    {
            /* 向文件写入数据 */
            ... ... ...
            /* 发射"文件改变了"这一信号 */
            g_signal_emit (self, CHANGED, 0);
    }
    int
    main (void)
    {
            File *file = file_new ("test.txt");
            g_signal_connect (file, "changed", file_print, NULL);
            g_signal_connect (file, "changed", file_print_xml, NULL);
            g_signal_connect (file, "changed", file_print_tex, NULL);
            ... ... ...
    }
    

上述代码的含义如下：

  * 在 file\_write 函数中，文件数据写入操作完毕后，就这一事件向外发射一个"CHANGED"信号，告诉所有响应者，文件内容改变了。至于哪些函数是这一信号的响应者，file\_write 函数不必知道。
  * file\_write 函数的使用者，如果希望哪些函数用于响应 file\_write 函数修改文件内容这一事件，那么就使用 g\_signal\_connect 函数（实际上它是一个宏）将响应函数与信号挂接到一起。这样，一旦事件的对应信号被 g\_signal\_emit 所发射，这些响应函数便会被自动调用。

为了实现上述的"信号/响应"模拟，那么 file\_write 函数的参数便不可能再是 FILE 类型的文件指针了，而是我们自定义的 File 类型的对象，其中封装了"信号/响应"功能。事实上，GObject 类的内部便封装了这些功能，所有经由 GObject 子类化而产生的对象，便可拥有这些功能。

#####GObject 子类对象的信号处理

首先，我们定义 GObject 子类 MyFile。这个过程，我们应当已经不再陌生，参考文档 [1]。

my-file.h 头文件内容如下：

    
    
    #ifndef MY_FILE_H
    #define MY_FILE_H
    #include <glib-object.h>
    #define MY_TYPE_FILE (my_file_get_type ())
    #define MY_FILE(object) G_TYPE_CHECK_INSTANCE_CAST ((object), MY_TYPE_FILE, MyFile)
    #define MY_IS_FILE(object) G_TYPE_CHECK_INSTANCE_TYPE ((object), MY_TYPE_FILE))
    #define MY_FILE_CLASS(klass) (G_TYPE_CHECK_CLASS_CAST ((klass), MY_TYPE_FILE, MyFileClass))
    #define MY_IS_FILE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE ((klass), MY_TYPE_FILE))
    #define MY_FILE_GET_CLASS(object) (\
                    G_TYPE_INSTANCE_GET_CLASS ((object), MY_TYPE_FILE, MyFileClass))
    typedef struct _MyFile MyFile;
    struct _MyFile {
            GObject parent;
    };
    typedef struct _MyFileClass MyFileClass;
    struct _MyFileClass {
            GObjectClass parent_class;
    };
    GType my_file_get_type (void);
    #endif
    

my-file.c 源文件内容如下：

    
    
    #include "my-file.h"
    G_DEFINE_TYPE (MyFile, my_file, G_TYPE_OBJECT);
    #define MY_FILE_GET_PRIVATE(object) (\
                    G_TYPE_INSTANCE_GET_PRIVATE ((object), MY_TYPE_FILE, MyFilePrivate))
    typedef struct _MyFilePrivate MyFilePrivate;
    struct _MyFilePrivate {
            GString *name;
            GIOChannel *file;
    };
    enum PropertyDList {
            PROPERTY_FILE_0,
            PROPERTY_FILE_NAME
    };
    static void
    my_file_dispose (GObject *gobject)
    {
            MyFile *self        = MY_FILE (gobject);
            MyFilePrivate *priv = MY_FILE_GET_PRIVATE (self);
            if (priv->file){
                    g_io_channel_unref (priv->file);
                    priv->file = NULL;
            }
            G_OBJECT_CLASS (my_file_parent_class)->dispose (gobject);
    }
    static void
    my_file_finalize (GObject *gobject)
    {       
            MyFile *self        = MY_FILE (gobject);
            MyFilePrivate *priv = MY_FILE_GET_PRIVATE (self);
            g_string_free (priv->name, TRUE);
            G_OBJECT_CLASS (my_file_parent_class)->finalize (gobject);
    }
    static void
    my_file_set_property (GObject *object, guint property_id,
                          const GValue *value, GParamSpec *pspec)
    {
            MyFile *self = MY_FILE (object);
            MyFilePrivate *priv = MY_FILE_GET_PRIVATE (self);
            switch (property_id){
            case PROPERTY_FILE_NAME:
                    if (priv->name)
                            g_string_free (priv->name, TRUE);
                    priv->name = g_string_new (g_value_get_string (value));
                    priv->file = g_io_channel_new_file (priv->name->str, "a+", NULL);
                    break;
            default:
                    G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
                    break;
            }
    }
    static void
    my_file_get_property (GObject *object, guint property_id,
                          GValue *value, GParamSpec *pspec)
    {
            MyFile *self = MY_FILE (object);
            MyFilePrivate *priv = MY_FILE_GET_PRIVATE (self);
            switch (property_id){
            case PROPERTY_FILE_NAME:
                    g_value_set_string (value, priv->name->str);
                    break;
            default:
                    G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
                    break;
            }
    }
    static
    void my_file_init (MyFile *self)
    {
    }
    static
    void my_file_class_init (MyFileClass *klass)
    {
            g_type_class_add_private (klass, sizeof (MyFilePrivate));
            GObjectClass *base_class = G_OBJECT_CLASS (klass);
            base_class->set_property = my_file_set_property;
            base_class->get_property = my_file_get_property;
            base_class->dispose      = my_file_dispose;
            base_class->finalize     = my_file_finalize;
            GParamSpec *pspec;
            pspec = g_param_spec_string ("name",
                                         "Name",
                                         "File name",
                                         NULL,
                                         G_PARAM_READABLE | G_PARAM_WRITABLE | G_PARAM_CONSTRUCT);
            g_object_class_install_property (base_class, PROPERTY_FILE_NAME, pspec);
            g_signal_new ("file_changed",
                          MY_TYPE_FILE,
                          G_SIGNAL_RUN_LAST | G_SIGNAL_NO_RECURSE | G_SIGNAL_NO_HOOKS,
                          0,
                          NULL,
                          NULL,
                          g_cclosure_marshal_VOID__VOID,
                          G_TYPE_NONE,
                          0);
    }
    void
    my_file_write (MyFile *self, gchar *buffer)
    {
            MyFilePrivate *priv = MY_FILE_GET_PRIVATE (self);
            g_io_channel_write_chars (priv->file, buffer, -1, NULL, NULL);
            g_io_channel_flush (priv->file, NULL);
            g_signal_emit_by_name(self, "file_changed");  
    }
    

MyFile 类的使用者----main.c 文件内容如下：

    
    
    #include "my-file.h"
    static void
    file_print (gpointer gobject, gpointer user_data)
    {       
            g_printf ("invoking file_print!\n");
    }
    static void
    file_print_xml (gpointer gobject, gpointer user_data)
    {       
            g_printf ("invoking file_print_xml!\n");
    }
    static void
    file_print_tex (gpointer gobject, gpointer user_data)
    {       
            g_printf ("invoking file_print_tex!\n");
    }
    int
    main (void)
    {
            g_type_init ();
            MyFile *file = g_object_new (MY_TYPE_FILE, "name", "test.txt", NULL);
            g_signal_connect (file, "file_changed", G_CALLBACK (file_print), NULL);
            g_signal_connect (file, "file_changed", G_CALLBACK (file_print_xml), NULL);
            g_signal_connect (file, "file_changed", G_CALLBACK (file_print_tex), NULL);
            my_file_write (file, "hello world!\n");
            g_object_unref (file);
            return 0;
    }
    

虽然 GObject 子类化以及对象私有属性等知识均已有所介绍，但是上述的 MyFile 类的实现依然有许多细节需要加以解释。

首先，是在 MyFile 类的类结构题初始化函数 my\_file\_class\_init 中，除了设置类属性之外，我们调用了 g\_signal\_new 函数用于建立 MyFile 类型与 "file\_changed" 信号的关联。至于究竟是何种关联，那不是我们所关心的！还有，g\_signal\_new 函数的参数有很多，很复杂，推荐阅读文档 [2]。

其次，是 MyFile 对象的析构函数。在 my-file.c 源文件中，函数 my\_file\_dispose 与 my\_file\_finalize 构成了 MyFile 对象的析构函数，前者用于解除 MyFile 对象对其它对象（是指那些具有引用计数且被 GObject 库的类型系统所管理的对象）的引用，后者用于 MyFile 对象属性的内存释放。至于分何要分为两个阶段进行 GObject 子类对象析构以及相关细节知识，还是另外开一篇文章来讨论吧，否则问题会被越搞越复杂。或者，也可阅读文档 [3]。

#####小结

当我刚开始写这篇文章的时候，我期望能够理清 GObject 信号与闭包的关系，但是现在不得不宣布很失败。还是冷静几天再卷土重来吧。

这篇文章，写了一整天。现在我不得不告诉你，其实 GObject 真的很复杂。不过，从我向自己抛出了第一个谎言之后，一直坚持到现在。尽管复杂，但是我们正在一点一点克服它。但是，最大的敌人不是 GObject，而是我自己。因为在这个过程中，我经常无法抗拒一种解剖 GObject 的欲望。它导致我经常陷入一个又一个的技术细节，而忘记了当初的目标。这种欲望之所以出现，是因为 GObject 是开源的，它赋予了我们每个人可以窥视它内部实现的权力。

我需要再次纠正一下认识。对于 GObject 牌的汽车，我现在只需要学习如何驾驶它，根本不需要去了解它的发动机是如何工作的。


<hr>


####<p>原文出处：<a href='http://garfileo.is-programmer.com/2011/3/22/gobject-deconstruction.25485.html' target='blank'>GObject 子类对象的析构过程</a></p>


在 "[GObject 的信号机制](http://garfileo.is-programmer.com/2011/3/21/gobject-signal.25477.html)"文中，谈到 GObject 子类对象的析构过程分为两个阶段，第一阶段是 dispose，第二阶段是 finalize。之所以划分成两个阶段而不是一步到位的内存释放，一切皆因尴尬现实之所迫。

#####引用计数与引用循环

现在，我们都知道了 GObject 类及其子类的对象，其内存管理基于引用计数机制而实现。所谓基于引用计数的内存管理，可大致描述为：

  * 使用 g\_object\_new 函数进行对象实例化的时候，对象的引用计数为 1；
  * 每次使用 g\_object\_ref函数引用对象时，对象的引用计数便会增 1；
  * 每次使用 g\_object\_unref 函数为对象解除引用时，对象的引用计数便会减 1；
  * 在 g\_object\_unref 函数中，如果发现对象的引用计数为 0，那么则调用对象的析构函数释放对象所占用的资源。

GObjec 类及其子类对象不仅存在继承的关系，还存在互相包含的关系，例如有一个 GObject 子类对象 A 包含（引用）了另一个 GObject
子类对象 B（也就是说对象 B 是对象 A 的属性），而对象 B 有可能反过来又引用了对象 A，这样便构成了 **引用循环** 。对于这种情况，对象 A
的析构函数不可能一步到位彻底释放它所占用的资源，可以论证一下：

  * 假设对象 A 的析构函数为 a\_deconstruct。
  * a\_deconstruct 函数只能在对象 A 的引用计数为 0 的时候被 g\_object\_unref 函数调用。
  * 在 g\_object\_new 对象 A 的时候，由于 A 所包含的对象 B 有可能反过来引用 A，那么 A 的引用计数就有可能不是 1 而是 2。
  * 在 g\_object\_unref 对象 A 的时候，由于此时对象 A 的引用计数可能为 2，所以 g\_object\_unref 只是将 A 的引用计数减掉 1，而不会调用 a_deconstruct 函数。
  * 对于对象 A 的使用者，在不清楚对象 A 的内部实现时，他会天真的认为 g\_object\_new 与 g\_object\_unref 的配对就可以回收 A 的资源，但事实则不然。
  * 对象 A 的使用者如果多次调用 g\_object\_unref 最终可以引发 a\_deconstruct 函数工作，从而实现对象 A 的资源释放，但是使用者并不清楚究竟该运行几次 g\_object\_unref 才能有这种效果，并且在对象 A 已经被析构的情况下，再次 g\_object\_unref 对象 A，那么就会出现段错误。

#####James Henstridge 的方案

为解决引用循环的问题，James Henstridge 给出了一个方案，那就是将 GObject 类及其子类对象的析构过程分为 dispose 阶段与 finalize 阶段。在 dispose 阶段，只解除对象 A 对其所有属性的引用，而在 finalize 阶段释放对象 A 所占用的资源。
**dispose 阶段可被重复执行多次，而 finalize 阶段仅被执行一次** 。

但是，与其说 James Henstridge 给出了一个方案，不如说他给出了一种约定。因为这种方案在 C 语言中是不可能自动实现，它需要 GObject 库的使用者小心谨慎的保证在 dispose 与 finalize 阶段之间不会出现程序错误（通常是段错误）。

例如"[GObject 的信号机制](http://garfileo.is-programmer.com/2011/3/21/gobject-signal.25477.html)"文中的 MyFile 对象的 dispose 代码：

    
    
    static void
    my_file_dispose (GObject *gobject)
    {
            MyFile *self        = MY_FILE (gobject);
            MyFilePrivate *priv = MY_FILE_GET_PRIVATE (self);
            if (priv->file){
                    g_io_channel_unref (priv->file);
                    priv->file = NULL;
            }
            G_OBJECT_CLASS (my_file_parent_class)->dispose (gobject);
    }
    

MyFile 对象的私有属性 file 是一个指向 GIOChannel 类型变量的指针，它与 GObject 库没有丝毫关系，其内存释放实际上可在 finalize 阶段执行，之所以将其放在 dispose 阶段执行，主要是想揭示 James Henstridge 所给出的约定。这种约定就是必须保证 my\_file\_dispose 可被无限次的执行而不出错，所以在 my\_file\_dispose 函数中添加了file 指针有效性判断与野指针消除的代码。

在 GObject 手册中，也有一个 dispose 的示例：

    
    
    static void
    maman_bar_dispose (GObject *gobject)
    {
            MamanBar *self = MAMAN_BAR (gobject);
            if (self->priv->an_object)
            {
                    g_object_unref (self->priv->an_object);
                    self->priv->an_object = NULL;
            }
            G_OBJECT_CLASS (maman_bar_parent_class)->dispose (gobject);
    }
    

从上述代码中可看出，MamanBar 对象的私有属性 an\_object 是一个 GObject 子类对象，也需要指针有效性判断与野指针消除的代码，因为我们必须要保证对象的 dispose 函数可被多次执行。

那么，多次执行对象的 dispose 函数的任务是由 g\_object\_unref 来完成吗？

肯定不是。因为 g\_object\_unref 也不知道该执行多少次 dispose 函数才可以将引用循环打破。

实际上，James Henstridge 所给出的这个约定，并非是让 GObject 自身可以智能的破解引用循环，而是认为 GObject 外的程序能够分析出引用循环的存在，并由它多次执行对象的 dispose 函数。

例如，基于 GObject 的类型管理与引用计数机制，可在 GObject 库之上建立一个内存回收功能的程序库， **GObject库自身的内存管理机制仅仅是方便上层的内存回收库的实现** 而已。至于 GObject 库的使用者，依然要像 C 语言程序员那样，兢兢业业的处理好每一块内存的分配与回收。

#####析构需要向上回溯

在 GObject 子类对象的 dispose 与 finalize 函数中，末尾都有一行比较类似的代码。例如 MyFile 对象的 dispose 函数，有：

    
    
    G_OBJECT_CLASS (my_file_parent_class)->dispose (gobject);
    

MyFile 对象的 finalize 函数，有：

    
    
    G_OBJECT_CLASS (my_file_parent_class)->finalize (gobject);
    

这两行代码主要是"请求" MyFile 父类对象进行析构。

因为 C 语言不是内建支持面向对象，所以继承需要从上至下的进行结构体包含，那么析构就除了要释放自身资源还需要引发父类对象的析构过程，这样才可以彻底消除整条继承链所占用的资源。

向上回溯析构，这还倒好理解，但是 G\_OBJECT\_CLASS (my\_file\_parent\_class) 是什么玩意？在 MyFile 类的实现中，我们从未声明与定义过 my\_file\_parent\_class 这个变量或者宏。

不，其实我们既声明了它，也定义了它，其中的玄机就在 my-file.c 源文件开始部分的 G\_DEFINE\_TYPE 宏之中。如果我们使用命令

    
    
    gcc -E -P my-file.c > my-file-extend.c
    

将 my-file.c 中所有的宏进行展开，可以发现：

    
    
    G_DEFINE_TYPE (MyFile, my_file, G_TYPE_OBJECT);
    

的展开代码为：

    
    
    static void my_file_init (MyFile * self);
    static void my_file_class_init (MyFileClass * klass);
    static gpointer my_file_parent_class = ((void *) 0);
    static void
    my_file_class_intern_init (gpointer klass)
    {
    	my_file_parent_class = g_type_class_peek_parent (klass);
    	my_file_class_init ((MyFileClass *) klass);
    } 
    GType
    my_file_get_type (void)
    {
    	static volatile gsize g_define_type_id__volatile = 0;
    	if (g_once_init_enter (&g_define_type_id__volatile)) {
    		GType g_define_type_id =
    		    g_type_register_static_simple (((GType) ((20) << (2))),
    						   g_intern_static_string
    						   ("MyFile"),
    						   sizeof (MyFileClass),
    						   (GClassInitFunc)
    						   my_file_class_intern_init,
    						   sizeof (MyFile),
    						   (GInstanceInitFunc)
    						   my_file_init,
    						   (GTypeFlags) 0); { { {
    		};
    		}
    		}
    		g_once_init_leave (&g_define_type_id__volatile,
    				   g_define_type_id);
    	}
    	return g_define_type_id__volatile;
    };
    

可以看出 my\_file\_parent\_class 是一个静态的全局指针，它在 my\_file\_class\_intern\_init 函数中指向 MyFile 类的父类结构体。另外，还可以看出 MyFile 类的类结构体初始化函数 my\_file\_class\_init 是由
my\_file\_class\_intern\_init 函数调用的，而后者会被 g\_object\_new 函数调用。

在 my\_file\_class\_init 函数调用之前，将 MyFile 类的父类结构体的地址保存为 my\_file\_parent\_class 指针是有用的。因为我们在 MyFile 类的类结构体初始化函数 my\_file\_class\_init 中覆盖了 MyFile 类所继承的父类结构体的 dispose 与 finaliz 方法：

    
    
    static
    void my_file_class_init (MyFileClass *klass)
    {
            g_type_class_add_private (klass, sizeof (MyFilePrivate));
            GObjectClass *base_class = G_OBJECT_CLASS (klass);
            ... ... ...
            base_class->dispose      = my_file_dispose;
            base_class->finalize     = my_file_finalize;
            ... ... ...
    }
    

而在 MyFile 对象的 dispose 与 finalize 函数中，我们需要将对象的析构向上回溯到其父类，这时如果直接从 MyFile 类的类结构体中提取父类结构体，那么就会出现 MyFile 对象的 dispose 与 finalize 函数的递归调用。由于预先保存了 MyFile 类的父类结构体地址，那么就可以保证回溯析构的顺利进行。

#####**其实，我们做错了！？**

**但是 James Henstridge 的约定，不仅仅是要保证 dispose 函数可被多次执行，还要保证在 dispose 函数执行之后并且在 finalize 函数执行之前，程序不会出错。这意味着 dispose 函数不能影响对象的行为（方法）。**

无论 MyFIle 类对象的 my\_file\_dispose 函数还是 GObject 手册中的 maman\_bar\_dispose 函数的实现，都不符合上述约定。

在 my\_file\_dispose 函数中，我们不仅释放了 GIOChannel 类型指针 file 所指向的内存区域，还消除了野指针。那么在执行
my\_file\_dispose 函数之后，显然所有要使用 file 指针的 MyFile
类对象的方法都会出现段错误。同理，maman\_bar\_dispose 函数也违背了 James Henstridge 的约定。

所以，在 MyFIle 类的设计中 my\_file\_dispose 函数应当是一个空函数，GObject 手册中的 maman\_bar\_dispose 函数也应当如此。

对于 GObject 子类对象的哪些属性应当在 dispose 函数中解除引用，哪些属性应当在 finalize 函数中进行资源释放，全面的判定准则就是：既要允许 dispose 函数可重复执行，还要不影响对象的方法。

因此，James Henstridge 的约定跟废话也差不了多少。因为在 dispose 函数中解除任何一个属性的引用都有可能破坏对象的方法！


<hr>

####<p>原文出处：<a href='http://garfileo.is-programmer.com/2011/3/25/gobject-signal-extra-1.25576.html' target='blank'>GObject 信号机制——信号注册</a></p>

上一篇文档 "[GObject 的信号机制](http://garfileo.is-programmer.com/2011/3/21/gobject-signal.25477.html)"只是挖了一个坑便结束了，本篇尝试填坑，不过也不敢有所保证。因为我也不确定会不会因为被 GObject的信号内幕再次搞晕。

我们先老老实实的阅读 GObject 参考手册的["Concepts /
Signal"部分](http://library.gnome.org/devel/gobject/stable/signal.html)，尽量多获得一些面上的认识。手册中最关键的一句话是：
**每一个信号在注册的时候都要与某种数据类型（包括 GObject 库中的内建类型或 GObject子类类型）存在关联，这种数据类型的使用者需要实现信号与闭包的连接，这样在信号被发射时，闭包会被调用** 。这句话，意味着我们要使用 GObject信号机制，那么就必须要完成两个步骤：第一个步骤是信号注册，主要解决信号与数据类型的关联问题；第二个步骤是信号连接，主要处理信号与闭包的连接问题。本文主要考察信号注册的大致过程。

信号可以与 GObject 库的类型管理机制中"可实例化"的数据类型进行关联，但是 GObject 参考手册建议我们最好是只在 GObject子类类型中使用信号，因为信号跟类/对象在逻辑上比较相符。

有 三个函数可以实现信号注册，即 g\_signal\_newv、g\_signal\_new\_valist 以及 g\_signal\_new，其中
g\_signal\_new\_valist 与 g\_signal\_new 函数皆基于 g\_signal\_newv 函数实现，但是 g\_signal\_new 函数的名字看上去最平易近人。我们不理睬它们内部是如何实现的，只需要理解它们所接受的参数的含义即可。所以，我们可以从分析 g\_signal\_new 函数的参数来理解有关信号注册的一些概念。

g\_signal\_new 函数的声明如下：

    
    
    guint g_signal_new (const gchar        *signal_name,
                        GType               itype,
                        GSignalFlags        signal_flags,
                        guint               class_offset,
                        GSignalAccumulator  accumulator,
                        gpointer            accu_data,
                        GSignalCMarshaller  c_marshaller,
                        GType               return_type,
                        guint               n_params,
                        ...);
    

g\_signal\_new 函数的参数较多，其中每个参数多少都有点深不可测的背景，所以直接理解是非常困难的。我们需要构建实例，从而获得最直观的理解。

首先，我们定义一个 GObject 的子类----SignalDemo 类，其头文件 signal-demo.h 内容如下：

    
    
    #ifndef SIGNAL_DEMO_H
    #define SIGNAL_DEMO_H
    #include <glib-object.h>
    #define SIGNAL_TYPE_DEMO (signal_demo_get_type ())
    #define SIGNAL_DEMO(object) \
            G_TYPE_CHECK_INSTANCE_CAST ((object), SIGNAL_TYPE_DEMO, SignalDemo)
    #define SIGNAL_IS_DEMO(object) \
            G_TYPE_CHECK_INSTANCE_TYPE ((object), SIGNAL_TYPE_DEMO))
    #define SIGNAL_DEMO_CLASS(klass) \
            (G_TYPE_CHECK_CLASS_CAST ((klass), SIGNAL_TYPE_DEMO, SignalDemoClass))
    #define SIGNAL_IS_DEMO_CLASS(klass) \
            (G_TYPE_CHECK_CLASS_TYPE ((klass), SIGNAL_TYPE_DEMO))
    #define SIGNAL_DEMO_GET_CLASS(object) (\
                    G_TYPE_INSTANCE_GET_CLASS ((object), SIGNAL_TYPE_DEMO, SignalDemoClass))
    typedef struct _SignalDemo SignalDemo;
    struct _SignalDemo {
            GObject parent;
    };
    typedef struct _SignalDemoClass SignalDemoClass;
    struct _SignalDemoClass {
            GObjectClass parent_class;
            void (*default_handler) (gpointer instance, const gchar *buffer, gpointer userdata);
    };
    GType signal_demo_get_type (void);
    #endif
    

SignalDemo 类的源文件 signal-demo.c 内容如下：

    
    
    #include "signal-demo.h"
    G_DEFINE_TYPE (SignalDemo, signal_demo, G_TYPE_OBJECT);
    static void
    signal_demo_default_handler (gpointer instance, const gchar *buffer, gpointer userdata)
    {
            g_printf ("Default handler said: %s\n", buffer);
    }
    void
    signal_demo_init (SignalDemo *self)
    {
    }
    void
    signal_demo_class_init (SignalDemoClass *klass)
    {
            klass->default_handler = signal_demo_default_handler;
    }
    

基于此前所写的 [GObject 学习笔记系列](http://garfileo.is-programmer.com/tag/GObject)，上述代码不难理解，无非就是定义了一个 SignalDemo 类，其类结构体中包含了一个函数指针 default\_handler，并在类结构体初始化函数中使该指针指向函数 signal\_demo\_default\_handler。

下面我们开始为 SignalDemo 类注册一个"hello"信号，只需修改一下 SignalDemo 类的类结构体初始化函数，即：

    
    
    void
    signal_demo_class_init (SignalDemoClass *klass)
    {
            klass->default_handler = signal_demo_default_handler;
            g_signal_new ("hello",
                          G_TYPE_FROM_CLASS (klass),
                          G_SIGNAL_RUN_FIRST,
                          G_STRUCT_OFFSET (SignalDemoClass, default_handler),
                          NULL,
                          NULL,
                          g_cclosure_marshal_VOID__STRING,
                          G_TYPE_NONE,
                          1, 
                          G_TYPE_STRING);
    }
    

此时，观察一下 g\_signal\_new 函数的参数：

  * 第 1 个参数是字符串"hello"，它表示信号。
  * 第 2 个参数是 SignalDemo 类的类型 ID，可以使用 G_TYPE_FROM_CLASS 宏从 SignalDemoClass 结构体中获取，也可直接使用 signal-demo.h 中定义的宏 SIGNAL\_TYPE\_DEMO。
  * 第 3 个参数可暂时略过。
  * 第 4 个参数比较关键，它是一个内存偏移量，主要用于从 SignalDemoClass 结构体中找到 default\_handler 指针的位置，可以使用 G\_STRUCT\_OFFSET 宏来获取，也可以直接根据 signal-demo.h 中的 SignalDemoClass 结构体的定义，使用 sizeof (GObjectClass) 来得到内存偏移量，因为 default\_handler 指针之前只有一个 GObjectClass 结构体成员。
  * 第 5 个和第 6 个参数暂时略过。
  * 第 7 个参数设定闭包的  marshal。在文档"[函数指针、回调函数与 GObject 闭包](http://garfileo.is-programmer.com/2011/3/20/function-pointer-and-callback-function-and-closure.25453.html)" 中，描述了 GObject 的闭包的概念与结构，我们可以将它视为回调函数 + 上下文环境而构成的一种数据结构，或者再简单一点，将其视为回调函数。另外，在那篇文档中，我们也对 marshal 的概念进行了一些粗浅的解释。事实上 marshal 主要是用来"翻译"闭包的参数和返回值类型的，它将翻译的结果传递给闭包。之所以不直接调用闭包，而是在其外加了一层 marshal 的包装，主要是方便 GObject 库与其他语言的绑定。例如，我们可以写一个 pyg\_closure\_marshal\_VOID\_\_STRING 函数，其中可以调用 python 语言编写的"闭包"并将其计算结果传递给 GValue 容器，然后再从 GValue 容器中提取计算结果。
  * 第 8 个参数指定 marshal 函数的返回值类型。由于本例的第 7 个参数所指定的 marshal 是 g\_cclosure\_marshal\_VOID\_\_STRING 函数的返回值是 void，而 void 类型在 GObject 库的类型管理系统是 G\_TYPE\_NONE 类型。
  * 第 9 个参数指定 g\_signal\_new 函数向 marshal 函数传递的参数个数，由于本例使用的 marshal 函数是 g\_cclosure\_marshal\_VOID\_\_STRING 函数，g\_signal\_new 函数只向其传递 1 个参数。
  * 第 10 个参数是可变参数，其数量由第 8 个参数决定，用于指定 g\_signal\_new 函数向 marshal 函数传递的参数类型。由于本例使用的 marshal 函数是 g\_cclosure\_marshal\_VOID\_\_STRING 函数，并且 g\_signal\_new 函数只向其传递一个参数，所以传入的参数类型为 G\_TYPE\_STRING（GObject 库类型管理系统中的字符串类型）。

注意，在上述的 g\_signal\_new 函数的第 7 个参数的解释中，我提到了 **闭包** 。事实上，g\_signal\_new 函数并没有闭包类型的参数，但是它在内部的确是构建了一个闭包，而且是通过它的第 4 个参数实现的。因为 g\_signal\_new 函数在其内部调用了 g\_signal\_type\_cclosure\_new 函数，后者所做的工作就是从一个给定的类结构体中通过内存偏移地址获得回调函数指针，然后构建闭包返于
g\_signal\_new 函数。既然 g\_signal\_new 函数的内部是需要闭包的，那么它的第 7～10 个参数自然都是为那个闭包做准备的。

需要注意，g\_cclosure\_marshal\_VOID\_\_STRING 所约定的回调函数类型为：

    
    
    void (*callback) (gpointer instance, const gchar *arg1, gpointer user_data)
    

这表明 g\_cclosure\_marshal\_VOID\_\_STRING 需要使用者向其回调函数传入 3 个参数，其中前两个参数是回调函数的必要参数，而第 3
个参数，即 userdata，是为使用者留的"后门"，使用者可以通过这个参数传入自己所需要的任意数据。由于 GObject 闭包约定了回调函数的第 1
个参数必须是对象本身，所以 g\_cclosure\_marshal\_VOID\_\_STRING 函数实际上要求使用者向其传入 2 个参数，但是在本例中
g\_signal\_new 只向其传递了 1 个类型为 G\_TYPE\_STRING 类型的参数，这有些蹊跷。

这 是因为 g\_signal\_new 函数所构建闭包只是让信号所关联的数据类型能够有一次可以自我表现的机会，即可以在信号被触发的时候，能够自动调用该数据类型的某个方法，例如 SignalDemo 类结构体的 default\_handler 指针所指向的函数。也就是说，SignalDemo 类自身是没有必要向闭包传递那个"userdata"参数的，只是信号的使用者有这种需求。这就是 g\_signal\_new 的参数中只表明它向闭包传递了 1 个 G\_TYPE\_STRING 类型参数的缘故。

上面讲的有些凌乱。现在总结一下：g\_signal\_new 函数内部所构建的闭包，它在被调用的时候，肯定是被传入了 3 个参数，它们被信号所关联的闭包分成了以下层次：

  * 第 1 个参数是信号的默认闭包（信号注册阶段出现）和信号使用者提供的闭包（信号连接阶段出现）所必需的，但是这个参数是隐式存在的，由 g\_signal\_new 暗自向闭包传递。
  * 第 2 个参数是显式的，同时也是信号的默认闭包和信号使用者提供的闭包所必须的，这个参数由信号的发射函数（例如 g\_signal\_emit\_by\_name）向闭包传递。
  * 第 3 个参数也是显式的，且只被信号使用者提供的闭包所关注，这个参数由信号的连接函数（例如 g\_signal\_connect）向闭包传递。

若要真正明白上述内容，我们必须去构建 SignalDemo 类的使用者，即 main.c 源文件，内容如下：

    
    
    #include "signal-demo.h"
    static void
    my_signal_handler (gpointer *instance, gchar *buffer, gpointer userdata)
    {
            g_print ("my_signal_handler said: %s\n", buffer);
            g_print ("my_signal_handler said: %s\n", (gchar *)userdata);
    }
    int
    main (void)
    {
            g_type_init ();
            gchar *userdata = "This is userdata";
            SignalDemo *sd_obj = g_object_new (SIGNAL_TYPE_DEMO, NULL);
            /* 信号连接 */
            g_signal_connect (sd_obj, "hello", 
                              G_CALLBACK (my_signal_handler), 
                              userdata);
            /* 发射信号 */
            g_signal_emit_by_name (sd_obj, 
                                   "hello", 
                                   "This is the second param", 
                                   G_TYPE_NONE);
            return 0;
    }
    

编译 signal-demo.c 与 main.c：

    
    
    $ gcc signal-demo.c main.c -o test $(pkg-config --cflags --libs gobject-2.0)
    

程序运行结果如下：

    
    
    $ ./test
    Default handler said: This is the second param
    my_signal_handler said: This is the second param
    my_signal_handler said: This is userdata
    

结合程序的运行结果，再回顾一下第 1 个实例中的那些乱七八糟的内容，现在应该清晰了许多。

现在，我们再来看一下在第 1 个实例中被我们忽略的 g\_signal\_new 函数的第  3 个参数，我们将其设为
G\_SIGNAL\_RUN\_FIRST。实际上，这个参数是枚举类型，是信号默认闭包的调用阶段的标识，可以是下面 7 种形式中 1 种，也可以是多种组合。

    
    
    typedef enum
    {
      G_SIGNAL_RUN_FIRST = 1 << 0,
      G_SIGNAL_RUN_LAST = 1 << 1,
      G_SIGNAL_RUN_CLEANUP = 1 << 2,
      G_SIGNAL_NO_RECURSE = 1 << 3,
      G_SIGNAL_DETAILED = 1 << 4,
      G_SIGNAL_ACTION = 1 << 5,
      G_SIGNAL_NO_HOOKS = 1 << 6
    } GSignalFlags;
    

这个参数被设为 G\_SIGNAL\_RUN\_FIRST，表示信号的默认闭包要先于信号使用者的闭包被调用，这个观察一下上面的 test 程序的输出结果便可知悉。如果我们将这个参数设为 G\_SIGNAL\_RUN\_LAST，则表示信号的默认闭包要迟于信号使用者的闭包而被调用。对于这个参数的理解暂且到此为止，后面在讲述信号连接的时候还会再次谈到它。

#####小结

现在，对信号注册的主要过程已有所了解，但是依 g\_signal\_new 函数的第 5 个与第 6 个参数，对于它们，我现在还不知道如何为其构建实例，以后再说吧。若你读到此处并且知道它们的用法，还望不吝赐教。


<hr>


####<p>原文出处：<a href='http://garfileo.is-programmer.com/2011/3/27/gobject-signal-extra-2.25621.html' target='blank'>GObject 信号机制——信号 Accumulator</a></p>

在文档 [1] 中，从外围对 GObject 信号注册的过程进行了初步分析。生命不息，折腾不止，我们应当以 [ Adrian Hands ](http://linuxtoy.org/archives/2010-free-software-awards.html) 大叔为榜样。所以，本文继续解决文档 [1] 中遗留的问题，即 g_signal_new 函数的第 5 个与第 6 个参数的含义。

首先，再次回放一下 g_signal_new 函数的众参数：

    
    
    guint g_signal_new (const gchar        *signal_name,
                        GType               itype,
                        GSignalFlags        signal_flags,
                        guint               class_offset,
                        GSignalAccumulator  accumulator,
                        gpointer            accu_data,
                        GSignalCMarshaller  c_marshaller,
                        GType               return_type,
                        guint               n_params,
                        ...);
    

其中，第 5 个参数是 accumulator，其类型为 GSignalAccumulator，这是一个函数指针类型，即：

    
    
    gboolean (*GSignalAccumulator) (GSignalInvocationHint *ihint,
                                    GValue *return_accu,
                                    const GValue *handler_return,
                                    gpointer data);
    

g\_signal\_new 的第 6 个参数 accu\_data 会被 g\_signal\_new 传递于 accumulator 所指向的函数，作为后者的第
4 个参数 data。

至此，从字面上对 g\_signal\_new 函数的第 5 个与第 6 个参数的含义便分析完毕了。当然，这远远不够。因为现在还不是很清楚
accumulator 这个函数指针的作用。

简单的说，accumulator
所指向的函数会在信号所连接的每个闭包（包括在信号注册阶段生成的信号默认闭包，以及信号连接阶段中信号使用者所提供的闭包）执行之后被调用，它的主要功能就是收集
**信号所连接的各个闭包的返回值** （简称" **信号返回值** "）。

至于 accumulator 这个单词的汉译，在文档 [1] 的评论中 [pingf](http://pingf.is-programmer.com/) 有一些建议。在此，我就不翻译了，而直呼其名。

为了更直观的理解信号 accumulator 的作用，可以对文档 [1] 中的实例进行一些修改，构建一个新的实例。

首先，照抄 SignalDemo 类的头文件 signal-demo.h：

    
    
    #ifndef SIGNAL_DEMO_H
    #define SIGNAL_DEMO_H
    #include <glib-object.h>
    #define SIGNAL_TYPE_DEMO (signal_demo_get_type ())
    #define SIGNAL_DEMO(object) \
            G_TYPE_CHECK_INSTANCE_CAST ((object), SIGNAL_TYPE_DEMO, SignalDemo)
    #define SIGNAL_IS_DEMO(object) \
            G_TYPE_CHECK_INSTANCE_TYPE ((object), SIGNAL_TYPE_DEMO))
    #define SIGNAL_DEMO_CLASS(klass) \
            (G_TYPE_CHECK_CLASS_CAST ((klass), SIGNAL_TYPE_DEMO, SignalDemoClass))
    #define SIGNAL_IS_DEMO_CLASS(klass) \
            (G_TYPE_CHECK_CLASS_TYPE ((klass), SIGNAL_TYPE_DEMO))
    #define SIGNAL_DEMO_GET_CLASS(object) (\
                    G_TYPE_INSTANCE_GET_CLASS ((object), SIGNAL_TYPE_DEMO, SignalDemoClass))
    typedef struct _SignalDemo SignalDemo;
    struct _SignalDemo {
            GObject parent;
    };
    typedef struct _SignalDemoClass SignalDemoClass;
    struct _SignalDemoClass {
            GObjectClass parent_class;
            void (*default_handler) (gpointer instance, const gchar *buffer, gpointer userdata);
    };
    GType signal_demo_get_type (void);
    #endif
    

然后对文档 [1] 中的 SignalDemo 类的源文件 signal-demo.c 进行一些修改，如下：

    
    
    #include "signal-demo.h"
    G_DEFINE_TYPE (SignalDemo, signal_demo, G_TYPE_OBJECT);
    #define g_marshal_value_peek_string(v)   (v)->data[0].v_pointer
    #define g_marshal_value_peek_pointer(v)  (v)->data[0].v_pointer
    void
    g_cclosure_user_marshal_INT__STRING (GClosure     *closure,
                                         GValue       *return_value G_GNUC_UNUSED,
                                         guint         n_param_values,
                                         const GValue *param_values,
                                         gpointer      invocation_hint G_GNUC_UNUSED,
                                         gpointer      marshal_data)
    {
            typedef gint (*GMarshalFunc_INT__STRING) (gpointer     data1,
                                                      gpointer     arg_1,
                                                      gpointer     data2);
            register GMarshalFunc_INT__STRING callback;
            register GCClosure *cc = (GCClosure*) closure;
            register gpointer data1, data2;
            gint v_return;
            g_return_if_fail (return_value != NULL);
            g_return_if_fail (n_param_values == 2);
            if (G_CCLOSURE_SWAP_DATA (closure)){
                    data1 = closure->data;
                    data2 = g_value_peek_pointer (param_values + 0);
            }
            else{
                    data1 = g_value_peek_pointer (param_values + 0);
                    data2 = closure->data;
            }
            callback = (GMarshalFunc_INT__STRING) (marshal_data ? marshal_data : cc->callback);
            v_return = callback (data1,
                                 g_marshal_value_peek_string (param_values + 1),
                                 data2);
            g_value_set_int (return_value, v_return);
    }
    gboolean
    signal_demo_accumulator (GSignalInvocationHint *ihint,
                             GValue *return_accu,
                             const GValue *handler_return,
                             gpointer data)
    {
            g_print ("%d\n", g_value_get_int (handler_return));
            g_print ("%s\n", (gchar *)data);
            return TRUE;
    }
    static gint
    signal_demo_default_handler (gpointer instance, const gchar *buffer, gpointer userdata)
    {
            g_printf ("Default handler said: %s\n", buffer);
            return 2;
    }
    static void
    signal_demo_init (SignalDemo *self)
    {
    }
    void
    signal_demo_class_init (SignalDemoClass *klass)
    {
            klass->default_handler = signal_demo_default_handler;
            g_signal_new ("hello",
                          G_TYPE_FROM_CLASS (klass),
                          G_SIGNAL_RUN_LAST,
                          G_STRUCT_OFFSET (SignalDemoClass, default_handler),
                          signal_demo_accumulator,
                          "haha haha",
                          g_cclosure_user_marshal_INT__STRING,
                          G_TYPE_INT,
                          1,
                          G_TYPE_STRING);
    }
    

相对于文档 [1] 中的 signal-demo.c，上述代码主要增加了两个宏和一个函数：

    
    
    #define g_marshal_value_peek_string(v)   (v)->data[0].v_pointer
    #define g_marshal_value_peek_pointer(v)  (v)->data[0].v_pointer
    void g_cclosure_user_marshal_INT__STRING ( ... );
    

这些代码不需要手工编写，我们可以使用文档 [2] 中提及的 glib-genmarshal 工具生成它们。

g\_cclosure\_user\_marshal\_INT\_\_STRING 函数（其返回值为 gint 类型）是作为信号默认闭包的 marshal 使用的，用于替换文档 [1] 中的 g\_cclosure\_marshal\_VOID\_\_STRING 函数（无返回值），即：

    
    
    /* signal_demo_class_init 函数内部 */
            g_signal_new ("hello",
                          G_TYPE_FROM_CLASS (klass),
                          G_SIGNAL_RUN_LAST,
                          G_STRUCT_OFFSET (SignalDemoClass, default_handler),
                          signal_demo_accumulator,
                          NULL,
                          g_cclosure_user_marshal_INT__STRING,
                          G_TYPE_INT,
                          1,
                          G_TYPE_STRING);
    

之所以替换文档 [1] 中的 g\_cclosure\_marshal\_VOID\_\_STRING 函数，是因为信号的 accumulator 需要信号存在返回值。

另外，上述代码中将文档 [1] 中 g\_signal\_new 函数的第 3 个参数由"G\_SIGNAL\_RUN\_FIRST" 修改为"G\_SIGNAL\_RUN\_LAST"，表示信号默认闭包设置为信号使用者的闭包调用结束后方被调用，也可以修改为"G\_SIGNAL\_RUN\_FIRST | G\_SIGNAL\_RUN\_LAST"，这表示信号默认闭包会在信号使用者的闭包调用之前与之后被调用。至于为什么需要如此修改，还是暂且作为一个悬念留给番外篇 (3) 去解释吧，我们尽量遵守 KISS 原则，一篇文章只解决一个问题。

下面开始修改文档 [1] 中的 SignalDemo 类的调用者，即 main.c 文件。

    
    
    #include "signal-demo.h"
    static gint
    my_signal_handler (gpointer *instance, gchar *buffer, gpointer userdata)
    {
            g_print ("my_signal_handler said: %s\n", buffer);
            g_print ("my_signal_handler said: %s\n", (gchar *)userdata);
    	return 1;
    }
    int
    main (void)
    {
            g_type_init ();
            gchar *userdata = "This is userdata";
            SignalDemo *sd_obj = g_object_new (SIGNAL_TYPE_DEMO, NULL);
            gint val = 0;
            /* 信号连接 */
            g_signal_connect (sd_obj, "hello",
                              G_CALLBACK (my_signal_handler),
                              userdata);
            /* 发射信号 */
            g_signal_emit_by_name (sd_obj,
                                   "hello",
                                   "This is the second param", &val);
            return 0;
    }
    

相对于文档 [1] 中的 main.c，上面代码所做的变动只有两处：

  * my\_signal\_handler 函数被重新定义为带有 gint 类型返回值的函数。
  * g\_signal\_emit\_by\_name 函数的调用多出一个无用的参数 val。之所以说这个参数没有用，是因为在本文的示例中，我们使用了信号 accumulator。如果我们没有使用信号 accumulator 的话，这个 val 参数可以保存最后一个信号闭包的返回值。虽然它在本文中没有用，但是它的存在是有意义的，可保证本文的示例不会出现段错误。

编译这个新的示例并执行编译结果：

    
    
    $ gcc signal-demo.c main.c -o test $(pkg-config --cflags --libs gobject-2.0)
    $ ./test
    my_signal_handler said: This is the second param
    my_signal_handler said: This is userdata
    1
    haha haha
    Default handler said: This is the second param
    2
    haha haha
    

根据 test 程序的输出结果去印证上述的程序源码，信号 accumulator 的工作背景及其过程便昭然在目。

<hr>

####<p>原文出处：<a href='http://garfileo.is-programmer.com/2011/4/4/gobject-signal-connection.25847.html' target='blank'>GObject 信号机制——信号连接</a></p>

文档 [1, 2] 讲述了 GObject 信号注册的相关细节，本文进一步分析信号与闭包的关联问题，即信号连接。

事实上，在文档 [1, 2] 中我们已对信号连接有所接触，例如：

    
    
    g_signal_connect (sd_obj, "hello",
                              G_CALLBACK (my_signal_handler),
                              userdata);
    

g\_signal\_connect 是一个宏，用于信号与回调函数的连接。在这个宏的内部，通过 g\_signal\_connect\_data 函数将回调函数封装为闭包，并关联到指定的信号。

使用 g\_signal\_connect 为信号设定的闭包会在信号的默认闭包执行之前被调用，且 g\_signal\_connect 的第 4 个参数是用户传递给闭包的参数，它是一个 void * 类型的万能指针。

还有一个宏 g\_signal\_connect\_after，它为信号设定的闭包会在信号的默认闭包执行之后被调用。

注意，上文接连两次提到 "信号的默认闭包"，文档 [1] 对此有较为详细的阐释，即信号注册阶段与信号相连接的闭包，通常是信号所属对象的某个方法。

对于 GObject 的普通用户而言，上述知识已足够。

在文档 [3] 中，为了能够在 GtkWidget 对象对应的 X 窗口构建完毕后的某个恰当的时机正确生成 GLXContext 渲染环境，我们选择了 "show" 信号。事实上，GtkWidget 对象有一个"realize"信号，与该信号连接的闭包会在 GtkWidget 对象的 X 窗口创建时被调用。如果我们使用 g\_signal\_connect 连接 "realize" 信号，那么我们定义的闭包会先于"realize"信号的默认闭包（即 GtkWidget 对象的 realize 方法）被调用，因此不能正确生成 GLXContext 渲染环境，这就是我们为什么选择了"show"信号的主要原因。但是，如果我们使用 g\_signal\_connect\_after 连接"realize"信号，那么 GtkWidget 对象的 realize 方法会先于我们的闭包被调用，因此也可以正确的生成 GLXContext渲染环境。













