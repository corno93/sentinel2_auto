

"""
    Project: 
        sentinel2_auto

    Author:
        Alex Cornelio

    File:
        Automate indice generation

    Usage:
        Run this script with a PATH at a a base directory where there are subdirectories filled with sentinel2 data

"""


from sentinel2_auto.bands import Bands
import os,sys




PATH = os.getcwd()


def collate_bands(path):
    """
        Collate all the bands in sub directories from the PATH.
        Assume all directories in path have sentinel 2 data
        Input: root dir
        Return: list of dictionaries where each dict has {"B1":<path>, "B2":<path>, etc}
    """

    collated_bands = []

    for dirname, dirnames, filenames in os.walk(path):

        for subdirname in dirnames:

            subdirname_path = os.path.join(path, subdirname)

            bands = {}

            for file in os.listdir(subdirname_path):

                if "B01" in file:
                    bands["B01"] = os.path.join(subdirname_path, file)

                elif "B02" in file:
                    bands["B03"] = os.path.join(subdirname_path, file)

                elif "B03" in file:
                    bands["B03"] = os.path.join(subdirname_path, file)

                elif "B04" in file:
                    bands["B04"] = os.path.join(subdirname_path, file)

                elif "B05" in file:
                    bands["B05"] = os.path.join(subdirname_path, file)

                elif "B06" in file:
                    bands["B06"] = os.path.join(subdirname_path, file)

                elif "B07" in file:
                    bands["B07"] = os.path.join(subdirname_path, file)

                elif "B08" in file:
                    bands["B08"] = os.path.join(subdirname_path, file)

                elif "B8A" in file:
                    bands["B8A"] = os.path.join(subdirname_path, file)

                elif "B09" in file:
                    bands["B09"] = os.path.join(subdirname_path, file)

                elif "B10" in file:
                    bands["B10"] = os.path.join(subdirname_path, file)

                elif "B11" in file:
                    bands["B11"] = os.path.join(subdirname_path, file)

                elif "B12" in file:
                    bands["B12"] = os.path.join(subdirname_path, file)

                elif "TCI" in file:
                    bands["TCI"] = os.path.join(subdirname_path, file)


            collated_bands.append(bands)

        break

    return collated_bands




def generate_indicies(bands):
    """
        Input: dictionary
        Output: saved gray and colour of indices
    """

    sentinel_bands = Bands(bands)


    # get path to subdirectory - bit hacky
    path = os.path.sep + os.path.sep.join(bands["B01"].strip(os.path.sep).split(os.path.sep )[:-1])

    ndwi = sentinel_bands.compute_ndwi()
    ndwi_path_gray = os.path.join(path, 'ndwi_gray.tif')
    ndwi.save_raster(ndwi_path_gray)

    ndwi_path = os.path.join(path, 'ndwi_colour.tif')
    ndwi.apply_colour_scale(ndwi_path)


    ndvi = sentinel_bands.compute_ndvi()
    ndvi_path_gray = os.path.join(path, 'ndvi_gray.tif')
    ndvi.save_raster(ndvi_path_gray)

    ndvi_path = os.path.join(path, 'ndvi_colour.tif')
    ndvi.apply_colour_scale(ndvi_path)



if __name__ == '__main__':


    collated_bands = collate_bands(PATH)
    print "FOUND %d PATHS" % len(collated_bands)

    for bands in collated_bands:

        generate_indicies(bands)

    