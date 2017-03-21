from PyQt5.QtWidgets import QVBoxLayout, QDialog

from GUI.Components import Set
from GUI.Sections import NeuralNetSection


class TestingWindow(QDialog):

    def __init__(self, parent=None, images=None):
        super(TestingWindow, self).__init__(parent)
        self.title = 'Convolutional Neural Network'
        self.left = 300
        self.top = 300
        self.images = images
        self.new_sets = []
        self.resize(960, 560)
        self.init_ui()

    def init_ui(self):

        testing_set = Set("Testing")
        testing_set.disable_set_operations()

        for image in self.images:
            testing_set.add_image(image)

        self.main_widget = NeuralNetSection([testing_set])
        self.main_widget.buttons_widget.setVisible(False)
        self.main_widget.empty_label.setVisible(False)
        self.main_widget.add_sets()
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.main_widget)
        self.setLayout(self.main_layout)

