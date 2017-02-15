import os

from PyQt5.QtCore import *
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QScrollArea, QAbstractItemView, QInputDialog, QMessageBox

from Framework.GUI.Components import ImageGrid, CustomPushButton

img_size = 44
base_dir = os.path.dirname(os.path.realpath(__file__)) + "/../../"


class NeuralNetSection(QWidget):

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
        self.sets = []

    def create_new_set(self, name, items):
        set_widget = QWidget()
        overall_layout = QVBoxLayout()
        label = QLabel("Set - " + name)
        overall_layout.setContentsMargins(0, 0, 0, 0)
        overall_layout.setSpacing(0)
        set_widget.setObjectName("setLayout")
        label.setObjectName("setLabel")
        image_grid = ImageGrid(name, self.data_panel)
        self.sets.append(image_grid)
        overall_layout.addWidget(label)
        overall_layout.addWidget(image_grid)
        set_widget.setLayout(overall_layout)

        self.main_widget.layout().insertWidget(self.main_widget.layout().count() - 1, set_widget)

        for item in items:
            item.parentIndex = name
            print(item)
            image_grid.addItem(item)


    def ask_for_set_name(self):

        if len(self.initial_image_grid.selectedItems()) == 0:
            self.show_error("Please select items to create a new set")
        else:
            text, ok = QInputDialog.getText(self, 'Convolutional Neural Network: New Set', 'Enter the name for the new set:')
            if len(text) == 0:
                self.show_error("You must enter a set name")
            elif ok:
                to_add = []
                exists = False
                setToAdd = None
                for set in self.sets:
                    if set.label == text:
                        exists = True
                        setToAdd = set

                for item in self.initial_image_grid.selectedItems():
                    taken = self.initial_image_grid.takeItem(self.initial_image_grid.row(item))
                    to_add.append(taken)
                    if exists:
                        setToAdd.addItem(taken)

                if not exists:
                    self.create_new_set(text, to_add)


    def show_error(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        msg.setText("Error!")
        msg.setInformativeText(message)
        msg.setWindowTitle("Convolutional Neural Network: Error")
        msg.setStandardButtons(QMessageBox.Ok)

        retval = msg.exec_()

    def init_ui(self):
        self.data_panel = self.main_window.datapanel
        self.overall_layout = QVBoxLayout()
        self.top_layout = QHBoxLayout()

        self.initial_image_grid = ImageGrid("Initial")
        self.initial_image_grid.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.add_button = CustomPushButton("+")
        self.trash_button = CustomPushButton("Delete")

        self.initial_image_grid.populate_from_folder(base_dir + "page-0400-cropped")

        self.top_grid_buttons = QVBoxLayout()
        self.top_grid_buttons.addWidget(self.add_button)
        self.top_grid_buttons.addStretch()
        self.top_grid_buttons.addWidget(self.trash_button)

        self.add_button.clicked.connect(self.ask_for_set_name)

        self.top_layout.addWidget(self.initial_image_grid)
        self.top_layout.addLayout(self.top_grid_buttons)

        self.overall_layout.addLayout(self.top_layout)

        self.main_layout = QVBoxLayout()



        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)

        self.main_widget = QWidget()
        self.main_layout.addStretch()
        self.main_widget.setLayout(self.main_layout)
        self.scroll.setWidget(self.main_widget)

        self.scroll.setContentsMargins(0, 0, 0, 0)
        self.main_widget.setContentsMargins(0, 0, 30, 0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.overall_layout.addWidget(self.scroll, 1)
        self.overall_layout.addStretch()
        self.setLayout(self.overall_layout)

        self.overall_layout.addStretch()




