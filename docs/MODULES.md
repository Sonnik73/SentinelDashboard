# Modules

This document describes each module shipped with SentinelDashboard. See [ARCHITECTURE.md](ARCHITECTURE.md#module-system) for how automatic module discovery works.

---

## Widget Modules

Modules registered with `"type": "widget"` in their manifest and rendered on the dashboard.

### system

- Manifest registers the widget entry only (title, icon, refresh) — there is no `service.py` or `api.py` in this module folder
- Data comes from `core/system.py`: CPU, memory, disk, temperature, uptime, hostname
- Endpoint: `GET /api/system`, wired directly in `routes/api.py` rather than through a per-module `api.py`
- `get_temperature()` calls `vcgencmd measure_temp`, which only works on real Raspberry Pi hardware. On other Linux systems it fails silently and reports `"N/A"`

### weather

- Data source: the [Yandex Weather API](https://yandex.ru/dev/weather/) `v2/informers` endpoint (switched from Open-Meteo in v1.5.0 — see below). Requires an API key in the `YANDEX_WEATHER_API_KEY` environment variable; see [INSTALL.md](INSTALL.md) for how to set it
- Configured in `config/dashboard.json` under `weather` (`cities`)
- Endpoint: `GET /api/weather`
- Rate limiting: Yandex's free "on your site" plan caps at 50 requests/day total. With 3 configured cities, `modules/weather/service.py` throttles itself server-side — it won't make a live request more often than once per `MIN_REFRESH_SECONDS` (7200s/2h by default), regardless of how often `/api/weather` is called or from how many devices, and serves the existing cache in between. The `refresh` field in `manifest.json` (also 7200) controls how often the frontend polls, but the server-side throttle is what actually protects the quota
- Offline behavior: on request failure (including a missing/invalid API key), falls back to the last successful response cached in `data/weather_cache.json`. Responses are tagged `"source": "online"` or `"source": "cache"` so the frontend can indicate staleness
- Switched from Open-Meteo (unreachable from the deployment network — see CHANGELOG v1.3.3 for the investigation) to Yandex Weather API in v1.5.0. **Not verified against the live Yandex endpoint** — implemented against Yandex's documented `v2/informers` response shape (`fact.temp`, `fact.humidity`, `fact.wind_speed`) and tested with a mocked HTTP client, but the development environment's own network policy blocks `api.weather.yandex.ru` too, so this needs a real first run (with `YANDEX_WEATHER_API_KEY` set) on the actual deployment to confirm the header name (`X-Yandex-Weather-Key`) and response shape are still correct

### rss

- Data source: RSS/Atom feeds, parsed with `feedparser`
- Configured in `config/dashboard.json` under `rss` (`feeds`, each with `name` and `url`)
- Endpoint: `GET /api/rss`
- Limits: up to 5 items per feed, 10 items total
- Offline behavior: same cache-fallback pattern as weather, cached in `data/rss_cache.json`

### network

- Pings each host listed in `config/dashboard.json` under `network.hosts`, and detects the active interface (Wi-Fi / Ethernet) and local IP
- Endpoint: `GET /api/network`
- Shells out to `ping` and `ip route` — both must be available in `PATH`

### birthdays

- Data source: the local file `data/birthdays.json` — nothing is fetched externally
- Endpoint: `GET /api/birthdays`
- Computes days remaining until each birthday and sorts by proximity
- Entries with an unparseable `date` field are still returned, flagged with an `error` field instead of being dropped

---

## View System (`modules/views`)

Unlike the widget modules above, `views` has **no `manifest.json`** and is not discovered by `core/loader.py` — it is imported directly by `routes/api.py`. It manages the JSON view files under `config/views/`.

Provided functions:

- `list_views()` — enumerate available views
- `load_view(name)` — load and normalize a view's layout (auto-upgrades legacy formats, defaults missing widget spans to 12)
- `save_view_layout(name, layout)` — persist an edited layout
- `create_view(name, title)` — scaffold a new view file, exposed via `POST /api/views/create` and the "Новый View" form in the Settings drawer

---

## Offline Caching

`weather` and `rss` are the only modules that fetch external data, and both follow the same pattern through `core/cache.py`: a successful response is saved to `data/<name>_cache.json`, and on failure (no network, timeout, API error) the last cached copy is served instead, marked `"source": "cache"`. This is the mechanism behind the project's offline-first behavior for online-dependent widgets.

---

## Adding a New Module

See `examples/example_widget/` for a minimal template, and the [Module System](ARCHITECTURE.md#module-system) section of ARCHITECTURE.md for the discovery convention (manifest, default template/service/api paths, automatic router loading).
