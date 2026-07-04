from importlib import import_module

from core.loader import get_widget_modules


def get_widgets():
    return get_widget_modules()


def get_widget_instances(module):
    """A module normally renders as one widget. It can opt into rendering
    as several independent, separately placeable widgets - one per entry
    it returns here - by defining get_widget_instances() in its service.py
    (see modules/cameras/service.py, used to give each configured camera
    its own widget). Modules that don't define it behave exactly as before."""
    if not module.service:
        return None

    try:
        service = import_module(f"modules.{module.id}.service")
    except Exception:
        return None

    get_instances = getattr(service, "get_widget_instances", None)
    if not callable(get_instances):
        return None

    instances = get_instances()
    return instances or None


def get_widgets_data():
    widgets = []

    for module in get_widgets():
        instances = get_widget_instances(module)

        if not instances:
            widgets.append({
                "id": module.id,
                "title": module.title,
                "icon": module.icon,
                "enabled": module.enabled,
                "refresh": module.refresh,
                "template": module.template,
                "service": module.service,
                "api": module.api,
            })
            continue

        for instance in instances:
            widgets.append({
                "id": f"{module.id}:{instance['id']}",
                "title": instance.get("title", instance["id"]),
                "icon": module.icon,
                "enabled": module.enabled,
                "refresh": module.refresh,
                "template": module.template,
                "service": module.service,
                "api": module.api,
            })

    return widgets
