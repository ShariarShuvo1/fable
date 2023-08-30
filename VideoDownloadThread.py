from PyQt6 import QtCore
from pytube.__main__ import YouTube


class VideoDownloadThread(QtCore.QThread):
    def set_values(self, card, video):
        self.card = card
        self.video = video

    def run(self):
        self.card.download_button.setText('Downloading Video')
        title = ""
        extension = self.video.mime_type.split('/')[1]
        p = ""
        t = ""
        for char in self.video.title:
            if char not in "#%&{}/|\\$!'\":@<>*?+`~=.":
                t += char
        if self.video.is_progressive:
            p = "_progressive"
        else:
            p = "_not_progressive"
        if self.video.type == 'video':

            res = '_' + str(self.video.resolution)
            fps = '_' + str(self.video.fps) + 'fps'
            title = t + fps + res + p + f'.{extension}'
        else:
            if extension == 'mp4':
                extension = 'mp3'
            abr = '_' + self.video.abr
            title = t + abr + p + f'.{extension}'

        self.card.path = f'./downloads/title'
        self.video.download(output_path='./downloads/', filename=title)
        self.card.download_button.setText('Downloaded')
