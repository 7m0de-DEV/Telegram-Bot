from bot import *
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.environ["token"]

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).concurrent_updates(True).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", helP))
    app.add_handler(CommandHandler("music", music))
    app.add_handler(CommandHandler("video", video))
    app.add_handler(CommandHandler("about",about))
    app.add_handler(MessageHandler(filters.AUDIO,song_recognazed))


    print("Bot is running... Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
