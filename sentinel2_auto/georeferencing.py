

from osgeo import gdal_array, gdal, ogr, osr
import os

def georeference_raster_to_ds(src_ds, raster, save_path=None, output_type="GTiff"):
    """
        Georeference a raster to a gdal dataset
        Input: gdal.Open object, np.array, output_type ('MEM' or 'GTiff'), save_path (string to directory for save)
        Output_type can be "GTiff" (locally saved geotiff), "MEM" (gdal.Open object in memory) ...

    """

    # get gdal data type (translates np dtypes to gdal's types)
    type_code = gdal_array.NumericTypeCodeToGDALTypeCode(raster.dtype)

    driver = gdal.GetDriverByName(output_type)

    # handle raster with many bands
    layers = 1
    if raster.ndim > 2:
        layers = raster.ndim


    # handle output types
    if output_type == "MEM":
        out_ds = driver.Create("", raster.shape[1], raster.shape[0], layers, type_code)#, ['COMPRESS=LZW'])   
        
    elif output_type == "GTiff":
        if not save_path:
            save_path = os.path.join(os.getcwd(), 'georeferenced.tif')
            
        out_ds = driver.Create(save_path, raster.shape[1], raster.shape[0], layers, type_code, ['COMPRESS=LZW'])    

    # if the raster has layers, add each separatly
    if raster.ndim > 2:

        for band in range (1, raster.ndim + 1):
            raster_band = raster[:, :, band-1]
            out_ds.GetRasterBand(band).WriteArray(raster_band)

    else:
        out_ds.GetRasterBand(1).WriteArray(raster)

    # add gis + metadata info
    out_ds.SetGeoTransform(src_ds.GetGeoTransform())
    out_ds.SetProjection(src_ds.GetProjection())
    out_ds.SetMetadata(src_ds.GetMetadata())



    if output_type == "MEM":
        return out_ds

    elif output_type == "GTiff":
        out_ds.FlushCache()
        del out_ds

