import os


def get_default_download_folder():
    if os.name == 'nt':
        import winreg
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            download_path = winreg.QueryValueEx(key, downloads_guid)[0]
    elif os.name == 'posix':
        download_path = os.path.join(os.path.expanduser('~'), 'Downloads')
    else:
        download_path = None
    return download_path


OUTPUT_PATH = None
ALWAYS_ASK_FOR_OUTPUT_PATH = None
ALWAYS_ASK_TO_ADD_MUSIC = None
MAXIMUM_SIMULTANEOUS_DOWNLOADS = None

if os.path.exists("settings.txt"):
    with open("settings.txt", "r") as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith("OUTPUT_PATH:"):
                output_path_lst = line.split(":")[1:]
                OUTPUT_PATH = ":".join(output_path_lst).strip()
            elif line.startswith("ALWAYS_ASK_FOR_OUTPUT_PATH:"):
                ALWAYS_ASK_FOR_OUTPUT_PATH = line.split(
                    ":")[1].strip().lower() == "true"
            elif line.startswith("ALWAYS_ASK_TO_ADD_MUSIC:"):
                ALWAYS_ASK_TO_ADD_MUSIC = line.split(
                    ":")[1].strip().lower() == "true"
            elif line.startswith("ADD_MUSIC:"):
                ADD_MUSIC = line.split(":")[1].strip().lower() == "false"
            elif line.startswith("MAXIMUM_SIMULTANEOUS_DOWNLOADS:"):
                MAXIMUM_SIMULTANEOUS_DOWNLOADS = int(
                    line.split(":")[1].strip())
            elif line.startswith("MAXIMUM_SEARCH_RESULTS:"):
                MAXIMUM_SEARCH_RESULTS = int(line.split(":")[1].strip())
            elif line.startswith("PLAYLIST_OUTPUT_PATH:"):
                playlist_output_path_lst = line.split(":")[1:]
                PLAYLIST_OUTPUT_PATH = ":".join(
                    playlist_output_path_lst).strip()
            elif line.startswith("ALWAYS_ASK_FOR_PLAYLIST_OUTPUT_PATH:"):
                ALWAYS_ASK_FOR_PLAYLIST_OUTPUT_PATH = line.split(
                    ":")[1].strip().lower() == "true"
            elif line.startswith("AUDIO_STORY_OUTPUT_PATH:"):
                audio_story_output_path_lst = line.split(":")[1:]
                AUDIO_STORY_OUTPUT_PATH = ":".join(
                    audio_story_output_path_lst).strip()
            elif line.startswith("ALWAYS_ASK_FOR_AUDIO_STORY_OUTPUT_PATH:"):
                ALWAYS_ASK_FOR_AUDIO_STORY_OUTPUT_PATH = line.split(
                    ":")[1].strip().lower() == "true"
            elif line.startswith("ALWAYS_START_WITH_AUDIO_STORY_MODE:"):
                ALWAYS_START_WITH_AUDIO_STORY_MODE = line.split(
                    ":")[1].strip().lower() == "true"
            elif line.startswith("ALWAYS_FAST_AUDIO_STORY_MODE:"):
                ALWAYS_FAST_AUDIO_STORY_MODE = line.split(
                    ":")[1].strip().lower() == "true"
            elif line.startswith("VOLUME:"):
                VOLUME = int(line.split(":")[1].strip())
else:
    with open("settings.txt", "w") as file:
        OUTPUT_PATH = get_default_download_folder()
        file.write(f"OUTPUT_PATH: {OUTPUT_PATH}\n")
        ALWAYS_ASK_FOR_OUTPUT_PATH = True
        file.write(f"ALWAYS_ASK_FOR_OUTPUT_PATH: {
                   ALWAYS_ASK_FOR_OUTPUT_PATH}\n")
        ALWAYS_ASK_TO_ADD_MUSIC = True
        file.write(f"ALWAYS_ASK_TO_ADD_MUSIC: {ALWAYS_ASK_TO_ADD_MUSIC}\n")
        ADD_MUSIC = False
        file.write(f"ADD_MUSIC: {ADD_MUSIC}\n")
        MAXIMUM_SIMULTANEOUS_DOWNLOADS = 5
        file.write(f"MAXIMUM_SIMULTANEOUS_DOWNLOADS: {
                   MAXIMUM_SIMULTANEOUS_DOWNLOADS}\n")
        MAXIMUM_SEARCH_RESULTS = 10
        file.write(f"MAXIMUM_SEARCH_RESULTS: {MAXIMUM_SEARCH_RESULTS}\n")
        PLAYLIST_OUTPUT_PATH = get_default_download_folder()
        file.write(f"PLAYLIST_OUTPUT_PATH: {PLAYLIST_OUTPUT_PATH}\n")
        ALWAYS_ASK_FOR_PLAYLIST_OUTPUT_PATH = True
        file.write(f"ALWAYS_ASK_FOR_PLAYLIST_OUTPUT_PATH: {
                   ALWAYS_ASK_FOR_PLAYLIST_OUTPUT_PATH}\n")
        AUDIO_STORY_OUTPUT_PATH = get_default_download_folder()
        file.write(f"AUDIO_STORY_OUTPUT_PATH: {AUDIO_STORY_OUTPUT_PATH}\n")
        ALWAYS_ASK_FOR_AUDIO_STORY_OUTPUT_PATH = True
        file.write(f"ALWAYS_ASK_FOR_AUDIO_STORY_OUTPUT_PATH: {
                   ALWAYS_ASK_FOR_AUDIO_STORY_OUTPUT_PATH}\n")
        ALWAYS_START_WITH_AUDIO_STORY_MODE = False
        file.write(f"ALWAYS_START_WITH_AUDIO_STORY_MODE: {
                   ALWAYS_START_WITH_AUDIO_STORY_MODE}\n")
        ALWAYS_FAST_AUDIO_STORY_MODE = False
        file.write(f"ALWAYS_FAST_AUDIO_STORY_MODE: {
                   ALWAYS_FAST_AUDIO_STORY_MODE}\n")
        VOLUME = 5
        file.write(f"VOLUME: {VOLUME}\n")


