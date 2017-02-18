from PyQt5.QtCore import *
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QScrollArea, QAbstractItemView, QInputDialog, \
    QMessageBox, QLineEdit, QComboBox, QMenu, QAction
from . import ImageGrid

class Set(QWidget):

    clicked_label = pyqtSignal(QWidget)

    def __init__(self, name, items, data_panel=None):
        super().__init__()
        self.name = name
        self.items = items
        self.data_panel = data_panel
        self.hidden = False
        self.init_ui()
        self.sets = []

    def expand(self):
        self.image_grid.setVisible(True)
        self.hidden = False

    def hide(self):
        self.image_grid.setVisible(False)
        self.hidden = True

    def toggle_visibility(self):
        if self.hidden:
            self.expand()
        else:
            self.hide()

    def label_clicked(self, event):
        if event.button() == Qt.RightButton: return
        self.clicked_label.emit(self)
        if len(self.image_grid.selectedIndexes()) > 0: return
        self.image_grid.setVisible(self.hidden)
        self.hidden = not self.hidden

    def addItem(self, item):
        self.image_grid.addItem(item)
        self.setItemCount(self.image_grid.count())

    def add_image(self, image):
        self.image_grid.add_image(image)
        self.setItemCount(self.image_grid.count())

    def takeItem(self, p_int):
        item = self.image_grid.takeItem(p_int)
        self.setItemCount(self.image_grid.count())
        return item

    def item(self, p_int):
        return self.image_grid.item(p_int)

    def clear(self):
        self.image_grid.clear()
        self.setItemCount(0)

    def setItemCount(self, count):
        plural = "s" if count == 0 or count > 1 else ""
        self.item_count_label.setText("(" + str(count) + " item" + plural + ")")

    def item_selected(self):
        count = len(self.image_grid.selectedIndexes())
        if count == 0:
            self.item_selected_label.setVisible(False)
        else:
            self.item_selected_label.setText("(" + str(count) + " selected)")
            self.item_selected_label.setVisible(True)

    def init_ui(self):
        self.overall_layout = QVBoxLayout()

        self.label_widget = QWidget()
        self.label_widget.setAutoFillBackground(True)
        self.label_widget.setObjectName("setLabelWidget")
        self.label_layout = QHBoxLayout()
        self.label_widget.setLayout(self.label_layout)
        self.label = QLabel("Set - " + self.name)
        self.label_layout.addWidget(self.label)
        self.label_layout.setContentsMargins(0, 0, 0, 0)

        self.item_selected_label = QLabel()
        self.item_count_label = QLabel()
        self.setItemCount(len(self.items))
        self.label_layout.addWidget(self.item_selected_label)
        self.label_layout.addStretch()
        self.label_layout.addWidget(self.item_count_label)

        self.label_widget.mousePressEvent = self.label_clicked
        self.overall_layout.setContentsMargins(0, 0, 0, 0)
        self.overall_layout.setSpacing(0)
        self.setObjectName("setLayout")
        self.label.setObjectName("setLabel")
        self.image_grid = ImageGrid(self.name, self.data_panel)
        self.image_grid.selectionModel().selectionChanged.connect(self.item_selected)
        self.overall_layout.addWidget(self.label_widget)
        self.overall_layout.addWidget(self.image_grid)
        self.setLayout(self.overall_layout)

        for item in self.items:
            item.parentIndex = self.name
            print(item)
            self.image_grid.addItem(item)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_right_click)

        # create context menu
        self.popMenu = QMenu(self)
        hide_action = QAction('Hide/Expand', self)
        rename_action = QAction('Rename', self)
        delete_action = QAction('Delete', self)
        hide_action.triggered.connect(self.toggle_visibility)
        self.popMenu.addAction(hide_action)
        self.popMenu.addAction(rename_action)
        self.popMenu.addAction(delete_action)
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
