import re
from datetime import datetime

import httpx

from core.cache import load_cache, save_cache
from core.config import get_section, update_section
from core.time import now, now_string, DEFAULT_TIME_FORMAT

# Read fresh from config/dashboard.json on every call rather than caching
# at import time, so a city added/edited/removed through Settings takes
# effect on the next refresh - no server restart needed (same reasoning
# as modules/cameras/service.py's get_hosts()).
def get_cities():
    return get_section("weather").get("cities", [])


def _save_cities(cities: list):
    # Merge into the existing section rather than replacing it outright -
    # "weather" also carries a "provider" key that a blind overwrite would
    # silently drop (found by diffing config/dashboard.json before/after
    # a save during testing).
    section = get_section("weather")
    section["cities"] = cities
    update_section("weather", section)


def validate_city(name: str, url: str) -> tuple[str, str]:
    name = (name or "").strip()
    url = (url or "").strip()

    if not name:
        raise ValueError("Name is required")

    if not url:
        raise ValueError("URL is required")

    return name, url


def add_city(name: str, url: str):
    name, url = validate_city(name, url)
    cities = get_cities()

    if any(city["name"] == name for city in cities):
        raise ValueError(f"City already exists: {name}")

    city = {"name": name, "url": url}
    cities.append(city)
    _save_cities(cities)

    return city


def update_city(name: str, new_name: str, new_url: str):
    new_name, new_url = validate_city(new_name, new_url)
    cities = get_cities()

    for city in cities:
        if city["name"] != name:
            continue

        city["name"] = new_name
        city["url"] = new_url
        _save_cities(cities)
        return city

    raise ValueError(f"Unknown city: {name}")


def delete_city(name: str):
    cities = get_cities()
    remaining = [city for city in cities if city["name"] != name]

    if len(remaining) == len(cities):
        raise ValueError(f"Unknown city: {name}")

    _save_cities(remaining)

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
            "cities": [fetch_city_weather(city) for city in get_cities()],
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
