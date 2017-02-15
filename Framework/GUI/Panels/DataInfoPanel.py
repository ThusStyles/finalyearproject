import os

from PyQt5.QtCore import *
from PyQt5.QtGui import (QFont, QPainter)
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QStyle, QStyleOption

from Framework.GUI.Components import CustomPushButton

base_dir = os.path.dirname(os.path.realpath(__file__)) + "/../../"
image_dir = base_dir + "images/"

class Datatable(QTableWidget):
    headers = ["Set name", "No. of items"]

    def __init__(self):
        QTableWidget.__init__(self)
        self.init_ui()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()


    def init_ui(self):
        self.verticalHeader().setVisible(False)
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(self.headers)
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.setDefaultAlignment(Qt.AlignLeft)
        self.setShowGrid(False)


    def addRow(self, title, items):
        rowPosition = self.rowCount()
        self.insertRow(rowPosition)
        self.setItem(rowPosition, 0, QTableWidgetItem(title))
        item = QTableWidgetItem()
        item.setData(Qt.EditRole, items)
        self.setItem(rowPosition, 1, item)
        self.setRowCount(rowPosition + 1)

    def updateInfo(self, set, itemCount):
        allRows = self.rowCount()
        for row in range(0, allRows):
            name = self.item(row, 0)
            print(name.text())
            if set == name.text():
                item = QTableWidgetItem()
                item.setData(Qt.EditRole, itemCount)
                self.setItem(row, 1, item)
                self.sortItems(1, Qt.DescendingOrder)
                return
        print(set, itemCount)
        self.addRow(set, itemCount)
        self.sortItems(1, Qt.DescendingOrder)


class DataInfoPanel(QWidget):

    def __init__(self, main_window):
        super().__init__()
        self.init_ui()
        self.main_window = main_window

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)

    def init_ui(self):

        self.layout = QVBoxLayout()
        self.setObjectName("tablePanel")

        self.training_label = QLabel("Training set")
        self.layout.addWidget(self.training_label)
        font = QFont()
        font.setLetterSpacing(QFont.AbsoluteSpacing, 2)
        font.setPixelSize(11.5)
        font.setCapitalization(QFont.AllUppercase)
        self.training_label.setFont(font)

        self.trainingTable = Datatable()
        self.trainingViewAll = CustomPushButton("View all")
        self.layout.addWidget(self.trainingTable)
        self.layout.addWidget(self.trainingViewAll)

        self.testing_label = QLabel("Test set")
        self.layout.addWidget(self.testing_label)
        self.testing_label.setFont(font)
        self.testingTable = Datatable()
        self.testingViewAll = CustomPushButton("View all")
        self.layout.addWidget(self.testingTable)
        self.layout.addWidget(self.testingViewAll)

        self.setContentsMargins(5, 0, 5, 0)
        self.setLayout(self.layout)
        self.setAutoFillBackground(True)







