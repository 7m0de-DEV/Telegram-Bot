import os
import yt_dlp
import shutil
from dir import cdir
from isURL import isURL


def download_audio(search_input):

    output_folder = cdir("Music")

    if isURL(search_input) == True:
        query = search_input
    else:
        query = f"ytsearch1:{search_input}"
    
    ffmpeg_path = os.environ.get("FFMPEG_PATH") or shutil.which("ffmpeg")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'writethumbnail': True,     
        'ffmpeg_location': ffmpeg_path,  
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
            {
                'key': 'EmbedThumbnail',  
            }
        ],
        'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': True, 
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(query, download=True)
            if 'entries' in info_dict:
                video_info = info_dict['entries'][0]
            else:
                video_info = info_dict
            
            song_title = video_info.get('title', 'Unknown Title')
            artist_name = video_info.get('artist') or video_info.get('uploader', 'Unknown Artist')
            if artist_name.endswith(" - Topic"):
                artist_name = artist_name.replace(" - Topic", "")

            
            downloaded_file = ydl.prepare_filename(video_info)
            full_path = os.path.splitext(downloaded_file)[0] + '.mp3'
            
            return song_title, artist_name, full_path
    except Exception as e:
        print(f"Error downloading: {e}")
        return None, None, None

