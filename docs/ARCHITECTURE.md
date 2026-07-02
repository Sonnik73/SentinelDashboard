# SentinelDashboard Architecture

## Philosophy

SentinelDashboard is a modular local dashboard platform.

Core principles:

- Modular architecture
- Offline-first operation
- Simple configuration
- JSON-based layouts
- Live preview editing
- Small safe development iterations

---

# High Level Architecture

Browser
    │
    ▼
FastAPI
    │
    ▼
Routes
    │
    ▼
Modules
    │
    ▼
Core Services

---

# Project Structure

core/
    Module discovery (loader)
    Automatic API loading (module_api)
    Configuration
    Cache
    System metrics
    Widgets
    Version
    Time

modules/
    System
    Weather
    RSS
    Network
    Birthdays
    Views

routes/
    Dashboard
    REST API

templates/
    Dashboard template
    Widget templates

static/
    JavaScript
    CSS

config/
    Dashboard configuration
    View definitions

tools/
    Project validation

docs/
    Documentation

---

# Module System

Modules are discovered automatically — there is no manual registration.

On startup, `core/loader.py` scans:

```
modules/*/manifest.json
```

Each manifest declares an `id`, `title`, `icon`, `type`, and optional `refresh` interval. Everything else follows **convention over configuration**:

| File | Default if not set in manifest |
|---|---|
| Template | `templates/widgets/<id>.html` |
| Service | `service.py`, if present in the module folder |
| API | `api.py`, if present in the module folder |

If a module folder contains an `api.py` exposing a `router = APIRouter()`, `core/module_api.py` imports it automatically and mounts it under `/api`. No manual wiring is required to add a new module — drop a folder with a `manifest.json` into `modules/` and it is picked up on the next restart.

The `system` module is a special case: it is registered for widget display purposes via its manifest, but its data comes from `core/system.py` through a dedicated core route (`/api/system`) rather than a per-module `service.py`/`api.py` pair.

See `examples/example_widget/` for a minimal module template.

---

# View Engine

Each dashboard view is stored as an individual JSON document.

Example:

View
    │
    ├── Layout
    │
    ├── Widgets
    │
    └── Metadata

The View Engine is responsible for:

- loading views
- normalizing layouts
- saving layouts
- exposing views through the REST API

---

# Layout Engine

The Layout Engine is the foundation of the dashboard's view system, delivered as part of the Stable v1 line.

Each layout consists of rows.

Each row contains widgets.

Each widget owns its own width (span).

Example:

Layout

├── Row
│     └── Widget(span=12)

├── Row
│     ├── Widget(span=6)
│     └── Widget(span=6)

└── Row
      ├── Widget(span=4)
      ├── Widget(span=4)
      └── Widget(span=4)

The engine supports:

- live preview
- automatic row packing
- span editing
- JSON serialization

---

# Widget System

Each widget is an independent template.

templates/widgets/

Examples:

- system
- weather
- rss
- network
- birthdays
- cameras *(placeholder — template only, no module/service behind it yet)*

Widgets are reusable and independent.

---

# Live Preview

Layout changes are immediately reflected in the browser without reloading the page.

The editor works entirely with the Layout Model.

---

# Development Workflow

Every sprint follows the same process:

1. One feature
2. Small patches
3. Validation (`python tools/check.py`)
4. Commit
5. Push

This approach minimizes regressions and keeps the project stable.

