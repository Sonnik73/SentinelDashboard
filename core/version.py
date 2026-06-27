from pathlib import Path

def get_version():
    try:
        return Path("VERSION").read_text(encoding="utf-8").strip()
    except Exception:
        return "development"
