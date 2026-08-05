import logging
from DBMS import log_activity
import os
import asyncio
from shazamio import Shazam
from telegram import Update
from telegram.ext import  ContextTypes
from telegram.error import TimedOut
from music_downloader import download_audio
from video_downloader import download_video, generate_thumbnail
from instagram_downloader import download_reel
from tiktok_downloader import download_tiktok
from isURL import isURL
from dir import cdir

logging.basicConfig(
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("yt_dlp").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Hello, {user.first_name}! 👋\n"
        "Welcome to the bot.\n"
        "you can download video, song, Instagram reel or TikTok video in the best quality\n\n"
        "use /help for more information about using the bot"
    )

 
async def helP(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
    "use /music and type song name or URL\n\n"
    "use /video and type video name or URL\n\n"
    "use /insta and type Instagram Reel URL\n\n"
    "use /tiktok and type TikTok Video URL\n\n"
    "or if you dont know the name of your song\n"
    "send me audio file have part of the song\n"
    "I will recognazed it and upload it to you"
    )

async def about(update:Update,contxt:ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("this bot dev by " \
    "@R_vqa")


async def music(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text("pleas type song name or URL beside the command")
        return
    
    song_name = " ".join(context.args)
    file_path = None

    if isURL(song_name) == True:
        status_message = await update.message.reply_text("🔗 Searching for the URL...")
    else:
        status_message = await update.message.reply_text(f"Searching for [{song_name}] on YouTube...")

    
    try:

        title, artist, file_path = await asyncio.to_thread(download_audio,song_name)
        if not file_path or not os.path.exists(file_path):
            await status_message.edit_text("❌ Failed to download audio. Please check the song name or link and try again.")
            return

        try:
            await log_activity(update.effective_user.id, update.effective_user.username, "download", song_name)

        except Exception as e:
            print(f"Logging failed: {e}")

        await status_message.edit_text("🎵 Sending the audio file, please wait...")
                
        with open(file_path, 'rb') as audio_file:
            await update.message.reply_audio(
                audio=audio_file,
                title=title,        
                performer=artist,
                read_timeout=120,  
                write_timeout=120
            )
        try:
            await log_activity(update.effective_user.id, update.effective_user.username, "upload", song_name)
        except Exception as e:
            print(f"Logging failed: {e}")
    except TimedOut:
        
        pass 
    except Exception as e:
        
        print(f"Error: {e}")
            
    finally:
        
        try:
            await status_message.delete()
        except Exception:
            pass 
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

async def video(update:Update,context:ContextTypes.DEFAULT_TYPE):
    
    if not context.args:
        await update.message.reply_text("pleas type video name or URL beside the command")
        return
    
    video_name = " ".join(context.args)
    file_path = None
    thumb_path = None

    if isURL(video_name) == True:
        status_message = await update.message.reply_text("🔗 Searching for the URL...")
    else:
        status_message = await update.message.reply_text(f"Searching for [{video_name}] on YouTube...")

    try:

        file_path, info = await asyncio.to_thread(download_video, video_name)
        if not file_path or not os.path.exists(file_path):
            await status_message.edit_text("❌ Failed to download video. Please check the video name or link and try again.")
            return

        thumb_path = await asyncio.to_thread(generate_thumbnail, file_path)

        try:
            await log_activity(update.effective_user.id, update.effective_user.username, "download", video_name)
        except Exception as e:
            print(f"Logging failed: {e}")

        await status_message.edit_text(" 🎥 Sending the video file, please wait...")
                
        thumb_file = open(thumb_path, "rb") if thumb_path and os.path.exists(thumb_path) else None
        with open(file_path, 'rb') as video_file:
            await update.message.reply_video(
                video=video_file,
                duration=int(info.get("duration") or 0) if info else 0,
                width=info.get("width") or 0 if info else 0,
                height=info.get("height") or 0 if info else 0,
                supports_streaming=True,
                thumbnail=thumb_file,
                read_timeout=120,  
                write_timeout=120,
            )
        if thumb_file:
            thumb_file.close()
        try:
            await log_activity(update.effective_user.id, update.effective_user.username, "upload", video_name)
        except Exception as e:
            print(f"Logging failed: {e}")

    except TimedOut:
        
        pass 
    except Exception as e:
        
        print(f"Error: {e}")
            
    finally:
        
        try:
            await status_message.delete()
        except Exception:
            pass 
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        if thumb_path and os.path.exists(thumb_path):
            os.remove(thumb_path)

async def song_recognazed(update:Update,context:ContextTypes.DEFAULT_TYPE):

    status = await update.message.reply_text("🎧 Listening...")

    try:

        audio = update.message.audio
        file = await audio.get_file()
        local_path = cdir("downloads")
        local_path = os.path.join(local_path, file.file_unique_id) + ".mp3"
        file = await audio.get_file()
        await file.download_to_drive(local_path,read_timeout=120,write_timeout=120)

    except Exception as e:
        await status.edit_text(f"something went wrong with download the audio file {e}")

    try:
        shazam = Shazam()
        result = await shazam.recognize(local_path)

        track = result.get("track")
        if not track:
            await status.edit_text("Couldn't recognize that one — try a clearer clip.")
            os.remove(local_path)
            return
    except Exception as e:
        await status.edit_text(f"something went wrong with recognazed the song {e}")

    title = track["title"]
    artist = track["subtitle"]
    await status.edit_text(f"Found: song {title}\n by {artist} \n seending  the full song...")

    title, artist, file_path = await asyncio.to_thread( download_audio, title)

    try:
        await log_activity(update.effective_user.id, update.effective_user.username, "download", title)
    except Exception as e:
        print(f"Logging failed: {e}")
    
    try:

        with open(file_path, "rb") as audio_file:
            await update.message.reply_audio(audio=audio_file,
                title=title,
                performer=artist,
                read_timeout=120,
                write_timeout=120
                )
    except Exception as e:
        await status.edit_text(f"something went wrong with upload the song {e}")

    try:
        await log_activity(update.effective_user.id, update.effective_user.username, "upload", title)
    except Exception as e:
        print(f"Logging failed: {e}")

    await status.delete()
    
    if local_path and os.path.exists(local_path):
        os.remove(local_path)
    if file_path and os.path.exists(file_path):
        os.remove(file_path)


async def insta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("please type Instagram Reel URL beside the command")
        return

    url = context.args[0]
    file_path = None
    thumb_path = None

    if not isURL(url):
        await update.message.reply_text("please provide a valid URL")
        return

    status_message = await update.message.reply_text("🔗 Downloading Instagram Reel...")

    try:
        file_path, info = await asyncio.to_thread(download_reel, url)

        if not file_path or not os.path.exists(file_path):
            await status_message.edit_text("❌ Failed to download Instagram Reel. Please check the URL and try again.")
            return

        thumb_path = await asyncio.to_thread(generate_thumbnail, file_path)

        try:
            await log_activity(update.effective_user.id, update.effective_user.username, "download", url)
        except Exception as e:
            print(f"Logging failed: {e}")

        await status_message.edit_text("🎥 Sending the video file, please wait...")

        with open(file_path, "rb") as video_file:
            thumb_file = open(thumb_path, "rb") if thumb_path and os.path.exists(thumb_path) else None
            await update.message.reply_video(
                video=video_file,
                duration=int(info.get("duration") or 0) if info else 0,
                width=info.get("width") or 0 if info else 0,
                height=info.get("height") or 0 if info else 0,
                supports_streaming=True,
                thumbnail=thumb_file,
                read_timeout=120,
                write_timeout=120,
            )
            if thumb_file:
                thumb_file.close()

        try:
            await log_activity(update.effective_user.id, update.effective_user.username, "upload", url)
        except Exception as e:
            print(f"Logging failed: {e}")

    except TimedOut:
        pass
    except Exception as e:
        print(f"Error: {e}")
        try:
            await status_message.edit_text("❌ An error occurred while processing the request.")
        except Exception:
            pass
    finally:
        try:
            await status_message.delete()
        except Exception:
            pass
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        if thumb_path and os.path.exists(thumb_path):
            os.remove(thumb_path)


async def tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("please type TikTok Video URL beside the command")
        return

    url = context.args[0]
    file_path = None
    thumb_path = None

    if not isURL(url):
        await update.message.reply_text("please provide a valid URL")
        return

    status_message = await update.message.reply_text("🔗 Downloading TikTok Video...")

    try:
        file_path, info = await asyncio.to_thread(download_tiktok, url)

        if not file_path or not os.path.exists(file_path):
            await status_message.edit_text("❌ Failed to download TikTok Video. Please check the URL and try again.")
            return

        thumb_path = await asyncio.to_thread(generate_thumbnail, file_path)

        try:
            await log_activity(update.effective_user.id, update.effective_user.username, "download", url)
        except Exception as e:
            print(f"Logging failed: {e}")

        await status_message.edit_text("🎥 Sending the video file, please wait...")

        with open(file_path, "rb") as video_file:
            thumb_file = open(thumb_path, "rb") if thumb_path and os.path.exists(thumb_path) else None
            await update.message.reply_video(
                video=video_file,
                duration=int(info.get("duration") or 0) if info else 0,
                width=info.get("width") or 0 if info else 0,
                height=info.get("height") or 0 if info else 0,
                supports_streaming=True,
                thumbnail=thumb_file,
                read_timeout=120,
                write_timeout=120,
            )
            if thumb_file:
                thumb_file.close()

        try:
            await log_activity(update.effective_user.id, update.effective_user.username, "upload", url)
        except Exception as e:
            print(f"Logging failed: {e}")

    except TimedOut:
        pass
    except Exception as e:
        print(f"Error: {e}")
        try:
            await status_message.edit_text("❌ An error occurred while processing the request.")
        except Exception:
            pass
    finally:
        try:
            await status_message.delete()
        except Exception:
            pass
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        if thumb_path and os.path.exists(thumb_path):
            os.remove(thumb_path)


        