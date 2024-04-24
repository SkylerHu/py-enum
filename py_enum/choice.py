#!/usr/bin/env python
# coding=utf-8
import six

from .enum import Enum, EnumMeta
from .utils import DynamicClassAttribute


__all__ = ['ChoiceEnum', ]


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
        """ 支持pickle"""
        return self._args

    @classmethod
    def _check_value_type(cls, value):
        # 在Enum中有处理，类型一定是tuple
        if not isinstance(value, tuple):
            raise TypeError('value should be a tuple, %r is a %s' % (value, type(value)))
        if len(value) < 2:
            raise ValueError('value should be a tuple, len(%r) = %d , len should be >= 2' % (value, len(value), ))
        if not isinstance(value[1], six.string_types):
            raise TypeError('value[1] %r use for label, should be a string' % (value[1], ))


class EnumChoiceMeta(EnumMeta):

    def __contains__(cls, value):
        return value in cls._value2member_map_

    def __getattribute__(cls, name):
        attr = super(EnumChoiceMeta, cls).__getattribute__(name)
        if name == '_member_names_':
            pass
        elif name in cls._member_names_:
            attr = attr.value
        return attr

    def __getattr__(cls, name):
        return super(EnumChoiceMeta, cls).__getattr__(name).value

    def __iter__(cls):
        return (cls._member_map_[name].option for name in cls._member_names_)


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

    @classmethod
    def get_label(cls, key, default_value=None):
        try:
            return cls._value2member_map_[key].label
        except KeyError:
            return default_value

    @classmethod
    def get_extra(cls, key):
        return cls._value2member_map_[key]._extra

    @classmethod
    def to_js_enum(cls):
        """js-enumerate 前端枚举lib需要的数据结构"""
        arr = []
        for key in cls._member_names_:
            member = cls[key]
            item = {
                'key': key,
                'value': member._value_,
                'label': member._label_,
            }
            if member._extra is not None:
                item['extra'] = member._extra
            arr.append(item)
        return arr
