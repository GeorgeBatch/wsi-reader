import os
import numpy as np

from os import PathLike
from pathlib import Path
from pixelengine import PixelEngine
from softwarerendercontext import SoftwareRenderContext
from softwarerenderbackend import SoftwareRenderBackend
from typing import List, Optional, Tuple, Union

from .base import WSIReader


class IsyntaxReader(WSIReader):
    """Implementation of the WSIReader interface for the isyntax format backed by the Philips pathology SDK."""

    def __init__(
        self,
        slide_path: Union[PathLike, str],
        cache_path: Optional[Union[PathLike, str]] = None,
        generate_cache=False,
        **kwargs
    ) -> None:
        """Open a slide. The object may be used as a context manager, in which case it will be closed upon exiting the context.

        Args:
            slide_path (Union[PathLike, str]): Path of the slide to open.
            cache_path (Optional[Union[PathLike, str]], optional): Path to the cache file for the image. If it's a path to a folder the file name is assumed to be the same as the image.  If None sets the path to the directory where the image is stored. If generate_cache is False and the cache file doesn't exist caching is disabled. Defaults to None.
            generate_cache (bool, optional): If True create the cache file if not present. Defaults to False.
        """
        slide_path = Path(slide_path)
        cache_path = Path(cache_path) if cache_path else slide_path.with_suffix(".fic")
        container_name = (
            "caching-ficom"
            if cache_path is None
            or cache_path.is_file()
            or (
                cache_path.is_dir()
                and (cache_path / slide_path.with_suffix(".fic").stem).exists()
            )
            or (
                generate_cache
                and os.access(
                    slide_path.parent if slide_path.suffix == ".fic" else slide_path,
                    os.W_OK,
                )
            )
            else "ficom"
        )
        self._pe = PixelEngine(SoftwareRenderBackend(), SoftwareRenderContext())
        self._pe["in"].open(str(slide_path), container_name, "r", str(cache_path))
        self._view = self._pe["in"]["WSI"].source_view
        trunc_bits = {0: [0, 0, 0]}
        self._view.truncation(False, False, trunc_bits)

    def close(self) -> None:
        """Close the slide.

        Returns:
            None
        """
        self._pe["in"].close()
        if hasattr(self, "_tile_dimensions"):
            delattr(self, "_tile_dimensions")
        if hasattr(self, "_level_dimensions"):
            delattr(self, "_level_dimensions")
        if hasattr(self, "_level_downsamples"):
            delattr(self, "_level_downsamples")

    @property
    def tile_dimensions(self) -> List[Tuple[int, int]]:
        if not hasattr(self, "_tile_dimensions"):
            tile_w, tile_h = self._pe["in"]["WSI"].block_size()[:2]
            self._tile_dimensions = [(tile_w, tile_h)] * self.level_count
        return self._tile_dimensions

    def _read_region(
        self, x_y: Tuple[int, int], level: int, tile_size: Tuple[int, int]
    ) -> Tuple[np.ndarray, np.ndarray]:
        x_start, y_start = x_y
        ds = self.level_downsamples[level]
        x_start = round(x_start * ds)
        y_start = round(y_start * ds)
        tile_w, tile_h = tile_size
        x_end, y_end = round(x_start + (tile_w - 1) * ds), round(
            y_start + (tile_h - 1) * ds
        )
        view_range = [x_start, x_end, y_start, y_end, level]
        regions = self._view.request_regions(
            [view_range],
            self._view.data_envelopes(level),
            True,
            [255, 255, 255],
            self._pe.BufferType(1),
        )
        (region,) = self._pe.wait_any(regions)
        tile = np.empty(np.prod(tile_size) * 4, dtype=np.uint8)
        region.get(tile)
        tile.shape = (tile_h, tile_w, 4)
        return tile[:, :, :3], tile[:, :, 3] > 0

    @property
    def level_dimensions(self) -> List[Tuple[int, int]]:
        if not hasattr(self, "_level_dimensions"):
            self._level_dimensions = []
            for level in range(self.level_count):
                x_step, x_end = self._view.dimension_ranges(level)[0][1:]
                y_step, y_end = self._view.dimension_ranges(level)[1][1:]
                range_x = (x_end + 1) // x_step
                range_y = (y_end + 1) // y_step
                self._level_dimensions.append((range_x, range_y))
        return self._level_dimensions

    @property
    def level_count(self) -> int:
        return self._view.num_derived_levels + 1

    @property
    def mpp(self) -> Tuple[Optional[float], Optional[float]]:
        return self._view.scale[0], self._view.scale[1]

    @property
    def dtype(self) -> np.dtype:
        return np.dtype(np.uint8)

    @property
    def n_channels(self) -> int:
        return 3

    @property
    def level_downsamples(self) -> List[float]:
        if not hasattr(self, "_level_downsamples"):
            self._level_downsamples = [
                float(self._view.dimension_ranges(level)[0][1])
                for level in range(self.level_count)
            ]
        return self._level_downsamples
