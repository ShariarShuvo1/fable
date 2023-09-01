import requests
from PyQt6.QtGui import QPixmap, QIcon
from pytube.__main__ import YouTube
from PyQt6 import QtCore
from ResolutionObject import ResolutionObject


class VideoInfoThread(QtCore.QThread):
    def set_values(self, window, url):
        self.window = window
        self.url = url

    def get_description(self):
        time = self.window.video.length
        duration_hour = time//3600
        duration_minute = (time-(duration_hour*3600))//60
        duration_second = time - (duration_hour*3600) - (duration_minute*60)
        if duration_hour != 0:
            time = f'{duration_hour} Hour: {duration_minute} Minute: {duration_second} Second'
        elif duration_minute != 0:
            time = f'{duration_minute} Minute: {duration_second} Second'
        else:
            time = f'{duration_second} Second'
        return f'Title: {self.window.video.title}\nChannel: {self.window.video.author}\nViews: {self.window.video.views}\nDuration: {time}'

    def run(self):
        try:
            self.window.description_preview.setText("Loading ...")
            self.window.video = YouTube(self.url)
            self.window.streams = self.window.video.streams
            self.window.thumbnail = QPixmap()
            self.window.thumbnail.loadFromData(requests.get(self.window.video.thumbnail_url.replace('hq720.jpg', 'maxresdefault.jpg'), stream=True).content)
            self.window.thumbnail_preview.setPixmap(self.window.thumbnail.scaledToHeight(150))
            self.window.description_preview.setText(self.get_description())
            self.add_to_combo()

        except:
            self.window.description_preview.setText("This video can not be downloaded")
            self.window.thumbnail_preview.setPixmap(QPixmap('./assets/dummy_thumbnail.png').scaledToHeight(150))

    def add_to_combo(self):
        self.window.resolution_dict = {}
        for r in self.window.video.streams:
            if r.type == 'video':
                obj = ResolutionObject(r, r.itag, r.mime_type, r.resolution, r.filesize_mb, r.fps)
            else:
                obj = ResolutionObject(r, r.itag, r.mime_type, r.abr, r.filesize_mb)
            self.window.resolution_dict[str(obj)] = obj
        idx = 0
        for stream, obj in self.window.resolution_dict.items():
            self.window.resolution_list.addItem(stream)
            if 'audio' in stream.lower():
                self.window.resolution_list.setItemIcon(idx, QIcon('assets/icons/music.png'))
            elif obj.source.is_progressive:
                self.window.resolution_list.setItemIcon(idx, QIcon('assets/icons/video-audio.png'))
            else:
                if obj.nvidia_available and 'mp4' in obj.source.mime_type:
                    self.window.resolution_list.setItemIcon(idx, QIcon('assets/icons/nvidia.png'))
                else:
                    self.window.resolution_list.setItemIcon(idx, QIcon('assets/icons/video.png'))
            idx += 1
        self.window.resolution_list.setDisabled(False)
        self.window.download_button.setDisabled(False)
