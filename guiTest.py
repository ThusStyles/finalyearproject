import sys
import os
import time
from PyQt5.QtCore import *

from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QApplication, QGridLayout, QListView, QMainWindow)
from PyQt5.QtGui import (QPixmap, QIcon, QImage)

class PopulateCarpet(QObject):

    added = pyqtSignal(int, QImage)
    finished = pyqtSignal()

    def __init__(self, index, folder_name):
        super().__init__()
        self.folder_name = folder_name
        self.index = index

    @pyqtSlot()
    def long_running(self):
        for file in os.listdir(self.folder_name):
            image = QImage(os.path.join(self.folder_name, file))
            self.added.emit(self.index, image)
        self.finished.emit()

class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.list_widgets = []
        self.threads = []
        self.objs = []
        self.initUI()

    def add_image(self, index, image):
        item = QListWidgetItem()
        icon = QIcon()
        pixmap = QPixmap(72, 72)
        pixmap.convertFromImage(image)
        icon = QIcon(pixmap)
        item.setIcon(icon)
        self.list_widgets[index].addItem(item)

    def initUI(self):
        hbox = QGridLayout(self)

        for i in range(10):
            list_widget = QListWidget(self)

            list_widget.setFlow(QListView.LeftToRight)
            list_widget.setResizeMode(QListView.Adjust)
            list_widget.setGridSize(QSize(30, 30))
            list_widget.setViewMode(QListView.IconMode)
            self.list_widgets.append(list_widget)

            # 1 - create Worker and Thread inside the Form
            obj = PopulateCarpet(i, str(i) + "-cropped")  # no parent!
            thread = QThread()  # no parent!

            obj.added.connect(self.add_image)

            obj.moveToThread(thread)
            obj.finished.connect(thread.quit)
            thread.started.connect(obj.long_running)

            self.threads.append(thread)
            self.objs.append(obj)

            thread.start()

            hbox.addWidget(list_widget, i // 3, i % 3)


        self.setLayout(hbox)

        self.move(300, 200)
        self.setWindowTitle('Red Rock')
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())