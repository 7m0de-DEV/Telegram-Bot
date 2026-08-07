import os
import asyncio
import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TimedOut
from music_downloader import download_audio
from DBMS import log_activity

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Supported trigger commands the bot will react to in channel posts.
# The message must start with one of these (case-insensitive) followed by
# the song name or URL, e.g.:  /music Blinding Lights
# ---------------------------------------------------------------------------
MUSIC_TRIGGERS = ("/music", "/song")


def _parse_channel_music_request(text: str) -> str | None:
    """
    Check if a channel post is a music request.

    Returns the song name / URL if the message starts with a known trigger,
    or None if this message should be ignored.
    """
    if not text:
        return None

    lower = text.strip().lower()
    for trigger in MUSIC_TRIGGERS:
        if lower.startswith(trigger):
            # Everything after the trigger is the song name / URL
            song = text.strip()[len(trigger):].strip()
            return song if song else None

    return None


# ---------------------------------------------------------------------------
# Channel post handler
# ---------------------------------------------------------------------------

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Listens to every post made in a channel where the bot is an admin.

    If the post text starts with a music trigger command, the bot:
      1. Downloads the requested song.
      2. Sends the audio file back to the same channel.
      3. Deletes the original trigger message (if the bot has delete permission).

    Bot requirements in the channel:
      - Must be added as an Administrator.
      - Needs "Post Messages" and (optionally) "Delete Messages" permissions.
    """
    post = update.channel_post
    if not post or not post.text:
        return

    song_query = _parse_channel_music_request(post.text)
    if not song_query:
        return  # Not a music request — ignore

    channel_id = post.chat_id
    file_path = None

    logger.info(f"[channel] Music request in {channel_id}: '{song_query}'")

    # Acknowledge the request with a status message in the channel
    try:
        status = await context.bot.send_message(
            chat_id=channel_id,
            text=f"🎵 Searching for [{song_query}]...",
        )
    except Exception as e:
        logger.error(f"[channel] Could not send status message: {e}")
        return

    try:
        title, artist, file_path = await asyncio.to_thread(download_audio, song_query)

        if not file_path or not os.path.exists(file_path):
            await status.edit_text("❌ Could not find the song. Please check the name and try again.")
            return

        try:
            await log_activity(None, f"channel:{channel_id}", "download", song_query)
        except Exception as e:
            logger.warning(f"[channel] Logging failed: {e}")

        await status.edit_text("🎵 Sending the audio file, please wait...")

        with open(file_path, "rb") as audio_file:
            await context.bot.send_audio(
                chat_id=channel_id,
                audio=audio_file,
                title=title,
                performer=artist,
                read_timeout=120,
                write_timeout=120,
            )

        try:
            await log_activity(None, f"channel:{channel_id}", "upload", song_query)
        except Exception as e:
            logger.warning(f"[channel] Logging failed: {e}")

        # Delete the original trigger message and the status message
        try:
            await context.bot.delete_message(chat_id=channel_id, message_id=post.message_id)
        except Exception:
            pass  # Bot may not have delete permission — that's fine

        try:
            await status.delete()
        except Exception:
            pass

    except TimedOut:
        pass
    except Exception as e:
        logger.error(f"[channel] Error processing music request: {e}")
        try:
            await status.edit_text("❌ An error occurred while processing the request.")
        except Exception:
            pass
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
