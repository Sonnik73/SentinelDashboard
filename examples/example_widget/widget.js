async function updateExample() {
    const container = document.getElementById("example-content");
    if (!container) return;

    try {
        const data = await apiGet("/api/example");
        container.innerHTML = `<p>${data.message}</p>`;
    } catch (error) {
        console.error("Example:", error);
    }
}

registerWidget("example", updateExample);
