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

- Data source: **scraped from rp5.ru** (desktop version, not `m.rp5.ru` — the mobile site loads its data table via JavaScript and doesn't have it in the raw HTML). No API key, no request quota — this is a "screen scrape" of an ordinary web page, not a documented API, which is the tradeoff that was accepted after Open-Meteo became unreachable (v1.3.3) and Yandex Weather API dropped its permanent free tier down to a 14-day trial (v1.6.0 — see below)
- Configured in `config/dashboard.json` under `weather.cities`, each entry needs `name` and the exact `url` of that city's rp5.ru page (e.g. `https://rp5.ru/Погода_в_Ульяновске`) — get it by visiting rp5.ru, searching the city, and copying the address bar. There's no reliable way to derive the URL from a plain city name in code (Russian noun declension isn't a simple string transform), so the URL is stored directly rather than generated
- **Gotcha confirmed on real hardware:** for a city with more than one weather station, `rp5.ru/Погода_в_<Город>` is a region-overview "hub" page (a map with links to each station) that has no forecast table at all — it will fail to parse every time. You need the URL of one *specific station*, e.g. `rp5.ru/Погода_в_Москве_(ВДНХ)` for Moscow, not `rp5.ru/Погода_в_Москве`. Small single-station cities (like Ulyanovsk) happen to work at the short URL, which is easy to mistake for the general pattern. When adding a city, open the page in a browser first and check whether it shows a forecast table directly or a map of sub-stations to pick from
- Endpoint: `GET /api/weather`
- Parsing: `modules/weather/service.py` extracts temperature, humidity, and wind speed from the page's forecast table (`class="t_temperature"`, the "Влажность" row, `class="t_wind_velocity"`), all from that table's first (nearest-time) data column, so the three values are internally consistent with each other. Verified against a real saved rp5.ru page during development, not against every possible city — **this depends on rp5.ru's page structure staying the same, and will need re-verification if the site is redesigned.** On any parsing failure it raises a clear error and falls back to cache exactly like a normal request failure — see Offline Caching below
- Rate limiting: none imposed by rp5.ru, but `modules/weather/service.py` still throttles itself to once per `MIN_REFRESH_SECONDS` (1800s/30min by default) as a courtesy — no reason to hit someone else's web page harder than a real weather API would allow anyway
- Offline behavior: on any failure (network error, or rp5.ru's page layout no longer matching the parser), falls back to the last successful response cached in `data/weather_cache.json`. Responses are tagged `"source": "online"` or `"source": "cache"` so the frontend can indicate staleness

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

### cameras

- Data source: a single still frame grabbed from each camera's RTSP stream via `ffmpeg` (`ffmpeg -rtsp_transport tcp -i <rtsp-url> -frames:v 1 -f image2 -`, output captured from stdout — no temp files, no video decoding beyond the first keyframe). Not a live video stream; the widget polls a fresh snapshot on the manifest's `refresh` interval (10s by default)
- Configured in `config/dashboard.json` under `cameras.hosts`, each entry needs `id` (used in the API URL and cache filename), `name` (display label), `ip`, and optionally `port` (default 554) and `path` (default `/1/1`) — the RTSP path is camera-model-specific; `/1/1` is a common Tiandy convention but **unverified beyond a specific model/firmware**, confirm it works once the camera is on the network and adjust `path` if not
- Credentials are shared across all cameras and read from `CAMERA_USERNAME`/`CAMERA_PASSWORD` environment variables (default username `admin` if unset), not stored in `config/dashboard.json` — same reasoning as `YANDEX_WEATHER_API_KEY` in the weather module: don't commit access credentials to a file that's tracked in git
- Endpoints: `GET /api/cameras` (per-camera status: `source`, `last_sync`, `error`) and `GET /api/cameras/<id>/snapshot` (the actual JPEG, `Content-Type: image/jpeg`). The widget's `<img>` tag points directly at the snapshot endpoint with a cache-busting timestamp query param; a failed load falls back to a `camera-snapshot-error` CSS class via the `onerror` handler
- Offline behavior: on failure (ffmpeg not installed, camera unreachable, wrong RTSP path/credentials, timeout), falls back to the last successful JPEG cached at `data/camera_<id>.jpg`, with status metadata in `data/cameras_cache.json` (same `core/cache.py`-based pattern as weather/rss, just split into a binary file + a small JSON status blob since `core/cache.py` only handles JSON). If no snapshot was ever captured, the endpoint returns 404/502 and the frontend shows "нет сигнала"

---

## View System (`modules/views`)

Unlike the widget modules above, `views` has **no `manifest.json`** and is not discovered by `core/loader.py` — it is imported directly by `routes/api.py`. It manages the JSON view files under `config/views/`.

Provided functions:

- `list_views()` — enumerate available views
- `load_view(name)` — load and normalize a view's layout (auto-upgrades legacy formats, defaults missing widget spans to 12)
- `save_view_layout(name, layout)` — persist an edited layout
- `create_view(name, title)` — scaffold a new view file, exposed via `POST /api/views/create` and the "Новый View" form in the Settings drawer
- `duplicate_view(source_name, new_name, new_title)` — copy an existing view's layout into a new file, exposed via `POST /api/views/duplicate` and the "📋 Дублировать" button
- `rename_view(name, new_title)` — changes only the `title` field, not the file/id, so existing `?view=<id>` links keep working. Exposed via `POST /api/views/rename` and the "✏️ Переименовать" button
- `delete_view(name)` — deletes a view file; refuses to delete the view named `default` (`DEFAULT_VIEW`) since `load_view()` falls back to it when a requested view doesn't exist. Exposed via `POST /api/views/delete` and the "🗑 Удалить" button, which the frontend also disables client-side when the current view is `default` (`is_default` flag from `GET /api/views`)
- `export_view(name)` — returns a view's raw on-disk JSON (`title` + `layout`, no `id`). Exposed via `GET /api/views/export?view=<id>`, which sends it as a downloadable file (`Content-Disposition: attachment`) via the "💾 Экспортировать" button
- `import_view(name, view_data, title)` — validates `view_data` has a `layout` list of rows and writes it as a new view file. Exposed via `POST /api/views/import`. The frontend reads the uploaded `.json` file client-side with the browser's File API and sends the parsed JSON in the request body, rather than a multipart upload — keeps the backend on plain JSON bodies like every other view endpoint and avoids adding `python-multipart` as a new dependency

---

## Offline Caching

`weather`, `rss`, and `cameras` fetch data from outside the process (external websites for the first two, local-network RTSP cameras for the third), and all follow the same pattern through `core/cache.py`: a successful response is saved to `data/<name>_cache.json`, and on failure (no network, timeout, API error) the last cached copy is served instead, marked `"source": "cache"`. `cameras` adapts this for binary data — the JSON cache only holds status metadata, the actual JPEG bytes live in a separate `data/camera_<id>.jpg` file. This is the mechanism behind the project's offline-first behavior for modules that depend on something outside their own process.

---

## Adding a New Module

See `examples/example_widget/` for a minimal template, and the [Module System](ARCHITECTURE.md#module-system) section of ARCHITECTURE.md for the discovery convention (manifest, default template/service/api paths, automatic router loading).
