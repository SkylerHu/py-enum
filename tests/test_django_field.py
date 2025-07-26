#!/usr/bin/env python
# coding=utf-8
import pytest

from tests.app.enums import Color, Status
from tests.app.models import ColorModel, ColorForm


@pytest.mark.django_db
def test_create() -> None:
    instance = ColorModel.objects.create()
    assert instance.color == Color.RED.value
    assert instance.status == Status.PROCESSING.value


@pytest.mark.django_db
def test_save_and_filter() -> None:
    instance = ColorModel()
    instance.color = Color.BLUE.value
    instance.save()

    assert instance.color == Color.BLUE.value

    instance2 = ColorModel.objects.get(pk=instance.pk)
    assert instance2.color == Color.BLUE.value

    instance3 = ColorModel.objects.filter(color=Color.BLUE.value).first()
    assert instance3.pk == instance.pk


@pytest.mark.django_db
def test_check_fail() -> None:
    form = ColorForm(data={"color": Color.BLUE.value})
    assert form.is_valid() is True

    _color = -1
    assert _color not in Color

    form = ColorForm(data={"color": _color})
    assert form.is_valid() is False
    assert form.errors.get("color")[0].startswith("Select a valid choice")
