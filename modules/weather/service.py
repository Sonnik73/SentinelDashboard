from core.config import get_section
from datetime import datetime
from core.cache import load_cache, save_cache
from core.time import now_string
import httpx

WEATHER_CONFIG = get_section("weather")
CITIES = WEATHER_CONFIG["cities"]
TIMEZONE = WEATHER_CONFIG["timezone"]


def fetch_city_weather(city):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": city["latitude"],
        "longitude": city["longitude"],
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
	"timezone": TIMEZONE,
    }

    response = httpx.get(url, params=params, timeout=15)
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

    except Exception as error:
        cached_data = load_cache("weather")

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
