import abc
import cv2
import numpy as np

from typing import List, Optional, Tuple, Union


class WSIReader(metaclass=abc.ABCMeta):
    """Interface class for a WSI reader."""

    @abc.abstractmethod
    def close(self) -> None:
        """Close the slide.

        Returns:
            None
        """
        raise NotImplementedError

    def __enter__(self) -> "WSIReader":
        return self

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        self.close()

    def read_region(
        self,
        x_y: Tuple[int, int],
        level: int,
        tile_size: Union[Tuple[int, int], int],
        normalize: bool = True,
        downsample_level_0: bool = False,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Reads the contens of the specified region in the slide from the given level.

        Args:
            x_y (Tuple[int, int]): coordinates of the top left pixel of the region in the given level reference frame.
            level (int): the desired level.
            tile_size (Union[Tuple[int, int], int]): size of the region. Can be a tuple in the format (width, height) or a single scalar to specify a square region.
            normalize (bool, optional): True to normalize the pixel values in therange [0,1]. Defaults to True.
            downsample_level_0 (bool, optional): True to render the region by downsampling from level 0. Defaults to False.

        Returns:
            Tuple[np.ndarray, np.ndarray]: tuple of pixel data and alpha mask of the specified region.
        """
        if isinstance(tile_size, int):
            tile_size = (tile_size, tile_size)

        x, y = x_y
        if downsample_level_0 and level > 0:
            downsample = round(
                self.level_dimensions[0][0] / self.level_dimensions[level][0]
            )
            x, y = x * downsample, y * downsample
            tile_w, tile_h = tile_size[0] * downsample, tile_size[1] * downsample
            width, height = self.level_dimensions[0]
        else:
            tile_w, tile_h = tile_size
            width, height = self.level_dimensions[level]

        tile_w = tile_w + x if x < 0 else tile_w
        tile_h = tile_h + y if y < 0 else tile_h
        x = max(x, 0)
        y = max(y, 0)
        tile_w = width - x if (x + tile_w > width) else tile_w
        tile_h = height - y if (y + tile_h > height) else tile_h

        tile, alfa_mask = self._read_region(
            (x, y), 0 if downsample_level_0 else level, (tile_w, tile_h)
        )
        if downsample_level_0 and level > 0:
            tile_w = tile_w // downsample
            tile_h = tile_h // downsample
            x = x // downsample
            y = y // downsample
            tile = cv2.resize(tile, (tile_w, tile_h), interpolation=cv2.INTER_CUBIC)
            alfa_mask = cv2.resize(
                alfa_mask.astype(np.uint8),
                (tile_w, tile_h),
                interpolation=cv2.INTER_CUBIC,
            ).astype(bool)

        if normalize:
            tile = self._normalize(tile)

        padding = [
            (y - x_y[1], tile_size[1] - tile_h + min(x_y[1], 0)),
            (x - x_y[0], tile_size[0] - tile_w + min(x_y[0], 0)),
        ]
        tile = np.pad(
            tile,
            padding + [(0, 0)] * (len(tile.shape) - 2),
            "constant",
            constant_values=0,
        )
        alfa_mask = np.pad(alfa_mask, padding, "constant", constant_values=0)

        return tile, alfa_mask

    def read_region_ds(
        self,
        x_y: Tuple[int, int],
        downsample: float,
        tile_size: Union[Tuple[int, int], int],
        normalize: bool = True,
        downsample_level_0: bool = False,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Reads the contens of the specified region in the slide for the given downsample factor.

        Args:
            x_y (Tuple[int, int]): coordinates of the top left pixel of the region in the given downsample factor reference frame.
            downsample (float): the desired downsample factor.
            tile_size (Union[Tuple[int, int], int]): size of the region. Can be a tuple in the format (width, height) or a single scalar to specify a square region.
            normalize (bool, optional): True to normalize the pixel values in therange [0,1]. Defaults to True.
            downsample_level_0 (bool, optional): True to render the region by downsampling from level 0. Defaults to False.

        Returns:
            Tuple[np.ndarray, np.ndarray]: tuple of pixel data and alpha mask of the specified region.
        """
        if downsample <= 0:
            raise RuntimeError("Downsample factor must be positive")

        if not isinstance(tile_size, tuple):
            tile_size = (tile_size, tile_size)

        if downsample == 1:
            downsample_level_0 = False

        if downsample in self.level_downsamples and not downsample_level_0:
            level = self.get_best_level_for_downsample(downsample)
            tile, alfa_mask = self.read_region(x_y, level, tile_size, False, False)
        else:
            level = (
                0
                if downsample_level_0
                else self.get_best_level_for_downsample(downsample)
            )
            x_y_level = (
                round(x_y[0] * downsample / self.level_downsamples[level]),
                round(x_y[1] * downsample / self.level_downsamples[level]),
            )
            tile_size_level = (
                round(tile_size[0] * downsample / self.level_downsamples[level]),
                round(tile_size[1] * downsample / self.level_downsamples[level]),
            )
            tile, alfa_mask = self.read_region(
                x_y_level, level, tile_size_level, False, downsample_level_0
            )
            tile = cv2.resize(tile, tile_size, interpolation=cv2.INTER_CUBIC)
            alfa_mask = cv2.resize(
                alfa_mask.astype(np.uint8), tile_size, interpolation=cv2.INTER_CUBIC
            ).astype(bool)

        if normalize:
            tile = self._normalize(tile)

        return tile, alfa_mask

    @abc.abstractmethod
    def _read_region(
        self, x_y: Tuple[int, int], level: int, tile_size: Tuple[int, int]
    ) -> Tuple[np.ndarray, np.ndarray]:
        raise NotImplementedError

    def get_best_level_for_downsample(self, downsample: float) -> int:
        """Return the best level for the given downsample factor.

        Args:
            downsample (float): the downsample factor.

        Returns:
            int: the level.
        """
        if downsample < self.level_downsamples[0]:
            return 0

        for i in range(1, self.level_count):
            if downsample < self.level_downsamples[i]:
                return i - 1

        return self.level_count - 1

    def get_downsampled_slide(
        self, dims: Tuple[int, int], normalize: bool = True
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Return a downsampled version of the slide with the given dimensions.

        Args:
            dims (Tuple[int, int]): size of the downsampled slide asa (width, height) tuple.
            normalize (bool, optional): True to normalize the pixel values in therange [0,1]. Defaults to True.

        Returns:
            Tuple[np.ndarray, np.ndarray]: tuple of pixel data and alpha mask of the downsampled slide.
        """
        downsample = min(a / b for a, b in zip(self.level_dimensions[0], dims))
        slide_downsampled, alfa_mask = self.read_region_ds(
            (0, 0),
            downsample,
            self.get_dimensions_for_downsample(downsample),
            normalize=normalize,
        )
        return slide_downsampled, alfa_mask

    def get_dimensions_for_downsample(self, downsample: float) -> Tuple[int, int]:
        """Return the slide dimensions for for a given fownsample factor.

        Args:
            downsample (float): downsample factor.

        Returns:
            Tuple[int, int]: slide dimensions for the given downsample factor as a tuple (width, height).
        """
        if downsample <= 0:
            raise RuntimeError("Downsample factor must be positive")
        if downsample in self.level_downsamples:
            level = self.level_downsamples.index(downsample)
            dims = self.level_dimensions[level]
        else:
            w, h = self.level_dimensions[0]
            dims = round(w / downsample), round(h / downsample)
        return dims

    @property
    @abc.abstractmethod
    def level_count(self) -> int:
        """Number of levels in the slide."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def level_dimensions(self) -> List[Tuple[int, int]]:
        """Slide dimensions for each slide level as a list of (width, height) tuples."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def tile_dimensions(self) -> List[Tuple[int, int]]:
        """Tile dimensions for each slide level as a list of (width, height) tuples."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def mpp(self) -> Tuple[Optional[float], Optional[float]]:
        """A tuple containing the number of microns per pixel of level 0 in the X and Y dimensions respectively, if known."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def dtype(self) -> np.dtype:
        """Numpy data type of the slide pixels.

        Returns:
            np.dtype: Pixels data type.
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def n_channels(self) -> int:
        """Number of channels in the slide.

        Returns:
            int: Number of channels.
        """
        raise NotImplementedError

    @property
    def level_downsamples(self) -> List[float]:
        """Return a list of downsample factors for each level of the slide.

        Returns:
            List[float]: The list of downsample factors.
        """
        if not hasattr(self, "_level_downsamples"):
            self._level_downsamples = []
            width, height = self.level_dimensions[0]
            for level in range(self.level_count):
                w, h = self.level_dimensions[level]
                ds = float(round(width / w))
                self._level_downsamples.append(ds)
        return self._level_downsamples

    @staticmethod
    def _normalize(pixels: np.ndarray) -> np.ndarray:
        if np.issubdtype(pixels.dtype, np.integer):
            pixels = (pixels / 255).astype(np.float32)
        return pixels
