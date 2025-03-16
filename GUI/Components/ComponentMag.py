from GUI.Config.Config_Widget import *
from Utils.Singleton import *
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
import sys
import os
import re
import numpy as np
from scipy import linalg
import matplotlib

matplotlib.use('QtAgg')


DIMENSION_MATRIX_TYPE = 120
DIMENSION_MATRIX_VALUE_WIDTH = 90
BORDER_MAXTRIX_VALUE = "border: 1px solid black;"


@singleton
class ComponentMagPlotter(QWidget):
    def __init__(self):
        super().__init__()

        # Create 2D figure for raw data
        self.pyplotFig2D = plt.figure()
        self.pyplotFig2D_axes = self.pyplotFig2D.add_subplot(111)

        # Create 3D figure for raw & calibrated data
        self.pyplotFig3D, (self.pyplotFig3D_Axes_RawData, self.pyplotFig3D_Axes_CalibData) = plt.subplots(
            1, 2, subplot_kw=dict(projection='3d'))

        # Configure figure display
        self.__configFig2D_RawData__()
        self.__configFig3D_RawData__()
        self.__configFig3D_CalibData__()

        # Create Canvas and Toolbar
        self.widgetFig2D = FigureCanvasQTAgg(self.pyplotFig2D)
        self.widgetFig3D = FigureCanvasQTAgg(self.pyplotFig3D)
        self.widgetToolbar = NavigationToolbar2QT(self.widgetFig2D, self)

        layout = QVBoxLayout()
        layout.addWidget(self.widgetToolbar)
        layout.addWidget(self.widgetFig2D)
        layout.addWidget(self.widgetFig3D)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def __configFig2D_RawData__(self):
        self.pyplotFig2D_axes.grid(True)
        self.pyplotFig2D_axes.set_title("Raw data")

    def __configFig3D_RawData__(self):
        self.pyplotFig3D_Axes_RawData.grid(True)
        self.pyplotFig3D_Axes_RawData.set_xlabel('MagX')
        self.pyplotFig3D_Axes_RawData.set_ylabel('MagY')
        self.pyplotFig3D_Axes_RawData.set_zlabel('MagZ')
        self.pyplotFig3D_Axes_RawData.set_title("Raw data")

    def __configFig3D_CalibData__(self):
        self.pyplotFig3D_Axes_CalibData.grid(True)
        self.pyplotFig3D_Axes_CalibData.set_xlabel('MagX')
        self.pyplotFig3D_Axes_CalibData.set_ylabel('MagY')
        self.pyplotFig3D_Axes_CalibData.set_zlabel('MagZ')
        self.pyplotFig3D_Axes_CalibData.set_title("Calibrated data")

    def plot(self, MagData):
        Time = MagData[:, 0]
        MagX = MagData[:, 1]
        MagY = MagData[:, 2]
        MagZ = MagData[:, 3]

        self.pyplotFig2D_axes.cla()
        self.pyplotFig2D_axes.plot(
            Time, MagX, label='MagX', lw=FIGURE_LINE_WIDTH)
        self.pyplotFig2D_axes.plot(
            Time, MagY, label='MagY', lw=FIGURE_LINE_WIDTH)
        self.pyplotFig2D_axes.plot(
            Time, MagZ, label='MagZ', lw=FIGURE_LINE_WIDTH)
        self.__configFig2D_RawData__()

        lim_max = Time[-1]
        if lim_max - FIGURE_DISPLAY_INTERVAL > 0:
            lim_min = lim_max - FIGURE_DISPLAY_INTERVAL
        else:
            lim_min = 0
        self.pyplotFig2D_axes.set_xlim(
            [float(lim_min), float(lim_max+FIGURE_DISPLAY_EXTENDED_DURRATION)])
        self.widgetFig2D.draw()

        self.pyplotFig3D_Axes_RawData.cla()
        self.__configFig3D_RawData__()
        self.pyplotFig3D_Axes_RawData.scatter(MagX, MagY, MagZ)
        self.pyplotFig3D.canvas.draw_idle()

    def plotCalibData(self, Time=[], CalibData_MagX=[], CalibData_MagY=[], CalibData_MagZ=[]):
        self.pyplotFig3D_Axes_CalibData.cla()
        self.pyplotFig3D_Axes_CalibData.scatter(
            CalibData_MagX, CalibData_MagY, CalibData_MagZ)
        self.__configFig3D_CalibData__()
        self.pyplotFig3D.canvas.draw_idle()

    def clear(self):
        # Clear content in figures
        self.pyplotFig2D_axes.cla()
        self.pyplotFig3D_Axes_RawData.cla()
        self.pyplotFig3D_Axes_CalibData.cla()

        # Re-configure settings
        self.__configFig2D_RawData__()
        self.__configFig3D_RawData__()
        self.__configFig3D_CalibData__()

        # Update figure
        self.widgetFig2D.draw()
        self.pyplotFig3D.canvas.draw_idle()


