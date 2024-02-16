import os


def get_download_folder():
    if os.name == 'nt':
        import winreg
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders'
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            download_path = winreg.QueryValueEx(key, downloads_guid)[0]
        return download_path
    elif os.name == 'posix':
        home = os.path.expanduser('~')
        try:
            with open(os.devnull, 'wb') as devnull:
                download_path = os.path.realpath(os.path.join(home, '.config/user-dirs.dirs'))
                with open(download_path, 'rb') as config_file:
                    for line in config_file:
                        line = line.decode(errors='ignore')
                        if line.startswith('XDG_DOWNLOAD_DIR'):
                            download_path = line.split('=')[1].strip().strip('"')
                            return os.path.expanduser(download_path)
        except Exception as e:
            print("Error:", e)
            return os.path.join(home, 'Downloads')
    else:
        return None


OUTPUT_PATH: str = get_download_folder()
ALWAYS_ASK_FOR_OUTPUT_PATH: bool = False
ALWAYS_ASK_TO_ADD_MUSIC: bool = False
MAXIMUM_SIMULTANEOUS_DOWNLOADS: int = 1
