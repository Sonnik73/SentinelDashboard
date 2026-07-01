from fastapi import APIRouter

from modules.network.service import get_network_status


router = APIRouter()


@router.get("/network")
def api_network():
    return get_network_status()
