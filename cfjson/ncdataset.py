import json
import numpy
import sys
from json import encoder
from collections import OrderedDict
from netCDF4 import Dataset, num2date



encoder.FLOAT_REPR = lambda o: format(o, '.4g')

AXIS_VAR=['time','lat','latitude','lon','longitude','site']

def print_val(val):
    """
    # Turn val into something JSON can deal with i.e. int, float or string
    """
    if type(val) in [bool, numpy.bool, numpy.bool_]:
        return bool(val)
    if type(val) in [int, numpy.int, numpy.int_, numpy.intc, numpy.intp, numpy.int8, numpy.int16, numpy.int32, numpy.int64, numpy.uint8, numpy.uint16, numpy.uint32, numpy.uint64]:
        return int(val)
    if type(val) in [float, numpy.float, numpy.float_, numpy.float16, numpy.float32, numpy.float64] :
        return 'null' if numpy.isnan(val) else '%.6g' % val
    if type(val) in [complex, numpy.complex, numpy.complex_, numpy.complex64, numpy.complex128]:
        return [float(val.real),float(val.imag)]
    else:
        return str(val)

    
    
class NCDataset(Dataset):
    """
    Class derived from the Dataset class of NetCDF4 library and implementing methods
    that dump to and load from JSON.
    """
    def to_dict(self,mapping={}):
        """
        Dumps the dataset as an ordered dictionnary following the same conventions as ncdump.
        Assumes the Dataset is CF complient.
        """
        res=OrderedDict()
        try:
            res['dimensions']=OrderedDict()
            for dim in self.dimensions:
                if len(self.dimensions[dim])>1:
                    res['dimensions'][dim]=len(self.dimensions[dim])
        except:
            print('Failed to export dimensions')
            raise
        try:
            res['attributes']=OrderedDict()
            for att in self.ncattrs():
                res['attributes'].update({str(att):print_val(self.getncattr(att))})
        except:
            print('Failed to export all global_attribute %s'%(att))
        res['variables']=OrderedDict()
        #Put axis variables first
        for special_var in AXIS_VAR:
            if special_var in self.variables:
                res['variables'][special_var]=None
        for var in self.variables:
            varout=mapping.get(var,var)
            try:
                if var=='dum1': #This is UDS artefact
                    continue
                if var=='time':
                    res['variables']['time']={
                        'shape':['time'],
                        'type': 'string',
                        'attributes':{'units':'ISO8601 timestamps'}    
                    }
                    continue
                vardims=[d for d in self.variables[var].dimensions if d in res['dimensions']]
                res['variables'][varout]={'attributes':OrderedDict()}
                if len(vardims):res['variables'][varout]['shape']=vardims
                for att in self.variables[var].ncattrs():
                    if att not in ['missing_value','cell_methods']: 
                        res['variables'][varout]['attributes'].update({str(att):print_val(self.variables[var].getncattr(att))})
            except:
                print('Failed to export variable %s description or attributes'%(var))
                raise

        for var in self.variables:
            varout=mapping.get(var,var)
            try:
                if var=='dum1':
                    continue
                self.variables[var].set_auto_mask(True)
                rawvals=numpy.ma.array(self.variables[var][:]).filled(numpy.nan).squeeze()
                if var == 'time' and 'units' in self.variables[var].ncattrs():
                    if 'calendar' in self.variables[var].ncattrs():
                        times=num2date(rawvals, self.variables[var].getncattr('units'),
                                       self.variables[var].getncattr('calendar'))
                    else:
                        times=num2date(rawvals, self.variables[var].getncattr('units'))
                    if not isinstance(times, numpy.ndarray):
                        times=[times]
                    vals=[t.strftime('%Y-%m-%dT%H:%M:%SZ') for t in times]
                    res['variables'][varout]['data']=vals
                else:
                    res['variables'][varout]['data']=rawvals.tolist()
            except:
                  print('Failed to export values for variable %s'%(var))
                  raise

        return res

    def json_dumps(self, indent=None, separators=None, mapping={}):
        """
        Dumps a JSON representation of the Dataset following the same conventions as ncdump.
        Assumes the Dataset is CF complient.
        """
        dico=self.to_dict(mapping)
        return json.dumps(dico, indent=indent, separators=separators).replace('NaN','null')

    
    def from_json(self, js, mapping={}):
        """
        Populates a NCDataset object from its JSON representation.
        """
        try:
            dico=json.JSONDecoder(object_pairs_hook=OrderedDict).decode(js)
        except:
            print('Could not decode JSON')
            raise

        try:
            for dim in dico['dimensions']:
                self.createDimension(dim,dico['dimensions'][dim])
        except:
            print('Issue occured when creating dimension %s'%dim)
            raise
            
        try:
            self.setncatts(dico['global_attributes'])
        except:
            print('Issue occured when inserting global attributes')

        
        for var in dico['variables']:
            try:
                if '_FillValue' in dico['variables'][var]['attributes']:
                    self.createVariable(var, dico['variables'][var]['type'],
                                        dimensions=dico['variables'][var]['dimensions'],
                                        fill_value=dico['variables'][var]['attributes']['_FillValue'])
                else:
                    self.createVariable(var, dico['variables'][var]['type'],
                                        dimensions=dico['variables'][var]['dimensions'])
            except:
                print('Could not create variable %s'%var)
                raise

            for att in dico['variables'][var]['attributes']:
                try:
                    if att != '_FillValue':
                        self.variables[var].setncattr(att, dico['variables'][var]['attributes'][att])
                except:
                    print('Failed to set variable %s attribute %s to %s'%(var,
                                                                          att,
                                                                          str(dico['variables'][var]['attributes'][att])))
                        
            try:
                self.variables[var][:]=numpy.array(dico['data'][var]).reshape(self.variables[var].shape)
            except:
                print('Could not populate variable %s'%var)
                
if __name__ == '__main__':
    import sys
    if len(sys.argv)<2:
        print('Usage: ncdataset.py netcdf_file [json_file]')
    else:
        nc=NCDataset(sys.argv[1])
        s=nc.json_dumps(indent=2)
        if len(sys.argv)<3:
            print(s)
        else:
            f=open(sys.argv[2],'w')
            f.write(s)
            f.close()
            
                
