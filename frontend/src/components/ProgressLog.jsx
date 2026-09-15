const STAGES = [
  "descargando repositorio",
  "construyendo fragmentos",
  "revisando seguridad",
  "generando explicacion",
];

export function ProgressLog({ status, stage }) {
  if (status === "listo") {
    return (
      <div className="log">
        <p className="log__line log__line--done">analisis completado</p>
      </div>
    );
  }
  if (status === "error") return null;

  const current = STAGES.indexOf(stage);

  return (
    <div className="log" role="status" aria-live="polite">
      {STAGES.map((item, index) => {
        const state =
          index < current ? "done" : index === current ? "active" : "pending";
        return (
          <p key={item} className={`log__line log__line--${state}`}>
            {state === "done" ? "hecho" : state === "active" ? "ahora" : "     "} · {item}
          </p>
        );
      })}
    </div>
  );
}
