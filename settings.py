from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon, QIntValidator, QFont
from PyQt6.QtWidgets import QDialog, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QRadioButton, QButtonGroup, \
    QFileDialog, QCheckBox, QLineEdit, QSpinBox

from Styles.SettingsStyle import *
from Consts.SettingsData import *


class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumSize(800, 400)
        self.setMaximumSize(1100, 700)
        self.layout = QVBoxLayout()

        self.ask_for_path = QRadioButton("Always ask for download path")
        self.ask_for_path.clicked.connect(self.ask_for_path_change)
        self.ask_for_path.setStyleSheet(RADIO_BUTTON_STYLE)
        self.ask_for_path.setCursor(Qt.CursorShape.PointingHandCursor)

        self.choose_output_path = QRadioButton("Choose a default download path")
        self.choose_output_path.clicked.connect(self.ask_for_path_change)
        self.choose_output_path.setStyleSheet(RADIO_BUTTON_STYLE)
        self.choose_output_path.setCursor(Qt.CursorShape.PointingHandCursor)

        self.output_path_layout = QHBoxLayout()

        self.output_path_label = QLabel(f"Download path: {get_output_path()}")
        self.output_path_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.output_path_label.setStyleSheet(OUTPUT_PATH_LABEL_STYLE)

        self.output_path_button = QPushButton("Change")
        self.output_path_button.setIcon(QIcon("./Assets/Icons/folder-icon.png"))
        self.output_path_button.setIconSize(QSize(20, 20))
        self.output_path_button.clicked.connect(self.change_output_path)
        self.output_path_button.setStyleSheet(OUTPUT_PATH_BUTTON_STYLE)
        self.output_path_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.output_path_layout.addWidget(self.output_path_label)
        self.output_path_layout.addWidget(self.output_path_button)
        self.output_path_layout.addStretch()

        if get_ask_for_output_path():
            self.ask_for_path.setChecked(True)
            self.output_path_button.setDisabled(True)
            self.output_path_label.setDisabled(True)
        else:
            self.choose_output_path.setChecked(True)
            self.output_path_button.setDisabled(False)
            self.output_path_label.setDisabled(False)

        self.always_ask_to_add_music = QCheckBox("Always ask to add music (If the file is video only)")
        self.always_ask_to_add_music.setChecked(get_always_ask_to_add_music())
        self.always_ask_to_add_music.clicked.connect(self.always_ask_to_add_music_change)
        self.always_ask_to_add_music.setStyleSheet(OUTPUT_PATH_LABEL_STYLE)
        self.always_ask_to_add_music.setCursor(Qt.CursorShape.PointingHandCursor)

        self.simultaneous_downloads_layout = QHBoxLayout()

        self.maximum_simultaneous_downloads_label = QLabel("Maximum simultaneous downloads: ")
        self.maximum_simultaneous_downloads_label.setStyleSheet(OUTPUT_PATH_LABEL_STYLE)

        self.maximum_simultaneous_downloads_input = QSpinBox()
        self.maximum_simultaneous_downloads_input.setRange(-1, 1000)
        self.maximum_simultaneous_downloads_input.setValue(get_maximum_simultaneous_downloads())
        self.maximum_simultaneous_downloads_input.setMaximumWidth(100)
        self.maximum_simultaneous_downloads_input.setFixedHeight(30)
        self.maximum_simultaneous_downloads_input.setSingleStep(1)
        self.maximum_simultaneous_downloads_input.setStyleSheet(OUTPUT_PATH_LABEL_STYLE)
        self.maximum_simultaneous_downloads_input.textChanged.connect(self.maximum_simultaneous_downloads_change)

        self.unlimited_label = QLabel("(-1 for unlimited)")
        self.unlimited_label.setStyleSheet(OUTPUT_PATH_LABEL_STYLE)

        self.simultaneous_downloads_layout.addWidget(self.maximum_simultaneous_downloads_label)
        self.simultaneous_downloads_layout.addWidget(self.maximum_simultaneous_downloads_input)
        self.simultaneous_downloads_layout.addWidget(self.unlimited_label)
        self.simultaneous_downloads_layout.addStretch()

        self.layout.addWidget(self.ask_for_path)
        self.layout.addWidget(self.choose_output_path)
        self.layout.addLayout(self.output_path_layout)
        self.layout.addWidget(self.always_ask_to_add_music)
        self.layout.addLayout(self.simultaneous_downloads_layout)
        self.layout.addStretch()

        self.footer_layout = QHBoxLayout()
        self.footer_layout.addStretch()
        self.restore_settings_button = QPushButton("Restore settings")
        self.restore_settings_button.clicked.connect(self.restore_settings)
        self.restore_settings_button.setStyleSheet(RESTORE_SETTINGS_BUTTON_STYLE)
        self.restore_settings_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.footer_layout.addWidget(self.restore_settings_button)

        self.done_button = QPushButton("Done")
        self.done_button.setStyleSheet(RESTORE_SETTINGS_BUTTON_STYLE)
        self.done_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.done_button.clicked.connect(self.close)
        self.footer_layout.addWidget(self.done_button)

        self.layout.addLayout(self.footer_layout)
        self.setLayout(self.layout)

    def restore_settings(self):
        set_output_path(get_default_download_folder())
        self.output_path_label.setText(f"Download path: {get_output_path()}")
        set_always_ask_for_output_path(True)
        self.ask_for_path.setChecked(True)
        self.choose_output_path.setChecked(False)
        self.output_path_button.setDisabled(True)
        self.output_path_label.setDisabled(True)
        set_always_ask_to_add_music(True)
        self.always_ask_to_add_music.setChecked(True)
        set_maximum_simultaneous_downloads(5)
        self.maximum_simultaneous_downloads_input.setValue(5)

    def change_output_path(self):
        output_path = QFileDialog.getExistingDirectory(
            self, "Select Directory", get_output_path())
        if output_path == "" or output_path == " " or output_path is None or not os.path.exists(output_path):
            set_output_path(get_default_download_folder())
        else:
            set_output_path(output_path)
        self.output_path_label.setText(f"Output path: {get_output_path()}")

    def ask_for_path_change(self):
        if self.ask_for_path.isChecked():
            self.output_path_button.setDisabled(True)
            self.output_path_label.setDisabled(True)
            set_always_ask_for_output_path(True)
        else:
            self.output_path_button.setDisabled(False)
            self.output_path_label.setDisabled(False)
            set_always_ask_for_output_path(False)

    def always_ask_to_add_music_change(self):
        set_always_ask_to_add_music(self.always_ask_to_add_music.isChecked())

    def maximum_simultaneous_downloads_change(self):
        value = self.maximum_simultaneous_downloads_input.text()
        set_maximum_simultaneous_downloads(int(value))
