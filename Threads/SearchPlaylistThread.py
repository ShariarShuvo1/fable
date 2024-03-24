from PyQt6.QtCore import QThread, pyqtSignal

from Youtube.SearchPlaylist import search_youtube_playlist


class SearchPlaylistThread(QThread):
    search_update = pyqtSignal(list)
    search_finished = pyqtSignal()
    total_videos = pyqtSignal(int)
    completed_videos = pyqtSignal(int)

    def __init__(self, query):
        super().__init__()
        self.query = query

    def run(self):
        search_youtube_playlist(self.query, self)
        self.search_finished.emit()