@singleton
class ComponentMagAnalyze(QWidget):
    def __init__(self):
        super().__init__()

        self.__current_NormOfGravity__ = '1024'

        self.__current_HardIronBias_b1__ = '0.0'
        self.__current_HardIronBias_b2__ = '0.0'
        self.__current_HardIronBias_b3__ = '0.0'

        self.__current_SoftIron_m11__ = '0.0'
        self.__current_SoftIron_m12__ = '0.0'
        self.__current_SoftIron_m13__ = '0.0'
        self.__current_SoftIron_m21__ = '0.0'
        self.__current_SoftIron_m22__ = '0.0'
        self.__current_SoftIron_m23__ = '0.0'
        self.__current_SoftIron_m31__ = '0.0'
        self.__current_SoftIron_m32__ = '0.0'
        self.__current_SoftIron_m33__ = '0.0'

        self.rawData = []
        self.calibData = []
        self.TimeCalibMag = []

        self.initWidgetNormOfMagnetic()
        self.initWidgetButtonAction()
        self.initWidgetHardIronBias()
        self.initWidgetSoftIronBias()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.__widget_NormOfMagnetic__)
        layout.addWidget(self.__widget_ButtonAction_)
        layout.addWidget(self.__widget_HardIronBias__)
        layout.addWidget(self.__widget_SoftIron__)

        self.setLayout(layout)

    def onChangeNormOfMagnetic(self, text):
        self.__current_NormOfGravity__ = text

    def initWidgetNormOfMagnetic(self):
        self.__label_NormOfGravity__ = QLabel(
            'Norm of Magnetometer or Gravity: ')
        self.__label_NormOfGravity__.setFixedWidth(280)
        # self.__label_NormOfGravity__

        self.__input_NormOfMagnetic__ = QLineEdit(
            self.__current_NormOfGravity__)
        self.__input_NormOfMagnetic__.setFixedWidth(100)
        self.__input_NormOfMagnetic__.textChanged.connect(
            self.onChangeNormOfMagnetic)

        self.__widget_NormOfMagnetic_Layout__ = QGridLayout()
        # self.__widget_NormOfMagnetic_Layout__.setAlignment(Qt.AlignmentFlag.AlignLeft)
        # self.__widget_NormOfMagnetic_Layout__.setContentsMargins(0, 0, 0, 0)
        self.__widget_NormOfMagnetic_Layout__.addWidget(
            self.__label_NormOfGravity__, 0, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.__widget_NormOfMagnetic_Layout__.addWidget(
            self.__input_NormOfMagnetic__, 0, 2, alignment=Qt.AlignmentFlag.AlignLeft)
        self.__widget_NormOfMagnetic__ = QWidget()
        self.__widget_NormOfMagnetic__.setLayout(
            self.__widget_NormOfMagnetic_Layout__)

    def initWidgetButtonAction(self):
        self.__button_Calibrate__ = QPushButton('Calibrate')
        self.__button_Calibrate__.clicked.connect(self.onCalibrate)
        self.__button_Calibrate__.setFixedWidth(DIMENSION_BUTTON_WIDTH)

        self.__widget_ButtonAction_Layout = QHBoxLayout()
        self.__widget_ButtonAction_Layout.addWidget(self.__button_Calibrate__)
        self.__widget_ButtonAction_ = QWidget()
        self.__widget_ButtonAction_.setLayout(
            self.__widget_ButtonAction_Layout)

    def initWidgetHardIronBias(self):
        self.__label_HardIronBias__ = QLabel('Hard iron bias')
        self.__label_HardIronBias__.setFixedWidth(DIMENSION_MATRIX_TYPE)

        self.__label_HardIronBias_b1__ = QLabel(
            self.__current_HardIronBias_b1__)
        self.__label_HardIronBias_b1__.setFixedWidth(
            DIMENSION_MATRIX_VALUE_WIDTH)
        self.__label_HardIronBias_b1__.setStyleSheet(BORDER_MAXTRIX_VALUE)

        self.__label_HardIronBias_b2__ = QLabel(
            self.__current_HardIronBias_b2__)
        self.__label_HardIronBias_b2__.setFixedWidth(
            DIMENSION_MATRIX_VALUE_WIDTH)
        self.__label_HardIronBias_b2__.setStyleSheet(BORDER_MAXTRIX_VALUE)

        self.__label_HardIronBias_b3__ = QLabel(
            self.__current_HardIronBias_b3__)
        self.__label_HardIronBias_b3__.setFixedWidth(
            DIMENSION_MATRIX_VALUE_WIDTH)
        self.__label_HardIronBias_b3__.setStyleSheet(BORDER_MAXTRIX_VALUE)

        self.__widget_HardIronBias_Layout__ = QHBoxLayout()
        self.__widget_HardIronBias_Layout__.addWidget(
            self.__label_HardIronBias__)
        self.__widget_HardIronBias_Layout__.addWidget(
            self.__label_HardIronBias_b1__)
        self.__widget_HardIronBias_Layout__.addWidget(
            self.__label_HardIronBias_b2__)
        self.__widget_HardIronBias_Layout__.addWidget(
            self.__label_HardIronBias_b3__)
        self.__widget_HardIronBias__ = QWidget()
        self.__widget_HardIronBias__.setLayout(
            self.__widget_HardIronBias_Layout__)

    def initWidgetSoftIronBias(self):
        self.__label_SoftIron__ = QLabel('Soft iron:')
        self.__label_SoftIron__.setFixedWidth(DIMENSION_MATRIX_TYPE)

        self.__label_SoftIron_m11__ = QLabel(self.__current_SoftIron_m11__)
        self.__label_SoftIron_m11__.setFixedWidth(DIMENSION_MATRIX_VALUE_WIDTH)
        self.__label_SoftIron_m11__.setStyleSheet(BORDER_MAXTRIX_VALUE)

        self.__label_SoftIron_m12__ = QLabel(self.__current_SoftIron_m12__)
        self.__label_SoftIron_m12__.setFixedWidth(DIMENSION_MATRIX_VALUE_WIDTH)
        self.__label_SoftIron_m12__.setStyleSheet(BORDER_MAXTRIX_VALUE)

        self.__label_SoftIron_m13__ = QLabel(self.__current_SoftIron_m13__)
        self.__label_SoftIron_m13__.setFixedWidth(DIMENSION_MATRIX_VALUE_WIDTH)
        self.__label_SoftIron_m13__.setStyleSheet(BORDER_MAXTRIX_VALUE)

        self.__label_SoftIron_m21__ = QLabel(self.__current_SoftIron_m21__)
        self.__label_SoftIron_m21__.setFixedWidth(DIMENSION_MATRIX_VALUE_WIDTH)
        self.__label_SoftIron_m21__.setStyleSheet(BORDER_MAXTRIX_VALUE)

        self.__label_SoftIron_m22__ = QLabel(self.__current_SoftIron_m22__)
        self.__label_SoftIron_m22__.setFixedWidth(DIMENSION_MATRIX_VALUE_WIDTH)
        self.__label_SoftIron_m22__.setStyleSheet(BORDER_MAXTRIX_VALUE)

        self.__label_SoftIron_m23__ = QLabel(self.__current_SoftIron_m23__)
        self.__label_SoftIron_m23__.setFixedWidth(DIMENSION_MATRIX_VALUE_WIDTH)
        self.__label_SoftIron_m23__.setStyleSheet(BORDER_MAXTRIX_VALUE)

        self.__label_SoftIron_m31__ = QLabel(self.__current_SoftIron_m31__)
        self.__label_SoftIron_m31__.setFixedWidth(DIMENSION_MATRIX_VALUE_WIDTH)
        self.__label_SoftIron_m31__.setStyleSheet(BORDER_MAXTRIX_VALUE)

        self.__label_SoftIron_m32__ = QLabel(self.__current_SoftIron_m32__)
        self.__label_SoftIron_m32__.setFixedWidth(DIMENSION_MATRIX_VALUE_WIDTH)
        self.__label_SoftIron_m32__.setStyleSheet(BORDER_MAXTRIX_VALUE)

        self.__label_SoftIron_m33__ = QLabel(self.__current_SoftIron_m33__)
        self.__label_SoftIron_m33__.setFixedWidth(DIMENSION_MATRIX_VALUE_WIDTH)
        self.__label_SoftIron_m33__.setStyleSheet(BORDER_MAXTRIX_VALUE)

        self.__widget_SoftIron_Layout__ = QGridLayout()
        # self.__widget_SoftIron_Layout__.setContentsMargins(0, 0, 0, 0)
        self.__widget_SoftIron_Layout__.addWidget(
            self.__label_SoftIron__, 0, 0)
        self.__widget_SoftIron_Layout__.addWidget(
            self.__label_SoftIron_m11__, 0, 1)
        self.__widget_SoftIron_Layout__.addWidget(
            self.__label_SoftIron_m12__, 0, 2)
        self.__widget_SoftIron_Layout__.addWidget(
            self.__label_SoftIron_m13__, 0, 3)
        self.__widget_SoftIron_Layout__.addWidget(
            self.__label_SoftIron_m21__, 1, 1)
        self.__widget_SoftIron_Layout__.addWidget(
            self.__label_SoftIron_m22__, 1, 2)
        self.__widget_SoftIron_Layout__.addWidget(
            self.__label_SoftIron_m23__, 1, 3)
        self.__widget_SoftIron_Layout__.addWidget(
            self.__label_SoftIron_m31__, 2, 1)
        self.__widget_SoftIron_Layout__.addWidget(
            self.__label_SoftIron_m32__, 2, 2)
        self.__widget_SoftIron_Layout__.addWidget(
            self.__label_SoftIron_m33__, 2, 3)

        self.__widget_SoftIron__ = QWidget()
        # self.__widget_SoftIron__.setContentsMargins(0, 0, 0, 0)
        self.__widget_SoftIron__.setLayout(self.__widget_SoftIron_Layout__)

    def setRawData(self, data):
        self.rawData = data

    def onCalibrate(self):

        F = int(self.__current_NormOfGravity__)
        b = np.zeros([3, 1])
        A_1 = np.eye(3)

        s = self.rawData.T
        M, n, d = self.__ellipsoid_fit(s)

        # calibration parameters
        M_1 = linalg.inv(M)
        b = -np.dot(M_1, n)
        A_1 = np.real(F / np.sqrt(np.dot(n.T, np.dot(M_1, n)) - d)
                      * linalg.sqrtm(M))

        self.calibData = np.empty((0, 3), int)

        self.CalibTime = []

        currentTime = 0.0

        data = np.array(s).T
        for row in data:

            # subtract the hard iron offset
            xm_off = row[0]-b[0]
            ym_off = row[1]-b[1]
            zm_off = row[2]-b[2]

            # multiply by the inverse soft iron offset
            xm_cal = xm_off * A_1[0, 0] + ym_off * \
                A_1[0, 1] + zm_off * A_1[0, 2]
            ym_cal = xm_off * A_1[1, 0] + ym_off * \
                A_1[1, 1] + zm_off * A_1[1, 2]
            zm_cal = xm_off * A_1[2, 0] + ym_off * \
                A_1[2, 1] + zm_off * A_1[2, 2]

            self.calibData = np.append(self.calibData, np.array(
                [[xm_cal[0], ym_cal[0], zm_cal[0]]]), axis=0)

            self.CalibTime.append(currentTime)
            currentTime += 0.1

        self.__current_HardIronBias_b1__ = str(b[0][0])
        self.__current_HardIronBias_b2__ = str(b[1][0])
        self.__current_HardIronBias_b3__ = str(b[2][0])

        self.__current_SoftIron_m11__ = str(A_1[0, 0])
        self.__current_SoftIron_m12__ = str(A_1[1, 0])
        self.__current_SoftIron_m13__ = str(A_1[2, 0])
        self.__current_SoftIron_m21__ = str(A_1[0, 1])
        self.__current_SoftIron_m22__ = str(A_1[1, 1])
        self.__current_SoftIron_m23__ = str(A_1[2, 1])
        self.__current_SoftIron_m31__ = str(A_1[0, 2])
        self.__current_SoftIron_m32__ = str(A_1[1, 2])
        self.__current_SoftIron_m33__ = str(A_1[2, 2])

        # print('.hard_bias_x     = {},'.format(self.__current_HardIronBias_b1__))
        # print('.hard_bias_y     = {},'.format(self.__current_HardIronBias_b2__))
        # print('.hard_bias_z     = {},'.format(self.__current_HardIronBias_b3__))
        # print('.soft_bias_c11   = {},'.format(self.__current_SoftIron_m11__))
        # print('.soft_bias_c12   = {},'.format(self.__current_SoftIron_m12__))
        # print('.soft_bias_c13   = {},'.format(self.__current_SoftIron_m13__))
        # print('.soft_bias_c21   = {},'.format(self.__current_SoftIron_m21__))
        # print('.soft_bias_c22   = {},'.format(self.__current_SoftIron_m22__))
        # print('.soft_bias_c23   = {},'.format(self.__current_SoftIron_m23__))
        # print('.soft_bias_c31   = {},'.format(self.__current_SoftIron_m31__))
        # print('.soft_bias_c32   = {},'.format(self.__current_SoftIron_m32__))
        # print('.soft_bias_c33   = {},'.format(self.__current_SoftIron_m33__))

        self.__label_HardIronBias_b1__.setText(
            self.__current_HardIronBias_b1__)
        self.__label_HardIronBias_b2__.setText(
            self.__current_HardIronBias_b2__)
        self.__label_HardIronBias_b3__.setText(
            self.__current_HardIronBias_b3__)

        self.__label_SoftIron_m11__.setText(self.__current_SoftIron_m11__)
        self.__label_SoftIron_m12__.setText(self.__current_SoftIron_m12__)
        self.__label_SoftIron_m13__.setText(self.__current_SoftIron_m13__)
        self.__label_SoftIron_m21__.setText(self.__current_SoftIron_m21__)
        self.__label_SoftIron_m22__.setText(self.__current_SoftIron_m22__)
        self.__label_SoftIron_m23__.setText(self.__current_SoftIron_m23__)
        self.__label_SoftIron_m31__.setText(self.__current_SoftIron_m31__)
        self.__label_SoftIron_m32__.setText(self.__current_SoftIron_m32__)
        self.__label_SoftIron_m33__.setText(self.__current_SoftIron_m33__)

        ComponentMagPlotter().plotCalibData(self.CalibTime,
                                            self.calibData[:, 0], self.calibData[:, 1], self.calibData[:, 2])

    def __ellipsoid_fit(self, s):
        ''' Estimate ellipsoid parameters from a set of points.

            Parameters
            ----------
            s : array_like
              The samples (M,N) where M=3 (x,y,z) and N=number of samples.

            Returns
            -------
            M, n, d : array_like, array_like, float
              The ellipsoid parameters M, n, d.

            References
            ----------
            .. [1] Qingde Li; Griffiths, J.G., "Least squares ellipsoid specific
               fitting," in Geometric Modeling and Processing, 2004.
               Proceedings, vol., no., pp.335-340, 2004
        '''

        # D (samples)
        D = np.array([s[0]**2., s[1]**2., s[2]**2.,
                      2.*s[1]*s[2], 2.*s[0]*s[2], 2.*s[0]*s[1],
                      2.*s[0], 2.*s[1], 2.*s[2], np.ones_like(s[0])])

        # S, S_11, S_12, S_21, S_22 (eq. 11)
        S = np.dot(D, D.T)
        S_11 = S[:6, :6]
        S_12 = S[:6, 6:]
        S_21 = S[6:, :6]
        S_22 = S[6:, 6:]

        # C (Eq. 8, k=4)
        C = np.array([[-1,  1,  1,  0,  0,  0],
                      [1, -1,  1,  0,  0,  0],
                      [1,  1, -1,  0,  0,  0],
                      [0,  0,  0, -4,  0,  0],
                      [0,  0,  0,  0, -4,  0],
                      [0,  0,  0,  0,  0, -4]])

        # v_1 (eq. 15, solution)
        E = np.dot(linalg.inv(C),
                   S_11 - np.dot(S_12, np.dot(linalg.inv(S_22), S_21)))

        E_w, E_v = np.linalg.eig(E)

        v_1 = E_v[:, np.argmax(E_w)]
        if v_1[0] < 0:
            v_1 = -v_1

        # v_2 (eq. 13, solution)
        v_2 = np.dot(np.dot(-np.linalg.inv(S_22), S_21), v_1)

        # quadratic-form parameters, parameters h and f swapped as per correction by Roger R on Teslabs page
        M = np.array([[v_1[0], v_1[5], v_1[4]],
                      [v_1[5], v_1[1], v_1[3]],
                      [v_1[4], v_1[3], v_1[2]]])
        n = np.array([[v_2[0]],
                      [v_2[1]],
                      [v_2[2]]])
        d = v_2[3]

        return M, n, d
