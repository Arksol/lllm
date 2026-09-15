import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "../services/api";

const FINISHED = ["listo", "error"];

// Lanza un analisis y sigue su estado hasta que termina.
export function useAnalysis(initialId = null) {
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState(null);
  const [starting, setStarting] = useState(false);
  const timer = useRef(null);

  const stopPolling = useCallback(() => {
    if (timer.current) {
      clearInterval(timer.current);
      timer.current = null;
    }
  }, []);

  const track = useCallback(
    (id) => {
      stopPolling();
      timer.current = setInterval(async () => {
        try {
          const next = await api.getAnalysis(id);
          setAnalysis(next);
          if (FINISHED.includes(next.status)) stopPolling();
        } catch (err) {
          setError(err.message);
          stopPolling();
        }
      }, 1200);
    },
    [stopPolling],
  );

  const start = useCallback(
    async (repoUrl, mode) => {
      setError(null);
      setStarting(true);
      try {
        const created = await api.createAnalysis({ repo_url: repoUrl, mode });
        setAnalysis(created);
        track(created.id);
        return created;
      } catch (err) {
        setError(err.message);
        return null;
      } finally {
        setStarting(false);
      }
    },
    [track],
  );

  const regenerate = useCallback(
    async (id) => {
      setError(null);
      try {
        const created = await api.regenerate(id);
        setAnalysis(created);
        track(created.id);
        return created;
      } catch (err) {
        setError(err.message);
        return null;
      }
    },
    [track],
  );

  useEffect(() => {
    if (!initialId) return undefined;
    let cancelled = false;
    api
      .getAnalysis(initialId)
      .then((data) => {
        if (cancelled) return;
        setAnalysis(data);
        if (!FINISHED.includes(data.status)) track(initialId);
      })
      .catch((err) => !cancelled && setError(err.message));
    return () => {
      cancelled = true;
    };
  }, [initialId, track]);

  useEffect(() => stopPolling, [stopPolling]);

  return { analysis, error, starting, start, regenerate, setError };
}
