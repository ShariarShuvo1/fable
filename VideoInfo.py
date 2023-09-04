import requests
from PyQt6.QtGui import QPixmap

from pytube.__main__ import YouTube
from PyQt6 import QtCore


class VideoInfo(QtCore.QThread):
    def set_value(self, card, window):
        self.window = window
        self.card = card
        self.card.title.setText('Loading...')

    def run(self):
        try:
            self.card.video = YouTube(self.card.url)
            self.card.title.setText(self.card.video.title)
            self.card.thumbnail = QPixmap()
            self.card.thumbnail.loadFromData(requests.get(self.card.video.thumbnail_url.replace('hq720.jpg', 'maxresdefault.jpg'), stream=True).content)
            self.card.thumbnail_preview.setPixmap(self.card.thumbnail.scaledToHeight(39))
        except:
            self.card.thumbnail_preview.setPixmap(QPixmap('./assets/dummy_thumbnail.png').scaledToHeight(39))
            self.card.title.setText('Invalid URL!')
