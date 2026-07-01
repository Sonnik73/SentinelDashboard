from core.loader import get_widget_modules


def get_widgets():
    return get_widget_modules()


def get_widgets_data():
    return [
        {
            "id": widget.id,
            "title": widget.title,
            "icon": widget.icon,
            "enabled": widget.enabled,
            "refresh": widget.refresh,
            "template": widget.template,
            "service": widget.service,
            "api": widget.api,
        }
        for widget in get_widgets()
    ]
