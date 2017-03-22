from PyQt5.QtCore import *
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QMenu, QAction

from . import ImageGrid, ErrorDialog, InputDialog


class Set(QWidget):

    clicked_set = pyqtSignal(QWidget)
    added_image = pyqtSignal(str)
    removed_image = pyqtSignal(str)
    create_new_set = pyqtSignal(str, object)
    rename_set_sig = pyqtSignal(object, str)
    delete_set_sig = pyqtSignal(object)
    move_to_set = pyqtSignal(str, object)

    def __init__(self, name):
        super().__init__()
        self.name = name
        self.hidden = False
        self.create_new_set_linked = False
        self.incorrectly_classified = 0
        self.incorrectly_classified_local = 0
        self.init_ui()
        self.all_images = []

    def count(self):
        return self.image_grid.count()

    def show_all(self):
        items = []
        for index in range(self.image_grid.count()):
            items.append(self.image_grid.item(index))

        print("SIZE OF ALL ", self.name, len(items), len(self.all_images))
        diff = [item for item in self.all_images if item not in items]
        for image in diff:
            self.addItem(image, False)

    def expand(self):
        self.image_grid.setVisible(True)
        self.hidden = False

    def hide(self):
        count = len(self.image_grid.selectedIndexes())
        if count > 0: return
        self.image_grid.setVisible(False)
        self.hidden = True

    def toggle_visibility(self):
        if self.hidden:
            self.expand()
        else:
            self.hide()

    def add_items(self, items):
        for item in items:
            self.addItem(item)

    def add_images(self, items):
        for item in items:
            added_item = self.add_image(item)
            self.items.append(added_item)

    def delete_set(self):
        if not self.image_grid.isEmpty:
            ErrorDialog.dialog(self, "This set must be empty before it's deleted")
            return
        self.delete_set_sig.emit(self)

    def rename_set(self):
        text, ok = InputDialog.dialog(self, 'Enter the new name for set '  + self.name + ":", "Set name...")
        if ok:
            if len(text) == 0:
                return self.show_error("You must enter a set name")
            self.rename_set_sig.emit(self, text)

    def move_selected(self):
        if len(self.image_grid.selectedIndexes()) == 0: return
        text, ok = InputDialog.dialog(self, 'Enter the name of the set to move to:', "Set name...")
        if ok:
            if len(text) == 0:
                return self.show_error("You must enter a set name")
            self.move_to_set.emit(text, self)

    def move_selected_trash(self):
        if len(self.image_grid.selectedIndexes()) == 0: return
        self.move_to_set.emit("Trash", self)

    def new_set_with_selected(self):
        print("New set with selected triggered")
        if len(self.image_grid.selectedIndexes()) == 0: return
        text, ok = InputDialog.dialog(self, 'Enter the new name for the new set:', "Set name...")
        if ok:
            if len(text) == 0:
                return self.show_error("You must enter a set name")
            self.create_new_set.emit(text, self)

    def show_error(self, message):
        ErrorDialog.dialog(self, message)

    def label_clicked(self, event):
        if event.button() == Qt.RightButton: return
        self.clicked_set.emit(self)
        if len(self.image_grid.selectedIndexes()) > 0: return
        self.image_grid.setVisible(self.hidden)
        self.hidden = not self.hidden

    def addItem(self, item, emit=True):
        self.image_grid.addItem(item)
        self.all_images.append(item)
        if emit:
            self.added_image.emit(self.name)
        self.setItemCount(self.image_grid.count())

    def add_image(self, image, emit=True):
        item = self.image_grid.add_image(image)
        self.all_images.append(item)
        if emit:
            self.added_image.emit(self.name)
        self.setItemCount(self.image_grid.count())
        return item

    def takeItem(self, p_int):
        item = self.image_grid.takeItem(p_int)
        self.setItemCount(self.image_grid.count())
        return item

    def takeFromBoth(self, p_int):
        item = self.takeItem(p_int)
        self.removed_image.emit(self.name)
        self.all_images.remove(item)
        return item

    def item(self, p_int):
        return self.image_grid.item(p_int)

    def clear(self):
        self.image_grid.clear()
        self.setItemCount(0)

    def setItemCount(self, count):
        plural = "s" if count == 0 or count > 1 else ""
        self.item_count_label.setText("(" + str(count) + " item" + plural + ")")

    def set_name(self, name):
        self.name = name
        self.label.setText("Set - " + self.name)

    def item_selected(self):
        count = len(self.image_grid.selectedIndexes())
        if count == 0:
            self.item_selected_label.setVisible(False)
            if self.create_new_set_linked:
                self.popMenu.removeAction(self.new_set_action)
                self.popMenu.removeAction(self.move_selected_action)
                self.popMenu.removeAction(self.move_selected_trash_action)
                self.hide_action.setVisible(True)
                self.create_new_set_linked = False
        else:
            self.item_selected_label.setText("(" + str(count) + " selected)")
            self.item_selected_label.setVisible(True)
            if not self.create_new_set_linked:
                self.popMenu.addAction(self.new_set_action)
                self.popMenu.addAction(self.move_selected_action)
                self.popMenu.addAction(self.move_selected_trash_action)
                self.hide_action.setVisible(False)
                self.create_new_set_linked = True

    def disable_set_operations(self):
        self.rename_action.setVisible(False)
        self.delete_action.setVisible(False)
        self.move_selected_action.setVisible(False)
        self.move_selected_trash_action.setVisible(False)
        self.new_set_action.setVisible(False)

    def init_ui(self):
        self.overall_layout = QVBoxLayout()
        self.overall_layout.setContentsMargins(0, 0, 0, 0)
        self.overall_layout.setSpacing(0)
        self.setObjectName("setLayout")

        self.label_widget = QWidget()
        self.label_widget.setAutoFillBackground(True)
        self.label_widget.setObjectName("setLabelWidget")
        self.label_layout = QHBoxLayout()
        self.label_widget.setLayout(self.label_layout)
        self.label = QLabel("Set - " + self.name)
        self.label.setObjectName("setLabel")
        self.label_layout.addWidget(self.label)
        self.label_layout.setContentsMargins(0, 0, 0, 0)

        self.item_selected_label = QLabel()
        self.item_count_label = QLabel()
        self.setItemCount(0)
        self.label_layout.addWidget(self.item_selected_label)
        self.label_layout.addStretch()
        self.label_layout.addWidget(self.item_count_label)

        self.label_widget.mousePressEvent = self.label_clicked

        self.image_grid = ImageGrid()
        self.image_grid.selectionModel().selectionChanged.connect(self.item_selected)

        self.overall_layout.addWidget(self.label_widget)
        self.overall_layout.addWidget(self.image_grid)
        self.setLayout(self.overall_layout)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_right_click)

        # create context menu
        self.popMenu = QMenu(self)
        self.hide_action = QAction('Hide/Expand', self)
        self.rename_action = QAction('Rename set', self)
        self.delete_action = QAction('Delete set', self)
        self.rename_action.triggered.connect(self.rename_set)
        self.delete_action.triggered.connect(self.delete_set)
        self.new_set_action = QAction("Create new set with selected", self)
        self.new_set_action.triggered.connect(self.new_set_with_selected)
        self.move_selected_action = QAction("Move selected to set", self)
        self.move_selected_action.triggered.connect(self.move_selected)
        self.move_selected_trash_action = QAction("Move selected to trash set", self)
        self.move_selected_trash_action.triggered.connect(self.move_selected_trash)
        self.hide_action.triggered.connect(self.toggle_visibility)
        self.popMenu.addAction(self.hide_action)
        self.popMenu.addAction(self.rename_action)
        self.popMenu.addAction(self.delete_action)
        self.popMenu.setStyleSheet("""
        QMenu{
            background: #d6d6d7;
            color: #202020;
        }
        QMenu::item { /* when user selects item using mouse or keyboard */
            padding: 3.5px 10px;
        }
        QMenu::item:selected { /* when user selects item using mouse or keyboard */
            background-color: #3e3e40;
            color: #d6d6d7;
        }
        """)

    def on_right_click(self, point):
        self.popMenu.exec_(self.mapToGlobal(point))