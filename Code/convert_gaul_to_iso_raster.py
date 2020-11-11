import pandas as pd
from osgeo import ogr, gdal
import os
import rasterio
import glob
#import raster_tools_kristine as rt
import subprocess
import numpy as np
from learn2map import raster_tools as rt
import unidecode
import geopandas as gpd
from pycountry import countries


in_tif = '/Users/kristine/WRI/NationalGeographic/Phase2/Country_Bounds/GAUL_Bounds.tif'
out_tif = '/Users/kristine/WRI/NationalGeographic/Phase2/Country_Bounds/GAUL_ISO_Bounds.tif'
out_match_tif = '/Users/kristine/WRI/NationalGeographic/Phase2/Country_Bounds/GAUL_ISO_Bounds_index.tif'

country_codes = pd.read_csv('/Users/kristine/WRI/NationalGeographic/Phase2/Country_Bounds/full_country_codes.csv')

in_src = rasterio.open(in_tif)
in_data = in_src.read(1)

gaul_countries = np.unique(in_data)
match_pixels = np.zeros((in_src.height,in_src.width))
out_data = np.zeros((in_src.height,in_src.width))
for gac in gaul_countries:
    if gac>0:
        try:
            iso_code = country_codes[country_codes['GAUL']==str(int(gac))]['ISO_NUM'].values[0]
            out_data[in_data==gac]=iso_code
        except:
            print(gac)
        match_pixels = np.logical_or(match_pixels,in_data==gac)
        
print(np.unique(out_data))
kwds = in_src.profile
with rasterio.open(out_match_tif, 'w', **kwds) as dst_dataset:
    match_pixels = match_pixels.astype('Float32')
    dst_dataset.nodataval = 0
    dst_dataset.write_band(1,match_pixels)
    
with rasterio.open(out_tif, 'w', **kwds) as dst_dataset:
    out_data = out_data.astype('Float32')
    dst_dataset.nodataval = 0
    dst_dataset.write_band(1,out_data)
    
