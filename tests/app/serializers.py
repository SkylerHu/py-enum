#!/usr/bin/env python
# coding=utf-8
from rest_framework import serializers

from .models import ColorModel
from .enums import Color


class ColorSerializer(serializers.ModelSerializer):

    class Meta:
        model = ColorModel
        fields = ("status",)
        depth = 1


class ApiSerializer(serializers.BaseSerializer):

    color = serializers.ChoiceField(help_text="选择颜色", choices=Color.choices)
