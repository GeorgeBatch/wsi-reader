"""wsi-reader is a format-independent WSI reader. The API is designed to be similar to openslide.

Backends based on the following libraries are available: tifffile, openslide and the Philips pathology SDK.
The reader works with all the image formats supported by the installed backends.

To install the package from the latest master with a desired backend (e.g. tifffile) use the following command:

    pip install "wsi-reader[tifffile] @ https://github.com/stefano-malacrino/wsi-reader.git"
"""

from os import PathLike
from pathlib import Path
from typing import Optional, Type, Union

from .base import WSIReader


def get_wsi_reader(slide_path: Union[PathLike, str]) -> Optional[Type[WSIReader]]:
    """Return a class implementing WSIReader interface based on the image file extension or None if no suitable implementation is found.

    Args:
        slide_path (Union[PathLike, str]): Path of the image file.

    Returns:
        Optional[Type[WSIReader]]: Reader class.
    """
    slide_path = Path(slide_path)
    if slide_path.suffix == ".isyntax":
        from .philips_backend import IsyntaxReader

        return IsyntaxReader

    with open(slide_path, "rb") as fh:
        header = fh.read(2)
        if header in {b"II", b"MM", b"EP"}:
            from .tifffile_backend import TiffReader

            return TiffReader

    if slide_path.suffix in (".mrxs", ".svslide"):
        from .openslide_backend import OpenslideReader

        return OpenslideReader

    return None
