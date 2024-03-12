PLAYLIST_CARD_STYLESHEET: str = """
    QWidget {
        background-color: #ab85ff;
        border-radius: 5px;
        padding: 4px;
    }
"""
PLAYLIST_CARD_DISABLED_STYLESHEET: str = """
    QWidget {
        background-color: #a0a0a0;
        border-radius: 5px;
        padding: 4px;
    }
"""

VIDEO_TITLE_STYLESHEET: str = """
    QLabel {
        font-size: 14px;
        font-weight: bold;
        padding: 0px;
    }
"""

REMOVE_BUTTON_STYLESHEET: str = """
    QPushButton {
        background-color: transparent;
        border: none;
    }
    QPushButton:hover {
        background-color: #ff82ac;
        border-radius: 10px;
    }
"""

ADD_BUTTON_STYLESHEET: str = """
    QPushButton {
        background-color: transparent;
        border: none;
    }
    QPushButton:hover {
        background-color: #82ff9e;
        border-radius: 10px;
    }
"""
DOWNLOAD_BUTTON_STYLESHEET: str = """
    QPushButton {
        padding: 5px;
        border-radius: 5px;
        background-color: #078a00;
        color: white;
        font-size: 20px;
        font-weight: bold;
        margin-left: 2px;
        margin-top: 2px;
    }
    QPushButton:hover {
        background-color: #076e01;
    }
    QPushButton:pressed {
        background-color: #055201;
    }
    QPushButton:disabled {
        background-color: #616161;
        color: #d1d1d1;
    }
"""