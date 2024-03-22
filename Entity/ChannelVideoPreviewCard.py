from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon, QCursor
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton

from Entity.PlaylistCard import open_url, format_duration
from Entity.Video import Video
from Entity.VideoViewer import VideoViewer
from Styles.CarouselStyle import CAROUSEL_THUMBNAIL_STYLESHEET
from Styles.DownloadListStyle import VIDEO_TITLE_STYLESHEET, VIDEO_TITLE_BUTTON_STYLESHEET
from Styles.PlaylistCardStyle import (
    PLAYLIST_CARD_STYLESHEET, ADD_BUTTON_STYLESHEET)


class ChannelVideoPreviewCard:
    def __init__(self, video: Video, main_window, number):
        self.main_window = main_window
        self.video: Video = video
        self.playlist_box: QWidget = QWidget()
        self.playlist_box.setMinimumWidth(480)
        self.playlist_box.setStyleSheet(PLAYLIST_CARD_STYLESHEET)

        self.story_number_label: QLabel = QLabel(
            f"{number}")
        self.story_number_label.setStyleSheet(VIDEO_TITLE_STYLESHEET)

        self.thumbnail_label: QLabel = QLabel()
        self.thumbnail_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.thumbnail_label.setToolTip("Click for preview")
        self.thumbnail_label.setWordWrap(True)
        self.thumbnail_label.setStyleSheet(VIDEO_TITLE_STYLESHEET)
        self.thumbnail_label.setFixedWidth(90)
        self.thumbnail_label.setFixedHeight(60)
        self.thumbnail_label.setStyleSheet(CAROUSEL_THUMBNAIL_STYLESHEET)
        self.thumbnail_label.mousePressEvent = self.on_thumbnail_click

        self.pixmap = QPixmap()
        self.pixmap.loadFromData(video.thumbnail.content)
        self.pixmap = self.pixmap.scaled(
            90, 60, Qt.AspectRatioMode.KeepAspectRatioByExpanding)
        self.thumbnail_label.setPixmap(self.pixmap)

        self.title_label: QPushButton = QPushButton(video.title)
        self.title_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.title_label.setToolTip(video.title)
        self.title_label.setStyleSheet(VIDEO_TITLE_BUTTON_STYLESHEET)
        self.title_label.clicked.connect(
            lambda checked: open_url(video.video_url))

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

        self.add_button: QPushButton = QPushButton()
        self.add_button.setToolTip("Add to Queue")
        self.add_button.setFixedHeight(65)
        self.add_button.setFixedWidth(65)
        self.add_button.clicked.connect(self.add_video)
        self.add_button.setIcon(QIcon('./Assets/Icons/search-add-icon.png'))
        self.add_button.setIconSize(QSize(65, 65))
        self.add_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.add_button.setStyleSheet(ADD_BUTTON_STYLESHEET)

        self.direct_download_button: QPushButton = QPushButton()
        self.direct_download_button.setToolTip(
            "Direct Download single Audio Story")
        self.direct_download_button.setIcon(
            QIcon("./Assets/Icons/search-single-download-icon.png"))
        self.direct_download_button.setIconSize(QSize(65, 65))
        self.direct_download_button.setCursor(
            Qt.CursorShape.PointingHandCursor)
        self.direct_download_button.setFixedSize(65, 65)
        self.direct_download_button.setStyleSheet(
            ADD_BUTTON_STYLESHEET)
        self.direct_download_button.clicked.connect(
            lambda checked: self.audio_story_download_direct())

        self.main_layout: QHBoxLayout = QHBoxLayout()
        self.main_layout.setContentsMargins(3, 3, 3, 3)

        self.top_right_layout: QVBoxLayout = QVBoxLayout()
        self.top_right_layout.addWidget(self.title_label)
        self.top_right_layout.addWidget(self.channel_label)
        self.top_right_layout.addWidget(self.duration_label)

        self.main_layout.addWidget(self.story_number_label)
        self.main_layout.addWidget(self.thumbnail_label)
        self.main_layout.addLayout(self.top_right_layout)

        self.main_layout.addStretch()
        self.main_layout.addWidget(self.add_button)
        self.main_layout.addWidget(self.direct_download_button)

        self.playlist_box.setLayout(self.main_layout)

    def add_video(self):
        self.playlist_box.setStyleSheet(PLAYLIST_CARD_STYLESHEET)
        self.main_window.audio_story_video_info_found([self.video])

    def audio_story_download_direct(self):
        self.main_window.audio_story_download_clicked(
            True, self.video.video_url)

    def on_thumbnail_click(self, event):
        viewer = VideoViewer(self.video)
        viewer.exec()
