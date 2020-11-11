import os
import pandas as pd
import numpy as np
import rasterio
import glob
import subprocess
import numpy as np
import rasterio

base_dir = '/home/globagriwrr001/globagriexpansion'
local_dir = '/home/globagriwrr001/local'
GS_BUCKET = 'gs://globagri-upload-bucket/'

countries_directory = os.path.join(base_dir,'Country_Polygons')

countries = ['AFG', 'AGO', 'ALB', 'ARE', 'ARG', 'ASM', 'ATG', 'AUS', 'AUT',
       'BAL', 'BDI', 'BEN', 'BFA', 'BGD', 'BGR', 'BHR', 'BHS', 'BLZ',
       'BMU', 'BOL', 'BRA', 'BRB', 'BRN', 'BTN', 'BWA', 'CAF', 'CAN',
       'CHE', 'CHL', 'CHN', 'CIV', 'CMR', 'COD', 'COG', 'COK', 'COL',
       'COM', 'CPV', 'CRI', 'CUB', 'CYM', 'CYP', 'CZE', 'DEU', 'DJI',
       'DMA', 'DNK', 'DOM', 'DZA', 'ECU', 'EGY', 'ERI', 'ESH', 'ESP',
       'ETH', 'FIN', 'FJI', 'FRA', 'FRO', 'FSM', 'GAB', 'GBR', 'GHA',
       'GIN', 'GLP', 'GMB', 'GNB', 'GNQ', 'GRC', 'GRD', 'GTM', 'GUF',
       'GUM', 'GUY', 'HND', 'HTI', 'HUN', 'IDN', 'IND', 'IRL', 'IRN',
       'IRQ', 'ISL', 'ISR', 'ITA', 'JAM', 'JOR', 'JPN', 'KEN', 'KHM',
       'KIR', 'KNA', 'KOR', 'KWT', 'LAO', 'LBN', 'LBR', 'LBY', 'LCA',
       'LKA', 'LSO', 'MAR', 'MDG', 'MDV', 'MEX', 'MHL', 'MLI', 'MLT',
       'MMR', 'MNG', 'MOZ', 'MRT', 'MSR', 'MTQ', 'MUS', 'MWI', 'MYS',
       'NAM', 'NCL', 'NER', 'NGA', 'NIC', 'NIU', 'NLD', 'NOR', 'NPL',
       'NRU', 'NZL', 'OMN', 'PAK', 'PAN', 'PER', 'PHL', 'PNG', 'POL',
       'PRI', 'PRK', 'PRT', 'PRY', 'PSE', 'PYF', 'QAT', 'REU', 'ROU',
       'RWA', 'SAU', 'SDN', 'SEN', 'SGP', 'SLB', 'SLE', 'SLV', 'SOM',
       'SPM', 'STP', 'SUN', 'SUR', 'SVK', 'SWE', 'SWZ', 'SYC', 'SYR',
       'TCD', 'TGO', 'THA', 'TKL', 'TLS', 'TON', 'TTO', 'TUN', 'TUR',
       'TUV', 'TZA', 'UGA', 'URY', 'USA', 'VCT', 'VEN', 'VGB', 'VNM',
       'VUT', 'WLF', 'WSM', 'YEM', 'YUG', 'ZAF', 'ZMB', 'ZWE']

#ISO clipping
input_raster = os.path.join(base_dir,'OtherFiles','GlobAgri_GAUL_ISO.tif')
out_cloud_directory = os.path.join(GS_BUCKET,'OtherFiles','country_bound_rasters')
out_name = 'iso_bounds_{}.tif'
for country in countries:
    shapefile = os.path.join(countries_directory,'{}_polygon.shp'.format(country))
    output_raster = os.path.join(local_dir,out_name.format(country))
    cmd = ['gdalwarp','-cutline',shapefile,'-crop_to_cutline','-overwrite',input_raster,output_raster]
    print(cmd)
    subprocess.call(cmd)
    cmd = ['sudo','gsutil','-m','cp',output_raster,out_cloud_directory]
    print(cmd)
    subprocess.call(cmd)
    
#Pixel area clipping
input_raster = os.path.join(base_dir,'OtherFiles','HydeLandPixelArea_ha.tif')
out_cloud_directory = os.path.join(GS_BUCKET,'OtherFiles','LandPixelArea_by_Country')
out_name = 'LandPixelArea_ha_{}.tif'
for country in countries:
    shapefile = os.path.join(countries_directory,'{}_polygon.shp'.format(country))
    output_raster = os.path.join(local_dir,out_name.format(country))
    cmd = ['gdalwarp','-cutline',shapefile,'-crop_to_cutline','-overwrite',input_raster,output_raster]
    print(cmd)
    subprocess.call(cmd)
    cmd = ['sudo','gsutil','-m','cp',output_raster,out_cloud_directory]
    print(cmd)
    subprocess.call(cmd)
    
