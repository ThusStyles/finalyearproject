import tensorflow as tf
import time
from datetime import timedelta
import numpy as np
from PyQt5.QtCore import QSettings


class NeuralNet:

    # Convolutional Layer 1.
    filter_size1 = 5
    num_filters1 = 16

    # Convolutional Layer 2.
    filter_size2 = 5
    num_filters2 = 36

    # Fully-connected layer.
    fc_size = 128  # Number of neurons in fully-connected layer.

    # Colour channels for gray scale images
    num_channels = 1
    num_classes = 10

    total_iterations = 0

    train_batch_size = 64
    test_batch_size = 256
    session = None
    accuracy = None
    optimizer = None
    y_true = None
    y_pred = None
    y_pred_cls = None
    y_true_cls = None
    x = None
    dataset = None

    def __init__(self, img_size, dataset, num_classes):
        self.img_size = img_size
        self.img_size_flat = img_size * img_size
        self.img_shape = (img_size, img_size)
        self.num_classes = num_classes
        self.dataset = dataset
        self.session = tf.Session()
        self.settings = QSettings("Theo Styles", "Convolutional Neural Network")
        self.img_size = self.settings.value("img_size", 44)
        self.img_size_flat = img_size * img_size
        self.img_shape = (img_size, img_size)
        self.run()

    def new_weights(self, shape):
        return tf.Variable(tf.truncated_normal(shape, stddev=0.05))

    def new_biases(self, length):
        return tf.Variable(tf.constant(0.05, shape=[length]))

    def new_conv_layer(self, input,
                       num_input_channels,
                       filter_size,
                       num_filters,
                       use_pooling=True):

        shape = [filter_size, filter_size, num_input_channels, num_filters]

        weights = self.new_weights(shape=shape)

        biases = self.new_biases(length=num_filters)

        layer = tf.nn.conv2d(input=input,
                             filter=weights,
                             strides=[1, 1, 1, 1],
                             padding='SAME')

        layer += biases

        if use_pooling:
            layer = tf.nn.max_pool(value=layer,
                                   ksize=[1, 2, 2, 1],
                                   strides=[1, 2, 2, 1],
                                   padding='SAME')

        layer = tf.nn.relu(layer)

        return layer, weights

    def flatten_layer(self, layer):
        layer_shape = layer.get_shape()
        num_features = layer_shape[1:4].num_elements()
        layer_flat = tf.reshape(layer, [-1, num_features])
        return layer_flat, num_features

    def get_fully_connected_layer(self, input, num_inputs, num_outputs, use_relu=True):

        weights = self.new_weights(shape=[num_inputs, num_outputs])
        biases = self.new_biases(length=num_outputs)

        layer = tf.matmul(input, weights) + biases

        if use_relu:
            layer = tf.nn.relu(layer)

        return layer

    def get_test_accuracy(self, show_example_errors=False, callback=None):

        num_test = len(self.dataset.testing_images)

        cls_pred = np.zeros(shape=(num_test, self.num_classes), dtype=np.float64)
        keep_prob = tf.placeholder(tf.float32)

        i = 0

        while i < num_test:

            j = min(i + self.test_batch_size, num_test)
            images = self.dataset.testing_images[i:j]
            feed_dict = {self.x: images}
            cls_pred[i:j] = self.y_pred.eval(feed_dict=feed_dict, session=self.session)

            i = j

        if callback: callback(cls_pred)

    def optimize(self, num_iterations, callback=None):

        for i in range(self.total_iterations,
                       self.total_iterations + num_iterations):

            x_batch, y_true_batch = self.dataset.next_batch(self.train_batch_size)

            feed_dict_train = {self.x: x_batch,
                               self.y_true: y_true_batch}
            self.session.run(self.optimizer, feed_dict=feed_dict_train)

            if callback: callback((i + 1) / num_iterations)

            if i % 100 == 0:
                acc = self.session.run(self.accuracy, feed_dict=feed_dict_train)

        self.total_iterations += num_iterations

    def close(self):
        self.session.close()

    def run(self):

        # START CONVOLUTION
        self.x = tf.placeholder(tf.float32, shape=[None, self.img_size_flat], name='x')
        x_image = tf.reshape(self.x, [-1, self.img_size, self.img_size, self.num_channels])
        self.y_true = tf.placeholder(tf.float32, shape=[None, self.num_classes], name='y_true')
        self.y_true_cls = tf.argmax(self.y_true, dimension=1)
        layer_conv1, weights_conv1 = \
            self.new_conv_layer(input=x_image,
                           num_input_channels=self.num_channels,
                           filter_size=self.filter_size1,
                           num_filters=self.num_filters1,
                           use_pooling=True)
        layer_conv2, weights_conv2 = \
            self.new_conv_layer(input=layer_conv1,
                           num_input_channels=self.num_filters1,
                           filter_size=self.filter_size2,
                           num_filters=self.num_filters2,
                           use_pooling=True)
        layer_flat, num_features = self.flatten_layer(layer_conv2)
        layer_fc1 = self.get_fully_connected_layer(input=layer_flat,
                                 num_inputs=num_features,
                                 num_outputs=self.fc_size,
                                 use_relu=True)
        layer_fc2 = self.get_fully_connected_layer(input=layer_fc1,
                                 num_inputs=self.fc_size,
                                 num_outputs=self.num_classes,
                                 use_relu=False)

        self.y_pred = tf.nn.softmax(layer_fc2)
        self.y_pred_cls = tf.argmax(self.y_pred, dimension=1)
        cross_entropy = tf.nn.softmax_cross_entropy_with_logits(logits=layer_fc2,
                                                                labels=self.y_true)
        cost = tf.reduce_mean(cross_entropy)

        self.optimizer = tf.train.AdamOptimizer(learning_rate=self.settings.value("learning_rate", 1e-4)).minimize(cost)

        correct_prediction = tf.equal(self.y_pred_cls, self.y_true_cls)
        self.accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
        self.session.run(tf.global_variables_initializer())