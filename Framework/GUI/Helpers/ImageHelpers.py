import os

import numpy as np
from PIL import Image, ImageChops, ImageOps
from PyQt5.QtGui import (QImage, qRgb)

gray_color_table = [qRgb(i, i, i) for i in range(256)]
base_dir = os.path.dirname(os.path.realpath(__file__)) + "/../../"

class ImageHelpers:

    @staticmethod
    def resize_images_in_folder(folder_name, size):
        dir = folder_name
        os.chdir(dir)
        filelist = [f for f in os.listdir(dir) if f.endswith(".tif")]

        for f in filelist:
            image = Image.open(dir + "/" + f)
            image = image.convert('L')
            image = ImageOps.invert(image)
            image = ImageOps.grayscale(image)
            image.thumbnail(size, Image.ANTIALIAS)
            image_size = image.size

            thumb = image.crop((0, 0, size[0], size[1]))

            offset_x = max((size[0] - image_size[0]) // 2, 0)
            offset_y = max((size[1] - image_size[1]) // 2, 0)

            thumb = ImageChops.offset(thumb, offset_x, offset_y)
            F_OUT = dir + "-cropped/" + f

            thumb.save(F_OUT)

    @staticmethod
    def resize_image(image, size):
        # Empty results
        image = Image.open(image)
        image = image.convert('L')
        image = ImageOps.invert(image)
        image = ImageOps.grayscale(image)
        image.thumbnail(size, Image.ANTIALIAS)
        image_size = image.size

        thumb = image.crop((0, 0, size[0], size[1]))

        offset_x = max((size[0] - image_size[0]) // 2, 0)
        offset_y = max((size[1] - image_size[1]) // 2, 0)

        thumb = ImageChops.offset(thumb, offset_x, offset_y)
        return thumb

    @staticmethod
    def toQImage(im, copy=False):
        if im is None:
            return QImage()

        if im.dtype == np.uint8:
            if len(im.shape) == 2:
                qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_Indexed8)
                qim.setColorTable(gray_color_table)
                return qim.copy() if copy else qim

            elif len(im.shape) == 3:
                if im.shape[2] == 3:
                    qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_RGB888);
                    return qim.copy() if copy else qim
                elif im.shape[2] == 4:
                    qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_ARGB32);
                    return qim.copy() if copy else qim