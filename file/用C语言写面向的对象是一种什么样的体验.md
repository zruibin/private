 
<!--BEGIN_DATA
{
    "create_date": "2017-04-12 11:51", 
    "modify_date": "2017-04-12 11:51", 
    "is_top": "0", 
    "summary": "用C语言写面向的对象是一种什么样的体验", 
    "tags": "C/C++", 
    "file_name": "用C语言写面向的对象是一种什么样的体验.md"
}
END_DATA-->

####<p>原文出处：<a href='http://blog.csdn.net/cgqzly123/article/details/60137155' target='blank'>用C语言写面向的对象是一种什么样的体验</a></p>


版权声明：本文为博主原创文章，未经博主允许不得转载。

最近从老东家离职，跳出来跟这几个以前的老同事，拉了一个创业团队，准备干一票，去之前也了解了一番，此次将使用C语言来开发，对于毕业之后一直从事C++面向对象思
维编码的我来说，虽然不舍，但是仔细想了下，这都不是事，谁说用C语言写不了面向对象？

众所周知面向对象的三个特性：封装性、继承性、多态性。这几个特性的具体含义我等会会班门弄斧讲一下含义，下面，请允许我先用C++面向对象思维将设计模式中最常用的简单工厂模式写一边，相信这三个特性不言而喻。

以下我将用一个工厂类实现具体汽车的生产，奔驰车、宝马车、奥迪车都将通过工厂类来生产，由父类指针指向具体的汽车实例：

头文件：

```
//Car.h
#ifndef CAR_H_
#define CAR_H_

typedef enum CarType_E
{
	CAR_TYPE_BENZE = 0,
	CAR_TYPE_BMW	  ,
	CAR_TYPE_AUDI	  ,
	CAR_TYPE_NONE	  ,
}CarType_E;

class BaseCar
{
public:
	BaseCar(CarType_E CarType);
	virtual ~BaseCar();

	virtual void CarSpeaker();
	CarType_E _CarType;
};

class BenzeCar : public BaseCar
{
public:
	BenzeCar(CarType_E CarType);
	~BenzeCar();
public:
	void CarSpeaker();
};

class BMWCar : public BaseCar
{
public:
	BMWCar(CarType_E CarType);
	~BMWCar();

	void CarSpeaker();
};

class AudiCar : public BaseCar
{
public:
	AudiCar(CarType_E CarType);
	~AudiCar();

	void CarSpeaker();
};

class CarFactory
{
public:
	BaseCar* createNewCar(CarType_E CarType);
};

#endif /* CAR_H_ */
```

源代码：

```
//Car.cpp
#include "Car.h"
#include <iostream>

using namespace std;

BaseCar::BaseCar(CarType_E CarType) : _CarType(CarType)
{
	printf("BaseCar create\n");
}

BaseCar::~BaseCar()
{
	printf("BaseCar delete\n");
}

void BaseCar::CarSpeaker()
{
	std::cout << "BeBu! BeBu" << endl;
}

BenzeCar::BenzeCar(CarType_E CarType) : BaseCar(CarType)
{
	printf("BenzeCar create\n");
}

BenzeCar::~BenzeCar()
{
	printf("BenzeCar delete\n");
}

void BenzeCar::CarSpeaker()
{
	printf("BeBu! BeBu! BenzeCar Car,Type:%d\n", _CarType);
}

BMWCar::BMWCar(CarType_E CarType) : BaseCar(CarType)
{
	printf("BMWCar create\n");
}

BMWCar::~BMWCar()
{
	printf("BMWCar delete\n");
}

void BMWCar::CarSpeaker()
{
	printf("BeBu! BeBu! BMWCar Car,Type:%d\n", _CarType);
}

AudiCar::AudiCar(CarType_E CarType) : BaseCar(CarType)
{
	printf("AudiCar create\n");
}

AudiCar::~AudiCar()
{
	printf("AudiCar delete\n");
}

void AudiCar::CarSpeaker()
{
	printf("BeBu! BeBu! AudiCar Car,Type:%d\n", _CarType);
}

BaseCar* CarFactory::createNewCar(CarType_E CarType)
{
	BaseCar* newCar = NULL;
	switch(CarType)
	{
		case CAR_TYPE_BENZE:
		{
			newCar = new BenzeCar(CAR_TYPE_BENZE);
			break;
		}
		case CAR_TYPE_BMW:
		{
			newCar = new BMWCar(CAR_TYPE_BMW);
			break;
		}
		case CAR_TYPE_AUDI:
		{
			newCar = new AudiCar(CAR_TYPE_AUDI);
			break;
		}
		default:
		{
			newCar = new BaseCar(CAR_TYPE_NONE);
			break;
		}
	}
	return newCar;
}

```

测试代码main.cpp

