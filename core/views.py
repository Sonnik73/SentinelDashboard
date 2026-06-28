from pathlib import Path
import json


VIEWS_DIR = Path("config/views")
DEFAULT_VIEW = "default"


def load_view(name: str | None = None):
    view_name = name or DEFAULT_VIEW
    view_file = VIEWS_DIR / f"{view_name}.json"

    if not view_file.exists():
        view_file = VIEWS_DIR / f"{DEFAULT_VIEW}.json"

    with open(view_file, "r", encoding="utf-8") as file:
        return json.load(file)


def get_view_widgets(name: str | None = None):
    view = load_view(name)
    return view.get("widgets", [])
