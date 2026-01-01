import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
import yt_dlp

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable not set")

CHANNEL_USERNAME = "@imdhaval_9999"
CHANNEL_LINK = "https://t.me/imdhaval_9999"

os.makedirs("downloads", exist_ok=True)

verified_users = set()

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in verified_users:
        await send_welcome(update)
        return

    keyboard = [
        [InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)],
        [
            InlineKeyboardButton("✅ Joined", callback_data="joined"),
            InlineKeyboardButton("❌ Not Joined", callback_data="not_joined"),
        ],
    ]

    await update.message.reply_text(
        "👋 *Welcome to YouTube MP3 Downloader Bot!* 🎧🎶\n\n"
        "📢 To use this bot, please join our channel first 👇\n\n"
        "After joining, click *Joined* ✅",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

# ================= VERIFY =================
async def verify_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "joined":
        try:
            member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
            if member.status in ("member", "administrator", "creator"):
                verified_users.add(user_id)
                await query.edit_message_text(
                    "🎉 *Verification Successful!* ✅\n\n"
                    "👇 Send any YouTube link now",
                    parse_mode="Markdown",
                )
            else:
                await query.edit_message_text(
                    "❌ *You have not joined yet!* 😕\n"
                    "Please join the channel and try again."
                )
        except Exception:
            await query.edit_message_text(
                "⚠️ Verification failed.\nMake sure bot is admin in channel."
            )

    elif query.data == "not_joined":
        await query.edit_message_text(
            "🚫 Channel join is mandatory to use this bot."
        )

# ================= WELCOME =================
async def send_welcome(update: Update):
    await update.message.reply_text(
        "🎧 *YouTube MP3 Downloader Bot Ready!* 🎶\n\n"
        "✨ *Features:*\n"
        "⚡ Unlimited downloads\n"
        "📥 No size limit\n"
        "📱 Mobile friendly\n\n"
        "👇 Send YouTube link now",
        parse_mode="Markdown",
    )

# ================= AUDIO SEND =================
async def send_audio(update, filepath, title, size_mb):
    with open(filepath, "rb") as audio:
        await update.message.reply_audio(
            audio=audio,
            title=title[:60],
            performer="UNLIMITED MP3 Bot",
            caption=(
                f"🎵 *{title[:30]}*\n"
                f"📏 *{size_mb} MB*\n"
                "📥 Long press to save"
            ),
            parse_mode="Markdown",
        )

# ================= URL HANDLER =================
async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in verified_users:
        await update.message.reply_text(
            "🚫 *Access Restricted!*\n"
            "Please use /start and verify first.",
            parse_mode="Markdown",
        )
        return

    url = update.message.text.strip()

    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text(
            "❌ Invalid YouTube link!",
            parse_mode="Markdown",
        )
        return

    await update.message.reply_text(
        "🔄 Downloading audio...",
        parse_mode="Markdown",
    )

    # clean old files
    for f in os.listdir("downloads"):
        os.remove(os.path.join("downloads", f))

    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "noplaylist": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", "Audio")

        for f in os.listdir("downloads"):
            filepath = os.path.join("downloads", f)
            size_mb = round(os.path.getsize(filepath) / (1024 * 1024), 1)
            await send_audio(update, filepath, title, size_mb)
            os.remove(filepath)
            return

        await update.message.reply_text("❌ No audio found")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)[:80]}")

# ================= MAIN =================
def main():
    print("🚀 UNLIMITED MP3 BOT STARTED")
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(verify_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))

    app.run_polling()

if __name__ == "__main__":
    main()
