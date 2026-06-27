from pathlib import Path
import json


CACHE_DIR = Path("data")


def get_cache_file(name: str) -> Path:
    return CACHE_DIR / f"{name}_cache.json"


def load_cache(name: str):
    cache_file = get_cache_file(name)

    if not cache_file.exists():
        return None

    with open(cache_file, "r", encoding="utf-8") as file:
        return json.load(file)


def save_cache(name: str, data):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    cache_file = get_cache_file(name)

    with open(cache_file, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
