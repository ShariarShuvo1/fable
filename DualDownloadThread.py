import os
import subprocess

import moviepy.editor as VideoEditor
from PyQt6 import QtCore
from pytube.__main__ import YouTube


class DualDownloadThread(QtCore.QThread):
    def set_values(self, card, video, window):
        self.window = window
        self.card = card
        self.video = video
        self.audio_list = self.card.streams.filter(only_audio=True)
        self.audio = self.audio_list.first()
        x = 0
        for audio in self.audio_list:
            if audio.mime_type == "audio/mp4":
                rate = int(audio.abr.split('kbps')[0])
                if rate > x:
                    x = rate
                    self.audio = audio

    def run(self):
        self.card.download_button.setText('Downloading Video')
        self.card.video_path = self.video.download()
        if 'mp4' in self.card.video_path:
            os.rename(self.card.video_path, 'video.mp4')
        else:
            os.rename(self.card.video_path, 'video.webm')

        self.card.progress_bar.setValue(0)
        self.card.progress_bar.setStyleSheet("QProgressBar::chunk {background-color: red;}")
        self.card.download_button.setText('Downloading Audio')

        self.card.progress_bar.resetFormat()

        self.card.audio_path = self.audio.download()
        os.rename(self.card.audio_path, 'audio.mp3')
        self.card.download_button.setText('Downloaded')

        try:
            subprocess.check_output('nvidia-smi')
            nvidia_available = True
        except Exception:
            nvidia_available = False
        if 'mp4' in self.card.video_path:
            video = VideoEditor.VideoFileClip('video.mp4')
        else:
            video = VideoEditor.VideoFileClip('video.webm')
        audio = VideoEditor.AudioFileClip('audio.mp3')
        final = video.set_audio(audio)
        x = self.card.video_path.split('\\')[-1]
        x = x.split('.')[0]
        if 'mp4' in self.card.video_path:
            path = f'{x}_edited.mp4'
        else:
            path = f'{x}_edited.webm'
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
        if os.path.exists(self.card.video_path):
            os.remove(self.card.video_path)
        self.window.queue_process()
