# SentinelDashboard Changelog

Все значимые изменения проекта фиксируются здесь.

---

## v2.8.9

### Added
- Birthday entries can now be added, edited, and removed from the Settings drawer ("Дни рождения" section) instead of hand-editing `data/birthdays.json` — same pattern as cameras, RSS, weather, and network. Backed by new `GET /api/birthdays/config` and `POST /api/birthdays/config/add` / `.../update` / `.../delete` in `modules/birthdays/api.py`
- `modules/birthdays/service.py` gains `save_birthdays()`, which writes straight to `data/birthdays.json` (creating the file and `data/` directory on first save — there was previously no writer at all, only `load_birthdays()`), and `add_birthday()` / `update_birthday()` / `delete_birthday()`, mirroring weather/rss/network's CRUD helpers. `validate_birthday()` rejects a `date` that isn't `MM-DD` with a 400 instead of silently accepting garbage that would later show up as an `error` entry on `/api/birthdays`. An entry has no separate `id` - identified by its (unique) `name`

### Verification
- Full add/rename/delete round trip verified via API (including a rejected malformed date) and through the Settings UI in a browser; confirmed `data/birthdays.json` is created on first add and reflects each change

---

## v2.8.8

### Added
- Network ping hosts can now be added, edited, and removed from the Settings drawer ("Хосты для пинга" section) instead of hand-editing `config/dashboard.json` — same pattern as cameras, RSS, and weather. Backed by new `GET /api/network/config` and `POST /api/network/config/add` / `.../update` / `.../delete` in `modules/network/api.py`
- `modules/network/service.py`'s `get_hosts()` reads `config/dashboard.json` fresh on every call instead of caching it at import time (it previously cached the whole `network` section into a module-level `NETWORK_CONFIG` at import), so a host added through the UI is picked up on the next refresh with no server restart. A host has no separate `id` - identified by its (unique) `name`, same as weather cities/RSS feeds
- `_save_hosts()` merges into the existing `network` section rather than replacing it outright, applying the read-merge-write fix from v2.8.7 from the start rather than retrofitting it later

### Verification
- Full add/rename/delete round trip verified via API and through the Settings UI in a browser; `config/dashboard.json` diffed byte-for-byte against a pre-test backup afterward with no drift

---

## v2.8.7

### Added
- Weather cities can now be added, edited, and removed from the Settings drawer ("Города погоды" section) instead of hand-editing `config/dashboard.json` — same pattern as cameras (v2.7.0) and RSS (v2.7.7). Backed by new `GET /api/weather/config` and `POST /api/weather/config/add` / `.../update` / `.../delete` in `modules/weather/api.py`
- `modules/weather/service.py`'s `get_cities()` reads `config/dashboard.json` fresh on every call instead of caching it at import time, so a city added through the UI is picked up on the next refresh with no server restart. A city has no separate `id` - identified by its (unique) `name`, same as RSS feeds

### Fixed
- Found while testing this: `_save_cities()`/`_save_hosts()`/`_save_feeds()` (weather, cameras, rss) all replaced their entire config section outright (`update_section("weather", {"cities": cities})`) instead of merging into it. Weather's section also carries a `provider` key, which a save from the UI was silently wiping - confirmed by diffing `config/dashboard.json` before/after a save. Cameras and RSS don't currently have any extra keys in their sections, so they weren't hit by this in practice, but were fixed the same way (read the current section, update just the one list key, write the merged result back) since the same bug was clearly waiting to happen there too

### Verification
- Full add/rename/delete round trip verified via API and through the Settings UI in a browser; confirmed `config/dashboard.json`'s `weather.provider` key survives a city add+delete cycle after the fix (it didn't before)

---

## v2.8.6

### Added
- `requirements.txt` — previously missing despite `docs/INSTALL.md` and `README.md` both referencing `pip install -r requirements.txt`. Lists the runtime dependencies actually imported by the code (`fastapi`, `uvicorn`, `jinja2`, `psutil`, `httpx`, `feedparser`), pinned as minimum versions matching what's been tested against this session

### Verification
- Installed into a fresh venv and confirmed `app.py` imports cleanly with nothing else present

---

## v2.8.5

