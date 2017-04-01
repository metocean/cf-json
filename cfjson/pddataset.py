import json
import numpy
import sys
import datetime
import pandas as pd
from json import encoder
from collections import OrderedDict

encoder.FLOAT_REPR = lambda o: format(o, '.4g')

AXIS_VAR=['time','lat','latitude','lon','longitude','site']
    
class PDDataset(pd.DataFrame):
    """
    Class to export pandas DataFrame - just support simple timeseries for now
    """
    def __init__(self,dataframe):
        self._data=dataframe._data
        self._item_cache=dataframe._item_cache
    
    def to_dict(self,mapping={},factor={},offset={}):
        """
        Dumps the dataset as an ordered dictionary following the same conventions as ncdump.
        """
        res=OrderedDict()
        try:
            res['dimensions']=OrderedDict({'time':len(self)})
        except:
            print('Failed to export dimensions')
            raise
        
        res['variables']=OrderedDict()
        #Put axis variables first
        for special_var in AXIS_VAR:
            if special_var in self.columns:
                res['variables'][special_var]=None
        for var in self.columns:
            varout=mapping.get(var,var)
            if varout is None:continue #Ignore variable by specify mapping to None
            try:
                res['variables'][varout]=OrderedDict({'attributes':{'standard_name':varout}})
                vardims=['time']
                if len(vardims):res['variables'][varout]['dimensions']=vardims
            except:
                print('Failed to export variable %s description or attributes'%(var))
                raise

        res['data']=OrderedDict()
        for special_var in AXIS_VAR:
            if special_var in self.columns:
                res['data'][special_var]=None
        timevals=[t.strftime('%Y-%m-%dT%H:%M:%SZ') for t in self.index.astype(datetime.datetime)]
        for var in self.columns:
            varout=mapping.get(var,var)
            fac=factor.get(var,1.0)
            off=offset.get(var,0.0)
            try:
                rawvals=(fac*self.loc[:,var].values+off).tolist()
                res['data'].update({varout:rawvals})
            except:
                  print('Failed to export values for variable %s'%(var))
                  raise
        return res

    def json_dumps(self, indent=None, separators=None, mapping={}, attributes={},factor={},offset={}):
        """
        Dumps a JSON representation of the Dataset following the same conventions as ncdump.
        Assumes the Dataset is CF complient.
        """
        dico=self.to_dict(mapping,factor,offset)
        try:
            dico['global_attributes']=OrderedDict(attributes)
        except:
            print('Failed to export all global_attribute %s'%(att))
        return json.dumps(dico, indent=indent, separators=separators)

                
if __name__ == '__main__':
    WINDDIR={'N':0,'NNE':22.5,'NE':45,'ENE':67.5,'E':90,'ESE':112.5,'SE':135,'SSE':157.5,
             'S':180,'SSW':202.5,'SW':225,'WSW':247.5,'W':270,'WNW':292.5,'NW':315,'NNW':337.5}
    convert_winddir=lambda d:WINDDIR[d] if d in WINDDR else d
    import sys
    if len(sys.argv)<2:
        print 'Usage: pddataset.py csv_file [json_file]'
    else:
        dataframe=pd.read_csv(sys.argv[1],header=4,index_col=0,parse_dates=True,converters={'WindDir':convert_winddir})
        df=PDDataset(dataframe)
        s=df.json_dumps(indent=2)
        if len(sys.argv)<3:
            print s
        else:
            f=open(sys.argv[2],'w')
            f.write(s)
            f.close()
            
                
