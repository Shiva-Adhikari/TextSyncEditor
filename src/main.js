window.addEventListener("DOMContentLoaded", () => {
    const websocket = new WebSocket("ws://localhost:8080/ws");
    const textArea = document.getElementById("textarea_id");

    const dmp = new diff_match_patch();

    // Store last sent text to avoid duplicate sends
    let prevText = "";
    let debounceTimer;
    const DEBOUNCE_DELAY = 500; // 500ms delay

    // Add event listener for when WebSocket connection is open
    websocket.addEventListener("open", () => {
      // Add event listener for textarea input changes
      textArea.addEventListener("input", () => {

        // Clear any pending timeout
        clearTimeout(debounceTimer);

        // Set a new timeout
        debounceTimer = setTimeout(() => {
            const currentText = textArea.value;

            if (currentText != prevText) {
                // generate patch from prevText to currentText
                const patches = dmp.patch_make(prevText, currentText);
                const patchText = dmp.patch_toText(patches)
                // window.alert("client le server lai send garxa: " +patchText);

                // send patch
                websocket.send(patchText);
            }
        }, DEBOUNCE_DELAY);
      });
    });


    // if server sends text, update text to textarea
    websocket.addEventListener("message", (event) => {
        const patchText = event.data;
        // window.alert("server bata aako: " +patchText);

        try {
            const patches = dmp.patch_fromText(patchText);
            const [newText, results] = dmp.patch_apply(patches, prevText);

            // only update if all patches applied successfully
            if (results.every(r => r === true)) {
                if (prevText.trim() !== newText.trim()) {
                    prevText = newText;
                    textArea.value = prevText;
                }
                //  else {
                    // window.alert("ALREADY UPTODATE")
                // }
            } else {
                console.error("Some patches failed to apply:", results);
            }
        } catch (e) {
            console.error('Failed to apply patch', e);
        }    
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