### Added
- Fullscreen Swipe: while a widget is fullscreen, swiping left/right jumps to the next/previous widget in the current view (wraps from last back to first and vice versa). `static/js/ui.js`'s `swipeToWidget()` calls `requestFullscreen()` directly on the target cell rather than exiting first - switching the fullscreen element directly is supported by modern browsers and avoids the "no longer a direct user gesture" pitfall of an async exit-then-request-again sequence
- Guards against a vertical-dominant touch move (e.g. scrolling a widget's own long content, like a news list) being misread as a swipe - only a horizontal move past a 60px threshold that's also larger than the vertical component counts

### Verification
- Verified with synthetic touch events in a `has_touch` Playwright context: a move below the threshold leaves fullscreen unchanged, swipe left/right correctly navigate next/previous, wraps around at both ends, and a vertical-dominant move doesn't trigger navigation

---

## v2.8.4

### Added
- Per-camera frame rate: `fps` is now a plain number input (1-10) per camera in Settings, instead of one global rate for every camera (`DEFAULT_FPS = 2` if a camera doesn't set one, `MIN_FPS`/`MAX_FPS` bound the valid range). `modules/cameras/service.py`'s `_start_stream()` passes each camera's own `fps` to ffmpeg's `-r`. Editing fps on an existing camera restarts its stream immediately, same as quality/resolution
- `modules/cameras/widget.js` rewritten around this: each camera instance gets its own `setInterval` computed from its actual fps (`1000 / fps` ms) instead of one shared interval for every camera, so two cameras can genuinely refresh at different rates on the same page. The loop only restarts when a camera's fps actually changes (tracked per instance), so the routine ~10s status poll doesn't hiccup a camera's frame cadence on every tick
- `/api/cameras` now includes each camera's `fps` so the frontend can read it

### Verification
- Captured the real `subprocess.Popen` args against a synthetic source and confirmed ffmpeg received `-r <configured fps>`. In a real browser with two cameras configured at fps=2 and fps=5, sampled each camera's `<img src>` over a 2s window: ~4 distinct frames for the fps=2 camera, ~11 for the fps=5 one — matching their independently configured rates on the same page

---

## v2.8.3

### Added
- Camera quality controls: each camera now has a `resolution` dropdown (original / 1280x720 / 854x480 / 640x360, passed to ffmpeg's `-vf scale=`) and a `quality` dropdown (high/medium/low/minimum, mapped to ffmpeg's `-q:v`) in the Settings "Камеры" section, both on the add form and on each existing camera's editable row. Backed by new `quality`/`resolution` fields on the camera host in `config/dashboard.json`, validated against a fixed set of choices in `modules/cameras/service.py`
- Changing quality or resolution for an existing camera now restarts its running stream (drops it from the in-memory `_streams` registry so `ensure_stream()` starts a fresh one on the next request) instead of only taking effect after the process happens to restart on its own — same "picked up live, no server restart" pattern as the rest of camera config

### Verification
- Verified the ffmpeg command actually receives `-q:v <quality>` and `-vf scale=<W>:<H>` by capturing the real `subprocess.Popen` args against a synthetic source, and confirmed the produced JPEG is actually the requested resolution (`file` reported the correct WxH). Full add/edit/delete round trip verified via the API and through the Settings UI in a browser

---

## v2.8.2

### Changed
- Camera frame rate lowered from ~3 fps to ~2 fps (`FRAME_RATE` in `modules/cameras/service.py`) — the real Raspberry Pi couldn't sustain 3 fps. `modules/cameras/widget.js`'s `CAMERA_FRAME_INTERVAL_MS` kept in sync (500ms, matching `1000 / FRAME_RATE`) so the frontend doesn't poll faster than frames actually arrive

### Fixed
- Found while testing the frame rate change on a clean checkout: `_read_frames`'s throttled snapshot write (`data/camera_<id>.jpg`) never ensured `data/` existed first, unlike the live tmpfs file. On a fresh clone with no `data/` directory yet (nothing else had triggered `core/cache.py`'s `save_cache()`, which does create it), the first throttled write raised `FileNotFoundError`, silently killing the frame-reading background thread — the live stream would just stop advancing with no obvious error. Fixed by creating `CACHE_DIR` alongside `LIVE_DIR` in `_start_stream()`. Verified end-to-end from a directory with `data/` freshly removed: 60/60 clean frames through the real `ensure_stream()` path, where it previously failed 100% of the time

---

## v2.8.1

### Added
- Themes: dark (the existing look, still the default) and a new light theme, toggled via a 🌙/☀️ button in the topbar. `static/css/style.css`'s colors are now CSS custom properties on `:root`, with a `:root[data-theme="light"]` override block for the alternative — a few intentionally-semantic colors (accent blue, status green, the camera placeholder's black) stay the same in both themes rather than becoming variables
- New `static/js/theme.js` wires up the toggle and persists the choice to `localStorage` (per-browser, not per-view/server-side, since it's a device display preference). `templates/dashboard.html`'s `<head>` applies the saved theme via an inline script before the stylesheet paints, so a saved preference never flashes the wrong theme first on load

### Verification
- Verified with Playwright: toggling changes the computed background color immediately, persists in `localStorage`, and survives a full page reload with no flash; screenshotted both themes to confirm text stays readable in light mode (dark headings on a light card, not just the light theme applied without contrast checking)

---

## v2.8.0

Closes out `docs/ROADMAP.md`'s "Version 2.1" Layout and Platform sections in full (everything except the three planned widgets — Meshtastic, Zabbix, Notifications — which stay open for a future sprint):

- Module Load-Failure Visibility (v2.7.1)
- Widget Height (v2.7.2)
- Widget Lock (v2.7.3)
- Responsive Layout (v2.7.4)
- Tablet Mode / touch drag & drop (v2.7.5)
- Widget Framework / Plugin Architecture (v2.7.6)
- RSS Source Config UI (v2.7.7)
- Widget Fullscreen (v2.7.8, added mid-sprint on request)

Wall Mode and Widget Resize turned out to already be satisfied by existing features (an ordinary view, the span dropdown) and needed no new code. See each patch version above for the full detail on its change.

---

## v2.7.8

### Added
- Widget Fullscreen: every widget card now has a ⛶ toggle in its top-right corner (a camera feed, the news list, system metrics - any widget) that expands it to fill the screen using the browser's native Fullscreen API. The button is injected once by `templates/dashboard.html`'s grid/pool loops rather than by each widget's own template, and `static/js/ui.js`'s `initFullscreenToggles()` wires it generically - no per-widget JS needed, and it works on a widget's own `widget.js`-driven card exactly the same as a built-in one
- Camera snapshots drop their compact-card `aspect-ratio: 4/3` while fullscreen (`object-fit: contain` instead) so a feed fills more of the screen for a closer look, rather than staying letterboxed to the grid card's proportions

### Verification
- Verified with Playwright: clicking the toggle enters fullscreen on the correct widget's cell (`document.fullscreenElement` matches), the icon flips to the exit glyph, and a second click exits cleanly

---

## v2.7.7

### Added
- RSS feeds can now be added, edited, and removed from the Settings drawer instead of hand-editing `config/dashboard.json` — a new "Источники новостей" section lists configured feeds with inline-editable name/URL plus a form to add a new one. Backed by `GET /api/rss/config` and `POST /api/rss/config/add` / `.../update` / `.../delete` in `modules/rss/api.py`
- `modules/rss/service.py`'s `get_feeds()` now reads fresh from `config/dashboard.json` on every call instead of caching it at import time (same reasoning as `modules/cameras/service.py`'s `get_hosts()` in v2.7.0), so a feed added through the UI is picked up on the next refresh with no server restart
- A feed has no separate `id` field (unlike cameras) - it's identified by its `name`, which must be unique among configured feeds

