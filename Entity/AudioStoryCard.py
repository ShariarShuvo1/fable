import os
import platform
import subprocess
from datetime import datetime

import PyQt6
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QProgressBar, QMessageBox

from Consts.SettingsData import get_ask_before_deleting
from Entity.AudioStory import AudioStory
from Entity.Resolution import Resolution
from Entity.SubCard import SubCard
from Entity.Video import Video
from Functions.SanitizeFilename import sanitize_filename
from Functions.format_time import format_time
from Styles.AudioStyleCardStyle import *
from Threads.AudioMergingThread import AudioMergingThread
from Threads.SearchThread import SearchThread

from Entity.File import File
from Functions.convertBitsToReadableString import convert_bits_to_readable_string
from Styles.DownloadListStyle import TOOL_ICON_BUTTON_STYLESHEET, VIDEO_TITLE_STYLESHEET, PROGRESS_BAR_STYLESHEET, \
    VIDEO_STATUS_STYLESHEET, TOOL_ICON_PLAY_BUTTON_STYLESHEET


class AudioStoryCard:

    def get_file(self, video: Video) -> File:
        resolution: Resolution | None = None
        best_abr = -1
        for res in video.resolution_list:
            if res.file_type == "audio" and res.abr > best_abr:
                best_abr = res.abr
                resolution = res
        extension: str = resolution.ext
        title = sanitize_filename(video.title)
        title += f"_{int(resolution.abr)}kbps"
        file_obj: File = File(
            f"{title}.{extension}",
            video.video_url,
            resolution.format_id,
            resolution.url,
            resolution.file_type,
            "Queued",
            datetime.now(),
            resolution.filesize,
            self.audio_story.out_path,
            True
        )
        return file_obj

    def on_search_finished(self, result_list: list[Video]):
        index = -1
        for i in range(len(self.audio_story.url_list)):
            if self.audio_story.url_list[i] is result_list[0].video_url:
                index = i
                break
        self.audio_story_info_list[index] = result_list[0]
        all_finished = True
        count = 0
        for video in self.audio_story_info_list:
            if video is None:
                all_finished = False
            else:
                count += 1
        self.dummy_progress_bar.setValue(count)
        if all_finished:
            if self.audio_story.title is None:
                self.audio_story.set_title(
                    f"{sanitize_filename(self.audio_story_info_list[0].title)}.mp3")
            self.generate_body()
            self.main_window.download_complete_in_card(self)

    def __init__(self, audio_story: AudioStory, main_window):
        self.spacer_item = None
        self.audio_merging_thread = None
        self.main_window = main_window
        self.audio_story = audio_story
        self.audio_story_info_list: list[Video | None] = [
            None] * len(self.audio_story.url_list)
        self.thread_list = []
        self.sub_card_list: list[SubCard] = []
        self.total_downloaded = 0

        self.icon_size: QSize = QSize(30, 30)

        self.audio_story_box: QWidget = QWidget()
        self.audio_story_box.setStyleSheet(DUMMY_WIDGET_STYLESHEET)

        self.dummy_label = QLabel(f"Getting information for {
                                  len(self.audio_story.url_list)} audio story")
        self.dummy_label.setStyleSheet(VIDEO_TITLE_STYLESHEET)

        self.dummy_progress_bar = QProgressBar()
        self.dummy_progress_bar.setRange(0, len(self.audio_story.url_list))
        self.dummy_progress_bar.setValue(0)
        self.dummy_progress_bar.setFixedHeight(16)
        self.dummy_progress_bar.setStyleSheet(PROGRESS_BAR_STYLESHEET)

        for index, url in enumerate(self.audio_story.url_list):
            search_thread = SearchThread(url, index)
            self.thread_list.append(search_thread)
            self.thread_list[-1].search_finished.connect(
                lambda result_list: self.on_search_finished(result_list))
            self.thread_list[-1].start()

        self.completed_button = QPushButton()
        self.completed_button.setToolTip(
            "Download Completed\nClick to open in the folder")
        self.completed_button.setIcon(
            QIcon("./Assets/Icons/completed-icon.png"))
        self.completed_button.setIconSize(self.icon_size)
        self.completed_button.setStyleSheet(TOOL_ICON_BUTTON_STYLESHEET)
        self.completed_button.setCursor(
            PyQt6.QtCore.Qt.CursorShape.PointingHandCursor)
        self.completed_button.clicked.connect(
            lambda: self.completed_button_clicked())

        self.play_button: QPushButton = QPushButton()
        self.play_button.setToolTip("Start Downloading This Audio Story")
        self.play_button.setIcon(QIcon("./Assets/Icons/play-icon.png"))
        self.play_button.setIconSize(self.icon_size)
        self.play_button.setStyleSheet(TOOL_ICON_PLAY_BUTTON_STYLESHEET)
        self.play_button.setCursor(
            PyQt6.QtCore.Qt.CursorShape.PointingHandCursor)
        self.play_button.clicked.connect(lambda: self.begin_download())

        self.title_label: QLabel = QLabel(self.audio_story.title)
        self.title_label.setStyleSheet(VIDEO_TITLE_STYLESHEET)

        self.remove_button: QPushButton = QPushButton()
        self.remove_button.setToolTip("Remove This Audio Story From The List")
        self.remove_button.setIcon(QIcon("./Assets/Icons/cancel-icon.png"))
        self.remove_button.setIconSize(self.icon_size)
        self.remove_button.setStyleSheet(REMOVE_BUTTON_STYLESHEET)
        self.remove_button.setCursor(
            PyQt6.QtCore.Qt.CursorShape.PointingHandCursor)
        self.remove_button.clicked.connect(lambda: self.delete_audio_story())

        self.delete_button = QPushButton()
        self.delete_button.setToolTip("Delete This Audio Story From The Disk")
        self.delete_button.setIcon(QIcon("./Assets/Icons/delete-icon.png"))
        self.delete_button.setIconSize(self.icon_size)
        self.delete_button.setStyleSheet(REMOVE_BUTTON_STYLESHEET)
        self.delete_button.setCursor(
            PyQt6.QtCore.Qt.CursorShape.PointingHandCursor)
        self.delete_button.clicked.connect(lambda: self.delete_audio_story())

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(16)
        self.progress_bar.setStyleSheet(PROGRESS_BAR_STYLESHEET)

        self.status_label = QLabel(self.audio_story.status)
        self.status_label.setStyleSheet(VIDEO_STATUS_STYLESHEET)

        self.file_size_label = QLabel("N/A")
        self.file_size_label.setStyleSheet(VIDEO_TITLE_STYLESHEET)

        self.speed_label = QLabel()
        self.speed_label.setStyleSheet(VIDEO_STATUS_STYLESHEET)
        self.speed_label.setFixedWidth(70)

        self.eta_label = QLabel()
        self.eta_label.setFixedWidth(70)
        self.eta_label.setStyleSheet(VIDEO_STATUS_STYLESHEET)

        self.datetime_label = QLabel(
            self.audio_story.added_date.strftime("%Y-%m-%d %H:%M:%S"))
        self.datetime_label.setToolTip(
            self.audio_story.added_date.strftime("%A, %B %d, %Y %H:%M:%S"))
        self.datetime_label.setStyleSheet(VIDEO_STATUS_STYLESHEET)
        self.datetime_label.setFixedWidth(110)
        self.datetime_label.setAlignment(
            PyQt6.QtCore.Qt.AlignmentFlag.AlignCenter)

        self.expand_button: QPushButton = QPushButton()
        self.expand_button.setToolTip(
            "Expand to see individual video downloads")
        self.expand_button.setIcon(QIcon("./Assets/Icons/expand-icon.png"))
        self.expand_button.setIconSize(self.icon_size)
        self.expand_button.setStyleSheet(ADD_BUTTON_STYLESHEET)
        self.expand_button.setCursor(
            PyQt6.QtCore.Qt.CursorShape.PointingHandCursor)
        self.expand_button.clicked.connect(lambda: self.expand_clicked())

        self.shrink_button: QPushButton = QPushButton()
        self.shrink_button.setToolTip(
            "Shrink to hide individual video downloads")
        self.shrink_button.setIcon(QIcon("./Assets/Icons/shrink-icon.png"))
        self.shrink_button.setIconSize(self.icon_size)
        self.shrink_button.setStyleSheet(ADD_BUTTON_STYLESHEET)
        self.shrink_button.setCursor(
            PyQt6.QtCore.Qt.CursorShape.PointingHandCursor)
        self.shrink_button.clicked.connect(lambda: self.shrink_clicked())

        self.main_layout = QVBoxLayout()

        self.main_layout.addWidget(self.dummy_label)
        self.main_layout.addWidget(self.dummy_progress_bar)

        self.main_row = QHBoxLayout()

        self.main_row.addWidget(self.play_button)
        self.main_row.addWidget(self.completed_button)
        self.completed_button.setHidden(True)

        self.information_layout = QVBoxLayout()

        self.information_layout.addWidget(self.title_label)
        self.information_layout.addWidget(self.progress_bar)

        self.main_row.addLayout(self.information_layout)
        self.main_row.addStretch()
        self.main_row.addSpacing(5)
        self.main_row.addWidget(self.speed_label)
        self.main_row.addSpacing(5)
        self.main_row.addWidget(self.eta_label)
        self.main_row.addSpacing(5)
        self.main_row.addWidget(self.status_label)
        self.main_row.addSpacing(5)
        self.main_row.addWidget(self.file_size_label)
        self.main_row.addSpacing(5)
        self.main_row.addWidget(self.datetime_label)
        self.main_row.addSpacing(5)
        self.main_row.addWidget(self.remove_button)
        self.main_row.addWidget(self.delete_button)
        self.main_row.addWidget(self.expand_button)
        self.main_row.addWidget(self.shrink_button)

        self.main_layout.addLayout(self.main_row)
        self.audio_story_box.setLayout(self.main_layout)

        self.title_label.setHidden(True)
        self.progress_bar.setHidden(True)
        self.status_label.setHidden(True)
        self.file_size_label.setHidden(True)
        self.datetime_label.setHidden(True)
        self.speed_label.setHidden(True)
        self.eta_label.setHidden(True)
        self.expand_button.setHidden(True)
        self.shrink_button.setHidden(True)
        self.play_button.setHidden(True)
        self.remove_button.setHidden(True)
        self.delete_button.setHidden(True)

    def completed_button_clicked(self):
        output_path = self.audio_story.out_path
        output_path = output_path.replace("\\", "/")
        if os.path.exists(output_path):
            system = platform.system()
            if system == "Windows":
                os.startfile(os.path.dirname(output_path))
            elif system == "Darwin":
                subprocess.call(["open", "-R", output_path])
            else:
                subprocess.call(["xdg-open", os.path.dirname(output_path)])

    def delete_audio_story(self):
        ask = False
        if get_ask_before_deleting():
            ask = True
        if ask:
            msg_box = QMessageBox()
            msg_box.setWindowIcon(QIcon("./Assets/logo.png"))
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setText(
                f"Are you sure you want to delete:\n{self.audio_story.title} ?")
            msg_box.setWindowTitle("Delete Download")
            msg_box.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg_box.setDefaultButton(
                QMessageBox.StandardButton.Yes)
            response = msg_box.exec()
            if response == QMessageBox.StandardButton.Yes:
                if self.audio_story.status == "Downloaded":
                    if os.path.exists(self.audio_story.out_path):
                        os.remove(self.audio_story.out_path)
                self.main_window.delete_audio_story_card(self)
        elif not ask:
            if self.audio_story.status == "Downloaded":
                if os.path.exists(self.audio_story.out_path):
                    os.remove(self.audio_story.out_path)
            self.main_window.delete_audio_story_card(self)

    def begin_download(self):
        self.spacer_item = self.main_row.itemAt(3)
        self.main_row.removeItem(self.spacer_item)
        self.progress_bar.show()
        self.speed_label.show()
        self.eta_label.show()
        self.remove_button.hide()
        self.audio_story_box.setStyleSheet(WIDGET_DOWNLOADING_STYLESHEET)
        self.play_button.hide()
        self.audio_story.set_status("Downloading")
        self.status_label.setText("Downloading")
        for sub_card in self.sub_card_list:
            sub_card.begin_download()

    def download_finished(self):
        self.total_downloaded += 1
        self.progress_bar.setValue(100)
        if self.total_downloaded == len(self.sub_card_list):
            self.speed_label.hide()
            self.eta_label.hide()
            audio_paths = []
            output_path = self.audio_story.out_path
            output_path = output_path.replace("\\", "/")
            for sub_card in self.sub_card_list:
                audio_paths.append(f'{output_path}/{sub_card.video.title}')
            self.audio_story.out_path = f"{
                output_path}/{self.audio_story.title}"
            if os.path.exists(self.audio_story.out_path):
                self.audio_story.title = f"{
                    self.audio_story.title[:-4]}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp3"
                self.title_label.setText(self.audio_story.title)
                self.audio_story.out_path = f"{
                    output_path}/{self.audio_story.title}"
            if self.audio_story.author is None:
                author = self.audio_story_info_list[0].uploader
            else:
                author = self.audio_story.author
            self.audio_merging_thread = AudioMergingThread(audio_paths, f"{
                                                           self.audio_story.out_path}",
                                                           self.audio_story_info_list[0],
                                                           self.audio_story.title, author)
            self.audio_merging_thread.progress_updated.connect(
                self.merging_progress_updated)
            self.audio_merging_thread.status.connect(
                self.merging_status_updated)
            self.audio_merging_thread.start()

    def merging_progress_updated(self, progress):
        self.progress_bar.setValue(progress)

    def merging_status_updated(self, status):
        self.status_label.setText(status)
        if status == "Downloaded":
            self.completed_button.show()
            self.delete_button.show()
            self.audio_story.set_status(status)
            self.main_row.insertItem(3, self.spacer_item)
            self.progress_bar.hide()
            size_bytes = os.path.getsize(self.audio_story.out_path)
            self.file_size_label.setText(
                convert_bits_to_readable_string(size_bytes))
            self.audio_story_box.setStyleSheet(WIDGET_DOWNLOADED_STYLESHEET)
            self.main_window.download_complete_in_card(self)

    def progress_updated(self):
        progress = 0
        for sub_card in self.sub_card_list:
            progress += sub_card.progress_bar.value()
        progress = progress // len(self.sub_card_list)
        self.progress_bar.setValue(progress)

    def eta_updated(self):
        eta = 0
        for sub_card in self.sub_card_list:
            eta_text = sub_card.eta_label.text()
            if len(eta_text) > 0:
                components = eta_text.split(" : ")
                total_seconds = 0
                for component in components:
                    if "H" in component:
                        total_seconds += int(component.strip("H")) * 3600
                    elif "M" in component:
                        total_seconds += int(component.strip("M")) * 60
                    elif "S" in component:
                        total_seconds += int(component.strip("S"))
                eta += total_seconds
        self.eta_label.setText(format_time(eta))

    def speed_updated(self):
        speed = 0
        for sub_card in self.sub_card_list:
            speed_text = sub_card.speed_label.text()
            if len(speed_text) > 2:
                speed_text = speed_text[:-2]
                bits = float(speed_text[:-2])
                unit = speed_text[-2:]
                units = ['B', 'KB', 'MB', 'GB']
                index = units.index(unit)
                for _ in range(index):
                    bits *= 1024
                speed += bits

        self.speed_label.setText(convert_bits_to_readable_string(speed) + "/s")

    def expand_clicked(self):
        for sub_card in self.sub_card_list:
            sub_card.download_box.show()
        self.expand_button.hide()
        self.shrink_button.show()

    def shrink_clicked(self):
        for sub_card in self.sub_card_list:
            sub_card.download_box.hide()
        self.expand_button.show()
        self.shrink_button.hide()

    def generate_body(self):
        self.audio_story_box.setStyleSheet(WIDGET_STYLESHEET)
        self.dummy_progress_bar.hide()
        self.dummy_label.hide()

        self.title_label.show()
        self.title_label.setText(self.audio_story.title)
        self.status_label.show()
        self.file_size_label.show()
        self.datetime_label.show()
        self.expand_button.show()
        self.play_button.show()
        self.remove_button.show()
        size = 0
        for video in self.audio_story_info_list:
            if video is not None:
                file: File = self.get_file(video)
                size += file.file_size
                sub_card = SubCard(file, self)
                self.sub_card_list.append(sub_card)
                self.main_layout.addWidget(sub_card.download_box)
                self.sub_card_list[-1].download_box.hide()
        self.file_size_label.setText(convert_bits_to_readable_string(size))
