import requests
from typing import List
from Entity.Resolution import Resolution


class Video:
    def __init__(self, title: str, uploader: str, view_count: int, duration: int, channel_url: str, thumbnail: requests.Response,
                 resolution_list: List[Resolution]):
        self.title: str = title
        self.uploader: str = uploader
        self.view_count: int = view_count
        self.duration: int = duration
        self.channel_url: str = channel_url
        self.thumbnail: requests.Response = thumbnail
        self.resolution_list: List[Resolution] = resolution_list