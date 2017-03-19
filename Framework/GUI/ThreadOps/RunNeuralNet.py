import numpy as np
from PyQt5.QtCore import QSettings, pyqtSignal, QObject, pyqtSlot

from Backend.NeuralNet import NeuralNet


class RunNeuralNet(QObject):

    finished = pyqtSignal()
    one_iteration = pyqtSignal(float)
    testing_finished = pyqtSignal(np.ndarray)
    created_neural_net = pyqtSignal(object)

    def __init__(self, dataset, img_size, num_classes):
        super().__init__()
        self.settings = QSettings("Theo Styles", "Convolutional Neural Network")
        self.dataset = dataset
        self.img_size = img_size
        self.num_classes = num_classes

    @pyqtSlot()
    def long_running(self):
        self.neuralNet = NeuralNet(self.img_size, self.dataset, self.num_classes)
        self.created_neural_net.emit(self.neuralNet)
        self.neuralNet.optimize(num_iterations=self.settings.value("iteration_amount", 1000), callback=self.finished_one_iteration)
        self.neuralNet.get_test_accuracy(show_example_errors=False, callback=self.finished_test_accuracy)

    def finished_test_accuracy(self, cls_pred):
        self.testing_finished.emit(cls_pred)
        self.finished.emit()

    def finished_one_iteration(self, amount):
        self.one_iteration.emit(int(amount * 100))