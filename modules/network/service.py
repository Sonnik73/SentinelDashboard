import re
import socket
import subprocess

from core.config import get_section, update_section
from core.time import now_string


# Read fresh from config/dashboard.json on every call rather than caching
# at import time, so a host added/edited/removed through Settings takes
# effect on the next refresh - no server restart needed (same reasoning
# as modules/cameras/service.py's get_hosts()).
def get_hosts():
    return get_section("network").get("hosts", [])


def _save_hosts(hosts: list):
    # Merge into the existing section rather than replacing it outright -
    # see modules/weather/service.py's _save_cities() for why (a blind
    # overwrite silently drops any sibling key the section might carry).
    section = get_section("network")
    section["hosts"] = hosts
    update_section("network", section)


def validate_host(name: str, address: str) -> tuple[str, str]:
    name = (name or "").strip()
    address = (address or "").strip()

    if not name:
        raise ValueError("Name is required")

    if not address:
        raise ValueError("Address is required")

    return name, address


def add_host(name: str, address: str):
    name, address = validate_host(name, address)
    hosts = get_hosts()

    if any(host["name"] == name for host in hosts):
        raise ValueError(f"Host already exists: {name}")

    host = {"name": name, "address": address}
    hosts.append(host)
    _save_hosts(hosts)

    return host


def update_host(name: str, new_name: str, new_address: str):
    new_name, new_address = validate_host(new_name, new_address)
    hosts = get_hosts()

    for host in hosts:
        if host["name"] != name:
            continue

        host["name"] = new_name
        host["address"] = new_address
        _save_hosts(hosts)
        return host

    raise ValueError(f"Unknown host: {name}")


def delete_host(name: str):
    hosts = get_hosts()
    remaining = [host for host in hosts if host["name"] != name]

    if len(remaining) == len(hosts):
        raise ValueError(f"Unknown host: {name}")

    _save_hosts(remaining)


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

    for host in get_hosts():
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
