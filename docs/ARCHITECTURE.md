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

The editor works entirely with the Layout Model. This includes widgets that weren't part of the current view when the page was loaded: `templates/dashboard.html` server-renders every registered widget module, not just the ones in the current view's layout — widgets outside the layout are rendered into a hidden `#widget-pool` (`display: none` via the `.hidden-widget` CSS class). `static/js/settings.js`'s `applyView()` looks up `.layout-cell` elements anywhere in the document, so toggling a widget in Settings can move its card from the pool into the visible grid (or back) without a page reload.

## Drag & Drop Reordering

While the Settings drawer is open, widget cards in the grid are draggable (native HTML5 Drag and Drop API, no library). `viewEditor.widgetOrder` in `settings.js` is the source of truth for widget order — dragging a card reorders it directly, and `buildLayoutFromSettings()` re-packs that order into rows using each widget's span, same as it already did for the checkbox-driven layout. Checking/unchecking a widget appends/removes it from `widgetOrder` without disturbing the order of widgets that stay checked.

This required removing `.settings-overlay`'s click-to-close behavior: the overlay used to cover the entire viewport (including the grid) to let a click anywhere outside the drawer close it, which made the grid completely unclickable — and therefore undraggable — while the drawer was open. The overlay is now `pointer-events: none` (a purely visual dimming layer); closing the drawer is done via the × button only.

Mouse-only for now — native HTML5 drag-and-drop doesn't fire on touch devices. Touch/tablet support is tracked separately under Tablet Mode in `docs/ROADMAP.md`.

---

# Development Workflow

Every sprint follows the same process:

1. One feature
2. Small patches
3. Validation (`python tools/check.py`)
4. Commit
5. Push

This approach minimizes regressions and keeps the project stable.

