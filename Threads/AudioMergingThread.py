import os

import eyed3
from PyQt6.QtCore import QThread, pyqtSignal
from moviepy.audio.AudioClip import concatenate_audioclips
from moviepy.audio.io.AudioFileClip import AudioFileClip
from proglog import ProgressBarLogger

from Entity.Video import Video


class AudioMergingThread(QThread):
    progress_updated = pyqtSignal(int)
    status = pyqtSignal(str)

    def __init__(self, audio_files: list[str], output_path: str, main_file: Video, title: str, parent=None):
        super().__init__(parent)
        self.audio_files = audio_files
        self.output_path = output_path
        self.main_file: Video = main_file
        self.title = title

    def run(self):
        audio_clips = [AudioFileClip(path) for path in self.audio_files]
        logger = MyBarLogger(self)

        concatenated_audio = concatenate_audioclips(audio_clips)

        concatenated_audio.write_audiofile(
            self.output_path, codec='mp3', logger=logger)
        for audio in audio_clips:
            audio.close()
        for audio in self.audio_files:
            if os.path.exists(audio):
                os.remove(audio)
        audio_file = eyed3.load(self.output_path)
        audio_file.tag.title = self.title
        audio_file.tag.artist = self.main_file.uploader
        audio_file.tag.images.set(
            3, self.main_file.thumbnail.content, 'image/jpeg', "Cover")
        audio_file.tag.save()
        self.status.emit("Downloaded")


class MyBarLogger(ProgressBarLogger):
    def __init__(self, thread: AudioMergingThread, **kwargs):
        super().__init__(**kwargs)
        self.thread: AudioMergingThread = thread

    def callback(self, **changes):
        pass

    def bars_callback(self, bar, attr, value, old_value=None):
        percentage = (value / self.bars[bar]['total']) * 100
        if old_value is None:
            self.thread.progress_updated.emit(0)
        else:
            self.thread.progress_updated.emit(int(percentage))
        if bar == "chunk":
            self.thread.status.emit("Merging")
