#!/usr/bin/env python
# coding=utf-8
import six

from .enum import Enum, EnumMeta
from .utils import DynamicClassAttribute


__all__ = ['ChoiceEnum', ]


class _ChoiceType(object):

    def __new__(cls, *args):
        cls._check_value_type(args)
        self = object.__new__(cls)
        self._value_ = args[0]
        self._label_ = self._value_
        self._extra = None
        if len(args) > 1:
            self._label_ = args[1]
            if len(args) == 3:
                self._extra = args[2]
            elif len(args) > 3:
                self._extra = args[2:]
        return self

    @classmethod
    def _check_value_type(cls, value):
        if not isinstance(value, tuple):
            raise TypeError('value should be a tuple, %r is a %s' % (value, type(value)))
        if len(value) < 2:
            raise ValueError('len(%r) = %d , len should be >= 2' % (value, len(value), ))
        if not isinstance(value[1], six.string_types):
            raise TypeError('value[1] %r use for label, should be a string' % (value[1], ))

    @property
    def label(self):
        """枚举值对应的显示文案"""
        return self._label_

    @property
    def extra(self):
        """枚举 具体 值"""
        return self._extra

    @property
    def option(self):
        """用于choices枚举及展示使用"""
        return self._value_, self._label_


class EnumChoiceMeta(EnumMeta):

    def __new__(metacls, *args, **kwargs):
        # 为了能够让__getattr__生效，要删除在父类setattr的属性
        enum_class = super().__new__(metacls, *args, **kwargs)
        for name in enum_class._member_names_:
            try:
                member = getattr(enum_class, name)
                if not isinstance(member, DynamicClassAttribute):
                    # 是动态的本身就没有设置
                    delattr(enum_class, name)
            except Exception:
                pass
        return enum_class

    def __delattr__(cls, attr):
        super(EnumMeta, cls).__delattr__(attr)

    def __contains__(cls, value):
        return value in cls._value2member_map_

    def __getattr__(cls, name):
        return super(EnumChoiceMeta, cls).__getattr__(name).value

    # 保持 Color['RED'] / Color(1) 可以获取对象
    # def __getitem__(cls, name):
    #     return super(EnumChoiceMeta, cls).__getitem__(name).value

    def __iter__(cls):
        return (cls._member_map_[name].option for name in cls._member_names_)


class ChoiceEnum(six.with_metaclass(EnumChoiceMeta, _ChoiceType, Enum)):

    @classmethod
    def get_label(cls, key, default_value=None):
        try:
            return cls._value2member_map_[key].label
        except KeyError:
            return default_value

    @classmethod
    def get_extra(cls, key):
        return cls._value2member_map_[key]._extra
