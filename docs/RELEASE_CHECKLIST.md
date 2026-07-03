# Release Checklist — v2.0

This checklist tracks the public release audit. Update it as each item is completed.

---

## Stage A — Documentation

- [x] README.md
- [x] docs/INSTALL.md
- [x] docs/DEVELOPMENT.md
- [x] docs/ENGINEERING.md
- [x] docs/ARCHITECTURE.md
- [x] docs/MODULES.md
- [x] docs/ROADMAP.md
- [x] docs/RELEASE_CHECKLIST.md (this file)

## Stage B — Repository Cleanup

- [x] Review examples/example_widget/ for accuracy against the current module convention (found and fixed: missing widget template, inaccurate install instructions)
- [x] LICENSE present and correct (MIT)
- [x] CHANGELOG.md kept in sync with VERSION
- [x] VERSION file kept in sync with commits
- [x] .gitignore covers .venv, __pycache__, runtime data cache, local config
- [x] Remove leftover dead config: `dashboard` block (title/refresh) and duplicate `widgets` block in config/dashboard.json were unused — removed. `available_widgets` in /api/views is now sourced dynamically from the module loader instead of static config
- [x] `network.router_ip` and `network.internet_host` in config/dashboard.json were unused (only `network.hosts` is read) — removed

## Stage C — Code Audit

- [x] Python — reviewed core/ and modules/*/service.py for consistency. Found and fixed 4 issues: feedparser silently swallows network failures instead of raising, so modules/rss/service.py's offline-cache fallback never triggered on outages and actively overwrote the last good cache with an empty "online" result — fixed by raising when a feed returns no entries with bozo set; get_rss()'s cache fallback now records `error` like get_weather() already did; removed unused `get_view_widgets()` in modules/views/service.py; fixed stray tab/space indentation mixing in core/system.py and modules/weather/service.py
- [x] JavaScript — reviewed static/js/*.js for consistency. Found and fixed 3 issues: widget updaters in widgets.js didn't guard against missing DOM elements (v1.3.4); dashboard.html footer showed a hardcoded stale version (v1.3.5); Live Preview silently did nothing for widgets outside the current view's server-rendered layout, now fixed with a hidden widget-pool render (v1.3.6)
- [x] `create_view()` in modules/views/service.py is now wired to `POST /api/views/create`, with a "Новый View" form in the Settings drawer (name input + create button). Validation errors (empty/invalid name) return 400, duplicate name returns 409, both shown inline instead of crashing
- [x] Confirmed: the `system` module's special-cased wiring (no service.py/api.py, data via core/system.py + a route hardcoded in routes/api.py) is intentional — decided against refactoring it into the standard convention. Documented in ARCHITECTURE.md, MODULES.md, and CLAUDE.md as the one deliberate exception
- [x] The `refresh` field in every module's manifest.json is now read by the frontend: static/js/widgets.js fetches /api/widgets and schedules each updater with setInterval(updater, widget.refresh * 1000) instead of hardcoding the interval (v1.3.7)
- [x] Fixed: `/api/weather` could hang up to 45s (3 cities × 15s timeout) when the network is unreachable before falling back to cache. Reduced per-city HTTP timeout from 15s to 5s (worst case now ~15s)

## Stage D — UX Audit

- [ ] Fresh install on a clean Raspberry Pi, following INSTALL.md start to finish — not testable from this environment, needs real hardware
- [x] Settings drawer — found and fixed a real bug: `.settings-drawer` had `height: 100vh` with no `overflow-y`, so once the drawer's content exceeded the viewport height (e.g. a standard 1280×720 screen with a few widgets plus the new "Create View" form), the Save/Reset/Share buttons were pushed off-screen with no scrollbar and were completely unreachable. Fixed with `overflow-y: auto`. Verified with a screenshot before and after
- [x] Layout editor — save, span editing, row packing, and Reset all verified working correctly via browser automation (multi-widget span-6 packing produces correct 2-per-row layout; Save persists across reload; Reset correctly discards unsaved changes)
- [x] Offline behavior — verified both weather and rss fall back to cache correctly on a simulated network failure (rss required the v1.4.1 fix earlier in this audit; weather already worked). "Поделиться представлением" (copy link) verified working
- [x] Error handling — verified: missing data/birthdays.json returns `{"source": "local", "items": []}` without crashing; unreachable network hosts return `{"online": false, "ping_ms": null}` without crashing. **Found and documented, not fixed:** an invalid `config/dashboard.json` doesn't crash the server (`core/module_api.py` already isolates per-module import failures with a `[WARN]` log), but produces a confusing partial failure — `/api/weather`, `/api/rss`, `/api/network` return a plain 404 as if the route never existed, while `/api/widgets` still reports those modules as `"enabled": true`, so Settings shows them as normal selectable widgets that silently hang on "Loading..." forever. A real fix needs `core/loader.py`/`core/module_api.py` to track and expose per-module load failures (e.g. an `available` flag on ModuleInfo, surfaced through `/api/widgets` and shown in the frontend) — an architectural change, deferred to a future release, not blocking v2.0
- [ ] **Open item (not a code bug):** as of July 2026, `api.open-meteo.com` has been unreachable from the deployment network for 5+ days (connection times out; DNS resolves fine). Investigation showed several other foreign weather APIs (Met.no, wttr.in, WeatherAPI.com, OpenWeatherMap) are also unreachable from this network, while Russian-hosted sites (RIA, rp5.ru) and major CDNs (Google, Cloudflare) work fine — likely a network/provider-level restriction on certain hosting ranges, not an app bug. Two candidate replacements were evaluated but not yet chosen:
  - **Yandex Weather API** (`api.weather.yandex.ru`) — confirmed reachable, clean JSON, but the permanently-free "on your site" plan caps at 50 requests/day total, which is below the current 3-cities x 10-min-refresh rate and would need throttling logic
  - **rp5.ru** — confirmed reachable, no request-count limit, but no self-serve API: the official XML export requires emailing support@rp5.ru for manual approval (fixed IP required, $1/location/month or free with mandatory backlink); scraping the site is the only self-serve option and would add a fragile HTML-parsing dependency
  - Decision deferred by project owner as of this audit; weather currently keeps working from cache (`data/weather_cache.json`, last successful sync visible in the `last_sync` field) with no risk of the hang bug since the timeout fix in v1.3.2

## Stage E — Release

- [ ] `git status` clean — no untracked files that should be committed or ignored
- [ ] All documentation cross-references verified (no broken links between docs)
- [ ] examples/example_widget/ tested end-to-end as a new-module template
- [ ] Final version bump to `2.0.0`
- [ ] Release tag created and pushed (`git tag v2.0.0 && git push --tags`)

---

Update this file as each box is checked. When every item above is checked, SentinelDashboard v2.0 is ready for public release.
