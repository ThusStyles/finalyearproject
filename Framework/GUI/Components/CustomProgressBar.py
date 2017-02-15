from PyQt5.QtCore import *
from PyQt5.QtWidgets import QProgressBar


class CustomProgressBar(QProgressBar):

    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self._text = None

    def setText(self, text):
        self._text = text

    def text(self):
        return self._text

    def setBusy(self):
        self.setRange(0, 0)

    def setDefault(self):
        self.setRange(0, 100)

