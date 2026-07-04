from pathlib import Path
import json
import os
import tempfile


CONFIG_FILE = Path("config/dashboard.json")


def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_config(config: dict):
    # Same atomic-write pattern as core/cache.py: a unique temp file per
    # write, swapped in with an atomic rename, so a concurrent load_config()
    # never catches config/dashboard.json mid-write.
    fd, tmp_path = tempfile.mkstemp(
        dir=CONFIG_FILE.parent, prefix=".dashboard_", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            json.dump(config, file, ensure_ascii=False, indent=4)
        Path(tmp_path).replace(CONFIG_FILE)
    except Exception:
        os.unlink(tmp_path)
        raise


def get_section(section: str):
    config = load_config()
    return config.get(section, {})


def update_section(section: str, data: dict):
    config = load_config()
    config[section] = data
    save_config(config)
