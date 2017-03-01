# cf-json
CF based JSON specification for climate and forecast data

The basic idea is to pretty print CF-NetCDF as a JSON dictionary with arrays following CF-NetCDF ordering conventions. 

CF-JSON has a number of standards outside CF-netcdf:
1. Singleton dimensions should be squashed
2. Any number of global attributes can be added at the top level of the JSON document, but must not use the reserved keys "variables","dimensions" or "data".
