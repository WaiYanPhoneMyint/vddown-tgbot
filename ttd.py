import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from yt_dlp import YoutubeDL
from pathlib import Path

# Get your bot token from environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Detect platform for logging or naming purposes
def detect_platform(url):
    if "tiktok.com" in url:
        return "TikTok"
    elif "youtube.com" in url or "youtu.be" in url:
        return "YouTube"
    elif "facebook.com" in url:
        return "Facebook"
    elif "twitter.com" in url or "x.com" in url:
        return "Twitter"
    elif "instagram.com" in url:
        return "Instagram"
    else:
        return "Unknown"

# Handle incoming messages
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    platform = detect_platform(url)
    await update.message.reply_text(f"📡 Platform: {platform}\n⏬ Downloading...")

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True,
        'noplaylist': True,
        'windowsfilenames': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        video_file = Path(filename)
        if not video_file.exists():
            # Try to find the actual file if extension changed
            possible_files = list(Path('.').glob(f"{video_file.stem}.*"))
            if possible_files:
                video_file = possible_files[0]

        if video_file.exists():
            await update.message.reply_video(video=open(video_file, 'rb'))
            video_file.unlink()  # Optional: delete after sending
        else:
            await update.message.reply_text("❌ Couldn't find the downloaded video.")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# Start the bot
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_video))
app.run_polling()
