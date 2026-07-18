from dotenv import load_dotenv
import asyncio
from DBMS import get_global_stats,get_all_user_ids
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
import os

load_dotenv()

admin_ID = os.environ["admin_ID"]

def is_admin(user_id):
   
    return user_id == int(admin_ID)


keyboard_main = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Stats", callback_data="admin:stats")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin:broadcast")],
    ])

keyboard_back = InlineKeyboardMarkup([[
        InlineKeyboardButton("back",callback_data="admin:back")
    ]])


   
async def admin_panel(update:Update,context:ContextTypes.DEFAULT_TYPE):

    if not is_admin(update.effective_user.id):
        await update.message.reply_text("UnAuthorized")
        return

    
    await update.message.reply_text("🔧 Admin Panel", reply_markup=keyboard_main)


async def handle_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):


    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        await query.edit_message_text("Unauthorized.")
        return

    action = query.data.split(":")[1]


    if action == "stats":
        total_users, total_downloads, total_uploads = await get_global_stats()
        await query.edit_message_text(
            f"📊 Bot Stats\n\n"
            f"Total users: {total_users}\n"
            f"Total downloads: {total_downloads or 0}\n"
            f"Total uploads: {total_uploads or 0}",reply_markup=keyboard_back
        )

    elif action == "broadcast":
        context.user_data["awaiting_broadcast"] = True

        await query.edit_message_text("Send me the message you want to broadcast to all users.",reply_markup=keyboard_back)
    
    elif action == "back":
       
       context.user_data["awaiting_broadcast"] = False

       await query.edit_message_text("🔧 Admin Panel", reply_markup=keyboard_main)


async def handle_broadcast_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_broadcast"):
        return
    if not is_admin(update.effective_user.id):
        return

    context.user_data["awaiting_broadcast"] = False
    message_text = update.message.text
    user_ids = await get_all_user_ids()

    sent, failed = 0, 0
    for uid in user_ids:
        try:
            await context.bot.send_message(chat_id=uid, text=message_text)
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)  # stay well under Telegram's rate limits

    await update.message.reply_text(f"Broadcast done — sent: {sent}, failed: {failed}")



