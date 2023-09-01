from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QFont, QCursor, QMovie
from copy import deepcopy
from PyQt6.QtWidgets import QScrollArea, QWidget, QGroupBox, QFormLayout, QPushButton, QHBoxLayout, QLineEdit, \
    QVBoxLayout, QGridLayout, QLabel, QComboBox, QProgressBar
from Card import Card
from pytube.__main__ import YouTube
from VideoInfoThread import VideoInfoThread
from VideoDownloadThread import VideoDownloadThread
from DualDownloadThread import DualDownloadThread
from Downloader import Downloader


class Ui_youtubeDownloader(object):
    def __init__(self):
        self.dual_download_thread = None
        self.downloader_thread = None
        self.queue_processing = False
        self.downloading = False
        self.thumbnail: QPixmap = None
        self.url = None
        self.video_info_thread = None
        self.streams = None
        self.video: YouTube = None
        self.card_list = QVBoxLayout()
        self.description_preview = None
        self.thumbnail_preview = None
        self.media_row = None
        self.queue: list[Card] = []
        self.video_download_thread = None
        self.resolution_dict = {}
        self.download_thread = None
        self.source = None
        self.download_button = None
        self.resolution_list = None
        self.edit_box = None
        self.url_label = None
        self.download_row = None
        self.resolution_row = None
        self.width = 0
        self.height = 0
        self.cards: list[Card] = []
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

        font = QFont()
        font.setBold(True)
        font.setPointSize(16)

        w = 1200 // 100
        h = 900 // 100

        # Row 1 input
        self.download_row = QHBoxLayout()
        self.url_label = QLabel("URL: ")
        self.url_label.setFont(font)

        self.edit_box = QLineEdit()
        self.edit_box.setFont(font)
        self.edit_box.setClearButtonEnabled(True)
        self.edit_box.setPlaceholderText("Place your YouTube URL here")
        self.edit_box.textChanged.connect(self.text_changed)

        self.download_row.addWidget(self.url_label)
        self.download_row.addWidget(self.edit_box)

        # Row 2 Resolution selection
        self.resolution_row = QHBoxLayout()

        self.resolution_list = QComboBox()
        temp_font = font
        temp_font.setBold(False)
        temp_font.setPointSize(13)
        self.resolution_list.setFont(temp_font)
        self.resolution_list.setPlaceholderText("Select a resolution")
        self.resolution_list.setDisabled(True)

        self.download_button = QPushButton("Download")
        self.download_button.setFont(font)
        self.download_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.download_button.setMaximumWidth(w * 20)
        self.download_button.clicked.connect(self.download_clicked)
        self.download_button.setDisabled(True)

        self.resolution_row.addWidget(self.resolution_list)
        self.resolution_row.addWidget(self.download_button)

        # Row 3 Media Info
        self.media_row = QHBoxLayout()
        self.thumbnail_preview = QLabel()
        self.thumbnail_preview.setPixmap(QPixmap('./assets/dummy_thumbnail.png').scaledToHeight(150))
        self.thumbnail_preview.setMaximumWidth(270)

        self.description_preview = QLabel()
        temp_font = font
        temp_font.setPointSize(13)
        temp_font.setBold(False)
        self.description_preview.setFont(temp_font)

        self.media_row.addWidget(self.thumbnail_preview)
        self.media_row.addWidget(self.description_preview)

        self.body.addLayout(self.download_row)
        self.body.addLayout(self.resolution_row)
        self.body.addLayout(self.media_row)
        empty_line = QLabel()
        empty_line.setMaximumHeight(2)
        empty_line.setStyleSheet("background-color: blue")
        self.body.addWidget(empty_line)
        self.body.addLayout(self.card_list)
        
        self.group_layout.setLayout(self.body)
        self.scroll_bar = QScrollArea()
        self.scroll_bar.setWidget(self.group_layout)
        self.scroll_bar.setWidgetResizable(True)
        self.YoutubeWindow.setCentralWidget(self.scroll_bar)
        QtCore.QMetaObject.connectSlotsByName(self.YoutubeWindow)

    def text_changed(self):
        self.description_preview.clear()
        self.thumbnail_preview.setPixmap(QPixmap('./assets/dummy_thumbnail.png').scaledToHeight(150))
        self.resolution_list.clear()
        self.download_button.setDisabled(True)
        self.resolution_list.setDisabled(True)
        self.video = None
        self.streams = None

        self.url = self.edit_box.text()
        if len(self.url) > 10:
            gif = QMovie('./assets/thumbnail_loading.gif')
            gif.setScaledSize(QSize(270, 150))
            self.thumbnail_preview.setMovie(gif)
            gif.start()
            self.video_info_thread = VideoInfoThread()
            self.video_info_thread.set_values(self, self.url)
            self.video_info_thread.start()

    def queue_process(self):
        if len(self.queue) > 0:
            self.downloading = True
            card = self.queue.pop(0)
            self.download(card)

    def download(self, card: Card):
        card.description_preview.setEnabled(True)
        if card.is_progressive or card.video_type in 'audio':
            self.video_download_thread = VideoDownloadThread()
            self.video_download_thread.set_values(card, self)
            self.video_download_thread.start()
        else:
            self.dual_download_thread = DualDownloadThread()
            self.dual_download_thread.set_values(card, self)
            self.dual_download_thread.start()

    def download_clicked(self):
        self.cards.append(Card(self, self.url, self.resolution_dict[self.resolution_list.currentText()].source))
        last_card = self.cards[-1]
        last_card.description_preview.setDisabled(True)
        self.card_list.insertLayout(0, last_card.card)
        self.queue.append(last_card)
        if not self.downloading:
            self.queue_process()

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
