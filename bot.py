import os
import yt_dlp
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    Filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not set")

CHANNEL_USERNAME = "@imdhaval_9999"
CHANNEL_LINK = "https://t.me/imdhaval_9999"

os.makedirs("downloads", exist_ok=True)

verified_users = set()

def start(update, context):
    user_id = update.effective_user.id

    if user_id in verified_users:
        send_welcome(update, context)
        return

    keyboard = [
        [InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)],
        [
            InlineKeyboardButton("✅ Joined", callback_data="joined"),
            InlineKeyboardButton("❌ Not Joined", callback_data="not_joined")
        ]
    ]

    update.message.reply_text(
        "👋 Welcome to YouTube MP3 Downloader Bot 🎧\n\n"
        "Please join our channel first 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def verify(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()

    try:
        member = context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ["member", "administrator", "creator"]:
            verified_users.add(user_id)
            query.edit_message_text("✅ Verified! Send YouTube link now.")
        else:
            query.edit_message_text("❌ Join channel first.")
    except:
        query.edit_message_text("⚠️ Bot must be admin in channel.")

def send_welcome(update, context):
    update.message.reply_text(
        "🎶 Send YouTube link to download MP3"
    )

def handle_url(update, context):
    user_id = update.effective_user.id

    if user_id not in verified_users:
        update.message.reply_text("❌ Use /start and verify first")
        return

    url = update.message.text.strip()

    if "youtube.com" not in url and "youtu.be" not in url:
        update.message.reply_text("❌ Invalid YouTube link")
        return

    update.message.reply_text("⏳ Downloading audio...")

    for f in os.listdir("downloads"):
        os.remove("downloads/" + f)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "downloads/%(title)s.%(ext)s",
        "noplaylist": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get("title", "Audio")

    for f in os.listdir("downloads"):
        path = "downloads/" + f
        update.message.reply_audio(
            audio=open(path, "rb"),
            title=title[:60],
            caption="🎵 MP3 Ready"
        )
        os.remove(path)
        return

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(verify))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_url))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
