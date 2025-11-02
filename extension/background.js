chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === "predict") {
    fetch("http://localhost:8000/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: msg.text })
    })
      .then((resp) => resp.json())
      .then((data) => sendResponse({ success: true, data }))
      .catch((err) => sendResponse({ success: false, error: err.message }));
    return true; // keep channel open for async response
  }
});
