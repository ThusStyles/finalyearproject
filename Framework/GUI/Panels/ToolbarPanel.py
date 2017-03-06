import os

from PyQt5.QtCore import *
from PyQt5.QtGui import (QIcon)
from PyQt5.QtWidgets import QToolBar

base_dir = os.path.dirname(os.path.realpath(__file__)) + "/../../"
image_dir = base_dir + "images/"

class ToolbarPanel(QToolBar):

    run_clicked = pyqtSignal()
    add_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def run(self):
        self.run_clicked.emit()

    def add_to_testing(self):
        self.add_clicked.emit()

    def init_ui(self):
        self.setContentsMargins(0, 0, 0, 0)
        self.addAction(QIcon(image_dir + "play-arrow.svg"), "Run Neural Network", self.run)
        self.addAction(QIcon(image_dir + "add-plus-button.svg"), "Add folder to testing set", self.add_to_testing)





