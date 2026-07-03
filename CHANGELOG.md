# SentinelDashboard Changelog

Все значимые изменения проекта фиксируются здесь.

---

## v1.4.1

### Fixed
- modules/rss/service.py: `feedparser.parse()` never raises on network failure (confirmed empirically — a DNS/connection error just yields `bozo=True, entries=[]`), so get_rss()'s try/except never caught real outages. On a network outage this silently returned `{"source": "online", "items": []}` and **overwrote the last good cache with an empty list** — the exact offline-cache bug the project documents itself as protecting against, just via a different mechanism than the weather timeout bug fixed in v1.3.2. fetch_feed() now raises when a feed returns no entries with `bozo` set (verified this doesn't false-positive on feeds that parse with cosmetic XML issues but still have entries)
- get_rss()'s cache fallback now records `cached_data["error"]`, matching get_weather()'s existing behavior for the same documented pattern

### Changed
- core/system.py, modules/weather/service.py: fixed a few lines mixing tabs and spaces for indentation

### Removed
- `get_view_widgets()` in modules/views/service.py — dead code, never called anywhere

---

## v1.4.0

### Added
- `POST /api/views/create` wires up the previously-unused `create_view()` in modules/views/service.py. Validation errors (empty/invalid name) return 400, duplicate view name returns 409
- Settings drawer: a "Новый View" form (name input + create button) lets you create a view from the UI, then switches to it. Moves "Create View" from ROADMAP.md's Version 2.0 wishlist to Completed
- Verified end-to-end in a browser: create succeeds and redirects to the new view, duplicate name shows an inline error, invalid characters and empty name are rejected with 400

---

## v1.3.9

### Confirmed
- The `system` module's special-cased wiring (no service.py/api.py, hardcoded route in routes/api.py) is an intentional, permanent exception to the module convention, not technical debt — closes the last open decision item in Stage C of RELEASE_CHECKLIST.md besides create_view() and the Python review

---

## v1.3.8

### Removed
- `network.router_ip` and `network.internet_host` in config/dashboard.json — dead config, never read by modules/network/service.py (only `network.hosts` is used). Closes the last open item in Stage B of RELEASE_CHECKLIST.md

---

## v1.3.7

### Changed
- static/js/widgets.js: refresh intervals are now read from the `refresh` field in each module's manifest.json (via /api/widgets) instead of being hardcoded in a separate setInterval call per widget. Manifest values already matched the hardcoded ones exactly (system=1s, network=30s, rss=300s, weather=600s, birthdays=3600s), so this is a wiring change with no behavior change. Verified in a browser: system widget's CPU value still refreshes every ~1s

---

## v1.3.6

### Fixed
- Live Preview didn't work for widgets outside the current view's server-rendered layout: checking a widget in Settings that wasn't already part of the view (e.g. "Система" on the "Wall" view, which only has weather+rss) did nothing visually until Save + full page reload, contradicting docs/ARCHITECTURE.md's claim that layout changes are reflected immediately. templates/dashboard.html now server-renders a hidden `#widget-pool` containing every widget module not in the current view's layout, reusing the already-shipped (but previously unused) `.hidden-widget` CSS class; static/js/settings.js's applyView() already knew how to pick up and reposition any `.layout-cell` found anywhere in the document, so no JS changes were needed

### Changed
- docs/RELEASE_CHECKLIST.md: marked the Stage C "JavaScript — review static/js/*.js for consistency" item done — full audit found and fixed 3 issues (missing DOM guards in widget updaters, hardcoded stale version in the footer, incomplete Live Preview for out-of-view widgets)

---

## v1.3.5

### Fixed
- Dashboard footer showed a hardcoded "v0.8.2" that was never updated since it was written, while the real version (already tracked in VERSION and exposed via /api/info) is v1.3.5. routes/dashboard.py now passes core.version.get_version() into the template context and templates/dashboard.html renders it

---

## v1.3.4

### Fixed
- static/js/widgets.js: updateSystemMetrics/updateWeather/updateRSS/updateNetwork now bail out early if their widget isn't in the DOM (matching the guard updateBirthdays already had). Previously any view that didn't include a widget (e.g. config/views/wall.json, which only has weather+rss) caused those updaters to throw on every interval and spam the console indefinitely

---

## v1.3.3

### Investigated
- api.open-meteo.com has been unreachable from the deployment network for 5+ days. Diagnostics showed the issue is specific to certain foreign hosting ranges (Open-Meteo, Met.no, wttr.in, WeatherAPI.com, OpenWeatherMap all unreachable), while Russian-hosted sites and major CDNs work fine. Evaluated Yandex Weather API (reachable, free, but capped at 50 requests/day) and rp5.ru (reachable, no limit, but no self-serve API) as replacements. Decision deferred; documented in RELEASE_CHECKLIST.md for follow-up

---

## v1.3.2

### Changed
- available_widgets in /api/views is now sourced dynamically from core.widgets.get_widgets_data() (automatic module discovery) instead of the static config/dashboard.json widgets block

### Fixed
- /api/weather could hang up to 45 seconds (3 cities x 15s timeout) when the network is unreachable before falling back to cache. Reduced per-city HTTP timeout from 15s to 5s (worst case now ~15s)
- Removed cameras from the selectable widget list in Settings — it had no backing module and silently did nothing when added to a layout

