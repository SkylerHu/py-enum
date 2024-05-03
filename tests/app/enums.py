#!/usr/bin/env python
# coding=utf-8
from py_enum import ChoiceEnum


class Color(ChoiceEnum):
    RED = (1, '红色')
    GREEN = (2, '绿色')
    BLUE = (3, '蓝色')


class OrderColor(ChoiceEnum):
    """主要用于python2中测试用例"""
    _order_ = 'RED GREEN BLUE'
    RED = (1, '红色')
    GREEN = (2, '绿色')
    BLUE = (3, '蓝色', {'value': 'blue'})


class Status(ChoiceEnum):
    PROCESSING = ('processing', '处理中')
    APPROVED = ('approved', '已审批')
    CANCELED = ('canceled', '已取消')
    CLOSED = ('closed', '已关闭')
