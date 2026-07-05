import os
import subprocess
import threading
import time
from pathlib import Path

from core.cache import CACHE_DIR, load_cache, save_cache
from core.config import get_section, update_section
from core.time import now_string

# Read fresh from config/dashboard.json on every call rather than caching
# at import time, so a camera added/edited/removed through Settings takes
# effect immediately - no server restart needed, unlike a manual edit of
# the JSON file (every other module still reads its config once at import,
# since none of them expose an in-app way to change it).
def get_hosts():
    return get_section("cameras").get("hosts", [])


# Genuine multi-fps rules out spawning ffmpeg per request (an RTSP
# handshake alone can take 1-2s). Instead one ffmpeg process per camera
# runs continuously, streaming MJPEG to stdout; a background thread splits
# it into frames and writes each one atomically (temp file + rename) so a
# concurrent HTTP reader never sees a torn/partial JPEG.
FRAME_RATE = 2
STARTUP_TIMEOUT = 8          # max wait for a fresh stream's first frame
STALE_AFTER = 5              # seconds without a new frame before restarting
STATUS_WRITE_INTERVAL = 2    # throttle status + last-known-good writes

# The live frame is rewritten several times a second - keep it on tmpfs
# (RAM-backed) rather than wearing out the SD card. Falls back to the
# normal cache dir if /dev/shm isn't available (e.g. non-Linux dev boxes).
LIVE_DIR = Path("/dev/shm/sentinel_cameras") if Path("/dev/shm").is_dir() else CACHE_DIR / "live"

JPEG_SOI = b"\xff\xd8"
JPEG_EOI = b"\xff\xd9"

_streams = {}
_streams_lock = threading.Lock()


class Stream:
    def __init__(self, camera_id):
        self.camera_id = camera_id
        self.process = None
        self.thread = None
        self.last_frame_at = 0
        self.last_status_write = 0
        self.error = None


def get_widget_instances():
    """Each configured camera gets its own independently placeable widget
    (see core/widgets.py) instead of one widget listing every camera -
    the user wants two cameras side by side as separate grid cells, not
    one shared card."""
    return [{"id": host["id"], "title": host["name"]} for host in get_hosts()]


def find_host(camera_id):
    for host in get_hosts():
        if host["id"] == camera_id:
            return host

    raise ValueError(f"Unknown camera: {camera_id}")


def validate_camera_id(camera_id: str) -> str:
    camera_id = (camera_id or "").strip().lower()

    if not camera_id or not camera_id.replace("-", "").replace("_", "").isalnum():
        raise ValueError("Camera id may contain only letters, numbers, hyphens and underscores")

    return camera_id


def _save_hosts(hosts: list):
    update_section("cameras", {"hosts": hosts})


def add_camera(camera_id: str, name: str, ip: str, port: int = 554, path: str = "/1/1"):
    camera_id = validate_camera_id(camera_id)
    name = (name or "").strip()
    ip = (ip or "").strip()

    if not name:
        raise ValueError("Name is required")

    if not ip:
        raise ValueError("IP is required")

    hosts = get_hosts()

    if any(host["id"] == camera_id for host in hosts):
        raise ValueError(f"Camera already exists: {camera_id}")

    host = {
        "id": camera_id,
        "name": name,
        "ip": ip,
        "port": int(port) if port else 554,
        "path": (path or "/1/1").strip() or "/1/1",
    }

    hosts.append(host)
    _save_hosts(hosts)

    return host


def update_camera(camera_id: str, name: str = None, ip: str = None, port=None, path: str = None):
    hosts = get_hosts()

    for host in hosts:
        if host["id"] != camera_id:
            continue

        if name and name.strip():
            host["name"] = name.strip()
        if ip and ip.strip():
            host["ip"] = ip.strip()
        if port:
            host["port"] = int(port)
        if path and path.strip():
            host["path"] = path.strip()

        _save_hosts(hosts)
        return host

    raise ValueError(f"Unknown camera: {camera_id}")


def delete_camera(camera_id: str):
    hosts = get_hosts()
    remaining = [host for host in hosts if host["id"] != camera_id]

    if len(remaining) == len(hosts):
        raise ValueError(f"Unknown camera: {camera_id}")

    with _streams_lock:
        stream = _streams.pop(camera_id, None)
        if stream is not None:
            _stop_stream(stream)

    _save_hosts(remaining)


def build_rtsp_url(host):
    username = os.environ.get("CAMERA_USERNAME", "admin")
    password = os.environ.get("CAMERA_PASSWORD", "")
    port = host.get("port", 554)
    path = host.get("path", "/1/1")

    return f"rtsp://{username}:{password}@{host['ip']}:{port}{path}"


def get_live_file(camera_id):
    return LIVE_DIR / f"camera_{camera_id}.jpg"


