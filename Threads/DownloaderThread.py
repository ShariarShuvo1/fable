import yt_dlp
from PyQt6.QtCore import QThread, pyqtSignal

from Entity.File import File


class DownloaderThread(QThread):
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)

    def __init__(self, file: File, parent=None):
        super().__init__(parent)
        self.video_url = file.webpage_url
        self.output_path = file.output_path
        self.format_id = file.format_id

    def run(self):
        try:
            ydl_opts = {
                'outtmpl': f'{self.output_path}/%(title)s.%(ext)s',
                'format': self.format_id,
                'progress_hooks': [self.progress_hook],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.video_url])
            self.status_updated.emit("Downloaded")
        except Exception as e:
            print(f"Error: {str(e)}")

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = d['_percent_str']
            percent = int(percent.split('.')[0])
            self.progress_updated.emit(percent)