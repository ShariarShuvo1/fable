import os
import multiprocessing
import moviepy.editor as video_editor
from re import sub as remove_space

from PyQt6.QtCore import pyqtSignal
from proglog import ProgressBarLogger

from pytube.__main__ import request as pytube_request
from pytube.__main__ import YouTube
from PyQt6 import QtCore


class MyBarLogger(ProgressBarLogger):

    def __init__(self, thread):
        super().__init__()
        self.thread = thread
        self.first_step_done = False

    def callback(self, **changes):
        for (parameter, value) in changes.items():
            x = 'Parameter %s is now %s' % (parameter, value)
            if 'Writing video' in x:
                self.thread.update_style_sheet("QProgressBar::chunk {background-color: #34ebe8;}")
                self.thread.update_status_text('Exporting Video')
                self.first_step_done = True

    def bars_callback(self, bar, attr, value, old_value=None):
        percentage = (value / self.bars[bar]['total']) * 100
        self.thread.update_value(int(percentage))


def get_title(video_object, video):
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
        title = t + fps + res + p
    else:
        if extension == 'mp4':
            extension = 'mp3'
        abr = '_' + video.abr
        title = t + abr + p
    title = remove_space(' +', ' ', title)
    return title, extension


def history_remover(name, extension):
    if os.path.exists(f'{name}.{extension}'):
        os.remove(f'{name}.{extension}')


class DualDownloadThread(QtCore.QThread):
    progress_value = pyqtSignal(int)
    status_text = pyqtSignal(str)
    style_sheet = pyqtSignal(str)
    do_toggle = pyqtSignal(bool)

    def set_values(self, card, window):
        self.window = window
        self.card = card
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
        self.logger = MyBarLogger(self)
        pytube_request.default_range_size = 1048576
        thread = multiprocessing.cpu_count()
        self.update_status_text('Fetching Data')
        video_object = YouTube(self.card.url, on_progress_callback=self.progress_func)
        video_youtube = video_object.streams.get_by_itag(self.card.itag)
        self.card.video = video_youtube
        video_title, video_extension = get_title(video_object, video_youtube)
        history_remover('video', video_extension)

        self.update_status_text('Downloading Video')
        self.filesize = video_youtube.filesize
        video_path = video_youtube.download()
        self.update_status_text('Video Downloaded')
        os.rename(video_path, f'video.{video_extension}')

        audio = video_object.streams.filter(only_audio=True).get_audio_only()
        self.filesize = audio.filesize
        pytube_request.default_range_size = 209715
        self.card.video = audio
        audio_title, audio_extension = get_title(video_object, audio)
        history_remover('audio', audio_extension)

        self.update_status_text('Downloading Audio')
        self.update_style_sheet("QProgressBar::chunk {background-color: red;}")
        audio_path = audio.download()
        self.update_status_text('Audio Downloaded')
        os.rename(audio_path, f'audio.{audio_extension}')

        video = video_editor.VideoFileClip(f'video.{video_extension}')

        audio = video_editor.AudioFileClip(f'audio.{audio_extension}')

        final = video.set_audio(audio)
        path = f'{video_title}_edited.{video_extension}'
        self.update_status_text('Mixing Files')
        self.update_value(100)
        self.update_style_sheet("QProgressBar::chunk {background-color: #FFFF00;}")
        try:
            final.write_videofile(path, logger=self.card.logger, threads=thread, codec='h264_nvenc')
        except:
            final.write_videofile(path, logger=self.logger)
        history_remover('video', video_extension)
        history_remover('audio', audio_extension)
        self.window.downloading = False
        self.update_style_sheet("QProgressBar::chunk {background-color: blue;}")
        self.toggle_delete_button(False)
        self.update_status_text('Download Complete')
        self.window.queue_process()
