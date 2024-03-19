from datetime import datetime

from Entity.File import File


class AudioStory:
    def __init__(self,
                 url_list: list[str],
                 status: str,
                 added_date: datetime,
                 out_path: str,
                 title: str = None,
                 file_list: list[File] = None,
                 ):
        self.url_list = url_list
        self.status = status
        self.added_date = added_date
        self.out_path = out_path
        self.title = title
        self.file_list = file_list

    def set_title(self, title: str):
        self.title = title

    def set_file_list(self, file_list: list[File]):
        self.file_list = file_list

    def set_status(self, status: str):
        self.status = status
