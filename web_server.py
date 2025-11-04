# web_server.py
import os

from flask import Flask


app = Flask(__name__)


@app.route("/")
def home():
    return "🤖 Weather Bot is running! Use Telegram to interact with the bot."


@app.route("/health")
def health():
    return "✅ Bot is healthy and running!"


def run_flask():
    """Запуск Flask сервера для хелс-чека"""
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
