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

TOOL_ICON_BUTTON_STYLESHEET: str = """
    QPushButton {
        background-color: transparent;
        border: none;
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