 
<!--BEGIN_DATA
{
    "create_date": "2017-04-06 11:13", 
    "modify_date": "2017-04-06 11:13", 
    "is_top": "0", 
    "summary": "iOS中书写代码规范35条小建议", 
    "tags": "iOS", 
    "file_name": "iOS中书写代码规范35条小建议.md"
}
END_DATA-->

####<p>原文出处：<a href='http://www.jianshu.com/p/71fdd1ae714c' target='blank'>iOS中书写代码规范35条小建议</a></p>

##iOS中书写代码规范35条小建议:


1.精简代码,
返回最后一句的值，这个方法有一个优点，所有的变量都在代码块中，也就是只在代码块的区域中有效，这意味着可以减少对其他作用域的命名污染。但缺点是可读性比较差

    
    
    NSURL *url = ({ NSString *urlString = [NSString stringWithFormat:@"%@/%@", baseURLString, endpoint];
    [NSURL URLWithString:urlString];
    });

2.关于编译器：关闭警告：

    
    
    #pragma clang diagnostic push
    #pragma clang diagnostic ignored "-Warc-performSelector-leaks"
    [myObj performSelector:mySelector withObject:name];
    #pragma clang diagnostic pop

3.忽略没用的变量

    
    
    #pragma unused (foo)
    明确定义错误和警告
    #error Whoa, buddy, you need to check for zero here!
    #warning Dude, don't compare floating point numbers like this!

