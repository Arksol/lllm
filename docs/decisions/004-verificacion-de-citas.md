# 004 — Verificar toda cita contra el código enviado

Estado: aceptada

## Contexto

Una explicación de código que inventa referencias es peor que no dar ninguna:
el usuario que aprende no tiene forma de detectar el error.

## Decisión

Toda cita, venga del proveedor de forma nativa o extraída del texto, pasa por
`rag/citations.py` antes de mostrarse. Se comprueba que el texto citado exista
literalmente en alguno de los fragmentos enviados. Si no cuadra, se descarta.

## Consecuencias

- Es preferible una explicación con menos referencias que una con una falsa.
- El comportamiento es igual con cualquier proveedor, tenga citas nativas o no.
- Se puede perder alguna cita válida si el modelo la parafrasea al citarla.
  Es el intercambio aceptado.
