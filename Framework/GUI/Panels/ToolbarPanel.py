import os

from PyQt5.QtGui import (QIcon)
from PyQt5.QtWidgets import QToolBar

base_dir = os.path.dirname(os.path.realpath(__file__)) + "/../../"
image_dir = base_dir + "images/"

class ToolbarPanel(QToolBar):

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setContentsMargins(0, 0, 0, 0)
        self.addAction(QIcon(image_dir + "play-arrow.svg"), "Play")





