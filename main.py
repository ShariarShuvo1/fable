import math
import sys
import webbrowser
from datetime import datetime
from typing import List

from PyQt6.QtCore import Qt, QEvent, QSize, pyqtSignal
from PyQt6.QtGui import QGuiApplication, QIcon, QPixmap, QMovie
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, \
    QLabel, QComboBox, QMessageBox, QProgressBar, QScrollArea, QFileDialog, QSplitter, QSpinBox, QCheckBox

from Entity.AboutMe import AboutMe
from Entity.AudioStory import AudioStory
from Entity.AudioStoryCard import AudioStoryCard
from Entity.AudioStoryPreviewCard import AudioStoryPreviewCard
from Entity.AudioStoryPreviewCardFastMode import AudioStoryPreviewCardFastMode
from Entity.Card import Card
from Entity.ChannelVideoPreviewCard import ChannelVideoPreviewCard
from Entity.MyWidget import MyWidget
from Entity.PlaylistCard import PlaylistCard
from Entity.Resolution import Resolution
from Entity.ToggleButton import ToggleButton
from Entity.Video import Video
from Entity.File import File
from Entity.VideoViewer import VideoViewer
from Functions.SanitizeFilename import *
from Functions.youtube_url_checker import *
from Resource.audio_story_channel import AUDIO_STORY_CHANNEL
from Resource.bracu import BRACU_COURSE_DATA
from Styles.AudioStyleCardStyle import CLEAR_ALL_BUTTON_STYLESHEET, AUDIO_STORY_DOWNLOAD_BUTTON_STYLESHEET
from Styles.BRACU_STYLE import LOAD_BUTTON_STYLESHEET, OPEN_BROWSER_BUTTON_STYLESHEET
from Styles.PlaylistStyle import PLAYLIST_PROGRESS_STYLESHEET
from Styles.SearchStyle import *
from Styles.CarouselStyle import *
from Styles.DownloadListStyle import *
from Styles.FooterStyle import *
import Consts.Constanats
from Consts.SettingsData import *
from Styles.SettingsStyle import OUTPUT_PATH_LABEL_STYLE
from Threads.ChannelSearchThread import ChannelSearchThread
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


