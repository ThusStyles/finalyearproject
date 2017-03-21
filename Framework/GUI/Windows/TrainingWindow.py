from PyQt5.QtWidgets import QVBoxLayout, QDialog

from GUI.Components import Set
from GUI.Sections import NeuralNetSection


class TrainingWindow(QDialog):

    def __init__(self, parent=None, sets=None):
        super(TrainingWindow, self).__init__(parent)
        self.title = 'Convolutional Neural Network'
        self.left = 300
        self.top = 300
        self.sets = sets
        self.new_sets = []
        self.resize(960, 560)
        self.init_ui()

    def init_ui(self):

        for set in self.sets:
            new_set = Set(set.name)
            self.new_sets.append(new_set)
            for image in set.all_images:
                image = image.imageData
                new_set.add_image(image, False)
                new_set.disable_set_operations()

        self.main_widget = NeuralNetSection(self.new_sets)
        self.main_widget.buttons_widget.setVisible(True)
        self.main_widget.empty_label.setVisible(False)
        self.main_widget.add_sets()
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.main_widget)
        self.setLayout(self.main_layout)

