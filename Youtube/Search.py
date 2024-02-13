import yt_dlp
import requests

from Entity.Resolution import Resolution
from Entity.Video import Video


def search_youtube(query, max_results=10, result_list=None):
    ydl_opts = {
        'quiet': True,
        'default_search': 'auto',
        'noplaylist': True,
        'max_results': max_results,
        'geo_bypass': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            search_results = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
            if result_list is not None:
                videos = []
                videos.extend(search_results.get('entries', []))
                for video in videos:
                    resolution_list = []
                    for format_item in video.get('formats', []):
                        if "vcodec" in format_item and "acodec" in format_item and "filesize" in format_item and "ext" in format_item and "url" in format_item and "vbr" in format_item and "abr" in format_item and "fps" in format_item and "height" in format_item:
                            if format_item.get("acodec").lower() != "none" and format_item.get(
                                    "vcodec").lower() == "none" and (
                                    str(format_item.get("abr")).lower() != "none" or str(
                                    format_item.get("abr")) != "0"):
                                new_resolution = Resolution(
                                    file_type="audio",
                                    abr=format_item.get("abr"),
                                    ext=format_item.get("ext"),
                                    filesize=format_item.get("filesize"),
                                    url=format_item.get("url"),
                                    acodec=format_item.get("acodec"),
                                )
                                resolution_list.append(new_resolution)
                            elif format_item.get("acodec").lower() == "none" and format_item.get(
                                    "vcodec").lower() != "none" and (
                                    str(format_item.get("vbr")).lower() != "none" or str(
                                    format_item.get("vbr")) != "0"):
                                new_resolution = Resolution(
                                    file_type="video",
                                    vbr=format_item.get("vbr"),
                                    ext=format_item.get("ext"),
                                    filesize=format_item.get("filesize"),
                                    url=format_item.get("url"),
                                    vcodec=format_item.get("vcodec"),
                                    fps=format_item.get("fps"),
                                    height=format_item.get("height"),
                                )
                                resolution_list.append(new_resolution)
                            elif format_item.get("acodec").lower() != "none" and format_item.get(
                                    "vcodec").lower() != "none" and (
                                    str(format_item.get("abr")).lower() != "none" or str(
                                    format_item.get("abr")) != "0") and (
                                    str(format_item.get("vbr")).lower() != "none" or str(
                                    format_item.get("vbr")) != "0"
                            ):
                                new_resolution = Resolution(
                                    file_type="mix",
                                    abr=format_item.get("abr"),
                                    vbr=format_item.get("vbr"),
                                    ext=format_item.get("ext"),
                                    filesize=format_item.get("filesize"),
                                    url=format_item.get("url"),
                                    acodec=format_item.get("acodec"),
                                    vcodec=format_item.get("vcodec"),
                                    fps=format_item.get("fps"),
                                    height=format_item.get("height"),
                                )
                                resolution_list.append(new_resolution)
                    video_obj = Video(
                        title=video.get('title'),
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
