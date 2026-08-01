from pathlib import Path
import json
import os
import tempfile


CACHE_DIR = Path("data")


def get_cache_file(name: str) -> Path:
    return CACHE_DIR / f"{name}_cache.json"


def load_cache(name: str):
    cache_file = get_cache_file(name)

    if not cache_file.exists():
        return None

    try:
        with open(cache_file, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, ValueError):
        # A truncated or otherwise unreadable cache file counts as "no
        # cache" rather than taking the endpoint down with a 500. Every
        # caller already treats None as their offline-fallback path, and
        # the next successful save_cache() overwrites the bad file, so this
        # heals itself. Same principle as a broken config/dashboard.json
        # not being allowed to kill the server.
        #
        # json.JSONDecodeError is a ValueError subclass, so catching
        # ValueError covers it - and this is deliberately broad, because a
        # corrupt cache must never be more disruptive than a missing one.
        return None

    # Valid JSON of the wrong shape is just as unusable as a truncated file -
    # every caller indexes the result as a mapping - so it gets the same
    # treatment here instead of an AttributeError surfacing deeper in.
    return data if isinstance(data, dict) else None


def save_cache(name: str, data):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    cache_file = get_cache_file(name)

    # Written to a uniquely-named temp file (mkstemp, not a fixed name)
    # and swapped in with an atomic rename, so concurrent writers never
    # collide on the same temp path and a concurrent load_cache() never
    # catches the file mid-truncate. A fixed temp filename would let two
    # threads' writes interleave into the same inode - json.JSONDecodeError
    # is a ValueError subclass, so callers that treat ValueError as "not
    # found" would misreport that corruption as a missing entry. Cameras
    # made this a frequently-hit race: two camera widgets can both write
    # status around the same moment.
    fd, tmp_path = tempfile.mkstemp(dir=CACHE_DIR, prefix=f".{name}_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        Path(tmp_path).replace(cache_file)
    except Exception:
        os.unlink(tmp_path)
        raise
