from bot import start,helP,about,music,video,song_recognazed,insta,tiktok,spotify
from channel import handle_channel_post
from telegram.ext import filters,CommandHandler,MessageHandler,ApplicationBuilder,CallbackQueryHandler
from dotenv import load_dotenv
from admin import admin_panel, handle_admin_command, handle_broadcast_text
from DBMS import init_db
import asyncio
import os

load_dotenv()

BOT_TOKEN = os.environ["token"]

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).concurrent_updates(True).build()
    asyncio.get_event_loop().run_until_complete(init_db())

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", helP))
    app.add_handler(CommandHandler("music", music))
    app.add_handler(CommandHandler("video", video))
    app.add_handler(CommandHandler("insta", insta))
    app.add_handler(CommandHandler("tiktok", tiktok))
    app.add_handler(CommandHandler("tt", tiktok))
    app.add_handler(CommandHandler("spotify", spotify))
    app.add_handler(CommandHandler("about",about))
    app.add_handler(CommandHandler("admin",admin_panel))
    app.add_handler(CallbackQueryHandler(handle_admin_command, pattern="^admin:"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,handle_broadcast_text))

    app.add_handler(MessageHandler(filters.AUDIO, song_recognazed))
    app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POSTS & filters.TEXT, handle_channel_post))
    
    
    print("Bot is running... Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
