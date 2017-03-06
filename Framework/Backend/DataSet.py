import random
import os
import numpy as np
from matplotlib import pyplot as plt


class DataSet:

    training_limit = 100
    testing_limit = 200
    all_images = []
    training_images = []
    testing_images = []
    all_testing_images = []
    training_labels = []
    training_cls = []

    total_iterations = 0
    index_in_epoch = 0
    epochs_completed = 0
    one_hot_size = 0
    current_testing_max = 0

    img_shape = ()
    base_dir = os.path.dirname(os.path.realpath(__file__)) + "/../"

    def __init__(self, img_size):
        self.img_shape = (img_size, img_size)
        self.training_labels = np.array([])
        self.training_images = np.array([])
        self.labels = []


    def get_label_index(self, name):
        self.labels.append(name)
        self.labels = sorted(set(self.labels), key=lambda x: self.labels.index(x))
        for i, label in enumerate(self.labels):
            if str(label) == str(name):
                return i


    def add_sets_to_training_data(self, numberOfSets, itemNames, images):
        if len(images) == 0 or len(itemNames) == 0: return

        self.training_images = []
        self.training_labels = []

        self.one_hot_size = numberOfSets

        for i, image in enumerate(images):
            one_hot = [0 for x in range(self.one_hot_size)]
            index = self.get_label_index(itemNames[i])
            one_hot[index] = 1
            self.training_images.append(image)
            self.training_labels.append(one_hot)


        self.training_labels = np.array(self.training_labels)
        self.training_images = np.array(self.training_images)
        self.training_cls = np.argmax(self.training_labels, axis=1)
        self.index_in_epoch = 0
        self.total_iterations = 0
        self.epochs_completed = 0
        self.training_limit = len(self.training_images)

    def set_testing_data(self, images):
        self.all_testing_images = images
        self.new_testing_data()

    def add_to_testing_data(self, image):
        self.all_testing_images.append(image)

    def new_testing_data(self):
        self.testing_images = []
        self.current_testing_max = min(len(self.all_testing_images), self.testing_limit)

        for x in self.all_testing_images[0:self.current_testing_max]:
            self.testing_images.append(x)

        print("SIZE OF TESITNG IMAGES BEFORE", len(self.all_testing_images))
        self.all_testing_images = self.all_testing_images[self.current_testing_max:]
        print("SIZE OF TESITNG IMAGES AFTER", len(self.all_testing_images))

        self.testing_images = np.array(self.testing_images)
        np.random.shuffle(self.testing_images)


    def set_training_limit(self, training_limit):
        self.index_in_epoch = 0
        self.total_iterations = 0
        self.epochs_completed = 0
        self.training_limit = training_limit
        self.training_images = []
        self.testing_images = []
        self.training_labels = []
        self.testing_labels = []

        for x in self.all_images[0:self.training_limit]:
            self.training_labels.append(x[0])
            self.training_images.append(x[1])

        self.max_limit = min(len(self.all_images), (self.training_limit + self.testing_limit))

        for x in self.all_images[self.training_limit:self.max_limit]:
            self.testing_labels.append(x[0])
            self.testing_images.append(x[1])

        self.training_labels = np.array(self.training_labels)
        self.training_images = np.array(self.training_images)
        self.testing_images = np.array(self.testing_images)
        self.testing_labels = np.array(self.testing_labels)
        self.testing_cls = np.argmax(self.testing_labels, axis=1)
        self.training_cls = np.argmax(self.training_labels, axis=1)

        print(len(self.training_images))
        print(len(self.testing_images))
        print(len(self.testing_cls))
        print(len(self.training_cls))


    def plot_images(self, images, cls_true, cls_pred=None):
        assert len(images) == len(cls_true)

        # Create figure with 3x3 sub-plots.
        fig, axes = plt.subplots(3, 3)
        fig.subplots_adjust(hspace=0.3, wspace=0.3)

        for i, ax in enumerate(axes.flat):
            # Plot image.
            if i >= len(images): continue
            ax.imshow(images[i].reshape(self.img_shape), cmap='binary')

            # Show true and predicted classes.
            if cls_pred is None:
                xlabel = "True: {0}".format(cls_true[i])
            else:
                xlabel = "True: {0}, Pred: {1}".format(cls_true[i], cls_pred[i])

            # Show the classes as the label on the x-axis.
            ax.set_xlabel(xlabel)

            # Remove ticks from the plot.
            ax.set_xticks([])
            ax.set_yticks([])

        # Ensure the plot is shown correctly with multiple plots
        # in a single Notebook cell.
        plt.show()


    def next_batch(self, batch_size):
        batch_size = min(batch_size, self.training_limit)
        start = self.index_in_epoch
        self.index_in_epoch += batch_size
        if self.index_in_epoch > self.training_limit:
            # Finished epoch
            self.epochs_completed += 1
            # Shuffle the data
            perm = np.arange(self.training_limit)
            np.random.shuffle(perm)
            self.training_images = self.training_images[perm]
            self.training_labels = self.training_labels[perm]
            # Start next epoch
            start = 0
            self.index_in_epoch = batch_size
            assert batch_size <= self.training_limit
        end = self.index_in_epoch
        return self.training_images[start:end], self.training_labels[start:end]


