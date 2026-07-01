from pathlib import Path
import json


MODULES_DIR = Path("modules")


class Widget:
    def __init__(self, widget_id, title, icon, enabled=True, refresh=60):
        self.widget_id = widget_id
        self.title = title
        self.icon = icon
        self.enabled = enabled
        self.refresh = refresh

    def to_dict(self):
        return {
            "id": self.widget_id,
            "title": self.title,
            "icon": self.icon,
            "enabled": self.enabled,
            "refresh": self.refresh,
        }


def load_widget_manifests():
    widgets = []

    for manifest_file in sorted(MODULES_DIR.glob("*/manifest.json")):
        try:
            with open(manifest_file, "r", encoding="utf-8") as file:
                manifest = json.load(file)

            if manifest.get("type") != "widget":
                continue

            widget = Widget(
                widget_id=manifest["id"],
                title=manifest.get("title", manifest["id"]),
                icon=manifest.get("icon", ""),
                enabled=manifest.get("enabled", True),
                refresh=manifest.get("refresh", 60),
            )

            widgets.append(widget)

        except Exception as error:
            print(f"[WARN] Failed to load widget manifest {manifest_file}: {error}")

    return widgets


def get_widgets():
    return [
        widget
        for widget in load_widget_manifests()
        if widget.enabled
    ]


def get_widgets_data():
    return [widget.to_dict() for widget in get_widgets()]
