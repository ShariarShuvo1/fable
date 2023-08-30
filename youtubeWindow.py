from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from PyQt6.QtWidgets import QScrollArea, QWidget, QGroupBox, QFormLayout, QPushButton, QHBoxLayout, QLineEdit, \
    QVBoxLayout, QGridLayout, QLabel, QComboBox, QProgressBar
from Card import Card
from pytube.__main__ import YouTube


class Ui_youtubeDownloader(object):
    def __init__(self):
        self.width = 0
        self.height = 0
        self.cards = []
        self.group_layout = None
        self.scroll_bar = None
        self.scroll = None
        self.ui = None
        self.centralwidget = None
        self.body = None
        self.YoutubeWindow = None
        self.MainWindow = None

    def setupUi(self, YoutubeWindow, MainWindow):
        self.MainWindow = MainWindow
        self.YoutubeWindow = YoutubeWindow
        self.YoutubeWindow.setFixedSize(1220, 900)

        self.group_layout = QGroupBox()
        self.group_layout.setFixedWidth(1200)
        self.group_layout.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum))

        self.body = QVBoxLayout()

        self.cards.append(Card(self))

        for card in self.cards:
            self.body.addLayout(card.card)
        self.group_layout.setLayout(self.body)
        self.scroll_bar = QScrollArea()
        self.scroll_bar.setWidget(self.group_layout)
        self.scroll_bar.setWidgetResizable(True)
        self.YoutubeWindow.setCentralWidget(self.scroll_bar)
        QtCore.QMetaObject.connectSlotsByName(self.YoutubeWindow)

    def add_new_card(self):
        self.cards.append(Card(self))
        self.body.addLayout(self.cards[-1].card)

    def delete_card(self, card, obj):
        if len(self.cards) > 1 and obj.download_button.text() == 'Downloaded':
            for i in range(self.body.count()):
                layout_item = self.body.itemAt(i)
                if layout_item.layout() == card:
                    for j in reversed(range(layout_item.count())):
                        new_layout = layout_item.itemAt(j)
                        for k in reversed(range(new_layout.count())):
                            new_layout.itemAt(k).widget().deleteLater()
                        layout_item.removeItem(new_layout)
                    self.body.removeItem(layout_item)
                    break
            self.cards.remove(obj)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    youtubeDownloader = QtWidgets.QMainWindow()
    ui = Ui_youtubeDownloader()
    ui.setupUi(youtubeDownloader, 'Dummy')
    youtubeDownloader.show()
    sys.exit(app.exec())
