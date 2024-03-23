from PyQt6.QtWidgets import QWidget


class MyWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setMouseTracking(True)

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.main_window.show_previous()
        else:
            self.main_window.show_next()
        event.accept()
