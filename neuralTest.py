from PIL import Image, ImageChops, ImageOps
import os
from skimage import io
import numpy as np
import random
from matplotlib import pyplot as plt
import tensorflow as tf
import time
from datetime import timedelta
from sklearn.metrics import confusion_matrix

all_images = []

training_limit = 100

training_images = []
testing_images = []

training_labels = []
testing_labels = []



# Counter for total number of iterations performed so far.
total_iterations = 0
index_in_epoch = 0
epochs_completed = 0
base_dir = "/Users/theostyles/PycharmProjects/extractLetters/"





#resize_images()
get_data()

testing_cls = np.argmax(testing_labels, axis=1)
training_cls = np.argmax(training_labels, axis=1)

testing_images = np.array(testing_images)
training_images = np.array(training_images)
testing_labels = np.array(testing_labels)
training_labels = np.array(training_labels)

print("Size of:")
print("- Training-set:\t\t{}".format(len(training_images)))
print("- Test-set:\t\t{}".format(len(testing_images)))
print(training_images[0].shape)
print(testing_images[0].shape)



# Split the test-set into smaller batches of this size.
test_batch_size = 256


optimize(num_iterations=2000)
print_test_accuracy(show_example_errors=True)