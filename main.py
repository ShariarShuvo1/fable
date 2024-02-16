import math
import sys
import re
import webbrowser
from datetime import datetime
from typing import List

import yt_dlp
from PyQt6.QtCore import Qt, QEvent, QSize, pyqtSignal, QThread
from PyQt6.QtGui import QGuiApplication, QIcon, QPixmap, QMovie
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, \
    QLabel, QComboBox, QMessageBox, QStyleFactory, QStyle, QProgressBar, QScrollArea, QFrame, QFileDialog

from Entity.Resolution import Resolution
from Entity.Video import Video
from Entity.File import File
from Functions.SanitizeFilename import *
from Styles.SearchStyle import *
from Styles.CarouselStyle import *
from Styles.DownloadListStyle import *
import Consts.Constanats
from Consts.Settings import *
from Threads.SearchThread import SearchThread


def is_youtube_url(text):
    youtube_regex = r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)"
    return re.match(youtube_regex, text) is not None


def open_channel(url):
    webbrowser.open(url)


def format_view_count(view_count):
    if view_count >= 1_000_000_000:
        return f"{view_count // 1_000_000_000}B"
    elif view_count >= 1_000_000:
        return f"{view_count // 1_000_000}M"
    elif view_count >= 1_000:
        return f"{view_count // 1_000}K"
    else:
        return str(view_count)


