import os
import pandas as pd
import numpy as np
import rasterio
import glob
import subprocess

base_dir = '/home/globagriwrr001/globagriexpansion'
output_dir = '/home/globagriwrr001/local'
GS_BUCKET = 'gs://globagri-upload-bucket/'
os.chdir(base_dir)


LPJmL_folder = os.path.join(base_dir,'LPJmL')
SPAM_GADM_bounds_f = os.path.join(base_dir,'OtherFiles','GADM_SPAM_Bounds.tif')
SPAM_GADM_bounds_src = rasterio.open(SPAM_GADM_bounds_f)

LPJmL_files = glob.glob(os.path.join(LPJmL_folder,'*.tif'))
print(LPJmL_files)


for lpj_file in LPJmL_files:
    average_LPJmL = np.zeros((SPAM_GADM_bounds_src.height,SPAM_GADM_bounds_src.width))
    out_lpj_file = os.path.join(output_dir,os.path.basename(lpj_file))
    
    with rasterio.open(lpj_file) as src:
        band1 = src.read(1)
        band2 = src.read(2)
        
        average_LPJmL = np.divide(np.add(band1,band2),2.0)
        
        kwds = src.profile
        kwds.update(count=1,compress='lzw')
        
        with rasterio.open(out_lpj_file, 'w', **kwds) as dst_dataset:
            average_LPJmL = average_LPJmL.astype('float32')
            dst_dataset.write(average_LPJmL, 1)
            
        cmd = ['sudo','gsutil','-m','cp',out_lpj_file,GS_BUCKET+'LPJmL_averaged/']
        subprocess.call(cmd)
        
        

