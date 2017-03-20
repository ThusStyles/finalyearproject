import os

from PyQt5.QtCore import *
from PyQt5.QtGui import (QIcon)
from PyQt5.QtWidgets import QToolBar
from GUI.Helpers import PathHelpers


class ToolbarPanel(QToolBar):

    run_clicked = pyqtSignal()
    add_clicked = pyqtSignal()
    export_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def run(self):
        self.run_clicked.emit()

    def add_to_testing(self):
        self.add_clicked.emit()

    def export_sets(self):
        self.export_clicked.emit()

    def enable_action(self, x, y):
        play = self.actionAt(x, y)
        if play != 0:
            play.setEnabled(True)

    def disable_action(self, x, y):
        play = self.actionAt(x, y)
        if play != 0:
            play.setEnabled(False)

    def init_ui(self):
        self.setContentsMargins(0, 0, 0, 0)
        self.addAction(QIcon(PathHelpers.getPath("images/play-arrow.svg")), "Run Neural Network", self.run)
        self.addAction(QIcon(PathHelpers.getPath("images/add-plus-button.svg")), "Choose folder to be imported", self.add_to_testing)
        self.addAction(QIcon(PathHelpers.getPath("images/export.svg")), "Export sets into folders", self.export_sets)





