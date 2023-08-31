from PyQt6 import QtCore
from pytube.__main__ import YouTube


class VideoDownloadThread(QtCore.QThread):
    def set_values(self, card, window):
        self.card = card
        self.window = window
        self.window.downloading = True

    def run(self):
        video_object = YouTube(self.card.url, on_progress_callback=self.card.progress_func, on_complete_callback=self.card.complete_func)
        video = video_object.streams.get_by_itag(self.card.itag)
        self.video = video
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
        self.card.progress_bar.resetFormat()
        video.download(filename=title)
        self.card.download_complete = True
        self.window.downloading = False
