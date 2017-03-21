import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import (QPixmap, QIcon)
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QListView, QAbstractItemView

from GUI.Helpers import ImageHelpers
from GUI.ThreadOps import PopulateImageGrid
from . import CustomListWidgetItem

grid_size_x = 33
grid_size_y = 30
item_size_x = 35
item_size_y = 35

class ImageGrid(QListWidget):
    def __init__(self):
        super().__init__()
        self.isEmpty = True
        self.settings = QSettings("Theo Styles", "Convolutional Neural Network")
        self.img_size = self.settings.value("img_size", 44)
        self.init_ui()

    def add_image_from_thread(self, item, image):
        if self.isEmpty:
            super().clear()
            self.setGridSize(QSize(item_size_x, item_size_y))
        pixmap = QPixmap(item_size_x, item_size_y)
        pixmap.convertFromImage(image)
        icon = QIcon(pixmap)
        item.setIcon(icon)
        self.updateGeometry()
        super().addItem(item)
        self.updateGeometry()
        self.isEmpty = False

    def add_image(self, image):
        if self.isEmpty:
            super().clear()
            self.setGridSize(QSize(item_size_x, item_size_y))

        item = CustomListWidgetItem(image)
        image = image.reshape(self.img_size, -1)
        image = ImageHelpers.toQImage(image)
        pixmap = QPixmap(self.img_size, self.img_size)
        pixmap.convertFromImage(image)
        icon = QIcon(pixmap)
        item.setIcon(icon)
        super().addItem(item)
        self.isEmpty = False
        return item

    def delete_image(self, image):
        count = self.count()
        for i in range(count):
            item = self.item(i)
            if item == None: continue
            if np.array_equal(item.imageData, image):
                deleted = self.takeItem(i)
                print("DELETING ", item)

    def populate_from_folder(self, folder_name, one_iteration=None):
        self.obj = PopulateImageGrid(folder_name)  # no parent!
        self.thread = QThread()

        self.obj.moveToThread(self.thread)
        self.obj.added.connect(self.add_image_from_thread)
        if one_iteration:
            self.obj.one_iteration.connect(one_iteration)
        self.thread.started.connect(self.obj.long_running)

        self.thread.start()

    def clear(self):
        self.setGridSize(QSize(grid_size_x, grid_size_y))
        self.isEmpty = True
        super().clear()
        super().addItem(QListWidgetItem("Empty"))

    def count(self):
        if self.isEmpty: return 0
        return super().count()

    def takeItem(self, p_int):
        if self.count() == 1:
            self.isEmpty = True
            self.setGridSize(QSize(60, 60))
            super().addItem(QListWidgetItem("Empty"))
        item = super().takeItem(p_int)
        return item

    def addItem(self, item):
        if self.isEmpty:
            super().clear()
            self.setGridSize(QSize(item_size_x, item_size_y))
        self.isEmpty = False
        super().addItem(item)

    def init_ui(self):
        super().addItem(QListWidgetItem("Empty"))
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)
        self.setFlow(QListView.LeftToRight)
        self.setResizeMode(QListView.Adjust)
        self.setGridSize(QSize(60, 60))
        self.setIconSize(QSize(grid_size_x, grid_size_y))
        self.setViewMode(QListView.IconMode)
        self.setDragEnabled(False)
        self.setObjectName("imageGrid")
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setAttribute(Qt.WA_MacShowFocusRect, False)

    def sizeHint(self):
        s = QSize()
        s.setHeight(super(QListWidget, self).sizeHint().height())
        s.setHeight(self.sizeHintForRow(0))
        return s