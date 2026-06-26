from datetime import datetime
import platform
import psutil


def get_system_metrics():
    return {
        "time": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
        "hostname": platform.node(),
        "cpu_percent": psutil.cpu_percent(interval=0.5),
        "memory_percent": psutil.virtual_memory().percent,
    }
