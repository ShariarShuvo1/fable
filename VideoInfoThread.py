import requests
from PyQt6.QtGui import QPixmap
from pytube.__main__ import YouTube
from PyQt6 import QtCore


class VideoInfoThread(QtCore.QThread):
    def set_values(self, card, url):
        self.card = card
        self.url = url

    def get_description(self):
        time = self.card.video.length
        duration_hour = time//3600
        duration_minute = (time-(duration_hour*3600))//60
        duration_second = time - (duration_hour*3600) - (duration_minute*60)
        if duration_hour != 0:
            time = f'{duration_hour} Hour: {duration_minute} Minute: {duration_second} Second'
        elif duration_minute != 0:
            time = f'{duration_minute} Minute: {duration_second} Second'
        else:
            time = f'{duration_second} Second'
        return f'Title: {self.card.video.title}\nChannel: {self.card.video.author}\nViews: {self.card.video.views}\nDuration: {time}'

    def run(self):
        try:
            self.card.description_preview.setText("Loading ...")
            self.card.video = YouTube(self.url)
            self.card.streams = YouTube(self.url).streams
            data = QPixmap()
            data.loadFromData(requests.get(self.card.video.thumbnail_url, stream=True).content)
            self.card.thumbnail_preview.setPixmap(data.scaledToHeight(150))
            self.card.description_preview.setText(self.get_description())

        except:
            self.card.description_preview.setText("This video can not be downloaded")
            self.card.thumbnail_preview.setPixmap(QPixmap('./assets/dummy_thumbnail.png').scaledToHeight(150))
