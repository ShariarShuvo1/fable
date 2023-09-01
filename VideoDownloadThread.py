from PyQt6 import QtCore
from pytube.__main__ import YouTube
from re import sub as remove_space


class VideoDownloadThread(QtCore.QThread):
    def set_values(self, card, window):
        self.card = card
        self.window = window
        self.window.downloading = True

    def run(self):
        self.card.status_label.setText('Fetching Data')
        video_object = YouTube(self.card.url, on_progress_callback=self.card.progress_func)
        video = video_object.streams.get_by_itag(self.card.itag)
        self.card.video = video
        extension = video.mime_type.split('/')[1]
        t = ""
        for char in video_object.title:
            if char not in "#%&{}/|\\$!'\":@<>*?+`~=.":
                t += char
        if video.is_progressive:
            p = "_not_rendered"
        else:
            p = "_rendered"
        if video.type == 'video':

            res = '_' + str(video.resolution)
            fps = '_' + str(video.fps) + 'fps'
            title = t + fps + res + p + f'.{extension}'
        else:
            if extension == 'mp4':
                extension = 'mp3'
            abr = '_' + video.abr
            title = t + abr + p + f'.{extension}'
        title = remove_space(' +', ' ', title)
        if video.type == 'audio':
            self.card.progress_bar.setStyleSheet("QProgressBar::chunk {background-color: red;}")
        self.card.status_label.setText(f'Downloading {video.type}')
        video.download(filename=title)
        self.card.status_label.setText('Download Complete')
        self.window.downloading = False
        self.card.progress_bar.setStyleSheet("QProgressBar::chunk {background-color: blue;}")
        self.card.delete_button.setDisabled(False)
        self.window.queue_process()
