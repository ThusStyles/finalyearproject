from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QComboBox, QStyleFactory, QListView


class CustomComboBox(QComboBox):

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setStyle(QStyleFactory.create("Windows"))

        self.setView(QListView())

        font = QFont()
        font.setLetterSpacing(QFont.AbsoluteSpacing, 0.8)
        font.setPixelSize(11)
        font.setCapitalization(QFont.AllUppercase)
        self.setFont(font)