import requests
import moviepy.editor as VideoEditor
import subprocess
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QFont, QCursor, QMovie, QIcon
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QProgressBar
from pytube.__main__ import YouTube
from VideoInfoThread import VideoInfoThread
from VideoDownloadThread import VideoDownloadThread
from DualDownloadThread import DualDownloadThread


class Card:
    def __init__(self, ui):
        self.video_title = ""
        self.video_download_thread = None
        self.audio_path = ""
        self.video_path = ""
        self.ui = ui
        self.path = ""
        self.source = None
        self.download_thread = None
        self.resolution_dict = dict()
        self.video_info_thread = None
        self.video = None
        self.streams = None
        w = 1200 // 100
        h = 900 // 100
        self.card = QVBoxLayout()
        font = QFont()
        font.setBold(True)
        font.setPointSize(16)

        # Row 1 input
        self.row1 = QHBoxLayout()
        self.url = QLabel("URL: ")
        self.url.setFont(font)

        self.edit_box = QLineEdit()
        self.edit_box.setFont(font)
        self.edit_box.setClearButtonEnabled(True)
        self.edit_box.setPlaceholderText("Place your YouTube URL here")
        self.edit_box.textChanged.connect(self.text_changed)

        self.delete_button = QPushButton()
        self.delete_button.setIcon(QIcon("./assets/icons/delete.png"))
        self.delete_button.setFixedWidth(50)
        self.delete_button.setFixedHeight(35)
        self.delete_button.setStyleSheet("QPushButton::hover{background-color: red;}")
        self.delete_button.clicked.connect(self.initiate_delete_card)

        self.row1.addWidget(self.url)
        self.row1.addWidget(self.edit_box)
        self.row1.addWidget(self.delete_button)

        # Row 2 Quality selection
        self.row2 = QHBoxLayout()

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

        self.row2.addWidget(self.resolution_list)
        self.row2.addWidget(self.download_button)

        # Row 3 Media Info
        self.row3 = QHBoxLayout()
        self.thumbnail_preview = QLabel()
        self.thumbnail_preview.setPixmap(QPixmap('./assets/dummy_thumbnail.png').scaledToHeight(150))
        self.thumbnail_preview.setMaximumWidth(270)

        self.description_preview = QLabel()
        temp_font = font
        temp_font.setPointSize(13)
        temp_font.setBold(False)
        self.description_preview.setFont(temp_font)

        self.row3.addWidget(self.thumbnail_preview)
        self.row3.addWidget(self.description_preview)

        # Row 4 Downloading Status
        self.row4 = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(20)

        self.empty_line = QLabel()
        self.empty_line.setMaximumHeight(2)
        self.empty_line.setStyleSheet("background-color: red")

        self.row4.addWidget(self.progress_bar)
        self.row4.addWidget(self.empty_line)

        self.card.addLayout(self.row1)
        self.card.addLayout(self.row2)
        self.card.addLayout(self.row3)
        self.card.addLayout(self.row4)

    def text_changed(self):
        self.description_preview.clear()
        self.thumbnail_preview.setPixmap(QPixmap('./assets/dummy_thumbnail.png').scaledToHeight(150))
        url = self.edit_box.text()
        if len(url) > 10:
            gif = QMovie('./assets/thumbnail_loading.gif')
            gif.setScaledSize(QSize(270, 150))
            self.thumbnail_preview.setMovie(gif)
            gif.start()
            self.video_info_thread = VideoInfoThread()
            self.video_info_thread.set_values(self, url)
            self.video_info_thread.start()

    def download_clicked(self):
        txt = self.resolution_list.currentText()
        if len(txt) > 3:
            self.source = self.resolution_dict[txt].source

            if self.source.is_progressive or self.source.type == 'audio':
                self.download_thread = VideoDownloadThread()
                self.download_thread.set_values(self, self.source)
                self.download_thread.start()
            elif self.source.type == 'video':
                self.video_download_thread = DualDownloadThread()
                self.video_download_thread.set_values(self, self.source)
                self.video_download_thread.start()

            self.edit_box.setDisabled(True)
            self.url.setDisabled(True)
            self.resolution_list.setDisabled(True)
            self.download_button.setDisabled(True)
            self.ui.add_new_card()

    def progress_func(self, video, file_path, remaining):
        finished = int(((self.source.filesize - remaining)/self.source.filesize)*100)
        self.progress_bar.setValue(finished)

    def complete_func(self, a, b):
        self.progress_bar.setValue(100)

    def initiate_delete_card(self):
        self.ui.delete_card(self.card, self)
