#!/usr/bin/env python
# coding=utf-8
import pytest

from py_enum import ChoiceEnum

from .test_base import _test_pickle_dump_load


def test_choice_enum(colors, status):
    assert colors.RED == 1
    assert status.CLOSED == 'closed'

    lst = list(colors)
    assert len(lst) == len(colors)
    assert len(colors) == 3


def test_choice_enum_value():
    pass


def test_choice_value_name():
    pass
