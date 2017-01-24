import sys
import os
from PyQt5.QtWidgets import QListWidgetItem, QApplication, QWidget, QPushButton, QHBoxLayout, QGroupBox, QDialog, QVBoxLayout, QGridLayout, QProgressBar, QMainWindow, QLineEdit, QLabel, QListWidget, QListView
from PyQt5.QtGui import (QPixmap, QIcon, QImage)
from PyQt5.QtCore import *
from PyQt5.QtCore import pyqtSlot, pyqtSignal

base_dir = os.path.dirname(os.path.realpath(__file__)) + "\\..\\..\\"

class PopulateCarpet(QObject):

    added = pyqtSignal(QImage)
    finished = pyqtSignal()

    def __init__(self, folder_name):
        global base_dir
        super().__init__()
        self.folder_name = folder_name
        self.dir = base_dir + folder_name + "\\"
        print(self.dir)

    @pyqtSlot()
    def long_running(self):
        for file in os.listdir(self.dir):
            print(self.dir + file)
            image = QImage(self.dir + file)
            self.added.emit(image)
        self.finished.emit()

class ImageGrid(QListWidget):
    def __init__(self, digit):
        super().__init__()
        self.digit = digit
        self.initUI()

    @pyqtSlot(QImage)
    def add_image(self, image):
        item = QListWidgetItem()
        pixmap = QPixmap(72, 72)
        pixmap.convertFromImage(image)
        icon = QIcon(pixmap)
        item.setIcon(icon)
        self.addItem(item)

    def initUI(self):

        self.setFlow(QListView.LeftToRight)
        self.setResizeMode(QListView.Adjust)
        self.setGridSize(QSize(30, 30))
        self.setViewMode(QListView.IconMode)

        # 1 - create Worker and Thread inside the Form
        self.obj = PopulateCarpet(str(self.digit) + "-cropped")  # no parent!
        self.thread = QThread()  # no parent!

        self.obj.added.connect(self.add_image)
        self.obj.moveToThread(self.thread)
        self.obj.finished.connect(self.thread.quit)
        self.thread.started.connect(self.obj.long_running)

        self.thread.start()

        self.show()


class MyProgressBar(QProgressBar):

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



class MainWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.title = 'Convolutional Neural Network'
        self.left = 300
        self.top = 300
        self.width = 960
        self.height = 560
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.outerArea = QVBoxLayout()

        self.grid = QGridLayout()
        self.grid.setColumnStretch(0, 1)
        self.grid.setColumnStretch(1, 3)
        self.grid.setColumnStretch(2, 1)

        self.leftArea = QVBoxLayout()

        self.trainingAmountLayout = QHBoxLayout()
        self.trainingAmountLabel = QLabel()
        self.trainingAmountLabel.setText("Training amount")
        self.trainingAmount = QLineEdit(self)
        self.trainingAmount.setText("100")
        self.trainingAmountLayout.addWidget(self.trainingAmountLabel)
        self.trainingAmountLayout.addWidget(self.trainingAmount)

        self.button = QPushButton('Run', self)
        self.button.setToolTip('Starts the running of the neural network')
        self.button.clicked.connect(self.run_clicked)

        self.leftArea.addLayout(self.trainingAmountLayout)
        self.leftArea.addWidget(self.button)

        self.grid.addLayout(self.leftArea, 0, 0)

        self.middleArea = QVBoxLayout()

        self.testing = ImageGrid(0)
        self.middleArea.addWidget(self.testing)

        self.grid.addLayout(self.middleArea, 0, 1)

        self.outerArea.addLayout(self.grid)
        self.outerArea.addStretch()
        self.progress = MyProgressBar()
        self.progress.setText('Not yet started')
        self.outerArea.addWidget(self.progress)


        self.setLayout(self.outerArea)


        self.show()

    @pyqtSlot()
    def run_clicked(self):
        print('PyQt5 button click')