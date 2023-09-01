from PyQt6 import QtCore


class Downloader(QtCore.QThread):
    def set_values(self, window):
        self.window = window

    def run(self):
        self.window.queue_processing = True
        while len(self.window.queue) != 0:
            if self.window.queue[0].download_complete:
                self.window.queue.pop(0)
                continue
            if not self.window.downloading:
                card = self.window.queue[0]
                self.window.download(card)
        self.window.queue_processing = False
