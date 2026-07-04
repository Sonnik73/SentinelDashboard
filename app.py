from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routes import api, dashboard
from core.module_api import load_module_routers
from modules.cameras.service import stop_all_streams


app = FastAPI(title="Sentinel Dashboard")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(dashboard.router)
app.include_router(api.router)

for router in load_module_routers():
    app.include_router(router, prefix="/api")


@app.on_event("shutdown")
def _stop_camera_streams():
    stop_all_streams()
