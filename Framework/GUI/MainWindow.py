import sys
import os
from PyQt5.QtWidgets import QListWidgetItem, QApplication, QWidget, QPushButton, QHBoxLayout, QGroupBox, QDialog, QVBoxLayout, QGridLayout, QProgressBar, QMainWindow, QLineEdit, QLabel, QListWidget, QListView, QScrollArea, QAbstractItemView
from PyQt5.QtGui import (QPixmap, QIcon, QImage, qRgb)
from PyQt5.QtCore import *
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from Framework.DataSet import DataSet
from Framework.NeuralNet import NeuralNet
import numpy as np

img_size = 44
base_dir = os.path.dirname(os.path.realpath(__file__)) + "/../../"
gray_color_table = [qRgb(i, i, i) for i in range(256)]

class PopulateCarpet(QObject):

    added = pyqtSignal(QImage)
    finished = pyqtSignal()

    def __init__(self, images):
        super().__init__()
        self.addItem(QListWidgetItem("Empty"))
        self.images = images

    @pyqtSlot()
    def long_running(self):
        for file in self.images:
            image = QImage(file)
            self.added.emit(image)
        self.finished.emit()


class LoadImages(QObject):

    finished = pyqtSignal()
    one_iteration = pyqtSignal(float)

    def __init__(self, limit, dataset):
        super().__init__()
        self.limit = limit
        self.dataset = dataset

    @pyqtSlot()
    def long_running(self):
        self.dataset.get_data(callback=self.finished_one_iteration)
        self.dataset.set_training_limit(self.limit)
        self.finished.emit()

    def finished_one_iteration(self, amount):
        self.one_iteration.emit(int(amount * 100))

class RunNeuralNet(QObject):

    finished = pyqtSignal()
    one_iteration = pyqtSignal(float)
    testing_finished = pyqtSignal(float, np.ndarray)
    created_neural_net = pyqtSignal(object)

    def __init__(self, dataset):
        super().__init__()
        self.dataset = dataset

    @pyqtSlot()
    def long_running(self):
        self.neuralNet = NeuralNet(img_size, self.dataset)
        self.created_neural_net.emit(self.neuralNet)
        self.neuralNet.optimize(num_iterations=100, callback=self.finished_one_iteration)
        self.neuralNet.get_test_accuracy(show_example_errors=False, callback=self.finished_test_accuracy)

    def finished_test_accuracy(self, test_acc, cls_pred):
        print(test_acc)
        print(cls_pred)
        self.testing_finished.emit(test_acc, cls_pred)
        self.finished.emit()


    def finished_one_iteration(self, amount):
        self.one_iteration.emit(int(amount * 100))

class CustomListWidgetItem(QListWidgetItem):
    def __init__(self, parentIndex):
        super().__init__()
        self.parentIndex = parentIndex

