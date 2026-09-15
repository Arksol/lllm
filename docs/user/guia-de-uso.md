# Guía de uso

## Primera vez

1. Abre LLLM y ve a **Ajustes**.
2. Elige un proveedor. Si no tienes clave de ninguno, instala
   [Ollama](https://ollama.com), descarga un modelo y elige "Ollama (local)":
   no necesita clave ni conexión.
3. Pulsa **Comprobar conexión**. Si las credenciales sirven, aparece la lista de
   modelos disponibles.
4. Elige uno, ponle nombre al perfil y guarda.

## Analizar un repositorio

1. En **Nuevo análisis**, pega la URL: `github.com/usuario/proyecto`.
2. Elige **junior** o **senior**.
3. Pulsa Analizar. Verás el progreso paso a paso.

Cuando termine tendrás la explicación a la izquierda, las citas verificadas y
los hallazgos de seguridad a la derecha.

## Volver a preguntar

En la pantalla del resultado hay un campo para preguntar sobre ese análisis.
No vuelve a descargar el repositorio: usa los fragmentos ya guardados y
selecciona los relevantes para tu pregunta.

**Regenerar** rehace el análisis completo y guarda una versión nueva; la
anterior sigue en el historial.

## Cambiar de modelo

En Ajustes, cualquier perfil guardado tiene un botón **usar**. Lo habitual es
tener dos: uno potente para análisis a fondo y uno local para código que no
debe salir del equipo.

## Si algo falla

| Mensaje | Qué hacer |
|---|---|
| "Configura un modelo en Ajustes" | aún no has guardado ningún perfil |
| "Dominio no permitido" | solo se admiten GitHub y Hugging Face |
| "GitHub limitó las peticiones" | espera unos minutos o añade un token |
| "No se pudo conectar con Ollama" | comprueba que Ollama esté en ejecución |
| "No se pudo contactar con el motor local" | el proceso del motor no arrancó; revisa el registro en la carpeta de datos |

## Por qué a veces hay pocas citas

Cada cita se comprueba contra el código que se le envió al modelo. Si el texto
citado no existe, se descarta. Una explicación con tres citas verificadas vale
más que una con diez sin comprobar.
