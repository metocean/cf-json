# cf-json
CF based JSON specification for climate and forecast data

The basic idea is to pretty print CF-NetCDF as a JSON dictionary with arrays following CF-NetCDF ordering conventions.

As with CF-NetCDF, the schema has 3 main sections:
1. dimensions - dictionary of data dimensions definign their length
2. variables - dictionary of variables definition with dimensions and other attributes.
3. data - dictionary of data keyed by variable id with data in arrays of shape coirresponding to dimensions

Numeric data should be expressed as numbers, text data as strings. null should be used to represent NaN. A missing_value or \_FillValue attribute can be defined as with CF-NetCDF.  

CF-JSON has a number of recommendations outside CF-netcdf:
1. Singleton dimensions should be squashed
2. Any number of global attributes can be added at the top level of the JSON document, but must not use the reserved keys "variables","dimensions" or "data".
3. Each variable should have a standard_name field that defines the cf-conventions standard name
