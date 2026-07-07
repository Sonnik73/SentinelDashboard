from fastapi import APIRouter, Body, HTTPException

from modules.network.service import add_host, delete_host, get_hosts, get_network_status, update_host


router = APIRouter()


@router.get("/network")
def api_network():
    return get_network_status()


@router.get("/network/config")
def api_network_config():
    return {"hosts": get_hosts()}


@router.post("/network/config/add")
def api_add_host(payload: dict = Body(...)):
    try:
        host = add_host(payload.get("name", ""), payload.get("address", ""))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return {"status": "ok", "host": host}


@router.post("/network/config/update")
def api_update_host(payload: dict = Body(...)):
    try:
        host = update_host(
            payload.get("name", ""),
            payload.get("new_name", ""),
            payload.get("new_address", ""),
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return {"status": "ok", "host": host}


@router.post("/network/config/delete")
def api_delete_host(payload: dict = Body(...)):
    try:
        delete_host(payload.get("name", ""))
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    return {"status": "ok"}
