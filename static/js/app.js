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
        console.error("Ошибка обновления метрик:", error);
    }
}

updateSystemMetrics();
setInterval(updateSystemMetrics, 1000);
