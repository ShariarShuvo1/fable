class Resolution:
    def __init__(self, file_type: str, ext: str, filesize: int, url: str, acodec: str = None,
                 vcodec: str = None, fps: float = None, abr: float = None, vbr: float = None, height:int = None):
        self.file_type: str = file_type
        self.ext: str = ext
        self.filesize: int = filesize
        self.url: str = url
        self.acodec: str | None = acodec
        self.vcodec: str | None = vcodec
        self.fps: float | None = fps
        self.abr: float | None = abr
        self.vbr: float | None = vbr
        self.height: int | None = height
