// Cliente de la API local. La aplicacion nunca habla directamente con un
// proveedor de modelo desde la interfaz: las claves viven en el motor local.
const BASE = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8756/api/v1";

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${BASE}${path}`, {
      headers: { "content-type": "application/json" },
      ...options,
    });
  } catch {
    throw new Error("No se pudo contactar con el motor local de LLLM.");
  }

  if (response.status === 204) return null;

  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(payload?.detail ?? `La peticion fallo (${response.status}).`);
  }
  return payload;
}

export const api = {
  health: () => request("/health/ready"),

  providers: () => request("/settings/providers"),
  storage: () => request("/settings/storage"),
  probe: (body) => request("/settings/probe", { method: "POST", body: JSON.stringify(body) }),
  profiles: () => request("/settings/profiles"),
  createProfile: (body) =>
    request("/settings/profiles", { method: "POST", body: JSON.stringify(body) }),
  setDefaultProfile: (id) => request(`/settings/profiles/${id}/default`, { method: "POST" }),
  deleteProfile: (id) => request(`/settings/profiles/${id}`, { method: "DELETE" }),

  createAnalysis: (body) =>
    request("/analysis", { method: "POST", body: JSON.stringify(body) }),
  getAnalysis: (id) => request(`/analysis/${id}`),
  history: () => request("/analysis/history"),
  regenerate: (id) => request(`/analysis/${id}/regenerate`, { method: "POST" }),
  ask: (id, question) =>
    request(`/analysis/${id}/ask`, { method: "POST", body: JSON.stringify({ question }) }),
  deleteAnalysis: (id) => request(`/analysis/${id}`, { method: "DELETE" }),
};
