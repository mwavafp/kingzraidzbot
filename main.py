import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv

# Load variabel lingkungan
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Logging
logging.basicConfig(level=logging.INFO)

# Fungsi utama menangani pesan masuk
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text

    if "twitter.com" in message_text or "x.com" in message_text:
        await update.message.reply_text("Permintaan Anda telah ditambahkan ke antrean dan akan segera diproses.")
        await update.message.reply_text("AI sedang memproses jawaban...")

        tweet_text = extract_tweet_text(message_text)

        if not tweet_text:
            await update.message.reply_text("Gagal mengambil isi tweet.")
            return

        ai_reply = ask_gemini(tweet_text)

        keyboard = [[InlineKeyboardButton("SALIN KODE", callback_data="copy_code")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(ai_reply, reply_markup=reply_markup)

# Ekstrak isi tweet via scraping sederhana
def extract_tweet_text(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        if response.ok:
            start = response.text.find('<meta name="description" content="') + 34
            end = response.text.find('">', start)
            return response.text[start:end].strip()
        else:
            return None
    except:
        return None

# Fungsi untuk menghubungi Gemini AI
def ask_gemini(tweet_text):
    prompt = f"""You are a smart, insightful, and respected crypto influencer in the community.

Write a concise and impactful one-sentence reply (less than 120 characters) to the tweet below.

Apply the appropriate reply strategy:
- If the tweet is a Shit Post: Reply with humor or light sarcasm.
- If it's a Step-by-Step Guide: Ask thoughtful questions to continue the discussion.
- If it's Bulleted Content: Ask for clarification or priority.
- If it's a Showcase of Success: Offer congratulations in a classy tone.
- If it's an Engagement Post (GM/GN): Reply warmly.
- If it's In-Depth Educational Content: Show appreciation and ask about broader implications.

Restrictions:
- Use a comma for a natural pause mid-sentence.
- End with ONLY one punctuation mark (period or question mark).
- Do NOT use quotation marks, hashtags, exclamation marks, or semicolons.

Here is the tweet:
{tweet_text}
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    response = requests.post(url, json=payload)
    if response.ok:
        data = response.json()
        try:
            return data['candidates'][0]['content']['parts'][0]['text']
        except:
            return "AI gagal memberikan jawaban."
    else:
        return "Gagal menghubungi AI."

# Jalankan bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is running...")
    app.run_polling()
