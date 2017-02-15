from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QPushButton


class CustomPushButton(QPushButton):

    def __init__(self, name):
        super().__init__(name)
        self.init_ui()

    def init_ui(self):
        font = QFont()
        font.setLetterSpacing(QFont.AbsoluteSpacing, 0.8)
        font.setPixelSize(11)
        font.setCapitalization(QFont.AllUppercase)
        self.setFont(font)


