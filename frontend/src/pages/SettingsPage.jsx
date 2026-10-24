import { useEffect, useState } from "react";
import { api } from "../api/client";
import { useProfiles } from "../hooks/useProfiles";

// Aqui el usuario decide con que modelo trabaja. El flujo es siempre el mismo
// para cualquier proveedor: elegir, comprobar credenciales, guardar perfil.
export function SettingsPage({ onProfilesChange }) {
  const { profiles, reload } = useProfiles();
  const [providers, setProviders] = useState([]);
  const [storage, setStorage] = useState(null);

  const [provider, setProvider] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [baseUrl, setBaseUrl] = useState("");
  const [models, setModels] = useState([]);
  const [model, setModel] = useState("");
  const [name, setName] = useState("");

  const [checking, setChecking] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [notice, setNotice] = useState(null);

  useEffect(() => {
    api.providers().then((data) => {
      setProviders(data);
      setProvider((current) => current || data[0]?.key || "");
    }).catch((err) => setError(err.message));
    api.storage().then(setStorage).catch(() => {});
  }, []);

  const selected = providers.find((p) => p.key === provider);

  function switchProvider(key) {
    setProvider(key);
    setModels([]);
    setModel("");
    setApiKey("");
    setBaseUrl("");
    setError(null);
    setNotice(null);
  }

  async function check(event) {
    event.preventDefault();
    if (selected?.requires_api_key && !apiKey.trim()) {
      setError("Este proveedor necesita una clave de API.");
      return;
    }
    setChecking(true);
    setError(null);
    setNotice(null);
    try {
      const found = await api.probe({
        provider,
        api_key: apiKey.trim() || null,
        base_url: baseUrl.trim() || null,
      });
      setModels(found);
      setModel(found[0]?.id ?? "");
      setNotice(
        found.length
          ? `${found.length} modelos disponibles.`
          : "La conexion funciona pero no se encontraron modelos.",
      );
    } catch (err) {
      setError(err.message);
      setModels([]);
    } finally {
      setChecking(false);
    }
  }

  async function save(event) {
    event.preventDefault();
    if (!model) {
      setError("Comprueba la conexion y elige un modelo.");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      await api.createProfile({
        name: name.trim() || `${selected?.label ?? provider} · ${model}`,
        provider,
        model,
        base_url: baseUrl.trim() || null,
        api_key: apiKey.trim() || null,
        is_default: profiles.length === 0,
      });
      setApiKey("");
      setName("");
      setNotice("Perfil guardado.");
      await reload();
      onProfilesChange?.();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function activate(id) {
    await api.setDefaultProfile(id);
    await reload();
    onProfilesChange?.();
  }

  async function remove(id) {
    await api.deleteProfile(id);
    await reload();
    onProfilesChange?.();
  }

  return (
    <div className="workspace">
      <main className="panel-main">
        <h1 className="lede">Elige con que modelo quieres trabajar.</h1>

        <form onSubmit={check} style={{ marginTop: "24px", maxWidth: "460px" }} noValidate>
          <label className="field">
            <span>Proveedor</span>
            <select value={provider} onChange={(e) => switchProvider(e.target.value)}>
              {providers.map((item) => (
                <option key={item.key} value={item.key}>
                  {item.label}
                </option>
              ))}
            </select>
          </label>

          {selected?.requires_api_key && (
            <label className="field">
              <span>Clave de API</span>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="se guarda en tu equipo"
                autoComplete="off"
              />
            </label>
          )}

          {selected?.supports_custom_base_url && (
            <label className="field">
              <span>URL del servidor</span>
              <input
                type="text"
                value={baseUrl}
                onChange={(e) => setBaseUrl(e.target.value)}
                placeholder="http://localhost:11434"
              />
            </label>
          )}

          <button className="btn btn--quiet" type="submit" disabled={checking}>
            {checking ? "Comprobando" : "Comprobar conexion"}
          </button>
        </form>

        {models.length > 0 && (
          <form onSubmit={save} style={{ marginTop: "20px", maxWidth: "460px" }} noValidate>
            <label className="field">
              <span>Modelo</span>
              <select value={model} onChange={(e) => setModel(e.target.value)}>
                {models.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.label || item.id}
                  </option>
                ))}
              </select>
            </label>

            <label className="field">
              <span>Nombre del perfil</span>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="opcional"
              />
            </label>

            <button className="btn" type="submit" disabled={saving}>
              {saving ? "Guardando" : "Guardar perfil"}
            </button>
          </form>
        )}

        {error && <p className="notice notice--error" role="alert">{error}</p>}
        {notice && <p className="notice" role="status">{notice}</p>}
      </main>

      <aside className="panel-aside">
        <h2 className="section-label">perfiles guardados</h2>
        {profiles.length === 0 ? (
          <p className="empty">Aun no has guardado ninguno.</p>
        ) : (
          profiles.map((profile) => (
            <div key={profile.id} className="card">
              <span className="card__title">
                {profile.name}
                {profile.is_default ? " · activo" : ""}
              </span>
              <span className="card__meta">
                {profile.provider} · {profile.model}
              </span>
              <div style={{ display: "flex", gap: "8px", marginTop: "10px" }}>
                {!profile.is_default && (
                  <button
                    className="mode"
                    type="button"
                    onClick={() => activate(profile.id)}
                  >
                    usar
                  </button>
                )}
                <button className="mode" type="button" onClick={() => remove(profile.id)}>
                  eliminar
                </button>
              </div>
            </div>
          ))
        )}

        {storage && (
          <p className="hint" style={{ marginTop: "18px" }}>
            {storage.detail}
          </p>
        )}
      </aside>
    </div>
  );
}
