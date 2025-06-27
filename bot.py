import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "7919706295:AAEiZTyzt92tmUbTwviROHgOkgQoL8_pNPA"

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

    # 🔍 Fetch real files from metadata
    metadata_url = f"https://archive.org/metadata/{identifier}"
    metadata = requests.get(metadata_url).json()
    files = metadata.get("files", [])

    # 🎯 Find the first MP4 file
    video_file = None
    for f in files:
        name = f.get("name", "")
        if name.endswith(".mp4"):
            video_file = name
            break

    if video_file:
        download_link = f"https://archive.org/download/{identifier}/{video_file}"
    else:
        download_link = "❌ No downloadable MP4 found."

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
