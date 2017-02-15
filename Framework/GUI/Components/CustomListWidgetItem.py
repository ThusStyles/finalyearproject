from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtCore import *

class CustomListWidgetItem(QListWidgetItem):

    def __init__(self, parentIndex, imageData):
        super().__init__()
        self.parentIndex = parentIndex
        self.imageData = imageData