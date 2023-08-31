import subprocess


class ResolutionObject:
    def __init__(self, source, tag, video_type, resolution, size, fps='Audio'):
        self.source = source
        self.tag = tag
        self.video_type = video_type
        self.resolution = resolution
        self.size = size
        self.fps = fps
        if source.is_progressive or 'audio' in self.video_type.lower():
            self.note = f'          No Render [Fast]'
        else:
            self.note = f'          iGPU Render [Slow]'
            try:
                subprocess.check_output('nvidia-smi')
                self.nvidia_available = True
            except Exception:
                self.nvidia_available = False
            if self.nvidia_available:
                self.note = f'          Nvidia Render [Super Fast]'

    def __str__(self):
        if self.fps != 'Audio':
            return f'{self.resolution} - {self.size} MB - {self.video_type} - {self.fps} fps - {self.note}'
        else:
            return f'{self.resolution} - {self.size} MB - {self.video_type} - {self.note}'
