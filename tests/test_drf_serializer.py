#!/usr/bin/env python
# coding=utf-8
import pytest

from tests.app.serializers import ColorSerializer


@pytest.mark.django_db
def test_validate(status):
    s = ColorSerializer(data={'status': status.CLOSED})
    assert s.is_valid() is True

    _status = 'no'
    assert _status not in status

    s = ColorSerializer(data={'status': _status})
    assert s.is_valid() is False
    assert s.errors['status'][0].code == 'invalid_choice'
