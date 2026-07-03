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
- [x] **Weather provider decided and implemented (revised twice):** `api.open-meteo.com` was unreachable from the deployment network (v1.3.3). Switched to Yandex Weather API in v1.5.0 — then the project owner discovered Yandex had quietly dropped its permanent free "on your site" tier down to a 14-day trial, invalidating that decision before it ever ran in production. Re-decided in v1.6.0: switched to scraping rp5.ru instead (no quota, no key, no trial expiry — the tradeoff is depending on undocumented page structure instead of a documented API). The owner supplied real saved rp5.ru pages (mobile and desktop) to develop the parser against actual markup instead of guessing — the desktop page's forecast table has temperature/humidity/wind in server-rendered HTML; the mobile page loads that table via JS and doesn't work for scraping. Verified end-to-end against the real captured HTML for Ulyanovsk (extraction, throttle, and cache-fallback-on-parse-failure all confirmed with real data, not just mocks). **Not verified for Moscow or Krasnodar** — their rp5.ru URLs in config/dashboard.json are constructed by standard Russian declension, not confirmed by an actual saved page, and this environment can't reach rp5.ru directly to check. Needs a first real run on the actual deployment to confirm all three cities work

## Stage E — Release

- [x] `git status` clean — verified after every commit this session
- [x] All documentation cross-references verified: all `.md`-to-`.md` links and anchors (`#module-system`, `#requirements`) resolve correctly. Found and fixed: README.md's Documentation list was missing links to MODULES.md and RELEASE_CHECKLIST.md; README.md's "Current Version: v1.2.4" was stale (same class of bug as the v0.8.2 dashboard footer fixed in v1.3.5) — now points to VERSION/CHANGELOG.md instead of a hardcoded number
- [x] examples/example_widget/ tested end-to-end: copied to modules/example/ + templates/widgets/example.html exactly per its own README, auto-discovered with zero code changes (`/api/widgets` and `/api/example` both worked), added to a view, rendered correctly as a "Loading..." placeholder in a browser (matching the documented "frontend wiring is manual" behavior) with no console errors. Cleaned up afterward — example_widget stays a template, not a shipped module
- [ ] Final version bump to `2.0.0`
- [ ] Release tag created and pushed (`git tag v2.0.0 && git push --tags`)

---

Update this file as each box is checked. When every item above is checked, SentinelDashboard v2.0 is ready for public release.