def get_snapshot_file(camera_id):
    """Last-known-good JPEG. Lives on the normal (SD-card) cache dir so it
    survives a restart, unlike the live tmpfs frame."""
    return CACHE_DIR / f"camera_{camera_id}.jpg"


def _write_status(camera_id, source, error=None):
    statuses = load_cache("cameras") or {}
    statuses[camera_id] = {
        "source": source,
        "last_sync": now_string(),
        "error": error,
    }
    save_cache("cameras", statuses)


def _read_frames(stream):
    """Background thread for the lifetime of one camera's ffmpeg process:
    splits its stdout into complete JPEG frames. Every frame is written to
    the tmpfs live file (cheap, RAM-backed); the SD-card-backed fallback
    snapshot and status metadata are only touched once per
    STATUS_WRITE_INTERVAL to avoid wearing the SD card at 3 fps."""
    live_file = get_live_file(stream.camera_id)
    tmp_file = live_file.with_suffix(".tmp.jpg")
    snapshot_file = get_snapshot_file(stream.camera_id)
    buffer = b""

    try:
        while True:
            chunk = stream.process.stdout.read(4096)
            if not chunk:
                break

            buffer += chunk

            while True:
                start = buffer.find(JPEG_SOI)
                if start == -1:
                    buffer = b""
                    break

                end = buffer.find(JPEG_EOI, start + 2)
                if end == -1:
                    buffer = buffer[start:]
                    break

                frame = buffer[start:end + 2]
                buffer = buffer[end + 2:]

                tmp_file.write_bytes(frame)
                tmp_file.rename(live_file)
                stream.last_frame_at = time.monotonic()

                now = time.monotonic()
                if now - stream.last_status_write >= STATUS_WRITE_INTERVAL:
                    stream.last_status_write = now
                    snapshot_file.write_bytes(frame)
                    _write_status(stream.camera_id, "online")

    except Exception as error:
        stream.error = str(error)


def _start_stream(camera_id):
    host = find_host(camera_id)
    stream = Stream(camera_id)

    LIVE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    stream.process = subprocess.Popen(
        [
            "ffmpeg", "-y",
            "-rtsp_transport", "tcp",
            "-timeout", "5000000",
            "-i", build_rtsp_url(host),
            "-r", str(FRAME_RATE),
            "-q:v", "5",
            "-f", "mjpeg",
            "-",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )

    stream.thread = threading.Thread(target=_read_frames, args=(stream,), daemon=True)
    stream.thread.start()

    return stream


def _stop_stream(stream):
    if stream.process and stream.process.poll() is None:
        stream.process.terminate()
        try:
            stream.process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            stream.process.kill()


def ensure_stream(camera_id):
    """Lazily starts a camera's stream on first use, and restarts it if the
    ffmpeg process has died or stopped producing frames."""
    with _streams_lock:
        stream = _streams.get(camera_id)

        is_dead = stream is not None and stream.process.poll() is not None
        is_stale = (
            stream is not None
            and stream.last_frame_at
            and time.monotonic() - stream.last_frame_at > STALE_AFTER
        )

        if stream is None or is_dead or is_stale:
            if stream is not None:
                _stop_stream(stream)
            stream = _start_stream(camera_id)
            _streams[camera_id] = stream

        return stream


def stop_all_streams():
    """Called on app shutdown so ffmpeg processes don't outlive the server."""
    with _streams_lock:
        for stream in _streams.values():
            _stop_stream(stream)
        _streams.clear()


def get_camera_frame(camera_id):
    """Returns (image_bytes, source). Ensures the camera's stream is
    running and, once it has produced at least one frame, just reads the
    live tmpfs file - no ffmpeg spawned per call, which is what makes 3 fps
    viable. Falls back to the last cached JPEG if the stream never
    produces a frame (same offline pattern as weather/rss)."""
    find_host(camera_id)  # raises ValueError for unknown cameras
    stream = ensure_stream(camera_id)
    live_file = get_live_file(camera_id)

    deadline = time.monotonic() + STARTUP_TIMEOUT
    while time.monotonic() < deadline:
        if live_file.exists():
            try:
                return live_file.read_bytes(), "online"
            except OSError:
                pass
        if stream.process.poll() is not None:
            break
        time.sleep(0.05)

    error = stream.error or "camera stream did not produce a frame"
    snapshot_file = get_snapshot_file(camera_id)

    if snapshot_file.exists():
        _write_status(camera_id, "cache", error)
        return snapshot_file.read_bytes(), "cache"

    _write_status(camera_id, "error", error)
    raise RuntimeError(error)


def get_cameras_status():
    statuses = load_cache("cameras") or {}
    cameras = []

    for host in get_hosts():
        status = statuses.get(host["id"], {})
        cameras.append({
            "id": host["id"],
            "name": host["name"],
            "source": status.get("source", "error"),
            "last_sync": status.get("last_sync"),
            "error": status.get("error"),
        })

    return {"cameras": cameras}
