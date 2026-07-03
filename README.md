# SentinelDashboard

> Modular information dashboard for Raspberry Pi and Linux servers.

SentinelDashboard is a lightweight, modular dashboard platform designed for Raspberry Pi, Linux servers and wall-mounted information displays.

The project focuses on:

- modular architecture
- offline-first operation
- simple JSON configuration
- live layout editing
- long-term maintainability

---

# Features

## System Monitoring

- CPU
- Memory
- Disk usage
- Temperature
- Uptime
- Hostname

## Information Widgets

- 🌤 Weather
- 📰 RSS News
- 🌐 Network Monitoring
- 🎂 Birthdays
- 📷 Cameras

## Dashboard Engine

- Multiple dashboard views
- Layout Engine
- Live Preview
- Widget span editor
- Automatic row packing
- JSON-based layouts
- Shareable dashboard links

---

# Architecture

Browser

↓

FastAPI

↓

Routes

↓

Modules

↓

Core

For a detailed description see:

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

# Project Structure

```
core/
modules/
routes/
config/
templates/
static/
tools/
docs/
```

---

# Requirements

- Python 3.11+ (developed and tested on Python 3.13)
- pip
- Linux or Raspberry Pi OS (Raspberry Pi 4/5 recommended)
- No Node.js / npm required — the project runs as a single `uvicorn` process

---

# Quick Start

```bash
git clone git@github.com:Sonnik73/SentinelDashboard.git

cd SentinelDashboard

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

uvicorn app:app --host 0.0.0.0 --port 8000
```

Open in your browser:

```
http://<RaspberryPi-IP>:8000
```

Example:

```
http://192.168.88.107:8000
```

---

# Documentation

- [INSTALL.md](docs/INSTALL.md)
- [DEVELOPMENT.md](docs/DEVELOPMENT.md)
- [ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [ENGINEERING.md](docs/ENGINEERING.md)
- [MODULES.md](docs/MODULES.md)
- [ROADMAP.md](docs/ROADMAP.md)
- [RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md)

---

# Development

Before every commit:

```bash
python tools/check.py
```

Recommended workflow:

One feature → Validation → Commit → Push

---

# Current Status

**Current Version:** see [VERSION](VERSION) / [CHANGELOG.md](CHANGELOG.md)

## Completed (Stable v1)

- Widget System
- View Engine
- Layout Engine
- Live Preview
- Layout Editor
- Modular API architecture
- Automatic module discovery

## Planned (after v2.0)

- Drag & Drop
- View Manager
- Responsive Layout
- Widget Framework
- Plugin Architecture

---

# License

MIT License
