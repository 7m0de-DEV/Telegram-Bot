import os
import shutil
import yt_dlp
from dir import cdir
from isURL import isURL


def is_instagram_url(url: str) -> bool:
    """
    Check if the input string is a valid Instagram link.
    """
    if not isURL(url):
        return False
    url_lower = url.lower()
    return "instagram.com" in url_lower or "instagr.am" in url_lower


def download_reel(url: str):
    """
    Downloads an Instagram Reel or Video by its link.

    Args:
        url (str): Instagram Reel link/URL.

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
        "outtmpl": os.path.join(output_dir, "insta_%(id)s.%(ext)s"),
        "noplaylist": True,
        "merge_output_format": "mp4",
        "postprocessor_args": ["-movflags", "+faststart"],
        "quiet": True,
    }

    if ffmpeg_path:
        ydl_opts["ffmpeg_location"] = ffmpeg_path

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            if "entries" in info and info["entries"]:
                info = info["entries"][0]

            file_path = ydl.prepare_filename(info)

            # Check if file format was merged into .mp4
            if not os.path.exists(file_path):
                base_path = os.path.splitext(file_path)[0]
                if os.path.exists(base_path + ".mp4"):
                    file_path = base_path + ".mp4"

            return file_path, info
    except Exception as e:
        print(f"Error downloading Instagram Reel: {e}")
        return None, None


# Alias for convenience
download_instagram_reel = download_reel
