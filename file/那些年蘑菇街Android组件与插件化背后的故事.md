 
<!--BEGIN_DATA
{
    "create_date": "2016-12-18 23:06", 
    "modify_date": "2016-12-18 23:06", 
    "is_top": "0", 
    "summary": "那些年蘑菇街Android组件与插件化背后的故事", 
    "tags": "Android", 
    "file_name": "那些年蘑菇街Android组件与插件化背后的故事.md"
}
END_DATA-->

####<p>原文出处：<a href='http://mogu.io/117-117' target='blank'>那些年蘑菇街Android组件与插件化背后的故事 -- 插件篇(一)</a></p>


###插件化的基石 -- apk动态加载

随着我街业务的蓬勃发展，产品和运营随时上新功能新活动的需求越来越强烈，经常可以听到“有个功能我想周x上，行不行”。行么？当然是不行啦，上新功能得发新版本啊，到时候费时费力打乱开发节奏不说，覆盖率也是个问题。苏格拉底曾经说过：“现在移动端的主要矛盾是产品日益增长的功能需求与平台落后的发布流程之间的矛盾”。

当然，作为一个靠谱的程序猿，我们就是为了满足产品的需求而存在的(正义脸)。于是在一个阳光明媚的早晨，吃完公司的免费早餐后，我和小强、叶开，决定做一个完善的Android动态加载框架。

Android动态加载技术在蘑菇街的第一次实践，还是在14年的时候，使用的就是之前网上广(tu)为(du)流(si)传(fang)的方式，这种方式有一个重大缺陷，就是插件内部对资源的访问只能通过自己定义的方式，包括对layout文件的inflate等，使用getResouces的方式，分分钟crash给你看，而且内部实现有些复杂，容易出现莫名其妙的ResourcesNotFound错误。在一段时间的使用之后，始终无法大面积推广，原因就是对开发人员来说，写一个“正常”的模块和写一个动态加载模块，写法是不一样的。这件事一直如哏在喉，如果这个框架无法做到对开发业务的同学们透明，那么就很难推广开去。如何做到对业务开发者透明呢，最重要的是对于各类系统api的使用，尤其是Android四大组件的使用和资源访问，都要遵循系统提供的方式。

抛开上面的东西，从头开始讲述一下动态加载的原理：  
**_Android应用程序的.java文件在编译期会通过javac命令编译成.class文件，最后再把所有的.class文件编译成.dex文件放在.apk包里面。那么动态加载就是在运行时把插件apk直接加载到classloader里面的技术。_**

看完上面的原理，不知道你有没有什么疑问，反正我是有的。

  1. 如何加载插件里面的.dex文件。
  2. apk里面的资源怎么办。

上面两个问题是动态加载框架最重要的两点，无法动态安装dex或资源文件的动态加载框架都是耍流氓。我们在实现这个框架的时候同样也遇到了这两个问题。

####如何动态加载插件代码：

