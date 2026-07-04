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


// The camera image itself refreshes on its own fast interval (see
// refreshCameraFrames below), independent of the ~10s manifest-driven
// status poll - rebuilding the whole <img> on every status poll would
// defeat that (a fresh DOM node re-decodes from scratch, causing visible
// flicker at a fast refresh rate). updateCameras() only creates each
// camera's DOM node once and afterwards just updates its status text.
let cameraIds = [];

function buildCameraItem(camera) {
    const item = document.createElement("div");
    item.className = "camera-item";
    item.id = `camera-item-${camera.id}`;
    item.innerHTML = `
        <div class="camera-header">
            <b>${camera.name}</b>
            <span class="small" id="camera-status-${camera.id}"></span>
        </div>
        <img
            class="camera-snapshot"
            id="camera-img-${camera.id}"
            alt="${camera.name}"
            onerror="this.classList.add('camera-snapshot-error')"
            onload="this.classList.remove('camera-snapshot-error')"
        >
    `;
    return item;
}

function updateCameraStatus(camera) {
    const statusEl = document.getElementById(`camera-status-${camera.id}`);
    if (!statusEl) return;

    const statusIcon = camera.source === "online" ? "🟢" :
        camera.source === "cache" ? "🟡" : "🔴";

    statusEl.textContent = `${statusIcon} ${camera.last_sync ?? "нет сигнала"}`;
}

async function updateCameras() {
    const container = document.getElementById("cameras-list");
    if (!container) return;

    try {
        const data = await apiGet("/api/cameras");

        if (!data.cameras || data.cameras.length === 0) {
            container.innerHTML = `<p class="small">Камеры не настроены</p>`;
            cameraIds = [];
            return;
        }

        cameraIds = data.cameras.map(camera => camera.id);

        data.cameras.forEach(camera => {
            if (!document.getElementById(`camera-item-${camera.id}`)) {
                container.appendChild(buildCameraItem(camera));
            }
            updateCameraStatus(camera);
        });

        refreshCameraFrames();

    } catch (error) {
        console.error("Cameras:", error);
    }
}

function refreshCameraFrames() {
    cameraIds.forEach(id => {
        const img = document.getElementById(`camera-img-${id}`);
        if (img) img.src = `/api/cameras/${id}/snapshot?t=${Date.now()}`;
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
    cameras: updateCameras,
};

Object.values(WIDGET_UPDATERS).forEach(updater => updater());

// Runs independently of the manifest-driven refresh above - camera frames
// need ~3/second, far faster than any widget's `refresh` field expresses.
const CAMERA_FRAME_INTERVAL_MS = 333;
setInterval(refreshCameraFrames, CAMERA_FRAME_INTERVAL_MS);

async function scheduleWidgetUpdates() {
    try {
        const widgets = await apiGet("/api/widgets");

        widgets.forEach(widget => {
            const updater = WIDGET_UPDATERS[widget.id];
            if (!updater || !widget.refresh) return;

            setInterval(updater, widget.refresh * 1000);
        });
    } catch (error) {
        console.error("Widget schedule:", error);
    }
}

scheduleWidgetUpdates();
