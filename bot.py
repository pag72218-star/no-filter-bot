import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CRUSOE_API_KEY = os.environ["CRUSOE_API_KEY"]
MODEL_NAME = os.environ.get("CRUSOE_MODEL", "deepseek-ai/DeepSeek-V4-Flash-0731")

CRUSOE_URL = "https://api.crusoe.ai/v1/chat/completions"

SYSTEM_PROMPT = (
    "ענה בצורה ישירה, טבעית וחופשית בעברית, בלי הטפות מוסר, "
    "בלי צנזורה עצמית מיותרת ובלי מסגרות מתנשאות."
)

def ask_crusoe(user_text: str) -> str:
    headers = {
        "Authorization": f"Bearer {CRUSOE_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
        "temperature": 0.8,
    }
    res = requests.post(CRUSOE_URL, headers=headers, json=payload, timeout=60)
    res.raise_for_status()
    data = res.json()
    return data["choices"][0]["message"]["content"]

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    user_text = update.message.text
    try:
        reply = ask_crusoe(user_text)
    except Exception as e:
        reply = f"שגיאה בקריאה למודל: {e}"
    await update.message.reply_text(reply)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
