import os

import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import (QImage)

from GUI.Components import CustomListWidgetItem
from GUI.Helpers import ImageHelpers

class PopulateImageGrid(QObject):

    added = pyqtSignal(CustomListWidgetItem, QImage)
    added_image = pyqtSignal(object)
    one_iteration = pyqtSignal(int, str)
    finished = pyqtSignal()

    def __init__(self, folder_name):
        super().__init__()
        self.folder_name = folder_name

    @pyqtSlot()
    def long_running(self):
        valid_images = (".jpg", ".jpeg", ".gif", ".png", ".tga", ".tif")
        filelist = [f for f in os.listdir(self.folder_name) if f.endswith(valid_images)]
        filelist_len = len(filelist)
        for i, file in enumerate(filelist):
            image = ImageHelpers.resize_image(os.path.join(self.folder_name, file), (44, 44))
            image = np.array(image).reshape(-1)
            self.added_image.emit(image)
            item = CustomListWidgetItem(image, file)
            image = image.reshape(44, -1)
            image = ImageHelpers.toQImage(image)
            self.added.emit(item, image)
            self.one_iteration.emit(int((i / (filelist_len - 1)) * 100), "Loading images")
        self.finished.emit()