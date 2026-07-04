import os
import subprocess

from core.cache import CACHE_DIR, load_cache, save_cache
from core.config import get_section
from core.time import now_string

CAMERAS_CONFIG = get_section("cameras")
HOSTS = CAMERAS_CONFIG.get("hosts", [])

# A single-frame RTSP grab, not a live stream - ffmpeg connects, waits for
# a keyframe, and exits. 8s covers a slow RTSP handshake on a real camera;
# the internal -timeout below lets ffmpeg fail on its own before that.
FFMPEG_TIMEOUT = 8


def find_host(camera_id):
    for host in HOSTS:
        if host["id"] == camera_id:
            return host

    raise ValueError(f"Unknown camera: {camera_id}")


def build_rtsp_url(host):
    username = os.environ.get("CAMERA_USERNAME", "admin")
    password = os.environ.get("CAMERA_PASSWORD", "")
    port = host.get("port", 554)
    path = host.get("path", "/1/1")

    return f"rtsp://{username}:{password}@{host['ip']}:{port}{path}"


def get_snapshot_file(camera_id):
    return CACHE_DIR / f"camera_{camera_id}.jpg"


def capture_snapshot(host):
    result = subprocess.run(
        [
            "ffmpeg", "-y",
            "-rtsp_transport", "tcp",
            "-timeout", "5000000",
            "-i", build_rtsp_url(host),
            "-frames:v", "1",
            "-q:v", "5",
            "-f", "image2",
            "-",
        ],
        capture_output=True,
        timeout=FFMPEG_TIMEOUT,
    )

    if result.returncode != 0 or not result.stdout:
        stderr_lines = result.stderr.decode(errors="replace").strip().splitlines()
        raise RuntimeError(stderr_lines[-1] if stderr_lines else "ffmpeg produced no output")

    return result.stdout


def get_camera_snapshot(camera_id):
    """Returns (image_bytes, source). Captures a fresh frame on success,
    or falls back to the last cached JPEG on failure, same offline
    pattern as weather/rss (see core/cache.py)."""
    host = find_host(camera_id)
    snapshot_file = get_snapshot_file(camera_id)
    statuses = load_cache("cameras") or {}

    try:
        image_bytes = capture_snapshot(host)

        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        snapshot_file.write_bytes(image_bytes)

        statuses[camera_id] = {"source": "online", "last_sync": now_string()}
        save_cache("cameras", statuses)

        return image_bytes, "online"

    except Exception as error:
        previous = statuses.get(camera_id, {})

        statuses[camera_id] = {
            "source": "cache" if snapshot_file.exists() else "error",
            "last_sync": previous.get("last_sync"),
            "error": str(error),
        }
        save_cache("cameras", statuses)

        if snapshot_file.exists():
            return snapshot_file.read_bytes(), "cache"

        raise


def get_cameras_status():
    statuses = load_cache("cameras") or {}
    cameras = []

    for host in HOSTS:
        status = statuses.get(host["id"], {})
        cameras.append({
            "id": host["id"],
            "name": host["name"],
            "source": status.get("source", "error"),
            "last_sync": status.get("last_sync"),
            "error": status.get("error"),
        })

    return {"cameras": cameras}
