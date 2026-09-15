const HOSTS = ["github.com", "huggingface.co"];

// Misma comprobacion que hace el motor, adelantada al formulario para que el
// usuario vea el error antes de esperar una peticion.
export function validateRepoUrl(raw) {
  const value = (raw ?? "").trim();
  if (!value) return "Escribe la URL de un repositorio.";

  let url;
  try {
    url = new URL(value.includes("://") ? value : `https://${value}`);
  } catch {
    return "Esa URL no tiene un formato valido.";
  }

  const host = url.hostname.replace(/^www\./, "");
  if (!HOSTS.includes(host)) {
    return `Por ahora solo se admiten ${HOSTS.join(" y ")}.`;
  }

  const parts = url.pathname.split("/").filter(Boolean);
  const trimmed = host === "huggingface.co" && ["datasets", "spaces"].includes(parts[0])
    ? parts.slice(1)
    : parts;
  if (trimmed.length < 2) return "Falta el propietario o el nombre del repositorio.";

  return null;
}

export function formatDate(value) {
  if (!value) return "";
  return new Date(value).toLocaleString("es", {
    day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit",
  });
}