### Removed
- Dead config/dashboard.json blocks: dashboard (title/refresh, never read) and widgets (duplicated manifest.json title/icon data, now fully replaced by dynamic sourcing)

---

## v1.3.1

### Fixed
- examples/example_widget/ was missing its widget template — following the example's own install steps would silently render an empty widget (Jinja2 include ignore missing)
- example_widget README now accurately documents that the frontend requires manual wiring in static/js/widgets.js (not automatic like the backend)

### Added
- Tracked two new findings in RELEASE_CHECKLIST.md for the Code Audit stage: unused create_view() function, and the manifest refresh field not being read anywhere in the frontend

---

## v1.3.0

### Added
- New docs/RELEASE_CHECKLIST.md tracking the 5-stage release audit (Documentation, Repository Cleanup, Code Audit, UX Audit, Release)

### Milestone
- Stage A (Documentation) of the v2.0 Release Candidate Audit is complete: README, INSTALL, DEVELOPMENT, ENGINEERING, ARCHITECTURE, MODULES, ROADMAP, and RELEASE_CHECKLIST have all been rewritten and verified against the actual codebase

---

## v1.2.9

### Fixed
- ROADMAP.md no longer lists already-shipped features (Widget Manifest System, Automatic Module Discovery, Birthdays Widget) under the unreleased Version 2.0 section
- Added missing Modular API Architecture to Completed

---

## v1.2.8

### Added
- New docs/MODULES.md: documents every module (system, weather, rss, network, birthdays), the view system, and the offline caching mechanism
- Flagged create_view() in modules/views/service.py as implemented but unused (candidate for code audit stage)

---

## v1.2.7

### Added
- Documented the Module System in ARCHITECTURE.md (automatic discovery, convention over configuration, API auto-loading)

### Fixed
- core/ and modules/ file lists in ARCHITECTURE.md now match the actual codebase (loader, module_api, system.py, birthdays module, system module)
- Layout Engine description no longer implies it belongs to an unreleased v2
- cameras widget flagged as placeholder (template only, not yet implemented)

---

## v1.2.6

### Added
- ENGINEERING.md principle 11: No Build Systems (fixes reference from DEVELOPMENT.md)

### Fixed
- Unwrapped check.py command now in a proper bash code fence

---

## v1.2.5

### Changed
- Rewrote DEVELOPMENT.md with proper markdown structure
- Documented tools/check.py behavior (Python syntax, JSON config, optional API checks)
- Established versioned commit convention (vX.Y.Z in commit message)

---

## v1.2.4

### Changed
- Split frontend settings logic and app bootstrap into separate modules

---

## v1.2.3

### Changed
- Split frontend widget updaters into a dedicated module

---

## v1.2.2

### Added
- Frontend API helper module (static/js/api.js)

---

## v1.2.1

### Added
- Module SDK example (examples/example_widget)

### Changed
- Cleaned cached bytecode from repository

---

## v1.2.0

### Changed
- Completed modular API architecture (core/module_api.py)

---

## v1.1.3

### Added
- Automatic module API discovery

---

## v1.1.2

### Added
- Manifest driven widget rendering

---

## v1.1.1

### Changed
- Stabilized self-describing module contract

---

## v1.1.0

### Added
- Core module loader (core/loader.py)

---

## v1.0.9

### Changed
- Strengthened module manifest validation

---

## v1.0.8

### Added
- Birthdays widget MVP

---

## v1.0.7

### Added
- Widget manifest foundation

---

## v1.0.6

### Added
- Layout Editor save action
- Live span preview in Settings Drawer
- Automatic row packing for dashboard widgets
- View layout saving through API

### Changed
- View Editor now uses layout as the main state model
- Improved resilience of project checks for external API timeouts

### Fixed
- Restored live data updates after layout editor refactor
- Added weather error reporting when falling back to cache

---

## v1.0.0

### Added
- First stable release
- Modular dashboard architecture
- System, Weather, RSS and Network widgets
- Dashboard Views Engine
- Settings Drawer
- View Editor state model
- Live Preview Engine
- Shareable dashboard views
- Project documentation

### Changed
- Stabilized project structure
- Cleaned unused architecture files
- Added Road to Stability documentation

---
## v0.9.4

### Added
- Settings Drawer action panel
- View Editor state model
- Current view status indicator
- Copy view link button foundation

### Fixed
- Restored dashboard auto update after View Editor changes

---

## v0.8.2 (In Progress)

### Added
- VERSION file
- Project identity

---

## v0.8.1

### Added
- Ping latency
- Raspberry Pi IP
- Automatic interface detection
- Compact Network Widget

---

## v0.8.0

### Added
- Network Widget
- Router monitoring
- Internet monitoring

---

## v0.7.1

### Fixed
- Dashboard auto update

---

## v0.7.0

### Added
- RSS Widget

---

## v0.6.0

### Added
- Configuration system
- Widget Engine

---

## v0.5.1

### Added
- Infrastructure Core

---

## v0.5.0

### Added
- Weather Widget
- Offline cache

---

## v0.4.0

### Added
- Progress bars

---

## v0.3.1

### Changed
- Project architecture refactoring