def format_duration(duration):
    hours, remainder = divmod(duration, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"


def convert_bits_to_readable_string(bits):
    units = ['B', 'KB', 'MB', 'GB']
    index = 0
    while bits >= 1024 and index < len(units) - 1:
        bits /= 1024.0
        index += 1
    return '{:.1f}{}'.format(bits, units[index])


class MainWindow(QMainWindow):
    array_changed = pyqtSignal()
    download_list_changed = pyqtSignal()

    def start_download(self, video: Video, index: int):
        if video and 0 <= index < len(video.resolution_list):
            resolution: Resolution = video.resolution_list[index]
            found = False
            for file in self.download_list:
                if file.webpage_url == video.video_url and file.format_id == resolution.format_id:
                    found = True
                    break
            if not found:
                if ALWAYS_ASK_FOR_OUTPUT_PATH:
                    output_path = QFileDialog.getExistingDirectory(self, "Select Directory", OUTPUT_PATH)
                else:
                    output_path = OUTPUT_PATH
                if len(output_path) > 0:
                    add_music = False
                    extension: str = resolution.ext
                    if ALWAYS_ASK_TO_ADD_MUSIC and resolution.file_type == "video":
                        msg_box = QMessageBox()
                        msg_box.setIcon(QMessageBox.Icon.Question)
                        msg_box.setText("Do you want to add the audio as well?")
                        msg_box.setWindowTitle("Add Audio")
                        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                        msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)
                        response = msg_box.exec()
                        if response == QMessageBox.StandardButton.Yes:
                            add_music = True
                            extension = "mp4"
                    title = sanitize_filename(video.title)
                    if resolution.file_type == "audio":
                        title += f"_{int(resolution.abr)}kbps"
                    elif resolution.file_type == "mix":
                        title += f"_{resolution.height}p"
                    elif resolution.file_type == "video":
                        title += f"_{resolution.height}p_{int(resolution.vbr)}kbps"
                    file: File = File(
                        f"{title}.{extension}",
                        video.video_url,
                        resolution.format_id,
                        resolution.url,
                        resolution.file_type,
                        "Queued",
                        datetime.now(),
                        resolution.filesize,
                        output_path,
                        add_music
                    )
                    self.download_list.append(file)
                    self.download_list_changed.emit()

    def __init__(self):
        super().__init__()

        self.currently_downloading_count: int = 0

        self.search_result: List[Video] = []
        self.array_changed.connect(self.update_carousel)
        self.search_thread = None

        self.download_list: List[File] = []
        self.download_list_changed.connect(self.download_list_viewer)

        self.setWindowTitle("Fable")
        self.setStyleSheet(WINDOW_STYLESHEET)

        main_layout: QVBoxLayout = QVBoxLayout()

        # Search Widget Began ========================================
        url_layout: QHBoxLayout = QHBoxLayout()

        self.url_input: QLineEdit = QLineEdit()
        self.url_input.setPlaceholderText("Enter Youtube URL or Search Videos...")
        self.url_input.setMinimumSize(500, 50)
        self.url_input.setClearButtonEnabled(True)
        self.url_input.setStyleSheet(URL_INPUT_STYLESHEET)
        self.url_input.installEventFilter(self)
        url_layout.addWidget(self.url_input)

        self.loading_label = QLabel()
        self.loading_label.setStyleSheet(LOADING_BUTTON_STYLESHEET)
        self.loading_label.setFixedSize(100, 50)
        self.loading_label.setVisible(False)
        movie = QMovie("./Assets/Icons/loading.gif")
        self.loading_label.setMovie(movie)
        movie.start()
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        url_layout.addWidget(self.loading_label)

        self.search_button: QPushButton = QPushButton("Search")
        self.search_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.search_button.setMinimumSize(100, 50)
        self.search_button.setStyleSheet(SEARCH_BUTTON_STYLESHEET)
        self.search_button.clicked.connect(self.search_clicked)

        url_layout.addWidget(self.search_button)

        main_layout.addLayout(url_layout)
        # Search Widget Finished ========================================

        # Search Result Began ============================================
        self.search_result_layout: QHBoxLayout = QHBoxLayout()

        self.prev_btn: QPushButton = QPushButton()
        self.prev_btn.setFixedSize(30, Consts.Constanats.CAROUSEL_HEIGHT)
        self.prev_btn.setIcon(QIcon("./Assets/Icons/prev_icon.png"))
        self.prev_btn.setIconSize(QSize(25, 25))
        self.prev_btn.setStyleSheet(CAROUSEL_BUTTON_STYLESHEET)
        self.prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_btn.clicked.connect(self.show_previous)
        self.search_result_layout.addWidget(self.prev_btn)

        self.next_btn: QPushButton = QPushButton()
        self.next_btn.setFixedSize(30, Consts.Constanats.CAROUSEL_HEIGHT)
        self.next_btn.setIcon(QIcon("./Assets/Icons/next_icon.png"))
        self.next_btn.setIconSize(QSize(25, 25))
        self.next_btn.setStyleSheet(CAROUSEL_BUTTON_STYLESHEET)
        self.next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_btn.clicked.connect(self.show_next)

        # Carousel of Boxes ============================================
        self.carousel_layout: QHBoxLayout = QHBoxLayout()
        self.current_index: int = 0
        self.update_carousel()
        self.search_result_layout.addLayout(self.carousel_layout)
        # Carousel of Boxes ============================================

        self.search_result_layout.addWidget(self.next_btn)

        main_layout.addLayout(self.search_result_layout)
        # Search Result End ============================================

        # Download List Began ============================================
        self.download_title = QLabel("Download List")
        self.download_title.setStyleSheet(DOWNLOAD_TITLE_STYLESHEET)
        self.download_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.download_title.setFixedHeight(50)
        main_layout.addWidget(self.download_title)
        self.download_list_layout = QVBoxLayout()
        self.download_list_layout.setSpacing(2)

        self.download_list_viewer()
        self.download_list_layout.addStretch()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet(SCROLL_AREA_STYLESHEET)

        self.download_list_container = QWidget()

        self.download_list_container.setLayout(self.download_list_layout)
        self.scroll_area.setWidget(self.download_list_container)

        main_layout.addWidget(self.scroll_area)
        # Download List End ============================================

        container: QWidget = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def download_list_viewer(self):
        while self.download_list_layout.count() - 1 > 0:
            item = self.download_list_layout.takeAt(0)
            widget = item.widget()
            widget.setParent(None)
        for i in range(len(self.download_list) - 1, -1, -1):
            video: File = self.download_list[i]
            download_box: QWidget = QWidget()
            if video.status == "Downloaded":
                download_box.setStyleSheet("background-color:#d9f7d8; ")
            elif video.status in "Downloading":
                download_box.setStyleSheet("background-color:#e3e6ff; ")
            elif video.status in "Paused":
                download_box.setStyleSheet("background-color:#ffffed; ")
            elif video.status in "Stopped":
                download_box.setStyleSheet("background-color:#ffe3e3; ")
            elif video.status in "Queued":
                download_box.setStyleSheet("background-color:#f7f7f7; ")
            download_box.setFixedHeight(Consts.Constanats.DOWNLOAD_BOX_HEIGHT)
            inside_download_layout = QHBoxLayout()
            inside_download_layout.setContentsMargins(0, 0, 0, 0)

            video_title = QLabel(video.title)
            video_title.setStyleSheet(VIDEO_TITLE_STYLESHEET)

            status_label = QLabel(video.status)
            status_label.setFixedWidth(80)
            status_label.setStyleSheet(VIDEO_STATUS_STYLESHEET)

            if video.file_size:
                file_size = convert_bits_to_readable_string(video.file_size)
            else:
                file_size = "N/A"
            file_size_label = QLabel(file_size)
            file_size_label.setStyleSheet(VIDEO_SIZE_STYLESHEET)
            file_size_label.setFixedWidth(60)

            datetime_label = QLabel(video.added_date.strftime("%Y-%m-%d %H:%M:%S"))
            datetime_label.setStyleSheet(VIDEO_STATUS_STYLESHEET)
            datetime_label.setFixedWidth(110)

            icon_size = QSize(30, 30)

            play_button = QPushButton()
            play_button.setIcon(QIcon("./Assets/Icons/play-icon.png"))
            play_button.setIconSize(icon_size)
            play_button.setStyleSheet(TOOL_ICON_BUTTON_STYLESHEET)

            pause_button = QPushButton()
            pause_button.setIcon(QIcon("./Assets/Icons/pause-icon.png"))
            pause_button.setIconSize(icon_size)
            pause_button.setStyleSheet(TOOL_ICON_BUTTON_STYLESHEET)

            cancel_button = QPushButton()
            cancel_button.setIcon(QIcon("./Assets/Icons/cancel-icon.png"))
            cancel_button.setIconSize(icon_size)
            cancel_button.setStyleSheet(TOOL_ICON_BUTTON_STYLESHEET)

            delete_button = QPushButton()
            delete_button.setIcon(QIcon("./Assets/Icons/delete-icon.png"))
            delete_button.setIconSize(icon_size)
            delete_button.setStyleSheet(TOOL_ICON_BUTTON_STYLESHEET)

            restart_button = QPushButton()
            restart_button.setIcon(QIcon("./Assets/Icons/restart-icon.png"))
            restart_button.setIconSize(icon_size)
            restart_button.setStyleSheet(TOOL_ICON_BUTTON_STYLESHEET)

            completed_button = QPushButton()
            completed_button.setIcon(QIcon("./Assets/Icons/completed-icon.png"))
            completed_button.setIconSize(icon_size)
            completed_button.setStyleSheet(TOOL_ICON_BUTTON_STYLESHEET)

            inside_layout = QHBoxLayout()
            inside_layout.setSpacing(0)

            if video.status in ("Queued", "Stopped"):
                if video.status == "Queued":
                    inside_layout.addWidget(play_button)
                else:
                    inside_layout.addWidget(restart_button)
                inside_layout.addSpacing(5)
                inside_layout.addWidget(video_title)
                inside_layout.addStretch()
                inside_layout.addWidget(status_label)
            elif video.status == "Downloaded":
                inside_layout.addWidget(completed_button)
                inside_layout.addSpacing(5)
                inside_layout.addWidget(video_title)
                inside_layout.addStretch()
                inside_layout.addWidget(status_label)
            elif video.status in ("Downloading", "Paused"):
                if video.status == "Downloading":
                    inside_layout.addWidget(pause_button)
                else:
                    inside_layout.addWidget(play_button)
                inside_layout.addSpacing(5)
                both_row = QVBoxLayout()
                top_row = QHBoxLayout()
                bottom_row = QHBoxLayout()
                top_row.addWidget(video_title)
                top_row.addStretch()

                progress_bar = QProgressBar()
                progress_bar.setFixedHeight(16)
                progress_bar.setTextVisible(True)
                progress_bar.setRange(0, 100)
                progress_bar.setValue(100)
                progress_bar.setStyleSheet(PROGRESS_BAR_STYLESHEET)
                bottom_row.addWidget(progress_bar)

                both_row.addStretch()
                both_row.addLayout(top_row)
                both_row.addLayout(bottom_row)
                both_row.addStretch()
                inside_layout.addLayout(both_row)
                inside_layout.addSpacing(10)
                if video.status == "Downloading":
                    inside_layout.addWidget(QLabel("Speed"))
                    inside_layout.addSpacing(10)
                    inside_layout.addWidget(QLabel("ETA"))
                    inside_layout.addSpacing(10)
                else:
                    inside_layout.addWidget(status_label)
            inside_layout.addWidget(file_size_label)
            inside_layout.addWidget(datetime_label)
            inside_layout.addWidget(cancel_button)
            inside_layout.addWidget(delete_button)

            inside_download_layout.addLayout(inside_layout)
            download_box.setLayout(inside_download_layout)
            self.download_list_layout.insertWidget(self.download_list_layout.count() - 1, download_box)

    def search_clicked(self):
        search_text: str = self.url_input.text()
        if len(search_text) > 0:
            self.search_button.setHidden(True)
            self.url_input.setDisabled(True)
            self.loading_label.setVisible(True)
            if self.search_thread and self.search_thread.isRunning():
                self.search_thread.terminate()
            self.search_thread = SearchThread(search_text, Consts.Constanats.TOTAL_ELEMENT_FOR_CAROUSEL)
            self.search_thread.search_finished.connect(self.on_search_finished)
            self.search_thread.start()

    def on_search_finished(self, result_list):
        self.search_result = result_list
        self.url_input.setDisabled(False)
        self.search_button.setHidden(False)
        self.loading_label.setVisible(False)
        self.array_changed.emit()

    def update_carousel(self):
        for i in reversed(range(self.carousel_layout.count())):
            self.carousel_layout.itemAt(i).widget().setParent(None)

        elements_to_show: int = min(
            self.current_index + Consts.Constanats.NUMBER_OF_ELEMENT_FOR_CAROUSEL,
            len(self.search_result)
        )
        if len(self.search_result) <= 3:
            self.prev_btn.setHidden(True)
            self.next_btn.setHidden(True)
        else:
            self.prev_btn.setHidden(False)
            self.next_btn.setHidden(False)

        for i in range(self.current_index, elements_to_show):
            current_video = self.search_result[i]
            carousel_box: QWidget = QWidget()
            carousel_box.setMinimumWidth(Consts.Constanats.CAROUSEL_WIDTH)
            carousel_box.setFixedHeight(Consts.Constanats.CAROUSEL_HEIGHT)
            carousel_box.setStyleSheet(CAROUSEL_BOX_STYLESHEET)
            inside_carousel_layout = QVBoxLayout()
            inside_carousel_layout.setContentsMargins(5, 1, 1, 1)
            inside_carousel_layout.setSpacing(1)

            first_row = QHBoxLayout()
            first_row.setContentsMargins(0, 0, 0, 0)
            first_row.setSpacing(0)

            thumbnail_label = QLabel()
            thumbnail_label.setFixedHeight(90)
            thumbnail_label.setStyleSheet(CAROUSEL_THUMBNAIL_STYLESHEET)
            pixmap = QPixmap()
            pixmap.loadFromData(current_video.thumbnail.content)
            pixmap = pixmap.scaled(120, 90, Qt.AspectRatioMode.KeepAspectRatio)
            thumbnail_label.setPixmap(pixmap)
            first_row.addWidget(thumbnail_label)

            resolution_layout = QVBoxLayout()

            resolution_combo = QComboBox()
            resolution_combo.setFixedHeight(40)
            resolution_combo.setStyleSheet(RESOLUTION_COMBOBOX_STYLESHEET)
            resolution_combo.setPlaceholderText("Choose Quality")

            for res in current_video.resolution_list:
                icon = QIcon("./Assets/Icons/audio.png") if res.file_type == "audio" else QIcon(
                    "./Assets/Icons/video_no_audio.png") if res.file_type == "video" else QIcon(
                    "./Assets/Icons/video.png")
                ext = f"[{res.ext}]"
                rate = f"{math.floor(res.abr)}kbps" if res.file_type == "audio" and res.abr else ""
                rate = f"[{math.floor(res.vbr)}kbps]" \
                    if ((res.file_type == "video" or res.file_type == "mix")
                        and res.vbr) else "" if rate == "" else rate
                file_size = f"[{convert_bits_to_readable_string(res.filesize)}]" if res.filesize else ""
                fps = f"[{res.fps}fps]" if res.fps else ""
                height = f"{res.height}p " if res.height else ""
                if res.file_type == "audio":
                    resolution_combo.addItem(
                        QIcon(icon),
                        f"{rate} {ext} {file_size}"
                    )
                else:
                    resolution_combo.addItem(
                        QIcon(icon),
                        f"{height}{ext} {fps} {rate} {file_size}"
                    )

            resolution_layout.addWidget(resolution_combo)

            download_selected_res = QPushButton("Download")
            (download_selected_res.clicked.connect(
                lambda checked,
                video=current_video,
                combo=resolution_combo: self.start_download(video, combo.currentIndex())
            )
            )

            download_selected_res.setStyleSheet(DOWNLOAD_CURRENT_RES_BUTTON_STYLESHEET)
            download_selected_res.setFixedHeight(40)
            download_selected_res.setCursor(Qt.CursorShape.PointingHandCursor)
            resolution_layout.addWidget(download_selected_res)
            first_row.addLayout(resolution_layout)
            first_row.addStretch()

            inside_carousel_layout.addLayout(first_row)

            title = QLabel(current_video.title)
            title.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            title.setWordWrap(True)
            title.setStyleSheet(CAROUSEL_TITLE_STYLESHEET)
            inside_carousel_layout.addWidget(title)

            channel = QPushButton(current_video.uploader)
            channel.setCursor(Qt.CursorShape.PointingHandCursor)
            channel.setStyleSheet(CAROUSEL_CHANNEL_STYLESHEET)
            channel.clicked.connect(lambda: open_channel(current_video.channel_url))
            inside_carousel_layout.addWidget(channel)

            views = QLabel(f"Views: {format_view_count(current_video.view_count)}")
            views.setStyleSheet(CAROUSEL_GENERAL_DATA_STYLESHEET)
            inside_carousel_layout.addWidget(views)

            duration = QLabel(f"Duration: {format_duration(current_video.duration)}")
            duration.setStyleSheet(CAROUSEL_GENERAL_DATA_STYLESHEET)
            inside_carousel_layout.addWidget(duration)

            inside_carousel_layout.addStretch()
            carousel_box.setLayout(inside_carousel_layout)
            self.carousel_layout.addWidget(carousel_box)

    def show_previous(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_carousel()

    def show_next(self):
        if (
                (self.current_index + Consts.Constanats.NUMBER_OF_ELEMENT_FOR_CAROUSEL) <
                Consts.Constanats.TOTAL_ELEMENT_FOR_CAROUSEL
        ):
            self.current_index += 1
            self.update_carousel()

    def eventFilter(self, obj, event):
        if obj is self.url_input:
            if event.type() == QEvent.Type.FocusIn:
                clipboard_text: str = QApplication.clipboard().text()
                if is_youtube_url(clipboard_text):
                    self.url_input.setPlaceholderText(f"{clipboard_text}    press [TAB] to paste")
                else:
                    self.url_input.setPlaceholderText("Enter Youtube URL or Search Videos...")
            elif event.type() == QEvent.Type.KeyPress:
                key_event = event
                if key_event.key() == Qt.Key.Key_Tab or key_event.key() == Qt.Key.Key_Right:
                    clipboard_text: str = QApplication.clipboard().text()
                    if clipboard_text not in self.url_input.text():
                        self.url_input.setText(clipboard_text)
                        return True
                elif key_event.key() == 16777220 and len(self.url_input.text()) > 0:
                    self.search_clicked()
            elif event.type() == QEvent.Type.MouseButtonPress:
                key_event = event
                if key_event.button() == Qt.MouseButton.RightButton:
                    clipboard_text: str = QApplication.clipboard().text()
                    if clipboard_text not in self.url_input.text():
                        self.url_input.setText(clipboard_text)
                        return True
            elif event.type() == QEvent.Type.FocusOut:
                self.url_input.setPlaceholderText("Enter Youtube URL or Search Videos...")
        return super().eventFilter(obj, event)


if __name__ == "__main__":
    app: QApplication = QApplication(sys.argv)

    primary_screen = QGuiApplication.primaryScreen().availableGeometry()
    Consts.Constanats.SCREEN_WIDTH = primary_screen.width()
    Consts.Constanats.SCREEN_HEIGHT = primary_screen.height()

    window: MainWindow = MainWindow()
    # window.showMaximized()
    window.show()
    sys.exit(app.exec())