### Verification
- Full add → rename → delete round trip verified both via direct API calls and through the actual Settings UI in a browser; `config/dashboard.json` came back byte-identical afterward

---

## v2.7.6

### Added
- Plugin Architecture / Widget Framework: a module can now ship its own `widget.js` in its folder (same convention as `service.py`/`api.py` — `core/loader.py` detects it, `routes/dashboard.py` serves it at `/modules/<id>/widget.js`, `templates/dashboard.html` includes it automatically) instead of needing `static/js/widgets.js` edited for every new widget
- New `static/js/registry.js` holds the shared `WIDGET_UPDATERS` map and a `registerWidget(id, updater)` function, loaded first so both `widgets.js`'s built-in updaters and any module's own `widget.js` can call it regardless of load order between them
- `modules/cameras/widget.js` is the real, working example: `updateCamera()` and the independent ~333ms fast image-refresh loop moved out of `static/js/widgets.js` entirely, changing nothing about camera behavior (re-verified: status text and live image refresh both still work)
- `examples/example_widget/` gained a `widget.js` demonstrating the new convention; the README now documents both options (a module's own `widget.js`, or the older direct edit of `static/js/widgets.js` for something considered a core built-in widget)

### Verification
- Temporarily installed `examples/example_widget/` as a real module (`modules/example/`) and confirmed it rendered live data end-to-end with zero central-file edits, then removed it again

---

## v2.7.5

### Added
- Tablet Mode: touch drag & drop for the layout editor. HTML5 native drag & drop (`dragstart`/`dragover`/`drop`) never fires on touch devices at all - `static/js/settings.js`'s `initDragAndDrop()` gained a parallel `touchstart`/`touchmove`/`touchend` implementation reaching the same `reorderWidget()` outcome. Touch events keep firing on the element where the touch started (unlike mouse `dragover`, which fires on whatever's under the pointer), so `document.elementFromPoint()` is used to find the actual cell under the finger as it moves. A locked widget (see Widget Lock, v2.7.3) resists touch-drag exactly like mouse-drag
- New `.drag-over` outline style highlights the cell currently under a touch-drag

### Verification
- Simulated a real touch drag with synthetic `TouchEvent`s in a `has_touch` Playwright context: dragging one widget onto another reordered them exactly like the mouse path, and a locked widget stayed in place under the same gesture

---

## v2.7.4

