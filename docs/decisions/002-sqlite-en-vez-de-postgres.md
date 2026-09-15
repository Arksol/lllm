# 002 — SQLite en vez de PostgreSQL + pgvector

Estado: aceptada · sustituye la decisión de base de datos del plan web

## Contexto

El plan original usaba PostgreSQL con pgvector para el historial y la búsqueda
semántica. En una aplicación de escritorio, eso obliga al usuario a instalar y
administrar un servidor de base de datos antes de poder usar el programa.

## Decisión

SQLite, en la carpeta de datos del sistema operativo. Para la recuperación de
fragmentos se usa BM25 en memoria (`rag/retrieval.py`) en lugar de embeddings.

## Consecuencias

- Instalación sin pasos previos: el archivo se crea al primer arranque.
- La búsqueda funciona sin conexión y sin servicio de embeddings, lo que
  importa cuando el usuario trabaja con un modelo local.
- A cambio: BM25 no capta sinónimos. Se compensa con señales estructurales
  (archivos raíz, configuración, puntos de entrada pesan más).
- Si un día hace falta búsqueda semántica, `rag/retrieval.py` es el único
  módulo que cambia; el resto habla con `select_overview` y `BM25Index.search`.
