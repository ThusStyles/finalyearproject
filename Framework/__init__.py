import sys

from PyQt5.QtWidgets import QApplication

from Framework.GUI.MainWindowNew import MainWindowNew

app = QApplication(sys.argv)
ex = MainWindowNew()
sys.exit(app.exec_())