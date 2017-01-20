from Framework.DataSet import DataSet
from Framework.NeuralNet import NeuralNet

img_size = 44
training_limit = 100

dataSet = DataSet(training_limit, img_size)
dataSet.get_data()
neuralNet = NeuralNet(img_size, dataSet)
neuralNet.optimize(num_iterations=1000)

neuralNet.print_test_accuracy(show_example_errors=True)