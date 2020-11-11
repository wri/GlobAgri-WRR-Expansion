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

#Define google cloud storage directories
output_dir = '/home/globagriwrr001/local'
GS_BUCKET = 'gs://globagri-upload-bucket'
bucket_name = 'globagri-upload-bucket'
    
    
#****************DESIRABILITY IN********************************************
def get_desirability_index(phys_area_file, distance_file,potential_yield, price,
                            lpjml_scaling, travel_time, average_speed, diesel_cost, fuel_eff, area_percent,
                            num_tons_per_truck=22.0,production_factor = 0.5,proximity_ratio=0.1):
    '''
    Function for calculating the desirability index for various crops. First calculates the revenue of the crop in $/tonnes and the 
        transportation cost in $/tonnes. Finds the profit of each pixel using (revenue-cost)*potential yield. Next calculates the distance
        in degrees to nearby cropland. Then scales the profit per pixel to the 0-1 range and the distance to nearby cropland to the 0-1 range.
                            
    Inputs:
        phys_area_file: A geotiff of physical area per pixel to use to calculate the distance to nearest cropland
        distance_file: The output file name to save the distance to nearest cropland calculation
        potential_yield: A numpy array of shape (height,width) representing the tonnes of fresh matter per hectare
        price: the price of crop at the farm gate in $/tonnes
        lpj_scaling: a scalar factor applied to the potential yield 
        travel_time: A numpy array of shape (height,width) the travel time in minutes to the nearest city
        average_speed: A number in kilometers per minute 
        diesel_cost: The cost of diesel in $/liter
        fuel_eff: The fuel efficiency of an average truck in liters of dieser/km
        area_percent: The ratio of area remaining in pixel for agriculture to the total land area in pixel (before removing exclusion areas)
        num_tons_per_truck: The number of tons a truck can hold in tonnes
        production_factor: fraction of profit that goes to production costs to produce the tonnes of crop
        proximity_ratio: factor to apply to proximity term for proportion of desirability index from proximity
        
    '''
    #Calculate dollar value of crop after production cost by multiplying price by production factor
    revenue = price*production_factor

    #Caclulate transportation cost as the $/tonne
    #$/truck as cost of diesel * average speed * fuel efficiency * travel time / number of tons per truck
    transportation_cost = diesel_cost*average_speed*fuel_eff*travel_time/num_tons_per_truck

    #Apply potential yield scaling factor to convert potential yield to attainable yeild
    lpj_factor = lpjml_scaling*potential_yield
    
    #Profit of each pixel = (revenue - transporation cost)*tonnes of crop produced/pixel
    profit = (revenue - transportation_cost)*lpj_factor
    
    #Use GDAL to calculate the distance to nearby cropland in degrees and read data
    gdal_expression = ('gdal_proximity.py {} {} -use_input_nodata YES -co COMPRESS=LZW').format(phys_area_file, distance_file)
    subprocess.check_output(gdal_expression, shell=True)
    distance = None
    with rasterio.open(distance_file) as dist_src:
        distance = dist_src.read(1)
    proximity = distance
    
    #Scale profit and proximity to both be on the 0-1 scale
    max_profit = np.amax(profit)
    min_profit = np.amin(profit)
    if max_profit != min_profit:
        scaled_profit = (profit-min_profit)/(max_profit-min_profit)
    else:
        scaled_profit = (profit-min_profit)
    
    max_proximity = np.amax(proximity)
    min_proximity = np.amin(proximity)
    if max_proximity != min_proximity:
        scaled_proximity = (proximity-min_proximity)/(max_proximity-min_proximity)
    else:
        scaled_proximity = (proximity-min_proximity)

    #Calculate diversity factor as e^(1-area remaining in pixel) so as the area remaining in the pixel fills up, the
    #diversity factor increases
    #Set nan and negative percents to 0
    area_percent[(area_percent<0)|(np.isnan(area_percent))] = 0
    area_factor = np.exp((1-area_percent))
    
    #Calculate index as
    index = scaled_profit - proximity_ratio*scaled_proximity - area_factor
    return index

