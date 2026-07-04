from fastapi import APIRouter, Body, HTTPException

from modules.rss.service import add_feed, delete_feed, get_feeds, get_rss, update_feed


router = APIRouter()


@router.get("/rss")
def api_rss():
    return get_rss()


@router.get("/rss/config")
def api_rss_config():
    return {"feeds": get_feeds()}


@router.post("/rss/config/add")
def api_add_feed(payload: dict = Body(...)):
    try:
        feed = add_feed(payload.get("name", ""), payload.get("url", ""))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return {"status": "ok", "feed": feed}


@router.post("/rss/config/update")
def api_update_feed(payload: dict = Body(...)):
    try:
        feed = update_feed(
            payload.get("name", ""),
            payload.get("new_name", ""),
            payload.get("new_url", ""),
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return {"status": "ok", "feed": feed}


@router.post("/rss/config/delete")
def api_delete_feed(payload: dict = Body(...)):
    try:
        delete_feed(payload.get("name", ""))
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

    return {"status": "ok"}
