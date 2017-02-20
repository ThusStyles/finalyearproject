import os

import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import (QPixmap, QIcon, QImage, qRgb)
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QListView, QAbstractItemView
from skimage import io
from Framework.GUI.Helpers import ImageHelpers
from . import CustomListWidgetItem
from Framework.GUI.ThreadOps import PopulateImageGrid

img_size = 44

class ImageGrid(QListWidget):
    def __init__(self, label, data_panel=None):
        super().__init__()
        self.isEmpty = True
        self.label = label
        self.data_panel = data_panel
        self.dont_update_tables = False
        self.init_ui()

    def add_image_from_thread(self, item, image):
        if self.isEmpty:
            super().clear()
            self.setGridSize(QSize(30, 30))
        pixmap = QPixmap(img_size, img_size)
        pixmap.convertFromImage(image)
        icon = QIcon(pixmap)
        item.setIcon(icon)
        self.updateGeometry()
        super().addItem(item)
        self.isEmpty = False

    def update_tables(self):
        if self.data_panel and not self.dont_update_tables:
            count = self.count()
            self.data_panel.trainingTable.updateInfo(self.label, count)

    def add_image(self, image):
        if self.isEmpty:
            super().clear()
            self.setGridSize(QSize(30, 30))
        item = CustomListWidgetItem(self.label, image)
        image = image.reshape(44, -1)
        image = ImageHelpers.toQImage(image)
        pixmap = QPixmap(img_size, img_size)
        pixmap.convertFromImage(image)
        icon = QIcon(pixmap)
        item.setIcon(icon)
        super().addItem(item)
        self.update_tables()
        self.isEmpty = False


    def populate_from_folder(self, folder_name):
        self.obj = PopulateImageGrid(folder_name)  # no parent!
        self.thread = QThread()

        self.obj.moveToThread(self.thread)
        self.obj.added.connect(self.add_image_from_thread)
        self.thread.started.connect(self.obj.long_running)

        self.thread.start()

    def clear(self):
        self.setGridSize(QSize(30, 30))
        self.isEmpty = True
        super().clear()
        self.update_tables()
        super().addItem(QListWidgetItem("Empty"))

    def count(self):
        if self.isEmpty: return 0
        return super().count()

    def takeItem(self, p_int):
        if self.count() == 1:
            self.isEmpty = True
            self.setGridSize(QSize(img_size, img_size))
            super().addItem(QListWidgetItem("Empty"))
        item = super().takeItem(p_int)
        self.update_tables()
        return item

    def addItem(self, item):
        if self.isEmpty:
            super().clear()
            self.setGridSize(QSize(30, 30))
        self.isEmpty = False
        super().addItem(item)
        self.update_tables()

    def init_ui(self):
        super().addItem(QListWidgetItem("Empty"))
        self.setFlow(QListView.LeftToRight)
        self.setResizeMode(QListView.Adjust)
        self.setGridSize(QSize(60, 60))
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