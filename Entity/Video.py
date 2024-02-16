import requests
from typing import List
from Entity.Resolution import Resolution


class Video:
    def __init__(self, video_url: str, title: str, uploader: str, view_count: int, duration: int, channel_url: str,
                 thumbnail: requests.Response,
                 resolution_list: List[Resolution]):
        self.video_url: str = video_url
        self.title: str = title
        self.uploader: str = uploader
        self.view_count: int = view_count
        self.duration: int = duration
        self.channel_url: str = channel_url
        self.thumbnail: requests.Response = thumbnail
        self.resolution_list: List[Resolution] = resolution_list

    def __str__(self):
        return f"Video URL: {self.video_url}, Title: {self.title}, Uploader: {self.uploader}, View Count: {self.view_count}, " \
               f"Duration: {self.duration}, Channel URL: {self.channel_url}, Thumbnail: {self.thumbnail}, " \
               f"Resolution List: {self.resolution_list}"
