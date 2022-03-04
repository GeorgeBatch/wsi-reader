# wsi_reader package

wsi-reader is a format-independent WSI reader. The API is designed to be similar to openslide.

Backends based on the following libraries are available: tifffile, openslide and the Philips pathology SDK.
The reader works with all the image formats supported by the installed backends.

To install the package from the latest master with a desired backend (e.g. tifffile) use the following command:

> pip install "wsi-reader[tifffile] @ https://github.com/stefano-malacrino/wsi-reader.git"


### wsi_reader.get_wsi_reader(slide_path: Union[os.PathLike, str])
Return a class implementing WSIReader interface based on the image file extension or None if no suitable implementation is found.


* **Parameters**

    **slide_path** (*Union**[**PathLike**, **str**]*) – Path of the image file.



* **Returns**

    Reader class.



* **Return type**

    Optional[Type[WSIReader]]


## Submodules

## wsi_reader.base module


### _class_ wsi_reader.base.WSIReader()
Bases: `object`

Interface class for a WSI reader.


#### _abstract_ close()
Close the slide.


* **Returns**

    None



#### _abstract property_ dtype(_: numpy.dtyp_ )
Numpy data type of the slide pixels.


* **Returns**

    Pixels data type.



* **Return type**

    np.dtype



#### get_best_level_for_downsample(downsample: float)
Return the best level for the given downsample factor.


* **Parameters**

    **downsample** (*float*) – the downsample factor.



* **Returns**

    the level.



* **Return type**

    int



#### get_dimensions_for_downsample(downsample: float)
Return the slide dimensions for for a given fownsample factor.


* **Parameters**

    **downsample** (*float*) – downsample factor.



* **Returns**

    slide dimensions for the given downsample factor as a tuple (width, height).



* **Return type**

    Tuple[int, int]



#### get_downsampled_slide(dims: Tuple[int, int], normalize: bool = True)
Return a downsampled version of the slide with the given dimensions.


* **Parameters**

    
    * **dims** (*Tuple**[**int**, **int**]*) – size of the downsampled slide asa (width, height) tuple.


    * **normalize** (*bool**, **optional*) – True to normalize the pixel values in therange [0,1]. Defaults to True.



* **Returns**

    tuple of pixel data and alpha mask of the downsampled slide.



* **Return type**

    Tuple[np.ndarray, np.ndarray]



#### _abstract property_ level_count(_: in_ )
Number of levels in the slide.


#### _abstract property_ level_dimensions(_: List[Tuple[int, int]_ )
Slide dimensions for each slide level as a list of (width, height) tuples.


#### _property_ level_downsamples(_: List[float_ )
Return a list of downsample factors for each level of the slide.


* **Returns**

    The list of downsample factors.



* **Return type**

    List[float]



#### _abstract property_ mpp(_: Tuple[Optional[float], Optional[float]_ )
A tuple containing the number of microns per pixel of level 0 in the X and Y dimensions respectively, if known.


#### _abstract property_ n_channels(_: in_ )
Number of channels in the slide.


* **Returns**

    Number of channels.



* **Return type**

    int



#### read_region(x_y: Tuple[int, int], level: int, tile_size: Union[Tuple[int, int], int], normalize: bool = True, downsample_level_0: bool = False)
Reads the contens of the specified region in the slide from the given level.


* **Parameters**

    
    * **x_y** (*Tuple**[**int**, **int**]*) – coordinates of the top left pixel of the region in the given level reference frame.


    * **level** (*int*) – the desired level.


    * **tile_size** (*Union**[**Tuple**[**int**, **int**]**, **int**]*) – size of the region. Can be a tuple in the format (width, height) or a single scalar to specify a square region.


    * **normalize** (*bool**, **optional*) – True to normalize the pixel values in therange [0,1]. Defaults to True.


    * **downsample_level_0** (*bool**, **optional*) – True to render the region by downsampling from level 0. Defaults to False.



* **Returns**

    tuple of pixel data and alpha mask of the specified region.



* **Return type**

    Tuple[np.ndarray, np.ndarray]



#### read_region_ds(x_y: Tuple[int, int], downsample: float, tile_size: Union[Tuple[int, int], int], normalize: bool = True, downsample_level_0: bool = False)
Reads the contens of the specified region in the slide for the given downsample factor.


* **Parameters**

    
    * **x_y** (*Tuple**[**int**, **int**]*) – coordinates of the top left pixel of the region in the given downsample factor reference frame.


    * **downsample** (*float*) – the desired downsample factor.


    * **tile_size** (*Union**[**Tuple**[**int**, **int**]**, **int**]*) – size of the region. Can be a tuple in the format (width, height) or a single scalar to specify a square region.


    * **normalize** (*bool**, **optional*) – True to normalize the pixel values in therange [0,1]. Defaults to True.


    * **downsample_level_0** (*bool**, **optional*) – True to render the region by downsampling from level 0. Defaults to False.



* **Returns**

    tuple of pixel data and alpha mask of the specified region.



* **Return type**

    Tuple[np.ndarray, np.ndarray]



#### _abstract property_ tile_dimensions(_: List[Tuple[int, int]_ )
Tile dimensions for each slide level as a list of (width, height) tuples.

## wsi_reader.openslide_backend module


### _class_ wsi_reader.openslide_backend.OpenslideReader(slide_path: Union[os.PathLike, str], \*\*kwargs)
Bases: `wsi_reader.base.WSIReader`

Implementation of the WSIReader interface backed by openslide


