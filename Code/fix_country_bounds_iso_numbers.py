import os
import pandas as pd
import numpy as np
import rasterio
import glob
import subprocess
from pycountry import countries


def convert_iso_num(data,iso_code_convert_list, iso_table,out_code):
    print(iso_code_convert_list)
    try:
        iso_num_convert_list = [iso_table[iso_table['ISO3']==x]['ISO_NUM'].values[0] for x in iso_code_convert_list]
    except:
        for x in iso_code_convert_list:
            print(x)
            print(iso_table[iso_table['ISO3']==x]['ISO_NUM'].values[0])
    data[np.isin(data,iso_num_convert_list)] = out_code
    return data

    
globagri_regions = ['CHN','SUN', 'BAL','YUG'];
SUN_iso_list = ['ARM', 'AZE', 'BLR', 'GEO', 'KAZ', 'KGZ', 'MDA', 'RUS', 'TJK', 'TKM', 'UKR', 'UZB', 'EST', 'LVA', 'LTU','LTU','EST','LVA']
BAL_iso_list = ['BEL', 'LUX'];
CHN_iso_list = ['CHN', 'TWN', 'HKG']
YUG_iso_list = ['BIH','HRV','MKD','MNE','SRB','SVN']

output_dir = '/Users/kristine/WRI/NationalGeographic/Phase2/Country_Bounds'
country_bounds_f = '/Users/kristine/WRI/NationalGeographic/Phase2/Country_Bounds/g2008_0/g2008_0_iso.tif'
iso_codes_df = pd.read_csv('/Users/kristine/WRI/NationalGeographic/Phase2/Country_Bounds/full_country_codes.csv')

country_bounds_src = rasterio.open(country_bounds_f)
country_bounds_nodata = country_bounds_src.nodatavals[0]
data = country_bounds_src.read(1)

for region in globagri_regions:
    if region == 'CHN':
        iso_list = CHN_iso_list
        out_code = 156
    elif region == 'SUN':
        iso_list = SUN_iso_list
        out_code = 643
    elif region=='YUG':
        iso_list = YUG_iso_list
        out_code = 891
    else:
        iso_list = BAL_iso_list
        out_code = 56
    data = convert_iso_num(data,iso_list,iso_codes_df,out_code)
    

kwds = country_bounds_src.profile
out_local_file = os.path.join(output_dir,'GlobAgri_GAUL_ISO.tif')

data[data<0] = 0
print(np.unique(data))
kwds.update(dtype=rasterio.int16)
with rasterio.open(out_local_file, 'w', **kwds) as dst_dataset:
    data = data.astype('Int16')
    dst_dataset.dtype = 'Int16'
    dst_dataset.nodataval = 0
    dst_dataset.write_band(1,data.astype('Int16'))
    
