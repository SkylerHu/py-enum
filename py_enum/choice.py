#!/usr/bin/env python
# coding=utf-8
import typing

import enum
from types import DynamicClassAttribute


__all__ = [
    "ChoiceEnum",
]

# 基类泛型
P = typing.TypeVar("P", bound=typing.Type[enum.Enum])

T = typing.TypeVar("T", bound=str)  # 用于value的类型
E = typing.TypeVar("E", bound=typing.Optional[dict])  # 用于extra的类型


def _check_value_type(value: typing.Any) -> None:
    # 在Enum中有处理，类型一定是tuple
    if not isinstance(value, tuple):
        raise TypeError(f"value should be a tuple, {value} is a {type(value)}")
    if len(value) < 2:
        raise ValueError(f"value should be a tuple, len({value}) = {len(value)} , len should be >= 2")
    if not isinstance(value[1], str):
        raise TypeError(f"value[1] {value[1]} use for label, should be a string")


class EnumChoiceMeta(enum.EnumMeta):
    """A metaclass for creating a enum choices."""

    def __new__(metacls: type, classname: str, bases: tuple, classdict: dict, **kwds: typing.Any) -> typing.Type[P]:
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

        return enum.unique(cls)

    def __contains__(cls, member: typing.Any) -> bool:  # type: ignore
        if not isinstance(member, enum.Enum):
            # Allow non-enums to match against member values.
            return any(x.value == member for x in cls)  # type: ignore
        return super().__contains__(member)

    @property
    def choices(cls: "EnumChoiceMeta") -> list[tuple[T, str]]:
        return [(member.value, member.label) for member in cls]  # type: ignore

    @property
    def names(cls: "EnumChoiceMeta") -> list[str]:
        return [member.name for member in cls]  # type: ignore

    @property
    def labels(cls: "EnumChoiceMeta") -> list[str]:
        return [label for _, label in cls.choices]  # type: ignore

    @property
    def values(cls: "EnumChoiceMeta") -> list[T]:
        return [value for value, _ in cls.choices]  # type: ignore

    def get_label(cls, value: T) -> str:
        try:
            return cls(value).label  # type: ignore
        except ValueError:
            return str(value)

    def get_extra(cls, value: T) -> typing.Optional[E]:
        try:
            return cls(value).extra  # type: ignore
        except ValueError:
            return None

    def to_js_enum(cls: "EnumChoiceMeta") -> list[dict]:
        """js-enumerate 前端枚举lib需要的数据结构"""
        arr = []
        for member in cls:  # type: ignore
            item = {
                "key": member.name,
                "value": member.value,
                "label": member.label,
            }
            if member.extra is not None:
                item["extra"] = member.extra
            arr.append(item)
        return arr


class ChoiceEnum(typing.Generic[T, E], enum.Enum, metaclass=EnumChoiceMeta):  # type: ignore
    _value_: T
    _label_: str
    _extra: E

    @DynamicClassAttribute
    def value(self) -> T:
        """The value of the Enum member."""
        return self._value_

    @DynamicClassAttribute
    def label(self) -> str:
        """枚举值对应的显示文案"""
        return self._label_

    @DynamicClassAttribute
    def extra(self) -> E:
        """枚举 具体 值"""
        return self._extra

    def __str__(self) -> str:
        return str(self.value)

    # A similar format was proposed for Python 3.10.
    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}.{self._name_}"
