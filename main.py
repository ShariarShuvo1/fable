import math
import sys
import webbrowser
from datetime import datetime
from typing import List

from PyQt6.QtCore import Qt, QEvent, QSize, pyqtSignal, QThread
from PyQt6.QtGui import QGuiApplication, QIcon, QPixmap, QMovie
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, \
    QLabel, QComboBox, QMessageBox, QStyleFactory, QStyle, QProgressBar, QScrollArea, QFrame, QFileDialog

from Entity.Card import Card
from Entity.Resolution import Resolution
from Entity.Video import Video
from Entity.File import File
from Functions.SanitizeFilename import *
from Functions.youtube_url_checker import *
from Styles.PlaylistStyle import PLAYLIST_PROGRESS_STYLESHEET
from Styles.SearchStyle import *
from Styles.CarouselStyle import *
from Styles.DownloadListStyle import *
from Styles.FooterStyle import *
import Consts.Constanats
from Consts.SettingsData import *
from Threads.SearchPlaylistThread import SearchPlaylistThread
from Threads.SearchThread import SearchThread
from settings import SettingsWindow





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
    delete_card_signal = pyqtSignal(Card)

    def start_download(self, video: Video, index: int):
        if video and 0 <= index < len(video.resolution_list):
            resolution: Resolution = video.resolution_list[index]
            found = False
            for card in self.download_list:
                if card.video.webpage_url == video.video_url and card.video.format_id == resolution.format_id:
                    found = True
                    break
            if not found:
                if ALWAYS_ASK_FOR_OUTPUT_PATH:
                    output_path = QFileDialog.getExistingDirectory(
                        self, "Select Directory", OUTPUT_PATH)
                else:
                    output_path = OUTPUT_PATH
                if len(output_path) > 0:
                    add_music = False
                    extension: str = resolution.ext
                    if ALWAYS_ASK_TO_ADD_MUSIC and resolution.file_type == "video":
                        msg_box = QMessageBox()
                        msg_box.setIcon(QMessageBox.Icon.Question)
                        msg_box.setText(
                            "Do you want to add the audio as well?")
                        msg_box.setWindowTitle("Add Audio")
                        msg_box.setStandardButtons(
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                        msg_box.setDefaultButton(
                            QMessageBox.StandardButton.Yes)
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
                    file_obj: File = File(
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
                    self.download_list_viewer(file_obj)

    def __init__(self):
        super().__init__()

        self.playlist_search_result = None
        self.currently_downloading_count: int = 0

        self.delete_card_signal.connect(lambda card: self.delete_card(card))

        self.search_result: List[Video] = []
        self.array_changed.connect(self.update_carousel)
        self.search_thread = None
        self.search_playlist_thread = None

        self.download_list: List[Card] = []

        self.setWindowTitle("Fable")
        self.setStyleSheet(WINDOW_STYLESHEET)

        main_layout: QVBoxLayout = QVBoxLayout()

        # Search Widget Began ========================================
        url_layout: QHBoxLayout = QHBoxLayout()

        self.url_input: QLineEdit = QLineEdit()
        self.url_input.setPlaceholderText(
            "Enter Youtube URL or Search Videos...")
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
        self.main_body_frame = QHBoxLayout()
        self.main_body_frame.setContentsMargins(0, 0, 0, 0)
        self.main_body_frame.setSpacing(0)

        self.download_frame = QVBoxLayout()

        self.download_title = QLabel("Download List")
        self.download_title.setStyleSheet(DOWNLOAD_TITLE_STYLESHEET)
        self.download_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.download_title.setFixedHeight(50)
        self.download_frame.addWidget(self.download_title)
        self.download_list_layout = QVBoxLayout()
        self.download_list_layout.setSpacing(2)

        self.download_list_layout.addStretch()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet(SCROLL_AREA_STYLESHEET)

        self.download_list_container = QWidget()

        self.download_list_container.setLayout(self.download_list_layout)
        self.scroll_area.setWidget(self.download_list_container)
        self.download_frame.addWidget(self.scroll_area)

        self.main_body_frame.addLayout(self.download_frame)

        # Playlist Start ============================================
        self.playlist_widget = QWidget()
        self.playlist_widget.setFixedWidth(500)
        self.playlist_layout = QVBoxLayout()
        self.playlist_layout.setContentsMargins(5, 0, 0, 0)

        self.playlist_title = QLabel("Playlist")
        self.playlist_title.setStyleSheet(PLAYLIST_TITLE_STYLESHEET)
        self.playlist_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.playlist_title.setFixedHeight(50)
        self.playlist_layout.addWidget(self.playlist_title)
        self.playlist_layout.setSpacing(0)

        self.playlist_progress = QProgressBar()
        self.playlist_progress.setFixedHeight(30)
        self.playlist_progress.setRange(0, 100)
        self.playlist_progress.setValue(0)
        self.playlist_progress.setHidden(True)
        self.playlist_progress.setStyleSheet(PLAYLIST_PROGRESS_STYLESHEET)
        self.playlist_layout.addWidget(self.playlist_progress)

        self.playlist_scroll_layout = QVBoxLayout()
        self.playlist_scroll_layout.setSpacing(2)
        self.playlist_scroll_layout.addStretch()

        self.playlist_scroll_area = QScrollArea()
        self.playlist_scroll_area.setWidgetResizable(True)
        self.playlist_scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.playlist_scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.playlist_scroll_area.setStyleSheet(SCROLL_AREA_STYLESHEET)

        self.playlist_container = QWidget()
        self.playlist_container.setLayout(self.playlist_scroll_layout)
        self.playlist_scroll_area.setWidget(self.playlist_container)
        self.playlist_layout.addWidget(self.playlist_scroll_area)

        self.playlist_download_button = QPushButton("Download")
        self.playlist_download_button.setStyleSheet(PLAYLIST_DOWNLOAD_BUTTON_STYLESHEET)
        self.playlist_download_button.setFixedHeight(30)
        self.playlist_download_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.playlist_layout.addWidget(self.playlist_download_button)

        self.playlist_widget.setLayout(self.playlist_layout)
        self.playlist_widget.setHidden(True)
        self.main_body_frame.addWidget(self.playlist_widget)
        # Playlist End ============================================

        main_layout.addLayout(self.main_body_frame)
        # Download List End ============================================

        # Footer Start ============================================
        self.footer_layout = QHBoxLayout()
        self.settings = QPushButton()
        self.settings.setIcon(QIcon("./Assets/Icons/settings.png"))
        self.settings.setIconSize(QSize(30, 30))
        self.settings.setStyleSheet(FOOTER_STYLESHEET)
        self.settings.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings.clicked.connect(self.show_settings_window)
        self.footer_layout.addWidget(self.settings)

        github = QPushButton()
        github.setIcon(QIcon("./Assets/Icons/github.png"))
        github.setIconSize(QSize(30, 30))

        github.setStyleSheet(FOOTER_STYLESHEET)
        github.setCursor(Qt.CursorShape.PointingHandCursor)
        github.clicked.connect(
            lambda: open_channel("https://github.com/ShariarShuvo1/fable"))
        self.footer_layout.addWidget(github)
        self.footer_layout.addStretch()
        main_layout.addLayout(self.footer_layout)
        # Footer End ============================================

        container: QWidget = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def show_settings_window(self):
        settings_window = SettingsWindow(self)
        settings_window.exec()

    def delete_card(self, card: Card):
        self.download_list_layout.removeWidget(card.download_box)
        card.download_box.setParent(None)
        card.download_box.deleteLater()
        self.download_list.remove(card)

    def download_list_viewer(self, video: File):
        card: Card = Card(video, self.currently_downloading_count, self)
        self.download_list.append(card)
        self.download_list_layout.insertWidget(0, card.download_box)

    def search_clicked(self):
        self.playlist_widget.setHidden(True)
        search_text: str = self.url_input.text()
        if len(search_text) > 0:
            self.search_button.setHidden(True)
            self.url_input.setDisabled(True)
            self.loading_label.setVisible(True)
            if is_youtube_playlist(search_text):
                self.playlist_widget.setHidden(False)
                self.playlist_progress.setHidden(False)
                if self.search_playlist_thread and self.search_playlist_thread.isRunning():
                    self.search_playlist_thread.terminate()
                self.search_playlist_thread = SearchPlaylistThread(search_text)
                self.search_playlist_thread.search_finished.connect(
                    self.on_playlist_search_finished)
                self.search_playlist_thread.total_videos.connect(
                    self.total_video_in_playlist)
                self.search_playlist_thread.completed_videos.connect(
                    self.update_playlist_progress)
                self.search_playlist_thread.start()
            else:
                if self.search_thread and self.search_thread.isRunning():
                    self.search_thread.terminate()
                self.search_thread = SearchThread(
                    search_text, Consts.Constanats.TOTAL_ELEMENT_FOR_CAROUSEL)
                self.search_thread.search_finished.connect(self.on_search_finished)
                self.search_thread.start()

    def total_video_in_playlist(self, total: int):
        self.playlist_progress.setRange(0, total)

    def update_playlist_progress(self, completed: int):
        self.playlist_progress.setValue(completed)

    def on_search_finished(self, result_list):
        self.search_result = result_list
        self.url_input.setDisabled(False)
        self.search_button.setHidden(False)
        self.loading_label.setVisible(False)
        self.array_changed.emit()

    def on_playlist_search_finished(self, result_list):
        self.playlist_progress.setHidden(True)
        self.playlist_search_result = result_list
        self.url_input.setDisabled(False)
        self.search_button.setHidden(False)
        self.loading_label.setVisible(False)
        # self.array_changed.emit()

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
            resolution_combo.setMinimumHeight(40)
            resolution_combo.setStyleSheet(RESOLUTION_COMBOBOX_STYLESHEET)
            resolution_combo.setPlaceholderText("Choose Quality")

            for res in current_video.resolution_list:
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

            download_selected_res.setStyleSheet(
                DOWNLOAD_CURRENT_RES_BUTTON_STYLESHEET)
            download_selected_res.setMinimumHeight(40)
            download_selected_res.setCursor(Qt.CursorShape.PointingHandCursor)
            resolution_layout.addWidget(download_selected_res)
            first_row.addLayout(resolution_layout)
            first_row.addStretch()

            inside_carousel_layout.addLayout(first_row)

            title = QLabel(current_video.title)
            title.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse)
            title.setWordWrap(True)
            title.setStyleSheet(CAROUSEL_TITLE_STYLESHEET)
            inside_carousel_layout.addWidget(title)

            channel = QPushButton(current_video.uploader)
            channel.setCursor(Qt.CursorShape.PointingHandCursor)
            channel.setStyleSheet(CAROUSEL_CHANNEL_STYLESHEET)
            channel.clicked.connect(
                lambda: open_channel(current_video.channel_url))
            inside_carousel_layout.addWidget(channel)

            views = QLabel(
                f"Views: {format_view_count(current_video.view_count)}")
            views.setStyleSheet(CAROUSEL_GENERAL_DATA_STYLESHEET)
            inside_carousel_layout.addWidget(views)

            duration = QLabel(
                f"Duration: {format_duration(current_video.duration)}")
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
                if is_youtube_url(clipboard_text) or is_youtube_playlist(clipboard_text):
                    self.url_input.setPlaceholderText(
                        f"{clipboard_text}    press [TAB] to paste")
                else:
                    self.url_input.setPlaceholderText(
                        "Enter Youtube URL or Search Videos...")
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
                self.url_input.setPlaceholderText(
                    "Enter Youtube URL or Search Videos...")
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