### Added
- Responsive Layout: below a 640px viewport, every widget now stacks full-width regardless of its chosen span - the 12-col grid otherwise left `span-3`/`span-4` widgets too narrow to read on a phone (text wrapping constantly, camera snapshots shrinking to postage-stamp size). Topbar wraps, footer stacks vertically, and the Settings drawer goes full-width instead of a fixed 320px (which could exceed the viewport on a small phone)
- Verified with Playwright at a 375px mobile viewport (`?view=server`, which mixes span-6/span-12 widgets): cells that render ~613px wide at 1280px desktop width render full ~355px wide (viewport minus padding) at 375px, while the desktop layout is unchanged

---

## v2.7.3

### Added
- Widget Lock: an optional `locked` flag on a layout item, toggled via a 🔓/🔒 button next to each widget in Settings. A locked widget can't be picked up by drag & drop (native `draggable` cleared) and its span/height dropdowns are disabled, so a position/size you've settled on can't be nudged by accident. Unlocking restores both immediately, no drawer reopen needed

### Changed
- Refactored the Settings widget checklist rendering into its own `renderWidgetsChecklist()`, driven by a cached `viewEditor.availableWidgets` instead of a fresh network fetch. The lock toggle (and the Reset button) need to re-render the checklist to reflect the new disabled/enabled state of the span and height dropdowns, and re-fetching from `/api/views` for that would have silently discarded any other unsaved edit in progress - found this while testing the lock toggle, before it ever shipped

---

## v2.7.2

### Added
- Widget Height: an optional per-widget `height` (px) in the layout, editable via a new dropdown next to the span selector in Settings ("Авто" / "Компактно" 220px / "Средне" 360px / "Высоко" 600px). Absent/0 keeps the pre-existing "grow to fit content" behavior, so every existing view renders unchanged until a height is explicitly picked. Applied on `.layout-cell` (both the server-rendered template and the client-side `applyView()` re-render), with the widget card stretching to fill and scrolling internally (`overflow-y: auto`) if its content is taller than the fixed height
- No backend change needed — `modules/views/service.py`'s `normalize_view()` already passes unknown layout-item keys through untouched, so `height` just rides along the same path as `span`

---

## v2.7.1

### Added
- Module load-failure visibility: `core/module_api.py` now tracks whether each module's `api.py` import succeeded (`MODULE_STATUS`), exposed via a new `get_module_status()`. `core/widgets.py` surfaces this as `available`/`error` on every widget from `/api/widgets` and `/api/views`. Previously, a module whose `api.py`/`service.py` failed to import (e.g. `config/dashboard.json` missing a section a module expects) still listed as a completely normal, addable widget in Settings — now it shows struck through with a ⚠️ tooltip carrying the actual error, instead of silently hanging on "Loading..." forever. Verified by temporarily breaking the weather module's config section: server stayed up, `available: false` with the real `KeyError` message appeared in `/api/widgets`, Settings rendered it struck through

### Roadmap
- Marked Wall Mode and Widget Resize as already satisfied (an ordinary view already covers "wall mode", the span dropdown already covers "resize") — no code needed for either, just closing them out in `docs/ROADMAP.md`

---

## v2.7.0

### Added
- Cameras can now be added, edited, and removed from the Settings drawer instead of hand-editing `config/dashboard.json` — a new "Камеры" section lists configured cameras with inline-editable name/IP/port/path plus a form to add a new one. Backed by `GET /api/cameras/config` and `POST /api/cameras/config/add` / `.../update` / `.../delete` in `modules/cameras/api.py`
- `modules/cameras/service.py` now reads `cameras.hosts` fresh on every call instead of caching it at import time, so a camera added through the UI shows up immediately in the widget list and Settings checklist — no server restart needed, unlike every other module (and unlike a manual edit of the same JSON file)
- `core/config.py` gets `save_config()`/`update_section()` for writing `config/dashboard.json` back out, using the same atomic-write pattern (unique temp file + rename) already used for `core/cache.py` and camera frames

### Changed
- Camera `id` is validated (letters, numbers, hyphens, underscores only) since it's used directly in the snapshot URL and cache filenames; deleting a camera also stops its running ffmpeg stream if one was active, rather than leaving it orphaned until the next restart

---

## v2.6.0

### Added
- Widget instances: a module can now render as several independent, separately placeable widgets instead of exactly one, by defining `get_widget_instances()` in its `service.py`. `core/widgets.py` expands each instance into a composite id (`<module_id>:<instance_id>`) that the rest of the system — Settings drawer checklist, drag & drop, per-widget span, layout JSON — treats as an ordinary opaque widget id, so nothing downstream needed to change. Modules that don't opt in behave exactly as before
- `cameras` uses this: each entry in `config/dashboard.json`'s `cameras.hosts` is now its own widget (`cameras:cam1`, `cameras:cam2`, ...) instead of one shared card listing every camera — with two physical cameras arriving, they can sit side by side as independently sized/positioned cards. `templates/widgets/cameras.html` and `static/js/widgets.js`'s camera updater were rewritten around a single camera per widget instance rather than a list

