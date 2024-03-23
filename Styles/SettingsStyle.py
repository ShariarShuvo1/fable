SETTINGS_LABEL_STYLE = """
    QLabel {
        font-size: 14px;
    }
"""

OUTPUT_PATH_BUTTON_STYLE = """
    QPushButton {
        border-radius: 5px;
        padding: 5px;
        border: 1px solid black;
        font-size: 14px;
    }
    QPushButton:hover {
        background-color: #e15cff;
    }
    QPushButton:pressed {
        background-color: #c954e3;
    }
"""
WHAT_IS_AUDIO_STORY_BUTTON_STYLE = """
    QPushButton {
        background-color: transparent;
    }
    QPushButton:hover {
        background-color: #e15cff;
        border-radius: 5px;
    }
"""

OUTPUT_PATH_LABEL_STYLE = """
    QLabel {
        font-size: 14px;
    }
    QCheckBox {
        font-size: 16px;
        padding: 5px;
        border-radius: 5px;
    }
    QCheckBox:checked {
        background-color: #e15cff;
    }
    QCheckBox:hover {
        background-color: #ec99ff;
    }
    QCheckBox:pressed {
        background-color: #e15cff;
    }
    QCheckBox::indicator:checked {
        background-color: #8400ff;
        border-radius: 5px;
    }
    QCheckBox:checked:hover {
        background-color: #e15cff;
    }
    QCheckBox:checked:pressed {
        background-color: #e15cff;
    }
    QSpinBox {
        padding: 5px;
        border-radius: 5px;
        font-size: 16px;
        background-color: transparent;
        border: 1px solid black;
    }
    QSpinBox:hover {
        background-color: #e15cff;
    }
    QSpinBox::up-button {
        subcontrol-origin: border;
        subcontrol-position: top right;
        width: 16px;
        border-image: url(./Assets/Icons/dropdown_arrow_pressed.png);
    }
    QSpinBox::down-button {
        subcontrol-origin: border;
        subcontrol-position: bottom right;
        width: 16px;
        border-image: url(./Assets/Icons/dropdown_arrow.png);
    }
    QSpinBox::up-button:hover {
        background-color: #c954e3;
        border-radius: 5px;
    }
    QSpinBox::down-button:hover {
        background-color: #c954e3;
        border-radius: 5px;
    }
    QSpinBox::up-button:pressed {
        background-color: #b44bcc;
    }
    QSpinBox::down-button:pressed {
        background-color: #b44bcc;
    }
    
"""

RADIO_BUTTON_STYLE = """
    QRadioButton {
        padding: 5px;
        border-radius: 5px;
        font-size: 20px;
    }
    QRadioButton:hover {
        background-color: #ec99ff;
    }
    QRadioButton:pressed {
        background-color: #e15cff;
    }
    QRadioButton:checked {
        background-color: #e15cff;
    }
    QRadioButton::indicator:checked {
        background-color: blue;
    }
    
"""

DONE_SETTINGS_BUTTON_STYLE = """
    QPushButton {
        padding: 5px;
        border-radius: 5px;
        background-color: #008531;
        color: white;
        font-size: 20px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #01702a;
    }
    QPushButton:pressed {
        background-color: #015e23;
    }
"""

RESTORE_SETTINGS_BUTTON_STYLE = """
    QPushButton {
        padding: 5px;
        border-radius: 5px;
        background-color: #9a00bd;
        color: white;
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
