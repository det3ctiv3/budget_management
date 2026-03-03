export function fmt(value) {
  return Number(value || 0).toFixed(2);
}

export function today() {
  return new Date().toISOString().slice(0, 10);
}

export function log(message, payload) {
  const logEl = document.getElementById("log");
  const row = `[${new Date().toLocaleTimeString()}] ${message}`;
  logEl.textContent = `${row}${payload ? `\n${JSON.stringify(payload, null, 2)}` : ""}\n\n${logEl.textContent}`;
}

export function toast(message, kind = "ok") {
  const region = document.getElementById("toastRegion");
  const node = document.createElement("div");
  node.className = kind === "error" ? "toast error" : "toast";
  node.textContent = message;
  region.prepend(node);
  setTimeout(() => node.remove(), 3000);
}

export function bindSettingsPanel() {
  const panel = document.getElementById("settingsPanel");
  const button = document.getElementById("settingsToggle");
  button.addEventListener("click", () => {
    const isHidden = panel.hasAttribute("hidden");
    if (isHidden) {
      panel.removeAttribute("hidden");
    } else {
      panel.setAttribute("hidden", "");
    }
    button.setAttribute("aria-expanded", String(isHidden));
  });
}
