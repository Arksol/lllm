import { useState } from "react";
import { validateRepoUrl } from "../utils/validators";

const MODES = [
  { key: "junior", label: "junior" },
  { key: "senior", label: "senior" },
];

export function RepoPrompt({ onSubmit, disabled, busy }) {
  const [url, setUrl] = useState("");
  const [mode, setMode] = useState("junior");
  const [error, setError] = useState(null);

  function submit(event) {
    event.preventDefault();
    const problem = validateRepoUrl(url);
    if (problem) {
      setError(problem);
      return;
    }
    setError(null);
    onSubmit(url.trim(), mode);
  }

  return (
    <form onSubmit={submit} noValidate>
      <div className="prompt-row">
        <input
          className="prompt-input"
          type="text"
          value={url}
          onChange={(event) => {
            setUrl(event.target.value);
            if (error) setError(null);
          }}
          placeholder="github.com/usuario/repositorio"
          aria-label="URL del repositorio"
          aria-invalid={Boolean(error)}
          disabled={disabled}
        />
        <button className="btn" type="submit" disabled={disabled || busy}>
          {busy ? "Iniciando" : "Analizar"}
        </button>
      </div>

      <div className="mode-row" role="group" aria-label="Nivel de explicacion">
        {MODES.map((item) => (
          <button
            key={item.key}
            type="button"
            className={`mode${mode === item.key ? " mode--on" : ""}`}
            aria-pressed={mode === item.key}
            onClick={() => setMode(item.key)}
            disabled={disabled}
          >
            {item.label}
          </button>
        ))}
      </div>

      {error && (
        <p className="notice notice--error" role="alert">
          {error}
        </p>
      )}
    </form>
  );
}
