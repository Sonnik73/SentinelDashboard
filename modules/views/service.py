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


def normalize_view(view: dict) -> dict:
    widgets = view.get("widgets", [])

    if "layout" not in view:
        view["layout"] = [
            [
                {
                    "widget": widget,
                    "span": 12,
                }
            ]
            for widget in widgets
        ]

    normalized = []

    for row in view["layout"]:
        new_row = []

        for item in row:
            if isinstance(item, str):
                item = {
                    "widget": item,
                    "span": 12,
                }

            if isinstance(item, dict) and "span" not in item:
                item["span"] = 12

            new_row.append(item)

        normalized.append(new_row)

    view["layout"] = normalized

    view["widgets"] = [
        item.get("widget")
        for row in view.get("layout", [])
        for item in row
        if isinstance(item, dict) and item.get("widget")
    ]

    return view


def load_view(name: str | None = None):
    view_name = name or DEFAULT_VIEW
    view_file = VIEWS_DIR / f"{view_name}.json"

    if not view_file.exists():
        view_name = DEFAULT_VIEW
        view_file = VIEWS_DIR / f"{DEFAULT_VIEW}.json"

    with open(view_file, "r", encoding="utf-8") as file:
        view = json.load(file)

    view["id"] = view_name
    return normalize_view(view)


def save_view_layout(name: str, layout: list):
    view_name = name or DEFAULT_VIEW
    view_file = VIEWS_DIR / f"{view_name}.json"

    if not view_file.exists():
        raise FileNotFoundError(f"View not found: {view_name}")

    with open(view_file, "r", encoding="utf-8") as file:
        view = json.load(file)

    view["layout"] = layout
    view.pop("widgets", None)

    view = normalize_view(view)

    view_to_save = dict(view)
    view_to_save.pop("id", None)

    with open(view_file, "w", encoding="utf-8") as file:
        json.dump(view_to_save, file, ensure_ascii=False, indent=4)

    view["id"] = view_name
    return view

def normalize_view_name(name: str) -> str:
    return (
        name.strip()
        .lower()
        .replace(" ", "-")
        .replace("_", "-")
    )


def validate_view_name(name: str) -> str:
    view_name = normalize_view_name(name)

    if not view_name:
        raise ValueError("View name is required")

    if not view_name.replace("-", "").isalnum():
        raise ValueError("View name may contain only letters, numbers and hyphens")

    return view_name


def create_view(name: str, title: str | None = None):
    view_name = validate_view_name(name)
    view_file = VIEWS_DIR / f"{view_name}.json"

    if view_file.exists():
        raise FileExistsError(f"View already exists: {view_name}")

    view = {
        "title": title or view_name.title(),
        "layout": [
            [
                {
                    "widget": "system",
                    "span": 12,
                }
            ]
        ],
    }

    VIEWS_DIR.mkdir(parents=True, exist_ok=True)

    with open(view_file, "w", encoding="utf-8") as file:
        json.dump(view, file, ensure_ascii=False, indent=4)

    view["id"] = view_name
    return normalize_view(view)


def duplicate_view(source_name: str, new_name: str, new_title: str | None = None):
    source_file = VIEWS_DIR / f"{source_name}.json"

    if not source_file.exists():
        raise FileNotFoundError(f"View not found: {source_name}")

    view_name = validate_view_name(new_name)
    view_file = VIEWS_DIR / f"{view_name}.json"

    if view_file.exists():
        raise FileExistsError(f"View already exists: {view_name}")

    with open(source_file, "r", encoding="utf-8") as file:
        source_view = json.load(file)

    view = {
        "title": new_title or f"{source_view.get('title', source_name)} (copy)",
        "layout": source_view.get("layout", []),
    }

    with open(view_file, "w", encoding="utf-8") as file:
        json.dump(view, file, ensure_ascii=False, indent=4)

    view["id"] = view_name
    return normalize_view(view)


def rename_view(name: str, new_title: str):
    view_file = VIEWS_DIR / f"{name}.json"

    if not view_file.exists():
        raise FileNotFoundError(f"View not found: {name}")

    new_title = new_title.strip()

    if not new_title:
        raise ValueError("Title is required")

    with open(view_file, "r", encoding="utf-8") as file:
        view = json.load(file)

    view["title"] = new_title

    with open(view_file, "w", encoding="utf-8") as file:
        json.dump(view, file, ensure_ascii=False, indent=4)

    view["id"] = name
    return normalize_view(view)


def delete_view(name: str):
    if name == DEFAULT_VIEW:
        raise ValueError("The default view cannot be deleted")

    view_file = VIEWS_DIR / f"{name}.json"

    if not view_file.exists():
        raise FileNotFoundError(f"View not found: {name}")

    view_file.unlink()

