import { useNavigate } from "react-router-dom";
import { RepoPrompt } from "../components/RepoPrompt";
import { ProgressLog } from "../components/ProgressLog";
import { CitationPanel } from "../components/CitationPanel";
import { SecurityFindings } from "../components/SecurityFindings";
import { useAnalysis } from "../hooks/useAnalysis";

export function AnalysisPage({ activeProfile }) {
  const navigate = useNavigate();
  const { analysis, error, starting, start } = useAnalysis();

  const sinModelo = !activeProfile;

  async function handleSubmit(url, mode) {
    const created = await start(url, mode);
    if (created) navigate(`/analisis/${created.id}`);
  }

  return (
    <div className="workspace">
      <main className="panel-main">
        <h1 className="lede">De noche, una linterna sobre cada archivo.</h1>

        {sinModelo ? (
          <p className="notice">
            Antes de analizar, elige un modelo en Ajustes. Puedes usar Claude,
            GPT, Gemini, un servidor propio o un modelo local con Ollama.
          </p>
        ) : (
          <p className="hint" style={{ marginTop: "14px" }}>
            Analizando con {activeProfile.model} · {activeProfile.provider}
          </p>
        )}

        <RepoPrompt onSubmit={handleSubmit} disabled={sinModelo} busy={starting} />

        {error && (
          <p className="notice notice--error" role="alert">
            {error}
          </p>
        )}

        {analysis && <ProgressLog status={analysis.status} stage={analysis.stage} />}
      </main>

      <aside className="panel-aside">
        <CitationPanel citations={analysis?.citations ?? []} />
        <SecurityFindings findings={analysis?.findings ?? []} />
      </aside>
    </div>
  );
}
