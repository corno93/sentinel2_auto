# sentinel2_auto

This repository enables users to quickly process [sentinel 2's](https://en.wikipedia.org/wiki/Sentinel-2) multispectral bands to produce [vegetation indices](https://phenology.cr.usgs.gov/ndvi_foundation.php). 
All sentinel2 data is publically available on the [Google Cloud Platform](https://cloud.google.com/storage/docs/public-datasets/sentinel-2).

For example:


![Demo Animation](../assets/example.png?raw=true)


Here Sentinel2's TCI image is on the left, the middle is NDVI and the right is NDRE.

## How to download your data

- Create kml of the area of land you wish to inspect. This can easily be done using Google Earth Pro.
- Knowing the latitude and longtitude of your area, figure out the UTM and MGRS coordinates. Simply do this by using this [site](http://www.legallandconverter.com/p50.html)
- Download the sentinel 2 tiles for your desired date by using this [site](https://console.cloud.google.com/storage/browser/gcp-public-data-sentinel-2/tiles). Ensure you have followed the correct tile formatting of ```/tiles/[UTM_ZONE]/[LATITUDE_BAND]/[GRID_SQUARE]/[GRANULE_ID]/...```. Here ```GRID_SQUARE``` and ```GRANDULE_ID``` are from the MGRS coordinate system.


## Dependencies
- Python2.7
- Gdal. If you are using Anaconda, I recommend installing this [one](https://anaconda.org/conda-forge/gdal)
- utm
- matplotlib
- This repo! Run at this repositry's root directory: ```pip install .``` (ensure above dependencies are already installed in your environment)


## How to run the code

See the examples/sentinel2_process.py script as an example.

Simply run this script (in your python environment) by: ```python sentinel2_process.py```


Additionally, automate generating indicies for several sets of data using the examples/sentinel2_automation.py script. 
After setting the base path to the sets of sentinel2 imagery, run this script (in your python environment) by: ```python sentinel2_automation.py```





## Class descriptions and methods

**Class GeoTiff is intended to be used anytime you have to do work with a geotiff.**

Upon class instantiation, all class variables are found regardless of projection.
Important class variables include: the gdal.Open object, projection, raster_data, geo_transform, pixel width (projection's native units), pixel height (projection's native units), no_data_value, no_data_mask, longtitude, latitude, easting, northing, zone number, zone letter, pixel width meters, pixel height meters, epsg code string. 

Methods include:
- find_gsd()
- resize_band()
- resample_band()
- cut_to_kml()
- change_projection()
- save_raster()


**Class Bands is intended to be used anytime you have a set of bands and you wish to compute indicies.**

The main variable is a dictionary that acts as a data structure for holding each band name as a key and its value been a GeoTiff object of that band. In this way, all the methods from GeoTiff can be called on each inputted band.
The name of the variable is self.geotiff_objs.

Methods include:
- resize_bands()
- resample_bands()
- cut_bands_to_kml()
- save_bands()
- compute_ndvi()
- compute_ndre()
- compute_ndwi()
- compute_rgb()

