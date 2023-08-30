from PyQt6 import QtCore
from pytube.__main__ import YouTube


class DualDownloadThread(QtCore.QThread):
    def set_values(self, card, video):
        self.card = card
        self.video = video
        self.audio = self.card.streams.filter(only_audio=True).first()

    def run(self):
        self.card.download_button.setText('Downloading Video')
        extension_video = self.video.mime_type.split('/')[1]
        t = ""
        for char in self.video.title:
            if char not in "#%&{}()[]^;/|\\$!'\":@<>*?+`~=.":
                t += char

        res = '_' + str(self.video.resolution)
        fps = '_' + str(self.video.fps) + 'fps'
        self.card.video_title = t + fps + res + f'.{extension_video}'
        extension_audio = self.audio.mime_type.split('/')[1]
        if extension_audio == 'mp4':
            extension_audio = 'mp3'
        abr = '_' + self.audio.abr
        audio_title = t + abr + f'.{extension_audio}'
        self.card.video_path = f'./downloads/{self.card.video_title}'
        self.card.video_path = self.video.download(output_path='./downloads/', filename=self.card.video_title)
        self.card.progress_bar.setValue(0)
        self.card.progress_bar.setStyleSheet("QProgressBar::chunk {background-color: red;}")
        self.card.download_button.setText('Downloading Audio')

        self.card.audio_path = f'./downloads/{audio_title}'
        self.card.audio_path = self.video.download(output_path='./downloads/', filename=audio_title)
        self.card.download_button.setText('Downloaded')
        self.card.merge_files()