### Fixed
- `core/cache.py`'s `save_cache()` wrote its atomic-replace temp file under a **fixed** name, so concurrent writers collided on the same path — normally rare, but two independent camera widgets writing status on their own request cycles hit it constantly under load (verified with 240 concurrent snapshot requests: reproduced 404s every run before the fix, 0 after). A reader could catch the shared temp file mid-write, and since `json.JSONDecodeError` is a `ValueError` subclass, that corruption was silently misreported as "unknown camera" (404) instead of the real transient failure. Fixed by giving every write its own unique temp file (`tempfile.mkstemp()`) before the atomic rename — this also benefits `weather`/`rss`, which share the same cache module

---

## v2.5.0

### Changed
- Cameras widget rearchitected from a one-shot ffmpeg snapshot per HTTP request to a genuine ~3 frames/second live feed. An RTSP handshake alone can take 1-2s, so spawning ffmpeg per request couldn't keep up with 3 fps — `modules/cameras/service.py` now keeps one persistent `ffmpeg` process per camera running continuously (`-r 3 -f mjpeg -`, streamed to stdout), with a background thread splitting the stream into individual JPEG frames
- Frames are written atomically (temp file + `Path.rename()`, which is atomic on POSIX) to avoid a torn/partial JPEG being served mid-write — confirmed with a 200-iteration concurrent-read stress test: the previous naive in-place overwrite approach corrupted 3/200 reads, the temp+rename approach had 0/200
- The live frame lives on `/dev/shm` (tmpfs, RAM-backed) rather than the SD-card-backed `data/` directory, since it's rewritten several times a second — writing that continuously to the SD card would cause meaningful wear over time on a Raspberry Pi. The SD-card-backed fallback snapshot (`data/camera_<id>.jpg`) and status metadata (`data/cameras_cache.json`) are still updated, just throttled to once every 2 seconds
- `get_camera_snapshot()` renamed to `get_camera_frame()`: once a camera's stream is running, it just reads the live tmpfs file — no ffmpeg spawned per call. `ensure_stream()` lazily starts a camera's stream on first request and restarts it if the process has died or gone stale (no new frame for 5s)
- `app.py` gets a shutdown hook (`stop_all_streams()`) so the persistent ffmpeg processes are terminated cleanly when the server stops, rather than left as orphans
- `static/js/widgets.js`'s `updateCameras()` now only creates each camera's DOM node once and afterwards updates its status text in place; the `<img>` itself refreshes on its own independent ~333ms interval (`refreshCameraFrames()`) so the manifest's 10s status-poll interval no longer governs image freshness. Rebuilding the whole `<img>` node on every poll would have caused visible flicker at 3 fps

### Known limitation
- Still unverified against real camera hardware — validated end-to-end with a synthetic `ffmpeg` test source (frame integrity, restart-on-death) and against unreachable/fake IPs (clean 502/404 degradation, no orphaned processes), but the actual Tiandy TC-C320N RTSP path/credentials remain to be confirmed once the cameras are on the network

---

## v2.4.0

### Added
- Cameras widget — the `cameras.html` template placeholder now has a real module behind it (`modules/cameras/`), auto-discovered with zero changes elsewhere thanks to the module convention
- `modules/cameras/service.py` grabs a single still frame from each camera's RTSP stream via `ffmpeg` (`-frames:v 1 -f image2 -`, captured from stdout, no temp files, no video decoding). This is a snapshot refreshed on an interval (10s by default), not a live video stream — browsers can't play RTSP directly, and this avoids needing a transcoding pipeline (HLS/WebRTC) on Raspberry Pi hardware
- `GET /api/cameras` (per-camera status) and `GET /api/cameras/<id>/snapshot` (the JPEG itself), following the same offline-cache pattern as weather/rss: on failure, serves the last successful snapshot from `data/camera_<id>.jpg` instead of breaking, with status metadata in `data/cameras_cache.json`
- `config/dashboard.json` gets a new `cameras.hosts` section (`id`, `name`, `ip`, `port`, `path`); credentials are shared across cameras and read from `CAMERA_USERNAME`/`CAMERA_PASSWORD` environment variables rather than committed, same reasoning as the weather module's API key handling
- INSTALL.md documents the new `ffmpeg` system dependency and the camera environment variables, including the systemd unit example

### Known limitation
- The RTSP path (`path` in config, defaults to `/1/1`) is a common Tiandy convention but **not yet verified against real hardware** — the cameras this was built for hadn't arrived yet. Verified end-to-end with a real `ffmpeg` binary against unreachable/fake IPs: connection failures, timeouts, and unknown-camera-id all degrade cleanly (502/404 with a clear message, falling back to cache, no crash) — only the actual RTSP path/credentials against a live Tiandy TC-C320N remain to be confirmed

