#! /usr/bin/env python
# coding=utf-8
from enum import IntEnum, Enum
from .enums import Color, Status

from django.db.models import IntegerChoices, TextChoices  # type: ignore


class Color2(IntEnum):
    RED = 1
    GREEN = 2
    BLUE = 3


class Status2(Enum):
    PROCESSING = ("processing", "处理中")
    APPROVED = ("approved", "已审批")
    CANCELED = ("canceled", "已取消")
    CLOSED = ("closed", "已关闭")


class Color3(IntegerChoices):  # type: ignore
    RED = 1, "红色"
    GREEN = 2, "绿色"
    BLUE = 3, "蓝色"


class Status3(TextChoices):  # type: ignore
    PROCESSING = 1, "处理中"
    APPROVED = 2, "已审批"
    CANCELED = 3, "已取消"
    CLOSED = 4, "已关闭"


def func_str(a: str, b: str) -> str:
    return f"{a}-{b}"


def func_int(a: int, b: int) -> int:
    return a + b


if __name__ == "__main__":
    # 这些应该不会产生mypy错误
    # 原生的
    color_value2: int = Color2.RED.value
    status_value2 = Status2.PROCESSING.value

    # django的
    color_value3 = Color3.RED.value  # type: ignore
    status_value3 = Status3.PROCESSING.value  # type: ignore

    # 自定义库的
    color_value: int = Color.RED.value
    status_value: str = Status.PROCESSING.value

    # 测试类型推断
    assert isinstance(color_value, int)
    assert isinstance(status_value, str)

    # 测试label属性
    color_label: str = Color.RED.label
    status_label: str = Status.PROCESSING.label

    assert func_str(Status.PROCESSING.value, Status.APPROVED.value) == "processing-approved"

    assert func_int(Color.RED.value, Color.GREEN.value) == 3
    assert func_int(Color2.RED.value, Color2.GREEN.value) == 3
    assert Color.values == [Color.RED.value, Color.GREEN.value, Color.BLUE.value]
