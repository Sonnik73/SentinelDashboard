import feedparser

from core.cache import load_cache, save_cache
from core.config import get_section, update_section
from core.time import now_string


# Read fresh from config/dashboard.json on every call rather than caching
# at import time, so a feed added/edited/removed through Settings takes
# effect on the next refresh - no server restart needed (same reasoning
# as modules/cameras/service.py's get_hosts()).
def get_feeds():
    return get_section("rss").get("feeds", [])


def _save_feeds(feeds: list):
    # Merge into the existing section rather than replacing it outright,
    # in case "rss" ever grows another key besides "feeds" - a blind
    # overwrite would silently drop it (see modules/weather/service.py's
    # _save_cities(), which actually hit this with a real "provider" key).
    section = get_section("rss")
    section["feeds"] = feeds
    update_section("rss", section)


def validate_feed(name: str, url: str) -> tuple[str, str]:
    name = (name or "").strip()
    url = (url or "").strip()

    if not name:
        raise ValueError("Name is required")

    if not url:
        raise ValueError("URL is required")

    return name, url


def add_feed(name: str, url: str):
    name, url = validate_feed(name, url)
    feeds = get_feeds()

    if any(feed["name"] == name for feed in feeds):
        raise ValueError(f"Feed already exists: {name}")

    feed = {"name": name, "url": url}
    feeds.append(feed)
    _save_feeds(feeds)

    return feed


def update_feed(name: str, new_name: str, new_url: str):
    new_name, new_url = validate_feed(new_name, new_url)
    feeds = get_feeds()

    for feed in feeds:
        if feed["name"] != name:
            continue

        feed["name"] = new_name
        feed["url"] = new_url
        _save_feeds(feeds)
        return feed

    raise ValueError(f"Unknown feed: {name}")


def delete_feed(name: str):
    feeds = get_feeds()
    remaining = [feed for feed in feeds if feed["name"] != name]

    if len(remaining) == len(feeds):
        raise ValueError(f"Unknown feed: {name}")

    _save_feeds(remaining)


def fetch_feed(feed):
    parsed = feedparser.parse(feed["url"])

    if parsed.bozo and not parsed.entries:
        raise RuntimeError(f"Failed to fetch feed {feed['url']}: {parsed.bozo_exception}")

    items = []

    for entry in parsed.entries[:5]:
        items.append(
            {
                "source": feed["name"],
                "title": entry.get("title", "Без заголовка"),
                "link": entry.get("link", ""),
            }
        )

    return items


def get_rss():
    try:
        news = []

        for feed in get_feeds():
            news.extend(fetch_feed(feed))

        data = {
            "source": "online",
            "last_sync": now_string(),
            "items": news[:10],
        }

        save_cache("rss", data)
        return data

    except Exception as error:
        cached_data = load_cache("rss")

        if cached_data:
            cached_data["source"] = "cache"
            cached_data["error"] = str(error)
            return cached_data

        return {
            "source": "error",
            "last_sync": None,
            "items": [],
        }
