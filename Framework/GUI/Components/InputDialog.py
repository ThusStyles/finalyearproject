from PyQt5.Qt import *
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QDialog, QCheckBox, QDialogButtonBox, QLineEdit


class InputDialog(QDialog):
    def __init__(self, parent=None, title="Dialog", placeholder="Example"):
        super(InputDialog, self).__init__(parent)
        self.setObjectName("darkBg")
        self.setAutoFillBackground(True)
        layout = QVBoxLayout(self)
        lbl = QLabel(title, self)
        lbl.setObjectName("brightLabel")
        layout.addWidget(lbl)

        self.input = QLineEdit()
        self.input.setPlaceholderText(placeholder)
        self.input.setAttribute(Qt.WA_MacShowFocusRect, False)
        layout.addWidget(self.input)


        layout.addWidget(QDialogButtonBox(
                        QDialogButtonBox.Ok|QDialogButtonBox.Cancel,
                        parent=self,
                        accepted=self.accept,
                        rejected=self.reject))

    @staticmethod
    def dialog(parent, title, placeholder):
        d = InputDialog(parent, title, placeholder)
        if d.exec_(): return d.input.text(), True
        else: return d.input.text(), False