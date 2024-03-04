import os


def get_default_download_folder():
    if os.name == 'nt':  # Windows
        import winreg
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            download_path = winreg.QueryValueEx(key, downloads_guid)[0]
    elif os.name == 'posix':  # macOS and Linux
        download_path = os.path.join(os.path.expanduser('~'), 'Downloads')
    else:
        download_path = None  # Unsupported OS
    return download_path


# OUTPUT_PATH: str = get_default_download_folder()
OUTPUT_PATH: str = "E:/Code/Projects/fable/vids"
ALWAYS_ASK_FOR_OUTPUT_PATH: bool = False
ALWAYS_ASK_TO_ADD_MUSIC: bool = True
MAXIMUM_SIMULTANEOUS_DOWNLOADS: int = 1
