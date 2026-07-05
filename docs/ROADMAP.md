# SentinelDashboard Roadmap

---

# Completed

## Core Platform

- Version System
- Modular Architecture
- Widget Engine
- View Engine
- Layout Engine
- Live Preview
- Settings Drawer
- Shareable Views
- Dashboard Grid
- Widget Templates
- Automatic Row Packing
- Layout Editor
- Widget Manifest System
- Automatic Module Discovery
- Modular API Architecture
- Birthdays Widget
- Project Documentation
- Create View
- Duplicate View
- Rename View (title only — the underlying view id/URL stays stable)
- Delete View
- Import / Export Views
- Drag & Drop Layout Editor (mouse only — see Roadmap's Layout section for touch/tablet support)
- Cameras Widget (~3 fps live feed from RTSP via a persistent `ffmpeg` process, see `docs/MODULES.md`; RTSP path convention not yet verified against real hardware)
- Camera Config UI (add/edit/delete cameras from Settings instead of hand-editing `config/dashboard.json`, picked up live with no server restart)
- Wall Mode — already satisfied by an ordinary view (`config/views/wall.json` is a working example); no dedicated kiosk mode was needed beyond the existing View system
- Widget Resize — already satisfied by the span dropdown in the Settings widget checklist; no separate drag-resize handle was needed
- Module Load-Failure Visibility: `ModuleInfo`'s API import result is now tracked (`core/module_api.py`'s `MODULE_STATUS`) and surfaced as `available`/`error` on every widget from `/api/widgets` and `/api/views`. Settings shows a broken widget struck through with a ⚠️ tooltip carrying the error, instead of listing it as a normal widget that silently never loads data
- Widget Height: an optional `height` (px) on a layout item, editable via a dropdown next to the span selector in Settings; absent/0 means "auto" (grows to content, the pre-existing default) so every existing view is unaffected until a height is explicitly picked
- Widget Lock: an optional `locked` flag on a layout item, toggled via a 🔓/🔒 button in Settings. A locked widget can't be picked up by drag & drop and its span/height dropdowns are disabled, so a position/size you've settled on can't be nudged by accident
- Responsive Layout: below 640px every widget stacks full-width regardless of its chosen span (a 12-col grid otherwise leaves span-3/span-4 widgets too narrow to read on a phone), and the topbar/footer/Settings drawer adapt to a narrow viewport
- Tablet Mode: touch drag & drop for the layout editor. HTML5 native drag & drop never fires on touch devices at all, so `static/js/settings.js`'s `initDragAndDrop()` gained a parallel `touchstart`/`touchmove`/`touchend` implementation reaching the same `reorderWidget()` outcome, respecting Widget Lock exactly like the mouse version
- Widget Framework / Plugin Architecture: a module can ship its own `widget.js` (auto-served at `/modules/<id>/widget.js`, auto-included by the dashboard page) that self-registers via `registerWidget()` instead of needing `static/js/widgets.js` edited for every new widget. `modules/cameras/widget.js` is the real example — its updater and fast image-refresh loop moved out of `widgets.js` entirely. Verified with a from-scratch module (`examples/example_widget/`, installed and removed during testing): it rendered live data with zero central-file edits
- RSS Source Config UI (add/edit/delete news feeds from Settings instead of hand-editing `config/dashboard.json`, picked up on the next refresh with no server restart — same pattern as Camera Config UI)
- Widget Fullscreen: every widget card gets a ⛶ toggle (injected once by `templates/dashboard.html`'s grid/pool loops, not by each widget's own template) that uses the browser's native Fullscreen API on that widget's `.layout-cell` — works the same for a camera feed, the news list, or system metrics with no per-widget code. Camera snapshots drop their compact-card 4:3 aspect ratio while fullscreen so a feed can be inspected more closely
- Themes: dark (default) and light, toggled via a 🌙/☀️ button in the topbar, saved per-browser (`localStorage`). `static/css/style.css`'s color tokens are CSS custom properties with a `:root[data-theme="light"]` override block; the choice is applied before the stylesheet paints to avoid a flash of the wrong theme on load

---

# Version 2.1

## Widgets

- Meshtastic
- Zabbix
- Notifications

---

# Future

Possible long-term ideas

- Widget Marketplace
- Cloud Synchronization
- Multi-user Profiles
- Remote Dashboard Management
- Mobile Companion
- REST API Extensions

---

# Development Philosophy

SentinelDashboard evolves through small engineering sprints.

Every sprint:

- completes one feature or module;
- keeps the project in a working state;
- finishes with validation;
- finishes with a commit;
- improves the architecture together with the code.

