from PyQt5.QtCore import QSettings, Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QLineEdit, QFormLayout, QSpinBox, QPushButton


class SettingsSection(QWidget):

    settings_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def changed(self):
        self.save_button.setDisabled(False)
        self.save_button.setText("Save")

    def save_settings(self):
        self.settings.setValue("testing_amount", self.testing_set_size.value())
        self.settings.setValue("iteration_amount", self.iteration_size.value())
        self.settings.setValue("learning_rate", float(self.learning_rate.text()))
        self.save_button.setDisabled(True)
        self.save_button.setText("Saved")

    def init_ui(self):
        self.settings = QSettings("Theo Styles", "Convolutional Neural Network")
        self.setObjectName("settingsSection")
        self.overall_layout = QFormLayout()
        self.overall_layout.setFormAlignment(Qt.AlignLeft)

        self.testing_set_size = QSpinBox()
        self.testing_set_size.setMaximum(1000000)
        self.testing_set_size.setValue(self.settings.value("testing_amount", 100))
        self.testing_set_size.setAttribute(Qt.WA_MacShowFocusRect, False)

        self.iteration_size = QSpinBox()
        self.iteration_size.setMaximum(1000000)
        self.iteration_size.setValue(self.settings.value("iteration_amount", 100))
        self.iteration_size.setAttribute(Qt.WA_MacShowFocusRect, False)

        self.learning_rate = QLineEdit()
        self.learning_rate.setText(repr(self.settings.value("learning_rate", repr(1e-4))))
        self.learning_rate.setAttribute(Qt.WA_MacShowFocusRect, False)

        self.testing_set_size.valueChanged.connect(self.changed)
        self.iteration_size.valueChanged.connect(self.changed)
        self.learning_rate.textChanged.connect(self.changed)

        self.overall_layout.addRow("Testing set size per iteration", self.testing_set_size)
        self.overall_layout.addRow("Neural Network number of iterations", self.iteration_size)
        self.overall_layout.addRow("Learning rate", self.learning_rate)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)
        self.overall_layout.addRow("", self.save_button)

        self.setLayout(self.overall_layout)
