import PyQt6
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QProgressBar, QPushButton, QWidget, QLayoutItem

from Entity.File import File
from Functions.convertBitsToReadableString import convert_bits_to_readable_string
from Functions.format_time import format_time
from Styles.DownloadListStyle import PROGRESS_BAR_STYLESHEET, TOOL_ICON_BUTTON_STYLESHEET, VIDEO_STATUS_STYLESHEET, \
    VIDEO_SIZE_STYLESHEET, VIDEO_TITLE_STYLESHEET
from Consts.Constanats import DOWNLOAD_BOX_HEIGHT
from Threads.DownloaderThread import DownloaderThread


def remove_inside_layout(layout):
    items = []
    for i in range(layout.count()):
        items.append(layout.itemAt(i))
    for item in items:
        layout.removeItem(item)


class Card:
    def __init__(self, video: File, currently_downloading_count: int):
        self.video: File = video
        self.thread = DownloaderThread(video, self)
        self.currently_downloading_count: int = currently_downloading_count

        self.icon_size: QSize = QSize(30, 30)

        self.both_row = QVBoxLayout()
        self.top_row = QHBoxLayout()
        self.bottom_row = QHBoxLayout()

        self.inside_layout = QHBoxLayout()
        self.inside_layout.setSpacing(0)

        self.remove_button = QPushButton()
        self.remove_button.setIcon(QIcon("./Assets/Icons/cancel-icon.png"))
        self.remove_button.setIconSize(self.icon_size)
        self.remove_button.setStyleSheet(TOOL_ICON_BUTTON_STYLESHEET)
        self.remove_button.setCursor(PyQt6.QtCore.Qt.CursorShape.PointingHandCursor)

        self.delete_button = QPushButton()
        self.delete_button.setIcon(QIcon("./Assets/Icons/delete-icon.png"))
        self.delete_button.setIconSize(self.icon_size)
        self.delete_button.setStyleSheet(TOOL_ICON_BUTTON_STYLESHEET)
        self.delete_button.setCursor(PyQt6.QtCore.Qt.CursorShape.PointingHandCursor)

        self.restart_button = QPushButton()
        self.restart_button.setIcon(QIcon("./Assets/Icons/restart-icon.png"))
        self.restart_button.setIconSize(self.icon_size)
        self.restart_button.setStyleSheet(TOOL_ICON_BUTTON_STYLESHEET)
        self.restart_button.setCursor(PyQt6.QtCore.Qt.CursorShape.PointingHandCursor)

        self.completed_button = QPushButton()
        self.completed_button.setIcon(
            QIcon("./Assets/Icons/completed-icon.png"))
        self.completed_button.setIconSize(self.icon_size)
        self.completed_button.setStyleSheet(TOOL_ICON_BUTTON_STYLESHEET)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(16)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setStyleSheet(PROGRESS_BAR_STYLESHEET)

        self.pause_button = QPushButton()
        self.pause_button.setIcon(QIcon("./Assets/Icons/pause-icon.png"))
        self.pause_button.setIconSize(self.icon_size)
        self.pause_button.setStyleSheet(TOOL_ICON_BUTTON_STYLESHEET)
        self.pause_button.setCursor(PyQt6.QtCore.Qt.CursorShape.PointingHandCursor)
        self.pause_button.clicked.connect(lambda: self.pause_download_video())

        self.play_button: QPushButton = QPushButton()
        self.play_button.setIcon(QIcon("./Assets/Icons/play-icon.png"))
        self.play_button.setIconSize(self.icon_size)
        self.play_button.setStyleSheet(TOOL_ICON_BUTTON_STYLESHEET)
        self.play_button.clicked.connect(lambda: self.start_download())
        self.play_button.setCursor(PyQt6.QtCore.Qt.CursorShape.PointingHandCursor)

        self.datetime_label = QLabel(
            self.video.added_date.strftime("%Y-%m-%d %H:%M:%S"))
        self.datetime_label.setStyleSheet(VIDEO_STATUS_STYLESHEET)
        self.datetime_label.setFixedWidth(110)
        self.datetime_label.setAlignment(PyQt6.QtCore.Qt.AlignmentFlag.AlignCenter)

        if self.video.file_size:
            self.file_size = convert_bits_to_readable_string(self.video.file_size)
        else:
            self.file_size = "N/A"

        self.file_size_label = QLabel(self.file_size)
        self.file_size_label.setStyleSheet(VIDEO_SIZE_STYLESHEET)
        self.file_size_label.setFixedWidth(130)
        self.file_size_label.setAlignment(PyQt6.QtCore.Qt.AlignmentFlag.AlignCenter)

        self.speed_label = QLabel()
        self.speed_label.setStyleSheet(VIDEO_STATUS_STYLESHEET)
        self.speed_label.setFixedWidth(70)
        self.speed_label.setAlignment(PyQt6.QtCore.Qt.AlignmentFlag.AlignCenter)

        self.eta_label = QLabel()
        self.eta_label.setFixedWidth(70)
        self.eta_label.setStyleSheet(VIDEO_STATUS_STYLESHEET)
        self.eta_label.setAlignment(PyQt6.QtCore.Qt.AlignmentFlag.AlignCenter)

        self.status_label: QLabel = QLabel(self.video.status)
        self.status_label.setFixedWidth(70)
        self.status_label.setStyleSheet(VIDEO_STATUS_STYLESHEET)
        self.status_label.setAlignment(PyQt6.QtCore.Qt.AlignmentFlag.AlignCenter)

        self.video_title: QLabel = QLabel(self.video.title)
        self.video_title.setStyleSheet(VIDEO_TITLE_STYLESHEET)

        self.inside_download_layout: QHBoxLayout = QHBoxLayout()
        self.inside_download_layout.setContentsMargins(0, 0, 0, 0)

        self.download_box: QWidget = QWidget()
        self.download_box.setFixedHeight(DOWNLOAD_BOX_HEIGHT)

        self.thread.progress_updated.connect(lambda progress=self.progress_bar: self.progress_bar.setValue(progress))
        self.thread.status_updated.connect(lambda status=video.status: self.download_finished(status))
        self.thread.status.connect(lambda status: self.update_status(status))
        self.thread.speed_updated.connect(lambda speed=self.speed_label: self.speed_label.setText(convert_bits_to_readable_string(speed) + "/s"))
        self.thread.eta_updated.connect(lambda eta=self.eta_label: self.eta_label.setText(format_time(eta)))
        self.thread.downloaded_size_updated.connect(lambda size: self.file_size_updated(size))

        self.construct_body()

    def update_status(self, status):
        if "Merg" in status:
            self.pause_button.setToolTip("You can not pause EXPORTING")
        self.status_label.setText(f"{status}")

    def file_size_updated(self, size: list):
        if size == ["", ""]:
            self.file_size_label.setText(f"N/A")
        else:
            downloaded_size = convert_bits_to_readable_string(size[0])
            if self.video.file_size:
                video_size = convert_bits_to_readable_string(size[1])
            else:
                video_size = "N/A"
            self.file_size_label.setText(f"{downloaded_size}/{video_size}")

    def download_finished(self, status: str):
        self.video.status = status
        if self.video.file_size:
            self.file_size_label.setText(convert_bits_to_readable_string(self.video.file_size))
        else:
            self.file_size_label.setText("N/A")
        self.construct_body()

    def pause_download_video(self):
        if self.video.status == "Downloading":
            self.video.status = "Paused"
            self.construct_body()
            self.thread.pause_download()

    def start_download(self):
        if self.video.status == "Queued":
            self.video.status = "Downloading"
            self.construct_body()
            self.thread.start()
        elif self.video.status == "Paused":
            self.thread.resume_download()
            self.video.status = "Downloading"
            self.construct_body()

    def construct_body(self):

        if self.inside_download_layout.count():
            remove_inside_layout(self.inside_download_layout)

        if self.bottom_row.count():
            remove_inside_layout(self.bottom_row)

        if self.top_row.count():
            remove_inside_layout(self.top_row)

        if self.both_row.count():
            remove_inside_layout(self.both_row)

        if self.inside_layout.count():
            remove_inside_layout(self.inside_layout)

        if self.video.status == "Downloaded":
            self.download_box.setStyleSheet("background-color:#d9f7d8; border-radius: 5px;")
        elif self.video.status in "Downloading":
            self.download_box.setStyleSheet("background-color:#e3e6ff; border-radius: 5px;")
        elif self.video.status in "Paused":
            self.download_box.setStyleSheet("background-color:#ffffed; border-radius: 5px;")
        elif self.video.status in "Stopped":
            self.download_box.setStyleSheet("background-color:#ffe3e3; border-radius: 5px;")
        elif self.video.status in "Queued":
            self.download_box.setStyleSheet("background-color:#f7f7f7; border-radius: 5px;")

        self.status_label.setText(self.video.status)

        if self.video.status in ("Queued", "Stopped"):
            if self.video.status == "Queued":
                self.inside_layout.addWidget(self.play_button)
            else:
                self.inside_layout.addWidget(self.restart_button)
            self.inside_layout.addSpacing(5)
            self.inside_layout.addWidget(self.video_title)
            self.inside_layout.addStretch()
            # self.inside_layout.addWidget(self.status_label)
        elif self.video.status == "Downloaded":
            self.inside_layout.addWidget(self.completed_button)
            self.inside_layout.addSpacing(5)
            self.inside_layout.addWidget(self.video_title)
            self.inside_layout.addStretch()
            # self.inside_layout.addWidget(self.status_label)
        elif self.video.status in ("Downloading", "Paused"):
            if self.video.status == "Downloading":
                self.inside_layout.addWidget(self.pause_button)
            else:
                self.inside_layout.addWidget(self.play_button)
            self.inside_layout.addSpacing(5)
            self.top_row.addWidget(self.video_title)
            self.top_row.addStretch()

            self.bottom_row.addWidget(self.progress_bar)

            self.both_row.addStretch()
            self.both_row.addLayout(self.top_row)
            self.both_row.addLayout(self.bottom_row)
            self.both_row.addStretch()
            self.inside_layout.addLayout(self.both_row)
            self.inside_layout.addSpacing(10)
            if self.video.status == "Downloading":
                self.inside_layout.addWidget(self.speed_label)
                self.inside_layout.addSpacing(10)
                self.inside_layout.addWidget(self.eta_label)
                self.inside_layout.addSpacing(10)
        self.inside_layout.addWidget(self.status_label)
        self.inside_layout.addWidget(self.file_size_label)
        self.inside_layout.addWidget(self.datetime_label)
        self.inside_layout.addWidget(self.remove_button)
        self.inside_layout.addWidget(self.delete_button)

        if self.video.status == "Queued":
            self.completed_button.setHidden(True)
            self.progress_bar.setHidden(True)
            self.speed_label.setHidden(True)
            self.eta_label.setHidden(True)
            self.pause_button.setHidden(True)
            self.restart_button.setHidden(True)

        if self.video.status == "Paused":
            self.play_button.setHidden(False)
            self.progress_bar.setHidden(False)
            self.speed_label.setHidden(True)
            self.eta_label.setHidden(True)
            self.completed_button.setHidden(True)
            self.pause_button.setHidden(True)
            self.restart_button.setHidden(True)

        if self.video.status == "Stopped":
            self.restart_button.setHidden(False)
            self.play_button.setHidden(True)
            self.progress_bar.setHidden(True)
            self.speed_label.setHidden(True)
            self.eta_label.setHidden(True)
            self.completed_button.setHidden(True)
            self.pause_button.setHidden(True)

        if self.video.status == "Downloading":
            self.pause_button.setHidden(False)
            self.progress_bar.setHidden(False)
            self.speed_label.setHidden(False)
            self.eta_label.setHidden(False)
            self.restart_button.setHidden(True)
            self.play_button.setHidden(True)
            self.completed_button.setHidden(True)

        if self.video.status == "Downloaded":
            self.completed_button.setHidden(False)
            self.pause_button.setHidden(True)
            self.progress_bar.setHidden(True)
            self.speed_label.setHidden(True)
            self.eta_label.setHidden(True)
            self.restart_button.setHidden(True)
            self.play_button.setHidden(True)

        self.inside_download_layout.addLayout(self.inside_layout)
        self.download_box.setLayout(self.inside_download_layout)
