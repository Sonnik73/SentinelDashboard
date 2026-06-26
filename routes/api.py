from fastapi import APIRouter

from core.system import get_system_metrics


router = APIRouter(prefix="/api")


@router.get("/system")
def api_system():
    return get_system_metrics()
