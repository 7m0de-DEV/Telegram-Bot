import os
import shutil
import json
import urllib.parse
import urllib.request
import yt_dlp
from dir import cdir
from isURL import isURL


def is_tiktok_url(url: str) -> bool:
    """
    Check if the input string is a valid TikTok link.
    """
    if not isURL(url):
        return False
    url_lower = url.lower()
    return (
        "tiktok.com" in url_lower
        or "vm.tiktok.com" in url_lower
        or "vt.tiktok.com" in url_lower
    )


def download_via_tikwm(url: str, output_dir: str):
    """
    Fallback method to download TikTok video via TikWM API (no watermark).
    """
    try:
        api_url = f"https://www.tikwm.com/api/?url={urllib.parse.quote(url)}"
        req = urllib.request.Request(
            api_url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                )
            },
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            res_data = json.loads(response.read().decode("utf-8"))

        if res_data.get("code") == 0 and "data" in res_data:
            data = res_data["data"]
            video_url = data.get("play") or data.get("wmplay")
            video_id = data.get("id", "video")
            title = data.get("title", "TikTok Video")
            duration = data.get("duration", 0)

            if video_url:
                file_path = os.path.join(output_dir, f"tiktok_{video_id}.mp4")
                v_req = urllib.request.Request(
                    video_url,
                    headers={
                        "User-Agent": (
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                        )
                    },
                )
                with urllib.request.urlopen(v_req, timeout=30) as v_res, open(
                    file_path, "wb"
                ) as f:
                    shutil.copyfileobj(v_res, f)

                info = {
                    "id": video_id,
                    "title": title,
                    "duration": duration,
                    "width": 0,
                    "height": 0,
                }
                return file_path, info
    except Exception as e:
        print(f"TikWM fallback failed: {e}")

    return None, None


def download_tiktok(url: str):
    """
    Downloads a TikTok video by its link.
    Tries yt-dlp first, and falls back to TikWM API if needed.

    Args:
        url (str): TikTok video link/URL.

    Returns:
        tuple: (file_path, info_dict) if successful, or (None, None) if download fails.
    """
    if not isURL(url):
        print("Error: Invalid URL provided.")
        return None, None

    output_dir = cdir("downloads")
    ffmpeg_path = os.environ.get("FFMPEG_PATH") or shutil.which("ffmpeg")

    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": os.path.join(output_dir, "tiktok_%(id)s.%(ext)s"),
        "noplaylist": True,
        "merge_output_format": "mp4",
        "postprocessor_args": ["-movflags", "+faststart"],
        "quiet": True,
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/avif,image/webp,*/*;q=0.8"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        },
    }

    if ffmpeg_path:
        ydl_opts["ffmpeg_location"] = ffmpeg_path

    # Try yt-dlp first
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            if "entries" in info and info["entries"]:
                info = info["entries"][0]

            file_path = ydl.prepare_filename(info)

            if not os.path.exists(file_path):
                base_path = os.path.splitext(file_path)[0]
                if os.path.exists(base_path + ".mp4"):
                    file_path = base_path + ".mp4"

            if file_path and os.path.exists(file_path):
                return file_path, info
    except Exception as e:
        print(f"yt-dlp failed for TikTok link, attempting fallback: {e}")

    # Fallback to TikWM API
    return download_via_tikwm(url, output_dir)


# Alias for convenience
download_tiktok_video = download_tiktok
