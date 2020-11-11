import sys
import os
from osgeo import gdal, gdalconst, osr, gdal_array
from collections import OrderedDict
import numpy as np
import netCDF4 as nc
import rasterio
#from matplotlib import pyplot as plt
import datetime
import logging
import subprocess
import urllib.request
import zipfile
import learn2map.raster_tools as rt
#The purpose of this code is to upload data from HYDE 3.2 land use to google earth engine
#Ascii grids are downloaded, converted to geotiffs, and uploaded to google earth engine
#Currently the code is set to upload the BC section of years


#Before running script make sure to authenticate google cloud service and earth engine
#Commands:
#> gsutil auth login
#> earthengine authenticate

#Before uploading assets, make sure to create folder and set to public
#Commands:
#> earthengine create folder (folder name)
#> earthengine acl set public (folder name)
#> earthengine create collection (collection name)
#> earthengine acl set public (collection name)


GS_FOLDER = 'OtherFiles'
GS_BUCKET = 'gs://globagri-upload-bucket/{}/'.format(GS_FOLDER)


def raster_clip(mask_file, in_file, out_file, resampling_method='average', out_format='Float32',
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
    res0 = ' '.join(map(str, res0))
    size0 = '{} {}'.format(str(in0.RasterXSize), str(in0.RasterYSize))


    if (out_format=='Float32') or (out_format=='Float64'):
        predictor_num = 3
    else:
        predictor_num = 2

    gdal_expression = (
        'gdalwarp -t_srs {} -te {} -ts {} '
        '-srcnodata {} -dstnodata {} -multi -overwrite -co NUM_THREADS=ALL_CPUS '
        '-co COMPRESS=LZW -co BIGTIFF=YES '
        '-r {} -ot {} "{}" "{}"').format(
        prj0, extent0, size0, srcnodata, dstnodata,
        resampling_method, out_format, in_file, out_file)
    print(gdal_expression)
    subprocess.check_output(gdal_expression, shell=True)

    in0 = None
    in1 = None

    return


def upload_asset(in_file,NDV,GS_BUCKET=GS_BUCKET):
    '''
    Function to upload geotiffs as images
    '''
    #Upload geotiff to staging bucket
    cmd = ['gsutil','-m','cp',in_file,GS_BUCKET]
    subprocess.call(cmd)




#Initialize NDV variable, it is always set to -9999.0 but I read it in from the ascii grid file later anyway
NDV= 0

directory = '/Users/kristine/WRI/NationalGeographic/Phase2/Crop_Livestock/SPAM_HYDE/2_GlobalRuminantLPS_GIS'
os.chdir(directory)
in_file = 'glps_gleam_61113_10km.tif'
out_file = 'glps_reprj.tif'
reference_file = '/Users/kristine/WRI/NationalGeographic/Phase2/Crop_Livestock/SPAM_HYDE/spam2010v1r1_global_phys_area.geotiff/spam2010V1r1_global_A_ACOF_A.tif'
raster_clip(reference_file, in_file, out_file, out_format='Byte',srcnodata = NDV, dstnodata=NDV, resampling_method='average')

upload_asset(out_file,NDV)

