from pathlib import Path
import json


CONFIG_FILE = Path("config/dashboard.json")


def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def get_section(section: str):
    config = load_config()
    return config.get(section, {})
