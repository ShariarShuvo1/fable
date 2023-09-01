from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar
from proglog import ProgressBarLogger


class MyBarLogger(ProgressBarLogger):

    def __init__(self, progress_bar: QProgressBar, label: QLabel):
        super().__init__()
        self.progress_bar: QProgressBar = progress_bar
        self.label: QLabel = label
        self.first_step_done = False

    def callback(self, **changes):
        if not self.first_step_done and self.label.text() == 'Audio Downloaded':
            self.label.setText('Mixing files')
        for (parameter, value) in changes.items():
            x = 'Parameter %s is now %s' % (parameter, value)
            if 'Writing video' in x:
                self.label.setText('Exporting Video')
                self.first_step_done = True

    def bars_callback(self, bar, attr, value, old_value=None):
        percentage = (value / self.bars[bar]['total']) * 100
        self.progress_bar.setValue(int(percentage))


class Card:

    def __init__(self, ui, url, video):
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
        self.progress_bar.setStyleSheet("QProgressBar::chunk {background-color: green;}")

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

        self.logger = MyBarLogger(self.progress_bar, self.status_label)

    def progress_func(self, video, file_path, remaining):
        finished = int(((self.video.filesize - remaining) / self.video.filesize) * 100)
        self.progress_bar.setValue(finished)

    def initiate_delete_card(self):
        self.ui.delete_card(self.card, self)
