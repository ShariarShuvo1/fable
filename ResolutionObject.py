class ResolutionObject:
    def __init__(self, tag, video_type, resolution, size, fps='Audio'):
        self.tag = tag
        self.video_type = video_type
        self.resolution = resolution
        self.size = size
        self.fps = fps

    def __str__(self):
        if self.fps != 'Audio':
            return f'{self.resolution} - {self.size} MB - {self.video_type} - {self.fps} fps'
        else:
            return f'{self.resolution} - {self.size} MB - {self.video_type}'
