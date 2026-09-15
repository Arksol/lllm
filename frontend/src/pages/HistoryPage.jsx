import { Link } from "react-router-dom";
import { useHistory } from "../hooks/useHistory";
import { formatDate } from "../utils/validators";

export function HistoryPage() {
  const { items, loading, error } = useHistory();

  return (
    <div className="workspace workspace--single">
      <main className="panel-main">
        <h1 className="lede">Todo lo que has analizado.</h1>

        {loading && <p className="empty">Cargando…</p>}
        {error && <p className="notice notice--error" role="alert">{error}</p>}

        {!loading && items.length === 0 && (
          <p className="empty">
            Aun no hay analisis. Empieza uno desde Nuevo analisis.
          </p>
        )}

        <div style={{ marginTop: "24px", maxWidth: "640px" }}>
          {items.map((item) => (
            <Link key={item.id} to={`/analisis/${item.id}`} className="card">
              <span className="card__title">{item.repo_slug}</span>
              <span className="card__meta">
                {item.mode} · {item.status} · {formatDate(item.created_at)}
              </span>
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
}
