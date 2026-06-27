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

        return result.returncode == 0

    except Exception:
        return False


def get_network_status():
    hosts = []

    for host in NETWORK_CONFIG.get("hosts", []):
        address = host["address"]
        is_online = ping_host(address)

        hosts.append(
            {
                "name": host["name"],
                "address": address,
                "online": is_online,
            }
        )

    return {
        "last_sync": now_string(),
        "interface": "Wi-Fi",
        "hosts": hosts,
    }

