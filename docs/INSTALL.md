# Installation

Requirements and supported platforms are listed in the main [README.md](../README.md#requirements).

## 1. Clone the repository

```bash
git clone git@github.com:Sonnik73/SentinelDashboard.git
cd SentinelDashboard
```

## 2. Set up a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure weather city URLs

The weather widget scrapes rp5.ru — no API key needed, but each city in `config/dashboard.json` under `weather.cities` needs its exact rp5.ru page URL (there's no reliable way to generate it from a city name). To find it: visit rp5.ru, search for your city, and copy the address bar (e.g. `https://rp5.ru/Погода_в_Ульяновске`). See [MODULES.md](MODULES.md) for details.

## 5. Set up cameras (optional)

The cameras widget grabs a still frame from each camera's RTSP stream using `ffmpeg`, which isn't installed by default on Raspberry Pi OS:

```bash
sudo apt install ffmpeg
```

Each camera is listed in `config/dashboard.json` under `cameras.hosts` (`id`, `name`, `ip`, `port`, `path` — the RTSP path is model-specific, see [MODULES.md](MODULES.md)). The username/password are shared across all cameras and read from the environment, not committed to config:

```bash
export CAMERA_USERNAME=admin
export CAMERA_PASSWORD=your-camera-password
```

If ffmpeg isn't installed or a camera is unreachable, the widget falls back to the last cached snapshot (or shows "нет сигнала") instead of crashing — the rest of the dashboard is unaffected.

## 6. Run the dashboard

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

Open in your browser:

```
http://<device-ip>:8000
```

---

## Running as a service (systemd)

To have SentinelDashboard start automatically on boot, create a systemd unit.

Create `/etc/systemd/system/sentinel-dashboard.service`:

```ini
[Unit]
Description=SentinelDashboard
After=network.target

[Service]
Type=simple
User=<your-username>
WorkingDirectory=/home/<your-username>/sentinel
Environment=CAMERA_USERNAME=admin
Environment=CAMERA_PASSWORD=your-camera-password
ExecStart=/home/<your-username>/sentinel/.venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Replace `<your-username>` and the path with your actual install location (for example `/home/anonim/sentinel`).

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable sentinel-dashboard
sudo systemctl start sentinel-dashboard
```

Check status and logs:

```bash
sudo systemctl status sentinel-dashboard
journalctl -u sentinel-dashboard -f
```

---

## Troubleshooting

- **Port already in use** — change `--port 8000` to another port, or find and stop the process using it: `sudo lsof -i :8000`
- **Permission denied on port 80/443** — ports below 1024 require root; prefer running on port 8000+ behind a reverse proxy instead of running the app as root
- **`ModuleNotFoundError`** — make sure the virtual environment is activated (`source .venv/bin/activate`) before running `pip install` or `uvicorn`
