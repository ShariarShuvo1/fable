import os
import subprocess

import moviepy.editor as VideoEditor
from PyQt6 import QtCore
from proglog import proglog

from pytube.__main__ import YouTube


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
    return title, extension


def history_remover(name, extension):
    if os.path.exists(f'{name}.{extension}'):
        os.remove(f'{name}.{extension}')


class DualDownloadThread(QtCore.QThread):
    def set_values(self, card, window):
        self.window = window
        self.card = card
        self.window.downloading = True

    def run(self):
        self.card.status_label.setText('Fetching Data')
        video_object = YouTube(self.card.url, on_progress_callback=self.card.progress_func,
                               on_complete_callback=self.card.complete_func)
        self.video = video_object.streams.get_by_itag(self.card.itag)
        self.card.video = self.video
        video_title, video_extension = get_title(video_object, self.video)
        history_remover('video', video_extension)

        self.card.status_label.setText('Downloading Video')
        video_path = self.video.download()
        self.card.status_label.setText('Video Downloaded')
        os.rename(video_path, f'video.{video_extension}')

        self.card.progress_bar.setValue(0)
        self.card.progress_bar.setStyleSheet("QProgressBar::chunk {background-color: red;}")

        audio_list = video_object.streams.filter(only_audio=True)
        audio = audio_list.first()
        x = 0
        for music in audio_list:
            if music.mime_type == "audio/mp4":
                rate = int(music.abr.split('kbps')[0])
                if rate >= x:
                    x = rate
                    audio = music
        self.card.video = audio
        audio_title, audio_extension = get_title(video_object, audio)
        history_remover('audio', audio_extension)

        self.card.status_label.setText('Downloading Audio')
        audio_path = audio.download()
        self.card.status_label.setText('Audio Downloaded')
        os.rename(audio_path, f'audio.{audio_extension}')

        video = VideoEditor.VideoFileClip(f'video.{video_extension}')

        audio = VideoEditor.AudioFileClip(f'audio.{audio_extension}')

        final = video.set_audio(audio)
        path = f'{video_title}_edited.{video_extension}'

        self.card.progress_bar.setValue(0)
        self.card.progress_bar.setStyleSheet("QProgressBar::chunk {background-color: yellow;")

        final.write_videofile(path, logger=self.card.logger)

        history_remover('video', video_extension)
        history_remover('audio', audio_extension)
        self.window.downloading = False
        self.window.queue_process()
