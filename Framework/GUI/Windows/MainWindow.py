import numpy as np
import sys
from PyQt5.QtCore import QThread, QSettings
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QMainWindow, QSplitter, QAction, QFileDialog, QDialog, QLabel

from Backend import DataSet
from GUI.Components import ErrorDialog
from GUI.Helpers import PathHelpers
from GUI.Panels import DataInfoPanel, MenuPanel, ToolbarPanel
from GUI.Sections import NeuralNetSection, SettingsSection, ReportsSection
from GUI.ThreadOps import RunNeuralNet, SaveLoad
from .TestingWindow import TestingWindow
from .TrainingWindow import TrainingWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Convolutional Neural Network'
        self.left = 300
        self.top = 300
        self.width = 960
        self.height = 560
        self.first_run = True
        self.current_save = None
        self.running = False
        self.iteration_stats = []
        self.settings = QSettings("Theo Styles", "Convolutional Neural Network")
        self.img_size = self.settings.value("img_size", 44)
        self.init_ui()

    def update_progress(self, amount=0, status="Running"):
        self.left_area.progressModule.progress.setText(status + " - " + str(amount) + "%")
        self.left_area.progressModule.progress.setValue(amount)

    def testing_finished(self, cls_pred):
        self.running = False
        self.main_area_reports.focus()
        for i, prob_array in enumerate(cls_pred):
            image = self.dataset.testing_images[i]
            pred_index = np.argmax(prob_array)
            prob = prob_array[pred_index]
            labelForDigit = self.dataset.labels[pred_index]
            for set in self.main_area_neural.sets:
                if set.name == labelForDigit:
                    item = set.add_image(image)
                    if prob <= 0.5:
                        item.set_important()

        self.toolbar.enable_action(0, 0)

    def run_neural_net(self):
        self.left_area.progressModule.progress.setDefault()
        self.obj = RunNeuralNet(self.dataset, self.img_size, len(self.main_area_neural.sets))  # no parent!
        self.thread = QThread()  # no parent!

        self.obj.moveToThread(self.thread)
        self.obj.one_iteration.connect(self.update_progress)
        self.obj.testing_finished.connect(self.testing_finished)
        self.thread.started.connect(self.obj.long_running)

        self.thread.start()
        self.toolbar.disable_action(0, 0)

    def add_toolbar_clicked(self):
        folder_name = QFileDialog.getExistingDirectory(self, "Select Directory With Testing Images")

        if folder_name:
            self.main_area_neural.top_widget.setVisible(True)
            self.main_area_neural.initial_image_grid_visible = True
            if self.main_area_neural.empty_label:
                self.main_area_neural.empty_label.setText("Now create sets by selecting images and using the + button to the right of the images!")
            self.main_area_neural.initial_image_grid.populate_from_folder(folder_name, self.update_progress)

    def export_sets(self):
        sets = self.main_area_neural.sets
        if len(sets) == 0:
            ErrorDialog.dialog(self, "There are no sets to export")
            return

        folder_name = QFileDialog.getExistingDirectory(self, "Select a directory to export to")

        if folder_name:
            self.left_area.progressModule.progress.setDefault()
            self.obj = SaveLoad(sets=self.main_area_neural.sets, folder_name=folder_name)  # no parent!
            self.thread = QThread()  # no parent!

            self.obj.moveToThread(self.thread)
            self.obj.one_iteration.connect(self.update_progress)
            self.thread.started.connect(self.obj.export_sets)

            self.thread.start()

    def run_clicked(self):
        sets = self.main_area_neural.sets

        if len(sets) == 0:
            return ErrorDialog.dialog(self, "Please create at least one set before running the neural network")

        if self.running:
            return ErrorDialog.dialog(self, "The neural network is already running")

        itemNames = []
        itemData = []
        setCount = 0
        total_incorrect = 0
        self.running = True

        for set in sets:
            setCount += 1
            itemCount = len(set.all_images)
            total_incorrect += set.incorrectly_classified_local
            set.incorrectly_classified_local = 0
            for index in range(itemCount):
                item = set.all_images[index]
                if item == None: continue
                itemNames.append(set.name)
                itemData.append(item.imageData)
            set.clear()

        self.iteration_stats.append(total_incorrect)
        self.dataset.add_sets_to_training_data(setCount, itemNames, itemData)

        if self.first_run or self.main_area_neural.initial_image_grid_visible:
            all_image_count = self.main_area_neural.initial_image_grid.count()
            testing_images = []
            for index in range(all_image_count):
                item = self.main_area_neural.initial_image_grid.item(index)
                if item == None: continue
                testing_images.append(item.imageData)
            self.main_area_neural.initial_image_grid.clear()
            self.main_area_neural.top_widget.setVisible(False)
            self.main_area_neural.initial_image_grid_visible = False
            self.dataset.set_testing_data(testing_images)
        else:
            self.dataset.new_testing_data()

        self.first_run = False

        self.run_neural_net()

    def finished_opening_sets(self):
        self.dataset.new_testing_data()
        self.main_area_reports.focus()

    def set_iteration_stats(self, iteration_stats):
        self.iteration_stats = iteration_stats

    def open_sets(self):
        fileName, filter = QFileDialog.getOpenFileName(self, 'Open sets save', PathHelpers.getPath("saves"),
                                                       "Set Files (*.sets)")

        if fileName:
            self.current_save = fileName
            self.main_area_neural.clear_sets()
            self.left_area.progressModule.progress.setDefault()
            self.obj = SaveLoad(self.current_save)  # no parent!
            self.thread = QThread()  # no parent!

            self.obj.moveToThread(self.thread)
            self.obj.one_iteration.connect(self.update_progress)
            self.obj.create_set.connect(self.main_area_neural.create_new_set)
            self.obj.add_to_training_set.connect(self.main_area_neural.add_images_to_set)
            self.obj.add_to_testing_set.connect(self.dataset.add_to_testing_data)
            self.obj.set_iteration_stats.connect(self.set_iteration_stats)
            self.obj.set_classified_info.connect(self.main_area_neural.set_classified_for_set)
            self.obj.finished.connect(self.finished_opening_sets)
            self.thread.started.connect(self.obj.load_images)

            self.thread.start()

    def save_sets_as(self):
        self.current_save = None
        self.save_sets()

    def save_sets(self):

        if self.current_save:
            fileName = self.current_save
        else:
            fileName, filter = QFileDialog.getSaveFileName(self, 'Save sets', PathHelpers.getPath("saves"),
                                               "Set Files (*.sets)")

        if fileName:
            sets = self.main_area_neural.sets[:]
            if self.main_area_neural.trash_set:
                sets.append(self.main_area_neural.trash_set)
            self.current_save = fileName
            self.left_area.progressModule.progress.setDefault()
            self.obj = SaveLoad(self.current_save, sets, self.dataset.all_testing_images, iteration_stats=self.iteration_stats)  # no parent!
            self.thread = QThread()  # no parent!

            self.obj.moveToThread(self.thread)
            self.obj.one_iteration.connect(self.update_progress)
            self.thread.started.connect(self.obj.save_images)

            self.thread.start()

    def deleted_set(self, set_name):
        self.datapanel.delete_training_row(set_name)

    def added_to_set(self, set_name):
        self.datapanel.increment_training_table(set_name)

    def removed_from_set(self, set_name):
        self.datapanel.decrement_training_table(set_name)

    def set_testing_amount(self, amount):
        self.datapanel.set_testing_amount(amount)

    def switch_to_neural(self):
        self.left_area.menu.setCurrentRow(0)

    def switch_to_reports(self):
        self.left_area.menu.setCurrentRow(1)

    def switch_to_settings(self):
        self.left_area.menu.setCurrentRow(2)

    def menu_changed(self, index):
        sets = self.main_area_neural.sets[:]
        if self.main_area_neural.trash_set:
            sets.append(self.main_area_neural.trash_set)
        self.main_area_neural.setVisible(False)
        self.main_area_settings.setVisible(False)
        self.main_area_reports.setVisible(False)
        if index == 0:
            self.main_area_neural.setVisible(True)
        elif index == 1:
            self.main_area_reports.setVisible(True)
            self.main_area_reports.focus(sets, self.iteration_stats)
        elif index == 2:
            self.main_area_settings.setVisible(True)
            self.main_area_settings.changed()

    def view_all_training(self):
        sets = self.main_area_neural.sets[:]
        if self.main_area_neural.trash_set:
            sets.append(self.main_area_neural.trash_set)

        self.training_window = TrainingWindow(self, sets)
        self.training_window.show()

    def view_all_testing(self):
        self.testing_window = TestingWindow(self, self.dataset.all_testing_images)
        self.testing_window.show()

    def exit_app(self):
        sys.exit(0)

    def about_clicked(self):
        d = QDialog(self)
        layout = QVBoxLayout()
        d.setLayout(layout)
        layout.addWidget(QLabel("Convolutional Neural Network - Created By Theo Styles"))
        layout.addWidget(QLabel("Credits:"))
        layout.addWidget(QLabel("Play icon made by Google from www.flaticon.com"))
        layout.addWidget(QLabel("Plus icon made by Madebyoliver from www.flaticon.com"))
        layout.addWidget(QLabel("Export icon made by Popcic from www.flaticon.com"))
        layout.addWidget(QLabel("Up arrow icon made by Google from www.flaticon.com"))
        layout.addWidget(QLabel("Down arrow icon made by Google from www.flaticon.com"))
        layout.addWidget(QLabel("Tick icon made by Eleonor Wang from www.flaticon.com"))
        d.setWindowTitle("About")
        d.exec_()

    def init_ui(self):
        self.settings = QSettings("Theo Styles", "Convolutional Neural Network")
        self.settings.setValue("test", 1)
        self.dataset = DataSet(self.img_size)
        self.dataset.test_set_changed.connect(self.set_testing_amount)
        qss_file = open(PathHelpers.getPath("GUI/Stylesheets/default.qss")).read()
        self.setStyleSheet(qss_file)

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.main_grid = QSplitter()
        self.main_grid.setObjectName("verticalSplitter")

        self.main_grid.setContentsMargins(0, 0, 0, 0)

        self.right_layout = QVBoxLayout()
        self.right_widget = QWidget()
        self.right_widget.setLayout(self.right_layout)

        self.right_grid = QSplitter()
        self.right_grid.setObjectName("verticalSplitter")

        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(0)
        self.right_grid.setContentsMargins(0, 0, 0, 0)

        self.right_stacking = QWidget()
        self.right_stacking_grid = QGridLayout()
        self.right_stacking.setLayout(self.right_stacking_grid)
        self.right_grid.addWidget(self.right_stacking)

        self.right_stacking_grid.setContentsMargins(0, 0, 0, 0)
        self.right_stacking_grid.setSpacing(0)

        self.main_area_neural = NeuralNetSection()
        self.main_area_neural.added_to_set.connect(self.added_to_set)
        self.main_area_neural.removed_from_set.connect(self.removed_from_set)
        self.main_area_neural.deleted_set.connect(self.deleted_set)
        self.right_stacking_grid.addWidget(self.main_area_neural, 0, 0)

        self.main_area_settings = SettingsSection()
        self.right_stacking_grid.addWidget(self.main_area_settings, 0, 0)
        self.main_area_settings.setVisible(False)

        self.main_area_reports = ReportsSection(self.main_area_neural.sets, self.iteration_stats)
        self.right_stacking_grid.addWidget(self.main_area_reports, 0, 0)
        self.main_area_reports.setVisible(False)


        self.datapanel = DataInfoPanel()
        self.datapanel.clicked_training_view_all_sig.connect(self.view_all_training)
        self.datapanel.clicked_testing_view_all_sig.connect(self.view_all_testing)
        self.right_grid.addWidget(self.datapanel)

        self.right_grid.setStretchFactor(0, 10)
        self.right_grid.setStretchFactor(1, 11)

        self.left_area = MenuPanel()
        self.left_area.selectedItem.connect(self.menu_changed)

        self.toolbar = ToolbarPanel()
        self.toolbar.run_clicked.connect(self.run_clicked)
        self.toolbar.add_clicked.connect(self.add_toolbar_clicked)
        self.toolbar.export_clicked.connect(self.export_sets)

        self.right_layout.addWidget(self.toolbar)
        self.right_layout.addWidget(self.right_grid)

        self.main_grid.addWidget(self.left_area)
        self.main_grid.addWidget(self.right_widget)

        self.setCentralWidget(self.main_grid)
        self.main_grid.setStretchFactor(0, 6)
        self.main_grid.setStretchFactor(1, 10)

        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.setStatusTip('Save the current sets')
        save_action.triggered.connect(self.save_sets)

        save_action_as = QAction("&Save As", self)
        save_action_as.setStatusTip('New save for the current sets')
        save_action_as.triggered.connect(self.save_sets_as)

        open_action = QAction("&Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip('Open a sets save file')
        open_action.triggered.connect(self.open_sets)

        exit_action = QAction("&Exit", self)
        exit_action.setStatusTip('Exit the application')
        exit_action.triggered.connect(self.exit_app)

        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(save_action_as)
        file_menu.addAction(exit_action)

        neural_action = QAction("&Neural Net", self)
        neural_action.setStatusTip('View the neural network')
        neural_action.triggered.connect(self.switch_to_neural)

        reports_action = QAction("&Reports", self)
        reports_action.setStatusTip('View reports and statistics')
        reports_action.triggered.connect(self.switch_to_reports)

        settings_action = QAction("&Settings", self)
        settings_action.setStatusTip('View settings')
        settings_action.triggered.connect(self.switch_to_settings)

        view_menu = menubar.addMenu('&View')
        view_menu.addAction(neural_action)
        view_menu.addAction(reports_action)
        view_menu.addAction(settings_action)

        import_action = QAction("&Import folder", self)
        import_action.setStatusTip('Import a folder of images')
        import_action.triggered.connect(self.add_toolbar_clicked)

        export_action = QAction("&Export sets", self)
        export_action.setStatusTip('Export sets to folder')
        export_action.triggered.connect(self.export_sets)

        settings_action = QAction("&Settings", self)
        settings_action.setStatusTip('View settings')
        settings_action.triggered.connect(self.switch_to_settings)

        tools_menu = menubar.addMenu('&Tools')
        tools_menu.addAction(import_action)
        tools_menu.addAction(export_action)

        run_action = QAction("&Run Neural Network", self)
        run_action.setStatusTip('Start running the neural network')
        run_action.triggered.connect(self.run_clicked)

        run_menu = menubar.addMenu('&Run')
        run_menu.addAction(run_action)

        about_action = QAction("&About", self)
        about_action.setStatusTip('About the application')
        about_action.triggered.connect(self.about_clicked)

        help_menu = menubar.addMenu('&Help')
        help_menu.addAction(about_action)

        self.show()