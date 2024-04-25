# py-enum
A python enum module for python2.7 and django choices fields.

通过改造python3中的enum.py而来，增加对python2的支持，并新增类`ChoiceEnum`用于以下场景：
- argparse使用 `add_argument` 的参数 `choices`
- Django中 `models.CharField` 的参数 `choices`
- Django REST framework `ChoiceField` 的参数 `choices`


## 1. 安装

	pip install py-enum

可查看版本变更记录[ChangeLog](./docs/CHANGELOG-1.x.md)

## 2. 使用(Usage)

### 2.1 用ChoiceEnum定义枚举

```python
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

### 2.2 基础用法
- `直接根据Key访问value值`，而并不是一个tuple，正是和原生Enum的区别
- get_label方法
- get_extra方法
- `直接遍历枚举类`，这是能够作为Choices Enum的关键

```python
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

Color.to_js_enum()
# 输出dict数据，可以通过接口序列化后给前端使用，结合js-enumerate前端枚举库
"""
[
    {"key": "RED", "value": 1, "label": "红色"},
    {"key": "GREEN", "value": 2, "label": "绿色"},
    {"key": "BLUE", "value": 3, "label": "蓝色", "extra": {"value": "blue"}}
]
"""
```

### 2.3 枚举对象实例化
```python
member = Color(Color.RED)  # 或者 Color(1)
member.value == 1  # true
member.name == 'RED'  # true
member.label == '红色'  # true
member.option == (1, '红色')  # true
member.extra == None  # true，因为没有定义
# 以上几个属性无法修改，直接赋值会抛出AttributeError异常
member.value in Color  # true
```

### 2.4 在Python argparse中使用
```python
import argparse

parser = argparse.ArgumentParser(description='test ChoiceEnum use in argparse.')
parser.add_argument('--color', type=int, choices=Color, required=True)
args = parser.parse_args(['--color', str(Color.RED)])
# args.color == Color.RED
```

### 2.5 在Django中使用
```python
from django.db import models

class ColorModel(models.Model):
    color = models.IntegerField(verbose_name='颜色', choices=Color, default=Color.RED)

instance = ColorModel.objects.create()
assert instance.color == colors.RED
instance.color = colors.BLUE
instance.save()
```

### 2.6 在DRF中使用
```python
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

### 2.7 类Enum和unique
和python3中原生的Enum并无太大区别，具体可以参考[官方原生开发文档](https://docs.python.org/3.6/library/enum.html)

```python
from py_enum import Enum, unique

@unique
class Season(Enum):
    SPRING = 1
    SUMMER = 2
    AUTUMN = 3
    WINTER = 4
```

## 3. 对比
- `Enum`可以在`Python2`中使用，但需要注意的是：
  - members无序，属性定义时申明的顺序和直接遍历枚举对象时并不一定一致；需通过`_order_`来定义member的顺序
  - python2没有定义__bool__，所以不能直接用class类或者member来做逻辑判断
  - 执行 Season.SPRING > Season.SUMMER 不会报错，但结果也不符合预期
    - py3执行会raise TypeError, 不允许比较
    - 但是ChoiceEnum是直接取值，可以用来做比较运算
  - 枚举类定义时，无法识别多个相同的Key
  - 在多继承方面会受限
- `Enum`和Python3原生enum.py对比，保留了`Enum`类和`unique`方法
- `ChoiceEnum`和Django的 models.Choices 的优势在于低版本Django也能使用，且普通Python项目脚本也能使用
- 新增了额外的特性
  - 额外多出了`ChoiceEnum.extra`的用法，对不同枚举成员做映射配置相关场景可以使用
  - 增加方法`ChoiceEnum.to_js_enum`返回数组数据，可以用于前端枚举库 [js-enumerate](https://github.com/SkylerHu/js-enum) 初始化使用
