#!/usr/bin/env python
# coding=utf-8
import typing

from py_enum import ChoiceEnum


class Color(ChoiceEnum[int, dict]):
    RED = (1, "红色", {"value": "red"})
    GREEN = (2, "绿色", {"value": "green"})
    BLUE = (3, "蓝色", {"value": "blue"})


class Status(ChoiceEnum):
    PROCESSING = ("processing", "处理中")
    APPROVED = ("approved", "已审批")
    CANCELED = ("canceled", "已取消")
    CLOSED = ("closed", "已关闭")


def test_int_values() -> typing.Tuple:
    # 测试整数类型的value
    red_value: int = Color.RED.value
    green_value: int = Color.GREEN.value
    blue_value: int = Color.BLUE.value
    return red_value, green_value, blue_value


def test_str_values() -> typing.Tuple:
    # 测试字符串类型的value
    processing_value: str = Status.PROCESSING.value
    approved_value: str = Status.APPROVED.value
    canceled_value: str = Status.CANCELED.value
    closed_value: str = Status.CLOSED.value
    return processing_value, approved_value, canceled_value, closed_value


def test_labels() -> typing.Tuple:
    # 测试label属性
    red_label: str = Color.RED.label
    processing_label: str = Status.PROCESSING.label
    return red_label, processing_label


def test_extras() -> typing.Tuple:
    # 测试extra属性
    blue_extra: typing.Optional[dict] = Color.BLUE.extra
    red_extra: typing.Optional[dict] = Color.RED.extra
    return blue_extra, red_extra


def test_options() -> typing.Tuple:
    # 测试option属性
    red_option: tuple = Color.RED.option
    processing_option: tuple = Status.PROCESSING.option
    return red_option, processing_option
