async function updateSystemMetrics() {
    try {
        const response = await fetch("/api/system");
        const data = await response.json();

        document.getElementById("time").textContent = data.time;
        document.getElementById("cpu").textContent = data.cpu_percent + "%";
        document.getElementById("ram").textContent = data.memory_percent + "%";
        document.getElementById("hostname").textContent = data.hostname;
    } catch (error) {
        console.error("Ошибка обновления метрик:", error);
    }
}

updateSystemMetrics();
setInterval(updateSystemMetrics, 1000);
