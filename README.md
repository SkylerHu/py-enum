# py-enum
A python enum module for django choices fields.

## 前言
通过改造python3中的enum.py而来，主要变更有：
- 在支持python3的同时，增加了对python2的支持
- Django中choice选项直接使用枚举对象

## 安装

	pip install py-enum

变更记录ChangeLog[详见](https://github.com/SkylerHu/py-enum/blob/master/docs/CHANGELOG-1.x.md)

# 类ChoiceEnum
集成自改造后的Enum对象，用于创建枚举型的基类。

## 使用

```
# 导入
from py_enum import ChoiceEnum, unique

# 定义
class Color(ChoiceEnum):
    RED = (1, '红色')
    GREEN = (2, '绿色')
    BLUE = (3, '蓝色', {'value': 'blue'})

@unique
class Status(ChoiceEnum):
    PROCESSING = ('processing', '处理中')
    APPROVED = ('approved', '已审批')
    CANCELED = ('canceled', '已取消')
    CLOSED = ('closed', '已关闭')
```
定义如上，按照`Key = (value, label, extra)`的形式进行定义，value定义的值；label是对值的描述；第三个参数是extra，额外信息，可以任意类型。

## 基础用法
- `直接根据Key访问value值`，而并不是一个tuple，正是和原生Enum的区别
- get_label方法
- get_extra方法
- `直接遍历枚举类`，这是能够作为Choices Enum的关键
```
print(Color.RED)  # 1
type(Color.RED)  # <enum 'Color'>
len(colors) == 3  # true
Color.RED in Color  # true
1 in Color  # true
0 not in Color  # true

Color.get_label(Color.RED)  # '红色'
Color.get_extra(Color.BLUE)  # {'value': 'blue'}

for value, label in Color:
    print(value, label)  # 直接遍历value和label
# 1, '红色'
# 2, '绿色'
# 3, '蓝色'
```
## 枚举对象实例化
```
member = Color(Color.RED)  # 或者 Color(1)
member.value == 1  # true
member.name == 'RED'  # true
member.label == '红色'  # true
member.option == (1, '红色')  # true
member.extra == None  # true，因为没有定义
# 以上几个属性无法修改，直接赋值会抛出AttributeError异常
member.value in Color  # true
```

## 在Django中使用
```
from django.db import models

class ColorModel(models.Model):
    color = models.IntegerField(verbose_name='颜色', choices=Color, default=Color.RED)

instance = ColorModel.objects.create()
assert instance.color == colors.RED
instance.color = colors.BLUE
instance.save()
```
## 在DRF中使用
```
from rest_framework import serializers

class ColorSerializer(serializers.Serializer):
    color = serializers.ChoiceField(help_text='选择颜色', choices=Color, default=Color.RED)

s = ColorSerializer()
s = ColorSerializer(data={'status': status.CLOSED})
assert s.is_valid() is True
s = ColorSerializer(data={'status': 1})
assert s.is_valid() is True
s = ColorSerializer(data={'status': 0})
assert s.is_valid() is False  # 值不在枚举定义范围内，校验不通过
```

# 类Enum和unique
和python3中原生的Enum并不太大区别，具体可以参考[官方原生开发文档](https://docs.python.org/3.6/library/enum.html)

## 导入

    from py_enum import Enum unique

    @unique
    class Season(Enum):
        SPRING = 1
        SUMMER = 2
        AUTUMN = 3
        WINTER = 4

## 对比
- 和`Python3`原生enum.py对比
  - 仅保留了`Enum`类和`unique`方法
- 在`Python2`中使用的区别有
  - members无序，属性定义时申明的顺序和直接遍历枚举对象时并不一定一致；需通过`_order_`来定义member的顺序
  - python2没有定义__bool__，所以不能直接用class类或者member来做逻辑判断
  - 执行 Season.SPRING > Season.SUMMER 不会报错，但结果也不符合预期 （py3执行会raise TypeError, 不允许比较）
  - 枚举类定义时，无法识别多个相同的Key
  - 在多继承方面会受限
