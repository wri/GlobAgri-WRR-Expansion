import rasterio
from rasterio.features import shapes
import geopandas as gp
import os
import pandas as pd
import numpy as np

iso_raster_dir = '/Users/kristine/WRI/NationalGeographic/Phase2/Country_Bounds/'
out_directory = '/Users/kristine/WRI/NationalGeographic/Phase2/Country_Bounds/Country_shapes'
os.chdir(iso_raster_dir)
iso_raster_f = 'GlobAgri_GAUL_ISO.tif'

iso_num_df = pd.read_csv('/Users/kristine/WRI/NationalGeographic/Phase2/Country_Bounds/full_country_codes.csv')

globagri_regions = ['CHN','SUN', 'BAL'];
SUN_iso_list = ['ARM', 'AZE', 'BLR', 'GEO', 'KAZ', 'KGZ', 'MDA', 'RUS', 'TJK', 'TKM', 'UKR', 'UZB'];
BAL_iso_list = ['BEL', 'LUX'];
YUG_iso_list = ['BIH','HRV','MKD','MNE','SRB','SVN']
CHN_iso_list = ['CHN', 'TWN', 'HKG']

def convert_iso_num(in_number,country_df):
    print(country_df[country_df['ISO_NUM']==in_number]['ISO3'].values)
    iso_code = country_df[country_df['ISO_NUM']==in_number]['ISO3'].values[0]
    if iso_code in SUN_iso_list:
        iso_code = 'SUN'
    elif iso_code in BAL_iso_list:
        iso_code = 'BAL'
    elif iso_code in CHN_iso_list:
        iso_code = 'CHN'
    elif iso_code in YUG_iso_list:
        iso_code='YUG'
    return iso_code


src = rasterio.open(iso_raster_f)
data = src.read(1)
unique_values = np.unique(data)
unique_values = [x for x in unique_values if x>0]


for i,pixel_value in enumerate(unique_values):
    if pixel_value==643:
        try:
            iso_code = convert_iso_num(pixel_value,iso_num_df)
            output_file = os.path.join(out_directory,'{}_polygon.shp'.format(iso_code))
            image = data#src.read(1) # first band
            transform = src.transform
            results = (
            {'properties': {'raster_val': v}, 'geometry': s}
            for j, (s, v) 
            in enumerate(
                shapes(data, mask=data==pixel_value, transform=src.transform)))
            geoms = list(results)

            gpd_polygonized_raster  = gp.GeoDataFrame.from_features(geoms)
    
            gpd_polygonized_raster.crs = 'EPSG:4326'
            gpd_polygonized_raster['geometry'] = gpd_polygonized_raster.geometry.buffer(0)
            gpd_polygonized_raster.to_file(output_file,driver='ESRI Shapefile')
        except:
           print('{} of {} and value {}'.format(i,len(unique_values),pixel_value))
