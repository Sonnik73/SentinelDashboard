from importlib import import_module

from fastapi import APIRouter

from core.loader import get_enabled_modules


# Populated once by load_module_routers() at startup, read by
# core/widgets.py to flag a module as unavailable if its api.py failed to
# import (e.g. modules/<id>/service.py errors out reading a malformed
# config/dashboard.json). Without this, a module whose backend crashed on
# import still looked like a perfectly normal, addable widget in Settings.
MODULE_STATUS = {}


def load_module_routers():
    routers = []
    MODULE_STATUS.clear()

    for module in get_enabled_modules():
        if not module.api:
            MODULE_STATUS[module.id] = {"available": True, "error": None}
            continue

        module_path = f"modules.{module.id}.api"

        try:
            api_module = import_module(module_path)
            router = getattr(api_module, "router", None)

            if isinstance(router, APIRouter):
                routers.append(router)
                MODULE_STATUS[module.id] = {"available": True, "error": None}
            else:
                error = f"{module.id} api.py has no APIRouter named router"
                print(f"[WARN] Module {error}")
                MODULE_STATUS[module.id] = {"available": False, "error": error}

        except Exception as error:
            print(f"[WARN] Failed to load API for module {module.id}: {error}")
            MODULE_STATUS[module.id] = {"available": False, "error": str(error)}

    return routers


def get_module_status(module_id: str):
    return MODULE_STATUS.get(module_id, {"available": True, "error": None})
