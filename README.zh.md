# py-enum

**中文** | [English](./README.md)

[![PyPI - Version](https://img.shields.io/pypi/v/py-enum)](https://pypi.org/project/py-enum/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/py-enum)](https://pypistats.org/packages/py-enum)
[![GitHub Actions Workflow Status](https://github.com/skylerhu/py-enum/actions/workflows/pre-commit.yml/badge.svg?branch=master)](https://github.com/skylerhu/py-enum/actions/workflows/pre-commit.yml)
[![GitHub Actions Workflow Status](https://github.com/skylerhu/py-enum/actions/workflows/test-py3.yml/badge.svg?branch=master)](https://github.com/skylerhu/py-enum/actions/workflows/test-py3.yml)
[![Codecov](https://codecov.io/gh/skylerhu/py-enum/graph/badge.svg)](https://codecov.io/gh/skylerhu/py-enum)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/py-enum)](https://pypi.org/project/py-enum/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/py-enum)](https://pypi.org/project/py-enum/)
[![PyPI - Implementation](https://img.shields.io/pypi/implementation/py-enum)](https://pypi.org/project/py-enum/)
[![GitHub License](https://img.shields.io/github/license/skylerhu/py-enum)](https://github.com/skylerhu/py-enum/blob/master/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

一个扩展了 `enum.Enum` 的 Python 枚举模块，为常见场景提供 `label`、`extra`、`choices` 支持：

- argparse 使用 `add_argument` 的参数 `choices`
- Django 中 `models.CharField` / `models.IntegerField` 的参数 `choices`
- Django REST framework `ChoiceField` 的参数 `choices`

## 安装

```bash
pip install py-enum
```

## 快速开始

### 定义枚举

```python
from py_enum import ChoiceEnum

class Color(ChoiceEnum):
    RED = (1, '红色')
    GREEN = (2, '绿色')
    BLUE = (3, '蓝色', {'value': 'blue'})

class Status(ChoiceEnum):
    PROCESSING = ('processing', '处理中')
    APPROVED = ('approved', '已审批')
    CANCELED = ('canceled', '已取消')
    CLOSED = ('closed', '已关闭')
```

按照 `Key = (value, label, extra)` 的形式定义：`value` 是枚举值，`label` 是描述，`extra` 是可选的额外信息（任意类型）。

### 基础用法

```python
Color.RED          # Color.RED
Color.RED.value    # 1
type(Color.RED)    # <enum 'Color'>
str(Color.RED)     # (1, 红色)
len(Color) == 3    # True
Color.RED in Color            # True
Color.RED.value in Color      # True
Color.RED.value in Color.values  # True
Color.RED in Color.values     # False  # 不支持如此使用
1 in Color         # True
0 not in Color     # True

# 扩展的类属性
Color.values   # [1, 2, 3]
Color.names    # ['RED', 'GREEN', 'BLUE']
Color.labels   # ['红色', '绿色', '蓝色']
Color.choices  # [(1, '红色'), (2, '绿色'), (3, '蓝色')]

# 扩展的类方法
Color.get_label(Color.RED.value)   # '红色'
Color.get_extra(Color.BLUE.value)  # {'value': 'blue'}

# 遍历
for member in Color:
    print(member.value, member.label)
# 1 红色
# 2 绿色
# 3 蓝色

```

### 成员属性

```python
member = Color(Color.RED.value)  # 或者 Color(1)
member.value   # 1
member.name    # 'RED'
member.label   # '红色'
member.option  # (1, '红色')
member.extra   # None（未定义时）
# 以上属性均为只读，赋值会抛出 AttributeError
member.value in Color  # True
```

### 在 argparse 中使用

```python
import argparse

parser = argparse.ArgumentParser(description='test ChoiceEnum use in argparse.')
parser.add_argument('--color', type=int, choices=Color, required=True)
args = parser.parse_args(['--color', str(Color.RED.value)])
# args.color == Color.RED.value
```

### 在 Django 中使用

```python
from django.db import models

class ColorModel(models.Model):
    color = models.IntegerField(verbose_name='颜色', choices=Color.choices, default=Color.RED.value)

instance = ColorModel.objects.create()
assert instance.color == Color.RED.value
instance.color = Color.BLUE.value
instance.save()
```

### 在 DRF 中使用

```python
from rest_framework import serializers

class ColorSerializer(serializers.Serializer):
    color = serializers.ChoiceField(help_text='选择颜色', choices=Color.choices, default=Color.RED.value)

s = ColorSerializer()
s = ColorSerializer(data={'color': Color.RED.value})
assert s.is_valid() is True
s = ColorSerializer(data={'color': 1})
assert s.is_valid() is True
s = ColorSerializer(data={'color': 0})
assert s.is_valid() is False  # 值不在枚举定义范围内，校验不通过
```

### 前端集成

`to_js_enum()` 输出数组数据，可序列化后配合前端枚举库 [js-enumerate](https://github.com/skylerhu/js-enum) 使用：

```python
Color.to_js_enum()
# [
#     {"key": "RED", "value": 1, "label": "红色"},
#     {"key": "GREEN", "value": 2, "label": "绿色"},
#     {"key": "BLUE", "value": 3, "label": "蓝色", "extra": {"value": "blue"}}
# ]
```

## 与 Django `models.Choices` 对比

| 特性 | `ChoiceEnum` | Django `models.Choices` |
|---|---|---|
| Django 版本要求 | 无（纯 Python） | Django 3.0+ |
| 非 Django 项目可用 | 是 | 否 |
| `extra` 扩展字段 | 是 | 否 |
| `to_js_enum()` 前端集成 | 是 | 否 |

## 变更日志

查看 [CHANGELOG-2.x](./docs/CHANGELOG-2.x.zh.md) 了解最新版本变更记录。

## 参与贡献

欢迎贡献！提交 PR 前请阅读[贡献指南](./docs/CONTRIBUTING.zh.md)。

## 许可证

本项目基于 [MIT 许可证](./LICENSE) 开源。
