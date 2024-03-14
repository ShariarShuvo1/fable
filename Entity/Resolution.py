class Resolution:
    def __init__(self, format_id: str, file_type: str, ext: str, filesize: int, url: str, fps: float = None,
                 abr: float = None, vbr: float = None, height: int = None):
        self.format_id: str = format_id
        self.file_type: str = file_type
        self.ext: str = ext
        self.filesize: int = filesize
        self.url: str = url
        self.fps: float | None = fps
        self.abr: float | None = abr
        self.vbr: float | None = vbr
        self.height: int | None = height

    def __str__(self):
        return f"Format ID: {self.format_id}, File Type: {self.file_type}, Extension: {self.ext}, File Size: {self.filesize}, " \
            f"URL: {self.url}, FPS: {self.fps}, ABR: {
                self.abr}, VBR: {self.vbr}, Height: {self.height}"
