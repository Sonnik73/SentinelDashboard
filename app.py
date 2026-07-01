from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routes import api, dashboard


app = FastAPI(title="Sentinel Dashboard")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(dashboard.router)
app.include_router(api.router)
