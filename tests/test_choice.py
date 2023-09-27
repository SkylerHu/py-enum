#!/usr/bin/env python
# coding=utf-8
import six
import pytest

from pickle import dumps, loads, HIGHEST_PROTOCOL

from py_enum import ChoiceEnum, unique


def test_enum_value(colors, status):
    assert colors.RED == 1
    assert status.CLOSED == 'closed'


def test_enum_len(colors):
    lst = list(colors)
    assert len(lst) == len(colors)
    assert len(colors) == 3


def test_value_name(colors):
    member = colors(colors.RED)
    assert member.value == 1
    assert member.name == 'RED'
    assert member.label == '红色'
    with pytest.raises(AttributeError):
        member.name = 'invierno'
    with pytest.raises(AttributeError):
        member.value = 2


def test_changing_member(colors):
    with pytest.raises(AttributeError):
        colors.RED = 4


def test_attribute_deletion(colors):
    assert hasattr(colors, 'RED')
    with pytest.raises(AttributeError):
        del colors.RED


def test_invalid_names():
    with pytest.raises(ValueError):
        class Wrong(ChoiceEnum):
            mro = (1, 2)
    with pytest.raises(TypeError):
        class Wrong2(ChoiceEnum):
            test = (1, 2)
    with pytest.raises(ValueError):
        class Wrong3(ChoiceEnum):
            test = 1


def test_contains(colors, status):
    assert colors.RED in colors
    assert 0 not in colors
    assert status.CLOSED in status


def test_enum_with_value_name_label():
    class Huh(ChoiceEnum):
        name = (1, 'label-name')
        value = (2, 'label-value')
        label = (3, 'label-label')
        option = (4, 'label-option')

    assert type(Huh.name) == int
    member = Huh(1)
    assert member.name == 'name'
    assert member.value == 1
    assert member.label == 'label-name'
    assert Huh.get_label(Huh.name) == 'label-name'

    assert Huh.option == 4
    assert member.option == (1, 'label-name')


def test_pickle_enum(status):
    for protocol in range(HIGHEST_PROTOCOL + 1):
        assert loads(dumps(status, protocol=protocol)) is status
        assert loads(dumps(status.CLOSED, protocol=protocol)) == status.CLOSED
        member = status(status.CLOSED)
        assert loads(dumps(member, protocol=protocol)) is member


def test_enum_member(colors):
    assert colors['RED'].value == 1
    assert colors(1).value == 1
    assert colors(1) is colors['RED']


def test_no_such_enum_member(colors):
    with pytest.raises(ValueError):
        colors(0)
    with pytest.raises(KeyError):
        colors['GREY']


def test_order_members(colors):
    _colors = colors
    if six.PY2:
        # python2需要定义排序 _order_
        class Color(ChoiceEnum):
            _order_ = 'RED GREEN BLUE'
            RED = (1, '红色')
            GREEN = (2, '绿色')
            BLUE = (3, '蓝色')
        _colors = Color
    else:
        with pytest.raises(TypeError):
            # python3定义了排序，属性顺序必须一致
            class Color(ChoiceEnum):
                _order_ = 'RED BLUE GREEN'
                RED = (1, '红色')
                GREEN = (2, '绿色')
                BLUE = (3, '蓝色')

    lst = [_colors.RED, _colors.GREEN, _colors.BLUE]
    assert [v for v, _ in list(_colors)] == lst
    assert [label for _, label in list(_colors)] == [_colors.get_label(v) for v in lst]
    assert _colors(_colors.RED).option == (1, '红色')
    assert list(_colors) == [_colors(v).option for v in lst]


def test_unique_clean():
    @unique
    class Clean(ChoiceEnum):
        RED = (1, '红色')
        GREEN = (2, '绿色')
        BLUE = (3, '蓝色')

    with pytest.raises(ValueError):
        @unique
        class Dirty(ChoiceEnum):
            RED = (1, '红色')
            GREEN = (2, '绿色')
            BLUE = (1, '蓝色')


def test_check_type():
    with pytest.raises(ValueError):
        class Color(ChoiceEnum):
            RED = 1


def test_label(colors):
    assert colors.get_label(colors.RED) == '红色'
    _color = 0
    assert _color not in colors
    assert colors.get_label(_color) is None
    assert colors.get_label(_color, default_value='red') == 'red'


def test_enum_extra():
    class Color(ChoiceEnum):
        RED = (1, '红色')
        GREEN = (2, '绿色', True)
        BLUE = (3, '蓝色', 3)
        GREY = (4, '灰色', 'grey')
        BLACK = (5, '黑色', {'value': 'grey'})
        WHITE = (6, '白色', (1, 2))
        YELLOW = (7, '黄色', 'first', 'second')

    assert Color.get_extra(Color.RED) is None
    assert Color(Color.GREEN).extra is True
    assert Color.get_extra(Color.BLUE) == 3
    assert Color.get_extra(Color.GREY) == 'grey'
    assert Color.get_extra(Color.BLACK)['value'] == 'grey'
    assert Color.get_extra(Color.WHITE) == (1, 2)
    assert Color.get_extra(Color.YELLOW) == ('first', 'second')
