import sys

from PyQt5.QtWidgets import QApplication

from GUI.MainWindow import MainWindow

app = QApplication(sys.argv)
ex = MainWindow()
sys.exit(app.exec_())