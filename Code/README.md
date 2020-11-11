# GlobAgri-WRR-Expansion
This repository contains code for allocating estimates of cropland and livestock areas from the GlobAgri-WRR model, described in the 2019 World Resources Report, ["Creating a Sutainable Food Future"](https://wrr-food.wri.org/).

The file structure is as follows
1. Average_LPJmL.py: used to average the rainfed and irrigated potential yields from LPJmL.
1. Expansion_Algorithm_v6.py: used to allocate changes in cropland and livestock areas.
1. Fill_Shapefile_Country_Cropland_Values.py: used to fill in GAUL country boundary shapefile with GlobAgri-WRR values to visualize
1. GetLandAreaPerPixel: uses Google Earth Engine to calculate the maximum land area per pixel
1. Merge_Final_Rasters.py: merge country level results from expansion to global files
1. Merge_GAUL_Countries.py: merge countries within GlobAgri-WRR regions
1. clip_rasters_by_country_bounds.py: used to clip rasters of 2010 values to country boundaries, including potential yield, cropland, livestock, travel time to cities, maximum areas per pixel, and urban areas.
1. convert_gaul_to_iso_raster.py: used to convert GAUL country boundaries shapefile to 10 kilometer raster 
1. convert_hyde_km_to_ha.py: converts the HYDE livestock areas from square kilometers per pixel to square hectares per pixel
1. fix_country_bounds_iso_numbers.py: changes ISO numbers encoded in convert_gaul_to_iso_raster.py to match regional groupings from GlobAgri-WRR including the former Soviet Union, the former Yugoslavia, Belgium-Luxembourg, and China, Hong Kong, and Taiwan.
1. polyganize_rasters.py: used to convert the ISO raster from fix_country_bounds_iso_numbers.py to polygons to clip rasters in clip_rasters_by_country_bounds.py
1. reproject_urban_built_up.py: converts 1 kilometer impervious surface percent to hectares of urban built up per pixel at the 10 kilometer resolution
1. upload_GLPS_to_gcloud.py: uploads the Global Livestock Production Systems raster to Google Cloud Storage
1. upload_LPJmL_to_gcloud.py: uploads LPJmL potential yield data to Google Cloud Storage
1. upload_hyde_to_gcloud.py: uploads HYDE data to Google Cloud Storage
1. upload_spam_to_gcloud.py: uploads SPAM data to Google Cloud
1. visualize_agriculture_rasters.py: used to create images of 2050 agricultural areas from expansion algorithm
1. visualize_country_totals.py: used to create images of country level changes in cropland and grazing land from GlobAgri_WRR
1. visualize_expansion_rasters.py: used to create images of 2010 - 2050 changes in agricultural land from expansion algorithm
