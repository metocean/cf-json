import unittest
import time
import xarray as xr

import sys
import os
sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..'))

from cfjson import *

TEST_FILES=['uds_single_site.nc','uds_multi_site.nc']
TMP_DIR='/tmp'

def write_file(filename,json):
    filename=os.path.join(TMP_DIR,filename)
    with open(filename,'w') as f:
        f.write(json)
    return filename

def read_file(filename):
    with open(filename) as f:
        jsonstr=f.read()
        print jsonstr
    return json.loads(jsonstr)

def check_required(obj):
    assert 'attributes' in obj
    assert 'dimensions' in obj
    assert 'variables' in obj
    for v in obj['variables']:
        assert 'data' in obj['variables'][v]
        assert 'shape' in obj['variables'][v]
        assert 'attributes' in obj['variables'][v]

class TestNCDataset(unittest.TestCase):
    def test_dumps(self):
        for ncfile in TEST_FILES:
            nc=NCDataset(ncfile)
            read_file(write_file(ncfile.replace('.nc','.json'),nc.json_dumps(indent=2)))
        
class TestXarray(unittest.TestCase):
    def test_dumps(self):
        for ncfile in TEST_FILES:
            nc=xr.open_dataset(ncfile)
            read_file(write_file(ncfile.replace('.nc','_xr.json'),nc.cfjson.json_dumps(indent=2)))
            
        
if __name__ == '__main__':
    unittest.main()