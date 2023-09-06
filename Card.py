from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar
from proglog import ProgressBarLogger

from DualDownloadThread import DualDownloadThread
from VideoDownloadThread import VideoDownloadThread


class Card:

    def __init__(self, ui, url, video):
        self.dual_download_thread = None
        self.ui = ui
        self.url = url
        self.video = video
        self.itag = self.video.itag
        self.is_progressive = self.video.is_progressive
        self.video_type = self.video.type
        self.card = QVBoxLayout()
        self.download_complete = False
        self.downloading = False
        self.current_text = ""
        self.video_title = ""
        self.video_download_thread = None
        self.audio_path = ""
        self.video_path = ""
        self.path = ""
        self.source = None
        self.download_thread = None
        self.resolution_dict = dict()
        self.video_info_thread = None
        self.streams = None
        w = 1200 // 100
        h = 900 // 100
        font = QFont()
        font.setBold(True)
        font.setPointSize(16)

        # Row 3 Media Info
        self.media_row = QHBoxLayout()
        self.thumbnail_preview = QLabel()
        self.thumbnail_preview.setPixmap(self.ui.thumbnail.scaledToHeight(68))
        self.thumbnail_preview.setMaximumWidth(120)

        self.description_preview = QLabel()
        temp_font = font
        temp_font.setPointSize(11)
        temp_font.setBold(False)
        self.description_preview.setFont(temp_font)
        if 'video' in self.video.type:
            string_to_display = f'{self.ui.video.title}\nQuality: {self.video.resolution}\nFPS: {self.video.fps}\nSize: {self.video.filesize_mb}MB   file-type: {self.video.mime_type.split("/")[1]}'
        else:
            string_to_display = f'{self.ui.video.title}\nQuality: {self.video.abr}\nType: Audio\nSize: {self.video.filesize_mb}MB   file-type: {self.video.mime_type.split("/")[1]}'
        self.description_preview.setText(string_to_display)

        self.media_row.addWidget(self.thumbnail_preview)
        self.media_row.addWidget(self.description_preview)

        # Row 4 Downloading Status
        self.progress_bar_row = QHBoxLayout()

        self.status_label = QLabel("Queued")

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(20)
        self.update_style_sheet("QProgressBar::chunk {background-color: green;}")

        self.delete_button = QPushButton()
        self.delete_button.setIcon(QIcon("./assets/icons/delete.png"))
        self.delete_button.setFixedWidth(50)
        self.delete_button.setFixedHeight(35)
        self.delete_button.setStyleSheet("QPushButton::hover{background-color: red;}")
        self.delete_button.clicked.connect(self.initiate_delete_card)

        self.progress_bar_row.addWidget(self.status_label)
        self.progress_bar_row.addWidget(self.progress_bar)
        self.progress_bar_row.addWidget(self.delete_button)

        # Row 5 empty line

        self.empty_line_row = QVBoxLayout()

        self.empty_line = QLabel()
        self.empty_line.setMaximumHeight(2)
        self.empty_line.setStyleSheet("background-color: red")

        self.empty_line_row.addWidget(self.empty_line)

        self.card.addLayout(self.media_row)
        self.card.addLayout(self.progress_bar_row)
        self.card.addLayout(self.empty_line_row)

    def progress_changed(self, value):
        self.progress_bar.setValue(value)

    def initiate_delete_card(self):
        self.ui.delete_card(self.card, self)

    def change_status_label(self, txt):
        self.status_label.setText(txt)

    def update_style_sheet(self, style_sheet):
        self.progress_bar.setStyleSheet(style_sheet)

    def toggle_delete_button_disable(self, do_toggle):
        self.delete_button.setDisabled(do_toggle)

    def download(self):
        self.description_preview.setEnabled(True)
        self.status_label.setText('Downloading')
        if self.is_progressive or self.video_type in 'audio':
            self.video_download_thread = VideoDownloadThread()
            self.video_download_thread.progress_value.connect(self.progress_changed)
            self.video_download_thread.status_text.connect(self.change_status_label)
            self.video_download_thread.style_sheet.connect(self.update_style_sheet)
            self.video_download_thread.do_toggle.connect(self.toggle_delete_button_disable)
            self.video_download_thread.set_values(self)
            self.video_download_thread.start()
        else:
            self.dual_download_thread = DualDownloadThread()
            self.dual_download_thread.progress_value.connect(self.progress_changed)
            self.dual_download_thread.status_text.connect(self.change_status_label)
            self.dual_download_thread.style_sheet.connect(self.update_style_sheet)
            self.dual_download_thread.do_toggle.connect(self.toggle_delete_button_disable)
            self.dual_download_thread.set_values(self)
            self.dual_download_thread.start()
