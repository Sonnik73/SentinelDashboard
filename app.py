from datetime import datetime
import platform

import psutil
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


app = FastAPI(title="Sentinel Dashboard")

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def dashboard(request: Request):
    data = {
        "time": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
        "hostname": platform.node(),
        "cpu_percent": psutil.cpu_percent(interval=0.5),
        "memory_percent": psutil.virtual_memory().percent,
    }

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context=data,
    )


@app.get("/api/system")
def api_system():
    return {
        "time": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
        "hostname": platform.node(),
        "cpu_percent": psutil.cpu_percent(interval=0.5),
        "memory_percent": psutil.virtual_memory().percent,
    }
