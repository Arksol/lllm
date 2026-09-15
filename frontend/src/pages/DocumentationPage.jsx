const SECTIONS = [
  {
    title: "Que hace LLLM",
    body:
      "Descarga un repositorio publico, lo parte en fragmentos, se lo entrega al " +
      "modelo que hayas elegido y devuelve una explicacion con citas al codigo real. " +
      "Nada del repositorio se ejecuta: solo se lee.",
  },
  {
    title: "Modo junior y modo senior",
    body:
      "El modo junior explica el proyecto desde cero, define cada termino tecnico " +
      "y recorre el flujo paso a paso. El modo senior asume experiencia y se centra " +
      "en arquitectura, deuda tecnica, mejoras y tecnologias que encajarian.",
  },
  {
    title: "Elegir y cambiar de modelo",
    body:
      "En Ajustes puedes guardar varios perfiles: Claude para analisis profundo, " +
      "un modelo local con Ollama para codigo privado, o cualquier servidor " +
      "compatible con OpenAI. Cambiar de perfil no requiere reconfigurar nada mas.",
  },
  {
    title: "Donde viven tus datos",
    body:
      "Todo se guarda en tu equipo: base de datos, historial y claves. Las claves " +
      "van al almacen de secretos del sistema operativo cuando esta disponible. " +
      "La aplicacion no envia telemetria.",
  },
  {
    title: "Por que algunas citas no aparecen",
    body:
      "Cada cita que devuelve el modelo se comprueba contra los fragmentos que se " +
      "le enviaron. Si el texto citado no existe en el codigo, se descarta. Es " +
      "preferible una explicacion con menos referencias que una con una falsa.",
  },
  {
    title: "Limites actuales",
    body:
      "Solo repositorios publicos de GitHub y Hugging Face. Se leen hasta 800 " +
      "archivos de texto por analisis. Los repositorios muy grandes se analizan de " +
      "forma parcial, priorizando archivos raiz, configuracion y puntos de entrada.",
  },
];

export function DocumentationPage() {
  return (
    <div className="workspace workspace--single">
      <main className="panel-main">
        <h1 className="lede">Como funciona esto.</h1>
        <div className="prose">
          {SECTIONS.map((section) => (
            <section key={section.title}>
              <h3>{section.title}</h3>
              <p>{section.body}</p>
            </section>
          ))}
        </div>
      </main>
    </div>
  );
}
