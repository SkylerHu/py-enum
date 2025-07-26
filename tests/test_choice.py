#!/usr/bin/env python
# coding=utf-8
import pytest
import argparse

from pickle import dumps, loads, HIGHEST_PROTOCOL

from py_enum import ChoiceEnum, unique


def test_enum_value(colors, status):
    assert colors.RED.value == 1
    assert status.CLOSED.value == "closed"


def test_enum_len(colors):
    lst = list(colors)
    assert len(lst) == len(colors)
    assert len(colors) == 3


def test_value_name(colors):
    member = colors(colors.RED.value)
    assert member.value == 1
    assert member.name == "RED"
    assert member.label == "红色"
    with pytest.raises(AttributeError):
        member.name = "invierno"
    with pytest.raises(AttributeError):
        member.value = 2


def test_changing_member(colors):
    with pytest.raises(AttributeError):
        colors.RED.value = 4


def test_attribute_deletion(colors):
    assert hasattr(colors, "RED")
    with pytest.raises(AttributeError):
        del colors.RED


def test_invalid_names():
    with pytest.raises(TypeError):

        class Wrong(ChoiceEnum):
            mro = (1, 2)

    with pytest.raises(TypeError):

        class Wrong2(ChoiceEnum):
            test = (1, 2)

    with pytest.raises(TypeError):

        class Wrong3(ChoiceEnum):
            test = 1

    with pytest.raises(ValueError):

        class Wrong4(ChoiceEnum):
            test = (1,)


def test_contains(colors, status):
    assert colors.RED.value in colors
    assert 0 not in colors
    assert status.CLOSED in status
    assert colors(colors.RED.value) in colors


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
    assert Huh.get_label(Huh.name) == "label-name"


def test_pickle_enum(status):
    for protocol in range(HIGHEST_PROTOCOL + 1):
        assert loads(dumps(status, protocol=protocol)) is status
        assert loads(dumps(status.CLOSED, protocol=protocol)) == status.CLOSED
        member = status(status.CLOSED)
        assert loads(dumps(member, protocol=protocol)) is member


def test_enum_member(colors):
    assert colors["RED"].value == 1
    member = colors(1)
    assert member.value == 1
    assert member is colors["RED"]


def test_no_such_enum_member(colors):
    with pytest.raises(ValueError):
        colors(0)
    with pytest.raises(KeyError):
        colors["GREY"]


def test_order_members(colors):
    _colors = colors
    with pytest.raises(TypeError):
        # python3定义了排序，属性顺序必须一致
        class Color(ChoiceEnum):
            _order_ = "RED BLUE GREEN"
            RED = (1, "红色")
            GREEN = (2, "绿色")
            BLUE = (3, "蓝色")

    lst = [_colors.RED.value, _colors.GREEN.value, _colors.BLUE.value]
    assert _colors.values == lst
    assert _colors.labels == [_colors.get_label(v) for v in lst]
    assert _colors.names == [_colors(v).name for v in lst]


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


def test_label(colors):
    assert colors.get_label(colors.RED.value) == "红色"
    _color = 0
    assert _color not in colors
    assert colors.get_label(_color) == "0"


def test_enum_extra():
    class Color(ChoiceEnum):
        RED = (1, "红色")
        GREEN = (2, "绿色", True)
        BLUE = (3, "蓝色", 3)
        GREY = (4, "灰色", "grey")
        BLACK = (5, "黑色", {"value": "grey"})
        WHITE = (6, "白色", (1, 2))
        YELLOW = (7, "黄色", "first", "second")

    assert Color.get_extra(Color.RED) is None
    assert Color(Color.GREEN).extra is True
    assert Color.get_extra(Color.BLUE) == 3
    assert Color.get_extra(Color.GREY) == "grey"
    assert Color.get_extra(Color.BLACK)["value"] == "grey"
    assert Color.get_extra(Color.WHITE) == (1, 2)
    assert Color.get_extra(Color.YELLOW) == ("first", "second")


def test_to_js_enum(color_extra):
    items = color_extra.to_js_enum()
    assert len(items) == len(color_extra)
    expect_output = [
        {"key": "RED", "label": "红色", "value": 1},
        {"key": "GREEN", "label": "绿色", "value": 2},
        {"key": "BLUE", "label": "蓝色", "value": 3, "extra": {"value": "blue"}},
    ]
    assert items == expect_output
    assert color_extra.get_extra(color_extra.BLUE.value) == {"value": "blue"}
    assert 4 not in color_extra
    assert color_extra.get_extra(4) is None


def test_use_in_argparse(colors):
    parser = argparse.ArgumentParser(description="test ChoiceEnum use in argparse.")
    parser.add_argument("--color", type=int, choices=colors, required=True)

    with pytest.raises(SystemExit):
        parser.parse_args(["--color"])

    test_c = -2
    assert test_c not in colors
    with pytest.raises(SystemExit):
        parser.parse_args(["--color", str(test_c)])

    test_c = 1
    assert test_c == colors.RED.value
    args = parser.parse_args(["--color", str(test_c)])
    assert args.color is colors.RED.value
    assert args.color == test_c


def test_cls_property(colors):
    _colors = colors
    assert _colors.values == [1, 2, 3]
    assert _colors.labels == ["红色", "绿色", "蓝色"]
    assert _colors.choices == [(1, "红色"), (2, "绿色"), (3, "蓝色")]
