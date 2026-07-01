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
        viewEditor.originalLayout = JSON.parse(JSON.stringify(data.layout || []));
        viewEditor.currentLayout = JSON.parse(JSON.stringify(data.layout || []));
        updateEditorState();

        document.getElementById("settings-current-view").textContent =
            `${data.current.title} (${data.current.id})`;

        const viewSelect = document.getElementById("settings-view-select");

        if (viewSelect) {
            viewSelect.innerHTML = "";

            data.available_views.forEach(viewId => {
                const option = document.createElement("option");
                option.value = viewId;
                option.textContent = viewId;
                option.selected = viewId === data.current.id;
                viewSelect.appendChild(option);
            });

            viewSelect.onchange = () => {
                const url = new URL(window.location.href);
                url.searchParams.set("view", viewSelect.value);
                window.location.href = url.toString();
            };
        }

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
                        <option value="3" ${getWidgetSpan(widget.id) === 3 ? "selected" : ""}>1/4</option>
                        <option value="4" ${getWidgetSpan(widget.id) === 4 ? "selected" : ""}>1/3</option>
                        <option value="6" ${getWidgetSpan(widget.id) === 6 ? "selected" : ""}>1/2</option>
                        <option value="12" ${getWidgetSpan(widget.id) === 12 ? "selected" : ""}>Вся ширина</option>
                    </select>
                </label>
            `;
        });
        container.querySelectorAll("input[type='checkbox']").forEach(input => {
            input.addEventListener("change", () => {
                viewEditor.currentLayout = buildLayoutFromSettings(container);
                updateEditorState();
                applyView();
            });
        });
 
        container.querySelectorAll(".widget-span-select").forEach(select => {
            select.addEventListener("change", () => {
                setWidgetSpan(
                    select.dataset.widgetSpan,
                    Number(select.value)
                );
 
                viewEditor.currentLayout = buildLayoutFromSettings(container);
                updateEditorState();
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
    originalLayout: [],
    currentLayout: [],
    currentView: "",
};

function getCurrentWidgets() {
    return viewEditor.currentLayout
        .flat()
        .map(item => item.widget)
        .filter(Boolean);
}

function getOriginalWidgets() {
    return viewEditor.originalLayout
        .flat()
        .map(item => item.widget)
        .filter(Boolean);
}

function arraysEqual(a, b) {
    return JSON.stringify([...a].sort()) === JSON.stringify([...b].sort());
}

function hasUnsavedChanges() {
    return !arraysEqual(
        viewEditor.originalLayout,
        viewEditor.currentLayout
    );
}



function findLayoutItem(widgetId) {
    return viewEditor.currentLayout
        .flat()
        .find(item => item.widget === widgetId);
}

function getWidgetSpan(widgetId) {
    const item = findLayoutItem(widgetId);
    return item ? item.span : 12;
}

function setWidgetSpan(widgetId, span) {
    const item = findLayoutItem(widgetId);
    if (item) {
        item.span = span;
    }
}

function buildLayoutFromSettings(container) {
    const selected = Array.from(
        container.querySelectorAll("input[type='checkbox']:checked")
    ).map(input => input.dataset.widgetId);

    const rows = [];
    let currentRow = [];
    let currentWidth = 0;

    selected.forEach(widgetId => {
        const select = container.querySelector(`[data-widget-span="${widgetId}"]`);
        const span = select ? Number(select.value) : getWidgetSpan(widgetId);

        if (currentWidth + span > 12 && currentRow.length > 0) {
            rows.push(currentRow);
            currentRow = [];
            currentWidth = 0;
        }

        currentRow.push({
            widget: widgetId,
            span: span,
        });

        currentWidth += span;
    });

    if (currentRow.length > 0) {
        rows.push(currentRow);
    }

    return rows;
}

function applyView() {
    const grid = document.querySelector(".grid");
    if (!grid) return;

    const cells = {};

    document.querySelectorAll(".layout-cell").forEach(cell => {
        const card = cell.querySelector("[data-widget]");
        if (card) {
            cells[card.dataset.widget] = cell;
        }
    });

    grid.innerHTML = "";

    viewEditor.currentLayout.forEach(row => {
        const rowElement = document.createElement("div");
        rowElement.className = "layout-row";
        rowElement.dataset.columns = row.length;

        row.forEach(item => {
            const widget = item.widget;
            const span = item.span || 12;
            const cell = cells[widget];

            if (!cell) return;

            cell.classList.remove(
                "span-1",
                "span-2",
                "span-3",
                "span-4",
                "span-6",
                "span-8",
                "span-9",
                "span-12"
            );

            cell.classList.add(`span-${span}`);

            const card = cell.querySelector("[data-widget]");
            if (card) {
                card.classList.remove("hidden-widget");
            }

            rowElement.appendChild(cell);
        });

        grid.appendChild(rowElement);
    });
}

function updateEditorState() {
    const state = document.getElementById("settings-state");
    const reset = document.getElementById("reset-view");

    if (!state) return;

    if (hasUnsavedChanges()) {
        state.textContent = "🟡 Есть несохранённые изменения";
        if (reset) reset.disabled = false;
        const save = document.getElementById("save-view");
        if (save) save.disabled = false;
    } else {
        state.textContent = "🟢 Без изменений";
        if (reset) reset.disabled = true;
        const save = document.getElementById("save-view");
        if (save) save.disabled = true;
    }
}


function getCurrentViewLink() {
    const url = new URL(window.location.href);

    if (hasUnsavedChanges()) {
        url.searchParams.set("view", "custom");
        url.searchParams.set("widgets", getCurrentWidgets().join(","));
    } else if (viewEditor.currentView) {
        url.searchParams.set("view", viewEditor.currentView);
        url.searchParams.delete("widgets");
    }

    return url.toString();
}

function initViewEditorActions() {
    const copyButton = document.getElementById("copy-view-link");
    const resetButton = document.getElementById("reset-view");
    const saveButton = document.getElementById("save-view");

    if (!copyButton) return;

    if (resetButton) {
        resetButton.addEventListener("click", () => {

            viewEditor.currentLayout = JSON.parse(JSON.stringify(viewEditor.originalLayout));

            document.querySelectorAll("#settings-widgets input").forEach(input => {
                input.checked = getOriginalWidgets().includes(input.dataset.widgetId);
            });

            updateEditorState();
            applyView();
        });
    }

    if (saveButton) {
        saveButton.addEventListener("click", async () => {
            saveButton.textContent = "⏳ Сохранение...";

            try {
                const response = await fetch("/api/views/save", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        view: viewEditor.currentView,
                        layout: viewEditor.currentLayout,
                    }),
                });

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }

                const data = await response.json();

                viewEditor.originalLayout = JSON.parse(JSON.stringify(data.layout));
                viewEditor.currentLayout = JSON.parse(JSON.stringify(data.layout));

                updateEditorState();
                applyView();

                saveButton.textContent = "✅ Сохранено";

                setTimeout(() => {
                    saveButton.textContent = "💾 Сохранить";
                }, 2000);
            } catch (error) {
                console.error("Save layout:", error);
                saveButton.textContent = "⚠️ Ошибка сохранения";

                setTimeout(() => {
                    saveButton.textContent = "💾 Сохранить";
                }, 2000);
            }
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
