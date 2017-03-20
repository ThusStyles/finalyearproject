import os
import copy
import numpy as np
from PIL import Image
from PyQt5.QtCore import QThread, QSettings, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QMainWindow, QSplitter, QAction, QFileDialog, QDialog, QScrollArea

from Backend import DataSet
from GUI.Panels import DataInfoPanel, MenuPanel, ToolbarPanel
from GUI.Sections import NeuralNetSection, SettingsSection
from GUI.ThreadOps import RunNeuralNet, SaveLoad
from GUI.Components import ErrorDialog
from GUI.Components import Set


class TrainingWindow(QDialog):

    def __init__(self, parent=None, sets=None):
        super(TrainingWindow, self).__init__(parent)
        self.title = 'Convolutional Neural Network'
        self.left = 300
        self.top = 300
        self.first_run = True
        self.current_save = None
        self.sets = sets
        self.new_sets = []
        self.resize(960, 560)
        self.init_ui()

    def init_ui(self):

        self.overall_layout = QVBoxLayout()
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
        self.main_widget.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.overall_layout.setContentsMargins(0, 0, 0, 0)

        self.overall_layout.addWidget(self.scroll, 1)
        self.overall_layout.addStretch()
        self.setLayout(self.overall_layout)

        for set in self.sets:
            new_set = Set(set.name)
            self.new_sets.append(new_set)
            for image in set.all_images:
                image = image.imageData
                new_set.add_image(image, False)
            self.main_layout.insertWidget(self.main_layout.count() - 1, new_set)

