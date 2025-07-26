#!/usr/bin/env python
# coding=utf-8
import pytest


@pytest.fixture
def colors():
    from tests.app.enums import Color

    return Color


@pytest.fixture
def color_extra():
    from tests.app.enums import ColorExtra

    return ColorExtra


@pytest.fixture
def status():
    from tests.app.enums import Status

    return Status
