import { Link } from "react-router-dom";
import { useHistory } from "../hooks/useHistory";

export function RepositoriesPage() {
  const { items, loading } = useHistory();

  const repos = Object.values(
    items.reduce((accumulator, item) => {
      const current = accumulator[item.repo_slug];
      accumulator[item.repo_slug] = {
        slug: item.repo_slug,
        url: item.repo_url,
        count: (current?.count ?? 0) + 1,
        lastId: current?.lastId ?? item.id,
      };
      return accumulator;
    }, {}),
  );

  return (
    <div className="workspace workspace--single">
      <main className="panel-main">
        <h1 className="lede">Los proyectos que has abierto.</h1>

        {loading && <p className="empty">Cargando…</p>}
        {!loading && repos.length === 0 && (
          <p className="empty">
            Aqui apareceran los repositorios en cuanto analices el primero.
          </p>
        )}

        <div style={{ marginTop: "24px", maxWidth: "640px" }}>
          {repos.map((repo) => (
            <Link key={repo.slug} to={`/analisis/${repo.lastId}`} className="card">
              <span className="card__title">{repo.slug}</span>
              <span className="card__meta">
                {repo.count} {repo.count === 1 ? "analisis" : "analisis"} · {repo.url}
              </span>
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
}
