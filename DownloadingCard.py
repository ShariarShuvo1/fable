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
        self.downloader_thread.progress_value.connect(self.progress_changed)
        self.downloader_thread.title_value.connect(self.update_title)
        self.downloader_thread.do_toggle.connect(self.toggle_delete_button_disabled)
        self.downloader_thread.thumbnail_value.connect(self.load_thumbnail)
        self.downloader_thread.stylesheet.connect(self.update_progress_bar_stylesheet)
        self.downloader_thread.set_value(self)
        self.downloader_thread.start()

    def delete_clicked(self):
        self.window.delete_card(self)

    def progress_changed(self, value):
        self.progress_bar.setValue(value)

    def update_title(self, txt):
        self.title.setText(txt)

    def toggle_delete_button_disabled(self, do_toggle):
        self.delete_button.setDisabled(do_toggle)

    def load_thumbnail(self, thumbnail):
        self.thumbnail_preview.setPixmap(thumbnail.scaledToHeight(73))

    def update_progress_bar_stylesheet(self, stylesheet):
        self.progress_bar.setStyleSheet(stylesheet)
