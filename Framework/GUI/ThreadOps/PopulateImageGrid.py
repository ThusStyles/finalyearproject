import os

from PyQt5.QtCore import *
from PyQt5.QtGui import (QPixmap, QIcon, QImage, qRgb)
from skimage import io
from Framework.GUI.Helpers import ImageHelpers
from Framework.GUI.Components import CustomListWidgetItem

class PopulateImageGrid(QObject):

    added = pyqtSignal(CustomListWidgetItem, QImage)
    finished = pyqtSignal()

    def __init__(self, folder_name):
        super().__init__()
        self.folder_name = folder_name

    @pyqtSlot()
    def long_running(self):
        filelist = [f for f in os.listdir(self.folder_name) if f.endswith(".tif")]
        for file in filelist:
            image = io.imread(os.path.join(self.folder_name, file), as_grey=True).reshape(-1)
            item = CustomListWidgetItem(None, image)
            image = image.reshape(44, -1)
            image = ImageHelpers.toQImage(image)
            self.added.emit(item, image)
        self.finished.emit()