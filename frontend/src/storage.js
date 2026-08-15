const PARENT_TOKEN_KEY = "lwm_parent_token";
const PARENT_EMAIL_KEY = "lwm_parent_email";
const ACTIVE_CHILD_KEY = "lwm_active_child";

function readJson(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

function writeJson(key, value) {
  localStorage.setItem(key, JSON.stringify(value));
}

export function getParentToken() {
  return localStorage.getItem(PARENT_TOKEN_KEY);
}

export function setParentSession(token, email) {
  localStorage.setItem(PARENT_TOKEN_KEY, token);
  if (email) localStorage.setItem(PARENT_EMAIL_KEY, email);
}

export function clearParentSession() {
  localStorage.removeItem(PARENT_TOKEN_KEY);
  localStorage.removeItem(PARENT_EMAIL_KEY);
}

// The active child session token persists across page reloads; the child's
// list and progress are always fetched fresh from the backend (see api.js).
export function getActiveChild() {
  return readJson(ACTIVE_CHILD_KEY, null);
}

export function setActiveChild(child) {
  writeJson(ACTIVE_CHILD_KEY, child);
}

export function clearActiveChild() {
  localStorage.removeItem(ACTIVE_CHILD_KEY);
}
