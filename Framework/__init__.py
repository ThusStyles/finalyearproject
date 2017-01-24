from Framework.DataSet import DataSet
from Framework.NeuralNet import NeuralNet
from Framework.GUI.MainWindow import MainWindow
from PyQt5.QtWidgets import QApplication
import sys

img_size = 44

dataSet = DataSet(img_size)
#dataSet.get_data()

accuracies = []
training_limits = [10, 20, 50, 100, 500, 1000, 5000, 20000, 40000]


def doRun(amount):
    dataSet.set_training_limit(amount)
    neuralNet = NeuralNet(img_size, dataSet)
    neuralNet.optimize(num_iterations=2000)
    accuracies.append(neuralNet.get_test_accuracy())
    neuralNet.close()


app = QApplication(sys.argv)
ex = MainWindow()
sys.exit(app.exec_())