def thumbnail_clicked(video: Video):
    viewer = VideoViewer(video)
    viewer.exec()


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
                        msg_box.setWindowIcon(QIcon("./Assets/logo.png"))
                        msg_box.setIcon(QMessageBox.Icon.Question)
                        remember_checkbox = QCheckBox("Remember my choice")
                        msg_box.setCheckBox(remember_checkbox)
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
                        if remember_checkbox.isChecked():
                            if response == QMessageBox.StandardButton.Yes:
                                set_add_music(True)
                            else:
                                set_add_music(False)
                            set_always_ask_to_add_music(False)
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

    def get_queue_size(self):
        count = 0
        for card in self.download_list:
            if isinstance(card, Card):
                if card.video.status == "Queued":
                    count += 1
            elif isinstance(card, AudioStoryCard) and not card.play_button.isHidden():
                if card.audio_story.status == "Queued":
                    count += 1
        return count

    def download_complete_in_card(self, initial_call=False):
        if not initial_call:
            self.currently_downloading_count -= 1
        if get_maximum_simultaneous_downloads() == -1:
            for card in self.download_list:
                if isinstance(card, Card):
                    if card.video.status == "Queued":
                        card.start_download()
                        self.currently_downloading_count += 1
                elif isinstance(card, AudioStoryCard) and not card.play_button.isHidden():
                    if card.audio_story.status == "Queued":
                        card.begin_download()
                        self.currently_downloading_count += 1
        else:
            while self.currently_downloading_count < get_maximum_simultaneous_downloads():
                for card in self.download_list:
                    if isinstance(card, Card):
                        if card.video.status == "Queued":
                            card.start_download()
                            self.currently_downloading_count += 1
                            break
                    elif isinstance(card, AudioStoryCard) and not card.play_button.isHidden():
                        if card.audio_story.status == "Queued":
                            card.begin_download()
                            self.currently_downloading_count += 1
                            break
                if self.get_queue_size() == 0:
                    break

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

        self.audio_story_list: List[AudioStoryPreviewCard |
                                    AudioStoryPreviewCardFastMode] = []

        self.channel_video_list: List[ChannelVideoPreviewCard] = []

        self.setWindowTitle("Fable")
        self.setStyleSheet(WINDOW_STYLESHEET)
        self.setWindowIcon(QIcon("./Assets/logo.png"))

        main_layout: QVBoxLayout = QVBoxLayout()

        self.splitter = QSplitter()
        self.splitter.setHandleWidth(5)
        self.splitter.setStyleSheet(SPLITTER_STYLESHEET)
        self.splitter.setOrientation(Qt.Orientation.Vertical)

        # Search Widget Began ========================================
        url_layout: QHBoxLayout = QHBoxLayout()

        self.url_input: QLineEdit = QLineEdit()
        self.url_input.setToolTip("Enter Youtube URL or Search Videos...")
        self.url_input.setPlaceholderText(
            "Enter Youtube URL or Search Videos...")
        self.url_input.setMinimumSize(500, 50)
        self.url_input.setClearButtonEnabled(True)
        self.url_input.setStyleSheet(URL_INPUT_STYLESHEET)
        self.url_input.installEventFilter(self)
        url_layout.addWidget(self.url_input)

        self.loading_label = QLabel()
        self.loading_label.setToolTip("Searching...")
        self.loading_label.setStyleSheet(LOADING_BUTTON_STYLESHEET)
        self.loading_label.setFixedSize(100, 50)
        self.loading_label.setVisible(False)
        movie = QMovie("./Assets/Icons/loading.gif")
        self.loading_label.setMovie(movie)
        movie.start()
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        url_layout.addWidget(self.loading_label)

        self.search_cancel_button: QPushButton = QPushButton("Cancel")
        self.search_cancel_button.setToolTip("Cancel Search")
        self.search_cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.search_cancel_button.setMinimumSize(100, 50)
        self.search_cancel_button.setStyleSheet(CANCEL_BUTTON_STYLESHEET)
        self.search_cancel_button.clicked.connect(self.cancel_search_clicked)
        self.search_cancel_button.setHidden(True)
        url_layout.addWidget(self.search_cancel_button)

        self.search_button: QPushButton = QPushButton()
        self.search_button.setToolTip("Search")
        self.search_button.setIcon(QIcon("./Assets/Icons/search-icon.png"))
        self.search_button.setIconSize(QSize(40, 40))
        self.search_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.search_button.setMinimumSize(100, 50)
        self.search_button.setStyleSheet(SEARCH_BUTTON_STYLESHEET)
        self.search_button.clicked.connect(self.search_clicked)
        url_layout.addWidget(self.search_button)

        self.direct_download_button: QPushButton = QPushButton()
        self.direct_download_button.setToolTip(
            "Direct Download single Audio Story")
        self.direct_download_button.setIcon(
            QIcon("./Assets/Icons/search-single-download-icon.png"))
        self.direct_download_button.setIconSize(QSize(90, 90))
        self.direct_download_button.setCursor(
            Qt.CursorShape.PointingHandCursor)
        self.direct_download_button.setMinimumSize(100, 150)
        self.direct_download_button.setStyleSheet(
            DIRECT_DOWNLOAD_BUTTON_STYLESHEET)
        self.direct_download_button.clicked.connect(
            lambda checked: self.audio_story_download_clicked(True, self.url_input.text()))
        url_layout.addWidget(self.direct_download_button)
        self.direct_download_button.hide()

        main_layout.addLayout(url_layout)
        # Search Widget Finished ========================================

        # Search Result Began ============================================
        self.search_result_layout: QHBoxLayout = QHBoxLayout()

        self.prev_btn: QPushButton = QPushButton()
        self.prev_btn.setToolTip("View Previous")
        self.prev_btn.setMinimumSize(30, 120)
        self.prev_btn.setIcon(QIcon("./Assets/Icons/prev_icon.png"))
        self.prev_btn.setIconSize(QSize(25, 25))
        self.prev_btn.setStyleSheet(CAROUSEL_BUTTON_STYLESHEET)
        self.prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_btn.clicked.connect(self.show_previous)
        self.search_result_layout.addWidget(self.prev_btn)

        self.next_btn: QPushButton = QPushButton()
        self.next_btn.setToolTip("View Next")
        self.next_btn.setMinimumSize(30, 120)
        self.next_btn.setIcon(QIcon("./Assets/Icons/next_icon.png"))
        self.next_btn.setIconSize(QSize(25, 25))
        self.next_btn.setStyleSheet(CAROUSEL_BUTTON_STYLESHEET)
        self.next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_btn.clicked.connect(self.show_next)

        # Carousel of Boxes ============================================
        self.carousel_layout: QHBoxLayout = QHBoxLayout()
        self.carousel_layout.setContentsMargins(0, 0, 0, 0)
        self.carousel_layout.setSpacing(3)
        self.carousel_widget: MyWidget = MyWidget(self)
        self.current_index: int = 0
        self.update_carousel()
        self.carousel_widget.setLayout(self.carousel_layout)
        self.search_result_layout.addWidget(self.carousel_widget)
        # Carousel of Boxes ============================================

        self.search_result_layout.addWidget(self.next_btn)

        main_layout.addLayout(self.search_result_layout)
        # Search Result End ============================================

        # Audio Story Start ============================================
        self.audio_story_widget = QWidget()
        self.audio_story_widget.setMinimumWidth(500)
        self.audio_story_layout = QVBoxLayout()
        self.audio_story_layout.setContentsMargins(0, 0, 0, 0)

        self.audio_story_download_button = QPushButton("Download Selected")
        self.audio_story_download_button.setIcon(
            QIcon("./Assets/Icons/search-single-download-icon.png"))
        self.audio_story_download_button.setIconSize(QSize(30, 30))
        self.audio_story_download_button.setToolTip(
            "Download Selected Audio Stories")
        self.audio_story_download_button.setStyleSheet(
            AUDIO_STORY_DOWNLOAD_BUTTON_STYLESHEET)
        self.audio_story_download_button.setFixedHeight(50)
        self.audio_story_download_button.setCursor(
            Qt.CursorShape.PointingHandCursor)
        self.audio_story_download_button.clicked.connect(
            self.audio_story_download_clicked)

        self.audio_story_name_input = QLineEdit()
        self.audio_story_name_input.setToolTip("Enter Audio Story Name\nThis will be the name of the final Audio "
                                               "Story file\n If not provided, Title of the first video will be used")
        self.audio_story_name_input.setPlaceholderText(
            "Enter Audio Story Name (Optional)")
        self.audio_story_name_input.setStyleSheet(URL_INPUT_STYLESHEET)
        self.audio_story_name_input.setFixedHeight(50)
        self.audio_story_name_input.setMaximumWidth(350)

        self.audio_story_author_name_input = QLineEdit()
        self.audio_story_author_name_input.setToolTip("Enter Author Name\nThis will be the name of the final Audio "
                                                      "Story file\n If not provided, Channel name will be used")
        self.audio_story_author_name_input.setPlaceholderText(
            "Enter Author Name (Optional)")
        self.audio_story_author_name_input.setStyleSheet(URL_INPUT_STYLESHEET)
        self.audio_story_author_name_input.setFixedHeight(50)
        self.audio_story_author_name_input.setMaximumWidth(300)

        self.clear_audio_story_queue_button = QPushButton("Clear Queue")
        self.clear_audio_story_queue_button.setToolTip(
            "Clear All Audio Stories from the Queue")
        self.clear_audio_story_queue_button.setStyleSheet(
            CLEAR_ALL_BUTTON_STYLESHEET)
        self.clear_audio_story_queue_button.setFixedHeight(50)
        self.clear_audio_story_queue_button.setFixedWidth(120)
        self.clear_audio_story_queue_button.setCursor(
            Qt.CursorShape.PointingHandCursor)
        self.clear_audio_story_queue_button.clicked.connect(
            self.clear_audio_story_list)

        self.audio_story_top_row = QHBoxLayout()

        self.audio_story_top_row.addWidget(self.audio_story_name_input)
        self.audio_story_top_row.addWidget(self.audio_story_author_name_input)
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

        # Channel List Began ============================================

        self.channel_search_thread: ChannelSearchThread | None = None

        self.channel_list_widget = QWidget()
        self.channel_list_layout = QVBoxLayout()
        self.channel_list_layout.setContentsMargins(0, 0, 0, 0)

        self.channel_language_combo = QComboBox()
        self.channel_language_combo.setToolTip("Choose a Language")
        self.channel_language_combo.setCursor(
            Qt.CursorShape.PointingHandCursor)
        self.channel_language_combo.setMinimumHeight(40)
        self.channel_language_combo.setStyleSheet(
            RESOLUTION_COMBOBOX_STYLESHEET)
        self.channel_language_combo.setPlaceholderText("Choose a Language")
        self.channel_language_combo.currentIndexChanged.connect(
            self.channel_language_combo_changed)

        for language, channels in AUDIO_STORY_CHANNEL.items():
            self.channel_language_combo.addItem(language)

        self.channel_list_combo = QComboBox()
        self.channel_list_combo.setToolTip("Choose a Channel")
        self.channel_list_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.channel_list_combo.setMinimumHeight(40)
        self.channel_list_combo.setStyleSheet(RESOLUTION_COMBOBOX_STYLESHEET)
        self.channel_list_combo.setPlaceholderText("Choose a Channel")

        self.channel_search_begin = QSpinBox()
        self.channel_search_begin.setToolTip("Search Begin")
        self.channel_search_begin.setRange(1, 1000000)
        self.channel_search_begin.setValue(1)
        self.channel_search_begin.setMinimumWidth(100)
        self.channel_search_begin.setFixedHeight(40)
        self.channel_search_begin.setStyleSheet(OUTPUT_PATH_LABEL_STYLE)
        self.channel_search_begin.setPrefix("Start: ")
        self.channel_search_begin.setSingleStep(1)

        self.channel_search_end = QSpinBox()
        self.channel_search_end.installEventFilter(self)
        self.channel_search_end.setToolTip("Search End")
        self.channel_search_end.setRange(1, 1000000)
        self.channel_search_end.setValue(10)
        self.channel_search_end.setMinimumWidth(100)
        self.channel_search_end.setFixedHeight(40)
        self.channel_search_end.setStyleSheet(OUTPUT_PATH_LABEL_STYLE)
        self.channel_search_end.setPrefix("End: ")
        self.channel_search_end.setSingleStep(1)

        self.channel_load_button = QPushButton("Load")
        self.channel_load_button.setMinimumHeight(40)
        self.channel_load_button.setFixedWidth(100)
        self.channel_load_button.setToolTip("Load Channel")
        self.channel_load_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.channel_load_button.setStyleSheet(LOAD_BUTTON_STYLESHEET)
        self.channel_load_button.clicked.connect(self.load_channel_clicked)

        self.channel_search_progress = QProgressBar()
        self.channel_search_progress.setFixedHeight(30)
        self.channel_search_progress.setRange(0, 100)
        self.channel_search_progress.setValue(0)
        self.channel_search_progress.setStyleSheet(
            PLAYLIST_PROGRESS_STYLESHEET)
        self.channel_search_progress.setHidden(True)

        self.channel_top_row = QHBoxLayout()
        self.channel_top_row.addWidget(self.channel_language_combo)
        self.channel_top_row.addWidget(self.channel_list_combo)

        self.channel_mid_row = QHBoxLayout()
        self.channel_mid_row.addWidget(self.channel_search_begin)
        self.channel_mid_row.addWidget(self.channel_search_end)
        self.channel_mid_row.addWidget(self.channel_load_button)

        self.channel_list_layout.addLayout(self.channel_top_row)
        self.channel_list_layout.addLayout(self.channel_mid_row)
        self.channel_list_layout.addWidget(self.channel_search_progress)

        self.channel_scroll_area = QScrollArea()
        self.channel_scroll_area.setWidgetResizable(True)
        self.channel_scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.channel_scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.channel_scroll_area.setStyleSheet(SCROLL_AREA_STYLESHEET)

        self.channel_scroll_layout = QVBoxLayout()
        self.channel_scroll_layout.setSpacing(2)
        self.channel_scroll_layout.addStretch()

        self.channel_container = QWidget()
        self.channel_container.setLayout(self.channel_scroll_layout)
        self.channel_scroll_area.setWidget(self.channel_container)
        self.channel_list_layout.addWidget(self.channel_scroll_area)

        self.channel_list_widget.setLayout(self.channel_list_layout)

        # Channel List End ============================================

        self.audio_story_channel_splitter = QSplitter()
        self.audio_story_channel_splitter.setHandleWidth(5)
        self.audio_story_channel_splitter.setStyleSheet(SPLITTER_STYLESHEET)
        self.audio_story_channel_splitter.setOrientation(
            Qt.Orientation.Horizontal)
        self.audio_story_channel_splitter.addWidget(
            self.audio_story_scroll_area)
        self.audio_story_channel_splitter.addWidget(self.channel_list_widget)
        self.audio_story_channel_splitter.setSizes([1000, 500])

        self.audio_story_layout.addWidget(self.audio_story_channel_splitter)
        self.audio_story_widget.setLayout(self.audio_story_layout)
        self.audio_story_widget.setHidden(True)
        # Audio Story End ============================================

        # Download List Began ============================================
        self.main_body_widget = QWidget()
        self.main_body_frame = QHBoxLayout()
        self.main_body_frame.setContentsMargins(0, 0, 0, 0)
        self.main_body_frame.setSpacing(0)

        self.download_frame = QVBoxLayout()
        self.download_widget = QWidget()

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
        self.download_frame.setSpacing(0)
        self.download_frame.setContentsMargins(0, 0, 0, 0)
        self.download_widget.setLayout(self.download_frame)

        # Playlist Start ============================================
        self.playlist_widget = QWidget()
        self.playlist_widget.setMinimumWidth(500)
        self.playlist_layout = QVBoxLayout()
        self.playlist_layout.setContentsMargins(5, 0, 0, 0)

        # BRACU start =============================================

        self.bracu_course_combo = QComboBox()
        self.bracu_course_combo.setToolTip("Choose a Course")
        self.bracu_course_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.bracu_course_combo.setMinimumHeight(40)
        self.bracu_course_combo.setStyleSheet(RESOLUTION_COMBOBOX_STYLESHEET)
        self.bracu_course_combo.setPlaceholderText("Choose a Course")

        for course, info in BRACU_COURSE_DATA.items():
            self.bracu_course_combo.addItem(course)

        self.bracu_course_combo.currentIndexChanged.connect(
            self.bracu_course_combo_changed)

        self.bracu_faculty_combo = QComboBox()
        self.bracu_faculty_combo.setToolTip("Choose a Faculty")
        self.bracu_faculty_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.bracu_faculty_combo.setMinimumHeight(40)
        self.bracu_faculty_combo.setStyleSheet(RESOLUTION_COMBOBOX_STYLESHEET)
        self.bracu_faculty_combo.setPlaceholderText("Choose a Faculty")

        self.bracu_faculty_combo.currentIndexChanged.connect(
            self.bracu_faculty_combo_changed)

        self.bracu_playlist_combo = QComboBox()
        self.bracu_playlist_combo.setToolTip("Choose a Playlist")
        self.bracu_playlist_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.bracu_playlist_combo.setMinimumHeight(40)
        self.bracu_playlist_combo.setStyleSheet(RESOLUTION_COMBOBOX_STYLESHEET)
        self.bracu_playlist_combo.setPlaceholderText("Choose a Playlist")

        self.bracu_playlist_load_button = QPushButton("Load")
        self.bracu_playlist_load_button.setFixedWidth(100)
        self.bracu_playlist_load_button.setToolTip("Load Playlist")
        self.bracu_playlist_load_button.setCursor(
            Qt.CursorShape.PointingHandCursor)
        self.bracu_playlist_load_button.setMinimumHeight(40)
        self.bracu_playlist_load_button.setStyleSheet(LOAD_BUTTON_STYLESHEET)
        self.bracu_playlist_load_button.clicked.connect(self.load_clicked)

        self.bracu_open_browser_button = QPushButton()
        self.bracu_open_browser_button.setIcon(
            QIcon("./Assets/Icons/yt-icon.png"))
        self.bracu_open_browser_button.setIconSize(QSize(35, 35))
        self.bracu_open_browser_button.setToolTip("Open Playlist in Browser\n"
                                                  "Source: https://docs.google.com/spreadsheets/u/1/d/1_"
                                                  "wSiAzh9iBO2Dktt_V1rGAyJGvRRr-TQyUzuLPNmFSo/htmlview?fbclid="
                                                  "IwAR2WgOStJe2UrGIM2WMx9fzG6WqMAWbbeAQ9Xe3Z1DTJRFe1NM5dveZnKVM")
        # I do not own this spreadsheet. All credit goes to the owner for the spreadsheet
        self.bracu_open_browser_button.setCursor(
            Qt.CursorShape.PointingHandCursor)
        self.bracu_open_browser_button.setFixedSize(40, 40)
        self.bracu_open_browser_button.setStyleSheet(
            OPEN_BROWSER_BUTTON_STYLESHEET)
        self.bracu_open_browser_button.clicked.connect(
            self.bracu_open_browser_button_click)

        self.bracu_widget = QWidget()
        self.bracu_layout = QVBoxLayout()

        bracu_top_row = QHBoxLayout()
        bracu_top_row.addWidget(self.bracu_course_combo)
        bracu_top_row.addWidget(self.bracu_faculty_combo)

        bracu_bottom_row = QHBoxLayout()
        bracu_bottom_row.addWidget(self.bracu_playlist_combo)
        bracu_bottom_row.addWidget(self.bracu_playlist_load_button)
        bracu_bottom_row.addWidget(self.bracu_open_browser_button)

        self.bracu_layout.addLayout(bracu_top_row)
        self.bracu_layout.addLayout(bracu_bottom_row)

        self.bracu_widget.setLayout(self.bracu_layout)
        self.bracu_widget.hide()

        # BRACU end =============================================

        self.playlist_title = QLabel("Playlist")
        self.playlist_title.setStyleSheet(PLAYLIST_TITLE_STYLESHEET)
        self.playlist_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.playlist_title.setFixedHeight(50)
        self.playlist_layout.addWidget(self.playlist_title)
        self.playlist_layout.addWidget(self.bracu_widget)
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
        self.playlist_resolution_combo.setToolTip(
            "Choose Quality For Selected")
        self.playlist_resolution_combo.setDisabled(True)
        self.playlist_resolution_combo.setCursor(
            Qt.CursorShape.PointingHandCursor)
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
        self.playlist_download_button.setIcon(
            QIcon("./Assets/Icons/search-single-download-icon.png"))
        self.playlist_download_button.setIconSize(QSize(30, 30))
        self.playlist_download_button.setToolTip(
            "Download Selected Videos from the Playlist")
        self.playlist_download_button.setDisabled(True)
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

        self.download_playlist_splitter = QSplitter()
        self.download_playlist_splitter.setHandleWidth(5)
        self.download_playlist_splitter.setStyleSheet(SPLITTER_STYLESHEET)
        self.download_playlist_splitter.setOrientation(
            Qt.Orientation.Horizontal)
        self.download_playlist_splitter.addWidget(self.download_widget)
        self.download_playlist_splitter.addWidget(self.playlist_widget)
        self.download_playlist_splitter.setSizes([1000, 500])
        self.main_body_frame.addWidget(self.download_playlist_splitter)
        self.main_body_frame.setSpacing(0)
        self.main_body_frame.setContentsMargins(0, 0, 0, 0)

        # Playlist End ============================================
        self.main_body_widget.setLayout(self.main_body_frame)

        self.splitter.addWidget(self.audio_story_widget)
        self.splitter.addWidget(self.main_body_widget)

        main_layout.addWidget(self.splitter)
        # Download List End ============================================

        # Footer Start ============================================
        self.footer_layout = QHBoxLayout()
        self.settings = QPushButton()
        self.settings.setToolTip("Click to Open Settings")
        self.settings.setIcon(QIcon("./Assets/Icons/settings.png"))
        self.settings.setIconSize(QSize(30, 30))
        self.settings.setStyleSheet(FOOTER_STYLESHEET)
        self.settings.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings.clicked.connect(self.show_settings_window)
        self.footer_layout.addWidget(self.settings)

        github = QPushButton()
        github.setToolTip("Click to Open Source Code on Github")
        github.setIcon(QIcon("./Assets/Icons/github.png"))
        github.setIconSize(QSize(30, 30))

        github.setStyleSheet(FOOTER_STYLESHEET)
        github.setCursor(Qt.CursorShape.PointingHandCursor)
        github.clicked.connect(
            lambda: open_channel("https://github.com/ShariarShuvo1/fable"))
        self.footer_layout.addWidget(github)

        about_me = QPushButton()
        about_me.setToolTip("Click to know about the developer")
        about_me.setIcon(QIcon("./Assets/Icons/info-icon.png"))
        about_me.setIconSize(QSize(25, 25))
        about_me.setStyleSheet(ABOUT_ME_STYLESHEET)
        about_me.setCursor(Qt.CursorShape.PointingHandCursor)
        about_me.clicked.connect(
            lambda: self.about_me_clicked())
        self.footer_layout.addWidget(about_me)

        self.footer_layout.addStretch()

        self.fast_audio_story_mode_label = QLabel("Fast Mode")
        self.fast_audio_story_mode_label.setToolTip("In fast mode there is no delay during searching\n"
                                                    "However, preview will be unavailable")
        self.fast_audio_story_mode_label.setStyleSheet(FOOTER_LABEL_STYLESHEET)
        self.footer_layout.addWidget(self.fast_audio_story_mode_label)

        self.fast_audio_story_toggler = ToggleButton()
        self.fast_audio_story_toggler.setToolTip("In fast mode there is no delay during searching\n"
                                                 "However, preview will be unavailable")
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
        self.fast_audio_story_toggler.clicked.connect(
            self.fast_audio_story_toggler_clicked)
        self.fast_audio_story_toggler_clicked()

        self.audio_story_mode_label = QLabel("Audio Story Mode")
        self.audio_story_mode_label.setToolTip(
            "Turn on Audio Story Download Mode")
        self.audio_story_mode_label.setStyleSheet(FOOTER_LABEL_STYLESHEET)
        self.footer_layout.addWidget(self.audio_story_mode_label)

        self.audio_story_toggler = ToggleButton()
        self.audio_story_toggler.setToolTip(
            "Turn on Audio Story Download Mode")
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

    def about_me_clicked(self):
        about_me = AboutMe()
        about_me.exec()

    def clear_channel_video_list(self):
        if self.channel_search_thread is not None and self.channel_search_thread.isRunning():
            self.channel_search_thread.terminate()
        for card in self.channel_video_list:
            self.channel_scroll_layout.removeWidget(card.playlist_box)
            card.playlist_box.deleteLater()
        self.channel_video_list.clear()
        self.channel_search_progress.setValue(0)
        self.channel_search_progress.setHidden(True)

    def load_channel_clicked(self):
        if self.channel_language_combo.currentIndex() >= 0 and self.channel_list_combo.currentIndex() >= 0:
            if self.channel_search_thread is not None and self.channel_search_thread.isRunning():
                msg_box = QMessageBox()
                msg_box.setWindowIcon(QIcon("./Assets/logo.png"))
                msg_box.setIcon(QMessageBox.Icon.Warning)
                msg_box.setText(
                    "A search is already in progress\n Are you sure you want to cancel it?")
                msg_box.setWindowTitle("Search in Progress")
                msg_box.setStandardButtons(
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                msg_box.setDefaultButton(QMessageBox.StandardButton.No)
                response = msg_box.exec()
                if response == QMessageBox.StandardButton.Yes:
                    self.clear_channel_video_list()
                else:
                    return
            else:
                self.clear_channel_video_list()
            self.channel_search_progress.setValue(0)
            self.channel_search_progress.setHidden(False)
            self.channel_search_progress.setRange(0,
                                                  self.channel_search_end.value() - self.channel_search_begin.value() + 1)
            url = AUDIO_STORY_CHANNEL[self.channel_language_combo.currentText(
            )][self.channel_list_combo.currentText()]
            self.channel_search_thread = ChannelSearchThread(
                url,
                self.channel_search_begin.value(),
                self.channel_search_end.value()
            )
            self.channel_search_thread.search_finished.connect(
                self.on_channel_search_finished)
            self.channel_search_thread.found_one.connect(
                self.found_one_channel)
            self.channel_search_thread.start()

    def found_one_channel(self, result: list[Video]):
        self.channel_search_progress.setValue(
            self.channel_search_progress.value() + 1)
        if len(result) > 1:
            number = result[1]
            self.channel_video_list.append(
                ChannelVideoPreviewCard(result[0], self, number))
            self.channel_scroll_layout.insertWidget(
                len(self.channel_video_list) - 1, self.channel_video_list[-1].playlist_box)

    def on_channel_search_finished(self):
        self.channel_search_progress.setHidden(True)

    def fast_audio_story_toggler_clicked(self):
        if self.fast_audio_story_toggler.isChecked():
            self.channel_list_widget.hide()
        else:
            self.channel_list_widget.show()

    def channel_language_combo_changed(self, index):
        self.channel_list_combo.clear()
        language = self.channel_language_combo.currentText()
        for channel in AUDIO_STORY_CHANNEL[language]:
            self.channel_list_combo.addItem(channel)

    def bracu_open_browser_button_click(self):
        if self.bracu_playlist_combo.currentIndex() >= 0 and self.bracu_faculty_combo.currentIndex() >= 0 and self.bracu_course_combo.currentIndex() >= 0:
            open_channel(BRACU_COURSE_DATA[self.bracu_course_combo.currentText(
            )][self.bracu_faculty_combo.currentText()][self.bracu_playlist_combo.currentText()])

    def load_clicked(self):
        if self.bracu_playlist_combo.currentIndex() >= 0 and self.bracu_faculty_combo.currentIndex() >= 0 and self.bracu_course_combo.currentIndex() >= 0:
            if self.search_thread and self.search_thread.isRunning():
                self.search_thread.terminate()
            if self.search_playlist_thread and self.search_playlist_thread.isRunning():
                self.search_playlist_thread.terminate()
            self.url_input.setDisabled(False)
            self.search_button.setHidden(False)
            self.loading_label.setVisible(False)
            self.search_cancel_button.setHidden(True)
            self.clear_playlist()
            if self.audio_story_toggler.isChecked():
                self.direct_download_button.show()
            search_text = BRACU_COURSE_DATA[self.bracu_course_combo.currentText(
            )][self.bracu_faculty_combo.currentText()][self.bracu_playlist_combo.currentText()]
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

    def bracu_course_combo_changed(self, index):
        self.bracu_playlist_combo.clear()
        self.bracu_faculty_combo.disconnect()
        self.bracu_faculty_combo.clear()
        self.bracu_faculty_combo.currentIndexChanged.connect(
            self.bracu_faculty_combo_changed)
        course = self.bracu_course_combo.currentText()
        for faculty, info in BRACU_COURSE_DATA[course].items():
            self.bracu_faculty_combo.addItem(faculty)

    def bracu_faculty_combo_changed(self, index):
        course = self.bracu_course_combo.currentText()
        faculty = self.bracu_faculty_combo.currentText()
        self.bracu_playlist_combo.clear()
        for playlist in BRACU_COURSE_DATA[course][faculty]:
            self.bracu_playlist_combo.addItem(playlist)

    def audio_story_download_clicked(self, direct=False, url: str | None = None):
        if url is None or url == "":
            if direct and (len(self.url_input.text()) == 0 or not is_youtube_url(self.url_input.text())):
                return
            elif not direct and len(self.audio_story_list) == 0:
                return
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
            if direct:
                url_list.append(url)
            else:
                if not self.fast_audio_story_toggler.isChecked():
                    for card in self.audio_story_list:
                        if card.add_button.isHidden():
                            url_list.append(card.video.video_url)
                else:
                    for card in self.audio_story_list:
                        if card.add_button.isHidden():
                            url_list.append(card.url)
            if len(url_list) > 0:
                title = self.audio_story_name_input.text()
                if len(title) > 0:
                    title = sanitize_filename(title) + ".mp3"
                else:
                    title = None
                author = self.audio_story_author_name_input.text()
                if len(author) == 0:
                    author = None
                audio_story = AudioStory(
                    url_list,
                    "Queued",
                    datetime.now(),
                    output_path,
                    title,
                    author
                )
                for audio_story_card in self.download_list:
                    if isinstance(audio_story_card, AudioStoryCard):
                        if audio_story_card.audio_story.url_list == audio_story.url_list:
                            return
                audio_story_card = AudioStoryCard(audio_story, self)
                self.download_list.append(audio_story_card)
                self.download_list_layout.insertWidget(
                    0, audio_story_card.audio_story_box)
                self.download_complete_in_card(True)
                if not direct:
                    self.clear_audio_story_list()

    def delete_audio_story_card(self, card: AudioStoryCard):
        self.download_list_layout.removeWidget(card.audio_story_box)
        card.audio_story_box.setParent(None)
        card.audio_story_box.deleteLater()
        self.download_list.remove(card)

    def audio_story_toggler_clicked(self):
        self.cancel_search_clicked()
        self.clear_audio_story_list()
        if self.audio_story_toggler.isChecked():
            self.audio_story_toggler.setToolTip(
                "Turn off Audio Story Download Mode")
            self.audio_story_mode_label.setToolTip(
                "Turn off Audio Story Download Mode")
            self.playlist_widget.setHidden(True)
            self.clear_playlist()
            self.direct_download_button.show()
            self.search_result.clear()
            self.update_carousel()
            self.audio_story_widget.show()
            self.fast_audio_story_mode_label.setDisabled(False)
            self.fast_audio_story_toggler.setDisabled(False)
            self.url_input.setMinimumSize(500, 150)
            self.search_button.setMinimumSize(100, 150)
            self.search_cancel_button.setMinimumSize(100, 150)
            self.loading_label.setFixedSize(100, 150)
            self.search_button.setIcon(
                QIcon("./Assets/Icons/search-add-icon.png"))
            self.search_button.setIconSize(QSize(90, 90))
            self.search_button.setToolTip("Add to Queue")
            self.url_input.setPlaceholderText("Drag and Drop URL here ")
        else:
            self.audio_story_mode_label.setToolTip(
                "Turn on Audio Story Download Mode")
            self.audio_story_toggler.setToolTip(
                "Turn on Audio Story Download Mode")
            self.direct_download_button.hide()
            self.audio_story_widget.hide()
            self.fast_audio_story_mode_label.setDisabled(True)
            self.fast_audio_story_toggler.setDisabled(True)
            self.url_input.setMinimumSize(500, 50)
            self.search_button.setMinimumSize(100, 50)
            self.search_cancel_button.setMinimumSize(100, 50)
            self.loading_label.setFixedSize(100, 50)
            self.search_button.setIcon(QIcon("./Assets/Icons/search-icon.png"))
            self.search_button.setIconSize(QSize(40, 40))
            self.search_button.setToolTip("Search")
            self.url_input.setPlaceholderText(
                "Enter Youtube URL or Search Videos...")

    def audio_story_searched(self):
        search_text: str = self.url_input.text()
        if is_youtube_url(search_text):
            found = False
            for card in self.audio_story_list:
                if isinstance(card, AudioStoryPreviewCard):
                    if card.video.video_url == search_text:
                        found = True
                        break
                elif isinstance(card, AudioStoryPreviewCardFastMode):
                    if card.url == search_text:
                        found = True
                        break
            if not found:
                self.fast_audio_story_toggler.setDisabled(True)
                self.direct_download_button.hide()
                if not self.fast_audio_story_toggler.isChecked():
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
                    self.add_to_audio_list_fast_mode(search_text)
            else:
                self.audio_story_video_info_found([])

    def audio_story_video_info_found(self, result_list):
        if len(result_list) > 0:
            video: Video = result_list[0]
            self.add_to_audio_list(video)
        if len(self.audio_story_scroll_layout) == 1:
            self.fast_audio_story_toggler.setDisabled(False)
        else:
            self.fast_audio_story_toggler.setDisabled(True)
        self.url_input.setDisabled(False)
        self.url_input.setText("")
        self.search_button.setHidden(False)
        self.loading_label.setVisible(False)
        self.search_cancel_button.setHidden(True)
        self.direct_download_button.show()

    def clear_audio_story_list(self):
        for card in self.audio_story_list:
            self.audio_story_scroll_layout.removeWidget(card.playlist_box)
            card.playlist_box.setParent(None)
            card.playlist_box.deleteLater()
        self.audio_story_list.clear()
        self.audio_story_name_input.setText("")
        self.fast_audio_story_toggler.setDisabled(False)

    def add_to_audio_list_fast_mode(self, url: str):
        self.fast_audio_story_toggler.setDisabled(True)
        self.audio_story_list.append(AudioStoryPreviewCardFastMode(url, self))
        self.audio_story_scroll_layout.insertWidget(
            len(self.audio_story_list) - 1, self.audio_story_list[-1].playlist_box)

    def add_to_audio_list(self, video: Video):
        found = False
        for card in self.audio_story_list:
            if isinstance(card, AudioStoryPreviewCard):
                if card.video.video_url == video.video_url:
                    found = True
                    break
            elif isinstance(card, AudioStoryPreviewCardFastMode):
                if card.url == video.video_url:
                    found = True
                    break
        if not found:
            self.fast_audio_story_toggler.setDisabled(True)
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
        self.bracu_widget.hide()
        self.playlist_title.setText("Playlist")
        self.playlist_title.setStyleSheet(PLAYLIST_TITLE_STYLESHEET)
        self.playlist_widget.setHidden(True)
        if self.audio_story_toggler.isChecked():
            self.direct_download_button.show()

    def playlist_download_clicked(self, index: int):
        if index >= 0:
            self.playlist_widget.setHidden(True)
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
        self.playlist_resolution_combo.setDisabled(True)
        self.playlist_resolution_combo.setCurrentIndex(-1)
        self.playlist_download_button.setDisabled(True)
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
        card: Card = Card(video, self.currently_downloading_count, self)
        self.download_list.append(card)
        self.download_list_layout.insertWidget(0, card.download_box)
        self.download_complete_in_card(True)

    def search_clicked(self):
        self.current_index = 0
        self.bracu_widget.hide()
        self.playlist_title.setText("Playlist")
        self.playlist_title.setStyleSheet(PLAYLIST_TITLE_STYLESHEET)
        self.search_result = []
        self.array_changed.emit()
        self.clear_playlist()
        self.playlist_widget.setHidden(True)
        search_text: str = self.url_input.text()
        if search_text.upper() == "BRACU" and not self.audio_story_toggler.isChecked():
            self.playlist_title.setText("BRACU Playlist")
            self.playlist_title.setStyleSheet(BRACU_PLAYLIST_TITLE_STYLESHEET)
            self.bracu_widget.show()
            self.playlist_widget.show()
            return
        if len(search_text) > 0:
            self.search_button.setHidden(True)
            self.search_cancel_button.setHidden(False)
            self.url_input.setDisabled(True)
            self.loading_label.setVisible(True)
            if is_youtube_playlist(search_text) and not self.audio_story_toggler.isChecked():
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
                    search_text, get_maximum_search_results())
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
        self.playlist_resolution_combo.setDisabled(False)
        self.playlist_download_button.setDisabled(False)
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
            carousel_box.setStyleSheet(CAROUSEL_BOX_STYLESHEET)
            inside_carousel_layout = QVBoxLayout()
            inside_carousel_layout.setContentsMargins(3, 3, 3, 3)
            inside_carousel_layout.setSpacing(1)

            first_row = QHBoxLayout()
            first_row.setContentsMargins(0, 0, 0, 0)
            first_row.setSpacing(0)

            thumbnail_label = QLabel()
            thumbnail_label.setCursor(Qt.CursorShape.PointingHandCursor)
            thumbnail_label.setToolTip("Click for preview")
            thumbnail_label.mousePressEvent = lambda event, video=current_video: thumbnail_clicked(
                video)
            thumbnail_label.setFixedHeight(90)
            thumbnail_label.setStyleSheet(CAROUSEL_THUMBNAIL_STYLESHEET)
            pixmap = QPixmap()
            pixmap.loadFromData(current_video.thumbnail.content)
            pixmap = pixmap.scaled(120, 90, Qt.AspectRatioMode.KeepAspectRatio)
            thumbnail_label.setPixmap(pixmap)
            thumbnail_label.setFixedSize(120, 90)
            thumbnail_label.setScaledContents(True)
            first_row.addWidget(thumbnail_label)

            resolution_layout = QVBoxLayout()

            resolution_combo = QComboBox()
            resolution_combo.setToolTip("Choose Quality to Download")
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
            download_selected_res.setIcon(
                QIcon("./Assets/Icons/search-single-download-icon.png"))
            download_selected_res.setIconSize(QSize(30, 30))
            download_selected_res.setToolTip("Download Selected Quality")
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

            inside_carousel_layout.addLayout(first_row)
            title = QPushButton(current_video.title)
            title.setMaximumWidth(550)
            title.setToolTip(current_video.title)
            title.setStyleSheet(CAROUSEL_TITLE_BUTTON_STYLESHEET)
            title.setCursor(Qt.CursorShape.PointingHandCursor)
            title.clicked.connect(
                lambda: open_channel(current_video.video_url))
            inside_carousel_layout.addWidget(title)

            channel = QPushButton(current_video.uploader)
            channel.setToolTip(
                f"Channel: {current_video.uploader}\nClick to Open Channel")
            channel.setCursor(Qt.CursorShape.PointingHandCursor)
            channel.setStyleSheet(CAROUSEL_CHANNEL_STYLESHEET)
            channel.clicked.connect(
                lambda: open_channel(current_video.channel_url))
            inside_carousel_layout.addWidget(channel)
            views = QLabel(
                f"Views: {format_view_count(current_video.view_count)}")
            views.setStyleSheet(CAROUSEL_GENERAL_DATA_STYLESHEET)

            duration = QLabel(
                f"Duration: {format_duration(current_video.duration)}")
            duration.setStyleSheet(CAROUSEL_GENERAL_DATA_STYLESHEET)
            extra_info_layout = QHBoxLayout()
            extra_info_layout.addWidget(views)
            extra_info_layout.addSpacing(10)
            extra_info_layout.addWidget(duration)
            extra_info_layout.addStretch()
            inside_carousel_layout.addLayout(extra_info_layout)
            carousel_box.setLayout(inside_carousel_layout)
            self.carousel_layout.addWidget(carousel_box)

    def show_previous(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_carousel()

    def show_next(self):
        if (
                (self.current_index + Consts.Constanats.NUMBER_OF_ELEMENT_FOR_CAROUSEL) <
                get_maximum_search_results()
        ):
            self.current_index += 1
            self.update_carousel()

    def eventFilter(self, obj, event):
        if obj is self.channel_search_end or obj is self.channel_search_begin:
            if event.type() == QEvent.Type.KeyPress:
                key_event = event
                if key_event.key() == 16777220:
                    self.load_channel_clicked()
        if obj is self.url_input:
            if event.type() == QEvent.Type.FocusIn:
                clipboard_text: str = QApplication.clipboard().text()
                if is_youtube_url(clipboard_text) or is_youtube_playlist(clipboard_text):
                    self.url_input.setPlaceholderText(
                        f"{clipboard_text}    press [TAB] to paste")
                else:
                    if self.audio_story_toggler.isChecked():
                        self.url_input.setPlaceholderText(
                            "Drag and Drop URL here ")
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
                elif key_event.button() == Qt.MouseButton.LeftButton and self.fast_audio_story_toggler.isChecked() and self.audio_story_toggler.isChecked():
                    clipboard_text: str = QApplication.clipboard().text()
                    if clipboard_text not in self.url_input.text() and is_youtube_url(clipboard_text):
                        self.url_input.setText(clipboard_text)
                        self.search_clicked()
                        return True
            elif event.type() == QEvent.Type.FocusOut:
                if self.audio_story_toggler.isChecked():
                    self.url_input.setPlaceholderText(
                        "Drag and Drop URL here ")
                else:
                    self.url_input.setPlaceholderText(
                        "Enter Youtube URL or Search Videos...")
        return super().eventFilter(obj, event)


if __name__ == "__main__":
    app: QApplication = QApplication(sys.argv)

    primary_screen = QGuiApplication.primaryScreen().availableGeometry()
    Consts.Constanats.SCREEN_WIDTH = primary_screen.width()
    Consts.Constanats.SCREEN_HEIGHT = primary_screen.height()

    window: MainWindow = MainWindow()
    window.showMaximized()
    window.show()
    sys.exit(app.exec())
