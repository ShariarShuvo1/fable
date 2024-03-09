from PyQt6.QtCore import QThread, pyqtSignal

from Youtube.SearchPlaylist import search_youtube_playlist


class SearchPlaylistThread(QThread):
    search_finished = pyqtSignal(list)
    total_videos = pyqtSignal(int)
    completed_videos = pyqtSignal(int)

    def __init__(self, query):
        super().__init__()
        self.query = query

    def run(self):
        result_list = []
        search_youtube_playlist(self.query, self, result_list)
        self.search_finished.emit(result_list)
