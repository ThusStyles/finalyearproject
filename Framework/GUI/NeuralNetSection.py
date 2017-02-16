import os

from PyQt5.QtCore import *
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QScrollArea, QAbstractItemView, QInputDialog, \
    QMessageBox, QLineEdit, QComboBox
from PyQt5.QtGui import QStandardItem

from Framework.GUI.Components import ImageGrid, CustomPushButton, CustomComboBox, Set

img_size = 44
base_dir = os.path.dirname(os.path.realpath(__file__)) + "/../../"


class NeuralNetSection(QWidget):

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
        self.sets = []
        self.expand_state = False
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

    def clicked_set(self, set):
        othersSelected = False
        for otherSet in self.sets:
            if len(otherSet.image_grid.selectedIndexes()) > 0:
                othersSelected = True
                break
        if not othersSelected: return
        if len(set.image_grid.selectedIndexes()) > 0: return

        print("None selected on set " + set.name)

        reply = QMessageBox.question(self, 'Message',
                                           "Are you sure you want to add items to set " + set.name + "?",
                                     QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            for oneSet in self.sets:
                selectedItems = oneSet.image_grid.selectedItems()
                for selectedItem in selectedItems:
                    item = oneSet.takeItem(oneSet.image_grid.row(selectedItem))
                    set.addItem(item)

        set.hidden = True


    def create_new_set(self, name, items):
        new_set = Set(name, items, self.data_panel)
        new_set.clicked_label.connect(self.clicked_set)
        self.sets.append(new_set)
        if self.empty_label:
            self.main_layout.removeWidget(self.empty_label)
            self.empty_label.deleteLater()
            self.empty_label = None

        self.main_layout.insertWidget(self.main_layout.count() - 1, new_set)


    def ask_for_set_name(self):

        if len(self.initial_image_grid.selectedItems()) == 0:
            self.show_error("Please select items to create a new set")
        else:
            text, ok = QInputDialog.getText(self, 'Convolutional Neural Network: New Set', 'Enter the name for the new set:')
            if len(text) == 0:
                self.show_error("You must enter a set name")
            elif ok:
                to_add = []
                exists = False
                setToAdd = None
                for set in self.sets:
                    if set.name == text:
                        exists = True
                        setToAdd = set

                for item in self.initial_image_grid.selectedItems():
                    taken = self.initial_image_grid.takeItem(self.initial_image_grid.row(item))
                    to_add.append(taken)
                    if exists:
                        setToAdd.addItem(taken)

                if not exists:
                    self.create_new_set(text, to_add)


    def show_error(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        msg.setText("Error!")
        msg.setInformativeText(message)
        msg.setWindowTitle("Convolutional Neural Network: Error")
        msg.setStandardButtons(QMessageBox.Ok)

        retval = msg.exec_()

    def init_ui(self):
        self.data_panel = self.main_window.datapanel
        self.overall_layout = QVBoxLayout()
        self.top_layout = QHBoxLayout()

        self.initial_image_grid = ImageGrid("Initial")
        self.add_button = CustomPushButton("+")
        self.trash_button = CustomPushButton("Delete")

        self.initial_image_grid.populate_from_folder(base_dir + "page-0400-cropped")

        self.top_grid_buttons = QVBoxLayout()
        self.top_grid_buttons.addWidget(self.add_button)
        self.top_grid_buttons.addStretch()
        self.top_grid_buttons.addWidget(self.trash_button)

        self.add_button.clicked.connect(self.ask_for_set_name)

        self.top_layout.addWidget(self.initial_image_grid)
        self.top_layout.addLayout(self.top_grid_buttons)

        self.overall_layout.addLayout(self.top_layout)

        self.buttons_layout = QHBoxLayout()
        self.expand_all_button = CustomPushButton("Hide All -")
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

        self.overall_layout.addLayout(self.buttons_layout)

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

        self.overall_layout.addWidget(self.scroll, 1)
        self.overall_layout.addStretch()
        self.setLayout(self.overall_layout)



