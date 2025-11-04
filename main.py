# main.py
import asyncio
import logging
from threading import Thread

from bot import run_bot
from web_server import run_flask


# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


def main():
    """Основная функция запуска"""
    # Запускаем Flask в отдельном потоке
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Запускаем бота в основном потоке
    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
