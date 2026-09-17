const apiUrlInput = document.getElementById("apiUrl");
const inputText = document.getElementById("inputText");
const scanBtn = document.getElementById("scanBtn");
const statusDiv = document.getElementById("status");
const resultDiv = document.getElementById("result");

// Load saved API URL
chrome.storage.local.get(["apiUrl"], (data) => {
  if (data.apiUrl) apiUrlInput.value = data.apiUrl;
});

apiUrlInput.addEventListener("change", () => {
  chrome.storage.local.set({ apiUrl: apiUrlInput.value });
});

scanBtn.addEventListener("click", async () => {
  const apiUrl = apiUrlInput.value.trim();
  const text = inputText.value.trim();
  resultDiv.textContent = "";
  if (!apiUrl) {
    statusDiv.textContent = "Set API URL first.";
    return;
  }
  if (!text) {
    statusDiv.textContent = "Paste text first.";
    return;
  }

  statusDiv.textContent = "Scanning...";
  try {
    const resp = await fetch(apiUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });

    if (!resp.ok) {
      const errData = await resp.json().catch(() => ({}));
      statusDiv.textContent = "API error " + resp.status + (errData.detail ? ": " + errData.detail : "");
      return;
    }

    const data = await resp.json();
    const label = (data.label || "").toLowerCase();
    const tags = data.tags || [];
    const score = data.score !== null && data.score !== undefined ? " (" + Math.round(data.score * 100) + "%)" : "";
    const tagText = tags.length > 0 ? " [" + tags.join(", ") + "]" : "";

    if (label === "malicious") {
      resultDiv.className = "result malicious";
      resultDiv.textContent = "MALICIOUS" + score + tagText;
    } else {
      resultDiv.className = "result normal";
      resultDiv.textContent = "NORMAL" + score;
    }
    statusDiv.textContent = "";
  } catch (err) {
    console.error(err);
    statusDiv.textContent = "Request failed: " + err.message;
  }
});

