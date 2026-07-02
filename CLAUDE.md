# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

SentinelDashboard is a modular, offline-first information dashboard for Raspberry Pi / Linux servers. It runs as a single `uvicorn` process — a FastAPI backend serving Jinja2 templates and vanilla JavaScript, with no Node.js, no build step, and no frontend framework. JSON files (`config/dashboard.json`, `config/views/*.json`, module `manifest.json`) are the source of truth for configuration, views, and layouts.

## Commands

Run the dev server:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

Validate before every commit (Python syntax, config JSON, and — if the server is already running on `127.0.0.1:8000` — live API endpoints):

```bash
python tools/check.py
```

If the server isn't running, the API portion of the check is skipped with a `[WARN]`, not a failure. There is no automated test suite (no pytest/unittest) — `tools/check.py` is the only validation gate.

**Note:** README/INSTALL reference `pip install -r requirements.txt`, but no `requirements.txt` currently exists in the repo. Runtime dependencies inferred from imports: `fastapi`, `uvicorn`, `jinja2`, `psutil`, `httpx`, `feedparser`.

## Architecture

```
Browser → FastAPI (app.py) → Routes (routes/) → Modules (modules/) → Core (core/)
```

### Module system — automatic discovery, no manual registration

On startup, `core/loader.py` scans `modules/*/manifest.json`. Each manifest declares `id`, `title`, `icon`, `type`, and optional `refresh`; everything else follows convention over configuration:

| Piece | Default location if not overridden in manifest |
|---|---|
| Template | `templates/widgets/<id>.html` |
| Service | `modules/<id>/service.py`, if present |
| API | `modules/<id>/api.py`, if present |

If a module folder has an `api.py` exposing `router = APIRouter()`, `core/module_api.py` imports it automatically and `app.py` mounts it under `/api`. **To add a new widget module: drop a folder with `manifest.json` (+ optional `service.py`/`api.py`/template) into `modules/` — no code changes elsewhere are needed.** See `examples/example_widget/` for the minimal template and `docs/MODULES.md` for the full convention.

Two exceptions to the standard convention:
- **`system`** module: manifest-registered for widget display, but its data comes from `core/system.py` via a route wired directly in `routes/api.py` (`/api/system`), not a per-module `service.py`/`api.py`.
- **`views`** module (`modules/views/`): has no `manifest.json` and is not discovered by the loader at all — it's imported directly by `routes/api.py` and `routes/dashboard.py` to manage `config/views/*.json`.

### View / Layout model

Each dashboard view is one JSON file in `config/views/`. A view has a `layout`: a list of rows, each row a list of `{"widget": id, "span": 1-12}` items. `modules/views/service.py` loads, normalizes (auto-upgrades legacy formats, defaults missing `span` to 12), and saves views. The frontend Layout Editor (`static/js/settings.js`) edits this model directly with live preview — no separate "widgets" list is authoritative once a layout exists.

### Offline caching pattern

Any module that fetches external data (currently `weather`, `rss`) follows the same pattern via `core/cache.py`: on success, write `data/<name>_cache.json`; on failure, serve the last cached copy tagged `"source": "cache"` (vs `"source": "online"`) so the frontend can indicate staleness. `data/` is gitignored — cache files are runtime state, not committed.

### Frontend wiring is NOT automatic

Unlike the backend, adding a widget's live data to the UI requires manually wiring `static/js/widgets.js` (fetch `/api/<id>`, write into `#<id>-content`, register with `setInterval`). The `refresh` value in a module's `manifest.json` is currently unused by the frontend — refresh intervals are hardcoded per-widget in `widgets.js` (tracked in `docs/RELEASE_CHECKLIST.md`). JS files under `static/js/` are grouped by responsibility (`api.js` fetch helpers, `app.js` bootstrap, `ui.js`, `widgets.js` per-widget updaters, `settings.js` layout editor/settings drawer) — keep new code in the file matching its responsibility rather than adding new global scripts.

## Conventions

- **Versioning**: every commit bumps `VERSION` and the commit message is `vX.Y.Z Short description` (patch = small fix/step, minor = completed feature/milestone, major = breaking change or release stage). Workflow: update `VERSION` → `python tools/check.py` → `git commit -m "vX.Y.Z ..."` → `git push`.
- **Python**: simple, explicit, minimal dependencies, small focused modules — matches the existing style in `core/` and `modules/*/service.py`.
- **JavaScript**: vanilla JS only, no frameworks, no build step, no bundler. Do not introduce Node.js/npm/Webpack/Vite/React/Vue — this is an explicit engineering principle (`docs/ENGINEERING.md` #11), not an oversight.
- **Small, working commits**: one completed unit of work per commit; large refactors are avoided in favor of small reviewable patches; every commit should leave the tree in a working state.
- **Docs evolve with code**: `docs/ARCHITECTURE.md`, `docs/MODULES.md`, `docs/ROADMAP.md`, and `CHANGELOG.md` are expected to be updated alongside behavioral changes, not left to drift.

## Known in-progress gaps (see `docs/RELEASE_CHECKLIST.md`)

- `create_view()` in `modules/views/service.py` is implemented but not wired to any API endpoint.
- `network.router_ip` / `network.internet_host` in `config/dashboard.json` are unused (only `network.hosts` is read).
- `cameras` widget is a template placeholder only — no `service.py`/`api.py` behind it.
- Weather: `api.open-meteo.com` has been unreachable from the deployment network; decision on a replacement provider (Yandex Weather API vs. rp5.ru) is deferred — don't "fix" this by swapping providers without checking current project owner direction.

## Key docs

- `docs/ARCHITECTURE.md` — module system, view/layout engine details
- `docs/MODULES.md` — per-module reference (system, weather, rss, network, birthdays, views)
- `docs/DEVELOPMENT.md` / `docs/ENGINEERING.md` — workflow and engineering principles
- `docs/ROADMAP.md` — planned v2.0 work (drag & drop, plugin architecture, etc.)
