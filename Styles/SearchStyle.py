WINDOW_STYLESHEET = """
    QMainWindow {
        background-color: white;
    }
"""

URL_INPUT_STYLESHEET: str = """
    QLineEdit {
        padding: 5px;
        border: 2px solid #5a026e;
        border-radius: 5px;
        selection-background-color: #9a00bd;
        selection-color: white;
        font-size: 20px;
    }
    QLineEdit:focus {
        border: 2px solid #9a00bd;
    }
"""

SEARCH_BUTTON_STYLESHEET: str = """
    QPushButton {
        padding: 5px;
        border-radius: 5px;
        background-color: #9a00bd;
        color: black;
        font-size: 20px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #80039c;
    }
    QPushButton:pressed {
        background-color: #66017d;
    }
"""

LOADING_BUTTON_STYLESHEET: str = """
    QLabel {
        padding: 5px;
        border-radius: 5px;
        border: 2px solid #5a026e;
    }
"""

CANCEL_BUTTON_STYLESHEET: str = """
    QPushButton {
        padding: 5px;
        border-radius: 5px;
        background-color: #e3002a;
        color: black;
        font-size: 20px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #d9022a;
    }
    QPushButton:pressed {
        background-color: #c90227;
    }
"""

DIRECT_DOWNLOAD_BUTTON_STYLESHEET: str = """
    QPushButton {
        padding: 5px;
        border-radius: 5px;
        background-color: #00d45f;
        color: black;
        font-size: 20px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #02ab4e;
    }
    QPushButton:pressed {
        background-color: #019142;
    }
"""
