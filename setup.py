# coding: utf-8
import sys
from distutils.core import setup

NAME = "cfjson"
VERSION = "0.1"

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["netcdf4"]

setup(
    name=NAME,
    version=VERSION,
    description="CF JSON converters",
    author_email="",
    url="",
    keywords=["CF-JSON"],
    install_requires=REQUIRES,
    long_description="""\
    Classes and functions for CF-JSON format conversion
    """
)

