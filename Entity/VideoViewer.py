import tempfile

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QSlider, QPushButton, QWidget
from PyQt6.QtGui import QIcon, QCloseEvent, QPixmap
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl, Qt, QSize

from Consts.SettingsData import get_volume, set_volume
from Entity.Video import Video
from Functions.format_time import format_time
from Functions.open_channel import open_channel
from Styles.AudioStyleCardStyle import SLIDER_STYLESHEET
from Styles.BRACU_STYLE import OPEN_BROWSER_BUTTON_STYLESHEET


class VideoViewer(QDialog):
    def __init__(self, video: Video):
        super().__init__()
        self.setWindowFlags(self.windowFlags(
        ) | Qt.WindowType.WindowMinMaxButtonsHint | Qt.WindowType.WindowCloseButtonHint)
        self.video: Video = video
        self.searchThread = None

        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(self.video.thumbnail.content)
            image_path = tmp_file.name

        self.label = QLabel(self)
        self.label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.label.mousePressEvent = self.thumbnail_clicked
        self.label.setToolTip("Click to Play Video")

        self.pixmap = QPixmap(image_path)
        if self.pixmap.isNull():
            self.label.setText("Error: Image not found or invalid format!")
        else:
            self.pixmap = self.pixmap.scaled(
                640, 480, Qt.AspectRatioMode.KeepAspectRatio)
            self.label.setPixmap(self.pixmap)
        self.label.setBaseSize(640, 480)

        self.setBaseSize(640, 480)
        self.setWindowTitle(f"Thumbnail preview of: {video.title}")
        self.setWindowIcon(QIcon("Assets/logo.png"))

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(self.label)

        self.video_player_widget = QWidget()
        self.video_player_layout = QVBoxLayout()
        self.video_player_widget.setLayout(self.video_player_layout)
        self.layout.addWidget(self.video_player_widget)

        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.video_widget = QVideoWidget()
        self.video_widget.setToolTip("Pause")
        self.video_widget.setCursor(Qt.CursorShape.PointingHandCursor)
        self.video_widget.mousePressEvent = self.play_pause
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.setAudioOutput(self.audio_output)

        self.video_player_layout.addWidget(self.video_widget)
        self.video_widget.hide()

        self.current_time_label = QLabel(f"{format_time(0)}")
        self.current_time_label.setFixedHeight(20)
        self.current_time_label.setFixedWidth(100)

        self.progress_layout = QHBoxLayout()
        self.progress_layout.addWidget(self.current_time_label)

        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setStyleSheet(SLIDER_STYLESHEET)
        self.progress_slider.setCursor(Qt.CursorShape.PointingHandCursor)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.setValue(0)
        self.progress_slider.setToolTip(f"{format_time(0)}")
        self.media_player.positionChanged.connect(self.update_duration)
        self.progress_slider.sliderReleased.connect(self.set_video_position)
        self.progress_slider.sliderPressed.connect(self.slider_pressed)
        self.progress_slider.sliderMoved.connect(self.slider_value_changed)
        self.progress_layout.addWidget(self.progress_slider)

        self.video_length_label = QLabel(f"{format_time(0)}")
        self.video_length_label.setFixedHeight(20)
        self.video_length_label.setFixedWidth(100)
        self.progress_layout.addWidget(self.video_length_label)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setStyleSheet(SLIDER_STYLESHEET)
        self.volume_slider.setCursor(Qt.CursorShape.PointingHandCursor)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(get_volume())
        self.volume_slider.setToolTip(f"{self.volume_slider.value()}%")
        self.audio_output.setVolume(get_volume() / 100.0)
        self.volume_slider.valueChanged.connect(self.change_volume)

        self.volume_label = QLabel(f"{get_volume()}%")
        self.volume_label.setFixedHeight(20)
        self.volume_slider.setFixedWidth(100)
        self.volume_title_label = QLabel("  Volume")
        self.volume_title_label.setFixedHeight(20)
        self.progress_layout.addWidget(self.volume_title_label)
        self.progress_layout.addWidget(self.volume_slider)
        self.progress_layout.addWidget(self.volume_label)

        self.open_browser_button = QPushButton()
        self.open_browser_button.setIcon(QIcon("./Assets/Icons/yt-icon.png"))
        self.open_browser_button.setIconSize(QSize(35, 35))
        self.open_browser_button.setToolTip("Open Video in Browser")
        self.open_browser_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.open_browser_button.setFixedSize(40, 40)
        self.open_browser_button.setStyleSheet(OPEN_BROWSER_BUTTON_STYLESHEET)
        self.open_browser_button.clicked.connect(
            lambda checked: open_channel(self.video.video_url))
        self.progress_layout.addWidget(self.open_browser_button)

        self.video_player_layout.addLayout(self.progress_layout)
        self.video_player_widget.hide()

    def thumbnail_clicked(self, event):
        self.label.hide()
        self.setWindowTitle(f"Video preview of: {self.video.title}")
        self.video_player_widget.show()
        self.get_video_url()

    def play_pause(self, event):
        if self.media_player.isPlaying():
            self.video_widget.setToolTip("Play")
            self.media_player.pause()
        else:
            self.video_widget.setToolTip("Pause")
            self.media_player.play()

    def update_duration(self, position):
        self.current_time_label.setText(f"{format_time(position // 1000)}")
        self.progress_slider.setToolTip(f"{format_time(position // 1000)}")
        self.progress_slider.setValue(position//1000)

    def slider_pressed(self):
        self.media_player.pause()

    def slider_value_changed(self):
        self.current_time_label.setText(
            f"{format_time(self.progress_slider.value())}")

    def set_video_position(self):
        position = self.progress_slider.value() * 1000
        self.media_player.setPosition(position)
        self.media_player.play()

    def change_volume(self, volume):
        set_volume(volume)
        self.volume_label.setText(f"{volume}%")
        self.volume_slider.setToolTip(f"{volume}%")
        self.audio_output.setVolume(volume / 100.0)

    def load_video(self, video_url):
        if video_url:
            self.progress_slider.setRange(0, self.video.duration)
            self.video_length_label.setText(
                f"{format_time(self.video.duration)}")
            media_content = QUrl(video_url)
            self.media_player.setSource(media_content)
            self.video_widget.show()
            self.media_player.play()

    def get_video_url(self):
        video_url = ""
        self.video: Video = self.video
        for res in self.video.resolution_list:
            if res.file_type == "mix":
                video_url = res.url
        return self.load_video(video_url)

    def closeEvent(self, event: QCloseEvent):
        self.media_player.stop()
        self.media_player.disconnect()
        event.accept()
