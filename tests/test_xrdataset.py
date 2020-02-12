"Tests for xrdataset.py"

import json
import unittest as uni

import numpy as np
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

    @staticmethod
    def test_from_json_scalar():
        "Test from_json for scalar / single-value data"

        ds1 = xr.Dataset()
        ds1['foo'] = ([], 1)
        json_str = ds1.cfjson.json_dumps()

        # Convert the list-of-length-one to a scalar / single value
        dict1 = json.loads(json_str)
        data_list = dict1['variables']['foo']['data']
        data_value = data_list[0]
        dict1['variables']['foo']['data'] = data_value

        ds2 = xr.Dataset()
        ds2.cfjson.from_json(json.dumps(dict1))


class TestTimeStringTimezones(uni.TestCase):

    def test_timezone_Z(self):

        ds = xr.Dataset()
        cfjson_string = '{"dimensions": {"time": 2}, "variables": {"x": {"shape": ["time"], "data": [10, 20], "attributes": {}}, "time": {"shape": ["time"], "data": ["2020-01-01T00:00:00Z", "2020-01-01T01:00:00Z"], "attributes": {"units": "ISO8601 timestamps"}}}}'
        ds.cfjson.from_json(cfjson_string)
        self.assertEqual(ds['time'].dtype, np.dtype('<M8[ns]'))

    def test_timezone_none(self):

        ds = xr.Dataset()
        cfjson_string = '{"dimensions": {"time": 2}, "variables": {"x": {"shape": ["time"], "data": [10, 20], "attributes": {}}, "time": {"shape": ["time"], "data": ["2020-01-01T00:00:00", "2020-01-01T01:00:00"], "attributes": {"units": "ISO8601 timestamps"}}}}'
        ds.cfjson.from_json(cfjson_string)
        self.assertEqual(ds['time'].dtype, np.dtype('<M8[ns]'))

    def test_timezone_mixed(self):

        ds = xr.Dataset()
        cfjson_string = '{"dimensions": {"time": 2}, "variables": {"x": {"shape": ["time"], "data": [10, 20], "attributes": {}}, "time": {"shape": ["time"], "data": ["2020-01-01T00:00:00", "2020-01-01T01:00:00Z"], "attributes": {"units": "ISO8601 timestamps"}}}}'
        ds.cfjson.from_json(cfjson_string)
        self.assertEqual(ds['time'].dtype, np.dtype('O'))
