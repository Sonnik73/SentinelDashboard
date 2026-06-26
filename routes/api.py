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
