import json
from json import encoder
import xarray as xr
from pandas import to_datetime
from collections import OrderedDict

encoder.FLOAT_REPR = lambda o: format(o, '.4g')

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
            res['global_attributes']=OrderedDict()
            res['global_attributes'].update(self._obj.attrs)
        except:
            print('Failed to export all global_attribute %s'%(att))
            
        res['variables']=OrderedDict()
        #Put axis variables first
        for special_var in AXIS_VAR:
            if special_var in self._obj.variables.keys():
                res['variables'][special_var]=None
        for var in self._obj.variables:
            try:
                if var=='dum1': #This is UDS artefact
                    continue
                if var=='time':
                    res['variables']['time']={
                        'dimensions':['time'],
                        'attributes':{'units':'ISO8601 timestamps'}    
                    }
                    continue
                vardims=[d for d in self._obj.variables[var].dims if d in res['dimensions']]
                varout=mapping.get(var,var)
                res['variables'][varout]={'attributes':OrderedDict()}
                if len(vardims):res['variables'][varout]['dimensions']=vardims
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

        res['data']=OrderedDict()
        for special_var in AXIS_VAR:
            if special_var in self._obj.variables:
                res['data'][special_var]=None
        for var in self._obj.variables:
            varout=mapping.get(var,var)
            try:
                if var=='dum1':
                    continue
                rawvals=self._obj.variables[var].values.squeeze()
                if var == 'time':
                    vals=[t.strftime('%Y-%m-%dT%H:%M:%SZ') for t in to_datetime(rawvals)]
                    res['data'][varout]=vals
                else:
                    res['data'][varout]=rawvals.tolist()
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
            dico['global_attributes'].update(attributes)
        except:
            print('Failed to set global_attributes %s'%(attributes))
        return json.dumps(dico, indent=indent, separators=separators)
    


if __name__ == '__main__':
    import sys
    if len(sys.argv)<2:
        print('Usage: xarray.py netcdf_file [json_file]')
    else:
        nc=xr.open_dataset(sys.argv[1])
        s=nc.cfjson.json_dumps(indent=2)
        if len(sys.argv)<3:
            print s
        else:
            f=open(sys.argv[2],'w')
            f.write(s)
            f.close()
