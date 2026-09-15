# Envoltura de escritorio

Tauri empaqueta el frontend compilado y arranca el motor local de Python como
proceso hijo (`sidecar`).

Antes de `npm run tauri build` hay que generar el binario del motor:

```
pip install pyinstaller
pyinstaller --onefile --name lllm-backend backend/app/main.py
```

y copiar el resultado a `src-tauri/binaries/` con el sufijo de plataforma que
Tauri espera (por ejemplo `lllm-backend-x86_64-unknown-linux-gnu`).

Se eligio Tauri sobre Electron porque usa el motor web del propio sistema: el
instalador queda en unos pocos megabytes en lugar de cien y el consumo de
memoria en reposo es notablemente menor.
