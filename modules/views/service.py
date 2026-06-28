from pathlib import Path
import json


VIEWS_DIR = Path("config/views")
DEFAULT_VIEW = "default"


def list_views():
    if not VIEWS_DIR.exists():
        return []

    return sorted(
        path.stem
        for path in VIEWS_DIR.glob("*.json")
        if path.is_file()
    )


def load_view(name: str | None = None):
    view_name = name or DEFAULT_VIEW
    view_file = VIEWS_DIR / f"{view_name}.json"

    if not view_file.exists():
        view_name = DEFAULT_VIEW
        view_file = VIEWS_DIR / f"{DEFAULT_VIEW}.json"

    with open(view_file, "r", encoding="utf-8") as file:
        view = json.load(file)

    view["id"] = view_name
    return view


def get_view_widgets(name: str | None = None):
    view = load_view(name)
    return view.get("widgets", [])
