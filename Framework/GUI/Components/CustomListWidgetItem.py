from PyQt5.QtWidgets import QListWidgetItem, QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import (QPixmap, QIcon, QImage, qRgb, QColor)
from PyQt5.QtCore import *
from GUI.Helpers import ImageHelpers

img_size = 44

class CustomListWidgetItem(QListWidgetItem):

    def __init__(self, imageData, title=None):
        super().__init__()
        self.imageData = imageData
        self.title = title

    def set_important(self):
        self.setBackground(QColor("red"))