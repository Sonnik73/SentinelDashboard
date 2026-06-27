from datetime import timedelta
from core.time import now, now_string
import platform
import subprocess

import psutil


def get_temperature():
    try:
        result = subprocess.run(
            ["vcgencmd", "measure_temp"],
            capture_output=True,
            text=True,
            timeout=2,
        )

        raw_temp = result.stdout.strip()
        return raw_temp.replace("temp=", "").replace("'C", "°C")

    except Exception:
        return "N/A"


def format_uptime(seconds):
    uptime = timedelta(seconds=int(seconds))

    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    return f"{days}д {hours}ч {minutes}м"


def get_system_metrics():
    return {
	"time": now_string(),
        "hostname": platform.node(),
        "cpu_percent": psutil.cpu_percent(interval=0.5),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
        "temperature": get_temperature(),
	"uptime": format_uptime(now().timestamp() - psutil.boot_time()),
    }
