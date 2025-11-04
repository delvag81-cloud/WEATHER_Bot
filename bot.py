# bot.py
import logging

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import Message
from config import BOT_TOKEN, DEFAULT_CITY
from services import get_weather


logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# Команда /start
@dp.message(Command("start"))
async def start_command(message: Message):
    user = message.from_user
    welcome_text = f"""
👋 Привет, {user.first_name}!

Я бот погоды! Я могу показать тебе текущую погоду в любом городе.

📋 **Доступные команды:**
/start - Начать работу
/weather - Погода в {DEFAULT_CITY}
/help - Помощь

🌍 **Или просто напиши название города,** и я покажу погоду там!
    """
    await message.answer(welcome_text)


# Команда /help
@dp.message(Command("help"))
async def help_command(message: Message):
    help_text = f"""
📖 **Помощь по боту:**

• Используй /weather для получения погоды в {DEFAULT_CITY}
• Напиши название любого города для получения погоды там
• Пример: "Москва", "London", "Париж"

🌤️ Бот использует данные OpenWeatherMap
    """
    await message.answer(help_text)


# Команда /weather
@dp.message(Command("weather"))
async def weather_command(message: Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    weather_info = await get_weather(DEFAULT_CITY)
    await message.answer(weather_info, parse_mode="Markdown")


# Обработка текстовых сообщений с названиями городов
@dp.message(F.text & ~F.command)
async def handle_city_message(message: Message):
    city = message.text
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    weather_info = await get_weather(city)
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


async def run_bot():
    """Запуск Telegram бота"""
    logger.info("Бот запущен...")
    print("🤖 Бот погоды запущен!")
    await dp.start_polling(bot)
