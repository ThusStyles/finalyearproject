import gzip
import os

import numpy as np
from PIL import Image
from PyQt5.QtCore import *

class SaveLoad(QObject):

    finished = pyqtSignal()
    create_set = pyqtSignal(str, object)
    add_to_training_set = pyqtSignal(str, object)
    add_to_testing_set = pyqtSignal(object)
    one_iteration = pyqtSignal(int, str)
    set_iteration_stats = pyqtSignal(list)
    set_classified_info = pyqtSignal(str, int, int)

    def __init__(self, filename=None, sets=None, testing_images=None, folder_name=None, iteration_stats=None):
        super().__init__()
        self.filename = filename
        self.sets = sets
        self.testing_images = testing_images
        self.folder_name = folder_name
        self.iteration_stats = iteration_stats

    def export_sets(self):
        total_image_count = 0
        images_done = 0

        for set in self.sets:
            total_image_count += len(set.all_images)

        for set in self.sets:
            set_dir = os.path.join(self.folder_name, set.name)
            if not os.path.exists(set_dir):
                os.makedirs(set_dir)
            images = set.all_images
            for i, image in enumerate(images):
                images_done += 1
                new_img = Image.fromarray(image.imageData.reshape(44, -1))
                img_title = image.title
                if not image.title:
                    img_title = set.name + "-" + str(i) + ".tif"
                new_img.save(os.path.join(set_dir, img_title))
                self.finished_one_iteration(images_done / (total_image_count - 1), "Exporting set " + set.name)

        self.finished.emit()

    def load_images(self):
        inF = gzip.open(self.filename, 'rb')
        s = inF.read()
        inF.close()
        lines = s.decode("utf-8").splitlines()
        setName = None
        training_images = []
        testing_images = []
        reading_status = 0
        num_lines = len(lines)
        for i, line in enumerate(lines):

            if "Iteration stats:" in line:
                reading_status = 2
            elif "Set:" in line:
                setName = line.replace("Set: ", "", 1)
                reading_status = 1
                self.create_set.emit(setName, [])
            elif "Icl:" in line:
                others = line.replace("Icl: ", "", 1).split(",")
                self.set_classified_info.emit(setName, int(others[0]), int(others[1]))
            elif "Testing set" in line:
                reading_status = 0
            else:
                # Line is an image
                pixels = line.split(",")
                image = []
                image_plain = []
                for pixel in pixels:
                    image_plain.append(pixel)
                    image.append(np.uint8(pixel))

                if len(image) == 0: continue
                if reading_status == 1:
                    self.add_to_training_set.emit(setName, [np.array(image)])
                elif reading_status == 0:
                    self.add_to_testing_set.emit(np.array(image))
                elif reading_status == 2:
                    # Reading iteration stats
                    self.set_iteration_stats.emit(image_plain)

            self.finished_one_iteration(i / (num_lines - 1), "Loading images")

        self.finished.emit()

    def save_images(self):

        f = gzip.open(self.filename, "wb")

        # Copy testing set to save
        testing_set = self.testing_images
        testing_set_len = len(testing_set)
        total_len = testing_set_len
        current_item = 0

        for set in self.sets:
            total_len += len(set.all_images)

        if self.iteration_stats and len(self.iteration_stats) > 0:
            f.write(bytes("Iteration stats:\n", encoding="utf-8"))
            for i, num in enumerate(self.iteration_stats):
                extra = '' if i == (len(self.iteration_stats) - 1) else ','
                f.write(bytes(str(num) + extra, encoding="utf-8"))
            f.write(bytes('\n', encoding="utf-8"))

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
            images = set.all_images
            f.write(bytes('Set: ' + set.name + '\n', encoding="utf-8"))
            f.write(bytes("Icl: " + str(set.incorrectly_classified_local) + ',' +  str(set.incorrectly_classified) +' \n', encoding="utf-8"))
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