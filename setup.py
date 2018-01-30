#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2013, Digium, Inc.
# Copyright (c) 2014-2016, Yelp, Inc.
import os

from setuptools import setup

import aiobravado

setup(
    name='aiobravado',
    version=aiobravado.version,
    license='BSD 3-Clause License',
    description='Async library for accessing Swagger-enabled APIs',
    long_description=open(os.path.join(os.path.dirname(__file__),
                                       'README.rst')).read(),
    author='Stephan Jaensch, Digium, Inc. and Yelp, Inc.',
    author_email='sj@sjaensch.org',
    url='https://github.com/sjaensch/aiobravado',
    packages=['aiobravado'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
        'bravado-asyncio >= 0.4.0',
        'bravado-core >= 4.11.0',
        'msgpack-python',
        'python-dateutil',
        'pyyaml',
    ],
    extras_require={
        # as recommended by aiohttp, see http://aiohttp.readthedocs.io/en/stable/#library-installation
        'aiohttp_extras': ['aiodns', 'cchardet'],
    },
)
