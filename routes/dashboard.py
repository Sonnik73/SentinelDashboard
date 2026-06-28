from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from core.system import get_system_metrics
from modules.views.service import load_view


router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/")
def dashboard(request: Request):
    view_name = request.query_params.get("view")
    view = load_view(view_name)
    visible_widgets = view.get("widgets", [])

    data = get_system_metrics()
    data["request"] = request
    data["view"] = view
    data["visible_widgets"] = visible_widgets

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context=data,
    )
