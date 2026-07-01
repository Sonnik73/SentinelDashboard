from fastapi import APIRouter

from modules.birthdays.service import get_birthdays


router = APIRouter()


@router.get("/birthdays")
def api_birthdays():
    return get_birthdays()