---

## v2.3.1

### Fixed
- `templates/dashboard.html` never bumped the `?v=` cache-busting query param on `widgets.js`, `settings.js`, or `app.js` despite both files being edited repeatedly across this whole session (v1.3.4 through v2.3.0) — only CSS got this treatment consistently. Browsers that had cached an old copy of these files (e.g. from before v1.4.0) could keep running stale JS indefinitely after a `git pull`, missing every view-management/import-export/drag-and-drop feature added since. Bumped `widgets.js` and `settings.js` to `?v=2`, `app.js` to `?v=28`

### Note
- If a browser is still showing old behavior after this, a hard refresh (Ctrl+Shift+R / Cmd+Shift+R) forces it to ignore any remaining cached copy regardless of the `?v=` value already in its cache

---

## v2.3.0

### Added
- Drag & Drop Layout Editor — closes out ROADMAP.md's Workspace section entirely. Native HTML5 Drag and Drop API, no new library, matching the vanilla-JS constraint
- `viewEditor.widgetOrder` in static/js/settings.js is now the source of truth for widget order (previously implicit in checkbox DOM order); `buildLayoutFromSettings()` packs that order into rows by span exactly as before. Checking/unchecking a widget appends/removes it from `widgetOrder` without disturbing the order of widgets that stay checked
- Widget cards become draggable while the Settings drawer is open; dropping one onto another reorders `widgetOrder` and re-renders immediately via the existing `applyView()`/row-packing logic

### Fixed
- Found while building drag & drop: `.settings-overlay` covered the entire viewport (including the grid) to support "click anywhere outside the drawer closes it" — which made the grid completely unclickable, and therefore undraggable, whenever the drawer was open. Changed the overlay to `pointer-events: none` (visual dimming only) and removed the click-to-close handler; closing the drawer is now via the × button only

### Known limitation
- Drag & drop is mouse-only — native HTML5 DnD doesn't fire on touch devices. Touch/tablet support is a separate, already-tracked ROADMAP.md item (Tablet Mode)

### Verified
- End-to-end in a browser: dragging a card reorders the grid and marks the view as having unsaved changes; Save persists the new order across reload; closing via the × button and disabling drag on close both still work; a newly-checked widget (previously in the hidden pool) can immediately be dragged like any other

---

## v2.2.0

### Added
- Import / Export Views — the last item of ROADMAP.md's Workspace section besides Drag & Drop
- `GET /api/views/export?view=<id>` downloads a view's raw JSON (`export_view()` in modules/views/service.py), served with `Content-Disposition: attachment` via a new "💾 Экспортировать текущий view" button
- `POST /api/views/import` creates a new view from uploaded JSON (`import_view()`), validating that `layout` is a list of rows before writing anything to disk. The frontend reads the uploaded `.json` file with the browser's File API and sends the parsed JSON in a normal request body — same pattern as every other view endpoint, and avoids adding `python-multipart` as a new dependency just for file uploads
- Settings drawer: new "Импорт View" section (file picker + button) and an "Экспортировать текущий view" button next to Duplicate/Rename/Delete
- Verified end-to-end in a browser: real file download via Export, real file upload via Import (including a full export→import round-trip reproducing the exact layout), and the invalid-JSON-file error path caught client-side before ever reaching the server

---

## v2.1.0

### Added
- Duplicate/Rename/Delete View — the first three items of ROADMAP.md's Workspace section, extending the Create View pattern from v1.4.0
- `POST /api/views/duplicate` copies an existing view's layout into a new file (`duplicate_view()` in modules/views/service.py)
- `POST /api/views/rename` changes only a view's `title`, not its file/id — existing `?view=<id>` links keep working (`rename_view()`)
- `POST /api/views/delete` deletes a view file, refusing to delete `default` since `load_view()` falls back to it when a requested view doesn't exist (`delete_view()`)
- Settings drawer: "📋 Дублировать" / "✏️ Переименовать" / "🗑 Удалить" buttons under Current View, using native `prompt()`/`confirm()` dialogs to keep the UI simple. The delete button is disabled (both client-side via a new `is_default` flag on `GET /api/views`, and server-side) when viewing the default view
- Verified end-to-end in a browser: duplicate → redirect to the copy, rename → title updates, delete → redirects to `/`; delete correctly blocked (disabled button + 400 if forced) on the default view; duplicate/rename/delete against nonexistent views correctly return 404, duplicate onto an existing name returns 409

---

## v2.0.1

### Changed
- docs/ROADMAP.md's "Version 2.0" section renamed to "Version 2.1" now that v2.0 has actually shipped

---

## v2.0.0

