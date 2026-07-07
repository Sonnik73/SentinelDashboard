// ------------------------------
// Settings Drawer
// ------------------------------
async function loadSettingsDrawer() {
    try {
        const params = new URLSearchParams(window.location.search);
        const view = params.get("view");
        const url = view ? `/api/views?view=${view}` : "/api/views";

        const data = await apiGet(url);

        viewEditor.currentView = data.current.id;
        viewEditor.currentIsDefault = Boolean(data.current.is_default);
        viewEditor.originalLayout = JSON.parse(JSON.stringify(data.layout || []));
        viewEditor.currentLayout = JSON.parse(JSON.stringify(data.layout || []));
        viewEditor.widgetOrder = getCurrentWidgets();
        updateEditorState();

        document.getElementById("settings-current-view").textContent =
            `${data.current.title} (${data.current.id})`;

        const deleteButton = document.getElementById("delete-view");
        if (deleteButton) {
            deleteButton.disabled = viewEditor.currentIsDefault;
            deleteButton.title = viewEditor.currentIsDefault
                ? "Нельзя удалить view по умолчанию"
                : "";
        }

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

        viewEditor.availableWidgets = data.available_widgets;
        renderWidgetsChecklist();

    } catch (error) {
        console.error("Settings:", error);
    }
}

