import os, sys
from osgeo import gdal, ogr, osr
import utm
import numpy as np
import math
import helpers
from georeferencing import georeference_raster_to_ds
import matplotlib as mpl
mpl.use('TkAgg') 
import matplotlib.cm as cm




class GeoTiff(object):
    """
        Class for managing all geotiffs and gdal.Open data sets
    """
    def __init__(self, geotiff_path=None, in_ds=None):
        """
            Class recieves a path to a geotiff or a Gdal Open object in memory.
            Gdal variables will be extracted accordingly
        """
        self.img_name = None

        if geotiff_path:
            in_ds = gdal.Open(geotiff_path)

        # figure out if its wgs84 or utm projected and assign variables accordingly
        proj = in_ds.GetProjection()
        if proj == "":
            print "This input (%s, %s) is not a georeferenced datasource" % (geotiff_path, in_ds)
            self.geo_referenced = False
            return None

        # extract information 
        self.in_ds = in_ds
        self.projection = self.in_ds.GetProjection()
        self.raster_dtype = self.in_ds.GetRasterBand(1).ReadAsArray().dtype
        self.raster_count = self.in_ds.RasterCount
        self.raster_data = self._extract_raster_data(self.in_ds)
        self.raster_data_shape = self.raster_data.shape
        self.geo_transform = self.in_ds.GetGeoTransform()
        self.pixel_width = self.geo_transform[1]    # the units for this will depend on the projection
        self.pixel_height = abs(self.geo_transform[5])

        self.no_data_value = self._get_no_data_val()
        if self.no_data_value:
            self.no_data_mask = self._set_no_data_mask()
        else:
            self.no_data_mask = None


        if "utm" not in self.projection.lower():
            self.utm_proj = False
            self.lon = self.geo_transform[0]
            self.lat = self.geo_transform[3]
            self.easting, self.northing, self.zone_num, self.zone_letter = utm.from_latlon(self.lat, self.lon)
            self.pixel_width_m, self.pixel_height_m = self.find_gsd() 
            self.epsg_code_string = "EPSG:" + helpers.get_epsg_code(self.lat, self.zone_num)

        else:
            self.utm_proj = True
            self.easting = self.geo_transform[0]
            self.northing = self.geo_transform[3]
            self.pixel_width_m = self.pixel_width
            self.pixel_height_m = self.pixel_height

            self.zone_num, self.zone_letter = self._extract_utm_info()
            if self.zone_num is not None:
                self.lat, self.lon = utm.to_latlon(self.easting, self.northing, self.zone_num, self.zone_letter)
                self.epsg_code_string = "EPSG:" + helpers.get_epsg_code(self.lat, self.zone_num)
        
        self.geo_referenced = True
        self.geotiff_path = geotiff_path
        if self.geotiff_path:
            self.img_name = os.path.basename(self.geotiff_path)
        else:
            self.img_name = str(self.in_ds)[76:89] # get the objects memory address - dangerous hardcoding but seems consistent



    def _update_vars(self, in_ds):
        """
            Method to refresh class variables after resampling/reprojecting.
        """
        self.in_ds = in_ds
        self.projection = self.in_ds.GetProjection()
        self.raster_data = self._extract_raster_data(self.in_ds)
        self.raster_data_shape = self.raster_data.shape
        self.geo_transform = self.in_ds.GetGeoTransform()
        self.pixel_width = self.geo_transform[1]    # the units for this will depend on the projection
        self.pixel_height = abs(self.geo_transform[5])

        if "utm" not in self.projection.lower():
            self.utm_proj = False
            self.lon = self.geo_transform[0]
            self.lat = self.geo_transform[3]
            self.pixel_width_m, self.pixel_height_m = self.find_gsd()

        else:
            self.utm_proj = True
            self.easting = self.geo_transform[0]
            self.northing = self.geo_transform[3]
            self.pixel_width_m = self.pixel_width
            self.pixel_height_m = self.pixel_height
        
    def __new__(cls, geotiff_path=None, in_ds=None):
        """
            Do checks on the input file - ensure it exists and that its georeferenced.
            If not, return None
        """
        if geotiff_path:

            # check if file exists
            if not os.path.isfile(geotiff_path):
                print "The file %s does not exist!" % (geotiff_path)
                return None

            in_ds = gdal.Open(geotiff_path)

        if in_ds:

            # check if its georeferenced
            if in_ds.GetProjection() == "":
                print "The file %s is not georeferenced!" % (geotiff_path)
                return None

            # create the class
            return super(GeoTiff, cls).__new__(cls, in_ds=in_ds)

        print "Well enter something...the geotiff path or a Gdal datasource object"
        return None


    def __hash__(self):
        """
            Hash the class for storage 
        """
        return hash(self.raster_data)

        
    def __eq__(self, other):
        """
            Compare two instances
        """
        return (self.raster_data == other.raster_data).all()


    def __repr__(self):
        """
            Display the object nicely when its printed
        """
        if not self.img_name:
            return None
        return "GeoTiff_obj_" + self.img_name




    def _set_no_data_mask(self):
        """
            Method sets a no data mask.
            The mask will be a boolean np array, where True indicates the pixel to mask out
        """
        return self.raster_data == self.no_data_value



    def _extract_utm_info(self):
        """
            Method extracts the zone_num and zone_letter from a gdal projection string
            This method is only called when the projection is in utm
            Ugly method 
        """
        try:
            temp = self.projection.split("UTM zone ")[1][:4]
            zone_num = ""
            zone_letter = ""
            for i in temp:

                if i.isdigit():
                    zone_num += i
                elif i.isalpha():
                    zone_letter += i

            return int(zone_num), zone_letter

        except Exception as e:
            print (e)
            return None, None



    def apply_colour_scale(self, save_path):
        """
            Apply a colour scale to a black and white image
            Input: directory to save the coloured image
            Return: None (saves file locally)

        """

        # shift from -1 - 1 to 0 - 1
        normalised_index = self.raster_data + 1.0
        normalised_index = normalised_index / 2.0

        # stretch data to 0.4% and 99.6% quartiles for maximum variation in the image
        minindex = np.nanpercentile(self.raster_data, 0.4)
        maxindex = np.nanpercentile(self.raster_data, 99.6)
        self.raster_data = (normalised_index - minindex) / (maxindex - minindex) 

        cmap = cm.get_cmap('RdYlGn')
        index_rgb = cmap(normalised_index)
        index_red = (index_rgb[:,:,0]*255).astype(np.uint8)     
        index_green = (index_rgb[:,:,1]*255).astype(np.uint8)
        index_blue = (index_rgb[:,:,2]*255).astype(np.uint8)

        # apply a no data mask if one exists
        if isinstance(self.no_data_mask, np.ndarray):
            index_blue[self.no_data_mask] = 255
            index_green[self.no_data_mask] = 255
            index_red[self.no_data_mask] = 255

        coloured = np.zeros((self.raster_data.shape[0], self.raster_data.shape[1], 3)).astype("uint8")
        coloured[:, :, 0] = index_blue
        coloured[:, :, 1] = index_green
        coloured[:, :, 2] = index_red

        # store back in raster data
        self.raster_data = coloured
        self.raster_count = 3
        georeference_raster_to_ds(self.in_ds, coloured, output_type="GTiff", save_path=save_path)



    @helpers.timing
    def save_raster(self, save_path=None):
        """
            Save the raster locally.
        """
        if not save_path:
            save_path = os.path.splitext(self.geotiff_path)[0] + "_raster.tif"

        gdal.Warp(save_path, self.in_ds, format='GTiff')



    def _get_no_data_val(self):
        """
            Extract the no data value of a dataset
        """
        return self.in_ds.GetRasterBand(1).GetNoDataValue()


    def _extract_raster_data(self, ds):
        """
            Extract all raster data for inputted geotiff.
            Return a list of numpy arrays
        """

        # sample the first band to get the shape and then preallocate knowing raster_count
        raster_shape = ds.GetRasterBand(1).ReadAsArray().astype(self.raster_dtype).shape
        raster_data = np.zeros((raster_shape[0], raster_shape[1], self.raster_count))

        if self.raster_count > 1:

            for band_idx in range(1, self.raster_count + 1):
                raster_data[:, :, band_idx - 1] = ds.GetRasterBand(band_idx).ReadAsArray().astype(self.raster_dtype)

        else:

            raster_data = ds.GetRasterBand(1).ReadAsArray().astype(self.raster_dtype)

        return raster_data


    def gps_coord_transform(self, pixel_coord):
        """
            Find the gps coordinate at a pixel by computing an affine transform
        """
 
        Xpixel = pixel_coord[1]
        Yline = pixel_coord[0]
        Xgeo = self.geo_transform[0] + Xpixel*self.geo_transform[1] + Yline*self.geo_transform[2]
        Ygeo = self.geo_transform[3] + Xpixel*self.geo_transform[4] + Yline*self.geo_transform[5]
        return (Ygeo, Xgeo)



    def find_gsd(self):
        """
            Find the gsd in meters. This function has been used so we dont need to reproject with gdal to find the
            gsd in meters - making this process alot faster
            It saves the pixel width and height in meters as class variables
        """

        # find gps coordiante of next pixel to the right and bottom
        gps_right = self.gps_coord_transform((0, 1))
        gps_bottom = self.gps_coord_transform((1, 0))

        # calc haversine dist of both, return pixel width and height in meters
        pixel_width_m = helpers.haversine_dist(gps_right, (self.lat, self.lon))*1000
        pixel_height_m = helpers.haversine_dist(gps_bottom, (self.lat, self.lon))*1000 

        return pixel_width_m, pixel_height_m



    def resize_band(self, shape, projection="wgs84"):
        """
            Resize the band to a image size.
            Then overwrite current gdal variables
        """
        resized_ds = gdal.Warp('', self.in_ds, format='MEM', width=shape[1], height=shape[0], dstSRS='EPSG:4326', resampleAlg="cubic")#, dstSRS='EPSG:4326')

        self._update_vars(resized_ds)


    def resample_band(self, fx, fy):
        """
            Resample the band to a pixel size in meters
            Then overwrite current gdal variables
            Gdal interpolation algs include: None (nearest neighbour),bilinear,cubic,cubicspline,lanczos,average,mode

            Inputs: fx (pixel width), fy (pixel hieght)
        """

        # if the projection is not in utm, scale the inputted fx and fy from meters to decimal degrees
        if not self.utm_proj:
            fx = float(fx / self.pixel_width_m) * self.pixel_width
            fy = float(fy / self.pixel_height_m) * self.pixel_height

        resampled_ds = gdal.Warp('', self.in_ds, format='MEM', xRes=fx, yRes=fy, resampleAlg=None)

        self._update_vars(resampled_ds)


    @helpers.timing
    def cut_to_kml(self, kml_path, output_type = 'MEM', save_path=None):
        """
            Cut a raster to a kml.
            Then overwrite current gdal variables.
            Warning: kmls are super annoying and this function has proved quite problematic if the kml is not in the right
            format and if there are too many nests in the kml's structure.
            If you ever do have a problem ensure that the kml has the same structure as the one included in the examples directory
            Inputs: path to the kml
        """

        if not os.path.isfile(kml_path):
            print "Kml with directory path %s does not exist!" % (kml_path)
            return

        if save_path:
            gdal.Warp(save_path, self.in_ds, format='GTiff', cutlineDSName=kml_path, cropToCutline=True)


        if not save_path:
            # hack - unfortunetly cannot get the cropToCutLine to work when saving to memory...
            gdal.Warp(os.path.join(os.getcwd(), 'cut.tif'), self.in_ds, format='GTiff', cutlineDSName=kml_path, cropToCutline=True)
            return self.geoTiff_factory(os.path.join(os.getcwd(), 'cut.tif'))




    def _extract_geo_info(self, in_ds):
        """
            Helper method to extract all info from gdal open object
            This has been made into a method because all these variables need to re-written
            everytime the GeoTiff object resamples, resizes
        """
        self.in_ds = in_ds
        self.projection = in_ds.GetProjection()
        self.raster_dtype = in_ds.GetRasterBand(1).ReadAsArray().dtype
        self.raster_count = in_ds.RasterCount
        self.raster_data = self._extract_raster_data(in_ds)
        self.raster_data_shape = self.raster_data.shape
        self.geo_transform = self.in_ds.GetGeoTransform()
        self.pixel_width = self.geo_transform[1]
        self.pixel_height = abs(self.geo_transform[5])
        self.lon = self.geo_transform[0]
        self.lat = self.geo_transform[3]
        self.find_gsd()



    @staticmethod
    def geoTiff_factory(geoTiff=None, in_ds=None):
        """
            Method returns a GeoTiff object for some gdal Open input data source.
            This is useful when we've created an object in code that we wish to wrap into this class
        """
        return GeoTiff(geoTiff, in_ds)




    def change_projection(self, EPSG):
        """
            Change the geotiffs projection to whatever is specified
        """
        reproj_ds = gdal.Warp('', self.in_ds, format='MEM', dstSRS=EPSG)
        self._update_vars(reproj_ds)




    @staticmethod
    def factory(geotiffs):
        """
            Return a list of GeoTiff objects for a list of geotiff directory paths
        """
        return [GeoTiff(geotiff) for geotiff in geotiffs]









