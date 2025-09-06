#!/usr/bin/env python
# coding=utf-8
from enum import Enum, unique  # noqa: F401,E402
from .choice import ChoiceEnum  # noqa: F401,E402

__version__ = "2.1.2"

VERSION = __version__

__all__ = ["ChoiceEnum", "Enum", "unique"]
