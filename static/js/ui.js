// ------------------------------
// UI Helpers
// ------------------------------

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

// Every widget card gets a fullscreen toggle for free (the button is
// injected once by templates/dashboard.html's grid loop, not by each
// widget's own template) using the browser's native Fullscreen API - a
// generic mechanism that works the same for a camera feed, a news list,
// or system metrics without any per-widget code.
function initFullscreenToggles() {
    document.querySelectorAll(".widget-fullscreen-toggle").forEach(button => {
        button.addEventListener("click", event => {
            event.stopPropagation();

            const cell = button.closest(".layout-cell");
            if (!cell) return;

            if (document.fullscreenElement === cell) {
                document.exitFullscreen();
            } else if (cell.requestFullscreen) {
                cell.requestFullscreen();
            } else if (cell.webkitRequestFullscreen) {
                cell.webkitRequestFullscreen();
            }
        });
    });

    document.addEventListener("fullscreenchange", () => {
        document.querySelectorAll(".widget-fullscreen-toggle").forEach(button => {
            const cell = button.closest(".layout-cell");
            const isFullscreen = cell && document.fullscreenElement === cell;

            button.textContent = isFullscreen ? "🗗" : "⛶";
            button.title = isFullscreen ? "Свернуть" : "Развернуть на весь экран";
        });
    });
}
