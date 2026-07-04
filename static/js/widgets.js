// ------------------------------
// Widget Updaters
// ------------------------------

async function updateSystemMetrics() {
    if (!document.getElementById("cpu")) return;

    try {
        const data = await apiGet("/api/system");

        document.getElementById("time").textContent = data.time;
        document.getElementById("cpu").textContent = data.cpu_percent + "%";
        document.getElementById("ram").textContent = data.memory_percent + "%";
        document.getElementById("disk").textContent = data.disk_percent + "%";
        document.getElementById("temperature").textContent = data.temperature;
        document.getElementById("uptime").textContent = data.uptime;
        document.getElementById("hostname").textContent = data.hostname;

        updateProgressBar("cpu-bar", data.cpu_percent);
        updateProgressBar("ram-bar", data.memory_percent);
        updateProgressBar("disk-bar", data.disk_percent);

    } catch (error) {
        console.error("System:", error);
    }
}


async function updateWeather() {
    const container = document.getElementById("weather-list");
    if (!container) return;

    try {
        const data = await apiGet("/api/weather");

        document.getElementById("weather-source").textContent =
            data.source === "online" ? "🟢 Онлайн" :
            data.source === "cache" ? "🟡 Кэш" : "🔴 Ошибка";

        document.getElementById("weather-sync").textContent =
            data.last_sync ?? "---";

        container.innerHTML = "";

        data.cities.forEach(city => {
            container.innerHTML += `
                <p>
                    <b>${city.name}</b><br>
                    🌡 ${city.temperature}°C
                    💧 ${city.humidity}%
                    💨 ${city.wind_speed} м/с
                </p>
            `;
        });

    } catch (error) {
        console.error("Weather:", error);
    }
}


async function updateRSS() {
    const container = document.getElementById("rss-list");
    if (!container) return;

    try {
        const data = await apiGet("/api/rss");

        document.getElementById("rss-source").textContent =
            data.source === "online" ? "🟢 Онлайн" :
            data.source === "cache" ? "🟡 Кэш" : "🔴 Ошибка";

        document.getElementById("rss-sync").textContent =
            data.last_sync ?? "---";

        container.innerHTML = "";

        data.items.slice(0, 5).forEach(item => {
            container.innerHTML += `
                <p>
                    <b>${item.source}</b><br>
                    <a href="${item.link}" target="_blank">
                        ${item.title}
                    </a>
                </p>
            `;
        });

    } catch (error) {
        console.error("RSS:", error);
    }
}


async function updateBirthdays() {
    const container = document.getElementById("birthdays-list");
    if (!container) return;

    try {
        const data = await apiGet("/api/birthdays");

        container.innerHTML = "";

        if (!data.items || data.items.length === 0) {
            container.innerHTML = `<p class="small">Нет записей</p>`;
            return;
        }

        data.items.slice(0, 5).forEach(item => {
            const days = item.days_until === 0
                ? "сегодня"
                : `через ${item.days_until} дн.`;

            container.innerHTML += `
                <p>
                    <b>${item.name}</b><br>
                    🎂 ${item.date} — ${days}<br>
                    <span class="small">${item.note ?? ""}</span>
                </p>
            `;
        });

    } catch (error) {
        console.error("Birthdays:", error);
    }
}


async function updateNetwork() {
    const container = document.getElementById("network-list");
    if (!container) return;

    try {
        const data = await apiGet("/api/network");

        document.getElementById("network-interface").textContent = data.interface;
        document.getElementById("network-ip").textContent = data.ip ?? "---";
        document.getElementById("network-sync").textContent = data.last_sync ?? "---";

        container.innerHTML = "";

        data.hosts.forEach(host => {
            const pingText = host.ping_ms !== null
                ? `${host.ping_ms} мс`
                : "нет ответа";

            container.innerHTML += `
                <div class="network-item">
                    <div class="network-main">
                        <span>${host.online ? "🟢" : "🔴"} <b>${host.name}</b></span>
                        <span>${pingText}</span>
                    </div>
                    <div class="small">${host.address}</div>
                </div>
            `;
        });

    } catch (error) {
        console.error("Network:", error);
    }
}


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


// ------------------------------
// Update Scheduler
// ------------------------------

const WIDGET_UPDATERS = {
    system: updateSystemMetrics,
    weather: updateWeather,
    rss: updateRSS,
    network: updateNetwork,
    birthdays: updateBirthdays,
    cameras: updateCamera,
};

// /api/widgets expands instanced widgets (currently only cameras) into
// composite ids like "cameras:cam1" - split off the instance id and hand
// it to the base module's updater. Ordinary widgets have no ":" and get
// undefined, which their (parameterless) updaters simply ignore.
async function scheduleWidgetUpdates() {
    try {
        const widgets = await apiGet("/api/widgets");

        widgets.forEach(widget => {
            const [baseId, instanceId] = widget.id.split(":");
            const updater = WIDGET_UPDATERS[baseId];
            if (!updater) return;

            updater(instanceId);

            if (widget.refresh) {
                setInterval(() => updater(instanceId), widget.refresh * 1000);
            }
        });
    } catch (error) {
        console.error("Widget schedule:", error);
    }
}

scheduleWidgetUpdates();

// Runs independently of the manifest-driven refresh above - camera frames
// need ~3/second, far faster than any widget's `refresh` field expresses.
const CAMERA_FRAME_INTERVAL_MS = 333;
refreshCameraFrames();
setInterval(refreshCameraFrames, CAMERA_FRAME_INTERVAL_MS);
