from PyQt5.QtWidgets import QListWidgetItem, QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import (QPixmap, QIcon, QImage, qRgb, QColor)
from PyQt5.QtCore import *
from Framework.GUI.Helpers import ImageHelpers

img_size = 44

class CustomListWidgetItem(QListWidgetItem):

    def __init__(self, imageData):
        super().__init__()
        self.imageData = imageData

    def set_important(self):
        self.setBackground(QColor("red"))