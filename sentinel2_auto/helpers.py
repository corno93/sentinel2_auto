

from osgeo import ogr, gdal
from math import *
from functools import wraps
from time import time

def timing(f):
    """
        Time methods convienently
    """
    @wraps(f)
    def wrapper(*args, **kwargs):

        start = time()
        result = f(*args, **kwargs)
        end = time()
        print 'Elapsed time: {time} for function {name}'.format(time=end-start, name=f.__name__)

        return result
    return wrapper




def get_epsg_code(lat, zone_num):
    """
        Returns the epsg code for a UTM zone.
        Kind of hacky but works
    """
    # begin epsg code with 327 if in the south
    if lat < 0:        
        epsg_code = str(327) + str(zone_num)

    # begin epsg code with 326 if in the south
    elif lat > 0:
        epsg_code = str(326) + str(zone_num)

    return epsg_code


def haversine_dist(coord1, coord2):
    """
        Calculate the great circle distance between two points on the earth (specified in decimal degrees)
        returns distance between points in km. 
    """
    # extract lats n lons
    lat1 = coord1[0]
    lon1 = coord1[1]
    lat2 = coord2[0]
    lon2 = coord2[1]
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    # Radius of earth in kilometers is 6371
    km = 6371* c

    return km




def resize_bands(band1, band2):
    """
        Function resizes the bands so they are the same size
        It will resize the smaller sized band to the larger sized band
    """
    band1_shape = band1.shape
    band2_shape = band2.shape

    if band1_shape > band2_shape:

        resized_band = cv2.resize(band2, (band1_shape[1], band1_shape[0]), interpolation=cv2.INTER_CUBIC)

    else:

        resized_band = cv2.resize(band1, (band2_shape[1], band2_shape[0]), interpolation=cv2.INTER_CUBIC)


    return resized_band


class MetadataExtraction(object):
    """
        Wrapper for handling exiftool for metadata extraction.
        Exiftool has been the best I have found so lets use it
    """
    def __init__(self, file_path):
        self.file_path = file_path
        self.exiftool_exe = "../bin/exiftool.exe"

    def extract_all_metadata(self):
        """
            Returns a dictionary with all found metadata fields as keys and their values
        """
        pass

    def extract_fields(self, fields):
        """
            Returns a dictionary with only the specified fields as keys and their values
        """
        pass


