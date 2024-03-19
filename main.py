import math
import sys
import webbrowser
from datetime import datetime
from typing import List

from PyQt6.QtCore import Qt, QEvent, QSize, pyqtSignal, QThread
from PyQt6.QtGui import QGuiApplication, QIcon, QPixmap, QMovie
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, \
    QLabel, QComboBox, QMessageBox, QStyleFactory, QStyle, QProgressBar, QScrollArea, QFrame, QFileDialog

from Entity.AudioStory import AudioStory
from Entity.AudioStoryCard import AudioStoryCard
from Entity.AudioStoryPreviewCard import AudioStoryPreviewCard
from Entity.Card import Card
from Entity.PlaylistCard import PlaylistCard
from Entity.Resolution import Resolution
from Entity.ToggleButton import ToggleButton
from Entity.Video import Video
from Entity.File import File
from Functions.SanitizeFilename import *
from Functions.youtube_url_checker import *
from Styles.AudioStyleCardStyle import CLEAR_ALL_BUTTON_STYLESHEET
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

    def start_download(self, video: Video, index: int, res=None, playlist_output_path=None,
                       add_music_to_playlist=False):
        if video and 0 <= index < len(video.resolution_list):
            if not res:
                resolution: Resolution = video.resolution_list[index]
            else:
                resolution: Resolution = res
            found = False
            for card in self.download_list:
                if isinstance(card, Card):
                    if not res and card.video.webpage_url == video.video_url and card.video.format_id == resolution.format_id:
                        found = True
                        break
                    elif res and card.video.webpage_url == video.video_url and card.video.format_id == resolution.format_id and card.video.add_music == add_music_to_playlist:
                        found = True
                        break
            if not found:

                if get_ask_for_output_path() and not res:
                    output_path = QFileDialog.getExistingDirectory(
                        self, "Select Directory", get_output_path())
                    if output_path == "" or output_path == " " or output_path is None:
                        return
                elif playlist_output_path and res:
                    output_path = playlist_output_path
                else:
                    output_path = get_output_path()
                if len(output_path) > 0:
                    add_music = get_add_music()
                    extension: str = resolution.ext
                    if get_always_ask_to_add_music() and resolution.file_type == "video" and not res:
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
                    elif res and add_music_to_playlist:
                        add_music = True
                        extension = "mp4"
                    for card in self.download_list:
                        if isinstance(card, Card):
                            if not res and card.video.webpage_url == video.video_url and card.video.format_id == resolution.format_id and card.video.add_music == add_music:
                                return
                    title = sanitize_filename(video.title)
                    if resolution.file_type == "audio":
                        title += f"_{int(resolution.abr)}kbps"
                    elif resolution.file_type == "mix":
                        title += f"_{resolution.height}p"
                    elif resolution.file_type == "video":
                        title += f"_{resolution.height}p_{
                        int(resolution.vbr)}kbps"
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

        self.currently_downloading_count: int = 0

        self.delete_card_signal.connect(lambda card: self.delete_card(card))

        self.search_result: List[Video] = []
        self.array_changed.connect(self.update_carousel)
        self.search_thread = None
        self.search_playlist_thread = None

        self.download_list: List[Card | AudioStoryCard] = []

        self.playlist_list: List[PlaylistCard] = []

        self.audio_story_list: List[AudioStoryPreviewCard] = []

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

        self.search_cancel_button: QPushButton = QPushButton("Cancel")
        self.search_cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.search_cancel_button.setMinimumSize(100, 50)
        self.search_cancel_button.setStyleSheet(CANCEL_BUTTON_STYLESHEET)
        self.search_cancel_button.clicked.connect(self.cancel_search_clicked)
        self.search_cancel_button.setHidden(True)
        url_layout.addWidget(self.search_cancel_button)

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

        # Audio Story Start ============================================
        self.audio_story_widget = QWidget()
        self.audio_story_widget.setMinimumWidth(500)
        self.audio_story_layout = QVBoxLayout()
        self.audio_story_layout.setContentsMargins(5, 0, 0, 0)

        self.audio_story_download_button = QPushButton("Download Selected")
        self.audio_story_download_button.setStyleSheet(
            PLAYLIST_DOWNLOAD_BUTTON_STYLESHEET)
        self.audio_story_download_button.setFixedHeight(50)
        self.audio_story_download_button.setCursor(
            Qt.CursorShape.PointingHandCursor)
        self.audio_story_download_button.clicked.connect(self.audio_story_download_clicked)

        self.audio_story_name_input = QLineEdit()
        self.audio_story_name_input.setPlaceholderText("Enter Audio Story Name (Optional)")
        self.audio_story_name_input.setStyleSheet(URL_INPUT_STYLESHEET)
        self.audio_story_name_input.setFixedHeight(50)
        self.audio_story_name_input.setFixedWidth(350)

        self.clear_audio_story_queue_button = QPushButton("Clear Queue")
        self.clear_audio_story_queue_button.setStyleSheet(
            CLEAR_ALL_BUTTON_STYLESHEET)
        self.clear_audio_story_queue_button.setFixedHeight(50)
        self.clear_audio_story_queue_button.setFixedWidth(100)
        self.clear_audio_story_queue_button.setCursor(
            Qt.CursorShape.PointingHandCursor)
        self.clear_audio_story_queue_button.clicked.connect(self.clear_audio_story_list)

        self.audio_story_top_row = QHBoxLayout()

        self.audio_story_top_row.addWidget(self.audio_story_name_input)
        self.audio_story_top_row.addWidget(self.audio_story_download_button)
        self.audio_story_top_row.addWidget(self.clear_audio_story_queue_button)

        self.audio_story_layout.addLayout(self.audio_story_top_row)

        self.audio_story_scroll_layout = QVBoxLayout()
        self.audio_story_scroll_layout.setSpacing(2)
        self.audio_story_scroll_layout.addStretch()

        self.audio_story_scroll_area = QScrollArea()
        self.audio_story_scroll_area.setWidgetResizable(True)
        self.audio_story_scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.audio_story_scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.audio_story_scroll_area.setStyleSheet(SCROLL_AREA_STYLESHEET)

        self.audio_story_container = QWidget()
        self.audio_story_container.setLayout(self.audio_story_scroll_layout)
        self.audio_story_scroll_area.setWidget(self.audio_story_container)
        self.audio_story_layout.addWidget(self.audio_story_scroll_area)

        self.audio_story_widget.setLayout(self.audio_story_layout)
        self.audio_story_widget.setHidden(True)
        main_layout.addWidget(self.audio_story_widget)
        # Audio Story End ============================================

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

        self.playlist_resolution_combo = QComboBox()
        self.playlist_resolution_combo.setMinimumHeight(40)
        self.playlist_resolution_combo.setStyleSheet(
            RESOLUTION_COMBOBOX_STYLESHEET)
        self.playlist_resolution_combo.setPlaceholderText(
            "Choose Quality For Selected")

        self.playlist_resolution_combo.addItem("Best Audio Only [Fast]")
        self.playlist_resolution_combo.addItem(
            "Video Only (with Audio) [Fast]")
        self.playlist_resolution_combo.addItem(
            "Best Video Only (No Audio) [Fast]")
        self.playlist_resolution_combo.addItem(
            "Best Quality (Video with Audio) [Slow]")

        self.playlist_download_button = QPushButton("Download Selected")
        self.playlist_download_button.setStyleSheet(
            PLAYLIST_DOWNLOAD_BUTTON_STYLESHEET)
        self.playlist_download_button.setFixedHeight(30)
        self.playlist_download_button.setCursor(
            Qt.CursorShape.PointingHandCursor)
        (self.playlist_download_button.clicked.connect(
            lambda checked,
                   combo=self.playlist_resolution_combo: self.playlist_download_clicked(combo.currentIndex())
        ))
        self.playlist_layout.addWidget(self.playlist_resolution_combo)
        self.playlist_layout.addSpacing(5)
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

        self.fast_audio_story_mode_label = QLabel("Fast Mode")
        self.fast_audio_story_mode_label.setStyleSheet(FOOTER_LABEL_STYLESHEET)
        self.footer_layout.addWidget(self.fast_audio_story_mode_label)

        self.fast_audio_story_toggler = ToggleButton()
        self.fast_audio_story_toggler.setFixedSize(50, 25)
        self.fast_audio_story_toggler.setCursor(
            Qt.CursorShape.PointingHandCursor)
        self.fast_audio_story_toggler.setChecked(
            get_always_fast_audio_story_mode())
        self.footer_layout.addWidget(self.fast_audio_story_toggler)
        self.fast_audio_story_mode_label.setDisabled(
            not get_always_start_with_audio_story_mode())
        self.fast_audio_story_toggler.setDisabled(
            not get_always_start_with_audio_story_mode())

        self.audio_story_mode_label = QLabel("Audio Story Mode")
        self.audio_story_mode_label.setStyleSheet(FOOTER_LABEL_STYLESHEET)
        self.footer_layout.addWidget(self.audio_story_mode_label)

        self.audio_story_toggler = ToggleButton()
        self.audio_story_toggler.setFixedSize(50, 25)
        self.audio_story_toggler.setCursor(Qt.CursorShape.PointingHandCursor)
        self.audio_story_toggler.setChecked(
            get_always_start_with_audio_story_mode())
        self.audio_story_toggler.clicked.connect(
            self.audio_story_toggler_clicked)
        if get_always_start_with_audio_story_mode():
            self.audio_story_toggler_clicked()
        self.footer_layout.addWidget(self.audio_story_toggler)

        main_layout.addLayout(self.footer_layout)
        # Footer End ============================================

        container: QWidget = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def audio_story_download_clicked(self):
        output_path = get_audio_story_output_path()
        if get_always_ask_for_audio_story_output_path():
            output_path = QFileDialog.getExistingDirectory(
                self, "Select Directory", get_audio_story_output_path())
            if output_path == "":
                output_path = get_audio_story_output_path()
            if output_path == "":
                output_path = get_default_download_folder()
        if output_path:
            url_list = []
            for card in self.audio_story_list:
                if card.add_button.isHidden():
                    url_list.append(card.video.video_url)
            if len(url_list) > 0:
                title = self.audio_story_name_input.text()
                if len(title) > 0:
                    title = sanitize_filename(title) + ".mp3"
                else:
                    title = None
                audio_story = AudioStory(
                    url_list,
                    "Queued",
                    datetime.now(),
                    output_path,
                    title
                )
                audio_story_card = AudioStoryCard(audio_story, self)
                self.download_list.append(audio_story_card)
                self.download_list_layout.insertWidget(0, audio_story_card.audio_story_box)
                self.clear_audio_story_list()

    def delete_audio_story_card(self, card: AudioStoryCard):
        self.download_list_layout.removeWidget(card.audio_story_box)
        card.audio_story_box.setParent(None)
        card.audio_story_box.deleteLater()
        self.download_list.remove(card)

    def audio_story_toggler_clicked(self):
        if self.audio_story_toggler.isChecked():
            self.search_result.clear()
            self.update_carousel()
            self.audio_story_widget.show()
            self.fast_audio_story_mode_label.setDisabled(False)
            self.fast_audio_story_toggler.setDisabled(False)
            self.url_input.setMinimumSize(500, 150)
            self.search_button.setMinimumSize(100, 150)
            self.search_cancel_button.setMinimumSize(100, 150)
            self.loading_label.setFixedSize(100, 150)
            self.search_button.setText("Add")
            self.url_input.setPlaceholderText("Drag and Drop URL here ")
        else:
            self.audio_story_widget.hide()
            self.fast_audio_story_mode_label.setDisabled(True)
            self.fast_audio_story_toggler.setDisabled(True)
            self.url_input.setMinimumSize(500, 50)
            self.search_button.setMinimumSize(100, 50)
            self.search_cancel_button.setMinimumSize(100, 50)
            self.loading_label.setFixedSize(100, 50)
            self.search_button.setText("Search")
            self.url_input.setPlaceholderText(
                "Enter Youtube URL or Search Videos...")

    def audio_story_searched(self):
        search_text: str = self.url_input.text()
        if is_youtube_url(search_text):
            found = False
            for card in self.audio_story_list:
                if card.video.video_url == search_text:
                    found = True
                    break
            if not found:
                if self.search_thread and self.search_thread.isRunning():
                    self.search_thread.terminate()
                if self.search_thread and self.search_thread.isRunning():
                    self.search_thread.terminate()
                self.search_thread = SearchThread(
                    search_text, Consts.Constanats.TOTAL_ELEMENT_FOR_CAROUSEL)
                self.search_thread.search_finished.connect(
                    self.audio_story_video_info_found)
                self.search_thread.start()
            else:
                self.audio_story_video_info_found([])

    def audio_story_video_info_found(self, result_list):
        if len(result_list) > 0:
            video: Video = result_list[0]
            self.add_to_audio_list(video)
        self.url_input.setDisabled(False)
        self.url_input.setText("")
        self.search_button.setHidden(False)
        self.loading_label.setVisible(False)
        self.search_cancel_button.setHidden(True)

    def clear_audio_story_list(self):
        for card in self.audio_story_list:
            self.audio_story_scroll_layout.removeWidget(card.playlist_box)
            card.playlist_box.setParent(None)
            card.playlist_box.deleteLater()
        self.audio_story_list.clear()
        self.audio_story_name_input.setText("")

    def add_to_audio_list(self, video: Video):
        self.audio_story_list.append(AudioStoryPreviewCard(video, self))
        self.audio_story_scroll_layout.insertWidget(
            len(self.audio_story_list) - 1, self.audio_story_list[-1].playlist_box)

    def cancel_search_clicked(self):
        if self.search_thread and self.search_thread.isRunning():
            self.search_thread.terminate()
        if self.search_playlist_thread and self.search_playlist_thread.isRunning():
            self.search_playlist_thread.terminate()
        self.url_input.setDisabled(False)
        self.search_button.setHidden(False)
        self.loading_label.setVisible(False)
        self.search_cancel_button.setHidden(True)
        self.clear_playlist()
        self.playlist_widget.setHidden(True)

    def playlist_download_clicked(self, index: int):
        if index >= 0:
            playlist: List[PlaylistCard] = []
            if get_ask_for_playlist_output_path():
                output_path = QFileDialog.getExistingDirectory(
                    self, "Select Directory", get_playlist_output_path())
                if output_path == "":
                    output_path = get_playlist_output_path()
                if output_path == "":
                    output_path = get_default_download_folder()
            else:
                output_path = get_playlist_output_path()
                if output_path == "":
                    output_path = get_default_download_folder()
            for card in self.playlist_list:
                if card.add_button.isHidden():
                    playlist.insert(0, card)
            if index == 0:
                for card in playlist:
                    best_res = None
                    best_abr = -1
                    for res in card.video.resolution_list:
                        if res.file_type == "audio" and res.abr > best_abr:
                            best_abr = res.abr
                            best_res = res
                    if best_res:
                        self.start_download(
                            card.video, 0, best_res, output_path)
            elif index == 1:
                for card in playlist:
                    best_height = 0
                    best_res = None
                    for res in card.video.resolution_list:
                        if res.file_type == "mix" and res.height > best_height:
                            best_height = res.height
                            best_res = res
                    if best_res:
                        self.start_download(
                            card.video, 0, best_res, output_path)
            elif index == 2:
                for card in playlist:
                    best_height_vbr = 0
                    best_res = None
                    for res in card.video.resolution_list:
                        if res.file_type == "video" and res.vbr > best_height_vbr:
                            best_height_vbr = res.vbr
                            best_res = res
                    if best_res:
                        self.start_download(
                            card.video, 0, best_res, output_path)
            elif index == 3:
                for card in playlist:
                    best_height_vbr = 0
                    best_res = None
                    for res in card.video.resolution_list:
                        if res.file_type == "video" and res.vbr > best_height_vbr:
                            best_height_vbr = res.vbr
                            best_res = res
                    if best_res:
                        self.start_download(
                            card.video, 0, best_res, output_path, True)
            self.clear_playlist()

    def clear_playlist(self):
        self.playlist_progress.setValue(0)
        self.playlist_progress.setHidden(True)
        for card in self.playlist_list:
            self.playlist_scroll_layout.removeWidget(card.playlist_box)
            card.playlist_box.setParent(None)
            card.playlist_box.deleteLater()
        self.playlist_list.clear()

    def show_settings_window(self):
        settings_window = SettingsWindow(self)
        settings_window.exec()

    def delete_card(self, card: Card):
        self.download_list_layout.removeWidget(card.download_box)
        card.download_box.setParent(None)
        card.download_box.deleteLater()
        self.download_list.remove(card)

    def download_list_viewer(self, video: File):
        print(video.title)
        card: Card = Card(video, self.currently_downloading_count, self)
        self.download_list.append(card)
        self.download_list_layout.insertWidget(0, card.download_box)

    def search_clicked(self):
        self.search_result = []
        self.array_changed.emit()
        self.clear_playlist()
        self.playlist_widget.setHidden(True)
        search_text: str = self.url_input.text()
        if len(search_text) > 0:
            self.search_button.setHidden(True)
            self.search_cancel_button.setHidden(False)
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
            elif self.audio_story_toggler.isChecked():
                if is_youtube_url(search_text):
                    self.audio_story_searched()
                else:
                    self.audio_story_video_info_found([])
            else:
                if self.search_thread and self.search_thread.isRunning():
                    self.search_thread.terminate()
                self.search_thread = SearchThread(
                    search_text, Consts.Constanats.TOTAL_ELEMENT_FOR_CAROUSEL)
                self.search_thread.search_finished.connect(
                    self.on_search_finished)
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
        self.search_cancel_button.setHidden(True)
        self.array_changed.emit()

    def on_playlist_search_finished(self, result_list):
        if len(result_list) == 0:
            self.clear_playlist()
            self.playlist_progress.setValue(0)
            self.playlist_progress.setHidden(True)
            self.url_input.setDisabled(False)
            self.search_button.setHidden(False)
            self.loading_label.setVisible(False)
            self.playlist_widget.setHidden(True)
            return
        self.playlist_progress.setHidden(True)
        self.url_input.setDisabled(False)
        self.search_cancel_button.setHidden(True)
        self.search_button.setHidden(False)
        self.loading_label.setVisible(False)
        idx = 0
        for video in result_list:
            self.playlist_list.append(PlaylistCard(video, self))
            self.playlist_scroll_layout.insertWidget(
                idx, self.playlist_list[-1].playlist_box)
            idx += 1
        self.playlist_scroll_layout.addStretch()

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