4.避免循环引用

  * 如果【block内部】使用【外部声明的强引用】访问【对象A】, 那么【block内部】会自动产生一个【强引用】指向【对象A】
  * 如果【block内部】使用【外部声明的弱引用】访问【对象A】, 那么【block内部】会自动产生一个【弱引用】指向【对象A】
    
    
	    __weak typeof(self) weakSelf = self;
	    dispatch_block_t block = ^{
	       [weakSelf doSomething]; // weakSelf != nil
	    // preemption, weakSelf turned nil
	    [weakSelf doSomethingElse]; // weakSelf == nil
	    };
	    最好这样调用：
	    __weak typeof(self) weakSelf = self;
	    myObj.myBlock = ^{
	    __strong typeof(self) strongSelf = weakSelf;
	    if (strongSelf) {
	         [strongSelf doSomething]; // strongSelf != nil
	    // preemption, strongSelf still not nil（抢占的时候，strongSelf 还是非 nil 的)
	    [strongSelf doSomethingElse]; // strongSelf != nil }
	    else { // Probably nothing... return;
	    }
	    };

5.宏要写成大写,至少要有大写,全部小写有时候书写不提示参数;

6.建议书写枚举模仿苹果——在列出枚举内容的同时绑定了枚举数据类型NSUInteger，这样带来的好处是增强的类型检查和更好的代码可读性,示例:

    
    
    // 不推荐写法
    typedef enum{
        UIControlStateNormal       = 0,
        UIControlStateHighlighted  = 1 << 0,
        UIControlStateDisabled     = 1 << 1,
    } UIControlState;
    
    
    // 推荐写法
    typedef NS_OPTIONS(NSUInteger, UIControlState) {
        UIControlStateNormal       = 0,
        UIControlStateHighlighted  = 1 << 0,
        UIControlStateDisabled     = 1 << 1,
    };

7.建议加载xib,xib名称用NSStringFromClass(),避免书写错误

    
    
    // 推荐写法
     [self.tableView registerNib:[UINib nibWithNibName:NSStringFromClass([DXRecommendTagVCell class]) bundle:nil] forCellReuseIdentifier:ID];
    
    
    // 不推荐写法
     [self.tableView registerNib:[UINib nibWithNibName:@"DXRecommendTagVCell" bundle:nil] forCellReuseIdentifier:ID];

8.场景需求:在继承中,凡是要求子类重写父类的方法必须先调用父类的这个方法进行初始化操作;建议:父类的方法名后面加上NS_REQUIRES_SUPER;
子类重写这个方法就会自动警告提示要调用这个super方法,示例代码

    
    
    // 注意:父类中的方法加`NS_REQUIRES_SUPER`,子类重写才有警告提示
    - (void)prepare NS_REQUIRES_SUPER;

9.建议书写属性名不要和系统一样,避免发生莫名其妙的问题;特别注意的是label;属性名不要写成`textLabel`

10.项目中添加plist类型文件,不要命名为info.plist,以防止和系统自带的文件重名,发生莫名其妙的问题;

11.如果控制器已经加载过,就不用再次加载,优化性能

    
    
        if (vc.isViewLoaded) return;

12.id类型属性不能用点语法,调用get方法只能用中括号调用,[id 方法名],利用iOS9新特性泛型就可以; 比如数组;

    
    
    @property (nonatomic,strong) NSMutableArray<DXTopics *> *topicsM;

13.如果不是属性,尽量不要点语法,一个老程序员的建议;

14.使用第三方框架,尽量不要更改内部文件,而应该再次封装,个性定制;

15.判断if书写方式  
建议这样写

    
    
    - (CGFloat)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath
    {
        if (indexPath.row == 0) return 44;
        if (indexPath.row == 1) return 80;
        if (indexPath.row == 2) return 50;
        return 44;
    }

而不是

    
    
    - (CGFloat)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath
    {
        if (indexPath.row == 0) {
            return 44;
        }else if (indexPath.row == 1){
            return 80;
        }else if (indexPath.row == 2){
            return 50;
        }else{
            return 44;
        }
    }

16接手一个新项目,快速的调试,查看某个模块或者方法的作用,需要注释掉一个方法,或者某个代码块,直接写`return;`而不是全选,注释掉;  
比如:查看这个方法`loadNewRecommendTags`作用

    
    
    - (void)loadNewRecommendTags
    {
        return;
        [SVProgressHUD show];
        // 取消之前的任务
        [self.manager.tasks makeObjectsPerformSelector:@selector(cancel)];
        NSMutableDictionary *params = [NSMutableDictionary dictionary];
        params[@"a"] = @"tag_recommend";
        params[@"c"] = @"topic";
        params[@"action"] = @"sub";
        [self.manager GET:DXCommonUrlPath parameters:params success:^(NSURLSessionDataTask * _Nonnull task, id  _Nonnull responseObject) {
            self.recommendTag = [DXRecommendTag mj_objectArrayWithKeyValuesArray:responseObject];
            [self.tableView reloadData];
            [SVProgressHUD dismiss];
        } failure:^(NSURLSessionDataTask * _Nullable task, NSError * _Nonnull error) {
            DXLog(@"%@",error);
            [SVProgressHUD dismiss];
        }];
    }

17.在一个自定义的View中,或者自定义cell中,modal出一个控制器建议:

    
    
    [UIApplication sharedApplication].keyWindow.rootViewController

代替

    
    
    self.window.rootViewController,因为程序可能不止一个window,self.window可能不是主窗口;

18.建议:用CGSizeZero 代替 CGSizeMake(0,0);  
CGRectZero代替CGRectMake(0, 0, 0, 0);  
CGPointZero代替CGPointMake(0, 0)

19.监听键盘的通知建议:

    
    
    UIKIT_EXTERN NSString *const UIKeyboardWillChangeFrameNotification

而不是,下面代码;因为键盘可能因为改变输入法,切换成表情输入,切换成英文,那么frame可能会变高,变矮,不一定会发出下面这些通知,但是肯定会发上面的通知

    
    
    UIKIT_EXTERN NSString *const UIKeyboardWillShowNotification;
    UIKIT_EXTERN NSString *const UIKeyboardDidShowNotification;
    UIKIT_EXTERN NSString *const UIKeyboardWillHideNotification;
    UIKIT_EXTERN NSString *const UIKeyboardDidHideNotification;

20.发布通知的字符串常量规范,建议模仿苹果;如上键盘的通知的书写,加上const
保证字符串不可更改,以Notification结尾,一看就知道是通知;应尽量保证可读性,不要怕句子太长;

    
    
    NSString *const buttonDidClickNotification = @"buttonDidClickNotification";

21.如果除数为0,iOS8以下会直接报错,(NaN—>Not a
Number)iOS9不会,所以应该判断,比如服务器返回图片的宽高,按比例缩放,CGFloat contentH = textW * self.height
/ self.width;

22.如果声明的属性,只想使用的get方法,不使用set方法,并且不想让外界更改这个属性的值,那么建议在括号里面加readonly;示例:

    
    
    @property(nonatomic,readonly,getter=isKeyWindow) BOOL keyWindow;

23.如果属性是BOOL类型,建议在括号中重写get方法名称,以提高可读性,示例代码如上;

24.从系统相册中取照片之前,应该判断系统相册是否可用,如果从相机中拍照获取,要判断相机是否可用

    
    
    // 判断相册是否可以打开
    if (![UIImagePickerController isSourceTypeAvailable:UIImagePickerControllerSourceTypePhotoLibrary]) return;
    //  判断相机是否可以打开
    if (![UIImagePickerController isSourceTypeAvailable:UIImagePickerControllerSourceTypeCamera]) return;

25.在导航控制中,或它的子控制器,设置导航栏的标题应该用self.navigationItem.title = @“标题”而不建议self.title =
@“标题”;

26.给cell设置分割线,建议用setFrame:通过设置它高度,设置分割线,而不推荐用给cell底部添加一个高度的UIView,这样做增加了一个控件,从
性能上来讲,不如用setFrame设置高度

27.大量操作图层会可能造成应用很卡,给用户体验差,所以尽量不要操作图层;比如设置按钮圆角,比如给button设置圆角;

    
    
    self.loginBtn.layer.cornerRadius = 5;
    self.loginBtn.layer.masksToBounds = YES;

28.给分类扩充方法,建议加上前缀,比如第三方框架`SDWebImage`,这样做跟系统的方法很容易区分开,减少了程序员之间的沟通成本,同理跟分类添加属性(
利用运行时),建议加前缀,以防止苹果官方过一段时间添加了一模一样的属性名,比如给UITextField分类添加了placeholderColor这个属性,万
一某天官方给placeholder扩充了这个命名一模一样的属性,那么就不好了

29.凡是在storyboard或者xib中给某个控件添加颜色,颜色对角线有分割线,表示可以设置透明度,如果给这个控件设置透明度建议在这里设置,而不是设置alpha,因为设置了alpha,那么上面有文字也会随着透明度变大,而变得不清楚;可以设置background -->other -->opacity

30.整形转化成浮点型,不建议这么写 a / b _1.0,这样写是错误写法,示例1.5 / 2 _ 1.0;根据运算法则,从作到右,0 _ 1.0 == 0,而应该在前面写1.0 _1.5 /2;建议直接强转;(double)a/b;

31.抽取方法,或者写工具类,能写类方法,尽量写成类方法,减少了创建对象的步骤,比如给UIView扩充分类加载xib,viewWithXib;

32.耗时操作应该放在子线程,避免卡主主线程,比如计算文件大小,下载大文件,清除缓存;

33.声明一个属性,如果是对象,比如数组,不能以new单词开始,否则直接报错,因为new在OC中是生成一个对象的方法,有特殊含义;比如,

    
    
    @property (nonatomic,strong) NSMutableArray<DXTopics *> *newTopicsM;

注意:如果newtopicsM是一个单词(区别于驼峰标志),这样写不会报错;如果是基本数据类型则不会报错,比如

    
    
    @property (nonatomic,assign) int newNumber;

但是如果一定要写new单词开头的属性,那么声明属性的时候,重写getter方法名称只不过使用getter方法的时候注意下

34.在自定义方法中,`and`这个词的用法应该保留。它不应该用于多个参数来说明，就像initWithWidth:height以下这个例子：

    
    
    - (instancetype)initWithWidth:(CGFloat)width height:(CGFloat)height;
    而不应该
    - (instancetype)initWithWidth:(CGFloat)width andHeight:(CGFloat)height;

35.建议POST请求参数字典的写法,这样比较装逼~

    
    
    // NSDictionaryOfVariableBindings这个宏生成一个字典,这个宏可以生成一个变量名到变量值映射的Dictionary,比如:
    NSNumber * packId=@(2);
    NSNumber *userId=@(22);
    NSNumber *proxyType=@(2);
    NSDictionary *param=NSDictionaryOfVariableBindings(packId,userId,proxyType);

