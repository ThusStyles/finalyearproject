import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from GUI.Helpers import PathHelpers

from GUI.Windows.MainWindow import MainWindow
import ctypes


myappid = u'theostyles.convneuralnet.1.0'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
app = QApplication(sys.argv)
app.setWindowIcon(QIcon(PathHelpers.getPath("images/logo.png")))
ex = MainWindow()
sys.exit(app.exec_())