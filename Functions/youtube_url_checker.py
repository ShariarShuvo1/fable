import re


def is_youtube_url(text):
    youtube_regex = r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)"
    return re.match(youtube_regex, text) is not None


def is_youtube_playlist(url):
    playlist_pattern = r'^https?://(?:www\.)?youtube\.com/playlist\?list=[a-zA-Z0-9_-]+$'
    return bool(re.match(playlist_pattern, url))
