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
- [ ] `network.router_ip` and `network.internet_host` in config/dashboard.json are also unused (only `network.hosts` is read) — candidate for removal, not yet done

## Stage C — Code Audit

- [ ] Python — review all modules for consistency with ENGINEERING.md principles
- [ ] JavaScript — review static/js/*.js for consistency (vanilla JS only, no leftover dead code)
- [ ] Known candidate: `create_view()` in modules/views/service.py is implemented but not wired to any API endpoint — decide whether to expose it or remove it
- [ ] Confirm the `system` module's special-cased wiring (no service.py/api.py of its own) is intentional and documented, or refactor to match the standard module convention
- [ ] The `refresh` field in every module's manifest.json is not read anywhere in the frontend — refresh intervals are hardcoded per-widget in static/js/widgets.js instead. Decide whether to wire manifest refresh values into the frontend or remove the unused field from manifests
- [x] Fixed: `/api/weather` could hang up to 45s (3 cities × 15s timeout) when the network is unreachable before falling back to cache. Reduced per-city HTTP timeout from 15s to 5s (worst case now ~15s)

## Stage D — UX Audit

- [ ] Fresh install on a clean Raspberry Pi, following INSTALL.md start to finish
- [ ] Settings drawer — all actions work as expected
- [ ] Layout editor — save, span editing, row packing
- [ ] Offline behavior — disconnect network, confirm weather/rss fall back to cache correctly
- [ ] Error handling — invalid config, missing data files, unreachable hosts
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
