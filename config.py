# config.py
import os

from dotenv import load_dotenv


# Загружаем переменные из .env
load_dotenv()

# Читаем ключи из переменных окружения
API_KEY = os.getenv("API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
DEFAULT_CITY = os.getenv("DEFAULT_CITY", "Saint Petersburg")

# Проверяем наличие необходимых переменных
if not API_KEY:
    raise ValueError("Не найден API_KEY в переменных окружения (.env)")
if not BOT_TOKEN:
    raise ValueError("Не найден BOT_TOKEN в переменных окружения (.env)")
