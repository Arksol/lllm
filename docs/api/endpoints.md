# API local

Base: `http://127.0.0.1:8756/api/v1`. Solo acepta peticiones del propio equipo.

## Análisis

### `POST /analysis`
Registra un análisis y lo ejecuta en segundo plano.

- Recibe: `{ "repo_url": string, "mode": "junior"|"senior", "profile_id"?: string }`
- Devuelve `202` con el análisis en estado `en_cola`.
- Errores: `400` URL inválida o dominio no permitido · `409` sin modelo configurado.
- Seguridad: allowlist de dominios, validación de esquema https.

### `GET /analysis/{id}`
Estado y resultado, incluidas citas verificadas y hallazgos de seguridad.

- Errores: `404` no existe.

### `POST /analysis/{id}/regenerate`
Crea una versión nueva conservando la anterior en el historial.

- Devuelve `202` con el nuevo id y `parent_id` apuntando al original.
- Errores: `404`.

### `POST /analysis/{id}/ask`
Vuelve a preguntar sobre un análisis ya hecho. Usa los fragmentos guardados, no
descarga el repositorio otra vez.

- Recibe: `{ "question": string }`
- Devuelve: `{ "answer": string, "citations": [...] }`
- Errores: `404` no existe o ya no conserva fragmentos · `502` fallo del proveedor.

### `GET /analysis/history`
Listado paginado. Query: `page`, `page_size` (máximo 100).

### `DELETE /analysis/{id}`
Elimina el análisis con sus fragmentos, citas y hallazgos.

## Ajustes

### `GET /settings/providers`
Catálogo de proveedores con sus requisitos (si piden clave, si admiten URL propia).

### `POST /settings/probe`
Comprueba credenciales y devuelve los modelos disponibles, sin guardar nada.

- Recibe: `{ "provider": string, "api_key"?: string, "base_url"?: string }`
- Errores: `400` credenciales inválidas o proveedor desconocido.

### `GET /settings/profiles` · `POST /settings/profiles`
Lista y crea perfiles de modelo. La clave se guarda en el almacén de secretos
del sistema; la respuesta solo indica si existe (`has_api_key`), nunca su valor.

### `POST /settings/profiles/{id}/default`
Marca un perfil como activo.

### `DELETE /settings/profiles/{id}`
Elimina el perfil y su credencial asociada.

### `GET /settings/storage`
Indica si las claves van al almacén del sistema o al archivo de respaldo.

## Salud

### `GET /health` · `GET /health/ready`
La segunda comprueba la base de datos e informa de qué herramientas de
seguridad externas hay disponibles en el sistema.