// Rebuilds the widget checklist from viewEditor.availableWidgets (cached
// from the last loadSettingsDrawer() fetch) and current viewEditor state,
// with no network round-trip - so toggling a lock or a span can re-render
// the checklist to reflect the change without wiping out any other
// unsaved edit the way re-fetching from the server would.
function renderWidgetsChecklist() {
    const container = document.getElementById("settings-widgets");
    if (!container) return;

    const currentWidgets = getCurrentWidgets();
    container.innerHTML = "";

    viewEditor.availableWidgets.forEach(widget => {
        const checked = currentWidgets.includes(widget.id) ? "checked" : "";
        const unavailable = widget.available === false;
        const warning = unavailable
            ? `<span class="settings-widget-warning" title="${widget.error ?? "Модуль не загрузился"}">⚠️</span>`
            : "";
        const locked = getWidgetLocked(widget.id);
        const disabled = locked ? "disabled" : "";

        container.innerHTML += `
            <label class="settings-widget${unavailable ? " settings-widget-unavailable" : ""}">
                <input
                    type="checkbox"
                    data-widget-id="${widget.id}"
                    ${checked}
                >
                <span>${widget.icon} ${widget.title}</span>
                ${warning}
                <select class="widget-span-select" data-widget-span="${widget.id}" ${disabled}>
                    <option value="3" ${getWidgetSpan(widget.id) === 3 ? "selected" : ""}>1/4</option>
                    <option value="4" ${getWidgetSpan(widget.id) === 4 ? "selected" : ""}>1/3</option>
                    <option value="6" ${getWidgetSpan(widget.id) === 6 ? "selected" : ""}>1/2</option>
                    <option value="12" ${getWidgetSpan(widget.id) === 12 ? "selected" : ""}>Вся ширина</option>
                </select>
                <select class="widget-height-select" data-widget-height="${widget.id}" ${disabled}>
                    <option value="0" ${getWidgetHeight(widget.id) === 0 ? "selected" : ""}>Авто</option>
                    <option value="220" ${getWidgetHeight(widget.id) === 220 ? "selected" : ""}>Компактно</option>
                    <option value="360" ${getWidgetHeight(widget.id) === 360 ? "selected" : ""}>Средне</option>
                    <option value="600" ${getWidgetHeight(widget.id) === 600 ? "selected" : ""}>Высоко</option>
                </select>
                <button
                    type="button"
                    class="widget-lock-toggle"
                    data-widget-lock="${widget.id}"
                    title="${locked ? "Разблокировать (можно перетаскивать и менять размер)" : "Заблокировать (нельзя перетащить или изменить размер)"}"
                >${locked ? "🔒" : "🔓"}</button>
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

    container.querySelectorAll(".widget-lock-toggle").forEach(button => {
        button.addEventListener("click", () => {
            const widgetId = button.dataset.widgetLock;
            setWidgetLocked(widgetId, !getWidgetLocked(widgetId));

            viewEditor.currentLayout = buildLayoutFromSettings(container);
            updateEditorState();
            applyView();
            renderWidgetsChecklist();
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

    container.querySelectorAll(".widget-height-select").forEach(select => {
        select.addEventListener("change", () => {
            setWidgetHeight(
                select.dataset.widgetHeight,
                Number(select.value)
            );

            viewEditor.currentLayout = buildLayoutFromSettings(container);
            updateEditorState();
            applyView();
        });
    });
}


// ------------------------------
// Cameras Config
// ------------------------------

async function loadCamerasConfig() {
    const container = document.getElementById("cameras-config-list");
    if (!container) return;

    try {
        const data = await apiGet("/api/cameras/config");
        container.innerHTML = "";

        if (!data.cameras || data.cameras.length === 0) {
            container.innerHTML = `<p class="small">Камеры не настроены</p>`;
            return;
        }

        data.cameras.forEach(camera => {
            const resolution = camera.resolution ?? "";
            const quality = camera.quality ?? 5;
            const fps = camera.fps ?? 2;

            const item = document.createElement("div");
            item.className = "camera-config-item";
            item.dataset.cameraId = camera.id;
            item.innerHTML = `
                <input type="text" class="settings-view-select camera-config-name" value="${camera.name}" placeholder="Название">
                <input type="text" class="settings-view-select camera-config-ip" value="${camera.ip}" placeholder="IP-адрес">
                <input type="text" class="settings-view-select camera-config-port" value="${camera.port ?? 554}" placeholder="Порт">
                <input type="text" class="settings-view-select camera-config-path" value="${camera.path ?? "/1/1"}" placeholder="Путь">
                <select class="settings-view-select camera-config-resolution">
                    <option value="" ${resolution === "" ? "selected" : ""}>Разрешение: оригинал</option>
                    <option value="1280x720" ${resolution === "1280x720" ? "selected" : ""}>Разрешение: 1280x720</option>
                    <option value="854x480" ${resolution === "854x480" ? "selected" : ""}>Разрешение: 854x480</option>
                    <option value="640x360" ${resolution === "640x360" ? "selected" : ""}>Разрешение: 640x360</option>
                </select>
                <select class="settings-view-select camera-config-quality">
                    <option value="2" ${quality === 2 ? "selected" : ""}>Качество: высокое</option>
                    <option value="5" ${quality === 5 ? "selected" : ""}>Качество: среднее</option>
                    <option value="10" ${quality === 10 ? "selected" : ""}>Качество: низкое</option>
                    <option value="20" ${quality === 20 ? "selected" : ""}>Качество: минимальное</option>
                </select>
                <input type="number" class="settings-view-select camera-config-fps" value="${fps}" min="1" max="10" placeholder="Кадров/сек">
                <div class="settings-view-manage-row">
                    <button class="settings-action-button camera-config-save">💾 Сохранить</button>
                    <button class="settings-action-button camera-config-delete">🗑 Удалить</button>
                </div>
            `;
            container.appendChild(item);
        });

        container.querySelectorAll(".camera-config-save").forEach(button => {
            button.addEventListener("click", async () => {
                const item = button.closest(".camera-config-item");

                try {
                    await postJson("/api/cameras/config/update", {
                        id: item.dataset.cameraId,
                        name: item.querySelector(".camera-config-name").value,
                        ip: item.querySelector(".camera-config-ip").value,
                        port: item.querySelector(".camera-config-port").value,
                        path: item.querySelector(".camera-config-path").value,
                        resolution: item.querySelector(".camera-config-resolution").value,
                        quality: item.querySelector(".camera-config-quality").value,
                        fps: item.querySelector(".camera-config-fps").value,
                    });

                    button.textContent = "✅ Сохранено";
                    setTimeout(() => { button.textContent = "💾 Сохранить"; }, 1500);

                    loadSettingsDrawer();
                } catch (error) {
                    window.alert(`Не удалось сохранить камеру: ${error.message}`);
                }
            });
        });

        container.querySelectorAll(".camera-config-delete").forEach(button => {
            button.addEventListener("click", async () => {
                const item = button.closest(".camera-config-item");
                const cameraId = item.dataset.cameraId;

                const confirmed = window.confirm(`Удалить камеру "${cameraId}"?`);
                if (!confirmed) return;

                try {
                    await postJson("/api/cameras/config/delete", { id: cameraId });
                    loadCamerasConfig();
                    loadSettingsDrawer();
                } catch (error) {
                    window.alert(`Не удалось удалить камеру: ${error.message}`);
                }
            });
        });

    } catch (error) {
        console.error("Cameras config:", error);
    }
}

function initCameraConfigActions() {
    const addButton = document.getElementById("add-camera-config");
    const state = document.getElementById("camera-config-state");

    if (!addButton || !state) return;

    addButton.addEventListener("click", async () => {
        const idInput = document.getElementById("camera-config-id");
        const nameInput = document.getElementById("camera-config-name");
        const ipInput = document.getElementById("camera-config-ip");
        const portInput = document.getElementById("camera-config-port");
        const pathInput = document.getElementById("camera-config-path");
        const resolutionInput = document.getElementById("camera-config-resolution");
        const qualityInput = document.getElementById("camera-config-quality");
        const fpsInput = document.getElementById("camera-config-fps");

        const id = idInput.value.trim();
        const name = nameInput.value.trim();
        const ip = ipInput.value.trim();

        if (!id || !name || !ip) {
            state.textContent = "⚠️ Заполните id, название и IP";
            return;
        }

        addButton.disabled = true;
        state.textContent = "⏳ Добавление...";

        try {
            await postJson("/api/cameras/config/add", {
                id,
                name,
                ip,
                port: portInput.value.trim(),
                path: pathInput.value.trim(),
                resolution: resolutionInput.value,
                quality: qualityInput.value,
                fps: fpsInput.value.trim(),
            });

            [idInput, nameInput, ipInput, portInput, pathInput].forEach(input => {
                input.value = "";
            });

            state.textContent = "✅ Камера добавлена";

            loadCamerasConfig();
            loadSettingsDrawer();
        } catch (error) {
            state.textContent = `⚠️ ${error.message}`;
        } finally {
            addButton.disabled = false;
        }
    });
}


// ------------------------------
// RSS Sources Config
// ------------------------------

async function loadRssConfig() {
    const container = document.getElementById("rss-config-list");
    if (!container) return;

    try {
        const data = await apiGet("/api/rss/config");
        container.innerHTML = "";

        if (!data.feeds || data.feeds.length === 0) {
            container.innerHTML = `<p class="small">Источники не настроены</p>`;
            return;
        }

        data.feeds.forEach(feed => {
            const item = document.createElement("div");
            item.className = "rss-config-item";
            item.dataset.feedName = feed.name;
            item.innerHTML = `
                <input type="text" class="settings-view-select rss-config-name" value="${feed.name}" placeholder="Название">
                <input type="text" class="settings-view-select rss-config-url" value="${feed.url}" placeholder="URL RSS-фида">
                <div class="settings-view-manage-row">
                    <button class="settings-action-button rss-config-save">💾 Сохранить</button>
                    <button class="settings-action-button rss-config-delete">🗑 Удалить</button>
                </div>
            `;
            container.appendChild(item);
        });

        container.querySelectorAll(".rss-config-save").forEach(button => {
            button.addEventListener("click", async () => {
                const item = button.closest(".rss-config-item");

                try {
                    await postJson("/api/rss/config/update", {
                        name: item.dataset.feedName,
                        new_name: item.querySelector(".rss-config-name").value,
                        new_url: item.querySelector(".rss-config-url").value,
                    });

                    button.textContent = "✅ Сохранено";
                    setTimeout(() => { button.textContent = "💾 Сохранить"; }, 1500);

                    loadRssConfig();
                } catch (error) {
                    window.alert(`Не удалось сохранить источник: ${error.message}`);
                }
            });
        });

        container.querySelectorAll(".rss-config-delete").forEach(button => {
            button.addEventListener("click", async () => {
                const item = button.closest(".rss-config-item");
                const feedName = item.dataset.feedName;

                const confirmed = window.confirm(`Удалить источник "${feedName}"?`);
                if (!confirmed) return;

                try {
                    await postJson("/api/rss/config/delete", { name: feedName });
                    loadRssConfig();
                } catch (error) {
                    window.alert(`Не удалось удалить источник: ${error.message}`);
                }
            });
        });

    } catch (error) {
        console.error("RSS config:", error);
    }
}

function initRssConfigActions() {
    const addButton = document.getElementById("add-rss-config");
    const state = document.getElementById("rss-config-state");

    if (!addButton || !state) return;

    addButton.addEventListener("click", async () => {
        const nameInput = document.getElementById("rss-config-name");
        const urlInput = document.getElementById("rss-config-url");

        const name = nameInput.value.trim();
        const url = urlInput.value.trim();

        if (!name || !url) {
            state.textContent = "⚠️ Заполните название и URL";
            return;
        }

        addButton.disabled = true;
        state.textContent = "⏳ Добавление...";

        try {
            await postJson("/api/rss/config/add", { name, url });

            nameInput.value = "";
            urlInput.value = "";

            state.textContent = "✅ Источник добавлен";

            loadRssConfig();
        } catch (error) {
            state.textContent = `⚠️ ${error.message}`;
        } finally {
            addButton.disabled = false;
        }
    });
}


// ------------------------------
// Weather Cities Config
// ------------------------------

async function loadWeatherConfig() {
    const container = document.getElementById("weather-config-list");
    if (!container) return;

    try {
        const data = await apiGet("/api/weather/config");
        container.innerHTML = "";

        if (!data.cities || data.cities.length === 0) {
            container.innerHTML = `<p class="small">Города не настроены</p>`;
            return;
        }

        data.cities.forEach(city => {
            const item = document.createElement("div");
            item.className = "weather-config-item";
            item.dataset.cityName = city.name;
            item.innerHTML = `
                <input type="text" class="settings-view-select weather-config-name" value="${city.name}" placeholder="Название">
                <input type="text" class="settings-view-select weather-config-url" value="${city.url}" placeholder="URL страницы rp5.ru">
                <div class="settings-view-manage-row">
                    <button class="settings-action-button weather-config-save">💾 Сохранить</button>
                    <button class="settings-action-button weather-config-delete">🗑 Удалить</button>
                </div>
            `;
            container.appendChild(item);
        });

        container.querySelectorAll(".weather-config-save").forEach(button => {
            button.addEventListener("click", async () => {
                const item = button.closest(".weather-config-item");

                try {
                    await postJson("/api/weather/config/update", {
                        name: item.dataset.cityName,
                        new_name: item.querySelector(".weather-config-name").value,
                        new_url: item.querySelector(".weather-config-url").value,
                    });

                    button.textContent = "✅ Сохранено";
                    setTimeout(() => { button.textContent = "💾 Сохранить"; }, 1500);

                    loadWeatherConfig();
                } catch (error) {
                    window.alert(`Не удалось сохранить город: ${error.message}`);
                }
            });
        });

        container.querySelectorAll(".weather-config-delete").forEach(button => {
            button.addEventListener("click", async () => {
                const item = button.closest(".weather-config-item");
                const cityName = item.dataset.cityName;

                const confirmed = window.confirm(`Удалить город "${cityName}"?`);
                if (!confirmed) return;

                try {
                    await postJson("/api/weather/config/delete", { name: cityName });
                    loadWeatherConfig();
                } catch (error) {
                    window.alert(`Не удалось удалить город: ${error.message}`);
                }
            });
        });

    } catch (error) {
        console.error("Weather config:", error);
    }
}

function initWeatherConfigActions() {
    const addButton = document.getElementById("add-weather-config");
    const state = document.getElementById("weather-config-state");

    if (!addButton || !state) return;

    addButton.addEventListener("click", async () => {
        const nameInput = document.getElementById("weather-config-name");
        const urlInput = document.getElementById("weather-config-url");

        const name = nameInput.value.trim();
        const url = urlInput.value.trim();

        if (!name || !url) {
            state.textContent = "⚠️ Заполните название и URL";
            return;
        }

        addButton.disabled = true;
        state.textContent = "⏳ Добавление...";

        try {
            await postJson("/api/weather/config/add", { name, url });

            nameInput.value = "";
            urlInput.value = "";

            state.textContent = "✅ Город добавлен";

            loadWeatherConfig();
        } catch (error) {
            state.textContent = `⚠️ ${error.message}`;
        } finally {
            addButton.disabled = false;
        }
    });
}


// ------------------------------
// Network Hosts Config
// ------------------------------

async function loadNetworkConfig() {
    const container = document.getElementById("network-config-list");
    if (!container) return;

    try {
        const data = await apiGet("/api/network/config");
        container.innerHTML = "";

        if (!data.hosts || data.hosts.length === 0) {
            container.innerHTML = `<p class="small">Хосты не настроены</p>`;
            return;
        }

        data.hosts.forEach(host => {
            const item = document.createElement("div");
            item.className = "weather-config-item";
            item.dataset.hostName = host.name;
            item.innerHTML = `
                <input type="text" class="settings-view-select network-config-name" value="${host.name}" placeholder="Название">
                <input type="text" class="settings-view-select network-config-address" value="${host.address}" placeholder="IP-адрес или домен">
                <div class="settings-view-manage-row">
                    <button class="settings-action-button network-config-save">💾 Сохранить</button>
                    <button class="settings-action-button network-config-delete">🗑 Удалить</button>
                </div>
            `;
            container.appendChild(item);
        });

        container.querySelectorAll(".network-config-save").forEach(button => {
            button.addEventListener("click", async () => {
                const item = button.closest(".weather-config-item");

                try {
                    await postJson("/api/network/config/update", {
                        name: item.dataset.hostName,
                        new_name: item.querySelector(".network-config-name").value,
                        new_address: item.querySelector(".network-config-address").value,
                    });

                    button.textContent = "✅ Сохранено";
                    setTimeout(() => { button.textContent = "💾 Сохранить"; }, 1500);

                    loadNetworkConfig();
                } catch (error) {
                    window.alert(`Не удалось сохранить хост: ${error.message}`);
                }
            });
        });

        container.querySelectorAll(".network-config-delete").forEach(button => {
            button.addEventListener("click", async () => {
                const item = button.closest(".weather-config-item");
                const hostName = item.dataset.hostName;

                const confirmed = window.confirm(`Удалить хост "${hostName}"?`);
                if (!confirmed) return;

                try {
                    await postJson("/api/network/config/delete", { name: hostName });
                    loadNetworkConfig();
                } catch (error) {
                    window.alert(`Не удалось удалить хост: ${error.message}`);
                }
            });
        });

    } catch (error) {
        console.error("Network config:", error);
    }
}

function initNetworkConfigActions() {
    const addButton = document.getElementById("add-network-config");
    const state = document.getElementById("network-config-state");

    if (!addButton || !state) return;

    addButton.addEventListener("click", async () => {
        const nameInput = document.getElementById("network-config-name");
        const addressInput = document.getElementById("network-config-address");

        const name = nameInput.value.trim();
        const address = addressInput.value.trim();

        if (!name || !address) {
            state.textContent = "⚠️ Заполните название и адрес";
            return;
        }

        addButton.disabled = true;
        state.textContent = "⏳ Добавление...";

        try {
            await postJson("/api/network/config/add", { name, address });

            nameInput.value = "";
            addressInput.value = "";

            state.textContent = "✅ Хост добавлен";

            loadNetworkConfig();
        } catch (error) {
            state.textContent = `⚠️ ${error.message}`;
        } finally {
            addButton.disabled = false;
        }
    });
}


// ------------------------------
// Birthdays Config
// ------------------------------

async function loadBirthdaysConfig() {
    const container = document.getElementById("birthdays-config-list");
    if (!container) return;

    try {
        const data = await apiGet("/api/birthdays/config");
        container.innerHTML = "";

        if (!data.items || data.items.length === 0) {
            container.innerHTML = `<p class="small">Дни рождения не настроены</p>`;
            return;
        }

        data.items.forEach(item => {
            const el = document.createElement("div");
            el.className = "weather-config-item";
            el.dataset.itemName = item.name;
            el.innerHTML = `
                <input type="text" class="settings-view-select birthdays-config-name" value="${item.name}" placeholder="Имя">
                <input type="text" class="settings-view-select birthdays-config-date" value="${item.date}" placeholder="MM-DD">
                <input type="text" class="settings-view-select birthdays-config-note" value="${item.note || ""}" placeholder="Заметка (необязательно)">
                <div class="settings-view-manage-row">
                    <button class="settings-action-button birthdays-config-save">💾 Сохранить</button>
                    <button class="settings-action-button birthdays-config-delete">🗑 Удалить</button>
                </div>
            `;
            container.appendChild(el);
        });

        container.querySelectorAll(".birthdays-config-save").forEach(button => {
            button.addEventListener("click", async () => {
                const item = button.closest(".weather-config-item");

                try {
                    await postJson("/api/birthdays/config/update", {
                        name: item.dataset.itemName,
                        new_name: item.querySelector(".birthdays-config-name").value,
                        new_date: item.querySelector(".birthdays-config-date").value,
                        new_note: item.querySelector(".birthdays-config-note").value,
                    });

                    button.textContent = "✅ Сохранено";
                    setTimeout(() => { button.textContent = "💾 Сохранить"; }, 1500);

                    loadBirthdaysConfig();
                } catch (error) {
                    window.alert(`Не удалось сохранить запись: ${error.message}`);
                }
            });
        });

        container.querySelectorAll(".birthdays-config-delete").forEach(button => {
            button.addEventListener("click", async () => {
                const item = button.closest(".weather-config-item");
                const itemName = item.dataset.itemName;

                const confirmed = window.confirm(`Удалить запись "${itemName}"?`);
                if (!confirmed) return;

                try {
                    await postJson("/api/birthdays/config/delete", { name: itemName });
                    loadBirthdaysConfig();
                } catch (error) {
                    window.alert(`Не удалось удалить запись: ${error.message}`);
                }
            });
        });

    } catch (error) {
        console.error("Birthdays config:", error);
    }
}

function initBirthdaysConfigActions() {
    const addButton = document.getElementById("add-birthdays-config");
    const state = document.getElementById("birthdays-config-state");

    if (!addButton || !state) return;

    addButton.addEventListener("click", async () => {
        const nameInput = document.getElementById("birthdays-config-name");
        const dateInput = document.getElementById("birthdays-config-date");
        const noteInput = document.getElementById("birthdays-config-note");

        const name = nameInput.value.trim();
        const dateValue = dateInput.value.trim();
        const note = noteInput.value.trim();

        if (!name || !dateValue) {
            state.textContent = "⚠️ Заполните имя и дату (MM-DD)";
            return;
        }

        addButton.disabled = true;
        state.textContent = "⏳ Добавление...";

        try {
            await postJson("/api/birthdays/config/add", { name, date: dateValue, note });

            nameInput.value = "";
            dateInput.value = "";
            noteInput.value = "";

            state.textContent = "✅ Запись добавлена";

            loadBirthdaysConfig();
        } catch (error) {
            state.textContent = `⚠️ ${error.message}`;
        } finally {
            addButton.disabled = false;
        }
    });
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
        loadCamerasConfig();
        loadRssConfig();
        loadWeatherConfig();
        loadNetworkConfig();
        loadBirthdaysConfig();
        setLayoutCellsDraggable(true);
    }

    function closeDrawer() {
        drawer.classList.remove("open");
        overlay.classList.remove("open");
        setLayoutCellsDraggable(false);
    }

    button.addEventListener("click", openDrawer);
    close.addEventListener("click", closeDrawer);
}


function initCreateViewAction() {
    const button = document.getElementById("create-view");
    const input = document.getElementById("new-view-name");
    const state = document.getElementById("create-view-state");

    if (!button || !input || !state) return;

    button.addEventListener("click", async () => {
        const name = input.value.trim();

        if (!name) {
            state.textContent = "⚠️ Введите название";
            return;
        }

        button.disabled = true;
        state.textContent = "⏳ Создание...";

        try {
            const response = await fetch("/api/views/create", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ name }),
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            const data = await response.json();

            const url = new URL(window.location.href);
            url.searchParams.set("view", data.view);
            window.location.href = url.toString();

        } catch (error) {
            console.error("Create view:", error);
            state.textContent = `⚠️ ${error.message}`;
            button.disabled = false;
        }
    });
}


async function postJson(url, body) {
    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
}


function initViewManagementActions() {
    const duplicateButton = document.getElementById("duplicate-view");
    const renameButton = document.getElementById("rename-view");
    const deleteButton = document.getElementById("delete-view");

    if (!duplicateButton && !renameButton && !deleteButton) return;

    if (duplicateButton) {
        duplicateButton.addEventListener("click", async () => {
            const name = window.prompt("Название нового view (латиница, цифры, дефис):");
            if (!name) return;

            try {
                const data = await postJson("/api/views/duplicate", {
                    source: viewEditor.currentView,
                    name,
                });

                const url = new URL(window.location.href);
                url.searchParams.set("view", data.view);
                window.location.href = url.toString();
            } catch (error) {
                console.error("Duplicate view:", error);
                window.alert(`Не удалось дублировать view: ${error.message}`);
            }
        });
    }

    if (renameButton) {
        renameButton.addEventListener("click", async () => {
            const title = window.prompt("Новое название view:");
            if (!title) return;

            try {
                await postJson("/api/views/rename", {
                    view: viewEditor.currentView,
                    title,
                });

                window.location.reload();
            } catch (error) {
                console.error("Rename view:", error);
                window.alert(`Не удалось переименовать view: ${error.message}`);
            }
        });
    }

    if (deleteButton) {
        deleteButton.addEventListener("click", async () => {
            if (viewEditor.currentIsDefault) return;

            const confirmed = window.confirm(
                `Удалить view "${viewEditor.currentView}"? Это действие необратимо.`
            );
            if (!confirmed) return;

            try {
                await postJson("/api/views/delete", { view: viewEditor.currentView });

                const url = new URL(window.location.href);
                url.searchParams.delete("view");
                window.location.href = url.toString();
            } catch (error) {
                console.error("Delete view:", error);
                window.alert(`Не удалось удалить view: ${error.message}`);
            }
        });
    }
}


function initImportExportActions() {
    const exportButton = document.getElementById("export-view");
    const importButton = document.getElementById("import-view");
    const importFile = document.getElementById("import-view-file");
    const importState = document.getElementById("import-view-state");

    if (!exportButton && !importButton) return;

    if (exportButton) {
        exportButton.addEventListener("click", () => {
            const url = `/api/views/export?view=${encodeURIComponent(viewEditor.currentView)}`;
            window.location.href = url;
        });
    }

    if (importButton) {
        importButton.addEventListener("click", async () => {
            const file = importFile.files[0];

            if (!file) {
                importState.textContent = "⚠️ Выберите файл";
                return;
            }

            let viewData;

            try {
                viewData = JSON.parse(await file.text());
            } catch (error) {
                importState.textContent = "⚠️ Файл не является корректным JSON";
                return;
            }

            const defaultName = file.name.replace(/\.json$/i, "");
            const name = window.prompt("Название для импортированного view:", defaultName);
            if (!name) return;

            importState.textContent = "⏳ Импорт...";

            try {
                const data = await postJson("/api/views/import", { name, view: viewData });

                const url = new URL(window.location.href);
                url.searchParams.set("view", data.view);
                window.location.href = url.toString();
            } catch (error) {
                console.error("Import view:", error);
                importState.textContent = `⚠️ ${error.message}`;
            }
        });
    }
}


// ------------------------------
// View Editor State
// ------------------------------

const viewEditor = {
    originalLayout: [],
    currentLayout: [],
    currentView: "",
    currentIsDefault: false,
    widgetOrder: [],
    availableWidgets: [],
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

// height is optional - absent/0 means "auto" (the card grows to fit its
// content, the pre-existing default behavior), matching the "Авто" option
// in the height dropdown rather than forcing every widget to a fixed size.
function getWidgetHeight(widgetId) {
    const item = findLayoutItem(widgetId);
    return item && item.height ? item.height : 0;
}

function setWidgetHeight(widgetId, height) {
    const item = findLayoutItem(widgetId);
    if (item) {
        if (height) {
            item.height = height;
        } else {
            delete item.height;
        }
    }
}

// A locked widget can't be picked up by drag & drop, and its span/height
// no longer change from the checklist - meant for a widget whose position
// and size you've settled on and don't want to nudge by accident.
function getWidgetLocked(widgetId) {
    const item = findLayoutItem(widgetId);
    return Boolean(item && item.locked);
}

function setWidgetLocked(widgetId, locked) {
    const item = findLayoutItem(widgetId);
    if (item) {
        if (locked) {
            item.locked = true;
        } else {
            delete item.locked;
        }
    }
}

function buildLayoutFromSettings(container) {
    const checkedIds = new Set(
        Array.from(container.querySelectorAll("input[type='checkbox']:checked"))
            .map(input => input.dataset.widgetId)
    );

    // widgetOrder is the source of truth for widget order (drag & drop
    // changes it directly) - keep it in sync with which boxes are
    // checked without disturbing the order of widgets that stay checked
    viewEditor.widgetOrder = viewEditor.widgetOrder.filter(id => checkedIds.has(id));

    checkedIds.forEach(id => {
        if (!viewEditor.widgetOrder.includes(id)) {
            viewEditor.widgetOrder.push(id);
        }
    });

    const rows = [];
    let currentRow = [];
    let currentWidth = 0;

    viewEditor.widgetOrder.forEach(widgetId => {
        const spanSelect = container.querySelector(`[data-widget-span="${widgetId}"]`);
        const span = spanSelect ? Number(spanSelect.value) : getWidgetSpan(widgetId);

        const heightSelect = container.querySelector(`[data-widget-height="${widgetId}"]`);
        const height = heightSelect ? Number(heightSelect.value) : getWidgetHeight(widgetId);

        if (currentWidth + span > 12 && currentRow.length > 0) {
            rows.push(currentRow);
            currentRow = [];
            currentWidth = 0;
        }

        const item = { widget: widgetId, span: span };
        if (height) {
            item.height = height;
        }
        if (getWidgetLocked(widgetId)) {
            item.locked = true;
        }
        currentRow.push(item);

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

            if (item.height) {
                cell.classList.add("fixed-height");
                cell.style.height = `${item.height}px`;
            } else {
                cell.classList.remove("fixed-height");
                cell.style.height = "";
            }

            // applyView() only ever runs while the Settings drawer (and
            // therefore drag & drop) is open, so it's safe to set
            // draggable unconditionally here rather than only clearing it
            // for locked widgets - otherwise unlocking one wouldn't make
            // it draggable again until the drawer was closed and reopened.
            if (item.locked) {
                cell.dataset.locked = "true";
            } else {
                delete cell.dataset.locked;
            }
            cell.draggable = !item.locked;
            cell.classList.toggle("draggable", !item.locked);

            const card = cell.querySelector("[data-widget]");
            if (card) {
                card.classList.remove("hidden-widget");
            }

            rowElement.appendChild(cell);
        });

        grid.appendChild(rowElement);
    });
}

// ------------------------------
// Drag & Drop reordering
// ------------------------------

function setLayoutCellsDraggable(enabled) {
    document.querySelectorAll(".layout-cell").forEach(cell => {
        const draggable = enabled && cell.dataset.locked !== "true";
        cell.draggable = draggable;
        cell.classList.toggle("draggable", draggable);
    });
}

function reorderWidget(draggedId, targetId) {
    const order = viewEditor.widgetOrder;
    const fromIndex = order.indexOf(draggedId);
    const toIndex = order.indexOf(targetId);

    if (fromIndex === -1 || toIndex === -1 || fromIndex === toIndex) return;

    order.splice(fromIndex, 1);
    order.splice(order.indexOf(targetId), 0, draggedId);

    const container = document.getElementById("settings-widgets");
    if (container) {
        viewEditor.currentLayout = buildLayoutFromSettings(container);
    }

    updateEditorState();
    applyView();
}

// Touch state shared across all cells' touch listeners below - HTML5
// native drag & drop (dragstart/dragover/drop) never fires on touch
// devices at all, so tablets need a separate touchstart/touchmove/touchend
// implementation reaching the same reorderWidget() outcome. Touch events
// keep firing on the element where the touch started, unlike mouse
// dragover which fires on whatever's under the pointer - elementFromPoint()
// is what finds the actual cell under the finger as it moves.
let touchDraggedCell = null;
let touchDraggedId = null;
let touchTargetCell = null;

function findCellAtPoint(x, y) {
    const el = document.elementFromPoint(x, y);
    return el ? el.closest(".layout-cell") : null;
}

function initDragAndDrop() {
    document.querySelectorAll(".layout-cell").forEach(cell => {
        const card = cell.querySelector("[data-widget]");
        if (!card) return;

        cell.addEventListener("dragstart", event => {
            event.dataTransfer.setData("text/plain", card.dataset.widget);
            event.dataTransfer.effectAllowed = "move";
            cell.classList.add("dragging");
        });

        cell.addEventListener("dragend", () => {
            cell.classList.remove("dragging");
        });

        cell.addEventListener("dragover", event => {
            if (!cell.draggable) return;
            event.preventDefault();
            event.dataTransfer.dropEffect = "move";
        });

        cell.addEventListener("drop", event => {
            if (!cell.draggable) return;
            event.preventDefault();

            const draggedId = event.dataTransfer.getData("text/plain");
            reorderWidget(draggedId, card.dataset.widget);
        });

        cell.addEventListener("touchstart", () => {
            if (!cell.draggable) return;
            touchDraggedCell = cell;
            touchDraggedId = card.dataset.widget;
            cell.classList.add("dragging");
        }, { passive: true });

        cell.addEventListener("touchmove", event => {
            if (!touchDraggedCell) return;
            event.preventDefault();

            const touch = event.touches[0];
            const target = findCellAtPoint(touch.clientX, touch.clientY);

            if (touchTargetCell && touchTargetCell !== target) {
                touchTargetCell.classList.remove("drag-over");
            }
            if (target && target !== touchDraggedCell && target.draggable) {
                target.classList.add("drag-over");
            }
            touchTargetCell = target;
        }, { passive: false });

        cell.addEventListener("touchend", () => {
            if (!touchDraggedCell) return;

            if (touchTargetCell) {
                touchTargetCell.classList.remove("drag-over");

                const targetCard = touchTargetCell.querySelector("[data-widget]");
                if (targetCard && touchTargetCell !== touchDraggedCell && touchTargetCell.draggable) {
                    reorderWidget(touchDraggedId, targetCard.dataset.widget);
                }
            }

            touchDraggedCell.classList.remove("dragging");
            touchDraggedCell = null;
            touchDraggedId = null;
            touchTargetCell = null;
        });
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
    const copyButton = document.getElementById("generate-view-link");
    const resetButton = document.getElementById("reset-view");
    const saveButton = document.getElementById("save-view");

    if (!copyButton && !resetButton && !saveButton) return;

    if (resetButton) {
        resetButton.addEventListener("click", () => {

            viewEditor.currentLayout = JSON.parse(JSON.stringify(viewEditor.originalLayout));
            viewEditor.widgetOrder = getOriginalWidgets();

            renderWidgetsChecklist();
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

                saveButton.textContent = "✅  Сохранено";

                setTimeout(() => {
                    window.location.reload();
                }, 800);
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
