from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import random
import numpy as np

class ReportsSection(QWidget):

    def __init__(self, sets, iteration_stats):
        super().__init__()
        self.sets = sets
        self.iteration_stats = iteration_stats if iteration_stats else []
        self.init_ui()

    def focus(self, sets=None, iteration_stats=None):
        self.sets = sets if sets else self.sets
        self.iteration_stats = iteration_stats if iteration_stats else self.iteration_stats

        y_data_1 = [len(set.all_images) for set in self.sets]
        y_data_2 = [set.incorrectly_classified for set in self.sets]
        x_data_1 = [set.name for set in self.sets]

        self.plot_bar(self.figure_1, self.canvas_1, x_data_1, y_data_1, "Items in each set", "Set name", "Number of items")
        self.plot_bar(self.figure_2, self.canvas_2, x_data_1, y_data_2, "Incorrectly classified in each set", "Set name", "Classified incorrectly")
        if iteration_stats and len(iteration_stats) > 2:
            self.plot_line(self.figure_3, self.canvas_3, np.arange(len(iteration_stats))[1:], iteration_stats[1:], "Incorrectly classified in each iteration",
                  "Iteration", "Classified incorrectly")

    def init_ui(self):
        # a figure instance to plot on

        plt.rcParams['axes.facecolor'] = '262626'
        plt.rcParams["figure.facecolor"] = '262626'

        self.figure_1 = plt.figure()
        self.canvas_1 = FigureCanvas(self.figure_1)

        self.figure_2 = plt.figure()
        self.canvas_2 = FigureCanvas(self.figure_2)

        self.figure_3 = plt.figure()
        self.canvas_3 = FigureCanvas(self.figure_3)


        self.overall_layout = QVBoxLayout()
        self.main_layout = QVBoxLayout()

        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)

        self.main_widget = QWidget()
        self.main_layout.addStretch()
        self.main_widget.setLayout(self.main_layout)
        self.scroll.setWidget(self.main_widget)

        self.scroll.setContentsMargins(0, 0, 0, 0)
        self.main_widget.setContentsMargins(0, 0, 30, 0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.overall_layout)

        self.main_layout.insertWidget(self.main_layout.count() - 1, self.canvas_1)
        self.main_layout.insertWidget(self.main_layout.count() - 1, self.canvas_2)
        self.main_layout.insertWidget(self.main_layout.count() - 1, self.canvas_3)

        self.overall_layout.addWidget(self.scroll, 1)
        self.overall_layout.addStretch()

        self.focus()

    def plot_line(self, figure, canvas, x_data, y_data, title, y_title, x_title):

        # create an axis
        ax = figure.add_subplot(111)

        ax.set_title(title)

        ax.set_ylabel(x_title)
        ax.set_xlabel(y_title)

        ax.spines['bottom'].set_color('#dfe0e6')
        ax.spines['top'].set_color('#dfe0e6')
        ax.spines['right'].set_color('#dfe0e6')
        ax.spines['left'].set_color('#dfe0e6')

        ax.tick_params(axis='x', colors='#dfe0e6')
        ax.tick_params(axis='y', colors='#dfe0e6')

        ax.yaxis.label.set_color('#dfe0e6')
        ax.xaxis.label.set_color('#dfe0e6')

        ax.title.set_color('#dfe0e6')

        # plot data
        ax.plot(x_data, y_data, color="#3a7bd5")
        canvas.setMinimumSize(self.canvas_2.size())
        # refresh canvas
        canvas.draw()

        # canvas.setMinimumSize(canvas.size())

    def plot_bar(self, figure, canvas, x_data, y_data, title, y_title, x_title):

        y_pos = np.arange(len(x_data))

        # create an axis
        ax = figure.add_subplot(111)

        ax.set_title(title)

        ax.set_ylabel(x_title)
        ax.set_xlabel(y_title)

        ax.spines['bottom'].set_color('#dfe0e6')
        ax.spines['top'].set_color('#dfe0e6')
        ax.spines['right'].set_color('#dfe0e6')
        ax.spines['left'].set_color('#dfe0e6')

        ax.tick_params(axis='x', colors='#dfe0e6')
        ax.tick_params(axis='y', colors='#dfe0e6')

        ax.yaxis.label.set_color('#dfe0e6')
        ax.xaxis.label.set_color('#dfe0e6')

        ax.title.set_color('#dfe0e6')

        # plot data
        ax.bar(y_pos, y_data, label=x_data, facecolor="#3a7bd5")
        ax.set_xticks(y_pos + 0.5)
        ax.set_xticklabels(x_data, rotation="vertical")

        # refresh canvas
        canvas.draw()

        canvas.setMinimumSize(canvas.size())
        figure.tight_layout()
