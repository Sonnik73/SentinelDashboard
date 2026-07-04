from dataclasses import dataclass
from pathlib import Path
import json


MODULES_DIR = Path("modules")


@dataclass
class ModuleInfo:
    id: str
    title: str
    icon: str = ""
    type: str = "module"
    enabled: bool = True
    refresh: int = 60
    path: str = ""
    template: str | None = None
    service: str | None = None
    api: str | None = None
    script: str | None = None


def load_module_manifest(manifest_file: Path) -> ModuleInfo:
    with open(manifest_file, "r", encoding="utf-8") as file:
        manifest = json.load(file)

    module_id = manifest["id"]

    module_path = manifest_file.parent

    default_template = f"widgets/{module_id}.html"
    default_service = "service.py" if (module_path / "service.py").exists() else None
    default_api = "api.py" if (module_path / "api.py").exists() else None
    default_script = "widget.js" if (module_path / "widget.js").exists() else None

    return ModuleInfo(
        id=module_id,
        title=manifest.get("title", module_id),
        icon=manifest.get("icon", ""),
        type=manifest.get("type", "module"),
        enabled=manifest.get("enabled", True),
        refresh=manifest.get("refresh", 60),
        path=str(module_path),
        template=manifest.get("template", default_template),
        service=manifest.get("service", default_service),
        api=manifest.get("api", default_api),
        script=manifest.get("script", default_script),
    )


def discover_modules():
    modules = []

    for manifest_file in sorted(MODULES_DIR.glob("*/manifest.json")):
        try:
            modules.append(load_module_manifest(manifest_file))
        except Exception as error:
            print(f"[WARN] Failed to load module manifest {manifest_file}: {error}")

    return modules


def get_enabled_modules():
    return [
        module
        for module in discover_modules()
        if module.enabled
    ]


def get_widget_modules():
    return [
        module
        for module in get_enabled_modules()
        if module.type == "widget"
    ]