def get_livestock_desirability_index(grazing_area_file, distance_file, potential_yield, price,
                            lpjml_scaling, travel_time, average_speed, diesel_cost, fuel_eff, area_percent,
                            num_tons_per_truck=22.0,production_factor = 0.5,proximity_ratio=0.05):
    '''
    Function for calculating the desirability index for various crops. First calculates the revenue of the crop in $/tonnes and the 
        transportation cost in $/tonnes. Finds the profit of each pixel using (revenue-cost)*potential yield. Next calculates the distance
        in degrees to nearby cropland. Then scales the profit per pixel to the 0-1 range and the distance to nearby cropland to the 0-1 range.
                            
    Inputs:
        grazing_area_file: A geotiff of livestock area per pixel to use to calculate the distance to nearest cropland
        distance_file: The output file name to save the distance to nearest livestock area calculation
        potential_yield: A numpy array of shape (height,width) representing the tonnes of grasses per hectare. Here we assume the tones of livestock 
                            production per hectare is proportional to potential yield of grasses
        price: the price of livestock at the farm gate in $/tonnes
        lpj_scaling: a scalar factor applied to the potential yield 
        travel_time: A numpy array of shape (height,width) the travel time in minutes to the nearest city
        average_speed: A number in kilometers per minute 
        diesel_cost: The cost of diesel in $/liter
        fuel_eff: The fuel efficiency of an average truck in liters of dieser/km
        area_percent: The ratio of area remaining in pixel for agriculture to the total land area in pixel (before removing exclusion areas)
        num_tons_per_truck: The number of tonnes a truck can hold in tonnes
        production_factor: fraction of profit that goes to production costs to produce the tonnes of livestock
        proximity_ratio: factor to apply to proximity term for proportion of desirability index from proximity
        
    '''
    #Calculate dollar value of crop after production cost by multiplying price by production factor
    revenue = price*production_factor

    #Caclulate transportation cost as the $/tonne
    #$/truck as cost of diesel * average speed * fuel efficiency * travel time / number of tons per truck
    transportation_cost = diesel_cost*average_speed*fuel_eff*travel_time/num_tons_per_truck

    #Apply potential yield scaling factor to convert potential yield to attainable yeild
    lpj_factor = lpjml_scaling*potential_yield
    
    #Profit of each pixel = (revenue - transporation cost)*tonnes of crop produced/pixel
    profit = (revenue - transportation_cost)*lpj_factor
    
    #Use GDAL to calculate the distance to nearby cropland in degrees and read data
    gdal_expression = ('gdal_proximity.py {} {} -use_input_nodata YES -co COMPRESS=LZW').format(phys_area_file, distance_file)
    subprocess.check_output(gdal_expression, shell=True)
    distance = None
    with rasterio.open(distance_file) as dist_src:
        distance = dist_src.read(1)
    proximity = distance
    
    #Scale profit and proximity to both be on the 0-1 scale
    max_profit = np.amax(profit)
    min_profit = np.amin(profit)
    if max_profit != min_profit:
        scaled_profit = (profit-min_profit)/(max_profit-min_profit)
    else:
        scaled_profit = (profit-min_profit)
    
    max_proximity = np.amax(proximity)
    min_proximity = np.amin(proximity)
    if max_proximity != min_proximity:
        scaled_proximity = (proximity-min_proximity)/(max_proximity-min_proximity)
    else:
        scaled_proximity = (proximity-min_proximity)

    #Calculate diversity factor as e^(1-area remaining in pixel) so as the area remaining in the pixel fills up, the
    #diversity factor increases
    #Set nan and negative percents to 0
    area_percent[(area_percent<0)|(np.isnan(area_percent))] = 0
    area_factor = np.exp((1-area_percent))
    
    #Calculate desirability index
    index = scaled_profit - proximity_ratio*scaled_proximity - area_factor
    return index



#*********DEFINE SOME CONSTANTS***************************************
fuel_eff = 0.2408; # liters of diesel/km
truck_payload = 21653.4; #kg
lpj_scaling = 0.6; #scaling factor for reducing LPJmL (calculate later)
average_speed = 1.16667; #kilometers per minute (comes from 70 km/hr)
max_distance = 100000000000000; #maximum distance to calculate distance to for distance calculation
ha_per_cycle = 100; #number of hectares to increase per cycle 
start_year = 2010
end_year = 2050
year_diff = end_year-start_year
sq_km_to_ha = 100 #number of hectares in a square kilometer
GLPS_Blocker = False
#******************************************************************************


