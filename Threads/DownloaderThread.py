import os

import yt_dlp
from PyQt6.QtCore import QThread, pyqtSignal
from moviepy.editor import VideoFileClip, AudioFileClip
from proglog import ProgressBarLogger

from Entity.File import File


class DownloaderThread(QThread):
    progress_updated = pyqtSignal(int)
    status = pyqtSignal(str)
    status_updated = pyqtSignal(str)
    speed_updated = pyqtSignal(int)
    eta_updated = pyqtSignal(int)
    downloaded_size_updated = pyqtSignal(list)
    pause_requested = pyqtSignal()
    resume_requested = pyqtSignal()

    def __init__(self, file: File, card, parent=None):
        super().__init__(parent)
        self.card = card
        self.file = file
        self.video_url = file.webpage_url
        self.output_path = file.output_path
        self.format_id = file.format_id
        self._paused = False

    def run(self):
        try:
            ydl_opts = {
                'outtmpl': f'{self.output_path}/{self.file.title}',
                'format': self.format_id,
                'progress_hooks': [self.progress_hook],
            }
            self.card.pause_button.setDisabled(True)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if self.file.file_type == "audio":
                    self.status.emit("Downloading\nAudio")
                else:
                    self.status.emit("Downloading\nVideo")
                ydl.download([self.video_url])
            self.card.pause_button.setDisabled(True)

            if self.file.file_type == "video" and self.file.add_music:
                self.progress_updated.emit(0)
                video_file = f"{self.output_path}/{self.file.title}"
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': self.file.output_path + "/" + f'%(title)s{self.file.format_id}.%(ext)s',
                    'progress_hooks': [self.progress_hook],
                }
                self.status.emit("Getting\nAudio Info")
                ydl = yt_dlp.YoutubeDL(ydl_opts)
                info = ydl.extract_info(self.video_url, download=False)
                audio_file = ydl.prepare_filename(info)
                audio_file = audio_file.replace('\\', '/')

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    self.status.emit("Downloading\nAudio")
                    ydl.download([self.video_url])

                self.card.pause_button.setDisabled(True)
                self.file.title = f"{
                    self.file.title[:self.file.title.rfind('.')]}_with_music.mp4"
                output_file = f"{self.output_path}/{self.file.title}"
                self.downloaded_size_updated.emit(["", ""])

                self.card.audio_path = audio_file
                self.card.video_path = video_file

                audio = AudioFileClip(audio_file)
                video = VideoFileClip(video_file)
                logger = MyBarLogger(self)

                audio = audio.set_duration(video.duration)
                video = video.set_audio(audio)
                video.write_videofile(
                    output_file, codec='libx264', audio_codec='aac', logger=logger)
                if os.path.exists(video_file):
                    os.remove(video_file)
                if os.path.exists(audio_file):
                    os.remove(audio_file)
            self.status_updated.emit("Downloaded")
        except Exception as e:
            print(f"Error: {str(e)}")

    def progress_hook(self, d):
        self.card.pause_button.setDisabled(False)
        if self._paused:
            self.pause_requested.emit()
            self.wait_resume()

        if d['status'] == 'downloading':
            percent = d['_percent_str']
            percent = int(percent.split('.')[0])
            self.progress_updated.emit(percent)

            eta = d.get('eta')
            if eta is not None:
                self.eta_updated.emit(eta)

            speed = d.get('speed')
            if speed is not None:
                self.speed_updated.emit(int(speed))

            total_bytes = d.get("total_bytes")
            downloaded_byte = d.get('downloaded_bytes')
            if total_bytes is not None:
                self.downloaded_size_updated.emit(
                    [downloaded_byte, total_bytes])

    def pause_download(self):
        self._paused = True

    def resume_download(self):
        self._paused = False

    def wait_resume(self):
        while self._paused:
            self.msleep(100)


class MyBarLogger(ProgressBarLogger):

    def __init__(self, thread: DownloaderThread, **kwargs):
        super().__init__(**kwargs)
        self.thread: DownloaderThread = thread

    def callback(self, **changes):
        pass

    def bars_callback(self, bar, attr, value, old_value=None):
        percentage = (value / self.bars[bar]['total']) * 100
        if old_value is None:
            self.thread.progress_updated.emit(0)
        else:
            self.thread.progress_updated.emit(int(percentage))
        if bar == "chunk":
            self.thread.status.emit("Preparing\nMerge")
        else:
            self.thread.status.emit("Merging")
