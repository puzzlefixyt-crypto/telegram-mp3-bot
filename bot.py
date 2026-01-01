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

BOT_TOKEN = "8208876135:AAGm9nOwTcyqR2WFNH-174PKecmUISKlS20"
CHANNEL_USERNAME = "@imdhaval_9999"

os.makedirs("downloads", exist_ok=True)

# 🔐 Verified users memory (restart ke baad reset hoga)
verified_users = set()

# ================= START COMMAND =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in verified_users:
        await send_welcome(update)
        return

    keyboard = [
        [InlineKeyboardButton("📢 Join Channel", url="https://t.me/imdhaval_9999")],
        [
            InlineKeyboardButton("✅ Joined", callback_data="joined"),
            InlineKeyboardButton("❌ Not Joined", callback_data="not_joined")
        ]
    ]

    await update.message.reply_text(
        "👋 *Welcome to YouTube MP3 Downloader Bot!* 🎧🎶\n\n"
        "📢 *Important Notice!*\n"
        "To use this bot, you must join our official channel first 👇\n\n"
        "✅ Join channel\n"
        "🔘 Click *Joined* to verify\n\n"
        "⚠️ Channel join is mandatory!",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= VERIFY BUTTON =================
async def verify_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "joined":
        try:
            member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
            if member.status in ["member", "administrator", "creator"]:
                verified_users.add(user_id)
                await query.edit_message_text(
                    "🎉 *Verification Successful!* ✅\n\n"
                    "🚀 You now have FULL UNLIMITED access!\n"
                    "👇 Send any YouTube link now",
                    parse_mode="Markdown"
                )
            else:
                await query.edit_message_text(
                    "❌ *You are not joined yet!* 😕\n\n"
                    "📢 Please join the channel first\n"
                    "🔄 Then click *Joined* again"
                )
        except:
            await query.edit_message_text(
                "⚠️ *Verification Error!* 😵\n\n"
                "👑 Make sure bot is admin in the channel"
            )

    elif query.data == "not_joined":
        await query.edit_message_text(
            "🚫 *Access Denied!* ❌\n\n"
            "📢 Channel join is compulsory to use this bot"
        )

# ================= WELCOME MESSAGE =================
async def send_welcome(update):
    welcome_msg = (
        "🎧 *Welcome to YouTube MP3 Downloader Bot!* 🎶\n\n"
        "✨ *UNLIMITED FEATURES:*\n"
        "📥 No file size limit (100MB+ OK!)\n"
        "⚡ Unlimited downloads\n"
        "📱 Perfect on mobile\n"
        "🌐 24/7 online FREE\n\n"
        "🔗 *How to use:*\n"
        "👉 Send any YouTube link\n"
        "🎵 Get full audio instantly\n\n"
        "🚀 *Unlimited mode activated!*\n"
        "👇 Send link now"
    )
    await update.message.reply_text(welcome_msg, parse_mode="Markdown")

# ================= AUDIO SENDER =================
async def send_audio(update, filepath, title, size_mb):
    try:
        with open(filepath, "rb") as audio:
            await update.message.reply_audio(
                audio=audio,
                title=title[:50],
                performer="UNLIMITED MP3 Bot",
                caption=(
                    f"✅ *{title[:30]}*\n"
                    f"📏 *{size_mb}MB* (Unlimited!)\n"
                    "📥 *Long press to save*"
                ),
                parse_mode="Markdown"
            )
        return True
    except:
        return False

# ================= URL HANDLER =================
async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in verified_users:
        await update.message.reply_text(
            "🚫 *Access Restricted!* ❌\n\n"
            "📢 Please join our channel first\n"
            "👉 Use /start to verify",
            parse_mode="Markdown"
        )
        return

    url = update.message.text.strip()

    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text(
            "❌ *Invalid URL!* 😕\n"
            "`https://youtu.be/VIDEO_ID`",
            parse_mode="Markdown"
        )
        return

    await update.message.reply_text("🔄 *Downloading audio...* 🎶", parse_mode="Markdown")

    for f in os.listdir("downloads"):
        os.remove(f"downloads/{f}")

    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "noplaylist": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", "Audio")

        for f in os.listdir("downloads"):
            filepath = f"downloads/{f}"
            size_mb = round(os.path.getsize(filepath) / (1024 * 1024), 1)

            await update.message.reply_text(
                f"📤 *Sending {size_mb}MB audio...*",
                parse_mode="Markdown"
            )

            if await send_audio(update, filepath, title, size_mb):
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