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

def raster_clip_reprj(mask_file, in_file, out_file, resampling_method='near', out_format='Float32',
                srcnodata='nan', dstnodata='nan', max_memory='2000'):
    """
    for every input in_file, get the same spatial resolution, projection, and
    extent as the input mask_file.

    output is a new raster file: out_file.
    """
    in0 = gdal.Open(mask_file)
    prj0 = in0.GetProjection()
    extent0, res0 = rt.get_raster_extent(in0)
    extent0 = ' '.join(map(str, extent0))
    #res0 = ' '.join(map(str, res0))
    res0 = '10000.0 10000.0'
    
    gdal_expression = (
        'gdalwarp -t_srs {} -tr {} '
        '-srcnodata {} -dstnodata {} -multi -overwrite '
        '-co COMPRESS=LZW -co BIGTIFF=YES '
        '-r {} -ot {} "{}" "{}"').format(
        prj0, res0, srcnodata, dstnodata,
        resampling_method, out_format, in_file, out_file)
    print(gdal_expression)
    subprocess.check_output(gdal_expression, shell=True)
    in0 = None
    in1 = None
    return
    

data_directory = '/Users/kristine/WRI/NationalGeographic/Phase2/Exclusion_Areas/GHS_BUILT_LDS2014_GLOBE_R2018A_54009_1K_V2_0'
os.chdir(data_directory)

one_km_percent_f = 'GHS_BUILT_LDS2014_GLOBE_R2018A_54009_1K_V2_0.tif'
ten_km_percent_f = 'BuiltUp_Percent_10km.tif'
pixel_area_f = 'LandPixelArea_ha.tif'
ten_km_area_f = 'BuiltUp_Area_ha.tif'


spam_ref = '/Users/kristine/WRI/NationalGeographic/Phase2/Crop_Livestock/SPAM_HYDE/spam2010v1r1_global_harv_area.geotiff/spam2010V1r1_global_H_ACOF_A.tif'

rt.raster_clip(spam_ref, one_km_percent_f, ten_km_percent_f,resampling_method='average',srcnodata=-200,dstnodata=np.nan)
cmd = ('gdal_calc.py -A {} -B {} --outfile={} --calc="B*A*0.01" --NoDataValue=nan').format(ten_km_percent_f,pixel_area_f,ten_km_area_f)
print(cmd)
subprocess.check_output(cmd,shell=True)



