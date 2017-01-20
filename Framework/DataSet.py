import random
import os
from skimage import io
from PIL import Image, ImageChops, ImageOps
import numpy as np
from matplotlib import pyplot as plt

class DataSet:

    training_limit = 100
    training_images = []
    testing_images = []
    training_labels = []
    testing_labels = []
    testing_cls = []
    training_cls = []

    total_iterations = 0
    index_in_epoch = 0
    epochs_completed = 0

    img_shape = ()
    base_dir = "/Users/theostyles/PycharmProjects/extractLetters/"

    def __init__(self, training_limit, img_size):
        self.training_limit = training_limit
        self.img_shape = (img_size, img_size)

    def get_training_cls(self):
        return self.training_cls

    def get_testing_cls(self):
        return self.testing_cls

    def get_training_data(self):
        return self.training_images

    def get_training_labels(self):
        return self.training_labels

    def get_testing_data(self):
        return self.testing_images

    def get_testing_labels(self):
        return self.testing_labels

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

    def get_data(self):

        all_images = []

        for x in range(10):
            dir = self.base_dir + str(x) + "-cropped"
            os.chdir(dir)
            filelist = [f for f in os.listdir(dir) if f.endswith(".tif")]

            for f in filelist:
                one_hot = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                one_hot[x] = 1
                all_images.append((one_hot, io.imread(f, as_grey=True).reshape(-1)))

        random.shuffle(all_images)

        for x in all_images[0:self.training_limit]:
            self.training_labels.append(x[0])
            self.training_images.append(x[1])

        max_limit = len(all_images) if (self.training_limit + 5000 > len(all_images)) else  (self.training_limit + 5000)

        for x in all_images[self.training_limit:max_limit]:
            self.testing_labels.append(x[0])
            self.testing_images.append(x[1])

        self.training_labels = np.array(self.training_labels)
        self.training_images = np.array(self.training_images)
        self.testing_images = np.array(self.testing_images)
        self.testing_labels = np.array(self.testing_labels)
        self.testing_cls = np.argmax(self.testing_labels, axis=1)
        self.training_cls = np.argmax(self.training_labels, axis=1)

        print("Size of:")
        print("- Training-set:\t\t{}".format(len(self.training_images)))
        print("- Test-set:\t\t{}".format(len(self.testing_images)))


    def resize_images(self):
        size = self.img_shape
        # Empty results
        for x in range(10):
            dir = self.base_dir + str(x)
            os.chdir(dir)
            filelist = [f for f in os.listdir(dir) if f.endswith(".tif")]

            for f in filelist:
                image = Image.open(dir + "/" + f)
                image = image.convert('L')
                image = ImageOps.invert(image)
                image = ImageOps.grayscale(image)
                image.thumbnail(size, Image.ANTIALIAS)
                image_size = image.size

                thumb = image.crop((0, 0, size[0], size[1]))

                offset_x = max((size[0] - image_size[0]) // 2, 0)
                offset_y = max((size[1] - image_size[1]) // 2, 0)

                thumb = ImageChops.offset(thumb, offset_x, offset_y)
                F_OUT = dir + "-cropped/" + f

                thumb.save(F_OUT)


