"Tests for xrdataset.py"

import unittest as uni

import xarray as xr

# pylint: disable=unused-import
from cfjson.xrdataset import CFJSONinterface


class TestDimensionlessVariable(uni.TestCase):
    """Tests for dimensionless / shape=[] variables
       This is allowed in the 0.2 (-ish?) spec, but a bit tricky with xarray...
    """

    @staticmethod
    def test_xarray_json_roundtrip():
        "Test round-trip xarray -> json -> xarray"
        ds1 = xr.Dataset()
        ds1['foo'] = ([], 1)
        json_str = ds1.cfjson.json_dumps()
        ds2 = xr.Dataset()
        ds2.cfjson.from_json(json_str)
