// ------------------------------
// Widget Updaters
// ------------------------------

async function updateSystemMetrics() {
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
    try {
        const data = await apiGet("/api/weather");

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


async function updateRSS() {
    try {
        const data = await apiGet("/api/rss");

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


async function updateBirthdays() {
    try {
        const data = await apiGet("/api/birthdays");

        const container = document.getElementById("birthdays-list");
        if (!container) return;

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
    try {
        const data = await apiGet("/api/network");

        document.getElementById("network-interface").textContent = data.interface;
        document.getElementById("network-ip").textContent = data.ip ?? "---";
        document.getElementById("network-sync").textContent = data.last_sync ?? "---";

        const container = document.getElementById("network-list");
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


// ------------------------------
// Update Scheduler
// ------------------------------

updateSystemMetrics();
updateWeather();
updateRSS();
updateNetwork();
updateBirthdays();

setInterval(updateSystemMetrics, 1000);
setInterval(updateWeather, 600000);
setInterval(updateRSS, 300000);
setInterval(updateNetwork, 30000);
setInterval(updateBirthdays, 3600000);
