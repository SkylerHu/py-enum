#!/usr/bin/env python
# coding=utf-8
import six
import pytest

from tests.app.models import ColorModel
from tests.app.serializers import ColorSerializer


@pytest.mark.django_db
def test_validate(status):
    s = ColorSerializer(data={'status': status.CLOSED})
    assert s.is_valid() is True
    instance = s.save()
    assert isinstance(instance, ColorModel)

    _status = 'no'
    assert _status not in status

    s = ColorSerializer(data={'status': _status})
    assert s.is_valid() is False
    if six.PY2:
        assert u'valid choice' in s.errors['status'][0]
    else:
        assert s.errors['status'][0].code == 'invalid_choice'
