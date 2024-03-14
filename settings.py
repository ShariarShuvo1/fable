from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon, QIntValidator, QFont
from PyQt6.QtWidgets import QDialog, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QRadioButton, QButtonGroup, \
    QFileDialog, QCheckBox, QLineEdit, QSpinBox, QComboBox

from Styles.CarouselStyle import RESOLUTION_COMBOBOX_STYLESHEET
from Styles.SettingsStyle import *
from Consts.SettingsData import *


class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumSize(800, 400)
        self.setMaximumSize(1100, 700)
        self.layout = QVBoxLayout()

        self.output_combo_label = QLabel("Download path: ")
        self.output_combo_label.setStyleSheet(SETTINGS_LABEL_STYLE)

        self.output_path_combo = QComboBox()
        self.output_path_combo.setMinimumHeight(40)
        self.output_path_combo.setStyleSheet(RESOLUTION_COMBOBOX_STYLESHEET)
        self.output_path_combo.setCursor(Qt.CursorShape.PointingHandCursor)

        self.output_path_combo.addItem("Always ask for download path")
        self.output_path_combo.addItem("Choose a default download path")
        self.output_path_combo.currentIndexChanged.connect(
            self.output_path_change)

        self.output_path_layout = QHBoxLayout()

        self.output_path_label = QLabel(f"Download path: {get_output_path()}")
        self.output_path_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.output_path_label.setStyleSheet(OUTPUT_PATH_LABEL_STYLE)

        self.output_path_button = QPushButton("Change")
        self.output_path_button.setIcon(
            QIcon("./Assets/Icons/folder-icon.png"))
        self.output_path_button.setIconSize(QSize(20, 20))
        self.output_path_button.clicked.connect(self.change_output_path)
        self.output_path_button.setStyleSheet(OUTPUT_PATH_BUTTON_STYLE)
        self.output_path_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.output_path_layout.addWidget(self.output_path_label)
        self.output_path_layout.addWidget(self.output_path_button)
        self.output_path_layout.addStretch()

        if get_ask_for_output_path():
            self.output_path_combo.setCurrentIndex(0)
            self.output_path_label.setHidden(True)
            self.output_path_button.setHidden(True)
        else:
            self.output_path_combo.setCurrentIndex(1)
            self.output_path_label.setHidden(False)
            self.output_path_button.setHidden(False)

        self.playlist_output_combo_label = QLabel("Playlist download path: ")
        self.playlist_output_combo_label.setStyleSheet(SETTINGS_LABEL_STYLE)

        self.playlist_output_path_combo = QComboBox()
        self.playlist_output_path_combo.setMinimumHeight(40)
        self.playlist_output_path_combo.setStyleSheet(
            RESOLUTION_COMBOBOX_STYLESHEET)
        self.playlist_output_path_combo.setCursor(
            Qt.CursorShape.PointingHandCursor)

        self.playlist_output_path_combo.addItem(
            "Always ask for playlist download path")
        self.playlist_output_path_combo.addItem(
            "Choose a default playlist download path")
        self.playlist_output_path_combo.currentIndexChanged.connect(
            self.playlist_output_path_change)

        self.playlist_output_path_layout = QHBoxLayout()

        self.playlist_output_path_label = QLabel(
            f"Playlist download path: {get_playlist_output_path()}")
        self.playlist_output_path_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter)
        self.playlist_output_path_label.setStyleSheet(OUTPUT_PATH_LABEL_STYLE)

        self.playlist_output_path_button = QPushButton("Change")
        self.playlist_output_path_button.setIcon(
            QIcon("./Assets/Icons/folder-icon.png"))
        self.playlist_output_path_button.setIconSize(QSize(20, 20))
        self.playlist_output_path_button.clicked.connect(
            self.change_playlist_output_path)
        self.playlist_output_path_button.setStyleSheet(
            OUTPUT_PATH_BUTTON_STYLE)
        self.playlist_output_path_button.setCursor(
            Qt.CursorShape.PointingHandCursor)

        self.playlist_output_path_layout.addWidget(
            self.playlist_output_path_label)
        self.playlist_output_path_layout.addWidget(
            self.playlist_output_path_button)
        self.playlist_output_path_layout.addStretch()

        if get_ask_for_playlist_output_path():
            self.playlist_output_path_combo.setCurrentIndex(0)
            self.playlist_output_path_label.setHidden(True)
            self.playlist_output_path_button.setHidden(True)
        else:
            self.playlist_output_path_combo.setCurrentIndex(1)
            self.playlist_output_path_label.setHidden(False)
            self.playlist_output_path_button.setHidden(False)

        self.add_music_combo_label = QLabel(
            "Add audio to video which does not have audio: ")
        self.add_music_combo_label.setStyleSheet(SETTINGS_LABEL_STYLE)

        self.add_music_combo = QComboBox()
        self.add_music_combo.setMinimumHeight(40)
        self.add_music_combo.setStyleSheet(RESOLUTION_COMBOBOX_STYLESHEET)
        self.add_music_combo.setCursor(Qt.CursorShape.PointingHandCursor)

        self.add_music_combo.addItem("Always ask to add music")
        self.add_music_combo.addItem("Never add music")
        self.add_music_combo.addItem("Always add music")
        if get_always_ask_to_add_music():
            self.add_music_combo.setCurrentIndex(0)
        elif get_add_music():
            self.add_music_combo.setCurrentIndex(2)
        else:
            self.add_music_combo.setCurrentIndex(1)
        self.add_music_combo.currentIndexChanged.connect(self.add_music_change)

        self.simultaneous_downloads_layout = QHBoxLayout()

        self.maximum_simultaneous_downloads_label = QLabel(
            "Maximum simultaneous downloads: ")
        self.maximum_simultaneous_downloads_label.setStyleSheet(
            OUTPUT_PATH_LABEL_STYLE)

        self.maximum_simultaneous_downloads_input = QSpinBox()
        self.maximum_simultaneous_downloads_input.setRange(-1, 1000)
        self.maximum_simultaneous_downloads_input.setValue(
            get_maximum_simultaneous_downloads())
        self.maximum_simultaneous_downloads_input.setMaximumWidth(100)
        self.maximum_simultaneous_downloads_input.setFixedHeight(30)
        self.maximum_simultaneous_downloads_input.setSingleStep(1)
        self.maximum_simultaneous_downloads_input.setStyleSheet(
            OUTPUT_PATH_LABEL_STYLE)
        self.maximum_simultaneous_downloads_input.textChanged.connect(
            self.maximum_simultaneous_downloads_change)

        self.unlimited_label = QLabel("(-1 for unlimited)")
        self.unlimited_label.setStyleSheet(OUTPUT_PATH_LABEL_STYLE)

        self.simultaneous_downloads_layout.addWidget(
            self.maximum_simultaneous_downloads_label)
        self.simultaneous_downloads_layout.addWidget(
            self.maximum_simultaneous_downloads_input)
        self.simultaneous_downloads_layout.addWidget(self.unlimited_label)
        self.simultaneous_downloads_layout.addStretch()

        self.always_start_audio_story_mode = QCheckBox(
            "Always start in audio story mode")
        self.always_start_audio_story_mode.setStyleSheet(
            OUTPUT_PATH_LABEL_STYLE)
        self.always_start_audio_story_mode.setChecked(
            get_always_start_with_audio_story_mode())
        self.always_start_audio_story_mode.stateChanged.connect(
            self.always_start_audio_story_mode_change)
        self.always_start_audio_story_mode.setCursor(
            Qt.CursorShape.PointingHandCursor)

        self.fast_audio_story_mode = QCheckBox("Always fast audio story mode")
        self.fast_audio_story_mode.setStyleSheet(OUTPUT_PATH_LABEL_STYLE)
        self.fast_audio_story_mode.setChecked(
            get_always_fast_audio_story_mode())
        self.fast_audio_story_mode.stateChanged.connect(
            self.fast_audio_story_mode_change)
        self.fast_audio_story_mode.setCursor(Qt.CursorShape.PointingHandCursor)

        self.layout.addWidget(self.output_combo_label)
        self.layout.addWidget(self.output_path_combo)
        self.layout.addSpacing(10)
        self.layout.addLayout(self.output_path_layout)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.playlist_output_combo_label)
        self.layout.addWidget(self.playlist_output_path_combo)
        self.layout.addSpacing(10)
        self.layout.addLayout(self.playlist_output_path_layout)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.add_music_combo_label)
        self.layout.addWidget(self.add_music_combo)
        self.layout.addSpacing(20)
        self.layout.addLayout(self.simultaneous_downloads_layout)
        self.layout.addSpacing(20)
        self.layout.addWidget(self.always_start_audio_story_mode)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.fast_audio_story_mode)
        self.layout.addStretch()

        self.footer_layout = QHBoxLayout()
        self.footer_layout.addStretch()
        self.restore_settings_button = QPushButton("Restore settings")
        self.restore_settings_button.clicked.connect(self.restore_settings)
        self.restore_settings_button.setStyleSheet(
            RESTORE_SETTINGS_BUTTON_STYLE)
        self.restore_settings_button.setCursor(
            Qt.CursorShape.PointingHandCursor)
        self.footer_layout.addWidget(self.restore_settings_button)

        self.done_button = QPushButton("Done")
        self.done_button.setStyleSheet(DONE_SETTINGS_BUTTON_STYLE)
        self.done_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.done_button.clicked.connect(self.close)
        self.footer_layout.addWidget(self.done_button)

        self.layout.addLayout(self.footer_layout)
        self.setLayout(self.layout)

    def fast_audio_story_mode_change(self):
        set_always_fast_audio_story_mode(
            self.fast_audio_story_mode.isChecked())

    def always_start_audio_story_mode_change(self):
        set_always_start_with_audio_story_mode(
            self.always_start_audio_story_mode.isChecked())

    def output_path_change(self):
        if self.output_path_combo.currentIndex() == 0:
            set_always_ask_for_output_path(True)
            set_output_path(get_default_download_folder())
            self.output_path_label.setText(
                f"Download path: {get_output_path()}")
            self.output_path_button.setHidden(True)
            self.output_path_label.setHidden(True)
        else:
            set_always_ask_for_output_path(False)
            self.output_path_button.setHidden(False)
            self.output_path_label.setHidden(False)

    def playlist_output_path_change(self):
        if self.playlist_output_path_combo.currentIndex() == 0:
            set_always_ask_for_playlist_output_path(True)
            set_playlist_output_path(get_default_download_folder())
            self.playlist_output_path_label.setText(
                f"Playlist download path: {get_playlist_output_path()}")
            self.playlist_output_path_button.setHidden(True)
            self.playlist_output_path_label.setHidden(True)
        else:
            set_always_ask_for_playlist_output_path(False)
            self.playlist_output_path_button.setHidden(False)
            self.playlist_output_path_label.setHidden(False)

    def add_music_change(self):
        if self.add_music_combo.currentIndex() == 0:
            set_always_ask_to_add_music(True)
            set_add_music(False)
        elif self.add_music_combo.currentIndex() == 1:
            set_always_ask_to_add_music(False)
            set_add_music(False)
        else:
            set_always_ask_to_add_music(False)
            set_add_music(True)

    def restore_settings(self):
        set_always_ask_for_output_path(True)
        set_always_ask_for_playlist_output_path(True)
        set_always_ask_to_add_music(True)
        set_maximum_simultaneous_downloads(5)
        self.output_path_combo.setCurrentIndex(0)
        self.output_path_label.setText(f"Download path: {get_output_path()}")
        self.output_path_button.setHidden(True)
        self.output_path_label.setHidden(True)
        self.playlist_output_path_combo.setCurrentIndex(0)
        self.playlist_output_path_label.setText(
            f"Playlist download path: {get_playlist_output_path()}")
        self.playlist_output_path_button.setHidden(True)
        self.playlist_output_path_label.setHidden(True)
        self.add_music_combo.setCurrentIndex(0)
        self.maximum_simultaneous_downloads_input.setValue(5)
        self.always_start_audio_story_mode.setChecked(False)
        self.fast_audio_story_mode.setChecked(False)

    def change_output_path(self):
        output_path = QFileDialog.getExistingDirectory(
            self, "Select Directory", get_output_path())
        if output_path == "" or output_path == " " or output_path is None or not os.path.exists(output_path):
            set_output_path(get_default_download_folder())
        else:
            set_output_path(output_path)
        self.output_path_label.setText(f"Output path: {get_output_path()}")

    def change_playlist_output_path(self):
        output_path = QFileDialog.getExistingDirectory(
            self, "Select Directory", get_playlist_output_path())
        if output_path == "" or output_path == " " or output_path is None or not os.path.exists(output_path):
            set_playlist_output_path(get_default_download_folder())
        else:
            set_playlist_output_path(output_path)
        self.playlist_output_path_label.setText(
            f"Playlist output path: {get_playlist_output_path()}")

    def maximum_simultaneous_downloads_change(self):
        value = self.maximum_simultaneous_downloads_input.text()
        set_maximum_simultaneous_downloads(int(value))
