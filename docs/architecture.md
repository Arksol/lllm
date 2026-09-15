# Arquitectura

## Forma general

Monolito modular dentro de un motor local, envuelto en una ventana de escritorio.

```
┌──────────────────────────────────────────────────────┐
│  Ventana Tauri                                        │
│  ┌────────────────────────────────────────────────┐  │
│  │  Interfaz React + Vite                          │  │
│  └───────────────────┬────────────────────────────┘  │
│                      │ http 127.0.0.1:8756            │
│  ┌───────────────────▼────────────────────────────┐  │
│  │  Motor FastAPI (proceso hijo)                   │  │
│  │                                                  │  │
│  │   analysis  ── orquesta ──┐                     │  │
│  │      │                     │                     │  │
│  │   ┌──▼───┐ ┌────┐ ┌────┐ ┌▼──────────────┐     │  │
│  │   │repos │ │rag │ │llm │ │security_scan  │     │  │
│  │   └──────┘ └────┘ └────┘ └───────────────┘     │  │
│  │                                                  │  │
│  │   core (config · seguridad · registro)          │  │
│  │   settings (perfiles de modelo · claves)        │  │
│  └───────────────────┬────────────────────────────┘  │
└──────────────────────┼───────────────────────────────┘
                       ▼
          SQLite + almacén de secretos del sistema
```

## Regla de dependencia

`analysis` conoce a los cuatro dominios. Los cuatro no se conocen entre sí ni
dependen de `analysis`. `core` es la única capa que todos pueden importar.

Esto es lo que permite sustituir cualquier pieza sin tocar el resto: cambiar
BM25 por embeddings toca solo `rag`; añadir GitLab toca solo `repos`; añadir un
proveedor toca solo `llm`.

## El pipeline

1. **Validar** — la URL se comprueba contra la allowlist antes de tocar la red.
2. **Descargar** — tarball de GitHub o archivos de Hugging Face. Solo texto,
   con límite de cantidad y tamaño. Nada se ejecuta.
3. **Fragmentar** — Python por árbol sintáctico para no cortar funciones; el
   resto por bloques de líneas.
4. **Revisar seguridad** — reglas propias siempre, más Semgrep y Bandit si están
   instalados en el sistema.
5. **Seleccionar** — los fragmentos que mejor explican el proyecto: raíz,
   configuración, puntos de entrada.
6. **Generar** — el proveedor activo produce la explicación con los fragmentos
   marcados como datos.
7. **Verificar** — cada cita se comprueba contra los fragmentos enviados. Las
   que no cuadran se descartan.

Los fragmentos se guardan, así que volver a preguntar no vuelve a descargar
nada: BM25 selecciona los relevantes para esa pregunta concreta.

## Qué cambió respecto al plan web

| Antes | Ahora | Por qué |
|---|---|---|
| SPA en Hostinger + VPS | Escritorio con Tauri | las claves no deben pasar por un servidor ajeno |
| PostgreSQL + pgvector | SQLite | el usuario no debe administrar una base de datos |
| Embeddings para RAG | BM25 + señales estructurales | funciona sin conexión y sin servicio externo |
| Claude fijo | Ocho proveedores | el requisito es elegir modelo |
| Claves en el servidor | Almacén de secretos del sistema | son del usuario, se quedan con él |

Las decisiones detalladas están en `docs/decisions/`.
