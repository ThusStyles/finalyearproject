import tensorflow as tf
import time
from datetime import timedelta
import numpy as np
from . import DataSet


class NeuralNet:
    # Convolutional Layer 1.
    filter_size1 = 5  # Convolution filters are 5 x 5 pixels.
    num_filters1 = 16  # There are 16 of these filters.

    # Convolutional Layer 2.
    filter_size2 = 5  # Convolution filters are 5 x 5 pixels.
    num_filters2 = 36  # There are 36 of these filters.

    # Fully-connected layer.
    fc_size = 128  # Number of neurons in fully-connected layer.

    # We know that the images are 44 pixels in each dimension.
    img_size = 44

    # Images are stored in one-dimensional arrays of this length.
    img_size_flat = img_size * img_size

    # Tuple with height and width of images used to reshape arrays.
    img_shape = (img_size, img_size)

    # Number of colour channels for the images: 1 channel for gray-scale.
    num_channels = 1

    # Number of classes, one class for each of 10 digits.
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
        print("NEURAL NET SIZE IS", self.num_classes)
        self.run()

    def new_weights(self, shape):
        return tf.Variable(tf.truncated_normal(shape, stddev=0.05))

    def new_biases(self, length):
        return tf.Variable(tf.constant(0.05, shape=[length]))

    def new_conv_layer(self, input,  # The previous layer.
                       num_input_channels,  # Num. channels in prev. layer.
                       filter_size,  # Width and height of each filter.
                       num_filters,  # Number of filters.
                       use_pooling=True):  # Use 2x2 max-pooling.

        # Shape of the filter-weights for the convolution.
        # This format is determined by the TensorFlow API.
        shape = [filter_size, filter_size, num_input_channels, num_filters]

        # Create new weights aka. filters with the given shape.
        weights = self.new_weights(shape=shape)

        # Create new biases, one for each filter.
        biases = self.new_biases(length=num_filters)

        # Create the TensorFlow operation for convolution.
        # Note the strides are set to 1 in all dimensions.
        # The first and last stride must always be 1,
        # because the first is for the image-number and
        # the last is for the input-channel.
        # But e.g. strides=[1, 2, 2, 1] would mean that the filter
        # is moved 2 pixels across the x- and y-axis of the image.
        # The padding is set to 'SAME' which means the input image
        # is padded with zeroes so the size of the output is the same.
        layer = tf.nn.conv2d(input=input,
                             filter=weights,
                             strides=[1, 1, 1, 1],
                             padding='SAME')

        # Add the biases to the results of the convolution.
        # A bias-value is added to each filter-channel.
        layer += biases

        # Use pooling to down-sample the image resolution?
        if use_pooling:
            # This is 2x2 max-pooling, which means that we
            # consider 2x2 windows and select the largest value
            # in each window. Then we move 2 pixels to the next window.
            layer = tf.nn.max_pool(value=layer,
                                   ksize=[1, 2, 2, 1],
                                   strides=[1, 2, 2, 1],
                                   padding='SAME')

        # Rectified Linear Unit (ReLU).
        # It calculates max(x, 0) for each input pixel x.
        # This adds some non-linearity to the formula and allows us
        # to learn more complicated functions.
        layer = tf.nn.relu(layer)

        # Note that ReLU is normally executed before the pooling,
        # but since relu(max_pool(x)) == max_pool(relu(x)) we can
        # save 75% of the relu-operations by max-pooling first.

        # We return both the resulting layer and the filter-weights
        # because we will plot the weights later.
        return layer, weights

    def flatten_layer(self, layer):
        # Get the shape of the input layer.
        layer_shape = layer.get_shape()

        # The shape of the input layer is assumed to be:
        # layer_shape == [num_images, img_height, img_width, num_channels]

        # The number of features is: img_height * img_width * num_channels
        # We can use a function from TensorFlow to calculate this.
        num_features = layer_shape[1:4].num_elements()

        # Reshape the layer to [num_images, num_features].
        # Note that we just set the size of the second dimension
        # to num_features and the size of the first dimension to -1
        # which means the size in that dimension is calculated
        # so the total size of the tensor is unchanged from the reshaping.
        layer_flat = tf.reshape(layer, [-1, num_features])

        # The shape of the flattened layer is now:
        # [num_images, img_height * img_width * num_channels]

        # Return both the flattened layer and the number of features.
        return layer_flat, num_features

    def new_fc_layer(self, input,  # The previous layer.
                     num_inputs,  # Num. inputs from prev. layer.
                     num_outputs,  # Num. outputs.
                     use_relu=True):  # Use Rectified Linear Unit (ReLU)?

        # Create new weights and biases.
        weights = self.new_weights(shape=[num_inputs, num_outputs])
        biases = self.new_biases(length=num_outputs)

        # Calculate the layer as the matrix multiplication of
        # the input and weights, and then add the bias-values.
        layer = tf.matmul(input, weights) + biases

        # Use ReLU?
        if use_relu:
            layer = tf.nn.relu(layer)

        return layer

    def get_test_accuracy(self, show_example_errors=False, callback=None):

        # Number of images in the test-set.
        num_test = len(self.dataset.testing_images)

        # Allocate an array for the predicted classes which
        # will be calculated in batches and filled into this array.
        cls_pred = np.zeros(shape=(num_test, self.num_classes), dtype=np.float64)
        keep_prob = tf.placeholder(tf.float32)

        # Now calculate the predicted classes for the batches.
        # We will just iterate through all the batches.
        # There might be a more clever and Pythonic way of doing this.

        # The starting index for the next batch is denoted i.
        i = 0

        while i < num_test:
            # The ending index for the next batch is denoted j.
            j = min(i + self.test_batch_size, num_test)

            # Get the images from the test-set between index i and j.
            images = self.dataset.testing_images[i:j]

            # Create a feed-dict with these images and labels.
            feed_dict = {self.x: images}

            # Calculate the predicted class using TensorFlow.
            #cls_pred[i:j] = self.session.run(self.y_pred_cls, feed_dict=feed_dict)

            cls_pred[i:j] = self.y_pred.eval(feed_dict=feed_dict, session=self.session)

            # Set the start-index for the next batch to the
            # end-index of the current batch.
            i = j

        if callback: callback(cls_pred)


    def plot_example_errors(self, cls_pred, correct):
        # This function is called from print_test_accuracy() below.

        # cls_pred is an array of the predicted class-number for
        # all images in the test-set.

        # correct is a boolean array whether the predicted class
        # is equal to the true class for each image in the test-set.

        # Negate the boolean array.
        incorrect = (correct == False)

        # Get the images from the test-set that have been
        # incorrectly classified.
        images = self.dataset.testing_images[incorrect]

        # Get the predicted classes for those images.
        cls_pred = cls_pred[incorrect]

        # Get the true classes for those images.
        cls_true = self.dataset.testing_cls[incorrect]

        # Plot the first 9 images.
        self.dataset.plot_images(images=images[0:9],
                    cls_true=cls_true[0:9],
                    cls_pred=cls_pred[0:9])

    def optimize(self, num_iterations, callback=None):
        # Ensure we update the global variable rather than a local copy.

        # Start-time used for printing time-usage below.
        start_time = time.time()

        for i in range(self.total_iterations,
                       self.total_iterations + num_iterations):

            # Get a batch of training examples.
            # x_batch now holds a batch of images and
            # y_true_batch are the true labels for those images.
            x_batch, y_true_batch = self.dataset.next_batch(self.train_batch_size)

            # Put the batch into a dict with the proper names
            # for placeholder variables in the TensorFlow graph.
            feed_dict_train = {self.x: x_batch,
                               self.y_true: y_true_batch}

            # Run the optimizer using this batch of training data.
            # TensorFlow assigns the variables in feed_dict_train
            # to the placeholder variables and then runs the optimizer.
            self.session.run(self.optimizer, feed_dict=feed_dict_train)

            if callback: callback((i + 1) / num_iterations)

            # Print status every 100 iterations.
            if i % 100 == 0:
                # Calculate the accuracy on the training-set.
                acc = self.session.run(self.accuracy, feed_dict=feed_dict_train)

                # Message for printing.
                msg = "Optimization Iteration: {0:>6}, Training Accuracy: {1:>6.1%}"

                # Print it.
                print(msg.format(i + 1, acc))

        # Update the total number of iterations performed.
        self.total_iterations += num_iterations

        # Ending time.
        end_time = time.time()

        # Difference between start and end-times.
        time_dif = end_time - start_time

        # Print the time-usage.
        print("Time usage: " + str(timedelta(seconds=int(round(time_dif)))))


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
        print(layer_conv1)
        layer_conv2, weights_conv2 = \
            self.new_conv_layer(input=layer_conv1,
                           num_input_channels=self.num_filters1,
                           filter_size=self.filter_size2,
                           num_filters=self.num_filters2,
                           use_pooling=True)
        print(layer_conv2)
        layer_flat, num_features = self.flatten_layer(layer_conv2)
        print(layer_flat)
        print(num_features)
        layer_fc1 = self.new_fc_layer(input=layer_flat,
                                 num_inputs=num_features,
                                 num_outputs=self.fc_size,
                                 use_relu=True)
        print(layer_fc1)
        layer_fc2 = self.new_fc_layer(input=layer_fc1,
                                 num_inputs=self.fc_size,
                                 num_outputs=self.num_classes,
                                 use_relu=False)
        print(layer_fc2)
        self.y_pred = tf.nn.softmax(layer_fc2)
        self.y_pred_cls = tf.argmax(self.y_pred, dimension=1)
        cross_entropy = tf.nn.softmax_cross_entropy_with_logits(logits=layer_fc2,
                                                                labels=self.y_true)
        cost = tf.reduce_mean(cross_entropy)

        self.optimizer = tf.train.AdamOptimizer(learning_rate=1e-4).minimize(cost)

        correct_prediction = tf.equal(self.y_pred_cls, self.y_true_cls)

        self.accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

        self.session.run(tf.global_variables_initializer())