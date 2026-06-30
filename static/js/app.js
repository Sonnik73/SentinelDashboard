function updateProgressBar(barId, value) {
    const bar = document.getElementById(barId);
    if (!bar) return;

    bar.style.width = value + "%";

    if (value >= 80) {
        bar.style.background = "#ef4444";
    } else if (value >= 50) {
        bar.style.background = "#f59e0b";
    } else {
        bar.style.background = "#4ade80";
    }
}

async function updateSystemMetrics() {
    try {
        const response = await fetch("/api/system");
        const data = await response.json();





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
    try {
        const response = await fetch("/api/weather");
        const data = await response.json();

        document.getElementById("weather-source").textContent =
            data.source === "online" ? "🟢 Онлайн" :
            data.source === "cache" ? "🟡 Кэш" : "🔴 Ошибка";

        document.getElementById("weather-sync").textContent =
            data.last_sync ?? "---";

        const container = document.getElementById("weather-list");
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

updateSystemMetrics();
updateWeather();
updateRSS();
updateNetwork();
async function updateRSS() {
    try {
        const response = await fetch("/api/rss");
        const data = await response.json();

        document.getElementById("rss-source").textContent =
            data.source === "online" ? "🟢 Онлайн" :
            data.source === "cache" ? "🟡 Кэш" : "🔴 Ошибка";

        document.getElementById("rss-sync").textContent =
            data.last_sync ?? "---";

        const container = document.getElementById("rss-list");
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

async function updateNetwork() {
    try {
        const response = await fetch("/api/network");
        const data = await response.json();

        document.getElementById("network-interface").textContent = data.interface;
        document.getElementById("network-ip").textContent = data.ip ?? "---";
        document.getElementById("network-sync").textContent = data.last_sync ?? "---";

        const container = document.getElementById("network-list");
        container.innerHTML = "";

        data.hosts.forEach(host => {
            const pingText = host.ping_ms !== null ? `${host.ping_ms} мс` : "нет ответа";

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


setInterval(updateSystemMetrics, 1000);
setInterval(updateWeather, 600000);
setInterval(updateRSS, 300000);
setInterval(updateNetwork, 30000);

async function loadSettingsDrawer() {
    try {
        const params = new URLSearchParams(window.location.search);
        const view = params.get("view");
        const url = view ? `/api/views?view=${view}` : "/api/views";

        const response = await fetch(url);
        const data = await response.json();

        viewEditor.currentView = data.current.id;
        viewEditor.originalWidgets = [...data.widgets];
        viewEditor.currentWidgets = [...data.widgets];
        updateEditorState();

        document.getElementById("settings-current-view").textContent =
            `${data.current.title} (${data.current.id})`;

        const container = document.getElementById("settings-widgets");
        container.innerHTML = "";

        data.available_widgets.forEach(widget => {
            const checked = data.widgets.includes(widget.id) ? "checked" : "";

            container.innerHTML += `
                <label class="settings-widget">
                    <input
                        type="checkbox"
                        data-widget-id="${widget.id}"
                        ${checked}
                    >
                    <span>${widget.icon} ${widget.title}</span>
                    <select class="widget-span-select" data-widget-span="${widget.id}">
                        <option value="3">1/4</option>
                        <option value="4">1/3</option>
                        <option value="6">1/2</option>
                        <option value="12">Вся ширина</option>
                    </select>
                </label>
            `;
        });

        container.querySelectorAll("input[type='checkbox']").forEach(input => {
            input.addEventListener("change", () => {
                viewEditor.currentWidgets = Array.from(
                    container.querySelectorAll("input[type='checkbox']:checked")
                ).map(item => item.dataset.widgetId);

                updateEditorState();
        applyView();
                applyView();
            });
        });

    } catch (error) {
        console.error("Settings:", error);
    }
}

function initSettingsDrawer() {
    const button = document.getElementById("settings-button");
    const close = document.getElementById("settings-close");
    const drawer = document.getElementById("settings-drawer");
    const overlay = document.getElementById("settings-overlay");

    if (!button || !close || !drawer || !overlay) return;

    function openDrawer() {
        drawer.classList.add("open");
        overlay.classList.add("open");
        loadSettingsDrawer();
    }

    function closeDrawer() {
        drawer.classList.remove("open");
        overlay.classList.remove("open");
    }

    button.addEventListener("click", openDrawer);
    close.addEventListener("click", closeDrawer);
    overlay.addEventListener("click", closeDrawer);
}

initSettingsDrawer();



// ------------------------------
// View Editor State
// ------------------------------

const viewEditor = {
    originalWidgets: [],
    currentWidgets: [],
    currentView: "",
};

function arraysEqual(a, b) {
    return JSON.stringify([...a].sort()) === JSON.stringify([...b].sort());
}

function hasUnsavedChanges() {
    return !arraysEqual(
        viewEditor.originalWidgets,
        viewEditor.currentWidgets
    );
}



function applyView() {
    document.querySelectorAll("[data-widget]").forEach(card => {
        const widget = card.dataset.widget;

        if (viewEditor.currentWidgets.includes(widget)) {
            card.classList.remove("hidden-widget");
        } else {
            card.classList.add("hidden-widget");
        }
    });
}

function updateEditorState() {
    const state = document.getElementById("settings-state");
    const reset = document.getElementById("reset-view");

    if (!state) return;

    if (hasUnsavedChanges()) {
        state.textContent = "🟡 Есть несохранённые изменения";
        if (reset) reset.disabled = false;
    } else {
        state.textContent = "🟢 Без изменений";
        if (reset) reset.disabled = true;
    }
}


function getCurrentViewLink() {
    const url = new URL(window.location.href);

    if (hasUnsavedChanges()) {
        url.searchParams.set("view", "custom");
        url.searchParams.set("widgets", viewEditor.currentWidgets.join(","));
    } else if (viewEditor.currentView) {
        url.searchParams.set("view", viewEditor.currentView);
        url.searchParams.delete("widgets");
    }

    return url.toString();
}

function initViewEditorActions() {
    const copyButton = document.getElementById("copy-view-link");
    const resetButton = document.getElementById("reset-view");

    if (!copyButton) return;

    if (resetButton) {
        resetButton.addEventListener("click", () => {

            viewEditor.currentWidgets = [...viewEditor.originalWidgets];

            document.querySelectorAll("#settings-widgets input").forEach(input => {
                input.checked = viewEditor.originalWidgets.includes(input.dataset.widgetId);
            });

            updateEditorState();
        });
    }

    copyButton.addEventListener("click", async () => {
        const link = getCurrentViewLink();

        if (navigator.clipboard && window.isSecureContext) {
            try {
                await navigator.clipboard.writeText(link);

                copyButton.textContent = "✅ Ссылка скопирована";

                setTimeout(() => {
                    copyButton.textContent = "📋 Копировать ссылку";
                }, 2000);

                return;
            } catch (e) {
            }
        }

        window.prompt("Скопируйте ссылку:", link);

        copyButton.textContent = "📋 Ссылка показана";

        setTimeout(() => {
            copyButton.textContent = "📋 Копировать ссылку";
        }, 2000);
    });
}

initViewEditorActions();
