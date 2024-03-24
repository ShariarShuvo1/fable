import os
from PyQt6.QtCore import QSettings, QDir

settings = QSettings("Fable", "MySettings")


def set_setting(setting_name, value):
    if type(value) is bool and value:
        value = "true"
    elif type(value) is bool and not value:
        value = "false"
    settings.setValue(setting_name, value)


def get_setting(setting_name, default=None):
    value = settings.value(setting_name, default)
    if value == "true":
        return True
    elif value == "false":
        return False
    return value


def get_default_download_folder():
    if os.name == 'nt':
        import winreg
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            download_path = winreg.QueryValueEx(key, downloads_guid)[0]
    elif os.name == 'posix':
        download_path = QDir.homePath() + '/Downloads'
    else:
        download_path = None
    return download_path


if not settings.contains("OUTPUT_PATH"):
    set_setting("OUTPUT_PATH", get_default_download_folder())
if not settings.contains("ALWAYS_ASK_FOR_OUTPUT_PATH"):
    set_setting("ALWAYS_ASK_FOR_OUTPUT_PATH", "true")
if not settings.contains("ALWAYS_ASK_TO_ADD_MUSIC"):
    set_setting("ALWAYS_ASK_TO_ADD_MUSIC", "true")
if not settings.contains("ADD_MUSIC"):
    set_setting("ADD_MUSIC", "false")
if not settings.contains("MAXIMUM_SIMULTANEOUS_DOWNLOADS"):
    set_setting("MAXIMUM_SIMULTANEOUS_DOWNLOADS", 5)
if not settings.contains("MAXIMUM_SEARCH_RESULTS"):
    set_setting("MAXIMUM_SEARCH_RESULTS", 10)
if not settings.contains("PLAYLIST_OUTPUT_PATH"):
    set_setting("PLAYLIST_OUTPUT_PATH", get_default_download_folder())
if not settings.contains("ALWAYS_ASK_FOR_PLAYLIST_OUTPUT_PATH"):
    set_setting("ALWAYS_ASK_FOR_PLAYLIST_OUTPUT_PATH", "true")
if not settings.contains("AUDIO_STORY_OUTPUT_PATH"):
    set_setting("AUDIO_STORY_OUTPUT_PATH", get_default_download_folder())
if not settings.contains("ALWAYS_ASK_FOR_AUDIO_STORY_OUTPUT_PATH"):
    set_setting("ALWAYS_ASK_FOR_AUDIO_STORY_OUTPUT_PATH", "true")
if not settings.contains("ALWAYS_START_WITH_AUDIO_STORY_MODE"):
    set_setting("ALWAYS_START_WITH_AUDIO_STORY_MODE", "false")
if not settings.contains("ALWAYS_FAST_AUDIO_STORY_MODE"):
    set_setting("ALWAYS_FAST_AUDIO_STORY_MODE", "false")
if not settings.contains("VOLUME"):
    set_setting("VOLUME", 5)
if not settings.contains("ASK_BEFORE_DELETING"):
    set_setting("ASK_BEFORE_DELETING", "true")


def set_ask_before_deleting(value: bool):
    set_setting("ASK_BEFORE_DELETING", value)


def get_ask_before_deleting():
    return get_setting("ASK_BEFORE_DELETING")


def set_maximum_search_results(value: int):
    set_setting("MAXIMUM_SEARCH_RESULTS", value)


def get_maximum_search_results():
    return get_setting("MAXIMUM_SEARCH_RESULTS")


def set_volume(value: int):
    set_setting("VOLUME", value)


def get_volume():
    return get_setting("VOLUME")


def set_audio_story_output_path(path: str):
    set_setting("AUDIO_STORY_OUTPUT_PATH", path)


def get_audio_story_output_path():
    return get_setting("AUDIO_STORY_OUTPUT_PATH")


def set_always_ask_for_audio_story_output_path(value: bool):
    set_setting("ALWAYS_ASK_FOR_AUDIO_STORY_OUTPUT_PATH", value)


def get_always_ask_for_audio_story_output_path():
    return get_setting("ALWAYS_ASK_FOR_AUDIO_STORY_OUTPUT_PATH")


def set_always_fast_audio_story_mode(value: bool):
    set_setting("ALWAYS_FAST_AUDIO_STORY_MODE", value)


def get_always_fast_audio_story_mode():
    return get_setting("ALWAYS_FAST_AUDIO_STORY_MODE")


def set_always_start_with_audio_story_mode(value: bool):
    set_setting("ALWAYS_START_WITH_AUDIO_STORY_MODE", value)


def get_always_start_with_audio_story_mode():
    return get_setting("ALWAYS_START_WITH_AUDIO_STORY_MODE")


def set_add_music(value: bool):
    set_setting("ADD_MUSIC", value)


def get_add_music():
    return get_setting("ADD_MUSIC")


def set_output_path(path: str):
    set_setting("OUTPUT_PATH", path)


def get_output_path():
    return get_setting("OUTPUT_PATH")


def set_playlist_output_path(path: str):
    set_setting("PLAYLIST_OUTPUT_PATH", path)


def get_playlist_output_path():
    return get_setting("PLAYLIST_OUTPUT_PATH")


def set_always_ask_for_output_path(value: bool):
    set_setting("ALWAYS_ASK_FOR_OUTPUT_PATH", value)


def set_always_ask_for_playlist_output_path(value: bool):
    set_setting("ALWAYS_ASK_FOR_PLAYLIST_OUTPUT_PATH", value)


def get_ask_for_output_path():
    return get_setting("ALWAYS_ASK_FOR_OUTPUT_PATH")


def get_ask_for_playlist_output_path():
    return get_setting("ALWAYS_ASK_FOR_PLAYLIST_OUTPUT_PATH")


def set_always_ask_to_add_music(value: bool):
    set_setting("ALWAYS_ASK_TO_ADD_MUSIC", value)


def get_always_ask_to_add_music():
    return get_setting("ALWAYS_ASK_TO_ADD_MUSIC")


def set_maximum_simultaneous_downloads(value: int):
    set_setting("MAXIMUM_SIMULTANEOUS_DOWNLOADS", value)


def get_maximum_simultaneous_downloads():
    return get_setting("MAXIMUM_SIMULTANEOUS_DOWNLOADS")
