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


in_shp = '/Users/kristine/WRI/NationalGeographic/Phase2/Results/globagri_national_totals/globagri_national_totals.shp'
data_dir = '/Users/kristine/WRI/NationalGeographic/Phase2/Results/Vizualizations'
gdf = gpd.read_file(in_shp)
print(list(gdf))

scenarios = ['2050 Baseline Scenario','No Productivity Gains After 2010 Scenario', 'Coordinated Effort Scenario','Highly Ambitious Scenario']

scenario_names = ['BASE','NOGAINS','COORD','AMB']

for i,scenario in enumerate(scenarios):
    for product in ['PA','GA']:
        if product == 'PA':
            title_name = 'Cropland'
        elif product == 'GA':
            title_name = 'Grazing Area'
        out_png_name = os.path.join(data_dir,"{}_Country_Change_{}.png".format(title_name.replace(" ", "_"),scenario.replace(" ", "_")))    
        print(out_png_name)
        column_name = 'D_{}_{}'.format(product,scenario_names[i])
        column = column_name[:10]

        new_col = column+'_scaled'
        gdf[new_col] = gdf[column]/(1.0e6)
        
        fig, ax1 = plt.subplots(1, 1, figsize=(8, 8))
        legend_kwds={'label': "Change in {} (Mha)".format(title_name), 'orientation': "horizontal",'pad':0.05}
        
        vmax = gdf[new_col].max()
        vmin = gdf[new_col].min()
        if (vmax>0) and (vmin<0):
            vcenter = 0
            divnorm = colors.DivergingNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
            cbar = plt.cm.ScalarMappable(norm=divnorm, cmap='seismic')
            gdf.plot(column=new_col, cmap='seismic',edgecolor='black', lw=0.2, legend=False, norm=divnorm, ax=ax1,missing_kwds={'color': 'lightgrey'})
            fig.colorbar(cbar, ax=ax1,**legend_kwds)
        elif (vmax<0) and (vmin<0):
            cbar = plt.cm.ScalarMappable(cmap='Blues_r')
            gdf.plot(column=new_col, cmap='Blues_r',edgecolor='black', lw=0.2, legend=False, ax=ax1, missing_kwds={'color': 'lightgrey'})
            fig.colorbar(cbar, ax=ax1,**legend_kwds)
        elif (vmax>0) and (vmin>0):
            cbar = plt.cm.ScalarMappable(cmap='Reds')
            gdf.plot(column=new_col, cmap='Reds',edgecolor='black', lw=0.2, legend=False, ax=ax1,missing_kwds={'color': 'lightgrey'})
            fig.colorbar(cbar, ax=ax1,**legend_kwds)
        title = ax1.set_title("\n".join(wrap('2010 - 2050 Change in {} under {}'.format(title_name,scenario))), fontsize=15)
        plt.tight_layout()

        plt.savefig(out_png_name,dpi=1000)
        plt.clf()
        