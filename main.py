from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor, QPicture, QPixmap
from audioDownloader import Ui_audioDownloader as ad
from youtubeWindow import Ui_youtubeDownloader as yd
from ObjectBuilder import object_builder
from pytube.__main__ import YouTube

class Ui_MainWindow(object):
    def __init__(self):
        self.title_logo = None
        self.title = None
        self.height = None
        self.width = None
        self.MainWindow = None
        self.youtubeDownloader = None
        self.centralwidget = None
        self.audioDownloader = None
        self.pointingHandMouse = QCursor(Qt.CursorShape.PointingHandCursor)
        self.ydGenerated = False
        self.adGenerated = False
        self.main_ui = None

    def setupUi(self, MainWindow, main_ui):
        self.main_ui = main_ui
        self.MainWindow = MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowIcon(QtGui.QIcon('./assets/logo.png'))
        MainWindow.setWindowTitle("Fable")
        MainWindow.resize(600, 500)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        
        self.title_logo: QtWidgets.QLabel = object_builder(QtWidgets.QLabel(parent=self.centralwidget), (150, 20, 101, 101), "", 24, True, "", None, None, "Fable")
        self.title_logo.setPixmap(QPixmap('./assets/logo.png').scaledToHeight(101))
        self.title: QtWidgets.QLabel = object_builder(QtWidgets.QLabel(parent=self.centralwidget), (260, 20, 301, 100), "Fabel", 54, True, "", None, None, "Fable")

        self.audioDownloader = object_builder(QtWidgets.QPushButton(parent=self.centralwidget), (50, 150, 501, 101), "Story Downloader", 24, True, "", self.audioDownloaderGenerator, self.pointingHandMouse, "Download Audio Story")

        self.youtubeDownloader = object_builder(QtWidgets.QPushButton(parent=self.centralwidget), (50, 330, 501, 101), "YouTube Downloader", 24, True, "", self.youtubeDownloaderGenerator, self.pointingHandMouse, "Download Youtube Video")

        MainWindow.setCentralWidget(self.centralwidget)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def mainHide(self):
        self.MainWindow.hide()

    def audioDownloaderGenerator(self):
        if not self.adGenerated:
            self.adGenerated = True
            self.mainHide()
            self.adWindow = QtWidgets.QMainWindow()
            self.adUi = ad()
            self.adUi.setupUi(self.adWindow, MainWindow)
            self.adWindow.show()
        else:
            self.mainHide()
            self.adWindow.show()

    def youtubeDownloaderGenerator(self):
        if not self.ydGenerated:
            self.ydGenerated = True
            self.mainHide()
            self.ydWindow = QtWidgets.QMainWindow()
            self.ydUi = yd()
            self.ydUi.setupUi(self.ydWindow, MainWindow)
            self.ydWindow.show()
        else:
            self.mainHide()
            self.ydWindow.show()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    screenSize = app.screens()[0].availableGeometry()
    ui.height = screenSize.height()
    ui.width = screenSize.width()
    ui.setupUi(MainWindow, ui)
    MainWindow.show()
    sys.exit(app.exec())
