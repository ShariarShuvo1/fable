import requests
from PyQt6.QtGui import QPixmap, QIcon
from pytube.__main__ import YouTube
from PyQt6 import QtCore
from ResolutionObject import ResolutionObject


class VideoInfoThread(QtCore.QThread):
    def set_values(self, window, card, url):
        self.window = window
        self.card = card
        self.url = url
        self.window.resolution_dict = {}

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
            self.card.video = YouTube(self.url, on_progress_callback=self.card.progress_func, on_complete_callback=self.card.complete_func)
            self.card.streams = self.card.video.streams
            data = QPixmap()
            data.loadFromData(requests.get(self.card.video.thumbnail_url, stream=True).content)
            self.card.thumbnail_preview.setPixmap(data.scaledToHeight(150))
            self.card.description_preview.setText(self.get_description())
            self.add_to_combo()
            self.window.download_button.setDisabled(False)

        except:
            self.card.description_preview.setText("This video can not be downloaded")
            self.card.thumbnail_preview.setPixmap(QPixmap('./assets/dummy_thumbnail.png').scaledToHeight(150))

    def add_to_combo(self):
        for r in self.card.streams:
            if r.type == 'video':
                obj = ResolutionObject(r, r.itag, r.mime_type, r.resolution, r.filesize_mb, r.fps)
            else:
                obj = ResolutionObject(r, r.itag, r.mime_type, r.abr, r.filesize_mb)
            self.window.resolution_dict[str(obj)] = obj
        idx = 0
        for stream in self.window.resolution_dict.keys():
            self.window.resolution_list.addItem(stream)
            if 'audio' in stream.lower():
                self.window.resolution_list.setItemIcon(idx, QIcon('assets/icons/music.png'))
            else:
                self.window.resolution_list.setItemIcon(idx, QIcon('assets/icons/video.png'))
            idx += 1
        self.window.resolution_list.setDisabled(False)
