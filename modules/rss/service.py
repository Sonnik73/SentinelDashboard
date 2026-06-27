import feedparser

from core.cache import load_cache, save_cache
from core.config import get_section
from core.time import now_string


RSS_CONFIG = get_section("rss")


def fetch_feed(feed):
    parsed = feedparser.parse(feed["url"])

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

        for feed in RSS_CONFIG.get("feeds", []):
            news.extend(fetch_feed(feed))

        data = {
            "source": "online",
            "last_sync": now_string(),
            "items": news[:10],
        }

        save_cache("rss", data)
        return data

    except Exception:
        cached_data = load_cache("rss")

        if cached_data:
            cached_data["source"] = "cache"
            return cached_data

        return {
            "source": "error",
            "last_sync": None,
            "items": [],
        }
