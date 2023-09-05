import os
from shutil import copyfileobj
import requests
import moviepy.editor as video_editor
from PyQt6 import QtCore
from PyQt6.QtGui import QPixmap
from DualDownloadThread import get_title
from pytube.__main__ import YouTube
from pytube.__main__ import request as pytube_request


class MusicDownloader(QtCore.QThread):
    def set_value(self, card):
        self.card = card

    def run(self):
        total_size = 0
        pytube_request.default_range_size = 209715
        total = len(self.card.videos)
        downloaded_file_list: list[str] = list()
        title = ""
        author = ""
        video = None
        audio = None
        while len(self.card.videos) != 0:
            self.card.title.setText('Loading...')
            url = self.card.videos.pop(0)
            video = YouTube(url, on_progress_callback=self.card.progress_func)

            # Determine best Audio
            audio = video.streams.filter(only_audio=True).get_audio_only()
            self.card.filesize = audio.filesize

            total_size += audio.filesize_mb
            self.card.title.setText(f'[{total - len(self.card.videos)}/{total}]    Downloading: {video.title} - {audio.filesize_mb} MB')
            self.card.thumbnail = QPixmap()
            self.card.thumbnail.loadFromData(requests.get(video.thumbnail_url.replace('hq720.jpg', 'maxresdefault.jpg'), stream=True).content)
            self.card.thumbnail_preview.setPixmap(self.card.thumbnail.scaledToHeight(73))
            if len(self.card.videos) == 0:
                title = video.title
                thumbnail = requests.get(video.thumbnail_url.replace('hq720.jpg', 'maxresdefault.jpg'), stream=True).raw
                f = open('thumbnail.jpg', 'wb')
                copyfileobj(thumbnail, f)
                f.close()

            path = audio.download()
            downloaded_file_list.append(path)
        self.card.title.setText('Mixing Audios')
        final_audios = []
        for audio_path in downloaded_file_list:
            final_audios.append(video_editor.AudioFileClip(audio_path))
        final_audio = video_editor.concatenate_audioclips(final_audios)
        title, extension = get_title(video, audio)
        path = f'{title}_edited.{extension}'
        final_audio.write_audiofile(path, logger=self.card.logger)

        if os.path.exists('./thumbnail.jpg'):
            os.remove('./thumbnail.jpg')
        for audio_path in downloaded_file_list:
            if os.path.exists(audio_path):
                os.remove(audio_path)
        self.card.title.setText(f'{title}\nDownload Complete\nTotal Size: {total_size} MB    Total Files: {total}')