def set_maximum_search_results(value: int):
    global MAXIMUM_SEARCH_RESULTS
    MAXIMUM_SEARCH_RESULTS = value
    with open("settings.txt", "r") as file:
        lines = file.readlines()
    with open("settings.txt", "w") as file:
        for line in lines:
            if line.startswith("MAXIMUM_SEARCH_RESULTS:"):
                file.write(f"MAXIMUM_SEARCH_RESULTS: {value}\n")
            else:
                file.write(line)


def get_maximum_search_results():
    return MAXIMUM_SEARCH_RESULTS


def set_volume(value: int):
    global VOLUME
    VOLUME = value
    with open("settings.txt", "r") as file:
        lines = file.readlines()
    with open("settings.txt", "w") as file:
        for line in lines:
            if line.startswith("VOLUME:"):
                file.write(f"VOLUME: {value}\n")
            else:
                file.write(line)


def get_volume():
    return VOLUME


def set_audio_story_output_path(path: str):
    global AUDIO_STORY_OUTPUT_PATH
    AUDIO_STORY_OUTPUT_PATH = path
    with open("settings.txt", "r") as file:
        lines = file.readlines()
    with open("settings.txt", "w") as file:
        for line in lines:
            if line.startswith("AUDIO_STORY_OUTPUT_PATH:"):
                file.write(f"AUDIO_STORY_OUTPUT_PATH: {path}\n")
            else:
                file.write(line)


def get_audio_story_output_path():
    return AUDIO_STORY_OUTPUT_PATH


def set_always_ask_for_audio_story_output_path(value: bool):
    global ALWAYS_ASK_FOR_AUDIO_STORY_OUTPUT_PATH
    ALWAYS_ASK_FOR_AUDIO_STORY_OUTPUT_PATH = value
    with open("settings.txt", "r") as file:
        lines = file.readlines()
    with open("settings.txt", "w") as file:
        for line in lines:
            if line.startswith(
                    "ALWAYS_ASK_FOR_AUDIO_STORY_OUTPUT_PATH:"):
                file.write(
                    f"ALWAYS_ASK_FOR_AUDIO_STORY_OUTPUT_PATH: {value}\n")
            else:
                file.write(line)


def get_always_ask_for_audio_story_output_path():
    return ALWAYS_ASK_FOR_AUDIO_STORY_OUTPUT_PATH


def set_always_fast_audio_story_mode(value: bool):
    global ALWAYS_FAST_AUDIO_STORY_MODE
    ALWAYS_FAST_AUDIO_STORY_MODE = value
    with open("settings.txt", "r") as file:
        lines = file.readlines()
    with open("settings.txt", "w") as file:
        for line in lines:
            if line.startswith("ALWAYS_FAST_AUDIO_STORY_MODE:"):
                file.write(f"ALWAYS_FAST_AUDIO_STORY_MODE: {value}\n")
            else:
                file.write(line)


def get_always_fast_audio_story_mode():
    return ALWAYS_FAST_AUDIO_STORY_MODE


def set_always_start_with_audio_story_mode(value: bool):
    global ALWAYS_START_WITH_AUDIO_STORY_MODE
    ALWAYS_START_WITH_AUDIO_STORY_MODE = value
    with open("settings.txt", "r") as file:
        lines = file.readlines()
    with open("settings.txt", "w") as file:
        for line in lines:
            if line.startswith("ALWAYS_START_WITH_AUDIO_STORY_MODE:"):
                file.write(f"ALWAYS_START_WITH_AUDIO_STORY_MODE: {value}\n")
            else:
                file.write(line)


