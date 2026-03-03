let baseUrl = "http://127.0.0.1:8000";

function normalizeBase(url) {
  const trimmed = (url || "").trim();
  if (!trimmed || trimmed === "/" || trimmed === ".") {
    return "";
  }
  return trimmed.replace(/\/$/, "");
}

export function setApiBase(url) {
  baseUrl = normalizeBase(url);
}

export function getApiBase() {
  return baseUrl;
}

export async function request(path, options = {}) {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const response = await fetch(`${baseUrl}${normalizedPath}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `HTTP ${response.status}`);
  }

  return response.json();
}
