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
- Cameras Widget (RTSP snapshot via `ffmpeg`, not live streaming — see `docs/MODULES.md`; RTSP path convention not yet verified against real hardware)

---

# Version 2.1

## Widgets

- Meshtastic
- Zabbix
- Notifications

## Layout

- Responsive Layout
- Tablet Mode
- Wall Mode
- Widget Height
- Widget Lock
- Widget Resize

## Platform

- Widget Framework
- Plugin Architecture
- Module load-failure visibility: `core/loader.py`/`core/module_api.py` don't currently expose *why* a module's API failed to load (e.g. invalid config/dashboard.json). `/api/widgets` still reports a broken module as `"enabled": true`, so Settings offers it as a normal widget that silently never loads data. Needs an `available`/error flag on `ModuleInfo`, surfaced through `/api/widgets` and shown in the frontend

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

