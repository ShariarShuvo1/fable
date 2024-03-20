DOWNLOAD_TITLE_STYLESHEET: str = """
    QLabel {
        font-size: 24px;
        padding: 10px;
        margin-top: 10px;
        border-top-left-radius: 5px;
        border-top-right-radius: 5px;
        font-weight: bold;
        color: white;
        background-color: #9a00bd;
    }
"""

VIDEO_TITLE_STYLESHEET: str = """
    QLabel {
        font-size: 14px;
        font-weight: bold;
        padding: 0px;
    }
"""

VIDEO_TITLE_BUTTON_STYLESHEET: str = """
    QPushButton {
        font-size: 14px;
        font-weight: bold;
        padding: 0px;
        color: black;
        text-align: left;
    }
    QPushButton:hover {
        color: #9a00bd;
    }
"""

TOOL_ICON_BUTTON_STYLESHEET: str = """
    QPushButton {
        background-color: transparent;
        border: none;
    }
"""

TOOL_ICON_PLAY_BUTTON_STYLESHEET: str = """
    QPushButton {
        background-color: #transparent;
        padding: 5px;
        border: none;
    }
    QPushButton:hover {
        background-color: #008b26;
    }
    QPushButton:pressed {
        background-color: #007e22;
    }
"""

TOOL_ICON_PAUSE_BUTTON_STYLESHEET: str = """
    QPushButton {
        background-color: transparent;
        padding: 5px;
        border: none;
    }
    QPushButton:hover {
        background-color: #c98c02;
    }
    QPushButton:pressed {
        background-color: #b97e02;
    }
"""

TOOL_ICON_DELETE_BUTTON_STYLESHEET: str = """
    QPushButton {
        padding: 5px;
        border: none;
    }
    QPushButton:hover {
        background-color: #d9022a;
    }
    QPushButton:pressed {
        background-color: #c90227;
    }
"""

VIDEO_STATUS_STYLESHEET: str = """
    QLabel {
        font-size: 12px;
    }
"""

VIDEO_SIZE_STYLESHEET: str = """
    QLabel {
        font-size: 14px;
        font-weight: bold;
    }
"""

PROGRESS_BAR_STYLESHEET: str = """
    QProgressBar {
        border-radius: 5px;
        background-color: #9a00bd;
        text-align: center;
        font-size: 14px;
        font-weight: bold;
        color: blue;
    }

    QProgressBar::chunk {
        background-color: lime;
        margin: 0.5px;
        border-radius: 5px;
    }
    
"""

SCROLL_AREA_STYLESHEET: str = """
    QScrollArea {
        border: none;
        margin: 0px;
        padding: 0px;
        background-color: white;
    }
    
    QScrollBar:vertical {
        border: none;
        background-color: #5a026e;
        width: 10px;
        margin: 0px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #9a00bd;
        min-height: 20px;
    }
    
    QScrollBar::add-line:vertical {
        height: 0px;
    }
    
    QScrollBar::sub-line:vertical {
        height: 0px;
    }
    
    QScrollBar::add-page:vertical {
        background: none;
    }
    
    QScrollBar::sub-page:vertical {
        background: none;
    }
    
    
"""

PLAYLIST_DOWNLOAD_BUTTON_STYLESHEET: str = """
    QPushButton {
        background-color: #009614;
        color: black;
        font-size: 14px;
        font-weight: bold;
        padding: 5px;
        border-radius: 5px;
    }
    QPushButton:hover {
        background-color: #018212;
    }
    QPushButton:pressed {
        background-color: darkgreen;
    }
"""

PLAYLIST_TITLE_STYLESHEET = """
    QLabel {
        font-size: 24px;
        margin-top: 10px;
        border-top-left-radius: 5px;
        border-top-right-radius: 5px;
        font-weight: bold;
        color: white;
        background-color: #9a00bd;
    }
"""
