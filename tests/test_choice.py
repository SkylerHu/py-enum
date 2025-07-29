#!/usr/bin/env python
# coding=utf-8
import pytest
import argparse

from pickle import dumps, loads, HIGHEST_PROTOCOL

from py_enum import ChoiceEnum, unique

from tests.app.enums import Color, Status


def test_enum_value():
    assert Color.RED.value == 1
    assert Status.CLOSED.value == "closed"


def test_enum_len():
    lst = list(Color)
    assert len(lst) == len(Color)
    assert len(Color) == 3


def test_value_name():
    member = Color(Color.RED.value)
    assert member.value == 1
    assert member.name == "RED"
    assert member.label == "红色"
    with pytest.raises(AttributeError):
        member.name = "invierno"
    with pytest.raises(AttributeError):
        member.value = 2


def test_changing_member():
    with pytest.raises(AttributeError):
        Color.RED = 4


def test_attribute_deletion():
    assert hasattr(Color, "RED")
    with pytest.raises(AttributeError):
        del Color.RED


def test_invalid_names():
    with pytest.raises(ValueError, match="Invalid enum member name: mro"):

        class Wrong(ChoiceEnum):
            mro = (1, "2")

    with pytest.raises(TypeError, match="use for label, should be a string"):

        class Wrong2(ChoiceEnum):
            test = (1, 2)

    with pytest.raises(ValueError, match="value should be a tuple"):

        class Wrong3(ChoiceEnum):
            test = 1

    with pytest.raises(ValueError, match="len should be >= 2"):

        class Wrong4(ChoiceEnum):
            test = (1,)

    with pytest.raises(ValueError, match="duplicate values found in"):

        class Wrong5(ChoiceEnum):
            V1 = (1, "label-name")
            V2 = (1, "label-value")


def test_contains():
    assert Color.RED.value in Color
    assert 0 not in Color
    assert Status.CLOSED.value in Status
    assert Color(Color.RED.value) in Color


def test_enum_with_value_name_label():
    class Huh(ChoiceEnum):
        name = (1, "label-name")
        value = (2, "label-value")
        label = (3, "label-label")
        option = (4, "label-option")

    assert isinstance(Huh.name.value, int)
    member = Huh(1)
    assert member.name == "name"
    assert member.value == 1
    assert member.label == "label-name"
    assert Huh.get_label(Huh.name.value) == "label-name"

    assert Huh.option.value == 4
    assert member.option == (1, "label-name")
    assert str(member) == "(1, 'label-name')"


def test_getnewargs():
    value, label = Color(Color.RED.value).__getnewargs__()
    assert value == Color.RED.value
    assert label == Color.get_label(value)


def test_pickle_enum():
    for protocol in range(HIGHEST_PROTOCOL + 1):
        assert loads(dumps(Status, protocol=protocol)) is Status
        assert loads(dumps(Status.CLOSED.value, protocol=protocol)) == Status.CLOSED.value
        member = Status(Status.CLOSED.value)
        assert loads(dumps(member, protocol=protocol)) is member


def test_enum_member():
    assert Color["RED"].value == 1
    member = Color(1)
    assert member.value == 1
    assert member is Color["RED"]


def test_no_such_enum_member():
    with pytest.raises(ValueError):
        Color(0)
    with pytest.raises(KeyError):
        Color["GREY"]


def test_order_members():
    with pytest.raises(TypeError):
        # python3定义了排序，属性顺序必须一致
        class Color2(ChoiceEnum):
            _order_ = "RED BLUE GREEN"
            RED = (1, "红色")
            GREEN = (2, "绿色")
            BLUE = (3, "蓝色")

    _colors = Color
    lst = [_colors.RED.value, _colors.GREEN.value, _colors.BLUE.value]
    assert [m.value for m in list(_colors)] == lst
    assert [m.label for m in list(_colors)] == [_colors.get_label(v) for v in lst]
    assert _colors(_colors.RED.value).option == (1, "红色")
    assert list(_colors.choices) == [_colors(v).option for v in lst]


def test_unique_clean():
    @unique
    class Clean(ChoiceEnum):
        RED = (1, "红色")
        GREEN = (2, "绿色")
        BLUE = (3, "蓝色")

    with pytest.raises(ValueError):

        @unique
        class Dirty(ChoiceEnum):
            RED = (1, "红色")
            GREEN = (2, "绿色")
            BLUE = (1, "蓝色")


def test_label():
    assert Color.get_label(Color.RED.value) == "红色"
    _color = 0
    assert _color not in Color
    assert Color.get_label(_color) is None


def test_enum_extra():
    class Color(ChoiceEnum):
        RED = (1, "红色")
        GREEN = (2, "绿色", True)
        BLUE = (3, "蓝色", 3)
        GREY = (4, "灰色", "grey")
        BLACK = (5, "黑色", {"value": "grey"})
        WHITE = (6, "白色", (1, 2))
        YELLOW = (7, "黄色", "first", "second")

    assert Color.get_extra(Color.RED.value) is None
    assert Color(Color.GREEN.value).extra is True
    assert Color.get_extra(Color.BLUE.value) == 3
    assert Color.get_extra(Color.GREY.value) == "grey"
    assert Color.get_extra(Color.BLACK.value)["value"] == "grey"
    assert Color.get_extra(Color.WHITE.value) == (1, 2)
    assert Color.get_extra(Color.YELLOW.value) == ("first", "second")
    _color = 0
    assert _color not in Color
    assert Color.get_extra(_color) is None


def test_to_js_enum():
    items = Color.to_js_enum()
    assert len(items) == len(Color)
    expect_output = [
        {"key": "RED", "label": "红色", "value": 1},
        {"key": "GREEN", "label": "绿色", "value": 2},
        {"key": "BLUE", "label": "蓝色", "value": 3, "extra": {"value": "blue"}},
    ]
    assert items == expect_output, items


def test_use_in_argparse():
    parser = argparse.ArgumentParser(description="test ChoiceEnum use in argparse.")
    parser.add_argument("--color", type=int, choices=Color, required=True)

    with pytest.raises(SystemExit):
        parser.parse_args(["--color"])

    test_c = -2
    assert test_c not in Color
    with pytest.raises(SystemExit):
        parser.parse_args(["--color", str(test_c)])

    test_c = 1
    assert test_c == Color.RED.value
    args = parser.parse_args(["--color", str(test_c)])
    assert args.color is Color.RED.value
    assert args.color == test_c


def test_cls_property():
    _colors = Color
    assert _colors.values == [1, 2, 3]
    assert _colors.names == ["RED", "GREEN", "BLUE"]
    assert _colors.labels == ["红色", "绿色", "蓝色"]
    assert _colors.choices == [(1, "红色"), (2, "绿色"), (3, "蓝色")]
