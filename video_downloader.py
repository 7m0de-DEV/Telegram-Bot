import os
import shutil
import subprocess
import yt_dlp
from dir import cdir
from isURL import isURL


def download_video(query):
    output_dir = cdir("Music")

    if isURL(query):
        search_query = query
    else:
        search_query = f"ytsearch1:{query}"

    ffmpeg_path = os.environ.get("FFMPEG_PATH") or shutil.which("ffmpeg")

    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "noplaylist": True,
        "merge_output_format": "mp4",
        "postprocessor_args": ["-movflags", "+faststart"],
        "quiet": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"]
            }
        },
    }

    if ffmpeg_path:
        ydl_opts["ffmpeg_location"] = ffmpeg_path

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=True)
            if "entries" in info and info["entries"]:
                info = info["entries"][0]
            file_path = ydl.prepare_filename(info)
            if not os.path.exists(file_path):
                base_path = os.path.splitext(file_path)[0]
                if os.path.exists(base_path + ".mp4"):
                    file_path = base_path + ".mp4"
            return file_path, info
    except Exception as e:
        print(f"Primary video download failed: {e}")

    # Fallback with alternate player clients
    fallback_opts = ydl_opts.copy()
    fallback_opts["extractor_args"] = {
        "youtube": {
            "player_client": ["web"]
        }
    }

    try:
        with yt_dlp.YoutubeDL(fallback_opts) as ydl:
            info = ydl.extract_info(search_query, download=True)
            if "entries" in info and info["entries"]:
                info = info["entries"][0]
            file_path = ydl.prepare_filename(info)
            if not os.path.exists(file_path):
                base_path = os.path.splitext(file_path)[0]
                if os.path.exists(base_path + ".mp4"):
                    file_path = base_path + ".mp4"
            return file_path, info
    except Exception as e:
        print(f"Fallback video download failed: {e}")
        return None, None


def generate_thumbnail(video_path):
    if not video_path or not os.path.exists(video_path):
        return None
    thumb_path = video_path.rsplit(".", 1)[0] + "_thumb.jpg"
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                video_path,
                "-ss",
                "00:00:01",
                "-vframes",
                "1",
                "-vf",
                "scale=320:-2",
                thumb_path,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return thumb_path
    except Exception as e:
        print(f"Failed to generate thumbnail: {e}")
        return None
