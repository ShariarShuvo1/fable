from Entity.Video import Video
from Entity.VideoViewer import VideoViewer


def thumbnail_clicked(video: Video):
    viewer = VideoViewer(video)
    viewer.exec()
