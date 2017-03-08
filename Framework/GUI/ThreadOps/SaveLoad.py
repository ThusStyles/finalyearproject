import os

from PyQt5.QtCore import *
from Framework.Backend.NeuralNet import NeuralNet
import numpy as np
import gzip

class SaveLoad(QObject):

    finished = pyqtSignal()
    create_set = pyqtSignal(str, object)
    add_to_training_set = pyqtSignal(str, object)
    add_to_testing_set = pyqtSignal(object)
    one_iteration = pyqtSignal(int, str)

    def __init__(self, filename, sets=None, testing_images=None):
        super().__init__()
        self.filename = filename
        self.sets = sets
        self.testing_images = testing_images


    def load_images(self):
        inF = gzip.open(self.filename, 'rb')
        s = inF.read()
        inF.close()
        lines = s.decode("utf-8").splitlines()
        setName = None
        training_images = []
        testing_images = []
        reading_training_set = False
        reading_testing_set = False
        num_lines = len(lines)
        for i, line in enumerate(lines):

            if "Set:" in line:
                setName = line.replace("Set: ", "", 1)
                reading_testing_set = False
                reading_training_set = True
                self.create_set.emit(setName, [])
            elif "Testing set" in line:
                reading_training_set = False
                reading_testing_set = True
            else:
                # Line is an image
                pixels = line.split(",")
                image = []
                for pixel in pixels:
                    image.append(np.uint8(pixel))
                if len(image) == 0: continue
                if reading_training_set:
                    self.add_to_training_set.emit(setName, [np.array(image)])
                elif reading_testing_set:
                    self.add_to_testing_set.emit(np.array(image))

            self.finished_one_iteration(i / (num_lines - 1), "Loading images")

        self.finished.emit()

    def save_images(self):

        f = gzip.open(self.filename, "wb")

        # Copy testing set to save
        testing_set = self.testing_images
        testing_set_len = len(testing_set)
        print("SAVING ", testing_set_len, "TESTING IMAGES")
        total_len = testing_set_len
        current_item = 0

        for set in self.sets:
            total_len += len(set.all_images)

        if testing_set_len > 0:
            f.write(bytes('Testing set\n', encoding="utf-8"))
            for image in testing_set:
                for i, pixel in enumerate(image):
                    extra = '' if i == (len(image) - 1) else ','
                    f.write(bytes(str(pixel) + extra, encoding="utf-8"))
                f.write(bytes('\n', encoding="utf-8"))
                current_item += 1
                self.finished_one_iteration(current_item / total_len, "Saving images")

        for set in self.sets:
            print("DOING SET")
            images = set.all_images
            f.write(bytes('Set: ' + set.name + '\n', encoding="utf-8"))
            for image in images:
                for i, pixel in enumerate(image.imageData):
                    extra = '' if i == (len(image.imageData) - 1) else ','
                    f.write(bytes(str(pixel) + extra, encoding="utf-8"))
                f.write(bytes('\n', encoding="utf-8"))
                current_item += 1
                self.finished_one_iteration(current_item / total_len, "Saving images")

        f.close()

    def finished_one_iteration(self, amount, label):
        self.one_iteration.emit(int(amount * 100), label)