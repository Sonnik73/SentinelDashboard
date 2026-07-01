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

- docs/ARCHITECTURE.md

---

# Project Structure

core/
modules/
routes/
config/
templates/
static/
tools/
docs/

---

# Quick Start

```bash
git clone git@github.com:Sonnik73/SentinelDashboard.git

cd SentinelDashboard

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

uvicorn app:app --host 0.0.0.0 --port 8000
Open:
http://<RaspberryPi-IP>:8000
Example:
http://192.168.88.107:8000
Documentation
INSTALL.md
DEVELOPMENT.md
ARCHITECTURE.md
ROADMAP.md
Development
Before every commit:
python tools/check.py
Recommended workflow:
One feature

↓

Validation

↓

Commit

↓

Push
Current Status
Current Version
v1.0.6
Completed
Stable v1
Widget System
View Engine
Layout Engine
Live Preview
Layout Editor
Next Target
v2.0
Drag & Drop
View Manager
Responsive Layout
Widget Framework
Plugin Architecture
License
MIT License
