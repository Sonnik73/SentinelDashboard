import re
import socket
import subprocess

from core.config import get_section
from core.time import now_string


NETWORK_CONFIG = get_section("network")


def ping_host(address: str):
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "1", address],
            capture_output=True,
            text=True,
            timeout=2,
        )

        if result.returncode != 0:
            return {
                "online": False,
                "ping_ms": None,
            }

        match = re.search(r"time=([\d.]+)", result.stdout)

        return {
            "online": True,
            "ping_ms": round(float(match.group(1)), 1) if match else None,
        }

    except Exception:
        return {
            "online": False,
            "ping_ms": None,
        }




def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("1.1.1.1", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "Unknown"

def detect_interface():
    try:
        result = subprocess.run(
            ["ip", "route", "get", "1.1.1.1"],
            capture_output=True,
            text=True,
            timeout=2,
        )

        match = re.search(r"dev\s+(\S+)", result.stdout)

        if not match:
            return "Unknown"

        interface = match.group(1)

        if interface.startswith("wl"):
            return "Wi-Fi"

        if interface.startswith("eth") or interface.startswith("en"):
            return "Ethernet"

        return interface

    except Exception:
        return "Unknown"


def get_network_status():
    hosts = []

    for host in NETWORK_CONFIG.get("hosts", []):
        address = host["address"]
        ping_result = ping_host(address)

        hosts.append(
            {
                "name": host["name"],
                "address": address,
                "online": ping_result["online"],
                "ping_ms": ping_result["ping_ms"],
            }
        )

    return {
        "last_sync": now_string(),
        "interface": detect_interface(),
        "ip": get_local_ip(),
        "hosts": hosts,
    }
