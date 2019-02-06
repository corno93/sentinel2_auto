
from geoTiff import GeoTiff
import sys, os
import numpy as np
from georeferencing import georeference_raster_to_ds
from osgeo import gdal_array, gdal, ogr, osr


class Bands(object):

    def __init__(self, bands, resize = True, resize_shape=None):
        """
            Enter data source upon class initialisation
        """
        

        # this dictionary acts as the main datastructure for this class.
        # it stores all the GeoTiff objects for each inputted band. 
        # note that GeoTiff objects get overwritten when using the resize_bands method
        self.geotiff_objs = {}

        self.add_bands(bands, resize, resize_shape)




    def resize_bands(self, users_shape=None):
        """
            Resize all the bands. 
            If the user enters a shape size (height, width), then the bands will resize to that.
            If not, the bands will resize to the largest shape out of all of them.
            This resize method only resizes the image resolution, not the pixel resolution (TODO. easy add)
        """

        if not users_shape:

            # get largest shape
            resize_shape = max([i.raster_data_shape for _, i in self.geotiff_objs.iteritems()])

            # iterate and resize
            for band_name, geo_ds in self.geotiff_objs.iteritems():
                geo_ds.resize_band(resize_shape)

        else:

            # iterate and resize
            for band_name, geo_ds in self.geotiff_objs.iteritems():
                geo_ds.resize_band(users_shape)



    def resample_bands(self, fx, fy):
    	"""
    		Resample all the bands
    	"""
        # iterate and resample to fx, fy
        for band_name, geo_ds in self.geotiff_objs.iteritems():
            geo_ds.resample_band(fx, fy)



    def cut_bands_to_kml(self, kml_path):
        """
            Cut all the bands to a kml
        """

        if not os.path.isfile(kml_path):
            print "Kml with directory path %s does not exist!" % (kml_path)
            return

        # iterate and cut
        for band_name, geotiff in self.geotiff_objs.iteritems():
            self.geotiff_objs[band_name] = geotiff.cut_to_kml(kml_path)




    def save_bands(self, save_path = None):
        """
            Method saves the bandset locally.
            Use can specify save directory path.
        """
        if not save_path:
            save_path = os.path.join(os.getcwd(), "band_raster_.tif")


        if not stack:

            for band_name, geo_ds in self.geotiff_objs.iteritems():

                split_name = os.path.splitext(save_path)
                geo_ds.save_raster(split_name[0] + str(band_name) + split_name[1])



    def _check_available_indexs(self):
        """
            This method checks what indexs are available to produce.
            It will set the appropriate index flag to True
        """

        # inputted bands
        inputted_bands = [band for band, _ in self.geotiff_objs.iteritems()]

        # do the check
        if "B04" in inputted_bands and "B07" in inputted_bands or "red" in inputted_bands and "nir" in inputted_bands:
            self.ndvi_flag = True
        else:
            self.ndvi_flag = False

        if "B05" in inputted_bands and "B07" in inputted_bands or "rededge" in inputted_bands and "nir" in inputted_bands:
            self.ndre_flag = True
        else:
            self.ndre_flag = False

        if "B08" in inputted_bands and "B11" in inputted_bands:
            self.ndwi_flag = True
        else:
            self.ndwi_flag = False

        if "B02" in inputted_bands and "B03" in inputted_bands and "B04" in inputted_bands or "blue" in inputted_bands and "green" in inputted_bands and "red" in inputted_bands:
            self.rgb_flag = True
        else:
            self.rgb_flag = False





    def add_bands(self, bands, resize, resize_shape):
        """
            Method coordinates adding the bands for the dataset. 
            It recieves a dictionary where keys are band names and values are the band file path.
            Check that each file path exists.
            Check that each band name exists accordining to what datasource was selected.

            Then create a GeoTiff object for each band and store these in the self.geotiff_objs dictionary where
            keys are the band name. 

            Check what indexs can be computed. 

            Finally resize all bands to a specified shape or to the largest band size

        """

        for band_name, band_path in bands.iteritems():


            # make geotiff object and see if its been instantiated correctly or not
            geotiff = GeoTiff(geotiff_path=band_path)
            if not geotiff:
                print "Band %s has failed" % band_path
                continue
            else:
                print "Adding band %s" % band_path
                self.geotiff_objs[band_name] = geotiff

        self._check_available_indexs()

        if resize:
            self.resize_bands(resize_shape)
        else:
            print "Warning: bands of different shapes will result in an error"



    def compute_ndvi(self):
        """
            Method computes the NDVI vegetation index
            ndvi = (nir - red)/(nir + red)
            This method also checks that the user has inputted the correct bands for ndvi and will notify if otherwise
        """

        if not self.ndvi_flag:
            print "Computer says no ndvi because you have not entered the correct bands :("
            return

        num = self.geotiff_objs["B07"].raster_data.astype(float) - self.geotiff_objs["B04"].raster_data.astype(float)
        dom = self.geotiff_objs["B07"].raster_data.astype(float) + self.geotiff_objs["B04"].raster_data.astype(float)

        np.seterr(divide='ignore', invalid='ignore')
        ndvi_raster = np.true_divide(num, dom) 

        # create gdal ds for ndvi and then extract into GeoTiff class
        ndvi_gdal_obj = georeference_raster_to_ds(self.geotiff_objs["B07"].in_ds, ndvi_raster, output_type="MEM")
        self.geotiff_objs["ndvi"] = GeoTiff.geoTiff_factory(in_ds=ndvi_gdal_obj)

        # set mask 
        self.geotiff_objs["ndvi"].no_data_mask = dom == 0


        return self.geotiff_objs["ndvi"]



    def compute_ndre(self):
        """
            Method computes the NDRE vegetation index
            ndre = (nir - rededge)/(nir + rededge)
            This method also checks that the user has inputted the correct bands for ndre and will notify if otherwise
        """
        if not self.ndre_flag:
            print "Computer says no ndre because you have not entered the correct bands :("
            return

        num = self.geotiff_objs["B07"].raster_data.astype(float) - self.geotiff_objs["B05"].raster_data.astype(float)
        dom = self.geotiff_objs["B07"].raster_data.astype(float) + self.geotiff_objs["B05"].raster_data.astype(float)

        np.seterr(divide='ignore', invalid='ignore')
        ndre_raster = np.true_divide(num, dom)

        # create gdal ds for ndre and then extract into GeoTiff class
        ndre_gdal_obj = georeference_raster_to_ds(self.geotiff_objs["B07"].in_ds, ndre_raster, output_type="MEM")
        self.geotiff_objs["ndre"] = GeoTiff.geoTiff_factory(in_ds=ndre_gdal_obj)

        # set mask 
        self.geotiff_objs["ndre"].no_data_mask = dom == 0

        return self.geotiff_objs["ndre"]



    def compute_ndwi(self):
        """
            Method computes the NDWI vegetation index
            ndwi = (nir - swir)/(nir + swir)
            This method also checks that the user has inputted the correct bands for ndre and will notify if otherwise
            Original paper:
            http://ceeserver.cee.cornell.edu/wdp2/cee6150/Readings/Gao_1996_RSE_58_257-266_NDWI.pdf

            Use bands 8 and 11 to find changes of water in leaves
        """
        if not self.ndwi_flag:
            print "Computer says no ndwi because you have not entered the correct bands :("
            return


        num = self.geotiff_objs["B08"].raster_data.astype(float) - self.geotiff_objs["B11"].raster_data.astype(float)
        dom = self.geotiff_objs["B08"].raster_data.astype(float) + self.geotiff_objs["B11"].raster_data.astype(float)

        np.seterr(divide='ignore', invalid='ignore')
        self.ndwi_raster = np.true_divide(num, dom)

        # create gdal ds for ndre and then extract into GeoTiff class
        ndwi_gdal_obj = georeference_raster_to_ds(self.geotiff_objs["B08"].in_ds, self.ndwi_raster, output_type="MEM")
        self.geotiff_objs["ndwi"] = GeoTiff.geoTiff_factory(in_ds=ndwi_gdal_obj)

        # set mask 
        self.geotiff_objs["ndwi"].no_data_mask = dom == 0

        return self.geotiff_objs["ndwi"]



    def compute_rgb(self, save=False, save_path=None):
        """
            Method makes an rgb image.
            TODO: exposure adjustment, calculate average of 3 bands with wieghts
        """
        if not self.rgb_flag:
            print "Computer says no rgb because you have not entered the correct bands :("
            return

        self.rgb_raster = np.zeros((self.geotiff_objs["B2"].raster_data_shape[0], self.geotiff_objs["B2"].raster_data_shape[1], 3))

        self.rgb_raster[:,:,0] = self.geotiff_objs["B2"].raster_data 
        self.rgb_raster[:,:, 1] = self.geotiff_objs["B3"].raster_data 
        self.rgb_raster[:,:, 2] = self.geotiff_objs["B4"].raster_data 

        # create gdal ds for ndre and then extract into GeoTiff class
        rgb_gdal_obj = georeference_raster_to_ds(self.geotiff_objs["B2"].in_ds, self.rgb_raster, output_type="MEM")
        self.geotiff_objs["rgb"] = GeoTiff.geoTiff_factory(in_ds=rgb_gdal_obj)

        # set mask 
        self.geotiff_objs["rgb"].no_data_mask = dom == 0

        return self.geotiff_objs["rgb"]








