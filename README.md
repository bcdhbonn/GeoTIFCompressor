# What is GeoTif Compressor

This code combines [gdal](https://gdal.org/) raster programs to lossy compress GeoTifs.
The compressed version of the GeoTif have round about 5% of the original size.

# Use of this code

You can either use the Python code or you can download a pre compiled version of the program [here](https://github.com/bcdhbonn/GeoTIFCompressor/releases/tag/BCDH)

Parameters:

| Parameter                       | Description |
|---------------------------------|---------------------------------------------------------------------------------------------------------|
| Import                          | location of image folder                                                                                |
| Output Folder                   | specify output file path                                                                                |
| Overwrite existing GeoTIFs      | replaces the original GeoTif with the compressed version                                                |
| Use Importh-Path as Output Path | loaction of imagefolder is the same as output file path                                                 |
| Create Image Pyramids           | Builds overview images with raster program [gdaladdo](https://gdal.org/programs/gdaladdo.html#gdaladdo) |