Public v2.0 release. All five stages of the RELEASE_CHECKLIST.md audit are complete — see it for the full breakdown of what was found and fixed at each stage (documentation, repository cleanup, code audit, UX audit, release). Highlights since v1.2.4 (the last version README used to reference):

- Full documentation pass across README/INSTALL/DEVELOPMENT/ENGINEERING/ARCHITECTURE/MODULES/ROADMAP
- Removed dead config (`config/dashboard.json`'s unused `dashboard`/`widgets` blocks, `network.router_ip`/`internet_host`); `/api/widgets` now sources from the module loader dynamically instead of static config
- JS code audit: fixed widget updaters crashing on views that don't include them, a stale hardcoded version in the dashboard footer, and Live Preview not working for widgets outside the current view's layout
- Python code audit: fixed a real offline-cache bug in the RSS module (feedparser silently swallowing network failures instead of raising, so outages overwrote the last good cache with nothing)
- `create_view()` wired up to `POST /api/views/create` with a Settings drawer UI — views can now be created without editing JSON by hand
- The `refresh` field in widget manifests is now actually read by the frontend instead of being a hardcoded duplicate in `widgets.js`
- Fixed a real UX bug found on real hardware: the Settings drawer's Save/Reset/Share buttons were unreachable off-screen on standard viewport heights
- Weather provider rewritten twice this cycle: Open-Meteo (unreachable from the deployment network) → Yandex Weather API (dropped its free tier before the integration shipped) → scraping rp5.ru directly. The final version was developed against real saved pages and debugged through two rounds of real-hardware testing, confirmed working end-to-end for all three configured cities

---

## v1.6.3

### Confirmed
- Weather (rp5.ru scraping) confirmed fully working on the real Raspberry Pi: `curl /api/weather` returns `"source": "online"` with real numbers for all three configured cities (Москва 26°C/44%, Краснодар 29°C/57%, Ульяновск 30°C/35%). Closes out the weather item in Stage D of RELEASE_CHECKLIST.md — the only real-hardware-only item left is a full fresh-install walkthrough of INSTALL.md

---

## v1.6.2

### Fixed
- `HUMIDITY_PATTERN` in modules/weather/service.py was too strict: it required `<td class="...">` to be immediately followed by the value, but real rp5.ru pages sometimes render that cell with extra `onmouseover`/`onmouseout` tooltip attributes in between (`<td class="d underlineRow " onmouseover="tooltip(...)" onmouseout="...">44</td>`), which made the regex fail to match even though the marker itself was found. `WIND_SPEED_PATTERN` already tolerated this (`[^>]*`) but `HUMIDITY_PATTERN` and `TEMPERATURE_PATTERN` didn't — both now do, for consistency. Found via a real second round of hardware testing; verified against both the original clean saved page and the real page with tooltip attributes
- Krasnodar's rp5.ru URL was hitting the same multi-station "hub" page problem as Moscow did in v1.6.1 — confirmed the correct station URL directly from a real page: `https://rp5.ru/Погода_в_Краснодаре,_Краснодарский_край`
- `extract_after()`'s search window raised from 2000 to 3000 chars for extra margin against real pages being more verbose than the reference sample used during development

---

## v1.6.1

### Fixed
- First real-hardware test of v1.6.0 (on the actual Pi, with real internet access) found that `https://rp5.ru/Погода_в_Москве` isn't a weather page at all — for cities with more than one weather station, that URL is a region-overview "hub" page with a map and links to individual stations, not a forecast table. Only single-station cities like Ulyanovsk happen to work at that short URL by coincidence. Confirmed the correct URL for Moscow directly from a real page: `https://rp5.ru/Погода_в_Москве_(ВДНХ)` (the "Москва (ВДНХ)" station link visible in the hub page's own navigation). `config/dashboard.json` updated; Krasnodar's URL still needs the same real-page verification

---

## v1.6.0

### Changed
- Weather provider switched again, this time from Yandex Weather API to scraping rp5.ru. Yandex quietly ended its permanent free "on your site" tier (now just a 14-day trial) before the v1.5.0 integration ever ran in production, which invalidated that decision. rp5.ru has no API, no key, and no quota, at the cost of depending on undocumented page structure instead of a documented contract
- `modules/weather/service.py` rewritten to scrape rp5.ru's desktop city pages (`https://rp5.ru/Погода_в_<Город>`) instead of calling an API. The **mobile** site (`m.rp5.ru`) was tried first and ruled out — it loads its weather table via JavaScript and doesn't expose humidity in the raw HTML at all, only the desktop version renders temperature/humidity/wind server-side. Extraction is regex-based (`class="t_temperature"`, the "Влажность" table row, `class="t_wind_velocity"`), reading all three values from the same forecast-table column so they're internally consistent
- Developed and verified against **real saved rp5.ru pages** (both mobile and desktop, supplied by the project owner) rather than guessed selectors — confirmed working end-to-end for Ulyanovsk, including the throttle and the fallback-to-cache path when parsing fails (simulated a site redesign, confirmed a clean error instead of a crash)
- `config/dashboard.json`'s `weather.cities` entries now hold a `url` (the exact rp5.ru page) instead of `latitude`/`longitude`, since there's no reliable way to generate a Russian-declined URL from a plain city name in code. Moscow and Krasnodar's URLs are constructed by standard declension but **not verified against a real page** — only Ulyanovsk was confirmed
- Throttle (`MIN_REFRESH_SECONDS`) relaxed from Yandex's quota-driven 2h down to 1800s (30min) — rp5.ru has no hard request cap, this is just politeness toward a plain web page instead of a rate-limited API. `modules/weather/manifest.json`'s `refresh` matches
- Removed everything Yandex-specific: `YANDEX_WEATHER_API_KEY` env var and its INSTALL.md/systemd documentation are gone, since scraping needs no credentials

