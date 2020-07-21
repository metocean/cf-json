# cf-json
Python package to import / export CF-JSON data

See also: https://github.com/cf-json/cf-json.github.io (which is the source for http://cf-json.org/).

Comment 2020-06-15: I'd really only trust the xarray methods at the moment, the other two have been neglected... So I'd recommend using those from here, and then xarray's own to_pandas, to_netcdf, etc. if required.


## Example

```python3
Python 3.8.3 (default, May 17 2020, 18:15:42)
Type 'copyright', 'credits' or 'license' for more information
IPython 7.10.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]: import json
   ...: import pprint as pp
   ...: import xarray as xr
   ...: from cfjson.xrdataset import CFJSONinterface
   ...: dset = xr.Dataset(data_vars={'hmo': ('time', [0.5, 0.6, 0.7])}, coords={'time': [1, 2, 3]})
   ...: dset['hmo'].attrs = {'standard_name': 'sea_surface_wave_significant_height', 'units': 'm'}
   ...: dset['time'].attrs = {'standard_name': 'time', 'units': 'days since 2020-01-01'}

In [2]: pp.pprint(json.loads(dset.cfjson.json_dumps()))
{'attributes': {},
 'dimensions': {'time': 3},
 'variables': {'hmo': {'attributes': {'standard_name': 'sea_surface_wave_significant_height',
                                      'units': 'm'},
                       'data': [0.5, 0.6, 0.7],
                       'shape': ['time']},
               'time': {'attributes': {'units': 'ISO8601 timestamps'},
                        'data': ['1970-01-01T00:00:00Z',
                                 '1970-01-01T00:00:00Z',
                                 '1970-01-01T00:00:00Z'],
                        'shape': ['time']}}}

In [3]:
```

## License

Copyright 2017, 2018 MetOcean Solutions Ltd.
Copyright 2019-2020 MetOcean Solutions / Meteorological Service of New Zealand Ltd.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
the content of this repository except in compliance with the License. See the
file [LICENSE](LICENSE) for details. You may also obtain a copy of the
License at
[https://www.apache.org/licenses/LICENSE-2.0](https://www.apache.org/licenses/LICENSE-2.0).

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied.  See the License for the
specific language governing permissions and limitations under the License.
