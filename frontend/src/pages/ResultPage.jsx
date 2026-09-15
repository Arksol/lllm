import { useState } from "react";
import { useParams } from "react-router-dom";
import { ProgressLog } from "../components/ProgressLog";
import { ExplanationView } from "../components/ExplanationView";
import { CitationPanel } from "../components/CitationPanel";
import { SecurityFindings } from "../components/SecurityFindings";
import { useAnalysis } from "../hooks/useAnalysis";
import { api } from "../services/api";

export function ResultPage() {
  const { id } = useParams();
  const { analysis, error, regenerate } = useAnalysis(id);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [asking, setAsking] = useState(false);
  const [askError, setAskError] = useState(null);

  async function ask(event) {
    event.preventDefault();
    if (question.trim().length < 3) {
      setAskError("Escribe una pregunta un poco mas larga.");
      return;
    }
    setAsking(true);
    setAskError(null);
    try {
      setAnswer(await api.ask(id, question.trim()));
    } catch (err) {
      setAskError(err.message);
    } finally {
      setAsking(false);
    }
  }

  if (error) {
    return (
      <div className="workspace workspace--single">
        <main className="panel-main">
          <p className="notice notice--error" role="alert">{error}</p>
        </main>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="workspace workspace--single">
        <main className="panel-main">
          <p className="empty">Cargando el analisis…</p>
        </main>
      </div>
    );
  }

  return (
    <div className="workspace">
      <main className="panel-main">
        <h1 className="lede">{analysis.repo_slug}</h1>
        <p className="card__meta">
          modo {analysis.mode} · {analysis.file_count} archivos ·{" "}
          {analysis.chunk_count} fragmentos
          {analysis.model ? ` · ${analysis.model}` : ""}
        </p>

        <ProgressLog status={analysis.status} stage={analysis.stage} />

        {analysis.status === "error" && (
          <p className="notice notice--error" role="alert">{analysis.error}</p>
        )}

        {analysis.status === "listo" && (
          <>
            <ExplanationView text={analysis.explanation} />

            <div style={{ display: "flex", gap: "10px", marginTop: "24px" }}>
              <button
                className="btn btn--quiet"
                type="button"
                onClick={() => regenerate(analysis.id)}
              >
                Regenerar
              </button>
            </div>

            <form onSubmit={ask} style={{ marginTop: "28px" }} noValidate>
              <h2 className="section-label">volver a preguntar</h2>
              <div className="prompt-row" style={{ marginTop: 0 }}>
                <input
                  className="prompt-input"
                  type="text"
                  value={question}
                  onChange={(event) => {
                    setQuestion(event.target.value);
                    if (askError) setAskError(null);
                  }}
                  placeholder="Como se gestionan los errores?"
                  aria-label="Pregunta sobre este analisis"
                />
                <button className="btn" type="submit" disabled={asking}>
                  {asking ? "Pensando" : "Preguntar"}
                </button>
              </div>
              {askError && (
                <p className="notice notice--error" role="alert">{askError}</p>
              )}
            </form>

            {answer && <ExplanationView text={answer.answer} />}
          </>
        )}
      </main>

      <aside className="panel-aside">
        <CitationPanel citations={answer?.citations ?? analysis.citations} />
        <SecurityFindings findings={analysis.findings} />
      </aside>
    </div>
  );
}
