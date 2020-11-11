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


EE_COLLECTION = 'users/globagriwrr001/LPJmL'
GS_FOLDER = 'LPJmL'
GS_BUCKET = 'gs://globagri-upload-bucket/{}/'.format(GS_FOLDER)

#DATA_DIR = '/Users/kristine/WRI/NationalGeographic/Phase2/SPAM_HYDE/spam2010v1r0_global_phys_area.geotiff/'
DATA_DIR = '/Users/kristine/WRI/NationalGeographic/Phase2/Crop_Livestock/LPJmL/lpjml_potential_yields/'

os.chdir(DATA_DIR)
PAUSE_FOR_OVERLOAD = True
NUM_ASSETS_AT_ONCE = 50

#VARIABLES = ['crop','grass']

#filename_convention = 'spam2010v1r0_global_physical-area_{}_{}.tif'#'spam2010v1r0_global_{physical-area}_{yams}_{h}'
ASC_FILENAME = 'harvest_{}_{}.asc'
TIF_FILENAME = 'harvest_{}_{}.tif'
VARIABLES = ['others']
#VARIABLES = ['rapeseed', 'sunflower', 'sugarcane', 'others', 'wheat', 'cassava', 'sugarbeet', 'groundnuts', 'millet', 'rice', 'soybeans', 'fpea', 'grasses', 'maize']
BANDS = ['rf','ir']

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

def convert_ascii_to_tif(in_file,out_file,band_name):
    '''
    Function to convert ascii files to geotiffs
    '''
    #Read in asc information, create geotiff driver, and copy over information
    drv = gdal.GetDriverByName('GTiff')
    ds_in = gdal.Open(in_file)
    ds_out = drv.CreateCopy(out_file, ds_in)
    
    #Get no data value
    NDV = ds_in.GetRasterBand(1).GetNoDataValue()
    
    #Get projection information and save to new file
    Projection = osr.SpatialReference()
    Projection.ImportFromEPSG(4326)
    ds_out.SetProjection(Projection.ExportToWkt())
    ds_out.GetRasterBand(1).SetDescription(band_name)
    
    #Close files
    ds_in = None
    ds_out = None
    
    return NDV

    
def combine_tiffs(NDV, varname, bands=BANDS, DATA_DIR=DATA_DIR):
    '''
    Function to combine multiple geotiffs into one geotiff with multiple bands
    '''
    #get names of geotiffs to be combined
    var_fnames = ['']*len(bands)
    for i,name in enumerate(bands):
        var_fnames[i] = DATA_DIR+TIF_FILENAME.format(varname, name)
    
    #command to merge geotiffs
    cmd = ['gdal_merge.py','-separate','-a_nodata',str(NDV),'-o',DATA_DIR+'{}.tif'.format(varname)] + var_fnames
    subprocess.call(cmd)
    
    # #remove files
    # for i,name in enumerate(varnames):
    #     os.remove(var_fnames[i])
    return None

def upload_asset(varname,NDV,DATA_DIR=DATA_DIR,EE_COLLECTION=EE_COLLECTION,GS_BUCKET=GS_BUCKET,VARIABLES=VARIABLES):
    '''
    Function to upload geotiffs as images
    '''
    #Upload geotiff to staging bucket
    TEMP_FILE_NAME = '{}_reprj.tif'.format(varname)
    cmd = ['gsutil','-m','cp',DATA_DIR+TEMP_FILE_NAME,GS_BUCKET]
    subprocess.call(cmd)




#Initialize NDV variable, it is always set to -9999.0 but I read it in from the ascii grid file later anyway
NDV= -9999

#For each year
for i,varname in enumerate(VARIABLES):
    #convert ascii to tif
    for band in BANDS:
        convert_ascii_to_tif(ASC_FILENAME.format(varname,band), TIF_FILENAME.format(varname,band),band)
    in_file = '{}.tif'.format(varname)
    out_file = '{}_reprj.tif'.format(varname)
    reference_file = '/Users/kristine/WRI/NationalGeographic/Phase2/Crop_Livestock/SPAM_HYDE/spam2010v1r1_global_phys_area.geotiff/spam2010V1r1_global_A_ACOF_A.tif'
    raster_clip(reference_file, in_file, out_file, srcnodata = NDV, dstnodata=NDV, resampling_method='average')
    #Combine multiple geotiffs to one geotiff with multiple bands
    combine_tiffs(NDV,varname)
    #Uplaod asset
    upload_asset(varname,NDV)

