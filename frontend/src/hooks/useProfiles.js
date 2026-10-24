import { useCallback, useEffect, useState } from "react";
import { api } from "../api/client";

// Perfiles de modelo guardados. Es lo que permite cambiar de proveedor sin
// tocar el resto de la aplicacion.
export function useProfiles() {
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const reload = useCallback(async () => {
    setLoading(true);
    try {
      setProfiles(await api.profiles());
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    reload();
  }, [reload]);

  const active = profiles.find((p) => p.is_default) ?? profiles[0] ?? null;

  return { profiles, active, loading, error, reload };
}
