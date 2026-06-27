from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from core.widgets import Widget, register_widget
from routes import api, dashboard


app = FastAPI(title="Sentinel Dashboard")

app.mount("/static", StaticFiles(directory="static"), name="static")

register_widget(
    Widget(
        widget_id="system",
        title="Raspberry Pi",
        icon="🖥",
        enabled=True,
        refresh=1,
    )
)

register_widget(
    Widget(
        widget_id="weather",
        title="Погода",
        icon="🌤",
        enabled=True,
        refresh=600,
    )
)

app.include_router(dashboard.router)
app.include_router(api.router)
