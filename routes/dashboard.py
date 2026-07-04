from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

from core.loader import get_enabled_modules
from core.system import get_system_metrics
from core.version import get_version
from modules.views.service import load_view
from core.widgets import get_widgets_data


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
    widgets_data = get_widgets_data()

    data["widget_templates"] = {
        widget["id"]: widget["template"]
        for widget in widgets_data
        if widget["template"]
    }
    data["widget_titles"] = {
        widget["id"]: widget["title"]
        for widget in widgets_data
    }
    # A module ships its own JS (see core/loader.py's optional widget.js
    # convention) instead of every new widget needing static/js/widgets.js
    # edited. Deduplicated by base module id, since an instanced widget
    # (cameras:cam1, cameras:cam2, ...) shares one script for its module.
    data["widget_scripts"] = sorted({
        f"/modules/{widget['id'].split(':')[0]}/widget.js"
        for widget in widgets_data
        if widget["script"]
    })

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context=data,
    )


@router.get("/modules/{module_id}/widget.js")
def module_widget_script(module_id: str):
    module = next((m for m in get_enabled_modules() if m.id == module_id), None)

    if not module or not module.script:
        raise HTTPException(status_code=404, detail=f"No widget.js for module: {module_id}")

    return FileResponse(Path(module.path) / module.script, media_type="application/javascript")
