from PyQt6.QtCore import QSize
from PyQt6.QtGui import QMovie, QIcon
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QPushButton
from MusicDownloader import MusicDownloader


class DownloadingCard:
    def __init__(self, videos, window):
        self.downloader_thread: MusicDownloader = None
        self.filesize: int = 100
        self.videos = videos
        self.window = window
        self.layout = QHBoxLayout()

        self.thumbnail_preview = QLabel()
        self.gif = QMovie('./assets/thumbnail_loading.gif')
        self.gif.setScaledSize(QSize(130, 73))
        self.thumbnail_preview.setMovie(self.gif)
        self.gif.start()
        self.layout.addWidget(self.thumbnail_preview)

        self.title = QLabel('')

        self.data_layout = QVBoxLayout()
        self.data_layout.addWidget(self.title)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(20)

        self.data_layout.addWidget(self.progress_bar)
        self.layout.addLayout(self.data_layout)

        self.delete_button = QPushButton()
        self.delete_button.setIcon(QIcon('./assets/icons/delete.png'))
        self.delete_button.setMaximumHeight(60)
        self.delete_button.setStyleSheet("QPushButton::hover{background-color: red;}")
        self.delete_button.clicked.connect(self.delete_clicked)
        self.delete_button.setDisabled(True)

        self.layout.addWidget(self.delete_button)

        self.downloader()

    def downloader(self):
        self.downloader_thread = MusicDownloader()
        self.downloader_thread.set_value(self)
        self.downloader_thread.start()

    def delete_clicked(self):
        pass

    def progress_func(self, video, file_path, remaining):
        finished = int(((self.filesize - remaining) / self.filesize) * 100)
        self.progress_bar.setValue(finished)
