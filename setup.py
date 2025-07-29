#!/usr/bin/env python
# coding=utf-8
import re

from setuptools import setup, find_packages


def read(file_name):
    with open(file_name, "r") as f:
        content = f.read()
    return content


version_match = re.search(r"__version__ = ['\"]([^'\"]+)['\"]", read("py_enum/__init__.py"))
if version_match is None:
    raise RuntimeError("Unable to find version string in py_enum/__init__.py")
version = version_match.group(1)

read_me = read("README.md")
# 替换文档的相对路径为绝对路径地址
read_me = read_me.replace("(./docs/", "(https://github.com/SkylerHu/py-enum/blob/master/docs/")


setup(
    name="py-enum",
    version=version,
    url="https://github.com/SkylerHu/py-enum.git",
    author="SkylerHu",
    author_email="skylerhu@qq.com",
    description="enums for choices fields",
    keywords=["python", "enum", "ChoiceEnum", "enumerate"],
    long_description=read_me,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests*", "tests"]),
    license="MIT Licence",
    include_package_data=True,
    package_data={"py_enum": ["py.typed"]},
    zip_safe=False,
    platforms="any",
    install_requires=[],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
