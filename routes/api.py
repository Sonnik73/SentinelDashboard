from modules.network.service import get_network_status
from modules.rss.service import get_rss
from core.widgets import get_widgets_data
from fastapi import APIRouter

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
