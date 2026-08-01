import platform
import re
import socket
import subprocess

import psutil

from core.config import get_section, update_section
from core.time import now_string


IS_WINDOWS = platform.system() == "Windows"
IS_MACOS = platform.system() == "Darwin"

# ping's output is localized - Russian Windows prints "время=12мс" where
# Linux prints "time=8.35 ms" - so anchor on the number in front of the
# millisecond unit rather than on the English word, and accept "<1ms"
# alongside "=1ms" (Windows reports sub-millisecond replies that way).
PING_TIME_PATTERN = re.compile(r"[=<]\s*(\d+(?:[.,]\d+)?)\s*(?:ms|мс)", re.IGNORECASE)

# Windows' ping exits 0 even when a router answers "Destination host
# unreachable" on behalf of a host that is actually down, so a zero exit
# code alone is not proof of life there. This is exactly how the cameras
# turned out to be missing from the network - ping said "Destination host
# unreachable" while still being a "successful" run.
UNREACHABLE_MARKERS = ("unreachable", "недоступен", "недостижим", "expired", "истек")


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


def build_ping_command(address: str):
    if IS_WINDOWS:
        # -n is the count and -w the per-reply timeout in milliseconds;
        # Linux spells the same two things -c and -W (seconds).
        return ["ping", "-n", "1", "-w", "1000", address]

    if IS_MACOS:
        # macOS uses -W as well, but reads it as milliseconds, not seconds.
        return ["ping", "-c", "1", "-W", "1000", address]

    return ["ping", "-c", "1", "-W", "1", address]


def decode_output(raw: bytes) -> str:
    """Windows' ping writes in the console OEM code page (cp866 on a Russian
    system), which is not what Python decodes with by default - getting it
    wrong turns "мс" into mojibake and silently breaks latency parsing. The
    "oem" codec resolves to whichever page the console actually uses and
    only exists on Windows, hence the fallback."""
    try:
        return raw.decode("oem")
    except (LookupError, UnicodeDecodeError, ValueError):
        return raw.decode("utf-8", errors="replace")


def parse_ping_ms(output: str):
    match = PING_TIME_PATTERN.search(output)

    if not match:
        return None

    # Some locales print a decimal comma, which float() won't take.
    return round(float(match.group(1).replace(",", ".")), 1)


def ping_host(address: str):
    try:
        result = subprocess.run(
            build_ping_command(address),
            capture_output=True,
            timeout=2,
        )

        if result.returncode != 0:
            return {
                "online": False,
                "ping_ms": None,
            }

        output = decode_output(result.stdout)
        ping_ms = parse_ping_ms(output)

        # A reply carrying no round-trip time is not evidence the host
        # answered - on Windows that is what an "unreachable" bounce from
        # the router looks like, exit code 0 and all.
        if ping_ms is None and any(marker in output.lower() for marker in UNREACHABLE_MARKERS):
            return {
                "online": False,
                "ping_ms": None,
            }

        return {
            "online": True,
            "ping_ms": ping_ms,
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

def classify_interface(name: str) -> str:
    """Maps an adapter name to a friendly label. Linux uses short prefixes
    (wlan0, eth0, enp3s0) while Windows uses human names that are localized
    ("Wi-Fi", "Ethernet", "Беспроводная сеть")."""
    lowered = name.lower()

    if lowered.startswith("wl") or "wi-fi" in lowered or "wifi" in lowered \
            or "wireless" in lowered or "беспровод" in lowered:
        return "Wi-Fi"

    if lowered.startswith(("eth", "en")) or "ethernet" in lowered or "локальной сети" in lowered:
        return "Ethernet"

    return name


def detect_interface_via_psutil():
    """Finds the adapter that owns the address we actually route out of.
    Used where `ip route` doesn't exist - Windows, and Linux installs
    without iproute2, which used to report "Unknown" on both."""
    local_ip = get_local_ip()

    if local_ip == "Unknown":
        return "Unknown"

    try:
        for name, addresses in psutil.net_if_addrs().items():
            for address in addresses:
                if address.family == socket.AF_INET and address.address == local_ip:
                    return classify_interface(name)
    except Exception:
        pass

    return "Unknown"


def detect_interface():
    if not IS_WINDOWS:
        try:
            result = subprocess.run(
                ["ip", "route", "get", "1.1.1.1"],
                capture_output=True,
                text=True,
                timeout=2,
            )

            match = re.search(r"dev\s+(\S+)", result.stdout)

            if match:
                return classify_interface(match.group(1))

        except Exception:
            pass

    return detect_interface_via_psutil()


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
