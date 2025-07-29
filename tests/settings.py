#!/usr/bin/env python
# coding=utf-8
SECRET_KEY = "py-enum"

ALLOWED_HOSTS = ["*"]

DATABASES = {"default": dict(ENGINE="django.db.backends.sqlite3", NAME=":memory:")}

USE_TZ = "Asia/Shanghai"

INSTALLED_APPS = (
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "rest_framework",
    "tests.app",
)

MIDDLEWARE_CLASSES = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
)
