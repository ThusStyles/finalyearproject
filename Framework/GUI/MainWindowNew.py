import os

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QMainWindow, QSplitter

from Framework.GUI.NeuralNetSection import NeuralNetSection
from Framework.GUI.Panels.DataInfoPanel import DataInfoPanel
from Framework.GUI.Panels.MenuPanel import MenuPanel
from Framework.GUI.Panels.ToolbarPanel import ToolbarPanel

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
        self.init_ui()

    def init_ui(self):
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
        self.right_layout.addWidget(self.toolbar)
        self.right_layout.addLayout(self.right_grid)

        self.right_grid.addWidget(self.main_area, 0, 0)

        self.main_grid.addWidget(self.left_area)
        self.main_grid.addWidget(self.right_widget)

        self.setCentralWidget(self.main_grid)
        self.main_grid.setStretchFactor(0, 1)
        self.main_grid.setStretchFactor(1, 2)

        self.show()