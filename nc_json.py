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
    def to_dict(self):
        """
        Dumps the dataset as an ordered dictionnary following the same conventions as ncdump.
        Assumes the Dataset is CF complient.
        """
        res=OrderedDict()
        res['dimensions']=OrderedDict()
        for dim in self.dimensions:
            res['dimensions'][dim]=len(self.dimensions[dim])

        res['variables']=OrderedDict()
        for var in self.variables:
            res['variables'][var]={'type':self.variables[var].datatype.name,
                                   'dimensions':[d for d in self.variables[var].dimensions],
                                   'attributes':OrderedDict()}
            for att in self.variables[var].ncattrs():
                res['variables'][var]['attributes'].update({str(att):print_val(self.variables[var].getncattr(att))})

        res['global_attributes']=OrderedDict()
        for att in self.ncattrs():
            res['global_attributes'].update({str(att):print_val(self.getncattr(att))})

        res['data']=OrderedDict()
        for var in self.variables:

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
        dico=json.JSONDecoder(object_pairs_hook=OrderedDict).decode(js)
        
        for dim in dico['dimensions']:
            self.createDimension(dim,dico['dimensions'][dim])

        self.setncatts(dico['global_attributes'])

        for var in dico['variables']:
            if '_FillValue' in dico['variables'][var]['attributes']:
                self.createVariable(var, dico['variables'][var]['type'],
                                    dimensions=dico['variables'][var]['dimensions'],
                                    fill_value=dico['variables'][var]['attributes']['_FillValue'])
            else:
                self.createVariable(var, dico['variables'][var]['type'],
                                    dimensions=dico['variables'][var]['dimensions'])
                
            for att in dico['variables'][var]['attributes']:
                if att != '_FillValue':
                    self.variables[var].setncattr(att, dico['variables'][var]['attributes'][att])
            
            self.variables[var][:]=numpy.array(dico['data'][var]).reshape(self.variables[var].shape)
        
        
#dst=NCDataset("/tmp/query_results/query.b2d4a6f8-d6c4-11e6-9a1c-0242ac130006.nc")
#js = dst.json_dumps(indent=4, separators=(',', ': '))

#new_dst=NCDataset('/tmp/seb.nc','w')

#new_dst.from_json(js)
#new_dst.close()
