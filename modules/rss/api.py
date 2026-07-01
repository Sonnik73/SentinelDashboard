from fastapi import APIRouter

from modules.rss.service import get_rss


router = APIRouter()


@router.get("/rss")
def api_rss():
    return get_rss()
