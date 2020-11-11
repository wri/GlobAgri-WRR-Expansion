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
import geopandas as gpd

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

iso_codes_df = pd.read_csv('/Users/kristine/WRI/NationalGeographic/Phase2/Country_Bounds/full_country_codes.csv')

harvest_areas_df = pd.read_csv('/Users/kristine/WRI/NationalGeographic/Phase2/Crop_Livestock/harv_area_country_all_scenarios.csv')
cropping_intensity_df = pd.read_csv('/Users/kristine/WRI/NationalGeographic/Phase2/Crop_Livestock/cropping_intensity_country_all_scenarios.csv')
livestock_areas_df = pd.read_csv('/Users/kristine/WRI/NationalGeographic/Phase2/Crop_Livestock/livestock_area_country_all_scenarios.csv')

scenarios = ['2010','2050 Baseline Scenario','Alternative Baseline Scenario','No Productivity Gains After 2010 Scenario',
            'Coordinated Effort Scenario','Highly Ambitious Scenario','Breakthrough Technologies Scenario']
scenario_names = ['2010','Baseline','AltBase','NoGains','Coordinated','Ambitious','Breakthrough']

in_shp = '/Users/kristine/WRI/NationalGeographic/Phase2/Country_Bounds/g2008_0/g2008_0_iso.shp'
out_shp = '/Users/kristine/WRI/NationalGeographic/Phase2/Country_Bounds/g2008_0/g2008_globagri_merged.shp'

in_gdf = gpd.read_file(in_shp)

globagri_regions = ['CHN','SUN', 'BAL','YUG'];
SUN_iso_list = ['SUN','ARM', 'AZE', 'BLR', 'GEO', 'KAZ', 'KGZ', 'MDA', 'RUS', 'TJK', 'TKM', 'UKR', 'UZB', 'EST', 'LVA', 'LTU','LTU','EST','LVA']
BAL_iso_list = ['BEL', 'LUX'];
CHN_iso_list = ['CHN', 'TWN', 'HKG']
YUG_iso_list = ['BIH','HRV','MKD','MNE','SRB','SVN']

out_gdf = in_gdf[~in_gdf['ISO3'].isin(SUN_iso_list+BAL_iso_list+CHN_iso_list+YUG_iso_list)].copy().dissolve(by='ISO3', aggfunc='first', as_index=False)

CHN_rows = in_gdf[in_gdf['ISO3'].isin(CHN_iso_list)].copy()
CHN_rows['ISO3'] ='CHN'
CHN_rows = CHN_rows.dissolve(by='ISO3', aggfunc='first', as_index=False)

YUG_rows = in_gdf[in_gdf['ISO3'].isin(YUG_iso_list)].copy()
YUG_rows['ISO3'] ='YUG'
YUG_rows = YUG_rows.dissolve(by='ISO3', aggfunc='first', as_index=False)

BAL_rows = in_gdf[in_gdf['ISO3'].isin(BAL_iso_list)].copy()
BAL_rows['ISO3'] ='BAL'
BAL_rows = BAL_rows.dissolve(by='ISO3', aggfunc='first', as_index=False)

SUN_rows = in_gdf[in_gdf['ISO3'].isin(SUN_iso_list)].copy()
SUN_rows['ISO3'] ='SUN'
SUN_rows = SUN_rows.dissolve(by='ISO3', aggfunc='first', as_index=False)

out_gdf = out_gdf.append(CHN_rows[list(in_gdf)],ignore_index=True)
out_gdf = out_gdf.append(SUN_rows[list(in_gdf)],ignore_index=True)
out_gdf = out_gdf.append(YUG_rows[list(in_gdf)],ignore_index=True)
out_gdf = out_gdf.append(BAL_rows[list(in_gdf)],ignore_index=True)
out_gdf.to_file(out_shp)