```
//main.cpp
#include <iostream>
#include "Car.h"
using namespace std;

int main() {
	CarFactory* carFactory = new CarFactory();
	BaseCar* newBenzeCar = carFactory->createNewCar(CAR_TYPE_BENZE);
	BaseCar* newBMWCar = carFactory->createNewCar(CAR_TYPE_BMW);
	BaseCar* newAudiCar = carFactory->createNewCar(CAR_TYPE_AUDI);

	newBenzeCar->CarSpeaker();
	newBMWCar->CarSpeaker();
	newAudiCar->CarSpeaker();

	delete newBenzeCar;
	newBenzeCar = NULL;
	delete newBMWCar;
	newBMWCar = NULL;
	delete newAudiCar;
	newAudiCar = NULL;
	delete carFactory;
	carFactory = NULL;
	return 0;
}

```

编译后输出：

![](./image/20170304214301094)  
  
以上便是简单工厂模式的源码示例，现在，我们来聊聊为什么用C语言我们也可以实现这面向对象思维的三大特性：

首先是封装性：C++的封装性就是将抽象类的函数和属性都封装起来，不对外开放，外部要使用这些属性和方法都必须通过一个具体实例对象去访问这些方法和属性，而我们知道，C语言中一旦包含了头文件便可以使用头文件中的函数和变量，其实C语言中也可以用一种方法达到这种效果，那便是使用结构体+函数指针+static，结构体中定义属性和函数指针，static将方法都限制在本模块使用，对外部，通过指针函数的方式访问，如此一来，便可以达到面向对象封装性的实现；

对于继承性：C++ 面向对象的继承是可以继承父类的属性和方法，在子类对象中的内存中是有父类对象的内存的，那么，用C语言来写的话我们完全可以在父类结构体中定义
一个父类变量在其中，在使用构造子类的时候同时构造父类，便可以达到继承性的特性；

对于多态性：C++中允许一个父类指针指向子类实体，在这个指针使用方法时，若此方法是虚函数，则执行动作会执行到具体的子类函数中，本质的实现方式是通过一个虚函数指针的方式，由于我们用C语言写面向对象本就是通过函数指针的方式来封装函数，那我们完全可以将结构体父类的变量的函数指针让他指向子类的函数来达到多态的特性。

  
好了，在你们面前班门弄斧了一番，下面开始具体的代码实现：

头文件：

```
#ifndef CAR_H_
#define CAR_H_

#include <stdio.h>
#include <stdlib.h>

typedef enum CarType
{
	CAR_BENZE = 0,
	CAR_BMW,
	CAR_AUDI,
	CAR_NONE,
}CarType;

typedef struct Base_Car
{
	CarType car_type;
	void (* speaker)(struct Base_Car* car);

	void* parent_car; //point to parent,if no any parent,then make it NULL
}Base_Car;

typedef struct Benze_Car
{
	Base_Car* car;
	void (* speaker)(struct Base_Car* car);
}Benze_Car;

typedef struct BMW_Car
{
	Base_Car* car;
	void (* speaker)(struct Base_Car* car);
}BMW_Car;

typedef struct Audi_Car
{
	Base_Car* car;
	void (* speaker)(struct Base_Car* car);
}Audi_Car;

typedef struct Car_Factory
{
	Base_Car* (* create_new_car)(CarType car_type);
}Car_Factory;

Car_Factory* new_car_factory();
void delete_car_factory(Car_Factory* car_factory);

Base_Car* new_Base_Car();
Benze_Car* new_benze_Car();
BMW_Car* new_bmw_Car();
Audi_Car* new_audi_Car();

void delete_Base_Car(struct Base_Car* car);
void delete_Benze_Car(struct Benze_Car* car);
void delete_BMW_Car(struct BMW_Car* car);
void delete_Audi_Car(struct Audi_Car* car);

#endif /* CAR_H_ */
```

