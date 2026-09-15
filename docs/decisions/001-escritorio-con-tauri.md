# 001 — Aplicación de escritorio con Tauri

Estado: aceptada

## Contexto

El proyecto nació como aplicación web desplegada en un servidor. Al abrirlo a
otras personas con el modelo de su preferencia, ese diseño deja de funcionar:
implicaría que las claves de API de terceros pasen por un servidor nuestro, con
la responsabilidad de custodiarlas y el coste de operarlo.

## Decisión

Aplicación de escritorio con Tauri. El frontend compilado se empaqueta junto a
un motor Python que corre como proceso hijo en 127.0.0.1.

Tauri sobre Electron porque usa el motor web del sistema operativo: el
instalador queda en pocos megabytes en vez de cien, y el consumo de memoria en
reposo es notablemente menor.

## Consecuencias

- Las claves nunca salen del equipo del usuario. No hay servidor que asegurar.
- Los modelos locales (Ollama) pasan a ser viables: el motor ya corre en la
  misma máquina.
- A cambio: hay que empaquetar para tres sistemas operativos y firmar
  binarios, y el usuario instala en vez de abrir una URL.
- Desaparece el despliegue en Hostinger y el VPS que exigía el plan original.
