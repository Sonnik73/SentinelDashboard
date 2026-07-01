from importlib import import_module

from fastapi import APIRouter

from core.loader import get_enabled_modules


def load_module_routers():
    routers = []

    for module in get_enabled_modules():
        if not module.api:
            continue

        module_path = f"modules.{module.id}.api"

        try:
            api_module = import_module(module_path)
            router = getattr(api_module, "router", None)

            if isinstance(router, APIRouter):
                routers.append(router)
            else:
                print(f"[WARN] Module {module.id} api.py has no APIRouter named router")

        except Exception as error:
            print(f"[WARN] Failed to load API for module {module.id}: {error}")

    return routers
