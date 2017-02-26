from PyQt5.QtWidgets import QVBoxLayout, QLabel, QDialog, QDialogButtonBox


class ErrorDialog(QDialog):
    def __init__(self, parent=None, title="Error!"):
        super(ErrorDialog, self).__init__(parent)
        self.setObjectName("darkBg")
        self.setAutoFillBackground(True)
        layout = QVBoxLayout(self)
        lbl = QLabel(title, self)
        lbl.setObjectName("brightLabel")
        layout.addWidget(lbl)

        layout.addWidget(QDialogButtonBox(
                        QDialogButtonBox.Ok,
                        parent=self,
                        accepted=self.accept,
                        rejected=self.reject))

    @staticmethod
    def dialog(parent, title):
        d = ErrorDialog(parent, title)
        return d.exec_()
