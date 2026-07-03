import re
from datetime import datetime

import httpx

from core.cache import load_cache, save_cache
from core.config import get_section
from core.time import now, now_string, DEFAULT_TIME_FORMAT

WEATHER_CONFIG = get_section("weather")
CITIES = WEATHER_CONFIG["cities"]

# rp5.ru has no documented API and no request quota, but scraping it is a
# fragile dependency on undocumented page structure - keep the request rate
# polite instead of hammering it on every /api/weather call.
MIN_REFRESH_SECONDS = 1800

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Extracted from a real rp5.ru city page (desktop version, not m.rp5.ru -
# the mobile site loads its hourly table via JS and doesn't have these
# values in the raw HTML). Each pattern is anchored on a CSS class or help
# text that looked stable, then matched against the nearest following
# value in the forecast table's first (nearest-time) column.
TEMPERATURE_PATTERN = re.compile(r'class="t_0"[^>]*><b>([+-]?)<span class="otstup"[^>]*></span>(\d+)</b>')
HUMIDITY_PATTERN = re.compile(r'<td class="[^"]*"[^>]*>(\d+)</td>')
WIND_SPEED_PATTERN = re.compile(r'class="wv_0[^"]*"[^>]*>(\d+)</div>')

HUMIDITY_MARKER = 'title="Относительная влажность на высоте 1.5 м (%)">Влажность</a>'


def extract_after(html, marker, pattern, window=3000):
    start = html.find(marker)

    if start == -1:
        raise ValueError(f"rp5.ru page layout changed: marker not found ({marker!r})")

    match = pattern.search(html, start, start + window)

    if not match:
        raise ValueError(f"rp5.ru page layout changed: value not found after marker ({marker!r})")

    return match


def fetch_city_weather(city):
    response = httpx.get(
        city["url"],
        headers={"User-Agent": USER_AGENT},
        timeout=10,
    )
    response.raise_for_status()

    html = response.text

    temp_match = extract_after(html, 'class="t_temperature"', TEMPERATURE_PATTERN)
    temperature = int(temp_match.group(2)) * (-1 if temp_match.group(1) == "-" else 1)

    humidity_match = extract_after(html, HUMIDITY_MARKER, HUMIDITY_PATTERN)
    humidity = int(humidity_match.group(1))

    wind_match = extract_after(html, 'class="t_wind_velocity"', WIND_SPEED_PATTERN)
    wind_speed = int(wind_match.group(1))

    return {
        "name": city["name"],
        "temperature": temperature,
        "humidity": humidity,
        "wind_speed": wind_speed,
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
        weather_data = {
            "source": "online",
            "last_sync": now_string(),
            "cities": [fetch_city_weather(city) for city in CITIES],
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
