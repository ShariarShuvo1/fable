from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont, QCursor
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QProgressBar
from PyQt6 import QtWidgets



class Card:
    def __init__(self, ui):
        w = 1200//100
        h = 900//100
        self.card = QVBoxLayout()
        font = QFont()
        font.setBold(True)
        font.setPointSize(16)

        # Row 1 input
        self.row1 = QHBoxLayout()
        self.url = QLabel("URL: ")
        self.url.setFont(font)

        self.edit_box = QLineEdit()
        self.edit_box.setFont(font)
        self.edit_box.setClearButtonEnabled(True)
        self.edit_box.setPlaceholderText("Place your YouTube URL here")

        self.row1.addWidget(self.url)
        self.row1.addWidget(self.edit_box)

        # Row 2 Quality selection
        self.row2 = QHBoxLayout()

        self.resolution_list = QComboBox()
        self.resolution_list.setFont(font)
        self.resolution_list.setPlaceholderText("Select a resolution")

        self.download_button = QPushButton("Download")
        self.download_button.setFont(font)
        self.download_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.download_button.setMaximumWidth(w*20)
        self.download_button.clicked.connect(lambda: ui.download_clicked(self.edit_box.text()))

        self.row2.addWidget(self.resolution_list)
        self.row2.addWidget(self.download_button)

        # Row 3 Media Info
        self.row3 = QHBoxLayout()
        self.thumbnail_preview = QLabel()
        self.thumbnail_preview.setPixmap(QPixmap('./assets/dummy_thumbnail.png').scaledToHeight(150))
        self.thumbnail_preview.setMaximumWidth(270)

        self.description_preview = QLabel()
        self.description_preview.setFont(font)

        self.row3.addWidget(self.thumbnail_preview)
        self.row3.addWidget(self.description_preview)

        # Row 4 Downloading Status
        self.row4 = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(20)

        self.empty_line = QLabel()
        self.empty_line.setMaximumHeight(2)
        self.empty_line.setStyleSheet("background-color: red")

        self.row4.addWidget(self.progress_bar)
        self.row4.addWidget(self.empty_line)

        self.card.addLayout(self.row1)
        self.card.addLayout(self.row2)
        self.card.addLayout(self.row3)
        self.card.addLayout(self.row4)
