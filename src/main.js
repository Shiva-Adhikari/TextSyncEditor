window.addEventListener("DOMContentLoaded", () => {
    const websocket = new WebSocket("ws://localhost:6789/");
    const textarea = document.getElementById("textarea_id");

    // Store last sent text to avoid duplicate sends
    let send_text = "";
    let debounceTimer;
    const DEBOUNCE_DELAY = 500; // 500ms delay

    // Add event listener for when WebSocket connection is open
    websocket.addEventListener("open", () => {
      // Add event listener for textarea input changes
      textarea.addEventListener("input", () => {
        const text = textarea.value;

        // Clear any pending timeout
        clearTimeout(debounceTimer);

        // Set a new timeout
        debounceTimer = setTimeout(() => {
          // Only send if text has changed from last sent text
          if (text !== send_text) {
            websocket.send(text);
            send_text = text; // Update the last sent text
          }
        }, DEBOUNCE_DELAY);
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