from fastapi import APIRouter, Body, HTTPException, Response

from modules.cameras.service import (
    add_camera,
    delete_camera,
    get_camera_frame,
    get_cameras_status,
    get_hosts,
    update_camera,
)


router = APIRouter()


@router.get("/cameras")
def api_cameras():
    return get_cameras_status()


@router.get("/cameras/config")
def api_cameras_config():
    return {"cameras": get_hosts()}


@router.post("/cameras/config/add")
def api_add_camera(payload: dict = Body(...)):
    try:
        camera = add_camera(
            payload.get("id", ""),
            payload.get("name", ""),
            payload.get("ip", ""),
            payload.get("port", 554),
            payload.get("path", "/1/1"),
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return {"status": "ok", "camera": camera}


@router.post("/cameras/config/update")
def api_update_camera(payload: dict = Body(...)):
    try:
        camera = update_camera(
            payload.get("id", ""),
            name=payload.get("name"),
            ip=payload.get("ip"),
            port=payload.get("port"),
            path=payload.get("path"),
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return {"status": "ok", "camera": camera}


@router.post("/cameras/config/delete")
def api_delete_camera(payload: dict = Body(...)):
    try:
        delete_camera(payload.get("id", ""))
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

    return {"status": "ok"}


@router.get("/cameras/{camera_id}/snapshot")
def api_camera_snapshot(camera_id: str):
    try:
        image_bytes, source = get_camera_frame(camera_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=502, detail=str(error))

    return Response(
        content=image_bytes,
        media_type="image/jpeg",
        headers={"X-Snapshot-Source": source},
    )
