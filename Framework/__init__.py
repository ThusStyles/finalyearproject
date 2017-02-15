from Framework.DataSet import DataSet
from Framework.NeuralNet import NeuralNet
from Framework.GUI.MainWindowNew import MainWindowNew
from PyQt5.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
ex = MainWindowNew()
sys.exit(app.exec_())