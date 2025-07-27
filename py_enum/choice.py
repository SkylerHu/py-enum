#!/usr/bin/env python
# coding=utf-8
import six

from .enum import Enum, EnumMeta
from .utils import DynamicClassAttribute


__all__ = [
    "ChoiceEnum",
]


class _ChoiceType(object):

    def __new__(cls, *args):
        cls._check_value_type(args)
        _args = args
        self = object.__new__(cls)
        self._value_ = args[0]
        self._label_ = self._value_
        self._extra = None
        # _check_value_type 校验过了，长度一定满足要求
        self._label_ = args[1]
        if len(args) == 3:
            self._extra = args[2]
        elif len(args) > 3:
            self._extra = args[2:]
        self._args = _args
        return self

    def __getnewargs__(self):
        """支持pickle"""
        return self._args

    @classmethod
    def _check_value_type(cls, value):
        # 在Enum中有处理，类型一定是tuple
        if not isinstance(value, tuple):
            raise TypeError("value should be a tuple, %r is a %s" % (value, type(value)))
        if len(value) < 2:
            raise ValueError(
                "value should be a tuple, len(%r) = %d , len should be >= 2"
                % (
                    value,
                    len(value),
                )
            )
        if not isinstance(value[1], six.string_types):
            raise TypeError("value[1] %r use for label, should be a string" % (value[1],))


class EnumChoiceMeta(EnumMeta):

    def __contains__(cls, value):
        if not isinstance(value, Enum):
            # Allow non-enums to match against member values.
            return any(x.value == value for x in cls)
        return super(EnumChoiceMeta, cls).__contains__(value)

    @property
    def names(cls):
        return [member.name for member in cls]

    @property
    def values(cls):
        return [member.value for member in cls]

    @property
    def labels(cls):
        return [member.label for member in cls]

    @property
    def choices(cls):
        return [(member.value, member.label) for member in cls]

    def get_label(cls, key):
        try:
            return cls(key).label
        except ValueError:
            return None

    def get_extra(cls, key):
        try:
            return cls(key).extra
        except ValueError:
            return None

    def to_js_enum(cls):
        """js-enumerate 前端枚举lib需要的数据结构"""
        arr = []
        for member in cls:
            item = {
                "key": member.name,
                "value": member.value,
                "label": member.label,
            }
            if member.extra is not None:
                item["extra"] = member.extra
            arr.append(item)
        return arr


class ChoiceEnum(six.with_metaclass(EnumChoiceMeta, _ChoiceType, Enum)):

    @DynamicClassAttribute
    def label(self):
        """枚举值对应的显示文案"""
        return self._label_

    @DynamicClassAttribute
    def extra(self):
        """枚举 具体 值"""
        return self._extra

    @DynamicClassAttribute
    def option(self):
        """用于choices枚举及展示使用"""
        return self._value_, self._label_

    def __str__(self):
        return str(self.option)
