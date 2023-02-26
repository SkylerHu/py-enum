#!/usr/bin/env python
# coding=utf-8
import re

from setuptools import setup, find_packages


with open('py_enum/__init__.py', 'rb') as f:
    init_py = f.read().decode('utf-8')
version = re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


setup(
    name='py-enum',
    version=version,
    url='https://github.com/SkylerHu/py-enum.git',
    author='skyler',
    author_email='skylerhu@qq.com',
    description='enums for choices fields',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'six>=1.12.0',
    ],
    python_requires=">=2.7",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',

    ],
)
