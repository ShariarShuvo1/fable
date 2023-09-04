from PyQt6.QtCore import QSize
from PyQt6.QtGui import QPixmap, QMovie, QIcon
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QLineEdit, QPushButton
from pytube.__main__ import YouTube
from VideoInfo import VideoInfo


class CurrentCard:
    def __init__(self, window, url):
        self.window = window
        self.url = url

        self.layout = QVBoxLayout()
        self.empty_line = QLabel()
        self.empty_line.setStyleSheet("background-color: black")
        self.empty_line.setMaximumHeight(1)
        self.layout.addWidget(self.empty_line)

        self.card_layout = QHBoxLayout()

        self.thumbnail_preview = QLabel()
        self.gif = QMovie('./assets/thumbnail_loading.gif')
        self.gif.setScaledSize(QSize(70, 39))
        self.thumbnail_preview.setMovie(self.gif)
        self.gif.start()
        self.card_layout.addWidget(self.thumbnail_preview)

        self.data_layout = QVBoxLayout()
        self.edit_text = QLineEdit()
        self.edit_text.setText(self.url)
        self.edit_text.setPlaceholderText("Paste new URL here")
        self.edit_text.textChanged.connect(self.text_changed)

        self.title = QLabel("")

        self.data_layout.addWidget(self.edit_text)
        self.data_layout.addWidget(self.title)

        self.card_layout.addLayout(self.data_layout)

        self.delete_button = QPushButton()
        self.delete_button.setIcon(QIcon('./assets/icons/delete.png'))
        self.delete_button.setMaximumHeight(60)
        self.delete_button.setStyleSheet("QPushButton::hover{background-color: red;}")
        self.delete_button.clicked.connect(self.delete_clicked)

        self.card_layout.addWidget(self.delete_button)

        self.layout.addLayout(self.card_layout)

        self.video: YouTube = None

        self.video_thread = VideoInfo()
        self.video_thread.set_value(self, window)
        self.video_thread.start()

    def text_changed(self):
        self.url = self.edit_text.text()
        self.gif = QMovie('./assets/thumbnail_loading.gif')
        self.gif.setScaledSize(QSize(70, 39))
        self.thumbnail_preview.setMovie(self.gif)
        self.gif.start()
        self.video_thread.terminate()
        self.video_thread = VideoInfo()
        self.video_thread.set_value(self, self.window)
        self.video_thread.start()

    def delete_clicked(self):
        self.window.delete_current_card(self)
