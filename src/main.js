window.addEventListener("DOMContentLoaded", () => {
    const websocket = new WebSocket("ws://localhost:6789/");
    const textarea = document.getElementById("textarea_id");

    // save text to server file
    websocket.addEventListener("open", () => {
        textarea.addEventListener("input", () => {
            const text = textarea.value;
            websocket.send(text);
        });
    });

    // if server sends text, update text to textarea
    websocket.addEventListener("message", (event) => {
        textarea.value = event.data;
    });

    // check error
    websocket.addEventListener("error", () => {
        console.error("Websocket error", error);
    });

    // check if server closed
    websocket.addEventListener("close", () => {
        console.warn("Websocket closed");
    });

});