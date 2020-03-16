# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_window(object):
    def setupUi(self, window):
        window.setObjectName("window")
        window.resize(789, 614)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(window.sizePolicy().hasHeightForWidth())
        window.setSizePolicy(sizePolicy)
        self.wid = QtWidgets.QWidget(window)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.wid.sizePolicy().hasHeightForWidth())
        self.wid.setSizePolicy(sizePolicy)
        self.wid.setObjectName("wid")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.wid)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 0, 621, 381))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.videoWidget = QVideoWidget(self.verticalLayoutWidget)
        self.videoWidget.setEnabled(True)
        self.videoWidget.setMinimumSize(QtCore.QSize(100, 100))
        self.videoWidget.setObjectName("videoWidget")
        self.verticalLayout.addWidget(self.videoWidget)
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.wid)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 390, 621, 80))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.playButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.playButton.setText("")
        self.playButton.setObjectName("playButton")
        self.horizontalLayout_2.addWidget(self.playButton)
        self.positionSlider = QtWidgets.QSlider(self.horizontalLayoutWidget)
        self.positionSlider.setOrientation(QtCore.Qt.Horizontal)
        self.positionSlider.setObjectName("positionSlider")
        self.horizontalLayout_2.addWidget(self.positionSlider)
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(self.wid)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(10, 480, 621, 80))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.pre_pb = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.pre_pb.setObjectName("pre_pb")
        self.horizontalLayout_3.addWidget(self.pre_pb)
        self.post_pb = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.post_pb.setObjectName("post_pb")
        self.horizontalLayout_3.addWidget(self.post_pb)
        self.separate_audio_pb = QtWidgets.QPushButton(self.wid)
        self.separate_audio_pb.setGeometry(QtCore.QRect(640, 10, 141, 31))
        self.separate_audio_pb.setObjectName("separate_audio_pb")
        self.play_chosen_pb = QtWidgets.QPushButton(self.wid)
        self.play_chosen_pb.setGeometry(QtCore.QRect(660, 504, 111, 31))
        self.play_chosen_pb.setObjectName("play_chosen_pb")
        window.setCentralWidget(self.wid)
        self.menuBar = QtWidgets.QMenuBar(window)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 789, 22))
        self.menuBar.setObjectName("menuBar")
        self.fileMenu = QtWidgets.QMenu(self.menuBar)
        self.fileMenu.setObjectName("fileMenu")
        window.setMenuBar(self.menuBar)
        self.statusbar = QtWidgets.QStatusBar(window)
        self.statusbar.setObjectName("statusbar")
        window.setStatusBar(self.statusbar)
        self.openAction = QtWidgets.QAction(window)
        self.openAction.setObjectName("openAction")
        self.exitAction = QtWidgets.QAction(window)
        self.exitAction.setObjectName("exitAction")
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addAction(self.exitAction)
        self.menuBar.addAction(self.fileMenu.menuAction())

        self.retranslateUi(window)
        QtCore.QMetaObject.connectSlotsByName(window)

    def retranslateUi(self, window):
        _translate = QtCore.QCoreApplication.translate
        window.setWindowTitle(_translate("window", "MainWindow"))
        self.pre_pb.setText(_translate("window", "Pre-Processing"))
        self.post_pb.setText(_translate("window", "Post-Processing"))
        self.separate_audio_pb.setText(_translate("window", "Separate Audio"))
        self.play_chosen_pb.setText(_translate("window", "Play Chosen"))
        self.fileMenu.setTitle(_translate("window", "File"))
        self.openAction.setText(_translate("window", "Open"))
        self.exitAction.setText(_translate("window", "Exit"))
from PyQt5.QtMultimediaWidgets import QVideoWidget


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    ui = Ui_window()
    ui.setupUi(window)
    window.show()
    sys.exit(app.exec_())
