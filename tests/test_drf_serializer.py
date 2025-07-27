#!/usr/bin/env python
# coding=utf-8
import pytest

from tests.app.enums import Status
from tests.app.models import ColorModel
from tests.app.serializers import ColorSerializer


@pytest.mark.django_db
def test_validate():
    s = ColorSerializer(data={"status": Status.CLOSED.value})
    assert s.is_valid() is True
    instance = s.save()
    assert isinstance(instance, ColorModel)

    _status = "no"
    assert _status not in Status

    s = ColorSerializer(data={"status": _status})
    assert s.is_valid() is False
    assert s.errors["status"][0].code == "invalid_choice"
