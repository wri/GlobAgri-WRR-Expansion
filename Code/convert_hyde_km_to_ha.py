import os
import pandas as pd
import numpy as np
import rasterio
import glob
import subprocess
import numpy as np
import rasterio
from osgeo import gdal
from learn2map import raster_tools as rt

data_dir = '/Users/kristine/WRI/NationalGeographic/Phase2/Crop_Livestock/SPAM_HYDE/2010AD_lu'
os.chdir(data_dir)

in_file = 'grazing_2010AD_reprj_km.tif'
out_file = 'grazing_2010AD_reprj_ha.tif'

cmd = ('gdal_calc.py -A {} --outfile={} --calc="A*100" --NoDataValue=-9999').format(in_file,out_file)
print(cmd)
subprocess.check_output(cmd,shell=True)



