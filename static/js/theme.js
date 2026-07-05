// The initial theme is already applied by the inline script in
// dashboard.html's <head> (before the stylesheet paints, to avoid a
// flash of the wrong theme) - this just wires up the toggle button and
// keeps its icon in sync.
function applyTheme(theme) {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("theme", theme);

    const button = document.getElementById("theme-toggle");
    if (!button) return;

    button.textContent = theme === "light" ? "🌙" : "☀️";
    button.title = theme === "light" ? "Тёмная тема" : "Светлая тема";
}

function initThemeToggle() {
    const button = document.getElementById("theme-toggle");
    if (!button) return;

    applyTheme(document.documentElement.dataset.theme || "dark");

    button.addEventListener("click", () => {
        const next = document.documentElement.dataset.theme === "light" ? "dark" : "light";
        applyTheme(next);
    });
}
