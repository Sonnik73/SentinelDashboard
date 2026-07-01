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
    Shared services
    Configuration
    Cache
    Widgets
    Version
    Time

modules/
    Weather
    RSS
    Network
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

The Layout Engine is the foundation of SentinelDashboard v2.

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
- cameras

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

