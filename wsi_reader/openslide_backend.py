import numpy as np
import openslide 

from os import PathLike
from typing import List, Optional, Tuple, Union

from .base import WSIReader

class OpenslideReader(WSIReader):
    """Implementation of the WSIReader interface backed by openslide"""

    def __init__(self, slide_path: Union[PathLike, str], **kwargs) -> None:
        """Open a slide. The object may be used as a context manager, in which case it will be closed upon exiting the context.

        Args:
            slide_path (Union[PathLike, str]): Path of the slide to open.
        """
        self._slide = openslide.open_slide(str(slide_path))

    def close(self) -> None:
        self._slide.close()
        if hasattr(self, "_tile_dimensions"):
            delattr(self, "_tile_dimensions")

    def _read_region(
        self, x_y: Tuple[int, int], level: int, tile_size: Tuple[int, int]
    ) -> Tuple[np.ndarray, np.ndarray]:
        tile = np.array(self._slide.read_region(x_y, level, tile_size), dtype=np.uint8)
        alfa_mask = tile[:, :, 3] > 0
        tile = tile[:, :, :3]
        return tile, alfa_mask

    def get_best_level_for_downsample(self, downsample: float) -> int:
        return self._slide.get_best_level_for_downsample(downsample)

    @property
    def level_dimensions(self) -> List[Tuple[int, int]]:
        return self._slide.level_dimensions

    @property
    def level_count(self) -> int:
        return self._slide.level_count

    @property
    def mpp(self) -> Tuple[Optional[float], Optional[float]]:
        mpp_x = self._slide.properties["openslide.mpp-x"]
        mpp_x = float(mpp_x) if mpp_x else mpp_x
        mpp_y = self._slide.properties["openslide.mpp-y"]
        mpp_y = float(mpp_y) if mpp_y else mpp_y
        return mpp_x, mpp_y

    @property
    def dtype(self) -> np.dtype:
        return np.dtype(np.uint8)

    @property
    def n_channels(self) -> int:
        return 3

    @property
    def level_downsamples(self) -> List[float]:
        """Return a list of downsample factors for each level of the slide.

        Returns:
            List[float]: The list of downsample factors.
        """
        return self._slide.level_downsamples

    @property
    def tile_dimensions(self) -> List[Tuple[int, int]]:
        if not hasattr(self, "_tile_dimensions"):
            self._tile_dimensions = []
            for level in range(self.level_count):
                tile_width = int(
                    self._slide.properties[f"openslide.level[{level}].tile-width"]
                )
                tile_height = int(
                    self._slide.properties[f"openslide.level[{level}].tile-height"]
                )
                self._tile_dimensions.append((tile_width, tile_height))
        return self._tile_dimensions
