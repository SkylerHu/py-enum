#!/usr/bin/env python
# coding=utf-8
from __future__ import absolute_import, unicode_literals

from django import forms
from django.db import models

from .enums import Color, Status


class ColorModel(models.Model):

    color = models.IntegerField(verbose_name="颜色", choices=Color.choices, default=Color.RED.value)
    status = models.CharField(
        verbose_name="状态", max_length=20, choices=Status.choices, default=Status.PROCESSING.value
    )


class ColorForm(forms.ModelForm):
    class Meta:
        model = ColorModel
        fields = ("color",)

    color = models.PositiveIntegerField(verbose_name="颜色", choices=Color.choices)
    status = models.CharField(verbose_name="状态", choices=Status.choices, max_length=20)
