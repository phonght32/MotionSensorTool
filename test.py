# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import sys

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import axes3d
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout,
                               QHeaderView, QLabel, QMainWindow, QSlider,
                               QTableWidget, QTableWidgetItem, QVBoxLayout,
                               QWidget)


"""This example implements the interaction between Qt Widgets and a 3D
matplotlib plot"""


class ApplicationWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.column_names = ["Column A", "Column B", "Column C"]

        # Central widget
        self._main = QWidget()
        self.setCentralWidget(self._main)

        # Main menu bar
        self.menu = self.menuBar()
        self.menu_file = self.menu.addMenu("File")
        exit = QAction("Exit", self, triggered=qApp.quit)  # noqa: F821
        self.menu_file.addAction(exit)

        self.menu_about = self.menu.addMenu("&About")
        about = QAction("About Qt", self,
                        shortcut=QKeySequence(QKeySequence.StandardKey.HelpContents),
                        triggered=qApp.aboutQt)  # noqa: F821
        self.menu_about.addAction(about)

        # Figure (Left)
        self.fig = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.fig)

        # Sliders (Left)
        min = 0
        max = 360
        self.slider_azim = QSlider(minimum=min, maximum=max, orientation=Qt.Orientation.Horizontal)
        self.slider_elev = QSlider(minimum=min, maximum=max, orientation=Qt.Orientation.Horizontal)

        self.slider_azim_layout = QHBoxLayout()
        self.slider_azim_layout.addWidget(QLabel(f"{min}"))
        self.slider_azim_layout.addWidget(self.slider_azim)
        self.slider_azim_layout.addWidget(QLabel(f"{max}"))

        self.slider_elev_layout = QHBoxLayout()
        self.slider_elev_layout.addWidget(QLabel(f"{min}"))
        self.slider_elev_layout.addWidget(self.slider_elev)
        self.slider_elev_layout.addWidget(QLabel(f"{max}"))

        # Table (Right)
        self.table = QTableWidget()
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # ComboBox (Right)
        self.combo = QComboBox()
        self.combo.addItems(["Wired", "Surface", "Triangular Surface", "Sphere"])

        # Right layout
        rlayout = QVBoxLayout()
        rlayout.setContentsMargins(1, 1, 1, 1)
        rlayout.addWidget(QLabel("Plot type:"))
        rlayout.addWidget(self.combo)
        rlayout.addWidget(self.table)

        # Left layout
        llayout = QVBoxLayout()
        rlayout.setContentsMargins(1, 1, 1, 1)
        llayout.addWidget(self.canvas, 88)
        llayout.addWidget(QLabel("Azimuth:"), 1)
        llayout.addLayout(self.slider_azim_layout, 5)
        llayout.addWidget(QLabel("Elevation:"), 1)
        llayout.addLayout(self.slider_elev_layout, 5)

        # Main layout
        layout = QHBoxLayout(self._main)
        layout.addLayout(llayout, 70)
        layout.addLayout(rlayout, 30)

        # Signal and Slots connections
        self.combo.currentTextChanged.connect(self.combo_option)
        self.slider_azim.valueChanged.connect(self.rotate_azim)
        self.slider_elev.valueChanged.connect(self.rotate_elev)

        # Initial setup
        self.plot_wire()
        self._ax.view_init(30, 30)
        self.slider_azim.setValue(30)
        self.slider_elev.setValue(30)
        self.fig.canvas.mpl_connect("button_release_event", self.on_click)

    # Matplotlib slot method
    def on_click(self, event):
        azim, elev = self._ax.azim, self._ax.elev
        self.slider_azim.setValue(azim + 180)
        self.slider_elev.setValue(elev + 180)

    # Utils methods

    def set_table_data(self, X, Y, Z):
        for i in range(len(X)):
            self.table.setItem(i, 0, QTableWidgetItem(f"{X[i]:.2f}"))
            self.table.setItem(i, 1, QTableWidgetItem(f"{Y[i]:.2f}"))
            self.table.setItem(i, 2, QTableWidgetItem(f"{Z[i]:.2f}"))

    def set_canvas_table_configuration(self, row_count, data):
        self.fig.set_canvas(self.canvas)
        self._ax = self.canvas.figure.add_subplot(projection="3d")

        self._ax.set_xlabel(self.column_names[0])
        self._ax.set_ylabel(self.column_names[1])
        self._ax.set_zlabel(self.column_names[2])

        self.table.setRowCount(row_count)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(self.column_names)
        self.set_table_data(data[0], data[1], data[2])

    # Plot methods

    def plot_wire(self):
        # Data
        self.X, self.Y, self.Z = axes3d.get_test_data(0.03)

        self.set_canvas_table_configuration(len(self.X[0]), (self.X[0], self.Y[0], self.Z[0]))
        self._ax.plot_wireframe(self.X, self.Y, self.Z, rstride=10, cstride=10, cmap="viridis")
        self.canvas.draw()

    def plot_surface(self):
        # Data
        self.X, self.Y = np.meshgrid(np.linspace(-6, 6, 30), np.linspace(-6, 6, 30))
        self.Z = np.sin(np.sqrt(self.X ** 2 + self.Y ** 2))

        self.set_canvas_table_configuration(len(self.X[0]), (self.X[0], self.Y[0], self.Z[0]))
        self._ax.plot_surface(self.X, self.Y, self.Z,
                              rstride=1, cstride=1, cmap="viridis", edgecolor="none")
        self.canvas.draw()

    def plot_triangular_surface(self):
        # Data
        radii = np.linspace(0.125, 1.0, 8)
        angles = np.linspace(0, 2 * np.pi, 36, endpoint=False)[..., np.newaxis]
        self.X = np.append(0, (radii * np.cos(angles)).flatten())
        self.Y = np.append(0, (radii * np.sin(angles)).flatten())
        self.Z = np.sin(-self.X * self.Y)

        self.set_canvas_table_configuration(len(self.X), (self.X, self.Y, self.Z))
        self._ax.plot_trisurf(self.X, self.Y, self.Z, linewidth=0.2, antialiased=True)
        self.canvas.draw()

    def plot_sphere(self):
        # Data
        u = np.linspace(0, 2 * np.pi, 100)
        v = np.linspace(0, np.pi, 100)
        self.X = 10 * np.outer(np.cos(u), np.sin(v))
        self.Y = 10 * np.outer(np.sin(u), np.sin(v))
        self.Z = 9 * np.outer(np.ones(np.size(u)), np.cos(v))

        self.set_canvas_table_configuration(len(self.X), (self.X[0], self.Y[0], self.Z[0]))
        self._ax.plot_surface(self.X, self.Y, self.Z)
        self.canvas.draw()

    # Slots

    @Slot()
    def combo_option(self, text):
        if text == "Wired":
            self.plot_wire()
        elif text == "Surface":
            self.plot_surface()
        elif text == "Triangular Surface":
            self.plot_triangular_surface()
        elif text == "Sphere":
            self.plot_sphere()

    @Slot()
    def rotate_azim(self, value):
        self._ax.view_init(self._ax.elev, value)
        self.fig.set_canvas(self.canvas)
        self.canvas.draw()

    @Slot()
    def rotate_elev(self, value):
        self._ax.view_init(value, self._ax.azim)
        self.fig.set_canvas(self.canvas)
        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = ApplicationWindow()
    w.setFixedSize(1280, 720)
    w.show()
    app.exec()