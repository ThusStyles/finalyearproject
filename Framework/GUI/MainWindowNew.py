import os

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QMainWindow, QSplitter
from PyQt5.QtCore import QThread

from Framework.GUI.NeuralNetSection import NeuralNetSection
from Framework.GUI.Panels.DataInfoPanel import DataInfoPanel
from Framework.GUI.Panels.MenuPanel import MenuPanel
from Framework.GUI.Panels.ToolbarPanel import ToolbarPanel
from Framework.Backend import DataSet
from Framework.GUI.ThreadOps import RunNeuralNet

img_size = 44
base_dir = os.path.dirname(os.path.realpath(__file__)) + "/../../"


class MainWindowNew(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Convolutional Neural Network'
        self.left = 300
        self.top = 300
        self.width = 960
        self.height = 560
        self.first_run = True
        self.init_ui()

    def update_progress(self, amount):
        print(amount)
        self.left_area.progressModule.progress.setText("Running - " + str(amount) + "%")
        self.left_area.progressModule.progress.setValue(amount)

    def testing_finished(self, cls_pred):
        print(cls_pred)

        for i, predicted in enumerate(cls_pred):
            image = self.dataset.testing_images[i]
            labelForDigit = self.dataset.labels[predicted]
            print("LABEL IS ", labelForDigit)
            for set in self.main_area.sets:
                if set.name == labelForDigit:
                    set.add_image(image)

    def run_neural_net(self):
        self.left_area.progressModule.progress.setDefault()
        self.obj = RunNeuralNet(self.dataset, img_size, len(self.main_area.sets))  # no parent!
        self.thread = QThread()  # no parent!

        self.obj.moveToThread(self.thread)
        #self.obj.finished.connect(self.reset_buttons)
        self.obj.one_iteration.connect(self.update_progress)
        self.obj.testing_finished.connect(self.testing_finished)
        self.thread.started.connect(self.obj.long_running)

        self.thread.start()

    def run_clicked(self):
        sets = self.main_area.sets

        itemNames = []
        itemData = []
        setCount = 0

        print("SETS LENGTH ", len(sets))

        for set in sets:
            setCount += 1
            imageArea = set.image_grid
            if imageArea.isEmpty: continue
            itemCount = imageArea.count()
            print("ITEM COUNT ", itemCount)
            for index in range(itemCount):
                item = set.item(index)
                if item == None: continue
                print(item)
                itemNames.append(item.parentIndex)
                itemData.append(item.imageData)
            imageArea.dont_update_tables = True
            set.clear()
            imageArea.dont_update_tables = False

        self.dataset.add_sets_to_training_data(setCount, itemNames, itemData)

        if self.first_run:
            all_image_count = self.main_area.initial_image_grid.count()
            testing_images = []
            for index in range(all_image_count):
                item = self.main_area.initial_image_grid.item(index)
                if item == None: continue
                testing_images.append(item.imageData)
            self.main_area.initial_image_grid.clear()
            self.main_area.top_widget.setVisible(False)
            self.dataset.set_testing_data(testing_images)

        self.first_run = False

        self.run_neural_net()


    def init_ui(self):
        self.dataset = DataSet(img_size)
        qss_file = open(base_dir + 'Framework/GUI/Stylesheets/default.qss').read()
        self.setStyleSheet(qss_file)

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.main_grid = QSplitter()

        self.main_grid.setContentsMargins(0, 0, 0, 0)

        self.right_layout = QVBoxLayout()
        self.right_widget = QWidget()
        self.right_widget.setLayout(self.right_layout)


        self.right_grid = QGridLayout()
        self.right_grid.setColumnStretch(0, 3)
        self.right_grid.setColumnStretch(1, 1)

        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(0)
        self.right_grid.setContentsMargins(0, 0, 0, 0)
        self.right_grid.setSpacing(0)

        self.datapanel = DataInfoPanel(self)
        self.right_grid.addWidget(self.datapanel, 0, 1)

        self.left_area = MenuPanel()
        self.main_area = NeuralNetSection(self)

        self.toolbar = ToolbarPanel()
        self.toolbar.run_clicked.connect(self.run_clicked)
        self.right_layout.addWidget(self.toolbar)
        self.right_layout.addLayout(self.right_grid)

        self.right_grid.addWidget(self.main_area, 0, 0)

        self.main_grid.addWidget(self.left_area)
        self.main_grid.addWidget(self.right_widget)

        self.setCentralWidget(self.main_grid)
        self.main_grid.setStretchFactor(0, 5)
        self.main_grid.setStretchFactor(1, 7)

        self.show()