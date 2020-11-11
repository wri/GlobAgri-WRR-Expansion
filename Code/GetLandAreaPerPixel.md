This code was run using Google Earth Engine and can be found by following [this link](https://code.earthengine.google.com/0c3998022528806bed00e6aa7aa5e522).
The code is also copied below:

//Define geometry to export over
var rect = [-180, -90, 180, 90];
var bounds = ee.Geometry.Rectangle(rect,null,false);

//Get area per pixel as measured by Google Earth Engine
var proj = image.projection()
var pixel_area = ee.Image.pixelArea().reproject({
  crs:proj.crs(),
  crsTransform: proj.getInfo().transform
  })
//Convert from square meters per pixel to hectares per pixel
var pixel_area_ha = pixel_area.multiply(0.0001)

//Load in maximum land area from HYDE and convert from square kilometers
//per pixel to hectares per pixel 
var max_land = HYDE_maxland.select(['maxln_cr']).multiply(100)

//Define new variable defined as follows:
//Where HYDE does have data: final_pixel_area = max_land
//Where HYDE does not have data: final_pixel_area = pixel_area_ha
var max_land_mask = max_land.mask()
var hyde_max_land_unmask = max_land.unmask()
pixel_area_ha = pixel_area_ha.updateMask(max_land_mask.not())
pixel_area_ha = pixel_area_ha.unmask()
var final_pixel_area = pixel_area_ha.add(hyde_max_land_unmask)

//Export image
Export.image.toCloudStorage({
    image: final_pixel_area.unmask(),
    description: 'HydeLandPixelArea_ha',
    bucket: 'globagri-upload-bucket',
    fileNamePrefix: 'HydeLandPixelArea_ha',
    crs: proj.getInfo().crs,
    crsTransform: proj.getInfo().transform,
    region: bounds,
    maxPixels: 1e13
  });
