import yt_dlp
import requests
from Consts.VideoFormat import formats

from Entity.Resolution import Resolution
from Entity.Video import Video
from Functions.youtube_url_checker import is_youtube_url


def search_channel(url, begin, finish, result_list=None):
    ydl_opts = {
        'quiet': True,
        'playlist_items': f'{begin}-{finish}',
        'geo_bypass': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            if 'youtube.com' in url or 'youtu.be' in url:
                search_results = ydl.extract_info(url, download=False)
            if result_list is not None:
                videos = []
                videos.extend(search_results.get('entries', []))
                for video in videos:
                    res_dict = {
                        "video": [],
                        "audio": [],
                        "mix": []
                    }
                    for format_item in video.get('formats', []):
                        if format_item.get("format_id") in formats:
                            new_resolution = Resolution(
                                format_id=format_item.get("format_id"),
                                file_type=formats[format_item.get(
                                    "format_id")],
                                abr=format_item.get("abr"),
                                vbr=format_item.get("vbr"),
                                ext=format_item.get("ext"),
                                filesize=format_item.get("filesize"),
                                url=format_item.get("url"),
                                fps=format_item.get("fps"),
                                height=format_item.get("height"),
                            )
                            if formats[format_item.get("format_id")] == "video":
                                res_dict["video"].append(new_resolution)
                            elif formats[format_item.get("format_id")] == "audio":
                                res_dict["audio"].append(new_resolution)
                            else:
                                res_dict["mix"].append(new_resolution)
                    resolution_list = []
                    resolution_list.extend(res_dict["audio"])
                    resolution_list.extend(res_dict["mix"])
                    resolution_list.extend(res_dict["video"])
                    if is_youtube_url(url):
                        video_url = url
                    else:
                        video_url = video.get('webpage_url')
                    video_obj = Video(
                        title=video.get('title'),
                        video_url=video_url,
                        uploader=video.get('uploader'),
                        view_count=video.get('view_count', 0),
                        duration=video.get('duration', 0),
                        channel_url=video.get('channel_url'),
                        thumbnail=requests.get(video.get('thumbnail', '')),
                        resolution_list=resolution_list
                    )
                    result_list.append(video_obj)
        except yt_dlp.DownloadError as e:
            print("Error:", e)
            return
