import os
import gzip

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QMainWindow, QSplitter, QAction, QFileDialog
from PyQt5.QtCore import QThread
import numpy as np

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
        self.current_save = None
        self.init_ui()

    def update_progress(self, amount):
        self.left_area.progressModule.progress.setText("Running - " + str(amount) + "%")
        self.left_area.progressModule.progress.setValue(amount)

    def testing_finished(self, cls_pred):
        print("CLS PRED", cls_pred)

        for i, prob_array in enumerate(cls_pred):
            image = self.dataset.testing_images[i]
            pred_index = np.argmax(prob_array)
            prob = prob_array[pred_index]
            labelForDigit = self.dataset.labels[pred_index]
            print("LABEL IS ", labelForDigit)
            for set in self.main_area.sets:
                if set.name == labelForDigit:
                    item = set.add_image(image)
                    if prob <= 0.5:
                        item.set_important()

        self.dataset.new_testing_data()

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
            itemCount = len(set.all_images)
            for index in range(itemCount):
                item = set.all_images[index]
                if item == None: continue
                print(item)
                itemNames.append(set.name)
                itemData.append(item.imageData)
            set.clear()

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

    def open_sets(self):
        fileName, filter = QFileDialog.getOpenFileName(self, 'Open sets save', base_dir + "Framework/saves",
                                                       "Set Files (*.sets)")

        if fileName:
            print(fileName)
            inF = gzip.open(fileName, 'rb')
            s = inF.read()
            inF.close()
            lines = s.decode("utf-8").splitlines()
            setName = ""
            images = []
            self.main_area.clear_sets()
            for i, line in enumerate(lines):
                if ("Set:" in line and (len(images) > 0)):
                    self.main_area.create_new_set(setName, images)
                    images = []

                if "Set:" in line:
                    setName = line.replace("Set: ", "", 1)
                    print("SET NAME:", setName)
                else:
                    #Line is an image
                    pixels = line.split(",")
                    image = []
                    for pixel in pixels:
                        image.append(np.uint8(pixel))
                    images.append(np.array(image))

                if i == (len(lines) - 1):
                    print("images is ", images)
                    self.main_area.create_new_set(setName, images)

    def save_sets_as(self):
        self.current_save = None
        self.save_sets()

    def save_sets(self):

        if self.current_save:
            fileName = self.current_save
        else:
            fileName, filter = QFileDialog.getSaveFileName(self, 'Save sets', base_dir + "Framework/saves",
                                               "Set Files (*.sets)")
            self.current_save = fileName

        if fileName:
            sets = self.main_area.sets
            f = gzip.open(fileName, "wb")
            for set in sets:
                images = set.all_images
                f.write(bytes('Set: ' + set.name + '\n', encoding="utf-8"))
                for image in images:
                    print(image)
                    for i, pixel in enumerate(image.imageData):
                        extra = '' if i == (len(image.imageData) - 1) else ','
                        f.write(bytes(str(pixel) + extra, encoding="utf-8"))
                    f.write(bytes('\n', encoding="utf-8"))

            f.close()
            # os.remove(fileName)
            # os.rename(fileName + ".gz", fileName)




    def added_to_set(self, set_name):
        self.datapanel.increment_training_table(set_name)

    def removed_from_set(self, set_name):
        self.datapanel.decrement_training_table(set_name)

    def init_ui(self):
        self.dataset = DataSet(img_size)
        qss_file = open(base_dir + 'Framework/GUI/Stylesheets/default.qss').read()
        self.setStyleSheet(qss_file)

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.main_grid = QSplitter()
        self.main_grid.setObjectName("verticalSplitter")

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

        self.datapanel = DataInfoPanel()
        self.right_grid.addWidget(self.datapanel, 0, 1)

        self.left_area = MenuPanel()
        self.main_area = NeuralNetSection()
        self.main_area.added_to_set.connect(self.added_to_set)
        self.main_area.removed_from_set.connect(self.removed_from_set)

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

        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.setStatusTip('Save the current sets')
        save_action.triggered.connect(self.save_sets)

        save_action_as = QAction("&Save As", self)
        save_action_as.setStatusTip('New save for the current sets')
        save_action_as.triggered.connect(self.save_sets_as)

        open_action = QAction("&Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip('Open a sets save file')
        open_action.triggered.connect(self.open_sets)

        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(save_action_as)




        self.show()