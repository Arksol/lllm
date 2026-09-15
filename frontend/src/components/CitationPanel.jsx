export function CitationPanel({ citations }) {
  return (
    <section>
      <h2 className="section-label">citas verificadas</h2>
      {citations.length === 0 ? (
        <p className="empty">
          Aun no hay citas. Solo se muestran las que apuntan a codigo que existe
          de verdad en el repositorio.
        </p>
      ) : (
        citations.map((citation) => (
          <blockquote
            key={`${citation.file_path}-${citation.start_line}`}
            className="citation"
          >
            {citation.text}
            <cite className="citation__source">
              {citation.file_path} · L{citation.start_line}–{citation.end_line}
            </cite>
          </blockquote>
        ))
      )}
    </section>
  );
}
