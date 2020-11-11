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
import zipfile

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


GS_FOLDER = 'SPAM'
GS_BUCKET = 'gs://globagri-upload-bucket/'

PAUSE_FOR_OVERLOAD = True
NUM_ASSETS_AT_ONCE = 50

#filename_convention = 'spam2010v1r0_global_physical-area_{}_{}.tif'#'spam2010v1r0_global_{physical-area}_{yams}_{h}'

VARIABLES = ['sesa', 'trof', 'pota', 'rest', 'cass', 'rape', 'smil', 'pige', 'cott', 'temf', 'lent', 'bana', 'yams', 'ocer', 
            'ofib', 'cowp', 'swpo', 'maiz', 'cnut', 'rice', 'vege', 'pmil', 'plnt', 'orts', 'barl', 'acof', 'coco', 'chic', 'sugb', 
            'opul', 'whea', 'sunf', 'oilp', 'rcof', 'toba', 'ooil', 'sugc', 'soyb', 'teas', 'sorg', 'bean', 'grou']
#BANDS = ['a','h','i','l','r','s'] 
BANDS = ['a']
   
def combine_tiffs(NDV, varname, bands, DATA_DIR, filename_convention):
    '''
    Function to combine multiple geotiffs into one geotiff with multiple bands
    '''
    #get names of geotiffs to be combined
    var_fnames = ['']*len(bands)
    for i,name in enumerate(bands):
        var_fnames[i] = DATA_DIR+filename_convention.format(varname.upper(), name.upper())
        print(var_fnames[i])
    
    #command to merge geotiffs
    cmd = ['gdal_merge.py','-separate','-co','COMPRESS=LZW','-a_nodata',str(NDV),'-o',DATA_DIR+'{}.tif'.format(varname)] + var_fnames
    subprocess.call(cmd)
    
    return None

def upload_asset(varname,NDV,DATA_DIR,EE_COLLECTION,GS_BUCKET,VARIABLES):
    '''
    Function to upload geotiffs as images
    '''
    #Upload geotiff to staging bucket
    TEMP_FILE_NAME = '{}.tif'.format(varname)
    cmd = ['gsutil','-m','cp',DATA_DIR+TEMP_FILE_NAME,GS_BUCKET]
    print(cmd)
    subprocess.call(cmd)
    
    
    # #Get asset id
    # asset_id = EE_COLLECTION+'/'+varname
    #
    # #Get band names
    # bands = ','.join(BANDS)
    # print(bands)
    #
    # #Upload GeoTIFF from google storage bucket to earth engine
    # cmd = ['earthengine','upload','image','--asset_id='+asset_id,'--force','--nodata_value='+str(NDV),'--bands='+bands,GS_BUCKET+TEMP_FILE_NAME]
    #
    # shell_output = subprocess.check_output(cmd)
    # shell_output = shell_output.decode("utf-8")
    # print(shell_output)
    #
    # #Get task id
    # task_id = ''
    # if 'Started upload task with ID' in shell_output:
    #     task_id = shell_output.split(': ')[1]
    #     task_id = task_id.strip()
    # else:
    #     print('Something went wrong!')
    #     task_id='ERROR'
    # return task_id,NDV






SPAM_options = ['phys_area']
for option in SPAM_options:
    #Set file names with the option name filled in
    EE_COLLECTION = 'users/globagriwrr001/MapSpam2010_v1_1_{}'.format(option)
    DATA_DIR = '/Users/kristine/WRI/NationalGeographic/Phase2/Crop_Livestock/SPAM_HYDE/spam2010v1r1_global_{}.geotiff/'.format(option)
    
    if option == 'phys_area':
        filename_convention = 'spam2010V1r1_global_A_{}_{}.tif'
    else:
        filename_convention = 'spam2010V1r1_global_'+option[0].upper()+'_{}_{}.tif'
    
    #Initialize NDV variable, it is always set to -1
    NDV= -1
    #Create empty array for task id's
    #task_ids = ['']*len(VARIABLES)

    #For each year
    for i,varname in enumerate(VARIABLES):
        #Combine multiple geotiffs to one geotiff with multiple bands
        new_GS_BUCKET = '{}SPAM/{}/'.format(GS_BUCKET,option)
        combine_tiffs(NDV,varname,bands=BANDS, DATA_DIR=DATA_DIR, filename_convention=filename_convention)
        #Uplaod asset
        upload_asset(varname,NDV,DATA_DIR=DATA_DIR,EE_COLLECTION=EE_COLLECTION,GS_BUCKET=new_GS_BUCKET,VARIABLES=VARIABLES)
