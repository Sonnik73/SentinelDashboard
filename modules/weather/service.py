from datetime import datetime
from core.cache import load_cache, save_cache
from core.time import now_string
import httpx




CITIES = [
    {
        "name": "Москва",
        "latitude": 55.7558,
        "longitude": 37.6173,
    },
    {
        "name": "Краснодар",
        "latitude": 45.0355,
        "longitude": 38.9753,
    },
    {
        "name": "Ульяновск",
        "latitude": 54.3142,
        "longitude": 48.4031,
    },
]




def fetch_city_weather(city):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": city["latitude"],
        "longitude": city["longitude"],
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        "timezone": "Europe/Moscow",
    }

    response = httpx.get(url, params=params, timeout=5)
    response.raise_for_status()

    data = response.json()
    current = data["current"]

    return {
        "name": city["name"],
        "temperature": current.get("temperature_2m"),
        "humidity": current.get("relative_humidity_2m"),
        "wind_speed": current.get("wind_speed_10m"),
    }


def get_weather():
    try:
        weather_data = {
            "source": "online",
            "last_sync": now_string(),
            "cities": [fetch_city_weather(city) for city in CITIES],
        }

        save_cache("weather", weather_data)
        return weather_data

    except Exception:
        cached_data = load_cache("weather")

        if cached_data:
            cached_data["source"] = "cache"
            return cached_data

        return {
            "source": "error",
            "last_sync": None,
            "cities": [],
        }
