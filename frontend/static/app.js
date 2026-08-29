/**
 * app.js ù DevHub shared frontend utilities
 * Provides: apiFetch, toast notifications, active nav link highlighting.
 */

const API_BASE = "";   // same-origin ù FastAPI serves everything on :8000

/**
 * apiFetch ù thin wrapper around fetch() that:
 *   - Prepends API_BASE to path
 *   - Sets JSON Content-Type on POST/PATCH/PUT
 *   - Throws on non-2xx responses (includes parsed error detail)
 *
 * @param {string} path    - e.g. "/api/teams/members"
 * @param {RequestInit} [options]
 * @returns {Promise<any>} - parsed JSON response body (or null for 204)
 */
async function apiFetch(path, options = {}) {
  const url = API_BASE + path;
  const headers = { ...(options.headers || {}) };

  if (options.body && typeof options.body === "object" && !(options.body instanceof FormData)) {
    options.body = JSON.stringify(options.body);
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(url, { ...options, headers });

  if (res.status === 204) return null;

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    const msg = data?.detail || data?.message || `HTTP ${res.status}`;
    throw new Error(msg);
  }

  return data;
}

// -- Toast notifications ---------------------------------------------------

let _toastContainer = null;

function _getContainer() {
  if (!_toastContainer) {
    _toastContainer = document.createElement("div");
    _toastContainer.id = "toast-container";
    document.body.appendChild(_toastContainer);
  }
  return _toastContainer;
}

/**
 * toast ù show a brief notification.
 * @param {string} message
 * @param {"success"|"error"|"info"} [type="info"]
 * @param {number} [duration=3000]
 */
function toast(message, type = "info", duration = 3000) {
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.textContent = message;
  _getContainer().appendChild(el);
  setTimeout(() => el.remove(), duration);
}

// -- Active nav link -------------------------------------------------------

(function markActiveNav() {
  const current = window.location.pathname.split("/").pop();
  document.querySelectorAll(".nav-link").forEach(link => {
    if (link.getAttribute("href") === current || link.getAttribute("href")?.endsWith("/" + current)) {
      link.classList.add("active");
    }
  });
})();

// -- Expose globals --------------------------------------------------------
window.apiFetch = apiFetch;
window.toast    = toast;
