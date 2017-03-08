import os

from PyQt5.QtCore import *
from PyQt5.QtGui import (qRgb, QPainter, QFont)
from PyQt5.QtWidgets import QListWidgetItem, QWidget, QVBoxLayout, QLabel, QListWidget, QAbstractItemView, QStyle, QStyleOption

from Framework.GUI.Components import CustomProgressBar

img_size = 44
base_dir = os.path.dirname(os.path.realpath(__file__)) + "/../../"
gray_color_table = [qRgb(i, i, i) for i in range(256)]


class ProgressModule(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.titleLabel = QLabel("STATUS")
        self.progress = CustomProgressBar()
        self.progress.setText("Waiting")

        font = QFont()
        font.setLetterSpacing(QFont.AbsoluteSpacing, 2)
        font.setPixelSize(11.5)
        self.titleLabel.setFont(font)
        self.titleLabel.setObjectName("titleLabel")

        self.layout.addWidget(self.titleLabel)
        self.layout.addWidget(self.progress)

        self.setLayout(self.layout)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.setObjectName("progressPanel")
        self.setAutoFillBackground(True)
        self.show()

    def setStatus(self, status):
        self.status.setText(status)

    def setProgress(self, prog):
        self.progress.setValue(prog)


class MenuModule(QListWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):

        self.setAttribute(Qt.WA_MacShowFocusRect, False)

        self.addItem(QListWidgetItem("Neural Network"))
        self.addItem(QListWidgetItem("Reports"))
        self.addItem(QListWidgetItem("Settings"))
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.item(0).setSelected(True)

        self.show()


class MenuPanel(QWidget):

    selectedItem = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)

    def selected_item(self, item):
        self.selectedItem.emit(self.menu.currentIndex().row())

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)
        self.titleLabel = QLabel("Neural Network")
        self.progressModule = ProgressModule()
        self.layout.addWidget(self.progressModule)
        self.menu = MenuModule()
        self.menu.selectionModel().selectionChanged.connect(self.selected_item)
        font = QFont()
        font.setLetterSpacing(QFont.AbsoluteSpacing, 2)
        font.setPixelSize(11.5)
        menuLabel = QLabel("MENU")
        menuLabel.setFont(font)
        menuLabel.setObjectName("menuLabel")


        self.layout.addWidget(menuLabel)
        self.layout.addWidget(self.menu)
        self.setObjectName("menuPanel")

        self.setLayout(self.layout)
        self.setAutoFillBackground(True)

