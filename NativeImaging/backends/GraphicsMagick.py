# encoding: utf-8
"""
An Image-compatible backend using GraphicsMagick via ctypes
"""

import ctypes
import sys

from NativeImaging.api import Image

import wand_wrapper as wand

class GraphicsMagickImage(Image):
    _wand = None

    NONE = NEAREST = 0
    ANTIALIAS = wand.FilterTypes['LanczosFilter']
    CUBIC = BICUBIC = wand.FilterTypes['CubicFilter']

    def __init__(self):
        self._wand = wand.NewMagickWand()
        assert self._wand, "NewMagickWand() failed???"

    def __del__(self):
        if self._wand:
            self._wand = wand.DestroyMagickWand(self._wand)

    @classmethod
    def open(cls, fp, mode="rb"):
        i = cls()

        if hasattr(fp, "read"):
            c_file = ctypes.pythonapi.PyFile_AsFile(fp)
            wand.MagickReadImageFile(i._wand, c_file)
        else:
            wand.MagickReadImage(i._wand, fp)

        return i

    def thumbnail(self, size, resample=ANTIALIAS):
        orig_width = x = wand.MagickGetImageWidth(self._wand)
        orig_height = y = wand.MagickGetImageHeight(self._wand)

        if x > size[0]: y = max(y * size[0] / x, 1); x = size[0]
        if y > size[1]: x = max(x * size[1] / y, 1); y = size[1]

        new_size = (x, y)

        wand.MagickStripImage(self._wand)
        return self.resize(new_size, resample=resample)

    def resize(self, size, resample=ANTIALIAS):
        return wand.MagickResizeImage(self._wand, size[0], size[1], resample, 1)

    def save(self,  fp, format="JPEG", **kwargs):
        wand.MagickSetImageFormat(self._wand, format)
        assert format == wand.MagickGetImageFormat(self._wand)

        if hasattr(fp, 'fileno'):
            c_file = ctypes.pythonapi.PyFile_AsFile(fp)
            wand.MagickWriteImageFile(self._wand, c_file)
        else:
            wand.MagickWriteImage(self._wand, fp)
