import datetime
import json
import sys
from collections import OrderedDict
from json import encoder

import numpy
import pandas as pd

encoder.FLOAT_REPR = lambda o: format(o, ".4f").rstrip("0").rstrip(".")

AXIS_VAR = ["time", "lat", "latitude", "lon", "longitude", "site"]


class PDDataset(pd.DataFrame):
    """
    Class to export pandas DataFrame - just support simple timeseries for now
    """

    def __init__(self, dataframe):
        self._data = dataframe._data
        self._item_cache = dataframe._item_cache

    def to_dict(self, mapping={}, factor={}, offset={}):
        """
        Dumps the dataset as an ordered dictionary following the same conventions as ncdump.
        """
        res = OrderedDict()
        try:
            res["dimensions"] = OrderedDict({"time": len(self)})
        except:
            print("Failed to export dimensions")
            raise

        res["variables"] = OrderedDict()
        # Put axis variables first
        for special_var in AXIS_VAR:
            if special_var in self.columns:
                res["variables"][special_var] = None
        for var in self.columns:
            varout = mapping.get(var, var)
            if varout is None:
                continue  # Ignore variable by specify mapping to None
            try:
                res["variables"][varout] = OrderedDict(
                    {"attributes": {"standard_name": varout}}
                )
                vardims = ["time"]
                if len(vardims):
                    res["variables"][varout]["shape"] = vardims
            except:
                print("Failed to export variable %s description or attributes" % (var))
                raise

        timevals = [
            t.strftime("%Y-%m-%dT%H:%M:%SZ") for t in self.index.to_pydatetime()
        ]
        res["variables"]["time"] = {
            "shape": ["time"],
            "attributes": {"units": "ISO8601 datetimes"},
            "type": "string",
            "data": timevals,
        }
        for var in self.columns:
            varout = mapping.get(var, var)
            try:
                rawvals = self.loc[:, var].values
                if rawvals.dtype != numpy.dtype("O"):
                    fac = factor.get(var, 1.0)
                    off = offset.get(var, 0.0)
                    if fac != 1.0:
                        rawvals = rawvals.astype("f") * fac
                    if off != 0.0:
                        rawvals = rawvals.astype("f") + off
                res["variables"][varout]["data"] = rawvals.tolist()
            except:
                print("Failed to export values for variable '%s'" % (var))
                raise
        return res

    def json_dumps(
        self,
        indent=None,
        separators=None,
        mapping={},
        attributes={},
        factor={},
        offset={},
    ):
        """
        Dumps a JSON representation of the Dataset following the same conventions as ncdump.
        Assumes the Dataset is CF compliant.
        """
        dico = self.to_dict(mapping, factor, offset)
        try:
            dico["attributes"] = OrderedDict(attributes)
        except:
            print("Failed to export all global attributes %s" % (att))
        return json.dumps(dico, indent=indent, separators=separators).replace(
            "NaN", "null"
        )


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: pddataset.py csv_file [json_file]")
    else:
        dataframe = pd.read_csv(sys.argv[1], header=1, index_col=0, parse_dates=True)
        df = PDDataset(dataframe)
        s = df.json_dumps(indent=2)
        if len(sys.argv) < 3:
            print(s)
        else:
            f = open(sys.argv[2], "w")
            f.write(s)
            f.close()
