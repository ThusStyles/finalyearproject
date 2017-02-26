from PyQt5.QtWidgets import QVBoxLayout, QLabel, QDialog, QCheckBox, QDialogButtonBox


class CustomDialog(QDialog):
    def __init__(self, parent=None, title="Dialog"):
        super(CustomDialog, self).__init__(parent)
        self.setObjectName("darkBg")
        self.setAutoFillBackground(True)
        layout = QVBoxLayout(self)
        lbl = QLabel(title, self)
        lbl.setObjectName("brightLabel")
        layout.addWidget(lbl)

        self.dontShowCBox = QCheckBox("Don't show this again")
        layout.addWidget(self.dontShowCBox)

        layout.addWidget(QDialogButtonBox(
                        QDialogButtonBox.Ok|QDialogButtonBox.Cancel,
                        parent=self,
                        accepted=self.accept,
                        rejected=self.reject))

    @staticmethod
    def dialog(parent, title):
        d = CustomDialog(parent, title)
        if d.exec_(): return True, d.dontShowCBox.isChecked()
        else: return False, False