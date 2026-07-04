from fastapi import APIRouter, HTTPException, Response

from modules.cameras.service import get_camera_snapshot, get_cameras_status


router = APIRouter()


@router.get("/cameras")
def api_cameras():
    return get_cameras_status()


@router.get("/cameras/{camera_id}/snapshot")
def api_camera_snapshot(camera_id: str):
    try:
        image_bytes, source = get_camera_snapshot(camera_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=502, detail=str(error))

    return Response(
        content=image_bytes,
        media_type="image/jpeg",
        headers={"X-Snapshot-Source": source},
    )
