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
import scipy as sp
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from textwrap import wrap
from rasterio.plot import show

in_shp = '/Users/kristine/WRI/NationalGeographic/Phase2/Results/globagri_national_totals/globagri_national_totals.shp'
data_dir = '/Users/kristine/WRI/NationalGeographic/Phase2/Results/All_Scenarios_Global_Results'
out_dir = '/Users/kristine/WRI/NationalGeographic/Phase2/Results/Vizualizations'
countries = gpd.read_file(in_shp)

scenarios = ['2050 Baseline Scenario','No Productivity Gains After 2010 Scenario', 'Coordinated Effort Scenario','Highly Ambitious Scenario']
scenario_names = ['BASE','ALTBASE','NOGAINS','COORD','AMB','BT']

for i,scenario in enumerate(scenarios):
    for product in ['Cropland','Grazing']:
        if product == 'Cropland':
            file_name = os.path.join(data_dir,'Cropland_Areas','{}_Cropland.tif'.format(scenario.replace(" ", "_")))
            missing = countries[countries['PA_2010'].isnull()]
            shapefile_column = 'PA_2010'
        elif product == 'Grazing':
            file_name = os.path.join(data_dir,'Grazing_Areas','{}_Grazing_Area.tif'.format(scenario.replace(" ", "_")))
            shapefile_column = 'GA_2010'
            missing = countries[countries['GA_2010'].isnull()]

        out_png_name = os.path.join(out_dir,"{}_{}.png".format(product,scenario.replace(" ", "_"))) 

        raster = rasterio.open(file_name)
        data = raster.read(1)
        vmax = np.amax(data)
        
        fig, ax1 = plt.subplots(1, 1, figsize=(8, 8))
        legend_kwds={'label': "2050 {} (ha)".format(product), 'orientation': "horizontal",'pad':0.05}
        
        norm = colors.Normalize(vmin=0, vmax=vmax)
        cbar = plt.cm.ScalarMappable(cmap='viridis',norm=norm)
        show(raster,cmap='viridis',norm=norm, ax=ax1,zorder=0)
        missing.plot(ax=ax1,facecolor='lightgrey',zorder=5)
        countries.plot(ax=ax1,facecolor="none",edgecolor='black', lw=0.2,zorder=10)
        fig.colorbar(cbar, ax=ax1,**legend_kwds)
        
        title = ax1.set_title("\n".join(wrap('{} Areas under {}'.format(product,scenario))), fontsize=15)

        plt.savefig(out_png_name,dpi=1000)
        plt.clf()
        