#### \__init__(slide_path: Union[os.PathLike, str], \*\*kwargs)
Open a slide. The object may be used as a context manager, in which case it will be closed upon exiting the context.


* **Parameters**

    **slide_path** (*Union**[**PathLike**, **str**]*) – Path of the slide to open.



#### close()
Close the slide.


* **Returns**

    None



#### _property_ dtype(_: numpy.dtyp_ )
Numpy data type of the slide pixels.


* **Returns**

    Pixels data type.



* **Return type**

    np.dtype



#### get_best_level_for_downsample(downsample: float)
Return the best level for the given downsample factor.


* **Parameters**

    **downsample** (*float*) – the downsample factor.



* **Returns**

    the level.



* **Return type**

    int



#### _property_ level_count(_: in_ )
Number of levels in the slide.


#### _property_ level_dimensions(_: List[Tuple[int, int]_ )
Slide dimensions for each slide level as a list of (width, height) tuples.


#### _property_ level_downsamples(_: List[float_ )
Return a list of downsample factors for each level of the slide.


* **Returns**

    The list of downsample factors.



* **Return type**

    List[float]



#### _property_ mpp(_: Tuple[Optional[float], Optional[float]_ )
A tuple containing the number of microns per pixel of level 0 in the X and Y dimensions respectively, if known.


#### _property_ n_channels(_: in_ )
Number of channels in the slide.


* **Returns**

    Number of channels.



* **Return type**

    int



#### _property_ tile_dimensions(_: List[Tuple[int, int]_ )
Tile dimensions for each slide level as a list of (width, height) tuples.

## wsi_reader.philips_backend module


### _class_ wsi_reader.philips_backend.IsyntaxReader(slide_path: Union[os.PathLike, str], cache_path: Optional[Union[os.PathLike, str]] = None, generate_cache=False, \*\*kwargs)
Bases: `wsi_reader.base.WSIReader`

Implementation of the WSIReader interface for the isyntax format backed by the Philips pathology SDK.


#### \__init__(slide_path: Union[os.PathLike, str], cache_path: Optional[Union[os.PathLike, str]] = None, generate_cache=False, \*\*kwargs)
Open a slide. The object may be used as a context manager, in which case it will be closed upon exiting the context.


* **Parameters**

    
    * **slide_path** (*Union**[**PathLike**, **str**]*) – Path of the slide to open.


    * **cache_path** (*Optional**[**Union**[**PathLike**, **str**]**]**, **optional*) – Path to the cache file for the image. If it’s a path to a folder the file name is assumed to be the same as the image.  If None sets the path to the directory where the image is stored. If generate_cache is False and the cache file doesn’t exist caching is disabled. Defaults to None.


    * **generate_cache** (*bool**, **optional*) – If True create the cache file if not present. Defaults to False.



#### close()
Close the slide.


* **Returns**

    None



#### _property_ dtype(_: numpy.dtyp_ )
Numpy data type of the slide pixels.


* **Returns**

    Pixels data type.



* **Return type**

    np.dtype



#### _property_ level_count(_: in_ )
Number of levels in the slide.


#### _property_ level_dimensions(_: List[Tuple[int, int]_ )
Slide dimensions for each slide level as a list of (width, height) tuples.


#### _property_ level_downsamples(_: List[float_ )
Return a list of downsample factors for each level of the slide.


* **Returns**

    The list of downsample factors.



* **Return type**

    List[float]



#### _property_ mpp(_: Tuple[Optional[float], Optional[float]_ )
A tuple containing the number of microns per pixel of level 0 in the X and Y dimensions respectively, if known.


#### _property_ n_channels(_: in_ )
Number of channels in the slide.


* **Returns**

    Number of channels.



* **Return type**

    int



#### _property_ tile_dimensions(_: List[Tuple[int, int]_ )
Tile dimensions for each slide level as a list of (width, height) tuples.

## wsi_reader.tifffile_backend module


### _class_ wsi_reader.tifffile_backend.TiffReader(slide_path: Union[os.PathLike, str], series: int = 0, \*\*kwargs)
Bases: `wsi_reader.base.WSIReader`

Implementation of the WSIReader interface backed by tifffile.


#### \__init__(slide_path: Union[os.PathLike, str], series: int = 0, \*\*kwargs)
Open a slide. The object may be used as a context manager, in which case it will be closed upon exiting the context.


* **Parameters**

    
    * **slide_path** (*Union**[**PathLike**, **str**]*) – Path of the slide to open.


    * **series** (*int**, **optional*) – For multi-series formats, image series to open. Defaults to 0.



#### close()
Close the slide.


* **Returns**

    None



#### _property_ dtype(_: numpy.dtyp_ )
Numpy data type of the slide pixels.


* **Returns**

    Pixels data type.



* **Return type**

    np.dtype



#### _property_ level_count(_: in_ )
Number of levels in the slide.


#### _property_ level_dimensions(_: List[Tuple[int, int]_ )
Slide dimensions for each slide level as a list of (width, height) tuples.


#### _property_ mpp(_: Tuple[Optional[float], Optional[float]_ )
A tuple containing the number of microns per pixel of level 0 in the X and Y dimensions respectively, if known.


#### _property_ n_channels(_: in_ )
Number of channels in the slide.


* **Returns**

    Number of channels.



* **Return type**

    int



#### _property_ tile_dimensions(_: List[Tuple[int, int]_ )
Tile dimensions for each slide level as a list of (width, height) tuples.
