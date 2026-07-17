from isURL import isURL
import yt_dlp
from dir import cdir
import subprocess

def download_video(query ) :

    output_dir = cdir("Music")
    
    if isURL(query) == True:
        search_query = query
    else:
        search_query = f"ytsearch1:{query}"

    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": f"{output_dir}/%(title)s.%(ext)s",
        "noplaylist": True,
        "merge_output_format": "mp4",
        "postprocessor_args": ["-movflags", "+faststart"],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(search_query, download=True)

        if "entries" in info:
            info = info["entries"][0]
        file_path = ydl.prepare_filename(info)

        return file_path, info

def generate_thumbnail(video_path):
    thumb_path = video_path.rsplit(".", 1)[0] + "_thumb.jpg"
    subprocess.run(
        ["ffmpeg", "-y", "-i", video_path, "-ss", "00:00:01",
         "-vframes", "1", "-vf", "scale=320:-2", thumb_path],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return thumb_path


