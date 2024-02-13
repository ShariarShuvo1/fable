from PyQt6.QtCore import QThread, pyqtSignal

from Youtube.Search import search_youtube


class SearchThread(QThread):
    search_finished = pyqtSignal(list)

    def __init__(self, query, max_results=10):
        super().__init__()
        self.query = query
        self.max_results = max_results

    def run(self):
        result_list = []
        search_youtube(self.query, self.max_results, result_list)
        self.search_finished.emit(result_list)
