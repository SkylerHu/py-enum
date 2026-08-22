# py-enum

[中文文档](./README.zh.md) | **English**

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

A Python `ChoiceEnum` module that extends `enum.Enum` with `label`, `extra`, and `choices` support. Built for:

- `choices` parameter of argparse `add_argument`
- `choices` parameter of Django `models.CharField` / `models.IntegerField`
- `choices` parameter of Django REST framework `ChoiceField`

## Installation

```bash
pip install py-enum
```

## Quick Start

### Define Enums

```python
from py_enum import ChoiceEnum

class Color(ChoiceEnum):
    RED = (1, 'Red')
    GREEN = (2, 'Green')
    BLUE = (3, 'Blue', {'value': 'blue'})

class Status(ChoiceEnum):
    PROCESSING = ('processing', 'Processing')
    APPROVED = ('approved', 'Approved')
    CANCELED = ('canceled', 'Canceled')
    CLOSED = ('closed', 'Closed')
```

Each member is defined as `Key = (value, label, extra)`: `value` is the enum value, `label` is the description, and `extra` is an optional field of any type.

### Basic Usage

```python
Color.RED          # Color.RED
Color.RED.value    # 1
type(Color.RED)    # <enum 'Color'>
str(Color.RED)     # (1, Red)
len(Color) == 3    # True
Color.RED in Color            # True
Color.RED.value in Color      # True
Color.RED.value in Color.values  # True
Color.RED in Color.values     # False  # not supported
1 in Color         # True
0 not in Color     # True

# Extended class properties
Color.values   # [1, 2, 3]
Color.names    # ['RED', 'GREEN', 'BLUE']
Color.labels   # ['Red', 'Green', 'Blue']
Color.choices  # [(1, 'Red'), (2, 'Green'), (3, 'Blue')]

# Extended class methods
Color.get_label(Color.RED.value)   # 'Red'
Color.get_extra(Color.BLUE.value)  # {'value': 'blue'}

# Iteration
for member in Color:
    print(member.value, member.label)
# 1 Red
# 2 Green
# 3 Blue

```

### Member Properties

```python
member = Color(Color.RED.value)  # or Color(1)
member.value   # 1
member.name    # 'RED'
member.label   # 'Red'
member.option  # (1, 'Red')
member.extra   # None (when not defined)
# All properties above are read-only; assignment raises AttributeError
member.value in Color  # True
```

### Usage with argparse

```python
import argparse

parser = argparse.ArgumentParser(description='test ChoiceEnum use in argparse.')
parser.add_argument('--color', type=int, choices=Color, required=True)
args = parser.parse_args(['--color', str(Color.RED.value)])
# args.color == Color.RED.value
```

### Usage with Django

```python
from django.db import models

class ColorModel(models.Model):
    color = models.IntegerField(verbose_name='color', choices=Color.choices, default=Color.RED.value)

instance = ColorModel.objects.create()
assert instance.color == Color.RED.value
instance.color = Color.BLUE.value
instance.save()
```

### Usage with Django REST framework

```python
from rest_framework import serializers

class ColorSerializer(serializers.Serializer):
    color = serializers.ChoiceField(help_text='Select color', choices=Color.choices, default=Color.RED.value)

s = ColorSerializer()
s = ColorSerializer(data={'color': Color.RED.value})
assert s.is_valid() is True
s = ColorSerializer(data={'color': 1})
assert s.is_valid() is True
s = ColorSerializer(data={'color': 0})
assert s.is_valid() is False  # value not in enum, validation fails
```

### Frontend Integration

`to_js_enum()` returns an array that can be serialized and used with the frontend enum library [js-enumerate](https://github.com/skylerhu/js-enum):

```python
Color.to_js_enum()
# [
#     {"key": "RED", "value": 1, "label": "Red"},
#     {"key": "GREEN", "value": 2, "label": "Green"},
#     {"key": "BLUE", "value": 3, "label": "Blue", "extra": {"value": "blue"}}
# ]
```

## Comparison with Django `models.Choices`

| Feature | `ChoiceEnum` | Django `models.Choices` |
|---|---|---|
| Django version requirement | None (pure Python) | Django 3.0+ |
| Works outside Django | Yes | No |
| `extra` field | Yes | No |
| `to_js_enum()` frontend integration | Yes | No |

## Changelog

See [CHANGELOG-2.x](./docs/CHANGELOG-2.x.md) for the latest release notes.

## Contributing

Contributions are welcome! Please read the [Contributing Guide](./docs/CONTRIBUTING.md) before submitting a pull request.

## License

This project is licensed under the [MIT License](./LICENSE).
