# coding: utf-8
from setuptools import setup

NAME = "cfjson"
VERSION = "0.4.1"

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

tests_require = [
    "netCDF4",
    "pandas",
    "xarray>=0.9.1",
]

install_requires = [
    "xarray>=0.9.1",
]

setup(
    name=NAME,
    version=VERSION,
    description="CF JSON converters",
    author_email="support@metocean.co.nz",
    keywords=["CF-JSON"],
    packages=[NAME],
    install_requires=install_requires,
    tests_require=tests_require,
    long_description="""\
    Classes and functions for CF-JSON format conversion
    """,
)