关于代码加载，系统提供了[DexClassLoader](https://developer.android.com/reference/dalvik/system/DexClassLoader.html)来加载插件代码。开发者可以对每一个插件分配一个[DexClassLoader](https://developer.android.com/reference/dalvik/system/DexClassLoader.html)(这是目前最常见的一种方式)，也可以动态得把插件加载到当前运行环境的classloader中。蘑菇街采用的是后者，这种方式可以有效的防止各种莫名其妙的[ClassCastException]
(https://developer.android.com/reference/java/lang/ClassCastException.html)，当你在crash后台看到各种 A cast A错误而欲哭无泪的时候，我想你会喜欢上这种方式。  
事情当然不会这么简单，系统提供的DexClassloader对外api中，只有一种方式可以向类加载器指定加载路径。就是在构造函数中传入apk/zip/dex路径。这完全不符合我们“动态”的原则，难道每次加载一个插件，都必须重新实例化一个类加载器出来吗？这个时候我们想到了google提供的multidex插件，这个插件旨在帮助函数超过65536上限的应用在编译期切割class到多个dex文件中。经过观察发现，5.0以下的Android系统，在应用安装的时候只认classes.dex文件，并在安装期对这个dex文件进行opt操作，生成的odex文件放在/data/dalivk-cache里面。那么剩下classes(N)
.dex怎么办呢，答案就是如果在编译期使用multidex插件的话，开发者还需要让自己的Application继承[MultiDexApplication]
(https://developer.android.com/reference/android/support/multidex/MultiDexApplication.html)，这样说起来，这个[MultiDexApplication](https://developer.android.com/reference/android/support/multidex/MultiDexApplication.html)应该就有加载剩下的classes(N).dex的能力了。查看[MultiDexApplication](https://developer.android.com/reference/android/support/multidex/MultiDexApplication.html)代码，果然找到了线索：

    
    
    public class MultiDexApplication extends Application {
      @Override
      protected void attachBaseContext(Context base) {
        super.attachBaseContext(base);
        MultiDex.install(this);
      }
    }
    

可以看到，它在attachBaseContext函数调用了support包中[MultiDex](https://developer.android.com/reference/android/support/multidex/MultiDex.html)类的install函数来安装classes(N).dex，于是都是应用层代码，它能动态安装那表示我们也可以。有了以上的分析，剩下要做的就只是去扒一扒install这个函数了。

* * *

####如何动态加载插件资源：

我们在开发的时候，当有需要用到资源的地方，可以直接调用[Context](https://developer.android.com/reference/android/content/Context.html)的getResources()函数返回[Resources](https://developer.android.com/reference/android/content/res/Resources.html)的来访问打包在apk中的资源文件。在研究如何
动态添加资源到系统的[Resources](https://developer.android.com/reference/android/content/res/Resources.html)对象的时候，有必要先了解一下[Resources](https://developer.android.com/reference/android/content/res/Resources.html)本身是如何访问到资源的。

查看系统的[Resources](https://developer.android.com/reference/android/content/res/Resources.html)源码，我们发现这个类主要做了两件事，首当其冲的当然是访问资源，另外一件就是管理资源配置信息。对于资源的动态加载来说，我们关心的是
它如何做第一件事的。**_实际上，[Resources](https://developer.android.com/reference/android/c
ontent/res/Resources.html)对资源的访问，全部代理给了另一个重要的对象[AssetManager](https://develope
r.android.com/reference/android/content/res/AssetManager.html)_**。那么问题转化成了，[As
setManager](https://developer.android.com/reference/android/content/res/AssetManager.html)是如何做到对资源的访问的。[Resources](https://developer.android.com/reference/android/content/res/Resources.html)类在它的构造函数里对[AssetManager](https://developer.android.com/reference/android/content/res/AssetManager.html)做了一些重要的初始化:

    
    
    public Resources(AssetManager assets, DisplayMetrics metrics, Configuration config,
                CompatibilityInfo compatInfo, IBinder token) {
            mAssets = assets;
            mMetrics.setToDefaults();
            if (compatInfo != null) {
                mCompatibilityInfo = compatInfo;
            }
            mToken = new WeakReference<IBinder>(token);
            updateConfiguration(config, metrics);
            assets.ensureStringBlocks();
    }
    

其中的重点就是调用了[AssetManager](https://developer.android.com/reference/android/content/res/AssetManager.html)对象的ensureStringBlocks()函数，这个函数的实现如下:

    
    
    /*package*/ final void ensureStringBlocks() {
        if (mStringBlocks == null) {
            synchronized (this) {
                if (mStringBlocks == null) {
                    makeStringBlocks(sSystem.mStringBlocks);
                }
            }
        }
    }
    

函数先判断mStringBlocks变量是否为空，如果不为空的话，表示需要被初始化，于是调用makeStringBlocks函数初始化mStringBloc
ks:

    
    
    /*package*/ final void makeStringBlocks(StringBlock[] seed) {
        final int seedNum = (seed != null) ? seed.length : 0;
        final int num = getStringBlockCount();
        mStringBlocks = new StringBlock[num];
        if (localLOGV) Log.v(TAG, "Making string blocks for " + this
                + ": " + num);
        for (int i=0; i<num; i++) {
            if (i < seedNum) {
                mStringBlocks[i] = seed[i];
            } else {
                mStringBlocks[i] = new StringBlock(getNativeStringBlock(i), true);
            }
        }
    }
    

这里的mStringBlocks对象是一个StringBlock数组，这个类被标记为@hide，表示应用层根本不需要关心它的存在。那么它是做什么用的呢，它就
是[AssetManager](https://developer.android.com/reference/android/content/res/AssetManager.html)能够访问资源的奥秘所在，[AssetManager](https://developer.android.com/refer
ence/android/content/res/AssetManager.html)所有访问资源的函数，例如getResourceTextArray()，
都最终通过StringBlock再代理到native进行访问的。看到这里，依然没有任何看到能够指示为什么开发者可以访问自己应用的资源，那么我们再看得前面一点，看看传入[Resources](https://developer.android.com/reference/android/content/res/Resources.html)的构造函数之前，asset参数是不是被“做过手脚”。函数调用辗转到ResourceManager的getTopLevelReso
urces函数:

    
    
    public Resources getTopLevelResources(String resDir, String[] splitResDirs,
                    String[] overlayDirs, String[] libDirs, int displayId,
                    Configuration overrideConfiguration, CompatibilityInfo compatInfo, IBinder token) {
        ...
        AssetManager assets = new AssetManager();
        if (resDir != null) {
            if (assets.addAssetPath(resDir) == 0) {
                  return null;
            }
        }
        ...
    }
    

函数代码有点多，截取最重要的部分，那就是系统通过调用[AssetManager](https://developer.android.com/reference/android/content/res/AssetManager.html)的addAssetPath函数，将需要加载的资源路径加了进去。addAssetPath函数返回一个int类型，它指示了每个被添加的资源路径在native层一个数组中的位置，这个数组保存了系统资源路径(framework-res.apk)，和应用自己添加的所有的资源路径。再回过头看makeStringBlocks函数，就豁然开朗了：

  1. makeStringBlocks函数的参数也是一个StringBlock数组，它表示系统资源，首先它调用getStringBlockCount函数得到当前应用所有要加载的资源路径数量。
  2. 然后进入循环，如果属于系统资源，就直接用传入参数seed中的对象来赋值。
  3. 如果是应用自己的资源，就实例化一个新的StringBlock对象来赋值。并在StringBlock的构造函数中调用getNativeStringBlock函数来获取一个native层的对象指针，这个指针被java层StringBlock对象用来调用native函数，最终达到访问资源的目的。

有兴趣的同学可以继续深入native层的源码，可以看到不管是addAssetPath函数还是makeStringBlocks函数，使用的都是native层同一个数组，这样，这两个函数就被关联了起来。

到这里，我们已经知道了如何动态添加资源路径的“秘密”。

* * *

解决了以上两个问题，一个基本满足要求的动态加载框架就被搭了起来。  
关于如何延迟加载组件的问题，请期待下一期的**那些年蘑菇街Android组件与插件化背后的故事**。

ps:查看native层Resources.cpp的代码，我们发现，Android5.0及以上版本是真正的支持动态添加资源路径到系统[Resources](https://developer.android.com/reference/android/content/res/Resources.html)对象,
直接反射调用getAsset.addAssetPath即可。5.0以下版本只是“伪动态”，需要自己重新实例化一个[Resources](https://developer.android.com/reference/android/content/res/Resources.html)对象和[AssetMana
ger](https://developer.android.com/reference/android/content/res/AssetManager.html)对象，添加完所有需要的资源路径后，替换运行环境的[Resources](https://developer.android.com/reference/android/content/res/Resources.html)对象才可以做到“动态”。这个跟5.0以下的Resources.cpp在初始化完成之后，无法动态扩展resTable有关。



<hr>




####<p>原文出处：<a href='http://mogu.io/119-119' target='blank'>那些年蘑菇街Android组件与插件化背后的故事 -- 插件篇(二)</a></p>

这阵子比较忙，组里的赤(xing)木(xing)大(dui)神(zhang)一直催我写第二篇。今天抽出空来，把这篇补上。  

上一篇已经交代了如何把一个插件apk动态加载到内存中，并做到可用。这篇介绍的是，我们如何在“合适”的时间加载某个插件。  

试想一个理想化的场景，一个app中，所有的模块都是一个个的插件，我们不可能在应用初始化的时候把所有的插件全部加载，dex optimize时长都能把人弄哭。 
 
那么就得找一个时间点，使我们可以知道，某个插件第一次被用到是什么时候，只要在这个时间加载这个插件就好。  

分析一下插件主要有哪些东西构成：

  1. 首先是逻辑代码，这些函数有些是自己插件内部用的，有些是外部其他插件也要用的。
  2. 页面，各种Activity。

Ok，我们一个个得解决上面的问题

###对外函数

在这种情况下，如果一个插件A需要调用插件B的函数，我们可以去检查插件B是否被加载过，如果还未加载，就加载它。  

这里不知道大家会不会有个疑问，我们是如何感知到插件A调用了插件B中的函数了呢？  
首先有个天然性的隔离就是，插件与插件之间在开发的时候，都是独立工程的，它们之间不应该存在直接的函数调用。  

然后，我们需要一个中间管理框架，用来统一处理插件间的函数(服务)调用，这也是蘑菇街组件管理框架所做的很重要的一件事。所有的插件/组件之间的函数(服务)调用，
必须过管理框架中转，最后由框架进行实际的调用。  

由于管理框架是一个通用框架，并不针对某个插件，所以插件所能提供的对外函数，要使用配置的方式告知外部和管理框架，未在配置定义的函数是不允许被调用的。
  
于是我们可以拦截到插件间的函数(服务)调用了，这是第一个可以检测到某个插件是否开始被使用的地方。

###页面，Activity

另外一种常见情况就是插件A需要启动插件B中的一个Activity。为了让开发插件的同学最小化得感知自己在开发一个插件，业务开发的同学依然可以使用任何系统提供的任何启动Activity的方式。但是作为需要知道启动了哪个Activity以便去安装某个插件的管理框架来说，需要对这个操作进行拦截。 
 
又到了read the fu*k source code的时间啦~  

首先我们从一个常见的startActivity函数调用开始，不论调用了哪个Context的startActivity函数，最后都会调用到ContextImpl的startActivity函数：

    
    
    @Override
    public void startActivity(Intent intent, Bundle options) {
        ...
        mMainThread.getInstrumentation().execStartActivity(
            getOuterContext(), mMainThread.getApplicationThread(), null,
            (Activity)null, intent, -1, options);
    }
    

看到它最后调用了mMainThread.getInstrumentation().execStartActivity来启动一个Activity，mMainThread是一个ActivityThread类型的对象，getInstrumentation函数返回一个Instrumentation类型的对象。顺理成章得，接下去是Instrumentation类的execStartActivity函数：

    
    
    public ActivityResult execStartActivity(
            Context who, IBinder contextThread, IBinder token, Activity target,
            Intent intent, int requestCode, Bundle options) {
        ...
        try {
            ...
            int result = ActivityManagerNative.getDefault()
                .startActivity(whoThread, who.getBasePackageName(), intent,
                        intent.resolveTypeIfNeeded(who.getContentResolver()),
                        token, target != null ? target.mEmbeddedID : null,
                        requestCode, 0, null, options);
            checkStartActivityResult(result, intent);
        } catch (RemoteException e) {
        }
        return null;
    }
    

调用到了ActivityManagerNative的startActivity函数，这是一个IPC调用，用于向远端的ActivityManagerService发起一个start activity的请求。当然大家可以拦截Instrumentation的execStartActivity函数，因为通过函数的入参，
已经知道了应用层请求启动哪个Activity了。但拦截这个函数有几个弊端，

  1. 第一就是execStartActivity函数只是启动Activity的某一个函数，类似的函数还有一些，如果我们都把它们拦截了，显得有点冗余了。
  2. 第二个弊端就是这里只是向ActivityManagerService发起一个IPC请求，具体这个Activity能否被启动，都还是未知数，如果在这里拦截而这个Activity，也会造成一些浪费和不确定性。

另外我们可以非常肯定得认为，在整个Activity启动的过程中，实例化某个具体Activity的操作一定是在当前应用程序进程进行的，不可能由远端的ActivityManagerService来执行，因为只有当前应用程序进行的内存中，才会有某个具体Activity的类存在。  

于是我们在ActivityThread类中找到了最后实例化某个Activity类的函数

    
    
    private Activity performLaunchActivity(ActivityClientRecord r, Intent customIntent) {
        ...
        Activity activity = null;
        try {
            java.lang.ClassLoader cl = r.packageInfo.getClassLoader();
            activity = mInstrumentation.newActivity(
                    cl, component.getClassName(), r.intent);
            StrictMode.incrementExpectedActivityCount(activity.getClass());
            r.intent.setExtrasClassLoader(cl);
            r.intent.prepareToEnterProcess();
            if (r.state != null) {
                r.state.setClassLoader(cl);
            }
        } catch (Exception e) {
            if (!mInstrumentation.onException(activity, e)) {
                throw new RuntimeException(
                    "Unable to instantiate activity " + component
                    + ": " + e.toString(), e);
            }
        }
        ...
        return activity;
    }
    

最关键的一句，就是调用mInstrumentation.newActivity来返回一个Activity对象，所以这里是最后实例化的地方，Instrumentation类的newActivity也就是我们需要拦截下来的操作。简单明了，只需要复写这个函数然后把自己的Instrumentation对象替换成运行上下文的就可以了~

到这里为止，Activity启动也被管理框架感知到了，自然可以去检测安装Activity所属的插件了。

* * *

以上就是蘑菇街组件与插件管理框架中插件安装的逻辑。
