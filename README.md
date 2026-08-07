# 🤖 7mode Telegram Media Bot

A powerful Telegram bot that lets users download music, videos, Instagram Reels, and TikTok videos — all in the best quality. It also features Shazam-powered song recognition and an admin panel with activity logging.

---

## ✨ Features

- 🎵 **Music Download** — Search by name or URL (YouTube)
- 🎥 **Video Download** — Search by name or URL (YouTube) with thumbnail support
- 📸 **Instagram Reels** — Download reels by URL
- 🎶 **TikTok Videos** — Download TikTok videos by URL
- 🎧 **spotify music** - Download music from spotify by URL
- 🔍 **Song Recognition** — Send an audio clip and the bot identifies the song via Shazam, then sends the full track
- 🛡️ **Admin Panel** — Monitor and manage bot activity
- 💾 **Database Logging** — Tracks downloads and uploads per user

---

## 📁 Project Structure

```
Python-Bot/
├── main.py                  # Entry point — starts the bot
├── bot.py                   # Core bot handlers and command logic
├── music_downloader.py      # Handles music downloads via yt-dlp
├── video_downloader.py      # Handles video downloads + thumbnail generation
├── instagram_downloader.py  # Handles Instagram Reel downloads
├── tiktok_downloader.py     # Handles TikTok video downloads
├── isURL.py                 # Utility to detect if input is a URL or a name
├── dir.py                   # Creates Music/ and downloads/ directories
├── DBMS.py                  # Database module for activity logging
├── admin.py                 # Admin panel logic
├── downloads/               # Temporary storage for files sent by users
├── Music/                   # Temporary storage for files sent to users
├── .env                     # Your bot token (not committed)
├── .env.example             # Template for environment variables
|── requirements.txt         # Python dependencies
|── channel.py               # channel command
|── spotify_downloader.py    # handles music download from spotify
```

---

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/Python-Bot.git
cd Python-Bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> Make sure you have **FFmpeg** installed and available in your system PATH.

### 3. Configure your environment

Copy `.env.example` to `.env` and fill in your bot token:

```bash
cp .env.example .env
```

```env
BOT_TOKEN=your_telegram_bot_token_here
```

### 4. Run the bot

```bash
python main.py
```

---

## 💬 Bot Commands

| Command | Description |
|---|---|
| `/start` | Welcome message |
| `/help` | Show all available commands |
| `/about` | About the bot |
| `/music <name or URL>` | Download a song |
| `/video <name or URL>` | Download a video |
| `/insta <URL>` | Download an Instagram Reel |
| `/tiktok <URL>` | Download a TikTok video |
| `/spotify` | Download music from spotify |


> 💡 **Tip:** You can also send an audio file to the bot and it will recognize the song using Shazam, then send you the full track!

---

## 📦 Key Dependencies

| Package | Purpose |
|---|---|
| `python-telegram-bot` | Telegram Bot API wrapper |
| `yt-dlp` | YouTube & web video/audio downloading |
| `shazamio` | Async Shazam song recognition |
| `ffmpeg-python` | Video processing & thumbnail generation |
| `aiosqlite` | Async SQLite for activity logging |
| `python-dotenv` | Environment variable management |

---

## 📌 Changelog

### v1.0
- 🚀 Initial release with music, video download, and Shazam recognition

### v1.1
- ➕ DBMS module for saving user activity data
- ➕ Admin panel
- 🔧 Various bug fixes in `bot.py`

### v1.2
- ➕ TikTok video download by URL
- ➕ Instagram Reel download by URL

### v1.3
- ➕ download from spotify by URL
- ➕ the bot can be add to channel 
- ➕ fix some bugs

---

## 👤 Author

Developed by [@R_vqa](https://t.me/R_vqa)
