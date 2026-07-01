from fastapi import APIRouter

from modules.weather.service import get_weather


router = APIRouter()


@router.get("/weather")
def api_weather():
    return get_weather()
