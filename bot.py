from datetime import datetime
import logging
import os

from dotenv import load_dotenv
import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)


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
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    welcome_text = f"""
👋 Привет, {user.first_name}!

Я бот погоды! Я могу показать тебе текущую погоду в любом городе.

📋 **Доступные команды:**
/start - Начать работу
/weather - Погода в Санкт-Петербурге
/help - Помощь

🌍 **Или просто напиши название города,** и я покажу погоду там!
    """
    await update.message.reply_text(welcome_text)


# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📖 **Помощь по боту:**

• Используй /weather для получения погоды в Санкт-Петербурге
• Напиши название любого города для получения погоды там
• Пример: "Москва", "London", "Париж"

🌤️ Бот использует данные OpenWeatherMap
    """
    await update.message.reply_text(help_text)


# Команда /weather
async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Погода в Санкт-Петербурге по умолчанию"""
    weather_info = get_weather("Saint Petersburg")
    await update.message.reply_text(weather_info, parse_mode="Markdown")


# Обработка текстовых сообщений с названиями городов
async def handle_city_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text

    # Показываем, что бот печатает
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="typing"
    )

    weather_info = get_weather(city)
    await update.message.reply_text(weather_info, parse_mode="Markdown")


# Обработка неизвестных команд
async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ Извините, я не понимаю эту команду.\n"
        "Используйте /help для просмотра доступных команд."
    )


# Обработка ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Ошибка при обработке сообщения: {context.error}")
    try:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Произошла ошибка при обработке запроса. Попробуйте позже.",
        )
    except Exception:
        pass


def main():
    """Запуск бота"""
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("weather", weather_command))

    # Обработчик для сообщений с названиями городов (не команд)
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_city_message)
    )

    # Обработчик неизвестных команд
    application.add_handler(MessageHandler(filters.COMMAND, handle_unknown))

    # Обработчик ошибок
    application.add_error_handler(error_handler)

    # Запускаем бота
    logger.info("Бот запущен...")
    print("🤖 Бот погоды запущен! Нажмите Ctrl+C для остановки.")

    application.run_polling()


if __name__ == "__main__":
    main()
