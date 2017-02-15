import os

import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import (QPixmap, QIcon, QImage, qRgb)
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QListView
from skimage import io

from . import CustomListWidgetItem

gray_color_table = [qRgb(i, i, i) for i in range(256)]
img_size = 44

class PopulateCarpet(QObject):

    added = pyqtSignal(CustomListWidgetItem, QImage)
    finished = pyqtSignal()

    def __init__(self, folder_name):
        super().__init__()
        self.folder_name = folder_name

    def toQImage(self, im, copy=False):
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

    @pyqtSlot()
    def long_running(self):
        for file in os.listdir(self.folder_name):
            image = io.imread(os.path.join(self.folder_name, file), as_grey=True).reshape(-1)
            item = CustomListWidgetItem(None, image)
            image = image.reshape(44, -1)
            image = self.toQImage(image)
            self.added.emit(item, image)
        self.finished.emit()

class ImageGrid(QListWidget):
    def __init__(self, label, data_panel=None):
        super().__init__()
        self.isEmpty = True
        self.label = label
        self.data_panel = data_panel
        self.init_ui()

    def toQImage(self, im, copy=False):
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
        if self.data_panel:
            print("Triggered")
            count = self.count()
            self.data_panel.trainingTable.updateInfo(self.label, count)

    def add_image(self, image, index):
        if self.isEmpty:
            super().clear()
            self.setGridSize(QSize(30, 30))
        item = CustomListWidgetItem(index, image)
        image = image.reshape(44, -1)
        image = self.toQImage(image)
        pixmap = QPixmap(img_size, img_size)
        pixmap.convertFromImage(image)
        icon = QIcon(pixmap)
        item.setIcon(icon)
        super().addItem(item)
        self.update_tables()
        self.isEmpty = False


    def populate_from_folder(self, folder_name):
        self.obj = PopulateCarpet(folder_name)  # no parent!
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
        self.setAttribute(Qt.WA_MacShowFocusRect, False)

    def sizeHint(self):
        s = QSize()
        s.setHeight(super(QListWidget, self).sizeHint().height())
        s.setHeight(self.sizeHintForRow(0))
        return s