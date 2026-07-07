from fastapi import APIRouter, Body, HTTPException

from modules.weather.service import add_city, delete_city, get_cities, get_weather, update_city


router = APIRouter()


@router.get("/weather")
def api_weather():
    return get_weather()


@router.get("/weather/config")
def api_weather_config():
    return {"cities": get_cities()}


@router.post("/weather/config/add")
def api_add_city(payload: dict = Body(...)):
    try:
        city = add_city(payload.get("name", ""), payload.get("url", ""))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return {"status": "ok", "city": city}


@router.post("/weather/config/update")
def api_update_city(payload: dict = Body(...)):
    try:
        city = update_city(
            payload.get("name", ""),
            payload.get("new_name", ""),
            payload.get("new_url", ""),
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return {"status": "ok", "city": city}


@router.post("/weather/config/delete")
def api_delete_city(payload: dict = Body(...)):
    try:
        delete_city(payload.get("name", ""))
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

    return {"status": "ok"}
