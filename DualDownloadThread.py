import os
import subprocess

import moviepy.editor as VideoEditor
from PyQt6 import QtCore
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
        title = t + fps + res + p + f'.{extension}'
    else:
        if extension == 'mp4':
            extension = 'mp3'
        abr = '_' + video.abr
        title = t + abr + p + f'.{extension}'
    return title, extension


class DualDownloadThread(QtCore.QThread):
    def set_values(self, card, window):
        self.window = window
        self.card = card
        self.window.downloading = True

    def run(self):
        video_object = YouTube(self.card.url, on_progress_callback=self.card.progress_func, on_complete_callback=self.card.complete_func)
        video = video_object.streams.get_by_itag(self.card.itag)
        self.video = video
        video_title, video_extension = get_title(video_object, video)

        self.card.progress_bar.resetFormat()

        video_path = video.download()
        if 'mp4' in video_extension:
            os.rename(video_path, 'video.mp4')
        else:
            os.rename(video_path, 'video.webm')

        self.card.progress_bar.setValue(0)
        self.card.progress_bar.resetFormat()
        self.card.progress_bar.setStyleSheet("QProgressBar::chunk {background-color: red;}")

        audio_list = video_object.streams.filter(only_audio=True)
        audio = audio_list.first()
        x = 0
        for music in audio_list:
            if music.mime_type == "audio/mp4":
                rate = int(music.abr.split('kbps')[0])
                if rate > x:
                    x = rate
                    audio = music
        self.video = audio

        audio_title, audio_extension = get_title(video_object, audio)

        audio_path = audio.download()
        if 'mp3' in audio_extension:
            os.rename(audio_path, 'audio.mp3')
        else:
            os.rename(audio_path, 'audio.webm')

        try:
            subprocess.check_output('nvidia-smi')
            nvidia_available = True
        except Exception:
            nvidia_available = False
        if 'mp4' in video_extension:
            video = VideoEditor.VideoFileClip('video.mp4')
        else:
            video = VideoEditor.VideoFileClip('video.webm')

        if 'mp3' in audio_extension:
            audio = VideoEditor.AudioFileClip('audio.mp3')
        else:
            audio = VideoEditor.AudioFileClip('audio.webm')

        final = video.set_audio(audio)
        if 'mp4' in self.card.video_path:
            path = f'{video_title}_edited.mp4'
        else:
            path = f'{video_title}_edited.webm'

        if nvidia_available:
            final.write_videofile(path, codec="h264_nvenc", threads=8)
        else:
            final.write_videofile(path)

        if os.path.exists('video.mp4'):
            os.remove('video.mp4')
        if os.path.exists('video.webm'):
            os.remove('video.webm')
        if os.path.exists('audio.mp3'):
            os.remove('audio.mp3')
        if os.path.exists('audio.webm'):
            os.remove('audio.webm')
        self.card.download_complete = True
        self.window.downloading = False
