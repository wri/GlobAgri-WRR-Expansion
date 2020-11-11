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

scenarios = ['2050 Baseline Scenario','Alternative Baseline Scenario','No Productivity Gains After 2010 Scenario',
            'Coordinated Effort Scenario','Highly Ambitious Scenario','Breakthrough Technologies Scenario']
scenario_names = ['BASE','ALTBASE','NOGAINS','COORD','AMB','BT']

in_shp = '/Users/kristine/WRI/NationalGeographic/Phase2/Country_Bounds/g2008_0/g2008_globagri_merged.shp'
out_shp = '/Users/kristine/WRI/NationalGeographic/Phase2/Country_Bounds/g2008_0/g2008_globagri_merged_areas.shp'


out_gdf = gpd.read_file(in_shp)
for i,row in out_gdf.iterrows():
    print(row['ISO3'])
    
    if row['ISO3'] in countries:
        cropping_intensity = cropping_intensity_df[cropping_intensity_df['ISO3']==row['ISO3']]['2010'].values[0]
        match_harvest_rows = harvest_areas_df[harvest_areas_df['ISO3']==row['ISO3']]['2010']
        harvest_row = match_harvest_rows.sum(axis=0)
        physical_area_2010 = harvest_row/cropping_intensity
        out_gdf.at[i,'PA_2010'] = physical_area_2010
        try:
            livestock_areas_2010 = livestock_areas_df[livestock_areas_df['ISO3']==row['ISO3']]['2010'].values[0]
        except:
            livestock_areas_2010 = None
        out_gdf.at[i,'GA_2010'] = livestock_areas_2010
    
        for k,scenario in enumerate(scenarios):
            scenario_name = scenario_names[k]
            cropping_intensity = cropping_intensity_df[cropping_intensity_df['ISO3']==row['ISO3']][scenario].values[0]
            match_harvest_rows = harvest_areas_df[harvest_areas_df['ISO3']==row['ISO3']][scenario]
            harvest_row = match_harvest_rows.sum(axis=0)
            physical_area = harvest_row/cropping_intensity
            out_gdf.at[i,'PA_{}'.format(scenario_name)] = physical_area
            try:
                livestock_areas = livestock_areas_df[livestock_areas_df['ISO3']==row['ISO3']][scenario].values[0]
            except:
                livestock_areas = None
            out_gdf.at[i,'GA_{}'.format(scenario_name)] = livestock_areas
            
            out_gdf.at[i,'D_PA_{}'.format(scenario_name)] = physical_area - physical_area_2010
            try:
                out_gdf.at[i,'D_GA_{}'.format(scenario_name)] = livestock_areas - livestock_areas_2010 
            except:
                out_gdf.at[i,'D_GA_{}'.format(scenario_name)] = None
    else:
        out_gdf.at[i,'PA_2010'] = None
        out_gdf.at[i,'GA_2010'] = None
        for k,scenario in enumerate(scenarios):
            scenario_name = scenario_names[k]
            out_gdf.at[i,'PA_{}'.format(scenario_name)] = None
            out_gdf.at[i,'GA_{}'.format(scenario_name)] = None
            out_gdf.at[i,'D_PA_{}'.format(scenario_name)] = None
            out_gdf.at[i,'D_GA_{}'.format(scenario_name)] = None
            
out_gdf.to_file(out_shp)


