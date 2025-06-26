import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 Send a movie name to search from Archive.org!")

def search_archive(movie_name):
    query = f'title:("{movie_name}") AND mediatype:(movies)'
    params = {
        'q': query,
        'fl[]': ['identifier', 'title', 'description'],
        'rows': 1,
        'output': 'json'
    }
    res = requests.get("https://archive.org/advancedsearch.php", params=params)
    docs = res.json().get("response", {}).get("docs", [])

    if not docs:
        return None

    doc = docs[0]
    identifier = doc["identifier"]
    title = doc.get("title", "Untitled")
    description = doc.get("description", "No description available.")
    view_link = f"https://archive.org/details/{identifier}"
    download_link = f"https://archive.org/download/{identifier}/{identifier}_512kb.mp4"

    return f"""🎬 *{title}*
📝 {description}

▶️ [Watch on Archive.org]({view_link})
📥 [Download MP4]({download_link})
"""

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movie_name = update.message.text
    result = search_archive(movie_name)

    if result:
        await update.message.reply_text(result, parse_mode="Markdown", disable_web_page_preview=True)
    else:
        await update.message.reply_text("❌ Movie not found. Try another title.")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
app.run_polling()
