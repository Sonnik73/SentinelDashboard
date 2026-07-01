from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routes import api, dashboard
from core.module_api import load_module_routers


app = FastAPI(title="Sentinel Dashboard")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(dashboard.router)
app.include_router(api.router)

for router in load_module_routers():
    app.include_router(router, prefix="/api")
