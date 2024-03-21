from PyQt6.QtCore import QThread, pyqtSignal

from Youtube.SearchChannel import search_channel


class ChannelSearchThread(QThread):
    found_one = pyqtSignal(list)
    search_finished = pyqtSignal(bool)

    def __init__(self, url, begin, finish):
        super().__init__()
        self.url = url
        self.begin = begin
        self.finish = finish

    def run(self):
        for i in range(self.begin, self.finish + 1):
            result_list = []
            search_channel(self.url, i, i, result_list)
            self.found_one.emit(result_list)
        self.search_finished.emit(True)
