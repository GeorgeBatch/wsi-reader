import numpy as np
import re
import tifffile
import xml.etree.ElementTree as ET
import zarr

from fractions import Fraction
from os import PathLike
from typing import List, Optional, Tuple, Union

from .base import WSIReader


class TiffReader(WSIReader):
    """Implementation of the WSIReader interface backed by tifffile."""

    def __init__(self, slide_path: Union[PathLike, str], series: int = 0, **kwargs) -> None:
        """Open a slide. The object may be used as a context manager, in which case it will be closed upon exiting the context.

        Args:
            slide_path (Union[PathLike, str]): Path of the slide to open.
            series (int, optional): For multi-series formats, image series to open. Defaults to 0.
        """
        self.series = series
        self._store = tifffile.imread(str(slide_path), aszarr=True, series=series)
        self._z = zarr.open(self._store, mode="r")

    def close(self) -> None:
        """Close the slide.

        Returns:
            None
        """
        self._store.close()
        if hasattr(self, "_mpp"):
            delattr(self, "_mpp")
        if hasattr(self, "_tile_dimensions"):
            delattr(self, "_tile_dimensions")
        if hasattr(self, "_level_dimensions"):
            delattr(self, "_level_dimensions")
        if hasattr(self, "_level_downsamples"):
            delattr(self, "_level_downsamples")

    @property
    def tile_dimensions(self) -> List[Tuple[int, int]]:
        if not hasattr(self, "_tile_dimensions"):
            self._tile_dimensions = []
            for level in range(self.level_count):
                page = self._store._data[level].pages[0]
                self._tile_dimensions.append((page.tilewidth, page.tilelength))
        return self._tile_dimensions

    def _read_region(
        self, x_y: Tuple[int, int], level: int, tile_size: Tuple[int, int]
    ) -> Tuple[np.ndarray, np.ndarray]:
        x, y = x_y
        tile_w, tile_h = tile_size
        return self._z[level][y : y + tile_h, x : x + tile_w], np.ones(
            (tile_h, tile_w), bool
        )

    @property
    def level_dimensions(self) -> List[Tuple[int, int]]:
        if not hasattr(self, "_level_dimensions"):
            self._level_dimensions = []
            for level in range(self.level_count):
                page = self._store._data[level].pages[0]
                self._level_dimensions.append((page.imagewidth, page.imagelength))
        return self._level_dimensions

    @property
    def level_count(self) -> int:
        return len(self._z)

    @property
    def mpp(self) -> Tuple[Optional[float], Optional[float]]:
        if not hasattr(self, "_mpp"):
            self._mpp: Tuple[Optional[float], Optional[float]] = (None, None)
            page = self._store._data[0].pages[0]
            if page.is_svs:
                metadata = tifffile.tifffile.svs_description_metadata(page.description)
                self._mpp = (metadata["MPP"], metadata["MPP"])
            elif page.is_ome:
                root = ET.fromstring(page.description)
                namespace_match = re.search("^{.*}", root.tag)
                namespace = namespace_match.group() if namespace_match else ""
                pixels = list(root.findall(namespace + "Image"))[self.series].find(
                    namespace + "Pixels"
                )
                mpp_x = pixels.get("PhysicalSizeX") if pixels else None
                mpp_y = pixels.get("PhysicalSizeY") if pixels else None
                self._mpp = (
                    float(mpp_x) if mpp_x else None,
                    float(mpp_y) if mpp_y else None,
                )
            elif page.is_philips:
                root = ET.fromstring(page.description)
                mpp_attribute = root.find(
                    "./Attribute/[@Name='PIM_DP_SCANNED_IMAGES']/Array/DataObject/[@ObjectType='DPScannedImage']/Attribute/[@Name='PIM_DP_IMAGE_TYPE'][.='WSI']/Attribute[@Name='PIIM_PIXEL_DATA_REPRESENTATION_SEQUENCE']/Array/DataObject[@ObjectType='PixelDataRepresentation']/Attribute[@Name='DICOM_PIXEL_SPACING']"
                )
                mpp = (
                    float(mpp_attribute.text)
                    if mpp_attribute and mpp_attribute.text
                    else None
                )
                self._mpp = (mpp, mpp)
            elif page.is_ndpi or page.is_scn or page.is_qpi or True:
                page = self._store._data[0].pages[0]
                if (
                    "ResolutionUnit" in page.tags
                    and page.tags["ResolutionUnit"].value == 3
                    and "XResolution" in page.tags
                    and "YResolution" in page.tags
                ):
                    self._mpp = (
                        1e4 / float(Fraction(*page.tags["XResolution"].value)),
                        1e4 / float(Fraction(*page.tags["YResolution"].value)),
                    )
        return self._mpp

    @property
    def dtype(self) -> np.dtype:
        return self._z[0].dtype

    @property
    def n_channels(self) -> int:
        page = self._store._data[0].pages[0]
        return page.samplesperpixel
