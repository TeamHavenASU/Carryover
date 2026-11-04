export const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options) {
  const res = await fetch(`${API}${path}`, options);
  let body = null;
  try {
    body = await res.json();
  } catch {
    // an empty or non JSON reply is handled below
  }
  if (!res.ok) {
    throw new Error((body && body.detail) || `Request failed (${res.status})`);
  }
  return body;
}

export function get(path, params) {
  const query = params ? "?" + new URLSearchParams(params).toString() : "";
  return request(path + query);
}

export function post(path, data) {
  return request(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: data === undefined ? undefined : JSON.stringify(data),
  });
}
