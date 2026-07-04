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

---

# Version 2.1

## Widgets

- Meshtastic
- Zabbix
- Notifications

## Layout

- Responsive Layout
- Tablet Mode

## Platform

- Widget Framework / Plugin Architecture (one and the same: let a module ship its own JS that self-registers, instead of centrally editing `static/js/widgets.js` for every new widget)

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