class ImageGrid(QListWidget):
    def __init__(self):
        super().__init__()
        self.isEmpty = True
        self.init_ui()

    @pyqtSlot(QImage)
    def add_image(self, image, index):
        if self.isEmpty:
            self.clear()
            self.setGridSize(QSize(30, 30))
        item = CustomListWidgetItem(index)
        pixmap = QPixmap(72, 72)
        pixmap.convertFromImage(image)
        icon = QIcon(pixmap)
        item.setIcon(icon)
        super().addItem(item)
        self.isEmpty = False

    def takeItem(self, p_int):
        if self.count() == 1:
            self.isEmpty = True
            self.setGridSize(QSize(60, 60))
            super().addItem(QListWidgetItem("Empty"))
        return super().takeItem(p_int)

    def addItem(self, item):
        if self.isEmpty:
            self.clear()
            self.setGridSize(QSize(30, 30))
        self.isEmpty = False
        super().addItem(item)

    def init_ui(self):
        super().addItem(QListWidgetItem("Empty"))
        self.setFlow(QListView.LeftToRight)
        self.setResizeMode(QListView.Adjust)
        self.setGridSize(QSize(60, 60))
        self.setViewMode(QListView.IconMode)
        self.setDragEnabled(False)

    def add_files(self, file_list):
        # 1 - create Worker and Thread inside the Form
        self.isEmpty = False
        self.clear()
        self.setGridSize(QSize(30, 30))
        self.obj = PopulateCarpet(file_list)  # no parent!
        self.thread = QThread()  # no parent!

        self.obj.added.connect(self.add_image)
        self.obj.moveToThread(self.thread)
        self.obj.finished.connect(self.thread.quit)
        self.thread.started.connect(self.obj.long_running)

        self.thread.start()


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

    def setDefault(self):
        self.setRange(0, 100)



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

        #LEFT AREA
        self.leftArea = QVBoxLayout()


        # LEFT AREA - LABELS
        self.trainingAmountLayout = QHBoxLayout()
        self.trainingAmountLabel = QLabel()
        self.trainingAmountLabel.setText("Training amount")
        self.trainingAmount = QLineEdit(self)
        self.trainingAmount.setText("100")
        self.trainingAmountLayout.addWidget(self.trainingAmountLabel)
        self.trainingAmountLayout.addWidget(self.trainingAmount)

        # LEFT AREA - BUTTON AREA

        self.buttonsLayout = QHBoxLayout()

        self.load_button = QPushButton('Load Images', self)
        self.load_button.setToolTip('Loading the requested number of images')
        self.load_button.clicked.connect(self.load_clicked)

        self.run_button = QPushButton('Run', self)
        self.run_button.setToolTip('Starts the running of the neural network')
        self.run_button.clicked.connect(self.run_clicked)
        self.run_button.setDisabled(True)

        self.buttonsLayout.addWidget(self.load_button)
        self.buttonsLayout.addWidget(self.run_button)

        self.leftArea.addLayout(self.trainingAmountLayout)
        self.leftArea.addLayout(self.buttonsLayout)

        self.accuracyLabel = QLabel()
        self.leftArea.addWidget(self.accuracyLabel)
        self.leftArea.addStretch()

        self.grid.addLayout(self.leftArea, 0, 0)

        self.middleArea = QVBoxLayout()
        self.imageAreas = []

        for i in range(10):
            item = ImageGrid()
            item.itemDoubleClicked.connect(self.double_clicked_predicted)
            self.imageAreas.append(item)
            self.middleArea.addWidget(item)

        self.grid.addLayout(self.middleArea, 0, 1)

        self.rightArea = QVBoxLayout()
        self.validationArea = ImageGrid()
        self.validationArea.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.rightArea.addWidget(self.validationArea)
        self.rightArea.addWidget(QLabel("Move selected to:"))

        self.validationGrid = QGridLayout()
        self.switchButtons = []

        col = 0
        row = 0
        for i in range(10):
            btn = QPushButton(str(i))
            self.switchButtons.append(btn)
            self.validationGrid.addWidget(btn, row, col)
            btn.clicked.connect(self.clicked_switch)
            col = col + 1
            if i == 4:
                col = 0
                row = row + 1

        self.rightArea.addLayout(self.validationGrid)

        self.rightArea.addStretch()
        self.grid.addLayout(self.rightArea, 0, 2)

        self.outerArea.addLayout(self.grid)
        self.outerArea.addStretch()
        self.progress = MyProgressBar()
        self.progress.setText('Not yet started')
        self.outerArea.addWidget(self.progress)


        self.setLayout(self.outerArea)


        self.show()

    def clicked_switch(self):
        sending_button = self.sender()
        print(sending_button)
        items = self.validationArea.selectedItems()
        index = int(sending_button.text())
        if self.validationArea.isEmpty: return
        for item in items:
            item.parentIndex = index
            self.imageAreas[index].addItem(self.validationArea.takeItem(self.validationArea.row(item)))

    def double_clicked_predicted(self, item):
        print("Done")
        print(item)
        if (item.parentIndex == None) or self.imageAreas[item.parentIndex].isEmpty: return
        self.validationArea.addItem(self.imageAreas[item.parentIndex].takeItem(self.imageAreas[item.parentIndex].row(item)))


    def reset_buttons(self):
        self.run_button.setText("Run")
        self.load_button.setText("Load Images")
        self.run_button.setDisabled(False)
        self.load_button.setDisabled(False)

    def update_progress(self, amount):
        self.progress.setValue(amount)

    def toQImage(self, im, copy=False):
        if im is None:
            return QImage()

        if im.dtype == np.uint8:
            if len(im.shape) == 2:
                qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_Indexed8)
                qim.setColorTable(gray_color_table)
                return qim.copy() if copy else qim

            elif len(im.shape) == 3:
                if im.shape[2] == 3:
                    qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_RGB888);
                    return qim.copy() if copy else qim
                elif im.shape[2] == 4:
                    qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_ARGB32);
                    return qim.copy() if copy else qim

    def testing_finished(self, accuracy, cls_pred):
        print(accuracy)
        print(cls_pred)
        self.accuracyLabel.setText("Accuracy:" + str(accuracy * 100))

        for i, predicted in enumerate(cls_pred):
            image = self.dataset.testing_images[i]
            imageAreaForDigit = self.imageAreas[predicted]
            print(image.reshape(44, -1))
            image = image.reshape(44, -1)
            image = self.toQImage(image)
            imageAreaForDigit.add_image(image, predicted)

    def created_neural_net(self, neuralNet):
        self.neuralNet = neuralNet


    @pyqtSlot()
    def run_clicked(self):
        self.load_button.setDisabled(True)
        self.run_button.setText("Running...")
        self.run_button.setDisabled(True)

        self.progress.setDefault()
        self.obj = RunNeuralNet(self.dataset)  # no parent!
        self.thread = QThread()  # no parent!

        self.obj.moveToThread(self.thread)
        self.obj.finished.connect(self.reset_buttons)
        self.obj.one_iteration.connect(self.update_progress)
        self.obj.testing_finished.connect(self.testing_finished)
        self.thread.started.connect(self.obj.long_running)

        self.thread.start()

    @pyqtSlot()
    def load_clicked(self):
        print('Load images')
        self.load_button.setText("Loading...")
        self.load_button.setDisabled(True)
        self.progress.setDefault()
        self.dataset = DataSet(img_size)
        self.obj = LoadImages(int(self.trainingAmount.text()), self.dataset)  # no parent!
        self.thread = QThread()  # no parent!

        self.obj.moveToThread(self.thread)
        self.obj.finished.connect(self.reset_buttons)
        self.obj.one_iteration.connect(self.update_progress)
        self.thread.started.connect(self.obj.long_running)

        self.thread.start()