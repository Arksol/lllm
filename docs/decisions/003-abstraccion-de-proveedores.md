# 003 — Capa de abstracción sobre los proveedores de modelo

Estado: aceptada

## Contexto

El requisito es que cualquier persona use LLLM con el modelo de su preferencia
y pueda cambiar entre modelos. Atarse al SDK de un proveedor haría que cada
proveedor nuevo tocara el dominio entero.

## Decisión

Una interfaz `LLMProvider` (`llm/base.py`) con `list_models` y `complete`.
Los dominios solo conocen esa interfaz. Los proveedores viven en
`llm/providers/` y se registran en `llm/registry.py`.

Los proveedores que hablan el dialecto de OpenAI comparten una sola
implementación: OpenAI, Mistral, Groq, OpenRouter y cualquier servidor
compatible son subclases de tres líneas.

## Consecuencias

- Añadir un proveedor no toca `analysis`, `rag` ni `security_scan`.
- La interfaz de Ajustes se construye leyendo el registro, así que un proveedor
  nuevo aparece en la pantalla sin tocar el frontend.
- Se pierde acceso a funciones propias de cada proveedor salvo que se modelen
  en la interfaz. Ya pasa con las citas: Claude las devuelve de forma nativa y
  para los demás se piden en el prompt. La verificación posterior
  (`rag/citations.py`) iguala el resultado.
