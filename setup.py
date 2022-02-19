from distutils.core import setup

setup(
    name="wsi-reader",
    version="0.1",
    description="",
    author="",
    author_email="",
    url="https://github.com/stefano-malacrino/wsi-reader",
    packages=["wsi_reader"],
    python_requires=">=3.6",
    install_requires=[
        "numpy>=1.19.2",
        "opencv-python-headless>=4.5.3.56",
    ],
    extras_require={
        "philips": [
            "pixelengine>=3.1.3",
            "softwarerendercontext>=3.1.3",
            "softwarerendercontext>=3.1.3",
        ],
        "tifffile": ["tifffile>=2021.10.12", "zarr>=2.10.1"],
        "openslide": ["openslide-python>=1.1.1"],
    },
)
