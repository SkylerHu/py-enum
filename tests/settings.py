#!/usr/bin/env python
# coding=utf-8
SECRET_KEY = "py-enum"

ALLOWED_HOSTS = ['*']

DATABASES = {
    "default": dict(ENGINE='django.db.backends.sqlite3', NAME=':memory:')
}

INSTALLED_APPS = (
    'tests.app',
)

MIDDLEWARE_CLASSES = ()
