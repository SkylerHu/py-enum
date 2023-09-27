#!/usr/bin/env python
# coding=utf-8
import re

from setuptools import setup, find_packages


def read(file_name):
    with open(file_name, 'rb') as f:
        content = f.read().decode('utf-8')
    return content


version = re.search("__version__ = ['\"]([^'\"]+)['\"]", read('py_enum/__init__.py')).group(1)


setup(
    name='py-enum',
    version=version,
    url='https://github.com/SkylerHu/py-enum.git',
    author='SkylerHu',
    author_email='skylerhu@qq.com',
    description='enums for choices fields',
    long_description=(read('README.md')),
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=['tests*', 'tests']),
    license='MIT Licence',
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
