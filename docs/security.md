# Seguridad

El código de un repositorio ajeno es material no confiable. Todo el diseño
parte de ahí.

## Nunca se ejecuta código descargado

No hay `pip install`, ni `npm install`, ni ejecución de scripts del repositorio.
Se descarga texto, se lee y se analiza. Las herramientas externas (Semgrep,
Bandit) también son analizadores estáticos y corren sobre archivos, no sobre el
programa.

## Inyección indirecta de instrucciones

Un README o un comentario puede contener órdenes dirigidas al modelo. Mitigación
en capas:

1. Los fragmentos se entregan delimitados y declarados como datos.
2. El prompt del sistema indica explícitamente que las instrucciones halladas en
   el material son parte de lo examinado, y que su presencia se reporte como
   riesgo.
3. El modelo no tiene herramientas con efectos: no puede escribir archivos,
   abrir conexiones ni acceder a credenciales. Su salida es texto que se
   verifica antes de mostrarse.

No hay solución determinista para la inyección de instrucciones. Esto reduce y
contiene el riesgo; no lo elimina.

## Peticiones a direcciones no previstas

`repos/validators.py` acepta solo https y solo dominios de la lista. Una URL
apuntando a una dirección interna de la red del usuario se rechaza antes de
abrir ninguna conexión.

## Credenciales

Van al almacén de secretos del sistema operativo. En la base de datos solo se
guarda una referencia, nunca el valor. Si no hay almacén disponible, se usa un
archivo local con permisos de solo-propietario y la interfaz lo indica.

Ninguna clave aparece en los registros ni en las respuestas de la API.

## La API local

Escucha solo en 127.0.0.1, con CORS limitado a los orígenes de la ventana y
`TrustedHostMiddleware` restringido a localhost. Así ninguna página abierta en
el navegador del usuario puede hablar con el motor. La documentación
interactiva solo se expone con `LLLM_DEBUG=true`.

## Errores

El usuario ve la causa y qué hacer. Nunca una traza interna: se registra en el
archivo de log y se responde con un mensaje neutro.

## Salida del modelo

Se trata como dato no confiable. La explicación se renderiza como texto
estructurado; no se interpreta HTML del modelo en ningún punto de la interfaz.
