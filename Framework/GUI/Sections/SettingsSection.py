from PyQt5.QtCore import QSettings, Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QFormLayout, QSpinBox, QPushButton, QDoubleSpinBox, QCheckBox


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
        self.settings.setValue("learning_rate", self.learning_rate.value())
        self.settings.setValue("limit_to_one_initially", self.limit_to_one_initially.isChecked())
        self.save_button.setDisabled(True)
        self.save_button.setText("Saved")

    def init_ui(self):
        self.settings = QSettings("Theo Styles", "Convolutional Neural Network")
        self.setObjectName("settingsSection")
        self.overall_layout = QFormLayout()
        self.overall_layout.setFormAlignment(Qt.AlignLeft)

        self.testing_set_size = QSpinBox()
        self.testing_set_size.setMaximum(1000000)
        self.testing_set_size.setSingleStep(100)
        self.testing_set_size.setValue(self.settings.value("testing_amount", 100))
        self.testing_set_size.setAttribute(Qt.WA_MacShowFocusRect, False)

        self.iteration_size = QSpinBox()
        self.iteration_size.setMaximum(1000000)
        self.iteration_size.setSingleStep(100)
        self.iteration_size.setValue(self.settings.value("iteration_amount", 100))
        self.iteration_size.setAttribute(Qt.WA_MacShowFocusRect, False)

        self.learning_rate = QDoubleSpinBox()
        self.learning_rate.setSingleStep(1e-4)
        self.learning_rate.setMaximum(1)
        self.learning_rate.setMinimum(0)
        self.learning_rate.setDecimals(4)
        self.learning_rate.setValue(float(self.settings.value("learning_rate", 1e-4)))
        self.learning_rate.setAttribute(Qt.WA_MacShowFocusRect, False)

        self.limit_to_one_initially = QCheckBox()
        bool_val = self.settings.value("limit_to_one_initially") == "true"
        self.limit_to_one_initially.setChecked(bool_val)
        self.limit_to_one_initially.setAttribute(Qt.WA_MacShowFocusRect, False)

        self.testing_set_size.valueChanged.connect(self.changed)
        self.iteration_size.valueChanged.connect(self.changed)
        self.learning_rate.valueChanged.connect(self.changed)
        self.limit_to_one_initially.stateChanged.connect(self.changed)

        self.overall_layout.addRow("Testing set size per iteration", self.testing_set_size)
        self.overall_layout.addRow("Neural Network number of iterations", self.iteration_size)
        self.overall_layout.addRow("Learning rate", self.learning_rate)
        self.overall_layout.addRow("Limit to one image per set initially?", self.limit_to_one_initially)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)
        self.overall_layout.addRow("", self.save_button)

        self.setLayout(self.overall_layout)
