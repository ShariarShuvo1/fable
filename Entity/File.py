from datetime import datetime

from Consts.Settings import *


class File:
    def __init__(self, title: str, webpage_url: str, format_id: str, download_url: str, file_type: str, status: str,
                 added_date: datetime, file_size: int | None = None, output_path: str = OUTPUT_PATH,
                 add_music: bool = False) -> None:
        self.title: str = title
        self.webpage_url: str = webpage_url
        self.format_id: str = format_id
        self.download_url: str = download_url
        self.file_type: str = file_type
        self.status: str = status
        self.added_date: datetime = added_date
        self.file_size: int = file_size
        self.output_path: str = output_path
        self.add_music: bool = add_music

    def __str__(self):
        return f"Title: {self.title}, Webpage URL: {self.webpage_url}, Format ID: {self.format_id}, " \
               f"Download URL: {self.download_url}, Output Path: {self.output_path}, File Type: {self.file_type}, " \
               f"Status: {self.status}, Added Date: {self.added_date}, File Size: {self.file_size}"

    def set_file_size(self, file_size: int) -> None:
        self.file_size = file_size

    def get_file_size(self) -> int | None:
        return self.file_size
