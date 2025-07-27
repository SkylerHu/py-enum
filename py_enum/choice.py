#!/usr/bin/env python
# coding=utf-8
from enum import Enum, EnumMeta, unique
from types import DynamicClassAttribute


__all__ = [
    "ChoiceEnum",
]


def _check_value_type(value):
    if not isinstance(value, tuple):
        raise TypeError(f"value should be a tuple, value is {value}")
    if len(value) < 2:
        raise ValueError(f"value should be a tuple, len({value}) = {len(value)} , len should be >= 2")
    if not isinstance(value[1], str):
        raise TypeError(f"value[1] {value[1]} use for label, should be a string")


class EnumChoiceMeta(EnumMeta):

    def __new__(metacls, classname, bases, classdict, **kwds):
        labels = []
        extras = []
        # classdict 是 _EnumDict 有这个属性
        for key in classdict._member_names:  # type: ignore
            args = classdict[key]
            _check_value_type(args)
            value = args[0]
            label = args[1]
            extra = None
            if len(args) == 3:
                extra = args[2]
            elif len(args) > 3:
                extra = args[2:]

            labels.append(label)
            extras.append(extra)

            # Use dict.__setitem__() to suppress defenses against double
            # assignment in enum's classdict.
            dict.__setitem__(classdict, key, value)

        cls = super().__new__(metacls, classname, bases, classdict, **kwds)  # type: ignore

        for member, label, extra in zip(cls.__members__.values(), labels, extras):
            # 此处设置枚举的值，是在 ChoiceEnum中动态属性会获取
            member._label_ = label
            member._extra = extra

        return unique(cls)

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


class ChoiceEnum(Enum, metaclass=EnumChoiceMeta):
    """ChoiceEnum with proper type annotations for mypy support"""

    def __getnewargs__(self):
        """支持pickle"""
        return (self._value_, self._label_, self._extra) if self._extra is not None else (self._value_, self._label_)

    @DynamicClassAttribute
    def value(self):
        """The value of the Enum member."""
        return self._value_

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

    # A similar format was proposed for Python 3.10.
    def __repr__(self):
        return f"{self.__class__.__qualname__}.{self._name_}"
