import yt_dlp
from Youtube.Search import search_youtube


def search_youtube_playlist(query, thread, result_list=None):
    ydl_opts = {
        'quiet': True,
        'geo_bypass': True,
        'extract_flat': True,
        'dump_single_json': True,
        'force_generic_extractor': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            search_results = ydl.extract_info(query, download=False)
            if result_list is not None:
                videos = []
                videos.extend(search_results.get('entries', []))
                thread.total_videos.emit(len(videos))
                thread.completed_videos.emit(0)
                count = 0
                for video in videos:
                    url = video.get("url")
                    temp_list = []
                    search_youtube(url, 1, temp_list)
                    result_list.append(temp_list[0])
                    count += 1
                    thread.completed_videos.emit(count)

        except yt_dlp.DownloadError as e:
            print("Error:", e)
