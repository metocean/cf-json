from netCDF4 import Dataset, num2date
import json
import numpy
from collections import OrderedDict
import sys

def print_val(val):
    """
    # Turn val into something JSON can deal with i.e. int, float or string
    """
    if type(val) in [str, unicode]:
        return str(val)
    if type(val) in [bool, numpy.bool, numpy.bool_]:
        return bool(val)
    if type(val) in [int, numpy.int, numpy.int_, numpy.intc, numpy.intp, numpy.int8, numpy.int16, numpy.int32, numpy.int64, numpy.uint8, numpy.uint16, numpy.uint32, numpy.uint64]:
        return int(val)
    if type(val) in [float, numpy.float, numpy.float_, numpy.float16, numpy.float32, numpy.float64] :
        return float(val)
    if type(val) in [complex, numpy.complex, numpy.complex_, numpy.complex64, numpy.complex128]:
        return [float(val.real),float(val.imag)]
    else:
        return str(type(val))

    
    
class NCDataset(Dataset):
    """
    Class derived from the Dataset class of NetCDF4 library and implementing methods
    that dump to and load from JSON.
    """
    def to_dict(self):
        """
        Dumps the dataset as an ordered dictionnary following the same conventions as ncdump.
        Assumes the Dataset is CF complient.
        """
        res=OrderedDict()
        try:
            res['dimensions']=OrderedDict()
            for dim in self.dimensions:
                res['dimensions'][dim]=len(self.dimensions[dim])
        except:
            print('Failed to export dimensions')
            raise

        res['variables']=OrderedDict()
        for var in self.variables:
            try:
                res['variables'][var]={'type':self.variables[var].datatype.name,
                                       'dimensions':[d for d in self.variables[var].dimensions],
                                       'attributes':OrderedDict()}
                for att in self.variables[var].ncattrs():
                    res['variables'][var]['attributes'].update({str(att):print_val(self.variables[var].getncattr(att))})
            except:
                print('Failed to export variable %s description or attributes'%(var))
                raise

        try:
            res['global_attributes']=OrderedDict()
            for att in self.ncattrs():
                res['global_attributes'].update({str(att):print_val(self.getncattr(att))})
        except:
            print('Failed to export all global_attribute %s'%(att))

        res['data']=OrderedDict()
        for var in self.variables:
            try:

                vals=numpy.array(self.variables[var]).flatten().tolist()
            
                  #if var == 'time' and 'units' in self.variables[var].ncattrs():
                  #    if 'calendar' in self.variables[var].ncattrs():
                  #        vals=[str(t) for t in num2date(vals, self.variables[var].getncattr('units'),
                  #        self.variables[var].getncattr('calendar'))]
                  #        res['data'].update({var:vals})
                  #    else:
                  #        vals=[str(t) for t in num2date(vals, self.variables[var].getncattr('units'))]
                  #        res['data'].update({var:vals})
                  #else:
                vals=[print_val(val) for val in vals]
                res['data'].update({var:vals})
            except:
                  print('Failed to export values for variable %s'%(var))
                  raise

        return res

    def json_dumps(self, indent=None, separators=None):
        """
        Dumps a JSON representation of the Dataset following the same conventions as ncdump.
        Assumes the Dataset is CF complient.
        """
        dico=self.to_dict()
        return json.dumps(dico, indent=indent, separators=separators)

    
    def from_json(self, js):
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
                
