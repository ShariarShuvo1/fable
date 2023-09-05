from PyQt6 import QtCore
from PyQt6.QtCore import pyqtSignal
from pytube.__main__ import request as pytube_request
from pytube.__main__ import YouTube
from re import sub as remove_space


class VideoDownloadThread(QtCore.QThread):
    progress_value = pyqtSignal(int)
    status_text = pyqtSignal(str)
    style_sheet = pyqtSignal(str)
    do_toggle = pyqtSignal(bool)

    def set_values(self, card, window):
        self.card = card
        self.window = window
        self.window.downloading = True

    def toggle_delete_button(self, toggle):
        self.do_toggle.emit(toggle)

    def update_style_sheet(self, style):
        self.style_sheet.emit(style)

    def update_value(self, value):
        self.progress_value.emit(value)

    def progress_func(self, video, file_path, remaining):
        finished = int(((self.filesize - remaining) / self.filesize) * 100)
        self.update_value(finished)

    def update_status_text(self, txt):
        self.status_text.emit(txt)

    def run(self):
        pytube_request.default_range_size = 1048576
        self.update_status_text('Fetching Data')
        video_object = YouTube(self.card.url, on_progress_callback=self.progress_func)
        video = video_object.streams.get_by_itag(self.card.itag)
        self.card.video = video
        self.filesize = video.filesize
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
            self.update_style_sheet("QProgressBar::chunk {background-color: red;}")
            pytube_request.default_range_size = 209715
        self.update_status_text(f'Downloading {video.type}')
        video.download(filename=title)
        self.update_value(100)
        self.update_status_text('Download Complete')
        self.window.downloading = False
        self.update_style_sheet("QProgressBar::chunk {background-color: blue;}")
        self.toggle_delete_button(False)
        self.window.queue_process()
