# LLLM — contexto del proyecto

Aplicación de escritorio que analiza repositorios de código con el modelo de IA
que el usuario elija. LLLM = Large Language Learning Model.

## Comandos

```bash
# backend (desde backend/)
python -m app.main        # arranca en 127.0.0.1:8756
pytest                    # pruebas
ruff check app            # estilo

# frontend (desde frontend/)
npm run dev               # puerto 1420, el que espera Tauri
npm run build
npm test

# escritorio (desde frontend/)
npm run tauri dev
```

## Reglas de arquitectura

- `analysis/service.py` es el único módulo que conoce a los demás dominios.
  `repos`, `rag`, `llm` y `security_scan` no se importan entre sí.
- Nunca importar un SDK de proveedor fuera de `llm/providers/`. El resto del
  código habla con la interfaz `LLMProvider` de `llm/base.py`.
- Añadir un proveedor: un archivo en `llm/providers/` + una línea en
  `llm/registry.py`. Nada más debe cambiar. Si hace falta tocar otra cosa, la
  abstracción está mal.
- SQLite, no PostgreSQL. Es una app de escritorio: el usuario no debe instalar
  ni administrar un servidor de base de datos.

## Reglas de seguridad

- El código descargado **nunca se ejecuta**. Solo lectura y análisis estático.
- Los fragmentos van al modelo marcados como datos, nunca como instrucciones.
- Toda cita se verifica contra los fragmentos enviados antes de mostrarse
  (`rag/citations.py`). Una cita que no cuadra se descarta.
- Las claves de API van a `settings/credentials.py`, nunca a la base de datos
  ni a un log.
- La validación de host en `repos/validators.py` no se relaja.

## Convenciones

- Los mensajes de error que ve el usuario van en español y dicen qué hacer.
- Los nombres de estado en base de datos son en español: `en_cola`,
  `procesando`, `listo`, `error`.
- Comentarios solo donde el porqué no se deduce del código.
- El diseño usa las variables de `frontend/src/styles/tokens.css`. No escribir
  colores literales en los componentes.

## Qué no tocar

- Los prompts de `llm/prompts/analysis.py` incluyen la defensa contra inyección
  de instrucciones. Al editarlos, conservar el bloque de reglas.
- `frontend/src/main.jsx` usa `HashRouter` a propósito: en escritorio no hay
  servidor que resuelva rutas.
