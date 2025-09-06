from enum import Enum, EnumMeta
from types import DynamicClassAttribute
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar, overload

__all__ = ["ChoiceEnum"]

_T = TypeVar("_T", bound="ChoiceEnum")
_ChoiceTypeT = TypeVar("_ChoiceTypeT", bound="_ChoiceType")
_EnumChoiceMetaT = TypeVar("_EnumChoiceMetaT", bound="EnumChoiceMeta")


def _check_value_type(value: Any) -> None:
    ...


class _ChoiceType:
    _value_: Any
    _label_: str
    _extra: Optional[Any]
    _args: Tuple[Any, ...]

    @overload
    def __new__(cls: Type[_ChoiceTypeT], value: Any, label: str) -> _ChoiceTypeT:
        ...

    @overload
    def __new__(cls: Type[_ChoiceTypeT], value: Any, label: str, extra: Any) -> _ChoiceTypeT:
        ...

    @overload
    def __new__(cls: Type[_ChoiceTypeT], *args: Any) -> _ChoiceTypeT:
        ...

    def __getnewargs__(self) -> Tuple[Any, ...]:
        ...


class EnumChoiceMeta(EnumMeta):
    def __new__(
        metacls: Type[_EnumChoiceMetaT], classname: str, bases: Tuple[Type[Any], ...], classdict: Any, **kwds: Any
    ) -> _EnumChoiceMetaT:
        ...

    def __contains__(cls, value: Any) -> bool:
        ...

    @property
    def names(cls) -> List[str]:
        ...

    @property
    def values(cls) -> List[Any]:
        ...

    @property
    def labels(cls) -> List[str]:
        ...

    @property
    def choices(cls) -> List[Tuple[Any, str]]:
        ...

    def get_label(cls, key: Any) -> Optional[str]:
        ...

    def get_extra(cls, key: Any) -> Optional[Any]:
        ...

    def to_js_enum(cls) -> List[Dict[str, Any]]:
        ...


class ChoiceEnum(_ChoiceType, Enum, metaclass=EnumChoiceMeta):  # type: ignore[misc]
    """ChoiceEnum with proper type annotations for mypy support"""

    # This is a base class for creating choice enums
    # Actual enum members will be defined in subclasses

    # Class attributes provided by metaclass - declare them for subclass inheritance
    names: List[str]
    values: List[Any]
    labels: List[str]
    choices: List[Tuple[Any, str]]

    @overload
    def __new__(cls: Type[_T], value: Any, label: str) -> _T:
        ...

    @overload
    def __new__(cls: Type[_T], value: Any, label: str, extra: Any) -> _T:
        ...

    @overload
    def __new__(cls: Type[_T], *args: Any) -> _T:
        ...

    def __init__(self, *args: Any) -> None:
        ...

    @classmethod
    def get_label(cls, key: Any) -> Optional[str]:
        ...

    @classmethod
    def get_extra(cls, key: Any) -> Optional[Any]:
        ...

    @classmethod
    def to_js_enum(cls) -> List[Dict[str, Any]]:
        ...

    def __getnewargs__(self) -> Tuple[Any, ...]:
        ...

    @DynamicClassAttribute
    def value(self) -> Any:
        ...

    @DynamicClassAttribute
    def label(self) -> str:
        ...

    @DynamicClassAttribute
    def extra(self) -> Optional[Any]:
        ...

    @DynamicClassAttribute
    def option(self) -> Tuple[Any, str]:
        ...

    def __str__(self) -> str:
        ...

    def __repr__(self) -> str:
        ...
