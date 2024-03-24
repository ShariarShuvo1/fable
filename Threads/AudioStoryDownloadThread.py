import yt_dlp
from PyQt6.QtCore import QThread, pyqtSignal
from proglog import ProgressBarLogger

from Entity.File import File


class AudioStoryDownloaderThread(QThread):
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
                'no_warnings': True,
                "quiet": True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if self.file.file_type == "audio":
                    self.status.emit("Downloading\nAudio")
                else:
                    self.status.emit("Downloading\nVideo")
                ydl.download([self.video_url])
            self.status_updated.emit("Downloaded")
        except Exception as e:
            print(f"Error: {str(e)}")

    def progress_hook(self, d):
        if self._paused:
            self.pause_requested.emit()
            self.wait_resume()

        if d['status'] == 'downloading':
            percent = d['_percent_str']
            percent = d['_percent_str']
            if percent.startswith("\x1b[0;94m100"):
                percent = "100.0%"
            else:
                percent = percent.split(" ")
                if len(percent) > 1:
                    if len(percent) > 2:
                        percent = percent[-1]
                    else:
                        percent = percent[1].split('%')[0]
                else:
                    percent = percent[0]
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
    def __init__(self, thread: AudioStoryDownloaderThread, **kwargs):
        super().__init__(**kwargs)
        self.thread: AudioStoryDownloaderThread = thread

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
