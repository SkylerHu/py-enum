#!/usr/bin/env python
# coding=utf-8
from __future__ import absolute_import, unicode_literals

from django import forms
from django.db import models

from .enums import Color, Status


class ColorModel(models.Model):

    color = models.IntegerField(verbose_name='颜色', choices=Color, default=Color.RED)
    status = models.CharField(verbose_name='状态', max_length=20, choices=Status, default=Status.PROCESSING)


class ColorForm(forms.ModelForm):
    class Meta:
        model = ColorModel
        fields = ('color', )
