// Renderiza la explicacion como texto plano estructurado. No se interpreta
// HTML del modelo: su salida se trata como dato no confiable.
export function ExplanationView({ text }) {
  if (!text) return null;

  const blocks = text.split("\n").filter((line) => line.trim());

  return (
    <article className="prose">
      {blocks.map((line, index) => {
        const key = `${index}-${line.slice(0, 12)}`;
        if (/^#{1,6}\s/.test(line)) {
          return <h3 key={key}>{line.replace(/^#{1,6}\s/, "")}</h3>;
        }
        if (/^\d+\.\s|^[-*]\s/.test(line)) {
          return <li key={key}>{line.replace(/^(\d+\.|[-*])\s/, "")}</li>;
        }
        return <p key={key}>{line}</p>;
      })}
    </article>
  );
}