def expansion(args):
    '''
    Function to allocate changes in cropland and livestock areas from GlobAgri.
    Inputs:
        args: a list = [iso, scenario] where iso is the 3 character ISO code and scenario is the name of the GlobAgri scenario
    '''
    iso = args[0]
    scenario = args[1]
    try:
        print(iso)
        
        #***************DEFINE AND READ FILES********************************************
        base_dir = '/home/globagriwrr001/globagriexpansion'
        saving_dir = os.path.join(GS_BUCKET,'Ag_Expansion_Results',scenario.replace(" ", "_"),iso,'')
        os.chdir(base_dir)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        #Define table of ISO and FAO codes by country
        FAO_country_codes = pd.read_csv(os.path.join(base_dir,'CSVs','full_country_codes.csv'))
        
        #Find the ISO number of the current country
        ISO_number = FAO_country_codes[FAO_country_codes['ISO3']==iso]['ISO_NUM'].values[0]
        
        #Read in country boundaries, a raster where each pixel is coded as the ISO number of each country or 0 otherwise
        Country_Boundaries_f = os.path.join(base_dir,'OtherFiles','country_bound_rasters','iso_bounds_{}.tif'.format(iso))
        Country_Boundaries_src = rasterio.open(Country_Boundaries_f)
        Country_Boundaries = Country_Boundaries_src.read(1)
        country_bounds = Country_Boundaries == ISO_number
                         
        #Read in GlobAgri results including cropping intensity, livestock areas, and harvest area by crop for each country
        all_scenario_cropping_intensity = pd.read_csv(os.path.join(base_dir,'CSVs','cropping_intensity_country_all_scenarios.csv'))
        all_scenario_livestock_area = pd.read_csv(os.path.join(base_dir,'CSVs','livestock_area_country_all_scenarios.csv'))
        all_scenario_harv_area = pd.read_csv(os.path.join(base_dir,'CSVs','harv_area_country_all_scenarios.csv'))

        #Read in table to map SPAM product name to its potential yield name
        spam_to_lpj_table = pd.read_csv(os.path.join(base_dir,'CSVs','map_spam_products_LPJmL_new.csv'))
                
        #Read in the travel time per pixel
        Nelson_travel_time_f = os.path.join(base_dir,'OtherFiles','NelsonTravelTime_by_Country','NelsonTravelTimeMinutes_{}.tif'.format(iso))
        Nelson_travel_time = Nelson_travel_time_src.read(1)
        Nelson_travel_time[np.where(country_bounds==0)] = Nelson_travel_time_src.nodatavals[0]
        
        #Read in the area of land in hectares per pixel. 
        max_pixel_area_f = os.path.join(base_dir,'OtherFiles','LandPixelArea_by_Country','LandPixelArea_ha_{}.tif'.format(iso))
        max_area_src = rasterio.open(max_pixel_area_f)
        max_area_in_pixel = max_area_src.read(1)
        
        #Read in the area of impervious surfaces in hectares per pixel
        urban_area_f = os.path.join(base_dir,'OtherFiles','BuiltUp_Area_by_Country','builtup_area_ha_{}.tif'.format(iso))
        urban_area_src = rasterio.open(urban_area_f)
        urban_area = urban_area_src.read(1)
        urban_area[np.isnan(urban_area)] = 0
        
        #Define folders for spam harvest area, hyde livestock areas, and potential yield
        spam_physical_area_folder = os.path.join(base_dir,'SPAM','phys_area_by_country_fixed')
        lpj_folder = os.path.join(base_dir,'LPJmL_averaged','LPJmL_by_Country')
        HYDE_area_folder = os.path.join(base_dir,'HYDE','HYDE_by_Country_fixed')
        
        #Read in the total cropland area per pixel (the sum of all crops physical area per pixel)
        physical_area_total_f = os.path.join(base_dir,'SPAM','phys_area_by_country_fixed','total_physical_area_{}.tif'.format(iso))
        physical_area_total_src = rasterio.open(physical_area_total_f)
        physical_area_total = physical_area_total_src.read(1)
        kwds = physical_area_total_src.profile
        
        #Read in the livestock area in hectares per pixel
        hyde_grazing_f = os.path.join(HYDE_area_folder,'grazing_2010AD_{}.tif'.format(iso))
        hyde_grazing_src = rasterio.open(hyde_grazing_f)
        hyde_grazing_area = hyde_grazing_src.read(1)
        hyde_mask = hyde_grazing_area==hyde_grazing_src.nodatavals[0]
        hyde_grazing_area[hyde_mask] = 0
        
        #Read in the potential yield for grasses (used in livestock desirability index)
        grasses_yield_f = os.path.join(lpj_folder,'grasses_{}.tif'.format(iso))
        grasses_yield_src = rasterio.open(grasses_yield_f)
        grasses_yield = grasses_yield_src.read(1)
        
        #Read the Global Livestock Production Systems (GLPS) which defines humid and temperate areas for livestock. From GlobAgri, 
        #all growth and reductions in livestock grazing areas in future years are estimated to come from humid and temperate zones.
        glps_f = os.path.join(base_dir,'OtherFiles','GLPS_by_Country','GLPS_{}.tif'.format(iso))
        glps_src = rasterio.open(glps_f)
        glps = glps_src.read(1)
        #Filter to humid and termperate zones
        glps = (glps==3)|(glps==4)|(glps==7)|(glps==8)

        #Define table of crop prices at the farm gate by country
        wb_spam_crop_prices = pd.read_csv(os.path.join(base_dir,'CSVs','SPAM_2010_Country_Prices.csv'))
        crop_prices = wb_spam_crop_prices[wb_spam_crop_prices['ISO_Code']==iso]
        
        #Read livestock price from table of livestock prices at the farm gate. If missing, fill in by the average value
        #of all countries
        wb_livestock_prices = pd.read_csv(os.path.join(base_dir,'CSVs','SPAM_2010_Livestock_Prices.csv'))
        try:
            livestock_priceslivestock_price = wb_livestock_prices[(wb_livestock_prices['Area Code']==FAO_STAT_code)&(wb_livestock_prices['Item']=='Meat live weight, cattle')]
            livestock_price = livestock_price['Value'].tolist()[0]
        except:
            livestock_price = wb_livestock_prices[wb_livestock_prices['Item']=='Meat live weight, cattle']
            livestock_price = np.mean(livestock_price['Value'].values)
            
        #Read diesel cost from table. If missing, fill in by the average value of all countries
        wb_diesel_cost = pd.read_csv(os.path.join(base_dir,'CSVs','WB_Diesel_Fuel_Cost.csv'))
        try:
            diesel_cost = wb_diesel_cost[wb_diesel_cost['Country Code']==iso].get('2010').tolist()[0]
        except:
            diesel_cost = np.mean(wb_diesel_cost['2010'].values)
        #*********************************************************************************************************************



        #*************GET CHANGE PER YEAR FOR GRAZING AREA, PHYSICAL AREA, AND CROPPING INTENSITY***************************************
        #Define a list of all spam crops using their "short name"
        crops = ['acof', 'bana', 'barl', 'bean', 'cass', 'chic', 'cnut', 'coco', 'cott', 'cowp', 'grou', 'lent', 'maiz',
                'ocer', 'ofib', 'oilp', 'ooil', 'opul', 'orts', 'pige', 'plnt', 'pmil', 'pota', 'rape', 'rcof', 'rest', 'rice',
                'sesa', 'smil', 'sorg', 'soyb', 'sugb', 'sugc', 'sunf', 'swpo', 'teas', 'temf', 'toba', 'trof', 'vege', 'whea', 'yams']

        #Find the change per year in cropping intenisty
        ci_start_year = all_scenario_cropping_intensity[all_scenario_cropping_intensity['ISO3']==iso]['2010'].values[0]
        ci_end_year = all_scenario_cropping_intensity[all_scenario_cropping_intensity['ISO3']==iso][scenario].values[0]
        cropping_intensity_change_per_year = (ci_end_year-ci_start_year)/(float(year_diff))
        
        #Read in pasture 2010 and 2050 areas
        try:
            pasture_area_2010 = all_scenario_livestock_area[all_scenario_livestock_area['ISO3']==iso]['2010'].values[0]
            pasture_area_2050 = all_scenario_livestock_area[all_scenario_livestock_area['ISO3']==iso][scenario].values[0]
        except:
            pasture_area_2010=0
            pasture_area_2050=0
        grazing_area_change_per_year = (pasture_area_2050-pasture_area_2010)/(year_diff)

        #Read in the 2010 and 2050 cropland areas
        country_harvest_area = all_scenario_harv_area[all_scenario_harv_area['ISO3']==iso].copy()
        glob_agri_start_year = country_harvest_area[['ISO3','SPAM short name','2010']].copy()
        glob_agri_end_year = country_harvest_area[['ISO3','SPAM short name',scenario]].copy()

        glob_agri_start_year['PhysArea'] = glob_agri_start_year['2010'].values/ci_start_year
        glob_agri_end_year['PhysArea'] = glob_agri_end_year[scenario].values/ci_end_year
        
        #Calculate change in physical area per year for each crop
        phys_area_change = pd.DataFrame()
        phys_area_change['CropName'] = glob_agri_start_year['SPAM short name'].values
        phys_area_change['Country'] = glob_agri_start_year['ISO3'].values
        phys_area_change['PhysAreaChangePerYear_ha'] = (glob_agri_end_year['PhysArea'].values - glob_agri_start_year['PhysArea'].values)/(year_diff)

        #Only select crops that appear in country
        selected_crops = [x for x in crops if x in phys_area_change['CropName'].values]
        print('Number of crops for {}: {}'.format(iso,len(selected_crops)))
        #*******************************************************************************************



        #*******GET 2010 REFERENCE YEAR AREAS***************************************************************
        year_name = 2010
        
        #Calculate the area available per pixel by removing impervious surface areas
        max_area_in_pixel[(max_area_in_pixel<0)|(np.isnan(max_area_in_pixel))] = 0
        area_left_in_pixel = max_area_in_pixel-urban_area
        area_left_in_pixel = area_left_in_pixel-physical_area_total

        if np.sum(area_left_in_pixel<0)>0:
            area_left_in_pixel[area_left_in_pixel<0]=0

        #Remove grazing areas that are greater than the area remaining in the pixel
        hyde_greater_than_area = hyde_grazing_area > area_left_in_pixel
        hyde_less_than_area = hyde_grazing_area <= area_left_in_pixel
        hyde_grazing_area[hyde_greater_than_area] = np.copy(area_left_in_pixel[hyde_greater_than_area])
        hyde_grazing_area[~country_bounds] = 0
        area_left_in_pixel[hyde_greater_than_area] = 0
        area_left_in_pixel[hyde_less_than_area] = np.copy(area_left_in_pixel[hyde_less_than_area] -  hyde_grazing_area[hyde_less_than_area])

        #Scale area remaining to leave 1% of all land for settlement areas
        area_left_in_pixel[~country_bounds] = 0
        area_left_in_pixel = 0.99*area_left_in_pixel #leave in 1% buffer
        
        #Save total cropland area of all crops in 2010 to file for reference
        total_phys_file = os.path.join(output_dir,'{}_{}_all_crops_new_physical_area.tif')
        with rasterio.open(physical_area_total_f) as src_dataset:
            with rasterio.open(total_phys_file.format(iso,year_name), 'w', **kwds) as dst_dataset:
                dst_dataset.write_band(1,physical_area_total)
            cmd = ['sudo','gsutil','-m','cp',total_phys_file.format(iso,year_name),saving_dir]
            subprocess.call(cmd)
        
        #Save total grazing area in 2010 to file for reference
        total_grazing_file = os.path.join(output_dir,'{}_{}_new_grazing_area.tif')
        with rasterio.open(Nelson_travel_time_f) as src_dataset:
            kwds = src_dataset.profile
            kwds.update(nodata=-1)
            temp_grazing_area = np.copy(hyde_grazing_area)
            with rasterio.open(total_grazing_file.format(iso,year_name), 'w', **kwds) as dst_dataset:
                temp_grazing_area[temp_grazing_area<0] = -1
                temp_grazing_area[~country_bounds] = -1
                dst_dataset.write_band(1,temp_grazing_area)
            cmd = ['sudo','gsutil','-m','cp',total_grazing_file.format(iso,year_name),saving_dir]
            subprocess.call(cmd)
            
        #Save area remaining in 2010 to file for reference
        area_remaining_file = os.path.join(output_dir,'{}_{}_area_remaining.tif')
        with rasterio.open(Nelson_travel_time_f) as src_dataset:
            kwds = src_dataset.profile
            kwds.update(nodata=-1)
            temp_area_left_in_pixel = np.copy(area_left_in_pixel)
            with rasterio.open(area_remaining_file.format(iso,year_name), 'w', **kwds) as dst_dataset:
                temp_area_left_in_pixel[temp_area_left_in_pixel<0] = -1
                temp_area_left_in_pixel[~country_bounds] = -1
                dst_dataset.write_band(1,temp_area_left_in_pixel.astype('float32'))
            cmd = ['sudo','gsutil','-m','cp',area_remaining_file.format(iso,year_name),saving_dir]
            subprocess.call(cmd)


        #Read in physical area by crop to array and matching potential yield to another array
        all_physical_area = np.zeros((len(selected_crops),hyde_grazing_src.height,hyde_grazing_src.width))
        all_potential_yield = np.zeros((len(selected_crops),hyde_grazing_src.height,hyde_grazing_src.width))
        for i,crop in enumerate(selected_crops):
            print(i,crop)
            with rasterio.open(os.path.join(spam_physical_area_folder,'{}_{}.tif'.format(crop,iso))) as src:
                all_physical_area[i,:,:] = src.read(1)

            matching_lpj_name = spam_to_lpj_table[spam_to_lpj_table['SPAM short name']==crop].get('YieldCrop').tolist()[0]
            with rasterio.open(os.path.join(lpj_folder,'{}_{}.tif'.format(matching_lpj_name,iso))) as src:
                all_potential_yield[i,:,:] = src.read(1)
        # #*******************************************************************************************





        #*********************EXPANSION FUNCTION TIME***************************************************
        #Copy raster profile but remove compression for temporary files used to measure distance
        temp_kwds = kwds
        temp_kwds['compress'] = None
        
        #Read change in areas per year for each crop into a table
        initial_area_to_allocate = pd.DataFrame()
        for i,crop in enumerate(selected_crops):
            crop_phys_area_change = phys_area_change[phys_area_change['CropName']==crop].get('PhysAreaChangePerYear_ha').tolist()[0]
            initial_area_to_allocate.at[0,crop] = crop_phys_area_change


        #LOOP THROUGH YEARS
        for year_index in np.arange((year_diff)):
            print('Year:',year_index,'ISO:',iso,'Scenario',scenario)
            area_to_allocate = initial_area_to_allocate.copy()
            
            #Loop through crops and calculate index
            indices = np.zeros((len(selected_crops),hyde_grazing_src.height,hyde_grazing_src.width))
            for i,crop in enumerate(selected_crops):
                #Write physical area to temporary file used to measure distance and define the file to save the distance values to
                temp_phys_file_for_dist = os.path.join(output_dir,'{}_{}_temp_phys_area.tif'.format(iso,crop))
                temp_crop_dist_file = os.path.join(output_dir,'{}_{}_temp_crop_distance.tif'.format(iso,crop))
                temp_physical_area_to_write = all_physical_area[i,:,:]
                with rasterio.open(temp_phys_file_for_dist, 'w', **temp_kwds) as dst_dataset:
                    dst_dataset.write(temp_physical_area_to_write.astype('float32'), 1)
                    
                #Read in potential yield for the current crop
                potential_yield = all_potential_yield[i,:,:]
                
                #Read in the crop price from the crop price table
                try:
                    crop_price = crop_prices[crop_prices['SPAM_short']==crop].get('Value').tolist()[0]
                except:
                    crop_price = np.mean(wb_spam_crop_prices[wb_spam_crop_prices['SPAM_short']==crop].get('Value').to_numpy())

                #Find the % of area remaining in the pixel for cropland
                percent_area_remaining = np.divide(area_left_in_pixel, max_area_in_pixel, out=np.zeros_like(area_left_in_pixel), where=max_area_in_pixel!=0)
                
                #Get the index at each pixel from the desirability index function
                index = get_desirability_index(temp_phys_file_for_dist, temp_crop_dist_file, potential_yield, crop_price,
                                    0.9, Nelson_travel_time, average_speed, diesel_cost, fuel_eff, country_bounds, percent_area_remaining)
                
                #Save to array and remove temporary files
                indices[i,:,:] = np.copy(index)
                os.remove(temp_phys_file_for_dist)
                os.remove(temp_crop_dist_file)

            #Allocate the number of hectares per year until the change per year has been allocated.
            #While there is still any cropland area left to allocate:
                #Cycle through each crop and add or remove a small area based on the change per year
            while(area_to_allocate.any(axis=None)):
                #Loop through crops
                for i,crop in enumerate(selected_crops):
                    #Use crop_area_to_allocate to track the area remaining to allocate, first set it to the annual change per year
                    crop_area_to_allocate = area_to_allocate.at[0,crop]
                    print(year_index,'Crop',crop,crop_area_to_allocate)

                    #Read in desirability index and physical area
                    index = np.copy(indices[i,:,:])
                    physical_area = np.copy(all_physical_area[i,:,:])
                    
                    #Initialize array to keep track of which pixels have been allocated into to prevent one pixel from being expaned into multiple times
                    #in a cycle
                    indices_used = np.zeros((hyde_grazing_src.height,hyde_grazing_src.width))

                    #If area to allocate is greater than 0, find the most desirable pixel and expand into that pixel by the minimum of:
                        #1. Area available in the pixel
                        #2. Maximum change in area per cycle
                        #3. Area remaining to allocate
                    #Remove the area added from the area remaining from pixel and add the area added to the physical area array
                    if crop_area_to_allocate >0:
                        #Each loop in the while loop is a cycle
                        while crop_area_to_allocate!=0:
                            
                            #If there is no area remaining in the country, set the crop_area_to_allocate to 0 which will end the loop
                            temp_area_remaining = np.copy(area_left_in_pixel)
                            temp_area_remaining[~country_bounds]=0
                            if np.sum(temp_area_remaining)==0:
                                crop_area_to_allocate=0
                            
                            #Take the minimum of the crop_area_to_allocate and ha_per_cycle, the maximum area change per cycle
                            alloc = min([crop_area_to_allocate,ha_per_cycle])
                            
                            #Define mask of valid pixels: pixels within the country bounds, have area remaining to expand into,
                            #are valid for physical area, and have not been expanded into yet (using indices_used)
                            mask = (~country_bounds) | (area_left_in_pixel<=0) | (physical_area<0) | (indices_used==1)
                            masked_index = np.ma.masked_array(index, mask=mask)

                            #Find the pixel with the highest desirability index
                            index_max = np.unravel_index(np.argmax(masked_index, axis=None), masked_index.shape)
                            
                            #Set indices_used at the maximum pixel to 1 so that it will not be expanded into again this year
                            indices_used[index_max] = 1
                            
                            #Define the area to add to the pixel as the minimum of the remaining area in the pixel and the limit from line 482
                            area_to_add = min(area_left_in_pixel[index_max],alloc)

                            #If the area_to_add<=0, all pixels in the country have been used, reset the indices_used to allow further expansion
                            if area_to_add<=0:
                                indices_used[:,:]=0
                            #if area_to_add>0: the max pixel is valid
                            else:
                                #Add area_to_add to physical area
                                physical_area[index_max] = physical_area[index_max] + area_to_add
                                #Remove area_to_add from area left in pixel
                                area_left_in_pixel[index_max] = area_left_in_pixel[index_max] - area_to_add
                                #Remove area_to_add from crop area left to allocate
                                crop_area_to_allocate = crop_area_to_allocate - area_to_add

                    #If area to allocate is less than 0, find the least desirable pixel and remove cropland equal to the minimum of:
                        #1. Crop physical area in the pixel
                        #2. Maximum change in area per cycle
                        #3. Area remaining to remove
                    #Remove the area added from the area remaining from pixel and add the area added to the physical area array
                    elif crop_area_to_allocate <0:
                        while crop_area_to_allocate!=0:
                            
                            #Find the minimum of the crop area remaining to remove and the maximum change in area per cycle
                            alloc = min([-1*crop_area_to_allocate,ha_per_cycle])
                            
                            #Define mask of valid pixels: pixels within the country bounds, with no cropland in the pixel,
                            #and have not been expanded into yet (using indices_used)
                            mask = (~country_bounds) | (area_left_in_pixel>=max_area_in_pixel) | (physical_area<=0) | (indices_used==1)
                            masked_index = np.ma.masked_array(index, mask=mask)
                            
                            #Find the pixel with the smallest desirability index to remove area from
                            index_min = np.unravel_index(np.argmin(masked_index, axis=None), masked_index.shape)
                            
                            #Set indices_used at the minimum pixel to 1 so that area will not be removed from it again this year
                            indices_used[index_min] = 1
                            
                            #Find the area to remove as the minimum of above and the cropland area in the pixel
                            area_to_remove = min(alloc, physical_area[index_min])
                            
                            #Remove area from physical area
                            physical_area[index_min] = physical_area[index_min] - area_to_remove
                            #Add area to area left in pixel
                            area_left_in_pixel[index_min] = area_left_in_pixel[index_min] + area_to_remove
                            #Add area to area left to allocate to bring it closer to 0
                            crop_area_to_allocate = crop_area_to_allocate + area_to_remove
                            
                            #If there is no physical area remaining, set crop_area_to_allocate to 0 to end cycles
                            if np.sum(physical_area>0)<=0:
                                crop_area_to_allocate = 0
                            #If area to remove<=0: there are no more pixels left to remove area from so set crop_area_to_allocate to 0 to end cycles
                            if area_to_remove<=0:
                                crop_area_to_allocate=0
                    
                    #Reset indices
                    index = None
                    indices_used = None
                    masked_index = None
                    mask = None

                    #Save new physical area to tracking array
                    all_physical_area[i,:,:] = np.copy(physical_area)
                    #Set area_to_allocate to remaining area to allocate to start the loop again
                    area_to_allocate.at[0,crop] = crop_area_to_allocate
                    
            #Once all changes in crop physical area have been allocated, then allocate change in livestock areas
            #Write physical area to temporary file used to measure distance and define the file to save the distance values to
            temp_grazing_file_for_dist = os.path.join(output_dir,'{}_temp_grazing_area.tif'.format(iso))
            temp_grazing_dist_file = os.path.join(output_dir,'{}_temp_grazing_distance.tif'.format(iso))
            with rasterio.open(temp_grazing_file_for_dist, 'w', **temp_kwds) as dst_dataset:
                grazing = hyde_grazing_area.astype('float32')
                dst_dataset.write(hyde_grazing_area, 1)
                
            #Find the % of area remaining in the pixel for cropland
            percent_area_remaining = np.divide(area_left_in_pixel, max_area_in_pixel, out=np.zeros_like(area_left_in_pixel), where=max_area_in_pixel!=0)
            
            #Get the index at each pixel from the desirability index function
            grazing_index = get_livestock_desirability_index(temp_grazing_file_for_dist, temp_grazing_dist_file, grasses_yield, livestock_price,
                                0.9, Nelson_travel_time, average_speed, diesel_cost, fuel_eff, country_bounds,percent_area_remaining)
            
            #Create grazing_area_left_to_allocate used to track how many hectares are left to allocate after each cycle
            grazing_area_left_to_allocate = grazing_area_change_per_year

            #Initialize array to track which pixels have already been allocated to
            indices_used = np.zeros((hyde_grazing_src.height,hyde_grazing_src.width))
            
            
            #If area to allocate is greater than 0, find the most desirable pixel and expand into that pixel by the minimum of:
                #1. Area available in the pixel
                #2. Maximum change in area per cycle
                #3. Area remaining to allocate
            if grazing_area_left_to_allocate >0:
                while grazing_area_left_to_allocate!=0:
                    
                    #If there is no area remaining in the country, set the crop_area_to_allocate to 0 which will end the loop
                    temp_area_remaining = np.copy(area_left_in_pixel)
                    temp_area_remaining[~country_bounds]=0
                    if np.sum(temp_area_remaining)==0:
                        grazing_area_left_to_allocate=0
                    
                    #Take the minimum of the grazing_area_left_to_allocate and ha_per_cycle, the maximum area change per cycle
                    alloc = min([grazing_area_left_to_allocate,ha_per_cycle])
                    
                    #Define mask of valid pixels: pixels within the country bounds, have area remaining to expand into,
                    #are valid for grazing area, are humid or temperate, and have not been expanded into yet (using indices_used)
                    mask = (~country_bounds) | (area_left_in_pixel<=0) | (hyde_grazing_area<0) | (glps==0) | (indices_used==1)
                    masked_index = np.ma.masked_array(grazing_index, mask=mask)
                    
                    #Find the pixel with the highest desirability index
                    index_max = np.unravel_index(np.argmax(masked_index, axis=None), masked_index.shape)
                    #Set indices_used at the maximum pixel to 1 so that it will not be expanded into again this year
                    indices_used[index_max]=1
                    
                    #Define the area to add to the pixel as the minimum of the remaining area in the pixel and the limit from line 482
                    area_to_add = min(area_left_in_pixel[index_max],alloc)

                    #If the area_to_add<=0, all pixels in the country have been used, reset the indices_used to allow further expansion
                    if area_to_add<=0:
                        indices_used[:,:]=0
                        #If the GLPS_Blocker=False, set GLPS = true for all pixels to allow grazing area to expand beyond humid and temperate
                        if GLPS_Blocker==False:
                            glps[:,:]=1
                    else:
                        #Add area_to_add to grazing area
                        hyde_grazing_area[index_max] = hyde_grazing_area[index_max] + area_to_add
                        #Remove area_to_add from area left in pixel
                        area_left_in_pixel[index_max] = area_left_in_pixel[index_max] - area_to_add
                        #Remove area_to_add from grazing_area_left_to_allocate
                        grazing_area_left_to_allocate = grazing_area_left_to_allocate - area_to_add


            #If area to allocate is less than 0, find the least desirable pixel and remove livestock area equal to the minimum of:
                #1. Livestock  area in the pixel
                #2. Maximum change in area per cycle
                #3. Area remaining to remove
            #Remove the area added from the area remaining from pixel and add the area added to the livestock area array
            elif grazing_area_left_to_allocate <0:
                print(year_index,'Grazing',grazing_area_left_to_allocate)
                while grazing_area_left_to_allocate!=0:
                    
                    #Find the minimum of the crop area remaining to remove and the maximum change in area per cycle
                    alloc = min([-1*grazing_area_left_to_allocate,ha_per_cycle])
                    
                    #Define mask of valid pixels: pixels within the country bounds, with no livestock area in the pixel, valid for contraction from GLPS
                    #and have not been expanded into yet (using indices_used)
                    mask = (~country_bounds) | (area_left_in_pixel>=max_area_in_pixel) | (hyde_grazing_area<=0) | (glps==0) | (indices_used==1)
                    masked_index = np.ma.masked_array(grazing_index, mask=mask)
                    
                    #Find the pixel with the smallest desirability index to remove area from
                    index_min = np.unravel_index(np.argmin(masked_index, axis=None), masked_index.shape)
                    
                    #Set indices_used at the minimum pixel to 1 so that area will not be removed from it again this year
                    indices_used[index_min]=1
                    
                    #Find the area to remove as the minimum of above and the grazing area in the pixel
                    area_to_remove = min(alloc, hyde_grazing_area[index_min])
                    
                    #Remove area from livestock area
                    hyde_grazing_area[index_min] = hyde_grazing_area[index_min] - area_to_remove
                    #Add area to area left in pixel
                    area_left_in_pixel[index_min] = area_left_in_pixel[index_min] + area_to_remove
                    #Add area to area left to allocate to bring it closer to 0
                    grazing_area_left_to_allocate = grazing_area_left_to_allocate + area_to_remove

                    #If there is no grazing area remaining, set crop_area_to_allocate to 0 to end cycles
                    if np.sum(hyde_grazing_area>0)<=0:
                        grazing_area_left_to_allocate = 0
                    #If area to remove<=0: there are no more pixels left to remove area from so set grazing_area_left_to_allocate to 0 to end cycles
                    if area_to_remove<=0:
                        grazing_area_left_to_allocate=0

            #Remove temporary files and reset some varaibles
            os.remove(temp_grazing_file_for_dist)
            os.remove(temp_grazing_dist_file)
            grazing_index = None
            indices_used = None
            masked_index = None
            mask = None

            #Define year name
            year_name = start_year + year_index +1
            #If we're on the last year, write arrays to geotiffs
            if year_index==39:
                output_dir2 = os.path.join(output_dir,'{}_Year_{}'.format(iso,year_name))
                if not os.path.exists(output_dir2):
                    os.makedirs(output_dir2)
                out_phys_file = os.path.join(output_dir2,'{}_{}_{}_new_physical_area.tif')
                out_grazing_file = os.path.join(output_dir2,'{}_{}_new_grazing_area.tif'.format(iso,year_name))

                with rasterio.open(Nelson_travel_time_f) as src_dataset:
                    kwds = src_dataset.profile
                    kwds.update(nodata=-1)
                    for i,crop in enumerate(selected_crops):
                        with rasterio.open(out_phys_file.format(iso,year_name,crop), 'w', **kwds) as dst_dataset:
                            all_physical_area = all_physical_area.astype('float32')
                            all_physical_area[i,~country_bounds] = -1
                            dst_dataset.write_band(1,all_physical_area[i,:,:])
                        cmd = ['sudo','gsutil','-m','cp',out_phys_file.format(iso,year_name,crop),saving_dir]
                        subprocess.call(cmd)

                with rasterio.open(Nelson_travel_time_f) as src_dataset:
                    kwds = src_dataset.profile
                    kwds.update(nodata=-1)
                    with rasterio.open(out_grazing_file, 'w', **kwds) as dst_dataset:
                        hyde_grazing_area = hyde_grazing_area.astype('float32')
                        hyde_grazing_area[~country_bounds] = -1
                        dst_dataset.write_band(1,hyde_grazing_area)
                    cmd = ['sudo','gsutil','-m','cp',out_grazing_file,saving_dir]
                    subprocess.call(cmd)


                total_phys_file = os.path.join(output_dir2,'{}_{}_all_crops_new_physical_area.tif')
                with rasterio.open(Nelson_travel_time_f) as src_dataset:
                    kwds = src_dataset.profile
                    kwds.update(nodata=-1)
                    final_total_physical_area = np.nansum(all_physical_area, axis=0)
                    with rasterio.open(total_phys_file.format(iso,year_name), 'w', **kwds) as dst_dataset:
                        final_total_physical_area[final_total_physical_area<0] = -1
                        final_total_physical_area[~country_bounds] = -1
                        dst_dataset.write_band(1,final_total_physical_area)
                    cmd = ['sudo','gsutil','-m','cp',total_phys_file.format(iso,year_name),saving_dir]
                    subprocess.call(cmd)
    except:
        print("FAILED {}".format(iso))
            

#Define scenarios and countries to loop over    
scenarios = ['2050 Baseline Scenario','Alternative Baseline Scenario','No Productivity Gains After 2010 Scenario',
            'Coordinated Effort Scenario','Highly Ambitious Scenario','Breakthrough Technologies Scenario']

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
#Define countries done 
countries_done = []
#Run remaining countries
countries = [x for x in countries if x not in countries_done]

print("Starting!")
#Loop through scenarios and run expansion algorithm in parallel over countries
for scenario in scenarios:
   args = [[iso,scenario] for iso in countries] 
   pool = mp.Pool(processes=8)
   results = pool.map(expansion, args)
   
