import os

from PyQt5.QtCore import *
from PyQt5.QtGui import (QFont, QPainter)
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QStyle, QStyleOption

from GUI.Components import CustomPushButton

base_dir = os.path.dirname(os.path.realpath(__file__)) + "/../../"
image_dir = base_dir + "images/"

class Datatable(QTableWidget):
    headers = ["Set name", "No. of items"]
    added = pyqtSignal()

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

    def add_row(self, title, items):
        rowPosition = self.rowCount()
        self.insertRow(rowPosition)
        self.setItem(rowPosition, 0, QTableWidgetItem(title))
        item = QTableWidgetItem()
        item.setData(Qt.EditRole, items)
        self.setItem(rowPosition, 1, item)
        self.setRowCount(rowPosition + 1)
        self.added.emit()

    def delete_row(self, set):
        allRows = self.rowCount()
        for row in range(0, allRows):
            name = self.item(row, 0)
            if set == name.text():
                self.removeRow(row)
                return

    def change_set(self, set, increment):
        allRows = self.rowCount()
        for row in range(0, allRows):
            name = self.item(row, 0)
            if set == name.text():
                item = QTableWidgetItem()
                new_count = 1 if increment else -1
                item.setData(Qt.EditRole, int(self.item(row, 1).text()) + new_count)
                self.setItem(row, 1, item)
                self.sortItems(1, Qt.DescendingOrder)
                return
        self.add_row(set, 1)
        self.sortItems(1, Qt.DescendingOrder)

    def increment_set(self, set):
        self.change_set(set, True)

    def decrement_set(self, set):
        self.change_set(set, False)


class DataInfoPanel(QWidget):

    clicked_training_view_all_sig = pyqtSignal()
    clicked_testing_view_all_sig = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)

    def added_to_table(self):
        self.empty_label.setVisible(False)
        self.trainingTable.setVisible(True)
        self.trainingViewAll.setVisible(True)

    def set_testing_amount(self, amount):
        plural = "s" if amount == 0 or amount > 1 else ""
        self.testing_quantity.setText(str(amount) + " item" + plural)
        if amount > 0:
            self.testingViewAll.setVisible(True)
        else:
            self.testingViewAll.setVisible(False)

    def delete_training_row(self, set):
        self.trainingTable.delete_row(set)

    def increment_training_table(self, set):
        self.trainingTable.increment_set(set)

    def decrement_training_table(self, set):
        self.trainingTable.decrement_set(set)

    def clicked_training_view_all(self):
        self.clicked_training_view_all_sig.emit()

    def clicked_testing_view_all(self):
        self.clicked_testing_view_all_sig.emit()

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
        self.empty_label = QLabel("Currently empty")
        self.trainingTable.setVisible(False)
        self.trainingTable.added.connect(self.added_to_table)
        self.trainingViewAll = CustomPushButton("View all")
        self.trainingViewAll.clicked.connect(self.clicked_training_view_all)
        self.trainingViewAll.setVisible(False)
        self.layout.addWidget(self.trainingTable)
        self.layout.addWidget(self.empty_label)
        self.layout.addWidget(self.trainingViewAll)

        self.testing_label = QLabel("Test set")
        self.layout.addWidget(self.testing_label)
        self.testing_label.setFont(font)
        self.testing_quantity = QLabel("0 items")
        self.testingViewAll = CustomPushButton("View all")
        self.testingViewAll.clicked.connect(self.clicked_testing_view_all)
        self.layout.addWidget(self.testing_quantity)
        self.layout.addWidget(self.testingViewAll)
        self.testingViewAll.setVisible(False)

        self.setContentsMargins(5, 0, 5, 0)
        self.setLayout(self.layout)
        self.setAutoFillBackground(True)







