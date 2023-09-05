import PyQt6
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QGroupBox, QPushButton, QVBoxLayout, QLabel, QScrollArea, QHBoxLayout, QLineEdit
from CurrentCard import CurrentCard
from DownloadingCard import DownloadingCard


class Ui_audioDownloader(object):
    def __init__(self):
        self.downloading_list: list[DownloadingCard] = list()
        self.current_list: list[CurrentCard] = list()
        self.download_button: QPushButton = None
        self.add_button: QPushButton = None
        self.downloading_list_viewer: QVBoxLayout = None
        self.current_list_viewer: QVBoxLayout = None
        self.edit_box: QLineEdit = None
        self.url_label = None
        self.download_row = None
        self.scroll_bar = None
        self.body = None
        self.back_button = None
        self.group_layout = None
        self.audioDownloader = None
        self.MainWindow = None

    def setupUi(self, audioDownloader, MainWindow):
        self.MainWindow = MainWindow
        self.audioDownloader = audioDownloader
        self.audioDownloader.setFixedSize(1220, 900)

        self.group_layout = QGroupBox()
        self.group_layout.setFixedWidth(1200)
        self.group_layout.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum))

        self.body = QVBoxLayout()

        font = QFont()
        font.setBold(True)
        font.setPointSize(16)

        w = 1200 // 100
        h = 900 // 100

        # Back Button
        self.back_button = QPushButton('<--BACK')
        self.back_button.setFont(font)
        self.back_button.setMaximumWidth(w * 10)
        self.back_button.clicked.connect(self.back_button_clicked)

        # URL Row
        self.download_row = QHBoxLayout()
        self.url_label = QLabel("URL: ")
        self.url_label.setFont(font)

        self.edit_box = QLineEdit()
        self.edit_box.setFont(font)
        self.edit_box.setClearButtonEnabled(True)
        self.edit_box.setPlaceholderText("Place your YouTube URL here")

        self.add_button = QPushButton('ADD')
        self.add_button.setFont(font)
        self.add_button.setStyleSheet('background-color: #32CD32')
        self.add_button.clicked.connect(self.add_button_clicked)

        self.download_row.addWidget(self.url_label)
        self.download_row.addWidget(self.edit_box)
        self.download_row.addWidget(self.add_button)

        self.body.addWidget(self.back_button)
        self.body.addLayout(self.download_row)

        self.current_list_viewer = QVBoxLayout()

        self.download_button = QPushButton('Download')
        self.download_button.setFont(font)
        self.download_button.setStyleSheet('background-color: ')
        self.download_button.setStyleSheet('background-color: #1be0af')
        self.download_button.clicked.connect(self.download_button_clicked)
        self.download_button.hide()

        self.body.addLayout(self.current_list_viewer)
        self.body.addWidget(self.download_button)
        empty_line = QLabel()
        empty_line.setMaximumHeight(2)
        empty_line.setStyleSheet("background-color: blue")
        self.body.addWidget(empty_line)

        self.downloading_list_viewer = QVBoxLayout()

        self.body.addLayout(self.downloading_list_viewer)
        self.group_layout.setLayout(self.body)
        self.scroll_bar = QScrollArea()
        self.scroll_bar.setWidget(self.group_layout)
        self.scroll_bar.setWidgetResizable(True)
        self.audioDownloader.setCentralWidget(self.scroll_bar)
        QtCore.QMetaObject.connectSlotsByName(audioDownloader)

    def delete_current_card(self, obj: CurrentCard):
        obj.video_thread.terminate()
        for i in reversed(range(obj.layout.count())):
            item = obj.layout.itemAt(i)
            if type(item) == PyQt6.QtWidgets.QHBoxLayout:
                for j in reversed(range(item.count())):
                    item2 = item.layout().itemAt(j)
                    if type(item2) == PyQt6.QtWidgets.QVBoxLayout:
                        for k in reversed(range(item2.count())):
                            item2.itemAt(k).widget().deleteLater()
                    else:
                        item.itemAt(j).widget().deleteLater()
                    item.removeItem(item2)
                obj.layout.removeItem(item)
            else:
                obj.layout.itemAt(i).widget().deleteLater()
        self.current_list_viewer.removeItem(obj.layout)
        self.current_list.remove(obj)
        if len(self.current_list) == 0:
            self.download_button.hide()

    def do_download(self):
        activate_download_button = True
        for card in self.current_list:
            if card.title.text() == "Invalid URL!" and card.title.text() == "":
                activate_download_button = False
                break
        return activate_download_button

    def add_button_clicked(self):
        if len(self.edit_box.text()) > 10:
            card = CurrentCard(self, self.edit_box.text())
            self.current_list_viewer.addLayout(card.layout)
            self.current_list.append(card)
            self.download_button.show()

    def download_button_clicked(self):
        if self.do_download():
            url_list = []
            for element in self.current_list:
                url_list.append(element.url)
            card = DownloadingCard(url_list, self)
            self.downloading_list_viewer.insertLayout(0, card.layout)
            self.downloading_list.append(card)
            for obj in self.current_list.copy():
                self.delete_current_card(obj)
            self.edit_box.clear()
            self.current_list = []

    def delete_card(self, obj: DownloadingCard):
        obj.downloader_thread.terminate()
        for i in reversed(range(obj.layout.count())):
            item = obj.layout.itemAt(i)
            if type(item) == PyQt6.QtWidgets.QVBoxLayout:
                for k in reversed(range(item.count())):
                    item.itemAt(k).widget().deleteLater()
                obj.layout.removeItem(item)
            else:
                item.widget().deleteLater()
        self.downloading_list_viewer.removeItem(obj.layout)
        self.downloading_list.remove(obj)




    def back_button_clicked(self):
        self.MainWindow.show()
        self.audioDownloader.hide()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    audioDownloader = QtWidgets.QMainWindow()
    ui = Ui_audioDownloader()
    ui.setupUi(audioDownloader, 'Dummy')
    audioDownloader.show()
    sys.exit(app.exec())
