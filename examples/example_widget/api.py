from fastapi import APIRouter

from modules.example.service import get_example


router = APIRouter()


@router.get("/example")
def api_example():
    return get_example()
