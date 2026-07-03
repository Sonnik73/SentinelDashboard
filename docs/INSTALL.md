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

## 4. Configure the weather API key

The weather widget uses the [Yandex Weather API](https://yandex.ru/dev/weather/), which requires a free API key. Get one from the Yandex Developer Console (the free "on your site" plan is capped at 50 requests/day, which is enough for this dashboard's built-in throttling — see [MODULES.md](MODULES.md)), then set it as an environment variable before starting the app:

```bash
export YANDEX_WEATHER_API_KEY=your-key-here
```

If the key isn't set, the weather widget falls back to cached/error state instead of crashing — the rest of the dashboard is unaffected.

## 5. Run the dashboard

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
Environment=YANDEX_WEATHER_API_KEY=your-key-here
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
