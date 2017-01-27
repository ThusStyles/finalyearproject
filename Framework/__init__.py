from Framework.DataSet import DataSet
from Framework.NeuralNet import NeuralNet
from Framework.GUI.MainWindow import MainWindow
from PyQt5.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
ex = MainWindow()
sys.exit(app.exec_())