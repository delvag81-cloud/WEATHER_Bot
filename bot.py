import asyncio
from datetime import datetime
import logging
import os
from threading import Thread

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv
from flask import Flask
import requests


# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Загружаем переменные из .env
load_dotenv()

# Читаем ключи из переменных окружения
API_KEY = os.getenv("API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not API_KEY:
    raise ValueError("Не найден API_KEY в переменных окружения (.env)")
if not BOT_TOKEN:
    raise ValueError("Не найден BOT_TOKEN в переменных окружения (.env)")

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Создаем Flask приложение для хелс-чека
app = Flask(__name__)


@app.route("/")
def home():
    return "🤖 Weather Bot is running! Use Telegram to interact with the bot."


@app.route("/health")
def health():
    return "✅ Bot is healthy and running!"


def get_weather(city: str = "Saint Petersburg") -> str:
    """
    Получает данные о погоде для указанного города
    """
    try:
        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric",
            "lang": "ru",
        }

        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather", params=params
        )
        response.raise_for_status()
        data = response.json()

        # Форматируем данные о погоде
        weather_info = f"🌤️ **Погода в {data['name']}**\n\n"
        weather_info += (
            f"• **Описание:** {data['weather'][0]['description'].capitalize()}\n"
        )
        weather_info += f"• **Температура:** {data['main']['temp']} °C\n"
        weather_info += f"• **Ощущается как:** {data['main']['feels_like']} °C\n"
        weather_info += f"• **Влажность:** {data['main']['humidity']}%\n"
        weather_info += f"• **Давление:** {data['main']['pressure']} гПа\n"

        if "grnd_level" in data["main"]:
            weather_info += (
                f"• **Давление у земли:** {data['main']['grnd_level']} гПа\n"
            )

        weather_info += f"• **Скорость ветра:** {data['wind']['speed']} м/с\n"

        # Время заката
        sunset_timestamp = data["sys"]["sunset"]
        sunset_time = datetime.fromtimestamp(sunset_timestamp).strftime("%H:%M:%S")
        weather_info += f"• **Закат:** {sunset_time}\n"

        return weather_info

    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка запроса к API погоды: {e}")
        return "❌ Ошибка при получении данных о погоде. Попробуйте позже."
    except KeyError as e:
        logger.error(f"Ошибка парсинга данных: {e}")
        return "❌ Не удалось обработать данные о погоде."
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        return "❌ Произошла непредвиденная ошибка."


# Команда /start
@dp.message(Command("start"))
async def start_command(message: Message):
    user = message.from_user
    welcome_text = f"""
👋 Привет, {user.first_name}!

Я бот погоды! Я могу показать тебе текущую погоду в любом городе.

📋 **Доступные команды:**
/start - Начать работу
/weather - Погода в Санкт-Петербурге
/help - Помощь

🌍 **Или просто напиши название города,** и я покажу погоду там!
    """
    await message.answer(welcome_text)


# Команда /help
@dp.message(Command("help"))
async def help_command(message: Message):
    help_text = """
📖 **Помощь по боту:**

• Используй /weather для получения погоды в Санкт-Петербурге
• Напиши название любого города для получения погоды там
• Пример: "Москва", "London", "Париж"

🌤️ Бот использует данные OpenWeatherMap
    """
    await message.answer(help_text)


# Команда /weather
@dp.message(Command("weather"))
async def weather_command(message: Message):
    """Погода в Санкт-Петербурге по умолчанию"""
    weather_info = get_weather("Saint Petersburg")
    await message.answer(weather_info, parse_mode="Markdown")


# Обработка текстовых сообщений с названиями городов
@dp.message(F.text & ~F.command)
async def handle_city_message(message: Message):
    city = message.text

    # Показываем, что бот печатает
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")

    weather_info = get_weather(city)
    await message.answer(weather_info, parse_mode="Markdown")


# Обработка неизвестных команд
@dp.message(F.command)
async def handle_unknown(message: Message):
    await message.answer(
        "❓ Извините, я не понимаю эту команду.\n"
        "Используйте /help для просмотра доступных команд."
    )


# Обработка ошибок
@dp.error()
async def error_handler(update: types.Update, exception: Exception):
    logger.error(f"Ошибка при обработке сообщения: {exception}")
    return True


def run_flask():
    """Запуск Flask сервера для хелс-чека"""
    port = int(os.environ.get("PORT", 443))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


async def run_bot():
    """Запуск Telegram бота"""
    logger.info("Бот запущен...")
    print("🤖 Бот погоды запущен!")
    await dp.start_polling(bot)


def main():
    """Основная функция запуска"""
    # Запускаем Flask в отдельном потоке
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Запускаем бота в основном потоке
    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
