# LLLM

**Large Language Learning Model.** Tres eles: no es un error de escritura.

Una aplicación de escritorio que analiza repositorios de código y te los
explica, usando el modelo de IA que tú elijas. Aprende de proyectos ajenos
mientras compruebas si son seguros.

---

## Qué hace

Le das la URL de un repositorio de GitHub o Hugging Face. LLLM lo descarga, lo
parte en fragmentos, se lo entrega al modelo que hayas configurado y devuelve
una explicación anclada al código real, con la cita del archivo y las líneas
que respaldan cada afirmación.

Dos formas de explicar:

- **Modo junior** — recorre el proyecto desde cero, define cada término técnico
  con un ejemplo, describe el flujo paso a paso y termina con tres cosas
  concretas que puedes aprender de ahí.
- **Modo senior** — asume experiencia. Arquitectura, deuda técnica ordenada por
  coste de arreglarla, mejoras concretas, tecnologías que encajarían y temas
  avanzados que este código saca a relucir.

Además:

- **Revisión de seguridad** sobre el código analizado: credenciales en el
  código, SQL concatenado, CORS abierto, TLS desactivado, HTML sin sanitizar.
- **Historial** de todo lo analizado, con la posibilidad de regenerar un
  análisis o volver a preguntar sobre él sin descargar el repositorio otra vez.

## El modelo lo eliges tú

Esto no es una aplicación atada a un proveedor. En Ajustes eliges el tuyo,
pones tu clave y listo:

| Proveedor | Necesita clave | Notas |
|---|---|---|
| Anthropic (Claude) | sí | citas nativas ancladas al fragmento |
| OpenAI | sí | |
| Google (Gemini) | sí | |
| Mistral | sí | |
| Groq | sí | |
| OpenRouter | sí | acceso a muchos modelos con una sola clave |
| Ollama | no | modelos locales, sin conexión a internet |
| Compatible con OpenAI | opcional | LM Studio, vLLM, o tu propio servidor |

Puedes guardar varios perfiles y cambiar entre ellos cuando quieras: Claude
para un análisis a fondo, un modelo local para código privado que no debe salir
de tu equipo.

Añadir un proveedor nuevo es crear un archivo en `backend/app/llm/providers/`
y registrarlo. Ningún otro archivo cambia.

## Tus datos se quedan en tu equipo

- La base de datos es SQLite, en la carpeta de datos de tu sistema operativo.
- Las claves de API van al almacén de secretos del sistema (Llavero en macOS,
  Credential Manager en Windows, Secret Service en Linux). Si no hay ninguno,
  se usa un archivo local con permisos restringidos y la app te lo dice.
- No hay telemetría. Las únicas conexiones salientes son al proveedor que
  elijas y al repositorio que pidas analizar.

## Seguridad

El código de un repositorio ajeno es material no confiable, y se trata como tal:

- **Nunca se ejecuta nada** de lo descargado. Solo se lee texto y se analiza.
- **Solo dominios permitidos** (github.com, huggingface.co). Una URL apuntando
  a una dirección interna de tu red se rechaza antes de tocar la red.
- **Inyección de instrucciones**: los fragmentos se le entregan al modelo
  marcados explícitamente como datos, nunca como órdenes. Si un repositorio
  incluye instrucciones ocultas, el modelo tiene indicación de ignorarlas y
  señalarlas como riesgo.
- **Citas verificadas**: cada cita que devuelve el modelo se comprueba contra
  los fragmentos que se le enviaron. Si el texto citado no existe en el código,
  se descarta antes de mostrarse.
- **API local cerrada**: escucha solo en 127.0.0.1, con CORS restringido a la
  ventana de la aplicación.

## Instalación

Requisitos: Python 3.11+, Node 18+, y Rust si vas a empaquetar el escritorio.

```bash
git clone <url-del-repositorio> lllm
cd lllm

# motor local
cd backend
pip install -e ".[dev]"
python -m app.main          # queda escuchando en 127.0.0.1:8756

# interfaz (en otra terminal)
cd ../frontend
npm install
npm run dev                 # http://localhost:1420
```

Para la aplicación de escritorio completa:

```bash
npm run tauri dev           # desarrollo
npm run tauri build         # instalador
```

Antes de `tauri build` hay que generar el binario del motor; los pasos están en
`src-tauri/README.md`.

## Variables de entorno

Todas opcionales, con el prefijo `LLLM_`:

| Variable | Por defecto | Para qué |
|---|---|---|
| `LLLM_DATA_DIR` | carpeta de datos del sistema | dónde viven base de datos y registros |
| `LLLM_PORT` | `8756` | puerto del motor local |
| `LLLM_MAX_REPO_FILES` | `800` | archivos leídos por análisis |
| `LLLM_MAX_CHUNKS_PER_ANALYSIS` | `40` | fragmentos enviados al modelo |
| `LLLM_DEBUG` | `false` | activa `/docs` y registro detallado |

Las claves de API **no** son variables de entorno: se configuran desde Ajustes
y se guardan cifradas por el sistema.

## Comandos

```bash
# backend
pytest                 # pruebas
ruff check app         # estilo
bandit -r app          # seguridad del propio código

# frontend
npm run dev
npm run build
npm test
npm run lint
```

## Estructura

```
lllm/
├── backend/        motor local: FastAPI + SQLite
│   └── app/
│       ├── llm/            proveedores de modelo (aquí se añaden nuevos)
│       ├── repos/          descarga de GitHub y Hugging Face
│       ├── rag/            fragmentación y verificación de citas
│       ├── security_scan/  revisión estática
│       ├── analysis/       orquestación del pipeline
│       └── settings/       perfiles de modelo y claves
├── frontend/       interfaz React + Vite
├── src-tauri/      envoltura de escritorio
└── docs/           arquitectura, decisiones, API
```

## API

El motor expone una API REST local en `/api/v1`. El detalle está en
`docs/api/endpoints.md`. Con `LLLM_DEBUG=true` tienes la documentación
interactiva en `http://127.0.0.1:8756/docs`.

## Estado

En desarrollo. Funciona el ciclo completo: analizar, explicar en ambos modos,
citar, revisar seguridad, guardar, regenerar y volver a preguntar.

## Licencia

MIT.
