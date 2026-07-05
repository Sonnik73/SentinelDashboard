// Ships with the cameras module itself (see core/loader.py's optional
// widget.js convention) rather than living in static/js/widgets.js -
// demonstrates that a new widget module needs no central JS file edited.

// Fallback used before a camera's real fps is known (matches DEFAULT_FPS
// in modules/cameras/service.py) and for any camera predating the fps
// field.
const DEFAULT_CAMERA_FPS = 2;

// Each camera can have its own fps, so each gets its own setInterval
// rather than one shared one - keyed by widget instance id.
const cameraFrameIntervals = {};
const cameraFps = {};

// Scoped to the visible grid only - a camera widget not placed in the
// current view still exists (hidden) in the widget pool for the Settings
// checkbox list, and refreshing its image would needlessly keep its
// ffmpeg stream alive on the backend for a card nobody sees.
function refreshCameraFrame(instanceId) {
    const grid = document.querySelector(".grid");
    if (!grid) return;

    const img = grid.querySelector(`#camera-img-${instanceId}`);
    if (!img) return;

    img.src = `/api/cameras/${instanceId}/snapshot?t=${Date.now()}`;
}

// (Re)starts this camera's own fast image-refresh loop at its configured
// fps - independent of the ~10s manifest-driven status poll, since
// rebuilding the <img> node on every status poll would defeat the point
// (a fresh node re-decodes from scratch, causing visible flicker at a
// fast refresh rate). A no-op if the fps hasn't actually changed, so the
// ~10s status poll doesn't restart (and hiccup) the loop every time.
function ensureCameraFrameLoop(instanceId, fps) {
    fps = fps || DEFAULT_CAMERA_FPS;
    if (cameraFps[instanceId] === fps) return;

    cameraFps[instanceId] = fps;

    if (cameraFrameIntervals[instanceId]) {
        clearInterval(cameraFrameIntervals[instanceId]);
    }

    const intervalMs = Math.round(1000 / fps);
    refreshCameraFrame(instanceId);
    cameraFrameIntervals[instanceId] = setInterval(() => refreshCameraFrame(instanceId), intervalMs);
}

// Each configured camera is its own widget instance (see
// core/widgets.py's get_widget_instances()), so a view can place cam1 and
// cam2 as separate, independently sized/positioned cards. updateCamera()
// touches that one camera's status text and (re)syncs its frame loop to
// its current fps.
async function updateCamera(instanceId) {
    const statusEl = document.getElementById(`camera-status-${instanceId}`);
    if (!statusEl) return;

    try {
        const data = await apiGet("/api/cameras");
        const camera = (data.cameras || []).find(c => c.id === instanceId);
        if (!camera) return;

        const statusIcon = camera.source === "online" ? "🟢" :
            camera.source === "cache" ? "🟡" : "🔴";

        statusEl.textContent = `${statusIcon} ${camera.last_sync ?? "нет сигнала"}`;

        ensureCameraFrameLoop(instanceId, camera.fps);

    } catch (error) {
        console.error("Camera:", error);
    }
}

registerWidget("cameras", updateCamera);
