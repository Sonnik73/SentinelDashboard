from modules.network.service import get_network_status
from modules.views.service import list_views, load_view
from core.version import get_version
from core.config import get_section
from modules.rss.service import get_rss
from core.widgets import get_widgets_data
from fastapi import APIRouter, Request

from core.system import get_system_metrics
from modules.weather.service import get_weather


router = APIRouter(prefix="/api")


@router.get("/system")
def api_system():
    return get_system_metrics()


@router.get("/weather")
def api_weather():
    return get_weather()

@router.get("/widgets")
def api_widgets():
    return get_widgets_data()

@router.get("/rss")
def api_rss():
    return get_rss()

@router.get("/network")
def api_network():
    return get_network_status()


@router.get("/info")
def api_info():
    from core.time import now_string

    return {
        "project": "SentinelDashboard",
        "version": get_version(),
        "build": now_string(),
    }


@router.get("/views")
def api_views(request: Request):
    view_name = request.query_params.get("view")
    current_view = load_view(view_name)

    widget_config = get_section("widgets")
    available_widgets = [
        {
            "id": widget_id,
            "title": meta.get("title", widget_id),
            "icon": meta.get("icon", ""),
        }
        for widget_id, meta in widget_config.items()
    ]

    return {
        "current": {
            "id": current_view.get("id"),
            "title": current_view.get("title", current_view.get("id")),
        },
        "available_views": list_views(),
        "available_widgets": available_widgets,
        "widgets": current_view.get("widgets", []),
        "layout": current_view.get("layout", []),
    }
