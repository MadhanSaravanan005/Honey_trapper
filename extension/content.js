function getLastMessage() {
  const messages = document.querySelectorAll(".message-in .selectable-text span");
  if (messages.length > 0) {
    return messages[messages.length - 1].innerText;
  }
  return null;
}

let lastSeen = "";

setInterval(() => {
  const lastMsg = getLastMessage();
  if (lastMsg && lastMsg !== lastSeen) {
    lastSeen = lastMsg;
    console.log("📩 Sending last message for scan:", lastMsg);

    chrome.runtime.sendMessage(
      { action: "predict", text: lastMsg },
      (response) => {
        if (chrome.runtime.lastError || !response || !response.success) {
          console.error("❌ Scan failed:", chrome.runtime.lastError?.message || response?.error || "No response received");
          return;
        }

        const data = response.data;
        console.log("✅ Backend scan result:", data);

        if (data && data.label === "malicious") {
          const messageElements = document.querySelectorAll(".message-in");
          if (messageElements.length > 0) {
            const target = messageElements[messageElements.length - 1];
            target.style.border = "2px solid red";
            target.style.borderRadius = "6px";

            // Avoid duplicate alert badge
            if (!target.querySelector(".ht-warning-tag")) {
              const tagBox = document.createElement("div");
              tagBox.className = "ht-warning-tag";
              tagBox.style.color = "#d93025";
              tagBox.style.fontSize = "12px";
              tagBox.style.fontWeight = "bold";
              tagBox.style.marginTop = "4px";
              tagBox.textContent = "⚠️ Malicious alert: " + (data.tags && data.tags.length > 0 ? data.tags.join(", ") : "suspicious pattern");
              target.appendChild(tagBox);
            }
          }
        }
      }
    );
  }
}, 5000);

