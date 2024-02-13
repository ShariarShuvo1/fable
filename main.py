import math
import sys
import re
import webbrowser
from typing import List

import requests
from PyQt6.QtCore import Qt, QEvent, QSize, pyqtSignal
from PyQt6.QtGui import QGuiApplication, QIcon, QPixmap, QMovie
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, \
    QLabel, QComboBox

from Entity.Video import Video
from Styles.SearchStyle import *
import Consts.Constanats
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

    def __init__(self):
        super().__init__()

        self.search_result: List[Video] = []
        self.array_changed.connect(self.update_carousel)
        self.search_thread = None

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
        # Search Result Began ============================================

        main_layout.addStretch()
        container: QWidget = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def search_clicked(self):
        search_text: str = self.url_input.text()
        self.search_button.setHidden(True)
        self.url_input.setDisabled(True)
        self.loading_label.setVisible(True)
        if is_youtube_url(search_text):
            pass
        else:
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
            # resolution_layout.addStretch()

            resolution_combo = QComboBox()
            resolution_combo.setFixedHeight(40)
            resolution_combo.setStyleSheet(RESOLUTION_COMBOBOX_STYLESHEET)
            resolution_combo.setPlaceholderText("Choose Quality")

            for res in current_video.resolution_list:
                if res.file_type == "audio":
                    resolution_combo.addItem(
                        QIcon("./Assets/Icons/audio.png"),
                        f"{math.floor(float(res.abr))}Kbps [{res.ext}] [{convert_bits_to_readable_string(res.filesize)}]"
                    )
                elif res.file_type == "video":
                    resolution_combo.addItem(
                        QIcon("./Assets/Icons/video_no_audio.png"),
                        f"{res.height}p [{res.ext}] [{res.fps}fps] [{int(res.vbr)}Kbps] [{convert_bits_to_readable_string(res.filesize)}]"
                    )
                elif res.file_type == "mix":
                    resolution_combo.addItem(
                        QIcon("./Assets/Icons/video.png"),
                        f"{res.height}p [{res.ext}] [{res.fps}fps]"
                    )
            resolution_layout.addWidget(resolution_combo)
            # first_row.addWidget(resolution_combo)

            download_selected_res = QPushButton("Download")
            download_selected_res.setStyleSheet(DOWNLOAD_CURRENT_RES_BUTTON_STYLESHEET)
            download_selected_res.setFixedHeight(40)
            download_selected_res.setCursor(Qt.CursorShape.PointingHandCursor)
            resolution_layout.addWidget(download_selected_res)
            first_row.addLayout(resolution_layout)
            first_row.addStretch()
            # first_row.addWidget(download_selected_res)

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
                if key_event.key() == Qt.Key.Key_Tab:
                    clipboard_text: str = QApplication.clipboard().text()
                    if is_youtube_url(clipboard_text):
                        self.url_input.setText(clipboard_text)
                        return True
                elif key_event.key() == 16777220 and len(self.url_input.text()) > 0:
                    self.search_clicked()
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
