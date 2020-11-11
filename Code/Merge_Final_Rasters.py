#!/usr/bin/env python3
import os
import pandas as pd
import numpy as np
import rasterio
import glob
import subprocess
import sys
import multiprocessing as mp
from google.cloud import storage
import datetime
import shutil

output_dir = '/home/globagriwrr001/local'
GS_BUCKET = 'gs://globagri-upload-bucket'
bucket_name = 'globagri-upload-bucket'
base_dir = '/home/globagriwrr001/globagriexpansion'
results_directory = os.path.join(base_dir,)

def merge_cropland_rasters(scenario, countries):
    total_phys_file = os.path.join(base_dir,'Ag_Expansion_Results',scenario.replace(" ", "_"),'{}/{}_{}_all_crops_new_physical_area.tif')
    file_paths = [total_phys_file.format(x,x,2050) for x in countries]
    out_list_file_path = os.path.join(output_dir,'cropland_list_for_vrt.txt')
    with open(out_list_file_path, 'w') as f:
        for item in file_paths:
            f.write("%s\n" % item)
    out_vrt_file_path = os.path.join(output_dir,'{}_global_2050_total_crop_areas.vrt'.format(scenario.replace(" ", "_")))
    out_tif_file_path = os.path.join(output_dir,'{}_global_2050_total_crop_areas.tif'.format(scenario.replace(" ", "_")))
    cmd = ('gdalbuildvrt -input_file_list {} {}'.format(out_list_file_path,out_vrt_file_path))
    
    print(cmd)
    subprocess.check_output(cmd,shell=True)
    cmd = ('gdal_translate -of GTiff -co "COMPRESS=LZW" {} {}'.format(out_vrt_file_path,out_tif_file_path))
    
    print(cmd)
    subprocess.check_output(cmd,shell=True)
    out_folder = os.path.join(GS_BUCKET,'Ag_Expansion_Results','All_Scenarios_Global_Results','')
    cmd = ('gsutil -m cp {} {}'.format(out_tif_file_path,out_folder))
    print(cmd)
    subprocess.check_output(cmd,shell=True)
    
def merge_livestock_rasters(scenario, countries):
    total_phys_file = os.path.join(base_dir,'Ag_Expansion_Results',scenario.replace(" ", "_"),'{}/{}_{}_new_grazing_area.tif')
    file_paths = [total_phys_file.format(x,x,2050) for x in countries]
    out_list_file_path = os.path.join(output_dir,'grazing_list_for_vrt.txt')
    with open(out_list_file_path, 'w') as f:
        for item in file_paths:
            f.write("%s\n" % item)
    out_vrt_file_path = os.path.join(output_dir,'{}_global_2050_grazing_areas.vrt'.format(scenario.replace(" ", "_")))
    out_tif_file_path = os.path.join(output_dir,'{}_global_2050_grazing_areas.tif'.format(scenario.replace(" ", "_")))
    cmd = ('gdalbuildvrt -input_file_list {} {}'.format(out_list_file_path,out_vrt_file_path))
    print(cmd)
    subprocess.check_output(cmd,shell=True)
    cmd = ('gdal_translate -of GTiff -co "COMPRESS=LZW" {} {}'.format(out_vrt_file_path,out_tif_file_path))
    print(cmd)
    subprocess.check_output(cmd,shell=True)
    out_folder = os.path.join(GS_BUCKET,'Ag_Expansion_Results','All_Scenarios_Global_Results','')
    cmd = ('gsutil -m cp {} {}'.format(out_tif_file_path,out_folder))
    print(cmd)
    subprocess.check_output(cmd,shell=True)
    
    
    

scenarios = ['2050 Baseline Scenario','No Productivity Gains After 2010 Scenario',
            'Coordinated Effort Scenario','Highly Ambitious Scenario']
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
       
for scenario in scenarios:
    merge_cropland_rasters(scenario,countries)
    merge_livestock_rasters(scenario,countries)
