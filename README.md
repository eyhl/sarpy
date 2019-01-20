# sarpy

Open source libary for prossing SAR images as python objects. Should be easy and simple to use but still very flexible.

## vision/ideas for developing
* Install with conda-forge
* Open source
* Few dependencies (numpy, scipy, Gdal/rasterio, matplotlib,)
* Cython/c backend for function that requires to loop through the pixels.
* Mainly SAR Specific functions (Functions purely related to signal processing should be implemented in scipy or equivalent )
* Load data from Sentinel 1 (GRDH and SLC) & and other mission into sarpy object. Also load sarpy files
 * Easy access data as numpy.
 * Easy access meta data.
* A back-end of function operating on and returning nuedgempy arrays
* Version 2 ideas
  * A wrapper to use the functions in Q-Gis.
  * GPU compatible
* Function
  * Easy indexing and subset
  * Delete bands (important for memory manege)
  * Calibrate Sar images
  * Geo locate Sar images 
  * Apply orbit file (sentinel 1)
  * Save as Tiff files + meta data?
  * Simple Filters (Boxcar, Lee, ratio edge, VMR??, maybe also the temporal speckle filter)
  * Apply DEM
  * Coregister images
  * SLC, Convert to phase and amplitude
  * In-SAR, inferogram
  * In-SAR, coherence
  * SIMPLE plot fuctions
* Class to work with coregistred images as a time-series
