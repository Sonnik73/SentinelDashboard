from datetime import datetime
from pathlib import Path
import json

import httpx


CACHE_FILE = Path("data/weather_cache.json")


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


def load_cache():
    if not CACHE_FILE.exists():
        return None

    with open(CACHE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_cache(data):
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(CACHE_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


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
            "last_sync": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            "cities": [fetch_city_weather(city) for city in CITIES],
        }

        save_cache(weather_data)
        return weather_data

    except Exception:
        cached_data = load_cache()

        if cached_data:
            cached_data["source"] = "cache"
            return cached_data

        return {
            "source": "error",
            "last_sync": None,
            "cities": [],
        }
