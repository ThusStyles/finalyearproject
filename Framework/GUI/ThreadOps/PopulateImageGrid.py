import os

from PyQt5.QtCore import *
from PyQt5.QtGui import (QPixmap, QIcon, QImage, qRgb)
from skimage import io
from Framework.GUI.Helpers import ImageHelpers
import numpy as np
from Framework.GUI.Components import CustomListWidgetItem

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
        filelist = [f for f in os.listdir(self.folder_name) if f.endswith(".tif")]
        filelist_len = len(filelist)
        for i, file in enumerate(filelist):
            image = ImageHelpers.resize_image(os.path.join(self.folder_name, file), (44, 44))
            image = np.array(image).reshape(-1)
            self.added_image.emit(image)
            item = CustomListWidgetItem(image)
            image = image.reshape(44, -1)
            image = ImageHelpers.toQImage(image)
            self.added.emit(item, image)
            self.one_iteration.emit(int((i / (filelist_len - 1)) * 100), "Adding to test set")
        self.finished.emit()