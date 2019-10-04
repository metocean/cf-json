# coding: utf-8
import sys
from setuptools import setup

NAME = "cfjson"
VERSION = "0.2"

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["netcdf4"]

tests_require = [
    "netCDF4",
    "pandas",
    "xarray>=0.9.1"]

setup(
    name=NAME,
    version=VERSION,
    description="CF JSON converters",
    author_email="ops@metocean.co.nz",
    keywords=["CF-JSON"],
    packages=[NAME],
    requires=REQUIRES,
    tests_require=tests_require,
    long_description="""\
    Classes and functions for CF-JSON format conversion
    """
)

