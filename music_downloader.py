import os
import shutil
import yt_dlp
from dir import cdir
from isURL import isURL


def download_audio(search_input):
    output_folder = cdir("Music")

    if isURL(search_input):
        query = search_input
    else:
        query = f"ytsearch1:{search_input}"

    ffmpeg_path = os.environ.get("FFMPEG_PATH") or shutil.which("ffmpeg")

    ydl_opts = {
        "format": "bestaudio/best",
        "writethumbnail": True,
        "ffmpeg_location": ffmpeg_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            },
            {
                "key": "EmbedThumbnail",
            },
        ],
        "outtmpl": os.path.join(output_folder, "%(title)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"]
            }
        },
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
        },
    }

    def attempt_download(opts):
        with yt_dlp.YoutubeDL(opts) as ydl:
            info_dict = ydl.extract_info(query, download=True)
            if not info_dict:
                return None, None, None

            if "entries" in info_dict and info_dict["entries"]:
                video_info = info_dict["entries"][0]
            else:
                video_info = info_dict

            song_title = video_info.get("title", "Unknown Title")
            artist_name = video_info.get("artist") or video_info.get(
                "uploader", "Unknown Artist"
            )
            if artist_name.endswith(" - Topic"):
                artist_name = artist_name.replace(" - Topic", "")

            downloaded_file = ydl.prepare_filename(video_info)
            full_path = os.path.splitext(downloaded_file)[0] + ".mp3"

            if os.path.exists(full_path):
                return song_title, artist_name, full_path

            if os.path.exists(downloaded_file):
                return song_title, artist_name, downloaded_file

            return song_title, artist_name, full_path

    # Try Primary Download
    try:
        title, artist, path = attempt_download(ydl_opts)
        if path and os.path.exists(path):
            return title, artist, path
    except Exception as e:
        print(f"Primary audio download attempt failed: {e}")

    # Fallback Download (without EmbedThumbnail & standard player client)
    fallback_opts = ydl_opts.copy()
    fallback_opts["postprocessors"] = [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ]
    fallback_opts["writethumbnail"] = False
    fallback_opts["extractor_args"] = {
        "youtube": {
            "player_client": ["web"]
        }
    }

    try:
        title, artist, path = attempt_download(fallback_opts)
        if path and os.path.exists(path):
            return title, artist, path
    except Exception as e:
        print(f"Fallback audio download attempt failed: {e}")

    return None, None, None
