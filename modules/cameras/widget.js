// Ships with the cameras module itself (see core/loader.py's optional
// widget.js convention) rather than living in static/js/widgets.js -
// demonstrates that a new widget module needs no central JS file edited.

// Each configured camera is its own widget instance (see
// core/widgets.py's get_widget_instances()), so a view can place cam1 and
// cam2 as separate, independently sized/positioned cards. updateCamera()
// only touches that one camera's status text; the <img> itself refreshes
// on its own fast interval (refreshCameraFrames below), independent of
// the ~10s manifest-driven status poll - rebuilding the <img> node on
// every status poll would defeat that (a fresh node re-decodes from
// scratch, causing visible flicker at a fast refresh rate).
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

    } catch (error) {
        console.error("Camera:", error);
    }
}

// Scoped to the visible grid only - a camera widget not placed in the
// current view still exists (hidden) in the widget pool for the Settings
// checkbox list, and refreshing its image would needlessly keep its
// ffmpeg stream alive on the backend for a card nobody sees.
function refreshCameraFrames() {
    const grid = document.querySelector(".grid");
    if (!grid) return;

    grid.querySelectorAll(".camera-snapshot").forEach(img => {
        const instanceId = img.id.replace(/^camera-img-/, "");
        img.src = `/api/cameras/${instanceId}/snapshot?t=${Date.now()}`;
    });
}

registerWidget("cameras", updateCamera);

// Runs independently of the manifest-driven refresh handled by
// registerWidget above - camera frames need ~2/second (matches
// FRAME_RATE in modules/cameras/service.py), far faster than any widget's
// `refresh` field expresses.
const CAMERA_FRAME_INTERVAL_MS = 500;
refreshCameraFrames();
setInterval(refreshCameraFrames, CAMERA_FRAME_INTERVAL_MS);
