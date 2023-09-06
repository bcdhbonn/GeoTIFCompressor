# What is GeoTif Compressor

This code converts a GeoTif in rgb format to about 5% of its original size by combining [gdal](https://gdal.org/) raster programs.
The original ground sampling distance is kept. However, fuzzy image edges may occur due to the applied jpeg lossy compression.
All meta data information is transferred. Image pyramids can be created and stored internally in the image.
The original file will not be overwritten if not explicitly defined.

# Use of this code

You can either use the Python code or you can download a pre compiled version of the program [here](https://github.com/bcdhbonn/GeoTIFCompressor/releases/tag/BCDH).

Parameters:

| Parameter                       | Description |
|---------------------------------|---------------------------------------------------------------------------------------------------------|
| Import                          | location of image folder                                                                                |
| Output Folder                   | specify output file path                                                                                |
| Overwrite existing GeoTIFs      | replaces the original GeoTif with the compressed version                                                |
| Use Importh-Path as Output Path | loaction of image folder is the same as output file path                                                |
| Create Image Pyramids           | Builds overview images with raster program [gdaladdo](https://gdal.org/programs/gdaladdo.html#gdaladdo) |