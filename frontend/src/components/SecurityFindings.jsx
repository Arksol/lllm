const ORDER = { alta: 0, media: 1, baja: 2, info: 3 };

export function SecurityFindings({ findings }) {
  const sorted = [...findings].sort(
    (a, b) => (ORDER[a.severity] ?? 9) - (ORDER[b.severity] ?? 9),
  );

  return (
    <section style={{ marginTop: "22px" }}>
      <h2 className="section-label">hallazgos de seguridad</h2>
      {sorted.length === 0 ? (
        <p className="empty">Sin hallazgos con las reglas aplicadas.</p>
      ) : (
        sorted.map((finding, index) => (
          <div key={`${finding.rule}-${index}`} className="finding">
            <span>
              {finding.message}
              <span className="card__meta">
                {finding.file_path} · L{finding.line} · {finding.tool}
              </span>
            </span>
            <span className={`tag tag--${finding.severity}`}>{finding.severity}</span>
          </div>
        ))
      )}
    </section>
  );
}
