from modules.network.service import get_network_status
from modules.views.service import list_views, load_view
from core.version import get_version
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

    return {
        "current": {
            "id": current_view.get("id"),
            "title": current_view.get("title", current_view.get("id")),
        },
        "available": list_views(),
        "widgets": current_view.get("widgets", []),
    }

    return {
        "current": {
            "id": current_view.get("id"),
            "title": current_view.get("title", current_view.get("id")),
        },
        "available": list_views(),
        "widgets": current_view.get("widgets", []),
    }
