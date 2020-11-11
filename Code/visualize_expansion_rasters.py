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
data_dir = '/Users/kristine/WRI/NationalGeographic/Phase2/Results'
out_dir = '/Users/kristine/WRI/NationalGeographic/Phase2/Results/Vizualizations'
countries = gpd.read_file(in_shp)

scenarios = ['2050 Baseline Scenario','No Productivity Gains After 2010 Scenario', 'Coordinated Effort Scenario','Highly Ambitious Scenario']
scenario_names = ['BASE','ALTBASE','NOGAINS','COORD','AMB','BT']

for i,scenario in enumerate(scenarios):
    for product in ['cropland','grazing']:
        if product == 'cropland':
            file_name = os.path.join(data_dir,'Cropland_Changes','{}_Cropland_Change.tif'.format(scenario.replace(" ", "_")))
            missing = countries[countries['PA_2010'].isnull()]
            shapefile_column = 'PA_2010'
        elif product == 'grazing':
            file_name = os.path.join(data_dir,'Grazing_Changes','{}_Grazing_Area_Change.tif'.format(scenario.replace(" ", "_")))
            shapefile_column = 'GA_2010'
            missing = countries[countries['GA_2010'].isnull()]

        out_png_name = os.path.join(out_dir,"{}_Raster_Change_{}.png".format(product,scenario.replace(" ", "_"))) 

        raster = rasterio.open(file_name)
        data = raster.read(1)
        vmax = np.amax(data)
        vmin = np.amin(data)
        
        fig, ax1 = plt.subplots(1, 1, figsize=(8, 8))
        legend_kwds={'label': "Change in {} (ha)".format(product), 'orientation': "horizontal",'pad':0.05}
        
        if (vmax>0) and (vmin<0):
            vcenter = 0
            divnorm = colors.DivergingNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
            cbar = plt.cm.ScalarMappable(norm=divnorm, cmap='seismic')
            show(raster,cmap='seismic', norm=divnorm, ax=ax1,zorder=0)
            missing.plot(ax=ax1,facecolor='lightgrey',zorder=5)
            countries.plot(ax=ax1,facecolor="none",edgecolor='black', lw=0.2,zorder=10)
            fig.colorbar(cbar, ax=ax1,**legend_kwds)
        elif (vmax<0) and (vmin<0):
            cbar = plt.cm.ScalarMappable(cmap='Blues_r')
            show(raster,cmap='Blues_r', ax=ax1,zorder=0)
            missing.plot(ax=ax1,facecolor='lightgrey',zorder=5)
            countries.plot(ax=ax1,facecolor="none",edgecolor='black', lw=0.2,zorder=10)
            fig.colorbar(cbar, ax=ax1,**legend_kwds)
        elif (vmax>0) and (vmin>0):
            cbar = plt.cm.ScalarMappable(cmap='Reds')
            show(raster,cmap='Reds', ax=ax1,zorder=0)
            missing.plot(ax=ax1,facecolor='lightgrey',zorder=5)
            countries.plot(ax=ax1,facecolor="none",edgecolor='black', lw=0.2,zorder=10)
            fig.colorbar(cbar, ax=ax1,**legend_kwds)
        
        title = ax1.set_title("\n".join(wrap('2010 - 2050 Change in {} under {}'.format(product,scenario))), fontsize=15)
        plt.tight_layout()

        plt.savefig(out_png_name,dpi=1000)
        plt.clf()
        