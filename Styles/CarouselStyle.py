CAROUSEL_BUTTON_STYLESHEET: str = """
    QPushButton {
        padding: 5px;
        border-radius: 5px;
        background-color: transparent;
    }
    QPushButton:hover {
        background-color: #f7e8fa;
    }
    QPushButton:pressed {
        background-color: #d6cad9;
    }
"""

CAROUSEL_BOX_STYLESHEET: str = """
    QWidget {
        padding: 2px;
        border-radius: 5px;
        background-color: #f7e8fa;
    }
"""

CAROUSEL_THUMBNAIL_STYLESHEET: str = """
    QLabel {
        padding: 0px;
        border-radius: 5px;
        margin-top: 1px;
        margin-bottom: 0px;
    }
"""

RESOLUTION_TITLE_STYLESHEET: str = """
    QLabel {
        font-size: 14px;
        padding: 0px;
        margin-top: 0px;
        font-weight: bold;
    }
"""

RESOLUTION_COMBOBOX_STYLESHEET = """
    QComboBox {
        border: 2px solid #555;
        border-radius: 5px;
        padding: 2px 2px 2px 2px;
        font-size: 14px;
        margin-left: 2px;
        margin-top: 4px;
    }

    QComboBox::drop-down {
        width: 30px;
        border-left: none;
    }

    QComboBox::down-arrow {
        image: url(./Assets/Icons/dropdown_arrow.png);
        width: 20px;
        height: 20px;
    }

    QComboBox::down-arrow:on {
        image: url(./Assets/Icons/dropdown_arrow_pressed.png);
    }

    QComboBox QAbstractItemView {
        background-color: #de8df0;
    }

    QScrollBar:vertical {
        background: #de8df0;
        width: 15px;
    }

    QScrollBar::handle:vertical {
        background: #9a00bd;
        border-radius: 7px;
    }

    QScrollBar::add-line:vertical {
        background: none;
        height: 20px;
        subcontrol-position: bottom;
        subcontrol-origin: margin;
    }

    QScrollBar::sub-line:vertical {
        background: none;
        height: 20px;
        subcontrol-position: top;
        subcontrol-origin: margin;
    }

    QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
        background: none;
    }
"""

DOWNLOAD_CURRENT_RES_BUTTON_STYLESHEET: str = """
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
"""

CAROUSEL_TITLE_STYLESHEET: str = """
    QLabel {
        font-size: 16px;
        padding: 0px;
        margin-top: 0px;
        font-weight: bold;
    }
"""

CAROUSEL_TITLE_BUTTON_STYLESHEET: str = """
    QPushButton {
        color: black;
        text-align: left;
        font-size: 16px;
        padding: 0px;
        margin-top: 0px;
        font-weight: bold;
    }
    QPushButton:hover {
        color: #9a00bd;
    }
"""

CAROUSEL_CHANNEL_STYLESHEET: str = """
    QPushButton {
        font-size: 14px;
        padding: 0px;
        margin-top: 0px;
        background-color: transparent;
        text-align: left;
    }
    QPushButton:hover {
        color: #9a00bd;
    }
"""

CAROUSEL_GENERAL_DATA_STYLESHEET: str = """
    QLabel {
        font-size: 13px;
        padding: 0px;
        margin: 0px;
    }
"""
