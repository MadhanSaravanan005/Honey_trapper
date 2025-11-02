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
    console.log("📩 Sending last message:", lastMsg);

    chrome.runtime.sendMessage(
      { action: "predict", text: lastMsg },
      (response) => {
        if (!response.success) {
          console.error("❌ Backend error:", response.error);
          return;
        }

        const data = response.data;
        console.log("✅ Backend response:", data);

        if (data.label === "malicious") {
          const lastElem = document.querySelectorAll(".message-in");
          if (lastElem.length > 0) {
            const target = lastElem[lastElem.length - 1];
            target.style.border = "2px solid red";

            const tagBox = document.createElement("div");
            tagBox.style.color = "red";
            tagBox.style.fontSize = "12px";
            tagBox.textContent = "⚠️ Malicious: " + (data.tags?.join(", ") || "unknown");
            target.appendChild(tagBox);
          }
        }
      }
    );
  }
}, 5000);
