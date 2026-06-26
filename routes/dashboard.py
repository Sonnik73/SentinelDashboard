from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from core.system import get_system_metrics


router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/")
def dashboard(request: Request):
    data = get_system_metrics()
    data["request"] = request

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context=data,
    )
