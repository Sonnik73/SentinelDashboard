from modules.views.service import (
    list_views,
    load_view,
    save_view_layout,
    create_view,
    duplicate_view,
    rename_view,
    delete_view,
    export_view,
    import_view,
    DEFAULT_VIEW,
)
from core.version import get_version
from core.widgets import get_widgets_data
from fastapi import APIRouter, Request, Body, HTTPException
from fastapi.responses import JSONResponse

from core.system import get_system_metrics


router = APIRouter(prefix="/api")


@router.get("/system")
def api_system():
    return get_system_metrics()



@router.get("/widgets")
def api_widgets():
    return get_widgets_data()




@router.get("/info")
def api_info():
    from core.time import now_string

    return {
        "project": "SentinelDashboard",
        "version": get_version(),
        "build": now_string(),
    }


@router.get("/views")
def api_views(request: Request):
    view_name = request.query_params.get("view")
    current_view = load_view(view_name)

    available_widgets = [
        {
            "id": widget["id"],
            "title": widget["title"],
            "icon": widget["icon"],
        }
        for widget in get_widgets_data()
    ]

    return {
        "current": {
            "id": current_view.get("id"),
            "title": current_view.get("title", current_view.get("id")),
            "is_default": current_view.get("id") == DEFAULT_VIEW,
        },
        "available_views": list_views(),
        "available_widgets": available_widgets,
        "widgets": current_view.get("widgets", []),
        "layout": current_view.get("layout", []),
    }


@router.post("/views/save")
def api_save_view(payload: dict = Body(...)):
    view = save_view_layout(
        payload["view"],
        payload["layout"],
    )

    return {
        "status": "ok",
        "view": view["id"],
        "layout": view["layout"],
    }


@router.post("/views/create")
def api_create_view(payload: dict = Body(...)):
    try:
        view = create_view(
            payload.get("name", ""),
            payload.get("title"),
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except FileExistsError as error:
        raise HTTPException(status_code=409, detail=str(error))

    return {
        "status": "ok",
        "view": view["id"],
        "title": view.get("title"),
    }


@router.post("/views/duplicate")
def api_duplicate_view(payload: dict = Body(...)):
    try:
        view = duplicate_view(
            payload.get("source", ""),
            payload.get("name", ""),
            payload.get("title"),
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except FileExistsError as error:
        raise HTTPException(status_code=409, detail=str(error))

    return {
        "status": "ok",
        "view": view["id"],
        "title": view.get("title"),
    }


@router.post("/views/rename")
def api_rename_view(payload: dict = Body(...)):
    try:
        view = rename_view(
            payload.get("view", ""),
            payload.get("title", ""),
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    return {
        "status": "ok",
        "view": view["id"],
        "title": view.get("title"),
    }


@router.post("/views/delete")
def api_delete_view(payload: dict = Body(...)):
    try:
        delete_view(payload.get("view", ""))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    return {"status": "ok"}


@router.get("/views/export")
def api_export_view(view: str):
    try:
        data = export_view(view)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    return JSONResponse(
        content=data,
        headers={"Content-Disposition": f'attachment; filename="{view}.json"'},
    )


@router.post("/views/import")
def api_import_view(payload: dict = Body(...)):
    try:
        view = import_view(
            payload.get("name", ""),
            payload.get("view", {}),
            payload.get("title"),
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except FileExistsError as error:
        raise HTTPException(status_code=409, detail=str(error))

    return {
        "status": "ok",
        "view": view["id"],
        "title": view.get("title"),
    }


