import os
import shutil

import requests
import eyed3
import moviepy.editor as video_editor
from PyQt6 import QtCore
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QPixmap
from DualDownloadThread import get_title
from pytube.__main__ import YouTube
from pytube.__main__ import request as pytube_request
from proglog import ProgressBarLogger


class MyBarLogger(ProgressBarLogger):

    def __init__(self, thread):
        super().__init__()
        self.thread = thread
        self.first_step_done = False

    def callback(self, **changes):
        pass

    def bars_callback(self, bar, attr, value, old_value=None):
        percentage = (value / self.bars[bar]['total']) * 100
        self.thread.update_value(int(percentage))


class MusicDownloader(QtCore.QThread):
    progress_value = pyqtSignal(int)
    title_value = pyqtSignal(str)
    do_toggle = pyqtSignal(bool)
    thumbnail_value = pyqtSignal(QPixmap)
    stylesheet = pyqtSignal(str)

    def set_value(self, card):
        self.card = card

    def update_title(self, txt):
        self.title_value.emit(txt)

    def update_stylesheet(self, style):
        self.stylesheet.emit(style)

    def update_thumbnail(self, thumbnail):
        self.thumbnail_value.emit(thumbnail)

    def toggle_disable_button(self, toggle):
        self.do_toggle.emit(toggle)

    def update_value(self, value):
        self.progress_value.emit(value)

    def progress_func(self, video, file_path, remaining):
        finished = int(((self.filesize - remaining) / self.filesize) * 100)
        self.update_value(finished)

    def run(self):
        try:
            self.logger = MyBarLogger(self)
            total_size = 0
            pytube_request.default_range_size = 209715
            total = len(self.card.videos)
            downloaded_file_list: list[str] = list()
            video = None
            audio = None
            self.picture = None
            r = 5
            g = 250
            b = 5
            description = ""
            while len(self.card.videos) != 0:
                self.update_stylesheet(f"QProgressBar::chunk {'{'}background-color: rgb({r}, {g}, {b});{'}'}")
                b = b + 30
                if b >= 255:
                    b = 255
                    g -= 30
                    if g <= 5:
                        r += 30
                        if r >= 255:
                            r = 5
                            g = 250
                            b = 5
                self.update_value(0)
                self.update_title('Loading...')
                url = self.card.videos.pop(0)
                video = YouTube(url, on_progress_callback=self.progress_func)
                description += f'{video.title}\n'

                # Determine best Audio
                audio = video.streams.filter(only_audio=True).get_audio_only()
                self.filesize = audio.filesize

                total_size += audio.filesize_mb
                self.update_title(f'[{total - len(self.card.videos)}/{total}]    Downloading: {video.title} - {audio.filesize_mb} MB')
                self.thumbnail = QPixmap()
                self.thumbnail_url = video.thumbnail_url.replace('hq720.jpg', 'maxresdefault.jpg')
                self.picture = requests.get(self.thumbnail_url, stream=True)
                self.thumbnail.loadFromData(self.picture.content)
                self.update_thumbnail(self.thumbnail)

                path = audio.download()
                self.update_value(100)
                self.update_stylesheet("QProgressBar::chunk {background-color: red;}")
                downloaded_file_list.append(path)
            self.update_title(f'{video.title}\nExporting Audio:')
            self.update_value(0)
            self.update_stylesheet("QProgressBar::chunk {background-color: #faea05;}")
            final_audios = []
            for audio_path in downloaded_file_list:
                final_audios.append(video_editor.AudioFileClip(audio_path))
            final_audio = video_editor.concatenate_audioclips(final_audios)
            title, extension = get_title(video, audio)
            path = f'{title}_edited.{extension}'
            final_audio.write_audiofile(path, logger=self.logger)

            for audio_path in downloaded_file_list:
                if os.path.exists(audio_path):
                    os.remove(audio_path)
            self.update_title(f'{video.title}\nTotal Size: {total_size} MB    Total Files: {total}\nDownload Complete')

            f = open(f'{title}_thumb.jpg', 'wb')
            res = requests.get(self.thumbnail_url, stream=True)
            shutil.copyfileobj(res.raw, f)
            f.close()

            audio_file = eyed3.load(path)
            audio_file.tag.title = f'{video.title}_title'
            audio_file.tag.artist = f'{video.author}'
            audio_file.tag.images.set(3, open(f'{title}_thumb.jpg', 'rb').read(), 'image/jpeg')
            audio_file.tag.save()

            if os.path.exists(f'{title}_thumb.jpg'):
                os.remove(f'{title}_thumb.jpg')

            self.toggle_disable_button(False)
            self.update_value(100)
            self.update_stylesheet("QProgressBar::chunk {background-color: blue;}")
        except:
            video = YouTube(self.card.videos[0])
            print(f"Invalid Video - {video.title}")
