# services.py
from datetime import datetime
import logging

import aiohttp
from config import API_KEY


logger = logging.getLogger(__name__)

# Словарь для сопоставления погоды и эмодзи
WEATHER_ICONS = {
    "Clear": "☀️",
    "Clouds": "☁️",
    "Rain": "🌧️",
    "Drizzle": "🌦️",
    "Thunderstorm": "⛈️",
    "Snow": "❄️",
    "Mist": "🌫️",
    "Fog": "🌫️",
    "Haze": "🌫️",
    "Dust": "🌫️",
    "Sand": "🌫️",
    "Ash": "🌋",
    "Squall": "💨",
    "Tornado": "🌪️",
}


async def get_weather(city: str) -> str:
    """
    Асинхронно получает данные о погоде для указанного города.
    """
    try:
        params = {"q": city, "appid": API_KEY, "units": "metric", "lang": "ru"}

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.openweathermap.org/data/2.5/weather", params=params
            ) as response:
                response.raise_for_status()  # Проверка на HTTP ошибки
                data = await response.json()

        if data.get("cod") != 200:
            logger.warning(
                f"API вернуло ошибку для города '{city}': {data.get('message')}"
            )
            return f"❌ Город '{city}' не найден. Попробуйте другое название."

        weather_main = data["weather"][0]["main"]
        icon = WEATHER_ICONS.get(weather_main, "🌤️")

        weather_info = f"{icon} **Погода в {data['name']}**\n\n"
        weather_info += (
            f"• **Описание:** {data['weather'][0]['description'].capitalize()}\n"
        )
        weather_info += f"• **Температура:** {data['main']['temp']} °C (ощущается как {data['main']['feels_like']} °C)\n"
        weather_info += f"• **Влажность:** {data['main']['humidity']}%\n"
        weather_info += f"• **Давление:** {data['main']['pressure']} гПа\n"
        weather_info += f"• **Скорость ветра:** {data['wind'].get('speed', 0)} м/с\n"

        sunset_timestamp = data["sys"]["sunset"]
        sunset_time = datetime.fromtimestamp(sunset_timestamp).strftime("%H:%M:%S")
        weather_info += f"• **Закат:** {sunset_time}\n"

        return weather_info

    except aiohttp.ClientError as e:
        logger.error(f"Ошибка сети при запросе к API погоды: {e}")
        return "❌ Ошибка сети. Попробуйте позже."
    except Exception as e:
        logger.error(f"Неожиданная ошибка в get_weather: {e}")
        return "❌ Произошла непредвиденная ошибка."