#Built up clipping
input_raster = os.path.join(base_dir,'OtherFiles','BuiltUp_Area_ha.tif')
out_cloud_directory = os.path.join(GS_BUCKET,'OtherFiles','BuiltUp_Area_by_Country')
out_name = 'builtup_area_ha_{}.tif'
for country in countries:
    shapefile = os.path.join(countries_directory,'{}_polygon.shp'.format(country))
    output_raster = os.path.join(local_dir,out_name.format(country))
    cmd = ['gdalwarp','-cutline',shapefile,'-crop_to_cutline','-overwrite',input_raster,output_raster]
    print(cmd)
    subprocess.call(cmd)
    cmd = ['sudo','gsutil','-m','cp',output_raster,out_cloud_directory]
    print(cmd)
    subprocess.call(cmd)
    
#GLPS clipping
input_raster = os.path.join(base_dir,'OtherFiles','glps_reprj.tif')
out_cloud_directory = os.path.join(GS_BUCKET,'OtherFiles','GLPS_by_Country')
out_name = 'GLPS_{}.tif'
for country in countries:
    shapefile = os.path.join(countries_directory,'{}_polygon.shp'.format(country))
    output_raster = os.path.join(local_dir,out_name.format(country))
    cmd = ['gdalwarp','-cutline',shapefile,'-crop_to_cutline','-overwrite',input_raster,output_raster]
    print(cmd)
    subprocess.call(cmd)
    cmd = ['sudo','gsutil','-m','cp',output_raster,out_cloud_directory]
    print(cmd)
    subprocess.call(cmd)
    
#NELSON travel time clipping
input_raster = os.path.join(base_dir,'OtherFiles','NelsonTravelTimeMinutes_reprj.tif')
out_cloud_directory = os.path.join(GS_BUCKET,'OtherFiles','NelsonTravelTime_by_Country')
out_name = 'NelsonTravelTimeMinutes_{}.tif'
for country in countries:
    shapefile = os.path.join(countries_directory,'{}_polygon.shp'.format(country))
    output_raster = os.path.join(local_dir,out_name.format(country))
    cmd = ['gdalwarp','-cutline',shapefile,'-crop_to_cutline','-overwrite',input_raster,output_raster]
    print(cmd)
    subprocess.call(cmd)
    cmd = ['sudo','gsutil','-m','cp',output_raster,out_cloud_directory]
    print(cmd)
    subprocess.call(cmd)
    
#HYDE clipping
for country in countries:
    input_raster = os.path.join(base_dir,'HYDE','grazing_2010AD_reprj_ha.tif')
    out_cloud_directory = os.path.join(GS_BUCKET,'HYDE','HYDE_by_Country')
    out_name = 'grazing_2010AD_{}.tif'
    shapefile = os.path.join(countries_directory,'{}_polygon.shp'.format(country))
    output_raster = os.path.join(local_dir,out_name.format(country))
    cmd = ['gdalwarp','-cutline',shapefile,'-crop_to_cutline','-overwrite',input_raster,output_raster]
    print(cmd)
    subprocess.call(cmd)
    cmd = ['sudo','gsutil','-m','cp',output_raster,out_cloud_directory]
    print(cmd)
    subprocess.call(cmd)
countries_done = []
countries = [x for x in countries if x not in countries_done]

#LPJmL clipping
lpj_folder = os.path.join(base_dir,'LPJmL_averaged')
rasters = glob.glob(os.path.join(lpj_folder,'*.tif'))
for country in countries:
    for raster in rasters:
        input_raster = raster
        out_cloud_directory = os.path.join(GS_BUCKET,'LPJmL_averaged','LPJmL_by_Country')
        crop = os.path.basename(raster).split('_reprj')[0]
        out_name = crop+'_{}.tif'
        shapefile = os.path.join(countries_directory,'{}_polygon.shp'.format(country))
        output_raster = os.path.join(local_dir,out_name.format(country))
        cmd = ['gdalwarp','-cutline',shapefile,'-crop_to_cutline','-overwrite',input_raster,output_raster]
        print(cmd)
        subprocess.call(cmd)
        cmd = ['sudo','gsutil','-m','cp',output_raster,out_cloud_directory]
        print(cmd)
        subprocess.call(cmd)

#SPAM Clipping
spam_folder = os.path.join(base_dir,'SPAM','phys_area')
rasters = glob.glob(os.path.join(spam_folder,'*.tif'))
for raster in rasters:
    input_raster = raster
    out_cloud_directory = os.path.join(GS_BUCKET,'SPAM','phys_area_by_country')
    crop = os.path.basename(raster).split('.')[0]
    out_name = crop+'_{}.tif'
    for country in countries:
        shapefile = os.path.join(countries_directory,'{}_polygon.shp'.format(country))
        output_raster = os.path.join(local_dir,out_name.format(country))
        cmd = ['gdalwarp','-cutline',shapefile,'-crop_to_cutline','-overwrite',input_raster,output_raster]
        print(cmd)
        subprocess.call(cmd)
        cmd = ['sudo','gsutil','-m','cp',output_raster,out_cloud_directory]
        print(cmd)
        subprocess.call(cmd)
