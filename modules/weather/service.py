import os
from datetime import datetime

import httpx

from core.cache import load_cache, save_cache
from core.config import get_section
from core.time import now, now_string, DEFAULT_TIME_FORMAT

WEATHER_CONFIG = get_section("weather")
CITIES = WEATHER_CONFIG["cities"]

YANDEX_API_URL = "https://api.weather.yandex.ru/v2/informers"

# Yandex's free "on your site" plan caps at 50 requests/day total. With 3
# configured cities, refreshing more often than this risks running out of
# quota mid-day, especially with more than one browser/device polling the
# dashboard at once. 3 cities x 12 refreshes/day = 36 requests/day.
MIN_REFRESH_SECONDS = 7200


def fetch_city_weather(city, api_key):
    response = httpx.get(
        YANDEX_API_URL,
        params={
            "lat": city["latitude"],
            "lon": city["longitude"],
            "lang": "ru_RU",
        },
        headers={"X-Yandex-Weather-Key": api_key},
        timeout=5,
    )
    response.raise_for_status()

    fact = response.json()["fact"]

    return {
        "name": city["name"],
        "temperature": fact.get("temp"),
        "humidity": fact.get("humidity"),
        "wind_speed": fact.get("wind_speed"),
    }


def is_cache_fresh(cached_data):
    if not cached_data or cached_data.get("source") != "online" or not cached_data.get("last_sync"):
        return False

    last_sync = datetime.strptime(cached_data["last_sync"], DEFAULT_TIME_FORMAT)
    return (now() - last_sync).total_seconds() < MIN_REFRESH_SECONDS


def get_weather():
    cached_data = load_cache("weather")

    if is_cache_fresh(cached_data):
        return cached_data

    try:
        api_key = os.environ.get("YANDEX_WEATHER_API_KEY")

        if not api_key:
            raise RuntimeError("YANDEX_WEATHER_API_KEY is not set")

        weather_data = {
            "source": "online",
            "last_sync": now_string(),
            "cities": [fetch_city_weather(city, api_key) for city in CITIES],
        }

        save_cache("weather", weather_data)
        return weather_data

    except Exception as error:
        if cached_data:
            cached_data["source"] = "cache"
            cached_data["error"] = str(error)
            return cached_data

        return {
            "source": "error",
            "last_sync": None,
            "error": str(error),
            "cities": [],
        }
