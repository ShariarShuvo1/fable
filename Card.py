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

    def __init__(self, ui, url, video):
        self.ui = ui
        self.url = url
        self.video = video
        self.itag = self.video.itag
        self.is_progressive = self.video.is_progressive
        self.video_type = self.video.type
        self.card = QVBoxLayout()
        self.download_complete = False
        self.downloading = False
        self.current_text = ""
        self.video_title = ""
        self.video_download_thread = None
        self.audio_path = ""
        self.video_path = ""
        self.path = ""
        self.source = None
        self.download_thread = None
        self.resolution_dict = dict()
        self.video_info_thread = None
        self.streams = None
        w = 1200 // 100
        h = 900 // 100
        font = QFont()
        font.setBold(True)
        font.setPointSize(16)

        # Row 3 Media Info
        self.media_row = QHBoxLayout()
        self.thumbnail_preview = QLabel()
        self.thumbnail_preview.setPixmap(self.ui.thumbnail.scaledToHeight(68))
        self.thumbnail_preview.setMaximumWidth(120)

        self.description_preview = QLabel()
        temp_font = font
        temp_font.setPointSize(11)
        temp_font.setBold(False)
        self.description_preview.setFont(temp_font)
        if 'video' in self.video.type:
            string_to_display = f'{self.ui.video.title}\nQuality: {self.video.resolution}\nFPS: {self.video.fps}'
        else:
            string_to_display = f'{self.ui.video.title}\nQuality: {self.video.abr}\nType: Audio'
        self.description_preview.setText(string_to_display)

        self.media_row.addWidget(self.thumbnail_preview)
        self.media_row.addWidget(self.description_preview)

        # Row 4 Downloading Status
        self.progress_bar_row = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(20)

        self.delete_button = QPushButton()
        self.delete_button.setIcon(QIcon("./assets/icons/delete.png"))
        self.delete_button.setFixedWidth(50)
        self.delete_button.setFixedHeight(35)
        self.delete_button.setStyleSheet("QPushButton::hover{background-color: red;}")
        self.delete_button.clicked.connect(self.initiate_delete_card)

        self.progress_bar_row.addWidget(self.progress_bar)
        self.progress_bar_row.addWidget(self.delete_button)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("QProgressBar::chunk {background-color: green;}")

        # Row 5 empty line

        self.empty_line_row = QVBoxLayout()

        self.empty_line = QLabel()
        self.empty_line.setMaximumHeight(2)
        self.empty_line.setStyleSheet("background-color: red")

        self.empty_line_row.addWidget(self.empty_line)

        self.card.addLayout(self.media_row)
        self.card.addLayout(self.progress_bar_row)
        self.card.addLayout(self.empty_line_row)

    def progress_func(self, video, file_path, remaining):
        finished = int(((self.video.filesize - remaining)/self.video.filesize)*100)
        self.progress_bar.setValue(finished)

    def complete_func(self, a, b):
        self.progress_bar.setValue(100)

    def initiate_delete_card(self):
        self.ui.delete_card(self.card, self)
