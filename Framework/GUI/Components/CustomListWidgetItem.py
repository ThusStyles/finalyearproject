from PyQt5.QtGui import (QColor)
from PyQt5.QtWidgets import QListWidgetItem


class CustomListWidgetItem(QListWidgetItem):

    def __init__(self, imageData, title=None):
        super().__init__()
        self.imageData = imageData
        self.title = title

    def set_important(self):
        self.setBackground(QColor("red"))