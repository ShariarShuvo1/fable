import math
import webbrowser

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon, QCursor
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QComboBox

from Entity.Video import Video
from Functions.convertBitsToReadableString import convert_bits_to_readable_string
from Styles.CarouselStyle import CAROUSEL_THUMBNAIL_STYLESHEET, RESOLUTION_COMBOBOX_STYLESHEET
from Styles.DownloadListStyle import VIDEO_TITLE_STYLESHEET, VIDEO_TITLE_BUTTON_STYLESHEET
from Styles.PlaylistCardStyle import (PLAYLIST_CARD_STYLESHEET, REMOVE_BUTTON_STYLESHEET, ADD_BUTTON_STYLESHEET,
                                      DOWNLOAD_BUTTON_STYLESHEET, PLAYLIST_CARD_DISABLED_STYLESHEET)


def format_duration(duration):
    hours, remainder = divmod(duration, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"


def open_url(url):
    webbrowser.open(url)


class PlaylistCard:
    def __init__(self, video: Video, main_window):
        self.main_window = main_window
        self.video: Video = video
        self.playlist_box: QWidget = QWidget()
        self.playlist_box.setMinimumWidth(480)
        self.playlist_box.setStyleSheet(PLAYLIST_CARD_STYLESHEET)
        # self.playlist_box.setFixedHeight(DOWNLOAD_BOX_HEIGHT)

        self.thumbnail_label: QLabel = QLabel()
        self.thumbnail_label.setStyleSheet(VIDEO_TITLE_STYLESHEET)
        self.thumbnail_label.setFixedHeight(60)
        self.thumbnail_label.setFixedWidth(90)
        self.thumbnail_label.setStyleSheet(CAROUSEL_THUMBNAIL_STYLESHEET)

        self.pixmap = QPixmap()
        self.pixmap.loadFromData(video.thumbnail.content)
        self.pixmap = self.pixmap.scaled(
            90, 60, Qt.AspectRatioMode.KeepAspectRatioByExpanding)
        self.thumbnail_label.setPixmap(self.pixmap)

        self.title_label: QPushButton = QPushButton(f"{video.title}")
        self.title_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.title_label.setToolTip(video.title)
        self.title_label.setStyleSheet(VIDEO_TITLE_BUTTON_STYLESHEET)
        self.title_label.clicked.connect(
            lambda: open_url(video.video_url))

        self.channel_label: QPushButton = QPushButton(
            f"Channel: {video.uploader}")
        self.channel_label.setCursor(
            QCursor(Qt.CursorShape.PointingHandCursor))
        self.channel_label.setToolTip(video.uploader)
        self.channel_label.setStyleSheet(VIDEO_TITLE_BUTTON_STYLESHEET)
        self.channel_label.clicked.connect(
            lambda: open_url(video.channel_url))

        self.duration_label: QLabel = QLabel(
            f"Duration: {format_duration(video.duration)}")
        self.duration_label.setStyleSheet(VIDEO_TITLE_STYLESHEET)

        self.remove_button: QPushButton = QPushButton()
        self.remove_button.setToolTip("Remove from Playlist")
        self.remove_button.setFixedHeight(100)
        self.remove_button.clicked.connect(self.remove_video)
        self.remove_button.setIcon(QIcon('./Assets/Icons/cancel-icon.png'))
        self.remove_button.setIconSize(QSize(20, 20))
        self.remove_button.setCursor(
            QCursor(Qt.CursorShape.PointingHandCursor))
        self.remove_button.setStyleSheet(REMOVE_BUTTON_STYLESHEET)

        self.add_button: QPushButton = QPushButton()
        self.add_button.setToolTip("Add to Playlist")
        self.add_button.setFixedHeight(100)
        self.add_button.clicked.connect(self.add_video)
        self.add_button.setIcon(QIcon('./Assets/Icons/add-icon.png'))
        self.add_button.setIconSize(QSize(20, 20))
        self.add_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.add_button.setStyleSheet(ADD_BUTTON_STYLESHEET)
        self.add_button.setHidden(True)

        self.main_layout: QHBoxLayout = QHBoxLayout()

        self.left_layout: QVBoxLayout = QVBoxLayout()

        self.top_layout: QHBoxLayout = QHBoxLayout()
        self.top_layout.addWidget(self.thumbnail_label)

        self.top_right_layout: QVBoxLayout = QVBoxLayout()
        self.top_right_layout.addWidget(self.title_label)
        self.top_right_layout.addWidget(self.channel_label)
        self.top_right_layout.addWidget(self.duration_label)

        self.top_layout.addLayout(self.top_right_layout)

        self.bottom_layout: QHBoxLayout = QHBoxLayout()

        self.resolution_combo = QComboBox()
        self.resolution_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.resolution_combo.setToolTip("Choose Quality to Download")
        self.resolution_combo.setMinimumHeight(40)
        self.resolution_combo.setStyleSheet(RESOLUTION_COMBOBOX_STYLESHEET)
        self.resolution_combo.setPlaceholderText("Choose Quality")

        for res in self.video.resolution_list:
            icon = QIcon("./Assets/Icons/audio.png") if res.file_type == "audio" else QIcon(
                "./Assets/Icons/video_no_audio.png") if res.file_type == "video" else QIcon(
                "./Assets/Icons/video.png")
            ext = f"[{res.ext}]"
            rate = f"{math.floor(
                res.abr)}kbps" if res.file_type == "audio" and res.abr else ""
            rate = f"[{math.floor(res.vbr)}kbps]" \
                if ((res.file_type == "video" or res.file_type == "mix")
                    and res.vbr) else "" if rate == "" else rate
            file_size = f"[{convert_bits_to_readable_string(
                res.filesize)}]" if res.filesize else ""
            fps = f"[{res.fps}fps]" if res.fps else ""
            height = f"{res.height}p " if res.height else ""
            if res.file_type == "audio":
                self.resolution_combo.addItem(
                    QIcon(icon),
                    f"{rate} {ext} {file_size}"
                )
            else:
                self.resolution_combo.addItem(
                    QIcon(icon),
                    f"{height}{ext} {fps} {rate} {file_size}"
                )
        self.bottom_layout.addWidget(self.resolution_combo)

        self.download_selected_res = QPushButton("Download")
        self.download_selected_res.setIcon(
            QIcon("./Assets/Icons/search-single-download-icon.png"))
        self.download_selected_res.setIconSize(QSize(20, 20))
        self.download_selected_res.setToolTip(
            "Download Selected Quality in standalone mode")
        (self.download_selected_res.clicked.connect(
            lambda checked,
            video=self.video,
            combo=self.resolution_combo: main_window.start_download(video, combo.currentIndex())
        )
        )

        self.download_selected_res.setStyleSheet(
            DOWNLOAD_BUTTON_STYLESHEET)
        self.download_selected_res.setMinimumHeight(40)
        self.download_selected_res.setCursor(Qt.CursorShape.PointingHandCursor)

        self.bottom_layout.addWidget(self.download_selected_res)

        self.left_layout.addLayout(self.top_layout)
        self.left_layout.addLayout(self.bottom_layout)

        self.main_layout.addLayout(self.left_layout)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.remove_button)
        self.main_layout.addWidget(self.add_button)

        self.playlist_box.setLayout(self.main_layout)

    def remove_video(self):
        self.playlist_box.setStyleSheet(PLAYLIST_CARD_DISABLED_STYLESHEET)
        self.title_label.setDisabled(True)
        self.channel_label.setDisabled(True)
        self.thumbnail_label.setDisabled(True)
        self.resolution_combo.setDisabled(True)
        self.download_selected_res.setDisabled(True)

        self.add_button.setHidden(False)
        self.remove_button.setHidden(True)

    def add_video(self):
        self.playlist_box.setStyleSheet(PLAYLIST_CARD_STYLESHEET)
        self.title_label.setDisabled(False)
        self.channel_label.setDisabled(False)
        self.thumbnail_label.setDisabled(False)
        self.resolution_combo.setDisabled(False)
        self.download_selected_res.setDisabled(False)

        self.remove_button.setHidden(False)
        self.add_button.setHidden(True)
