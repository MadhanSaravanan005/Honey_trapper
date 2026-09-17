chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === "predict") {
    chrome.storage.local.get(["apiUrl"], (result) => {
      const targetUrl = result.apiUrl || "http://localhost:8000/predict";

      fetch(targetUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: msg.text || "" })
      })
        .then(async (resp) => {
          const data = await resp.json().catch(() => ({}));
          if (!resp.ok) {
            sendResponse({ success: false, error: data.detail || `Server error (${resp.status})` });
          } else {
            sendResponse({ success: true, data });
          }
        })
        .catch((err) => sendResponse({ success: false, error: err.message }));
    });
    return true; // Keep channel open for async response
  }
});

