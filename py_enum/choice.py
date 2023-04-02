#!/usr/bin/env python
# coding=utf-8
import six

from .enum import Enum, EnumMeta

__all__ = ['ChoiceEnum', ]


class _ChoiceType(object):

    def __new__(cls, *args):
        cls.check_value_type(args)
        self = object.__new__(cls)
        self._value_ = args[0]
        self._label_ = self._value_
        self.extra = None
        if len(args) > 0:
            self._label_ = args[1]
            if len(args) == 3:
                self.extra = args[2]
            elif len(args) > 3:
                self.extra = args[2:]
        return self

    @classmethod
    def check_value_type(cls, value):
        if not isinstance(value, tuple):
            raise TypeError('value should be a tuple, %r is a %s' % (value, type(value)))
        if len(value) < 2:
            raise ValueError('len(%r) = %d , len should be >= 2' % (value, len(value), ))
        if not isinstance(value[1], six.string_types):
            raise TypeError('value[1] %r use for label, should be a string' % (value[1], ))

    @property
    def value(self):
        """枚举 具体 值"""
        return self._value_

    @property
    def label(self):
        """枚举值对应的显示文案"""
        return self._label_

    @property
    def name(self):
        """枚举的名称/Key"""
        return self._name_

    @property
    def option(self):
        """用于choices枚举及展示使用"""
        return self.value, self.label


class EnumChoiceMeta(EnumMeta):

    def __contains__(cls, value):
        return value in cls._value2member_map_

    def __getattr__(cls, name):
        return super(EnumChoiceMeta, cls).__getattr__(name).value

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
        return cls._value2member_map_[key].extra
