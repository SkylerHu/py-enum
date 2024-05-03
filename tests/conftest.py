#!/usr/bin/env python
# coding=utf-8
import pytest


@pytest.fixture
def colors():
    from tests.app.enums import Color
    return Color


@pytest.fixture
def order_colors():
    from tests.app.enums import OrderColor
    return OrderColor


@pytest.fixture
def status():
    from tests.app.enums import Status
    return Status
