#!/usr/bin/env python
# coding=utf-8
import pytest

from tests.app.models import ColorModel, ColorForm


@pytest.mark.django_db
def test_create(colors, status):
    instance = ColorModel.objects.create()
    assert instance.color == colors.RED.value
    assert instance.status == status.PROCESSING.value


@pytest.mark.django_db
def test_save_and_filter(colors):
    instance = ColorModel()
    instance.color = colors.BLUE.value
    instance.save()

    assert instance.color == colors.BLUE.value

    instance2 = ColorModel.objects.get(pk=instance.pk)
    assert instance2.color == colors.BLUE.value

    instance3 = ColorModel.objects.filter(color=colors.BLUE.value).first()
    assert instance3.pk == instance.pk


@pytest.mark.django_db
def test_check_fail(colors):
    form = ColorForm(data={"color": colors.BLUE.value})
    assert form.is_valid() is True

    _color = -1
    assert _color not in colors

    form = ColorForm(data={"color": _color})
    assert form.is_valid() is False
    assert form.errors.get("color")[0].startswith("Select a valid choice")
