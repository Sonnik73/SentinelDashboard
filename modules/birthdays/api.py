from fastapi import APIRouter, Body, HTTPException

from modules.birthdays.service import add_birthday, delete_birthday, get_birthdays, load_birthdays, update_birthday


router = APIRouter()


@router.get("/birthdays")
def api_birthdays():
    return get_birthdays()


@router.get("/birthdays/config")
def api_birthdays_config():
    return {"items": load_birthdays()}


@router.post("/birthdays/config/add")
def api_add_birthday(payload: dict = Body(...)):
    try:
        item = add_birthday(payload.get("name", ""), payload.get("date", ""), payload.get("note", ""))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return {"status": "ok", "item": item}


@router.post("/birthdays/config/update")
def api_update_birthday(payload: dict = Body(...)):
    try:
        item = update_birthday(
            payload.get("name", ""),
            payload.get("new_name", ""),
            payload.get("new_date", ""),
            payload.get("new_note", ""),
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return {"status": "ok", "item": item}


@router.post("/birthdays/config/delete")
def api_delete_birthday(payload: dict = Body(...)):
    try:
        delete_birthday(payload.get("name", ""))
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    return {"status": "ok"}
