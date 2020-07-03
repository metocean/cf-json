import datetime as dt
import json
from json import encoder
import xarray as xr
import numpy as np
from pandas import to_datetime
from collections import OrderedDict
import dateutil
import logging
import six

logging.basicConfig()

encoder.FLOAT_REPR = lambda o: format(o, '.4f').rstrip('0').rstrip('.')

AXIS_VAR=['time','lat','latitude','lon','longitude','site']
SPECIAL_ATTRS=['missing_value','cell_methods']

@xr.register_dataset_accessor('cfjson')
class CFJSONinterface(object):
    def __init__(self, xarray_obj):
        self._obj=xarray_obj
        
    def to_dict(self,mapping):
        """
        Dumps the dataset as an ordered dictionary following the same conventions as ncdump.
        """
        res=OrderedDict()
        try:
            res['dimensions']=OrderedDict()
            for dim in self._obj.dims:
                if self._obj.dims[dim]>1:
                    res['dimensions'][dim]=self._obj.dims[dim]
        except:
            print('Failed to export dimensions')
            raise
        
        try:
            res['attributes']=OrderedDict()
            res['attributes'].update(self._obj.attrs)
        except:
            print('Failed to export all global_attribute %s'%(att))
            
        res['variables']=OrderedDict()
        #Put axis variables first
        for special_var in AXIS_VAR:
            if special_var in self._obj.variables.keys():
                res['variables'][special_var]=None
        for var in self._obj.variables:
            try:
                if var=='dum1': #This is a UDS artefact
                    continue
                if var=='time':
                    res['variables']['time']={
                        'shape':['time'],
                        'attributes':{'units':'ISO8601 timestamps'}    
                    }
                    continue
                vardims=[d for d in self._obj.variables[var].dims if d in res['dimensions']]
                varout=mapping.get(var,var)
                res['variables'][varout]={'attributes':OrderedDict()}
                if vardims:
                    res['variables'][varout]['shape'] = vardims
                else:
                    res['variables'][varout]['shape'] = []
                for att in self._obj.variables[var].attrs:
                    if att not in SPECIAL_ATTRS:
                        newatt=self._obj.variables[var].attrs[att]
                        try:
                            newatt=float(newatt)
                        except:
                            newatt=str(newatt)
                        res['variables'][varout]['attributes'][att]=newatt
            except:
                print('Failed to export variable %s description or attributes'%(var))
                raise

        for var in self._obj.variables:
            varout=mapping.get(var,var)
            try:
                if var=='dum1':
                    continue
                rawvals=np.atleast_1d(self._obj.variables[var].values.squeeze())
                if var == 'time':
                    vals=[t.strftime('%Y-%m-%dT%H:%M:%SZ') for t in to_datetime(rawvals)]
                    res['variables'][varout]['data']=vals
                else:
                    res['variables'][varout]['data']=rawvals.tolist()
            except:
                  print('Failed to export values for variable %s'%(var))
                  raise

        return res

    def json_dumps(self, indent=2, separators=None, mapping={}, attributes={}):
        """
        Dumps a JSON representation of the Dataset following the same conventions as ncdump.
        Assumes the Dataset is CF complient.
        """
        dico=self.to_dict(mapping)
        try:
            dico['attributes'].update(attributes)
        except:
            print('Failed to set global attributes %s'%(attributes))
        return json.dumps(dico, indent=indent, separators=separators).replace('NaN','null')
    

    def from_json(self, js):
        """Convert CF-JSON string or dictionary to xarray Dataset
        Example:
        import xarray as xr
        from cfjson import xrdataset
        cfjson_string = '{"dimensions": {"time": 1}, "variables": {"x": {"shape": ["time"], "data": [1], "attributes": {}}}}'
        dataset = xr.Dataset()
        dataset.cfjson.from_json(cfjson_string)

        """

        if isinstance(js, six.string_types):
            try:
                dico = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(js)
            except:
                print('Could not decode JSON string')
                raise
        else:
            dico = js

        if 'attributes' in dico.keys():
            # Copy global attributes
            logging.debug('copying global attributes: {}'.format(dico['attributes'].items()))
            for k,v in six.iteritems(dico['attributes']):
                self._obj.attrs[k] = v
        else:
            logging.debug('no global attributes found')

        # Copy variables and their attributes and dimensions
        for varname,var in six.iteritems(dico['variables']):
            logging.debug('copying variable "{}" data'.format(varname))
            if "shape" not in var.keys():
                logging.warning("missing shape (required by CF-JSON spec >=0.2)")
                var["shape"] = []
            # Ideally we'd use udunits to find "time" variables, but tricky in
            # Python (cf_units doesn't seem to provide utScan or utIsTime)...
            if 'units' in var['attributes'] and var['attributes']['units'] == 'ISO8601 timestamps':
                time_strings = var['data']
                logging.debug('units string indicates time variable, converting to datetime64')
                time_dt = [dateutil.parser.parse(tx) for tx in time_strings]
                # If timezone information was provided (e.g., "Z")
                if any([t.utcoffset() is not None for t in time_dt]):
                    if all([t.utcoffset() == dt.timedelta(0) for t in time_dt]):
                        # Timezone-aware, even if they're all the same timezone, would lead to dtype=object
                        time_dt = [t.replace(tzinfo=None) for t in time_dt]
                    else:
                        logging.warning('Mixed timezones (or mixed naive / aware) in input, may lead to dtype=object in output')
                self._obj[varname] = (var['shape'], time_dt)
                logging.debug('copying variable "{}" attributes: {}'.format(varname, var['attributes'].items()))
                self._obj[varname].attrs = var['attributes']
                self._obj[varname].attrs['units'] = 'Python datetime64 objects'
            else:
                if var['shape']:
                    # shape=['dim1'] (in contrast to shape=[])
                    self._obj[varname] = (var['shape'], var['data'])
                else:
                    # shape=[] is allowed, but a bit more tricky...
                    if isinstance(var['data'], list):
                        if len(var['data']) > 1:
                            msg = 'len(data) > 1 not allowed with empty / missing shape; varname: {}'.format(varname)
                            raise Exception(msg)
                        # shape=[] with data=[1.2] (in contrast to data=1.2)
                        self._obj[varname] = (var['shape'], var['data'][0])
                    else:
                        # shape=[] with data=1.2 (in contrast to data=[1.2])
                        self._obj[varname] = (var['shape'], var['data'])
                        # TODO: is shape=[] with data=[] allowed and needs to be handled?
                logging.debug('copying variable "{}" attributes: {}'.format(varname, var['attributes'].items()))
                # Some cases result in a dtype=object array with None elements,
                # but if this is just due to a mix of "null" and numeric values,
                # we can avoid some downstream problems by casting now, which
                # should also convert any None values to numpy NaN.
                if self._obj[varname].dtype == 'O':
                    dtype_set = set([type(el) for el in self._obj[varname].data.flatten()])
                    if str not in dtype_set:
                        if float not in dtype_set:
                            logging.warning('casting variable "{}" to float to preserve None / NaN, but no floats in original data'.format(varname))
                        self._obj[varname] = self._obj[varname].astype(float)

                self._obj[varname].attrs = var['attributes']



if __name__ == '__main__':
    import sys
    if len(sys.argv)<2:
        print('Usage: xarray.py netcdf_file [json_file]')
    else:
        nc=xr.open_dataset(sys.argv[1])
        s=nc.cfjson.json_dumps(indent=2)
        if len(sys.argv)<3:
            print(s)
        else:
            f=open(sys.argv[2],'w')
            f.write(s)
            f.close()
