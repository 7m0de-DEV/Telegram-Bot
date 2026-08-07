import os
import re
import shutil
import subprocess
import glob
import requests
from dir import cdir


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def is_spotify_url(url: str) -> bool:
    """Return True if the string is a Spotify track URL."""
    return bool(re.search(r"open\.spotify\.com/track/", url, re.IGNORECASE))


def _fetch_spotify_metadata(url: str) -> dict:
    """
    Fetch track title, artist, and track cover URL via Spotify's public oEmbed
    endpoint — no API key required.

    oEmbed response fields used:
        title       → track name
        author_name → artist name (correct field, not parsed from title)
        thumbnail_url → track cover art (highest quality available)
    """
    meta = {"title": "", "artist": "", "thumbnail_url": ""}
    try:
        resp = requests.get(
            "https://open.spotify.com/oembed",
            params={"url": url},
            timeout=10,
        )
        if resp.ok:
            data = resp.json()
            meta["title"]         = data.get("title", "").strip()
            meta["artist"]        = data.get("author_name", "").strip()
            raw_thumb: str        = data.get("thumbnail_url", "")

            # Spotify oEmbed returns a low-res thumbnail (e.g. 300x300).
            # Replace the size token in the URL to request the largest size.
            # Spotify CDN URLs look like: .../image/<hash>
            # We can request full resolution by stripping the size suffix if present.
            meta["thumbnail_url"] = raw_thumb

    except Exception as e:
        print(f"[spotify] oEmbed lookup failed: {e}")
    return meta


def _download_thumbnail(thumbnail_url: str, dest_dir: str, stem: str) -> str | None:
    """
    Download the track cover art and save it as a .jpg.
    Returns the local file path, or None on failure.
    """
    if not thumbnail_url:
        return None
    try:
        resp = requests.get(thumbnail_url, timeout=15)
        resp.raise_for_status()
        thumb_path = os.path.join(dest_dir, f"{stem}_thumb.jpg")
        with open(thumb_path, "wb") as f:
            f.write(resp.content)
        return thumb_path
    except Exception as e:
        print(f"[spotify] Thumbnail download failed: {e}")
        return None


# ---------------------------------------------------------------------------
# Main public function
# ---------------------------------------------------------------------------

def download_spotify_track(url: str):
    """
    Download a Spotify track as an MP3 with its cover art thumbnail.

    Uses `spotdl` (https://github.com/spotDL/spotify-downloader) which
    fetches audio matched directly to the Spotify track and auto-embeds
    metadata + cover art into the MP3.

    The cover art is also saved separately so the bot can send it as a
    standalone photo message to the user.

    Requires `spotdl` to be installed:
        pip install spotdl

    Args:
        url (str): A Spotify track URL
                   (e.g. https://open.spotify.com/track/...).

    Returns:
        tuple: (title, artist, file_path, thumbnail_path)
               title          — track name from Spotify
               artist         — artist name from Spotify (via author_name)
               file_path      — absolute path to the downloaded .mp3
               thumbnail_path — absolute path to the saved cover art .jpg
                                (can be None if thumbnail download failed)
               Returns (None, None, None, None) on complete failure.
    """
    if not is_spotify_url(url):
        print("[spotify] Not a valid Spotify track URL.")
        return None, None, None, None

    output_dir  = cdir("Music")
    ffmpeg_path = os.environ.get("FFMPEG_PATH") or shutil.which("ffmpeg")
    spotdl_path = shutil.which("spotdl")

    if not spotdl_path:
        print("[spotify] spotdl is not installed. Run: pip install spotdl")
        return None, None, None, None

    # --- Step 1: resolve metadata ---
    meta           = _fetch_spotify_metadata(url)
    title          = meta["title"]  or "Unknown Title"
    artist         = meta["artist"] or "Unknown Artist"
    safe_stem      = re.sub(r'[\\/*?:"<>|]', "_", f"{title} - {artist}")

    print(f"[spotify] Resolved → '{title}' by '{artist}'")

    # --- Step 2: download the track cover art separately ---
    thumbnail_path = _download_thumbnail(meta["thumbnail_url"], output_dir, safe_stem)
    if thumbnail_path:
        print(f"[spotify] Cover art saved → {thumbnail_path}")
    else:
        print("[spotify] Cover art unavailable, continuing without thumbnail.")

    # --- Step 3: run spotdl to download the audio ---
    # spotdl auto-embeds the Spotify cover art and all ID3 tags into the MP3.
    cmd = [
        spotdl_path,
        "download",
        url,
        "--output",  output_dir,
        "--format",  "mp3",
        "--bitrate", "192k",
    ]

    if ffmpeg_path:
        cmd += ["--ffmpeg", ffmpeg_path]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,    # 5-minute timeout
        )
        if result.returncode != 0:
            print(f"[spotify] spotdl exited with code {result.returncode}")
            print(result.stderr)
            return None, None, None, None

    except subprocess.TimeoutExpired:
        print("[spotify] spotdl timed out.")
        return None, None, None, None
    except Exception as e:
        print(f"[spotify] spotdl error: {e}")
        return None, None, None, None

    # --- Step 4: locate the downloaded .mp3 ---
    # spotdl names files as "{artist} - {title}.mp3"
    file_path = None

    expected_name = re.sub(r'[\\/*?:"<>|]', "_", f"{artist} - {title}") + ".mp3"
    expected_path = os.path.join(output_dir, expected_name)
    if os.path.exists(expected_path):
        file_path = expected_path
    else:
        # Fall back: pick the most recently modified .mp3 in the output dir
        mp3_files = glob.glob(os.path.join(output_dir, "*.mp3"))
        if mp3_files:
            file_path = max(mp3_files, key=os.path.getmtime)

    if not file_path or not os.path.exists(file_path):
        print("[spotify] Could not locate the downloaded file.")
        return None, None, None, None

    print(f"[spotify] Download complete → {file_path}")
    return title, artist, file_path, thumbnail_path
