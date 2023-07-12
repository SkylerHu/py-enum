#!/usr/bin/env python
# coding=utf-8
from rest_framework import serializers

from .models import ColorModel


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorModel
        fields = ('status', )
        depth = 1
