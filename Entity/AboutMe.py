from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton

from Functions.open_channel import open_channel
from Styles.AboutMeStyle import *


class AboutMe(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About Me")
        self.setWindowIcon(QIcon("Assets/logo.png"))

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.picture_label = QLabel(self)
        pixmap = QPixmap("Assets/profile.png")
        pixmap = pixmap.scaled(300, 300)
        self.picture_label.setPixmap(pixmap)
        self.layout.addWidget(self.picture_label)

        self.right_layout = QVBoxLayout()
        self.layout.addLayout(self.right_layout)

        self.name_label = QLabel("Md. Shariar Islam Shuvo")
        self.name_label.setStyleSheet(NAME_STYLE)
        self.right_layout.addWidget(self.name_label)
        self.right_layout.addSpacing(20)

        self.bio_label = QLabel("I am a student of BRAC University.\n"
                                "I am a web and software developer\n"
                                "and a competitive programmer.")
        self.bio_label.setStyleSheet(BIO_STYLE)
        self.right_layout.addWidget(self.bio_label)
        self.right_layout.addSpacing(20)

        self.contact_label = QLabel("Contact me:")
        self.contact_label.setStyleSheet(NAME_STYLE)
        self.right_layout.addWidget(self.contact_label)
        self.right_layout.addSpacing(5)

        self.bottom_layout = QHBoxLayout()
        self.right_layout.addLayout(self.bottom_layout)
        self.right_layout.addStretch()

        self.github_label = QPushButton()
        self.github_label.setToolTip("Open my GitHub Profile")
        self.github_label.setIcon(QIcon("Assets/Icons/github.png"))
        self.github_label.setIconSize(QSize(30, 30))
        self.github_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.github_label.setStyleSheet(FOOTER_STYLESHEET)
        self.github_label.clicked.connect(
            lambda: open_channel("https://github.com/ShariarShuvo1/"))
        self.bottom_layout.addWidget(self.github_label)

        self.linkedin_label = QPushButton()
        self.linkedin_label.setToolTip("Open my LinkedIn Profile")
        self.linkedin_label.setIcon(QIcon("Assets/Icons/linkedin.png"))
        self.linkedin_label.setIconSize(QSize(30, 30))
        self.linkedin_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.linkedin_label.setStyleSheet(FOOTER_STYLESHEET)
        self.linkedin_label.clicked.connect(lambda: open_channel(
            "https://www.linkedin.com/in/shariarshuvo1/"))
        self.bottom_layout.addWidget(self.linkedin_label)

        self.facebook_label = QPushButton()
        self.facebook_label.setToolTip("Open my Facebook Profile")
        self.facebook_label.setIcon(QIcon("Assets/Icons/facebook.png"))
        self.facebook_label.setIconSize(QSize(30, 30))
        self.facebook_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.facebook_label.setStyleSheet(FOOTER_STYLESHEET)
        self.facebook_label.clicked.connect(lambda: open_channel(
            "https://www.facebook.com/ShariarShuvo01/"))
        self.bottom_layout.addWidget(self.facebook_label)

        self.email_label = QPushButton()
        self.email_label.setToolTip("Send me an Email at:\n"
                                    "shariaislamshuvo@gmail.com")
        self.email_label.setIcon(QIcon("Assets/Icons/email.png"))
        self.email_label.setIconSize(QSize(30, 30))
        self.email_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.email_label.setStyleSheet(FOOTER_STYLESHEET)
        self.email_label.clicked.connect(
            lambda: open_channel("mailto:shariaislamshuvo@gmail.com"))
        self.bottom_layout.addWidget(self.email_label)
