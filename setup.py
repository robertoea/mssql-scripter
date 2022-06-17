#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import io
import os
import platform as _platform
import sys

from setuptools import setup

MSSQLSCRIPTER_VERSION = "2.0.0a1"

CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "License :: OSI Approved :: MIT License",
]

DEPENDENCIES = ["wheel>=0.37.1"]

setup(
    install_requires=DEPENDENCIES,
    name="mssql-scripter",
    version=MSSQLSCRIPTER_VERSION,
    description="Microsoft SQL Scripter Command-Line Tool",
    license="MIT",
    author="Microsoft Corporation",
    author_email="sqlcli@microsoft.com",
    url="https://github.com/Microsoft/mssql-scripter/",
    zip_safe=True,
    long_description=open("README.rst").read(),
    classifiers=CLASSIFIERS,
    include_package_data=True,
    scripts=["mssql-scripter", "mssql-scripter.bat"],
    packages=[
        "mssqlscripter",
        "mssqlscripter.mssqltoolsservice",
        "mssqlscripter.jsonrpc",
        "mssqlscripter.jsonrpc.contracts",
    ],
)