源文件：

    
```
#include "Car.h"

static void Car_speaker(struct Base_Car* car)
{
	printf("this is a car\n");
}

static void Benze_speaker(struct Base_Car* car)
{
	printf("this is Benze Car, car type is :%d\n",car->car_type);
}

static void BMW_speaker(struct Base_Car* car)
{
	printf("this is BMW Car, car type is :%d\n",car->car_type);
}

static void Audi_speaker(struct Base_Car* car)
{
	printf("this is Audi Car, car type is :%d\n",car->car_type);
}

Benze_Car* new_benze_Car()
{
	Benze_Car* real_car = (Benze_Car*)malloc(sizeof(Benze_Car));
	Base_Car* base_car = new_Base_Car();
	printf("Benze_Car create\n");
	real_car->car = base_car;
	real_car->speaker = Benze_speaker;
	base_car->car_type = CAR_BENZE;
	base_car->parent_car = (void*)real_car;
	base_car->speaker = real_car->speaker;
	return real_car;
}

BMW_Car* new_bmw_Car()
{
	BMW_Car* real_car = (BMW_Car*)malloc(sizeof(BMW_Car));
	Base_Car* base_car = new_Base_Car();
	printf("BMW_Car create\n");
	base_car->car_type = CAR_BMW;
	real_car->car = base_car;
	real_car->speaker = BMW_speaker;
	base_car->car_type = CAR_BMW;
	base_car->parent_car = (void*)real_car;
	base_car->speaker = real_car->speaker;
	return real_car;
}

Audi_Car* new_audi_Car()
{
	Audi_Car* real_car = (Audi_Car*)malloc(sizeof(Audi_Car));
	Base_Car* base_car = new_Base_Car();
	printf("Audi_Car create\n");
	base_car->car_type = CAR_AUDI;
	real_car->car = base_car;
	real_car->speaker = Audi_speaker;
	base_car->car_type = CAR_AUDI;
	base_car->parent_car = (void*)real_car;
	base_car->speaker = real_car->speaker;
	return real_car;
}

Base_Car* new_Base_Car()
{
	Base_Car* base_car = (Base_Car*)malloc(sizeof(Base_Car));
	printf("BaseCar create\n");
	base_car->car_type = CAR_NONE;
	base_car->parent_car = NULL;
	base_car->speaker = Car_speaker;
	return base_car;
}

Base_Car* create_new_Car(CarType car_type)
{
	Base_Car* base_car = NULL;
	switch(car_type)
	{
		case CAR_BENZE:
		{
			Benze_Car* real_car = new_benze_Car();
			base_car = real_car->car;
			break;
		}
		case CAR_BMW:
		{
			BMW_Car* real_car = new_bmw_Car();
			base_car = real_car->car;
			break;
		}
		case CAR_AUDI:
		{
			Audi_Car* real_car = new_audi_Car();
			base_car = real_car->car;
			break;
		}
		default:
			break;
	}
	return base_car;
}

void delete_Benze_Car(struct Benze_Car* car)
{
	free(car->car);
	car->car = NULL;
	free(car);
	printf("Benze_Car delete\n");
}

void delete_BMW_Car(struct BMW_Car* car)
{
	free(car->car);
	car->car = NULL;
	free(car);
	printf("BMW_Car delete\n");
}

void delete_Audi_Car(struct Audi_Car* car)
{
	free(car->car);
	car->car = NULL;
	free(car);
	printf("Audi_Car delete\n");
}

void delete_Base_Car(struct Base_Car* car)
{
	if(NULL != car->parent_car)
	{
		switch(car->car_type)
		{
			case CAR_BENZE:
			{
				delete_Benze_Car((Benze_Car*)car->parent_car);
				car = NULL; //base car will be delete in child free function
				break;
			}
			case CAR_BMW:
			{
				delete_BMW_Car((BMW_Car*)car->parent_car);
				car = NULL;
				break;
			}
			case CAR_AUDI:
			{
				delete_Audi_Car((Audi_Car*)car->parent_car);
				car = NULL;
				break;
			}
			default:
				break;
		}
	}
	if(NULL != car)
	{
		free(car);
		car = NULL;
	}
	printf("Base_Car delete\n");
}

Car_Factory* new_car_factory()
{
	Car_Factory* car_factory = (Car_Factory*)malloc(sizeof(Car_Factory));
	car_factory->create_new_car = create_new_Car;
	return car_factory;
}

void delete_car_factory(Car_Factory* car_factory)
{
	free(car_factory);
	car_factory = NULL;
}
```

测试文件main.cpp

```
#include <stdio.h>
#include "Car.h"
int main()
{
	Car_Factory* car_factory = new_car_factory();
	Base_Car* benzeCar = car_factory->create_new_car(CAR_BENZE);
	Base_Car* bmwCar = car_factory->create_new_car(CAR_BMW);
	Base_Car* audiCar = car_factory->create_new_car(CAR_AUDI);

	benzeCar->speaker(benzeCar);
	bmwCar->speaker(bmwCar);
	audiCar->speaker(audiCar);

	delete_Base_Car(benzeCar);
	benzeCar = NULL;
	delete_Base_Car(bmwCar);
	bmwCar = NULL;
	delete_Base_Car(audiCar);
	audiCar = NULL;
	delete_car_factory(car_factory);
	car_factory = NULL;
	return 0;
}
```

编译后执行：

![](./image/20170304220138604)  

以上的结果可以看出，我们的测试代码接口都是一样的，效果达到了C++面向对象的设计理念，用C语言完成了一次狠狠的逆袭，希望读者朋友在你的项目工程中有帮助。其实
程序员的工作大部分是写代码，但是代码的阅读对象往往并不是我们自己，将我们的思维写进去才是一个程序员的境界，不要简单的根据流程去写一个代码，否则，程序员就真的只是一个工具了；

哦，BTW，在函数中我使用了本结构体的指针在里面，是为了达到在函数中使用示例的属性，这样就独立每一个示例的属性操作了。  