### Known limitations
- Confirmed working against real captured HTML for **Ulyanovsk only**; Moscow and Krasnodar need a real run to confirm their URLs and page structure match
- Scraping is inherently fragile: if rp5.ru redesigns its page, the parser will start raising and the widget will fall back to cache indefinitely until someone updates the selectors in `modules/weather/service.py`

---

## v1.5.0

### Changed
- Weather provider switched from Open-Meteo (unreachable from the deployment network since June 2026, see v1.3.3) to the Yandex Weather API. Project owner's decision, choosing it over rp5.ru because rp5 would've meant either a fragile HTML scrape with no way to verify it in this development environment, or manual approval for its paid XML export
- `modules/weather/service.py` rewritten against Yandex's `v2/informers` endpoint (`fact.temp`, `fact.humidity`, `fact.wind_speed`), reading the API key from a new `YANDEX_WEATHER_API_KEY` environment variable (documented in INSTALL.md, including the systemd unit example)
- Added a server-side throttle (`MIN_REFRESH_SECONDS`, 2h): `get_weather()` now serves the existing cache instead of making a live request if it was refreshed recently, regardless of how many clients call `/api/weather` or how often — protects the free tier's 50 requests/day cap (3 cities x 12 refreshes/day = 36/day) in a way that a frontend-only polling interval couldn't, since the dashboard can be viewed from multiple devices at once
- `modules/weather/manifest.json`'s `refresh` raised from 600s to 7200s to match; `config/dashboard.json`'s now-unused `weather.timezone` removed and `weather.provider` updated to `"yandex"`

### Known limitation
- **Not verified against the live Yandex endpoint.** This development environment's own network policy blocks `api.weather.yandex.ru`, the same way it blocked `api.open-meteo.com` — verification was limited to a mocked HTTP client (confirms the header, request shape, response parsing, throttle, and error-fallback logic all work), plus `tools/check.py`. Needs a real first run with `YANDEX_WEATHER_API_KEY` set on the actual deployment to confirm the endpoint/header/response shape are still correct

---

## v1.4.3

### Fixed
- README.md's Documentation list was missing links to docs/MODULES.md and docs/RELEASE_CHECKLIST.md, even though both exist and are actively referenced elsewhere
- README.md showed a stale "Current Version: v1.2.4" (same class of doc-drift bug as the hardcoded v0.8.2 dashboard footer fixed in v1.3.5) — now points to VERSION/CHANGELOG.md instead of a hardcoded number that will go stale again

### Verified (Stage E, no code change needed)
- examples/example_widget/ tested end-to-end exactly per its own README: copied to modules/example/ + templates/widgets/example.html, auto-discovered with zero code changes, rendered correctly in a browser matching documented behavior. Cleaned up afterward
- All documentation cross-references and anchors verified resolving correctly
- `git status` clean

---

## v1.4.2

### Fixed
- static/css/style.css: `.settings-drawer` had `height: 100vh` with no `overflow-y`, so once its content exceeded the viewport height (a normal 1280×720 screen with the widget list plus the new "Create View" form was already enough), the Save/Reset/Share buttons were pushed off-screen with no way to scroll to them — completely unreachable. Added `overflow-y: auto`. Verified with before/after screenshots

### Verified (Stage D UX audit, no code change needed)
- Layout editor: span-based row packing, Save (persists across reload), Reset (discards unsaved changes), and the copy-view-link button all work correctly
- Offline behavior: weather and rss both correctly fall back to cache on a simulated network failure
- Error handling: missing data/birthdays.json and unreachable network hosts both degrade gracefully without crashing

### Documented, not fixed (deferred — architectural change)
- An invalid config/dashboard.json doesn't crash the server, but produces a confusing partial failure: /api/weather, /api/rss, /api/network return a plain 404, while /api/widgets still reports those modules as enabled, so Settings offers them as normal widgets that silently never load. Tracked in ROADMAP.md under Platform

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
