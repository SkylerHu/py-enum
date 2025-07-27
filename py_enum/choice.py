#!/usr/bin/env python
# coding=utf-8
from typing import TypeVar, Generic, Union, Tuple, Type, Any

from enum import Enum, EnumMeta, unique
from types import DynamicClassAttribute

# 定义类型变量，用于泛型支持
T = TypeVar('T')
ExtraT = TypeVar('ExtraT')

__all__ = [
    "ChoiceEnum",
]


def _check_value_type(value):
    if len(value) < 2:
        raise ValueError(f"value should be a tuple, len({value}) = {len(value)} , len should be >= 2")
    if not isinstance(value[1], str):
        raise TypeError(f"value[1] {value[1]} use for label, should be a string")


class ChoiceType(object):

    def __new__(cls, *args):
        _check_value_type(args)
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


class EnumChoiceMeta(EnumMeta):

    def __new__(metacls: Type, classname: str, bases: tuple, classdict: dict, **kwds: Any) -> Type:
        has_generic = any(base is Generic for base in bases)
        if has_generic:
            bases = tuple(base for base in bases if base is not Generic)

        cls = super().__new__(metacls, classname, bases, classdict, **kwds)  # type: ignore

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


class ChoiceEnum(Generic[T, ExtraT], ChoiceType, Enum, metaclass=EnumChoiceMeta):  # type: ignore
    """ChoiceEnum with proper type annotations for mypy support"""
    _value_: T
    _label_: str
    _extra: ExtraT

    @DynamicClassAttribute
    def value(self) -> T:
        """The value of the Enum member."""
        return self._value_

    @DynamicClassAttribute
    def label(self) -> str:
        """枚举值对应的显示文案"""
        return self._label_

    @DynamicClassAttribute
    def extra(self) -> Union[ExtraT, None]:
        """枚举 具体 值"""
        return self._extra

    @DynamicClassAttribute
    def option(self) -> Tuple[T, str]:
        """用于choices枚举及展示使用"""
        return self._value_, self._label_

    def __str__(self) -> str:
        return str(self.option)

    # A similar format was proposed for Python 3.10.
    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}.{self._name_}"
