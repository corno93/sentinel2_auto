"""
    Project: 
        sentinel2_auto

    Author:
        Alex Cornelio

    File:
        Tests for the GeoTiff class

    Tests:

        Resampling
        Reprojecting
        Kml cutting
        Georeferencing and saving
        Applying colourscale

"""

from sentinel2_auto.geoTiff import GeoTiff
from sentinel2_auto.georeferencing import georeference_raster_to_ds
import unittest
import os





file = "test_TCI.jp2"
kml = "test.kml"


class TestSentinel2AutoMethods(unittest.TestCase):


    def setUp(self):
        """
            Create the GeoTiff object
        """
        self.geotiff = GeoTiff(file)
        self.cut_img_path = os.path.join(os.getcwd(), 'cut_img.tif')
        self.georeferenced_img_path = os.path.join(os.getcwd(), 'georeferenced.tif')
        self.coloured_path = os.path.join(os.getcwd(), 'coloured.tif')

    
    def test_resample(self):
        """
            Test the resampling
        """
        self.geotiff.resample_band(5,5)
        self.assertAlmostEqual(self.geotiff.pixel_width_m, 5)
        self.assertAlmostEqual(self.geotiff.pixel_height_m, 5)



    def test_reprojecting(self):
        """
            Test the reprojecting. Reproject to UTM for convienence and check that utm_proj flag was set to True
        """
        desired_proj = self.geotiff.epsg_code_string

        self.geotiff.change_projection(desired_proj)
        self.assertTrue(self.geotiff.utm_proj)



    def test_kml_cut(self):
        """
            Ensuring the kml cutting works
        """
        self.geotiff.cut_to_kml(kml, save_path=self.cut_img_path)
        self.assertTrue(os.path.exists(self.cut_img_path))


        before = self.geotiff.raster_data_shape
        self.cut_img = self.geotiff.cut_to_kml(kml)
        after = self.cut_img.raster_data_shape
        print "Before cut: ", before
        print "After cut: ", after
        self.assertTrue(self.cut_img.raster_data_shape==(103, 104, 3))
         


    def test_georeferencing_and_saving(self):
        """
            Test georeferencing some non geo data and saving it
        """
        cut_img = GeoTiff(self.cut_img_path)
        single_band = cut_img.raster_data[:, :, 1]

        # georeference it
        georeference_raster_to_ds(cut_img.in_ds, single_band, save_path = self.georeferenced_img_path, output_type = "GTiff")
        self.assertTrue(os.path.exists(self.georeferenced_img_path))

        geoImg = GeoTiff(self.georeferenced_img_path)
        self.assertTrue(geoImg.geo_referenced)


    def test_colourscale(self):
        """
            Apply a colourscale to the black and white band and save it and check georeferencing
        """
        

        geotiff = GeoTiff(self.georeferenced_img_path)
        geotiff.apply_colour_scale(self.coloured_path)
        self.assertTrue(os.path.exists(self.coloured_path))


        geoImg = GeoTiff(self.coloured_path)
        self.assertTrue(geoImg.geo_referenced)        




if __name__ == '__main__':


    suite = unittest.TestLoader().loadTestsFromTestCase(TestSentinel2AutoMethods)
    unittest.TextTestRunner(verbosity=2).run(suite)



