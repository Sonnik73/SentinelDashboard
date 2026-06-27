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


_WIDGETS = []


def register_widget(widget):
    _WIDGETS.append(widget)


def get_widgets():
    return [widget for widget in _WIDGETS if widget.enabled]


def get_widgets_data():
    return [widget.to_dict() for widget in get_widgets()]
