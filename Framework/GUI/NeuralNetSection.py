import os

from PyQt5.QtCore import *
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QScrollArea, QAbstractItemView, QInputDialog, \
    QMessageBox, QLineEdit, QComboBox, QSplitter
from PyQt5.QtGui import QStandardItem

from Framework.GUI.Components import ImageGrid, CustomPushButton, CustomComboBox, Set, CustomDialog, ErrorDialog, InputDialog
import numpy as np

img_size = 44
base_dir = os.path.dirname(os.path.realpath(__file__)) + "/../../"


class NeuralNetSection(QWidget):

    added_to_set = pyqtSignal(str)
    removed_from_set = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.sets = []
        self.trash_set = None
        self.expand_state = False
        self.dont_ask = False
        self.dont_ask_trash = False
        self.current_index = 0
        self.selected_items = []

    def expand_clicked(self):
        if self.expand_state:
            self.expand_all()
            self.expand_all_button.setText("Hide all -")
        else:
            self.hide_all()
            self.expand_all_button.setText("Expand all +")

        self.expand_state = not self.expand_state


    def expand_all(self):
        for set in self.sets:
            set.expand()

    def hide_all(self):
        for set in self.sets:
            set.hide()

    def trash_clicked(self):
        ok = False
        if not self.dont_ask_trash:
            ok, dont_ask_trash = CustomDialog.dialog(self, "Are you sure you want to add items to the trash set?")
            self.dont_ask_trash = dont_ask_trash

        if self.dont_ask_trash or ok:
            index = self.initial_image_grid.currentRow()
            trash_set = self.add_or_create_set("Trash")
            self.initial_image_grid.setCurrentRow(index)
            if not self.trash_set:
                self.sets.remove(trash_set)
            self.trash_set = trash_set


    def clicked_set(self, set):
        othersSelected = False
        trash_selected = False if not self.trash_set else len(self.trash_set.image_grid.selectedIndexes()) > 0
        for otherSet in self.sets:
            if len(otherSet.image_grid.selectedIndexes()) > 0 or trash_selected:
                othersSelected = True
                break
        if not othersSelected: return
        if len(set.image_grid.selectedIndexes()) > 0: return

        print("None selected on set " + set.name)

        if not self.dont_ask:
            ok, dont_ask = CustomDialog.dialog(self, "Are you sure you want to add items to set " + set.name + "?")
            self.dont_ask = dont_ask

        if self.dont_ask or ok:
            for oneSet in self.sets:
                selectedItems = oneSet.image_grid.selectedItems()
                for selectedItem in selectedItems:
                    item = oneSet.takeFromBoth(oneSet.image_grid.row(selectedItem))
                    set.addItem(item)

            for selectedItem in self.trash_set.image_grid.selectedItems():
                item = self.trash_set.takeFromBoth(self.trash_set.image_grid.row(selectedItem))
                set.addItem(item)

        set.hidden = True

    def added_to_set_event(self, set_name):
        self.added_to_set.emit(set_name)

    def removed_from_set_event(self, set_name):
        self.removed_from_set.emit(set_name)

    def is_existing_set(self, name):
        for set in self.sets:
            if set.name == name:
                ErrorDialog.dialog(self, "There is already a set with this name")
                return True
        return False

    def rename_set(self, set, new_name):
        if self.is_existing_set(new_name): return
        set.set_name(new_name)

    def delete_set(self, to_delete):
        for set in self.sets:
            if set == to_delete:
                self.main_layout.removeWidget(to_delete)
                self.sets.remove(to_delete)
                to_delete.deleteLater()

    def create_new_set_with_selected(self, name, old_set):
        if self.is_existing_set(name): return
        selected = old_set.image_grid.selectedItems()
        items = []
        for sItem in selected:
            item = old_set.takeItem(old_set.image_grid.row(sItem))
            items.append(item)
        print("ITEMS ARE ", items)
        self.create_new_set(name, items)

    def clear_sets(self):
        for set in self.sets:
            self.main_layout.removeWidget(set)
            set.deleteLater()
        self.sets = []

    def create_new_set(self, name, items):
        if name == "": return
        new_set = Set(name)
        new_set.added_image.connect(self.added_to_set_event)
        new_set.removed_image.connect(self.removed_from_set_event)
        new_set.clicked_set.connect(self.clicked_set)
        new_set.create_new_set.connect(self.create_new_set_with_selected)
        new_set.rename_set_sig.connect(self.rename_set)
        new_set.delete_set_sig.connect(self.delete_set)

        if len(items) > 0:
            if isinstance(items[0], (np.ndarray, np.generic)):
                new_set.add_images(items)
            else:
                new_set.add_items(items)
        self.sets.append(new_set)
        if self.empty_label:
            self.main_layout.removeWidget(self.empty_label)
            self.empty_label.deleteLater()
            self.empty_label = None

        self.main_layout.insertWidget(self.main_layout.count() - 1, new_set)
        return new_set

    def add_or_create_set(self, name):
        to_add = []
        exists = False
        setToAdd = None

        for set in self.sets:
            if set.name == name:
                exists = True
                setToAdd = set

        if name == "Trash" and self.trash_set:
            setToAdd = self.trash_set
            exists = True

        for item in self.initial_image_grid.selectedItems():
            taken = self.initial_image_grid.takeItem(self.initial_image_grid.row(item))
            to_add.append(taken)
            if exists:
                setToAdd.addItem(taken)

        if not exists:
            return self.create_new_set(name, to_add)
        else:
            return setToAdd

    def ask_for_set_name(self):

        if len(self.initial_image_grid.selectedItems()) == 0:
            self.show_error("Please select items to create a new set")
        else:
            text, ok = InputDialog.dialog(self, 'Enter the name for the new set:', "Set name...")
            if len(text) == 0:
                self.show_error("You must enter a set name")
            elif ok:
                for set in self.sets:
                    if set.name == text:
                        ErrorDialog.dialog(self, "There is already a set with this name")
                        index = self.initial_image_grid.currentRow() + 1
                        self.initial_image_grid.setCurrentRow(index)
                        return
                index = self.initial_image_grid.currentRow()
                self.add_or_create_set(text)
                self.initial_image_grid.setCurrentRow(index)


    def show_error(self, message):
        ErrorDialog.dialog(self, message)

    def init_ui(self):
        self.overall_layout = QVBoxLayout()

        self.main_splitter = QSplitter()
        self.main_splitter.setOrientation(Qt.Vertical)

        self.top_widget = QWidget()
        self.top_layout = QHBoxLayout()

        self.initial_image_grid = ImageGrid()
        self.add_button = CustomPushButton("+")
        self.add_button.setToolTip("Create a new set with the selected images")
        self.trash_button = CustomPushButton("Delete")
        self.trash_button.clicked.connect(self.trash_clicked)
        self.trash_button.setToolTip("Add to the trash set")

        self.top_widget.setLayout(self.top_layout)

        self.initial_image_grid.populate_from_folder(base_dir + "page-0400-cropped")

        self.top_grid_buttons = QVBoxLayout()
        self.top_grid_buttons.addWidget(self.add_button)
        self.top_grid_buttons.addStretch()
        self.top_grid_buttons.addWidget(self.trash_button)

        self.add_button.clicked.connect(self.ask_for_set_name)

        self.top_layout.addWidget(self.initial_image_grid)
        self.top_layout.addLayout(self.top_grid_buttons)

        self.lower_layout = QVBoxLayout()
        self.lower_widget = QWidget()
        self.lower_widget.setLayout(self.lower_layout)

        self.buttons_layout = QHBoxLayout()
        self.expand_all_button = CustomPushButton("Hide All -")
        self.expand_all_button.setToolTip("Toggles visibility of sets below")
        self.expand_all_button.clicked.connect(self.expand_clicked)

        self.search_field = QLineEdit()
        self.search_field.setAttribute(Qt.WA_MacShowFocusRect, False)
        self.search_field.setObjectName("searchField")
        self.search_field.setPlaceholderText("Search for sets...")
        self.sort_button = CustomComboBox()

        self.sort_button.addItem("Name (Ascending)")
        self.sort_button.addItem("Name (Descending)")
        self.sort_button.addItem("Item count (Ascending)")
        self.sort_button.addItem("Item count (Descending)")
        self.sort_button.setEditable(False)
        self.buttons_layout.addWidget(self.expand_all_button)
        self.buttons_layout.addWidget(self.search_field)
        self.buttons_layout.addWidget(self.sort_button)

        self.lower_layout.addLayout(self.buttons_layout)

        self.main_layout = QVBoxLayout()

        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)

        self.main_widget = QWidget()
        self.empty_label = QLabel("No sets yet! Add some using the (+) button above.")
        self.main_layout.addWidget(self.empty_label)
        self.main_layout.addStretch()
        self.main_widget.setLayout(self.main_layout)
        self.scroll.setWidget(self.main_widget)

        self.scroll.setContentsMargins(0, 0, 0, 0)
        self.main_widget.setContentsMargins(0, 0, 30, 0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.lower_layout.addWidget(self.scroll, 1)
        self.lower_layout.addStretch()

        self.main_splitter.setObjectName("horizontalSplitter")
        self.main_splitter.addWidget(self.top_widget)
        self.main_splitter.addWidget(self.lower_widget)

        self.overall_layout.addWidget(self.main_splitter)
        self.setLayout(self.overall_layout)



