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

// Switches fullscreen straight from one widget's cell to another's
// (direction: 1 = next, -1 = previous), wrapping around at the ends.
// Calling requestFullscreen() on a different element while one is
// already fullscreen just swaps the fullscreen target in modern
// browsers - no need to exit first, which also avoids the "no longer a
// direct user gesture" pitfall of exiting async and re-requesting later.
function swipeToWidget(direction) {
    const grid = document.querySelector(".grid");
    if (!grid) return;

    const cells = Array.from(grid.querySelectorAll(".layout-cell"));
    const currentIndex = cells.indexOf(document.fullscreenElement);
    if (currentIndex === -1) return;

    const nextCell = cells[(currentIndex + direction + cells.length) % cells.length];
    if (!nextCell || nextCell === document.fullscreenElement) return;

    if (nextCell.requestFullscreen) {
        nextCell.requestFullscreen();
    } else if (nextCell.webkitRequestFullscreen) {
        nextCell.webkitRequestFullscreen();
    }
}

// Swipe left/right while a widget is fullscreen to jump to the next/
// previous one - built for Tablet/Wall Mode, where exiting fullscreen
// just to tap another widget's toggle is a lot of friction. Guards
// against vertical scrolling inside a widget's own scrollable content
// (a long news list, say) being misread as a swipe.
function initFullscreenSwipe() {
    const SWIPE_THRESHOLD_PX = 60;
    let touchStart = null;

    document.addEventListener("touchstart", event => {
        if (!document.fullscreenElement) return;
        const touch = event.touches[0];
        touchStart = { x: touch.clientX, y: touch.clientY };
    }, { passive: true });

    document.addEventListener("touchend", event => {
        if (!document.fullscreenElement || !touchStart) return;

        const touch = event.changedTouches[0];
        const deltaX = touch.clientX - touchStart.x;
        const deltaY = touch.clientY - touchStart.y;
        touchStart = null;

        if (Math.abs(deltaX) < SWIPE_THRESHOLD_PX || Math.abs(deltaX) < Math.abs(deltaY)) return;

        swipeToWidget(deltaX < 0 ? 1 : -1);
    });
}