def get_always_start_with_audio_story_mode():
    return ALWAYS_START_WITH_AUDIO_STORY_MODE


def set_add_music(value: bool):
    global ADD_MUSIC
    ADD_MUSIC = value
    with open("settings.txt", "r") as file:
        lines = file.readlines()
    with open("settings.txt", "w") as file:
        for line in lines:
            if line.startswith("ADD_MUSIC:"):
                file.write(f"ADD_MUSIC: {value}\n")
            else:
                file.write(line)


def get_add_music():
    return ADD_MUSIC


def set_output_path(path: str):
    global OUTPUT_PATH
    OUTPUT_PATH = path
    with open("settings.txt", "r") as file:
        lines = file.readlines()
    with open("settings.txt", "w") as file:
        for line in lines:
            if line.startswith("OUTPUT_PATH:"):
                file.write(f"OUTPUT_PATH: {path}\n")
            else:
                file.write(line)


if OUTPUT_PATH == "" or OUTPUT_PATH == " " or OUTPUT_PATH is None or not os.path.exists(OUTPUT_PATH):
    set_output_path(get_default_download_folder())


def get_output_path():
    return OUTPUT_PATH


def set_playlist_output_path(path: str):
    global PLAYLIST_OUTPUT_PATH
    PLAYLIST_OUTPUT_PATH = path
    with open("settings.txt", "r") as file:
        lines = file.readlines()
    with open("settings.txt", "w") as file:
        for line in lines:
            if line.startswith("PLAYLIST_OUTPUT_PATH:"):
                file.write(f"PLAYLIST_OUTPUT_PATH: {path}\n")
            else:
                file.write(line)


if PLAYLIST_OUTPUT_PATH == "" or PLAYLIST_OUTPUT_PATH == " " or PLAYLIST_OUTPUT_PATH is None or not os.path.exists(
        PLAYLIST_OUTPUT_PATH):
    set_playlist_output_path(get_default_download_folder())


def get_playlist_output_path():
    return PLAYLIST_OUTPUT_PATH


def set_always_ask_for_output_path(value: bool):
    global ALWAYS_ASK_FOR_OUTPUT_PATH
    ALWAYS_ASK_FOR_OUTPUT_PATH = value
    with open("settings.txt", "r") as file:
        lines = file.readlines()
    with open("settings.txt", "w") as file:
        for line in lines:
            if line.startswith("ALWAYS_ASK_FOR_OUTPUT_PATH:"):
                file.write(f"ALWAYS_ASK_FOR_OUTPUT_PATH: {value}\n")
            else:
                file.write(line)


def set_always_ask_for_playlist_output_path(value: bool):
    global ALWAYS_ASK_FOR_PLAYLIST_OUTPUT_PATH
    ALWAYS_ASK_FOR_PLAYLIST_OUTPUT_PATH = value
    with open("settings.txt", "r") as file:
        lines = file.readlines()
    with open("settings.txt", "w") as file:
        for line in lines:
            if line.startswith("ALWAYS_ASK_FOR_PLAYLIST_OUTPUT_PATH:"):
                file.write(f"ALWAYS_ASK_FOR_PLAYLIST_OUTPUT_PATH: {value}\n")
            else:
                file.write(line)


def get_ask_for_output_path():
    return ALWAYS_ASK_FOR_OUTPUT_PATH


def get_ask_for_playlist_output_path():
    return ALWAYS_ASK_FOR_PLAYLIST_OUTPUT_PATH


def set_always_ask_to_add_music(value: bool):
    global ALWAYS_ASK_TO_ADD_MUSIC
    ALWAYS_ASK_TO_ADD_MUSIC = value
    with open("settings.txt", "r") as file:
        lines = file.readlines()
    with open("settings.txt", "w") as file:
        for line in lines:
            if line.startswith("ALWAYS_ASK_TO_ADD_MUSIC:"):
                file.write(f"ALWAYS_ASK_TO_ADD_MUSIC: {value}\n")
            else:
                file.write(line)


def get_always_ask_to_add_music():
    return ALWAYS_ASK_TO_ADD_MUSIC


def set_maximum_simultaneous_downloads(value: int):
    global MAXIMUM_SIMULTANEOUS_DOWNLOADS
    MAXIMUM_SIMULTANEOUS_DOWNLOADS = value
    with open("settings.txt", "r") as file:
        lines = file.readlines()
    with open("settings.txt", "w") as file:
        for line in lines:
            if line.startswith("MAXIMUM_SIMULTANEOUS_DOWNLOADS:"):
                file.write(f"MAXIMUM_SIMULTANEOUS_DOWNLOADS: {value}\n")
            else:
                file.write(line)


def get_maximum_simultaneous_downloads():
    return MAXIMUM_SIMULTANEOUS_DOWNLOADS
