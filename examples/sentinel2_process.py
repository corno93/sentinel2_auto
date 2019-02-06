

"""
    Project: 
        sentinel2_auto

    Author:
        Alex Cornelio

    File:
        Example on how to process sentinel2 data using this repo

    Usage:
        python sentinel2_process.py

"""

import os, sys
from sentinel2_auto.bands import Bands



if __name__ == '__main__':


    kml = "/Users/lcornelio/code/sentinel2_auto/centennial_park.kml"
    
    bands_data = {
            "B05" : "/Users/lcornelio/code/sentinel2_auto/tiles_56_H_LH_S2A_MSIL1C_20190204T000241_N0207_R030_T56HLH_20190204T012019.SAFE_GRANULE_L1C_T56HLH_A018903_20190204T000237_IMG_DATA_T56HLH_20190204T000241_B05.jp2",
            "B07" : "/Users/lcornelio/code/sentinel2_auto/tiles_56_H_LH_S2A_MSIL1C_20190204T000241_N0207_R030_T56HLH_20190204T012019.SAFE_GRANULE_L1C_T56HLH_A018903_20190204T000237_IMG_DATA_T56HLH_20190204T000241_B07.jp2",
            "B04" : "/Users/lcornelio/code/sentinel2_auto/tiles_56_H_LH_S2A_MSIL1C_20190204T000241_N0207_R030_T56HLH_20190204T012019.SAFE_GRANULE_L1C_T56HLH_A018903_20190204T000237_IMG_DATA_T56HLH_20190204T000241_B04.jp2",
            "TCI" : "/Users/lcornelio/code/sentinel2_auto/tiles_56_H_LH_S2A_MSIL1C_20190204T000241_N0207_R030_T56HLH_20190204T012019.SAFE_GRANULE_L1C_T56HLH_A018903_20190204T000237_IMG_DATA_T56HLH_20190204T000241_TCI.jp2"
            }

    # add bands and resize all of them so they are the same size as the largest band (to avoid mis matching dimensions)
    sentinel_bands = Bands(bands_data)

    # cut kml
    sentinel_bands.cut_bands_to_kml(kml)

    # save tci
    sentinel_bands["tci"].save_raster(os.path.join(os.getcwd(), 'tci_gray.tif'))

    # compute and save gray and coloured ndvi, ndre, ndwi
    ndvi = sentinel_bands.compute_ndvi()
    ndvi.save_raster(os.path.join(os.getcwd(), 'ndvi_gray.tif'))
    ndvi.apply_colour_scale(os.path.join(os.getcwd(), 'ndvi_colour.tif'))

    ndre = sentinel_bands.compute_ndre()
    ndre.save_raster(os.path.join(os.getcwd(), 'ndre_gray.tif'))
    ndre.apply_colour_scale(os.path.join(os.getcwd(), 'ndre_colour.tif'))

    ndwi = sentinel_bands.compute_ndwi()
    ndwi.save_raster(os.path.join(os.getcwd(), 'ndwi_gray.tif'))
    ndwi.apply_colour_scale(os.path.join(os.getcwd(), 'ndwi_colour.tif'))



