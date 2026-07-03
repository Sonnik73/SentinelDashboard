from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from core.system import get_system_metrics
from core.version import get_version
from modules.views.service import load_view
from core.loader import get_widget_modules


router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/")
def dashboard(request: Request):
    view_name = request.query_params.get("view")
    view = load_view(view_name)
    visible_widgets = view.get("widgets", [])
    layout = view.get("layout", [])

    data = get_system_metrics()
    data["request"] = request
    data["version"] = get_version()
    data["view"] = view
    data["visible_widgets"] = visible_widgets
    data["layout"] = layout
    data["widget_templates"] = {
        module.id: module.template
        for module in get_widget_modules()
        if module.template
    }

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context=data,
    )
