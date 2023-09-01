import os
import multiprocessing
import moviepy.editor as video_editor
from re import sub as remove_space
from pytube.__main__ import YouTube
from PyQt6 import QtCore


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
    def set_values(self, card, window):
        self.window = window
        self.card = card
        self.window.downloading = True

    def run(self):
        thread = multiprocessing.cpu_count()
        self.card.status_label.setText('Fetching Data')
        video_object = YouTube(self.card.url, on_progress_callback=self.card.progress_func)
        video_youtube = video_object.streams.get_by_itag(self.card.itag)
        self.card.video = video_youtube
        video_title, video_extension = get_title(video_object, video_youtube)
        history_remover('video', video_extension)

        self.card.status_label.setText('Downloading Video')
        video_path = video_youtube.download()
        self.card.status_label.setText('Video Downloaded')
        os.rename(video_path, f'video.{video_extension}')
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

        video = video_editor.VideoFileClip(f'video.{video_extension}')

        audio = video_editor.AudioFileClip(f'audio.{audio_extension}')

        final = video.set_audio(audio)
        path = f'{video_title}_edited.{video_extension}'
        self.card.progress_bar.setStyleSheet("QProgressBar::chunk {background-color: #FFFF00;}")
        self.card.status_label.setText('Mixing Files')
        try:
            final.write_videofile(path, logger=self.card.logger, threads= thread, codec='h264_nvenc')
        except:
            final.write_videofile(path, logger=self.card.logger)
        history_remover('video', video_extension)
        history_remover('audio', audio_extension)
        self.window.downloading = False
        self.card.progress_bar.setStyleSheet("QProgressBar::chunk {background-color: blue;}")
        self.card.delete_button.setDisabled(False)
        self.card.status_label.setText('Download Complete')
        self.window.queue_process()
