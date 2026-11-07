const { app, BrowserWindow, net, protocol, shell } = require("electron");
const { spawn } = require("node:child_process");
const fs = require("node:fs");
const path = require("node:path");
const { pathToFileURL } = require("node:url");
protocol.registerSchemesAsPrivileged([{ scheme: "lllm", privileges: { standard: true, secure: true, supportFetchAPI: true, corsEnabled: true } }]);
const API = "http://127.0.0.1:8756";
let backend, mainWindow, quitting = false;
function startBackend() {
  const executable = path.join(process.resourcesPath, "lllm-backend.exe");
  if (app.isPackaged) {
    if (!fs.existsSync(executable)) throw new Error("No se encontró el motor local empaquetado.");
    backend = spawn(executable, [], { windowsHide: true, stdio: ["ignore", "pipe", "pipe"], env: { ...process.env, LLLM_HOST: "127.0.0.1", LLLM_PORT: "8756" } });
  } else {
    const localPython = path.resolve(__dirname, "../../backend/.venv/Scripts/python.exe");
    const python = process.env.LLLM_PYTHON || (process.platform === "win32" && fs.existsSync(localPython) ? localPython : "python");
    backend = spawn(python, ["-m", "app.main"], { cwd: path.resolve(__dirname, "../../backend"), windowsHide: true, stdio: ["ignore", "pipe", "pipe"], env: { ...process.env, LLLM_HOST: "127.0.0.1", LLLM_PORT: "8756" } });
  }
  backend.stdout.on("data", (data) => process.stdout.write(`[motor] ${data}`));
  backend.stderr.on("data", (data) => process.stderr.write(`[motor] ${data}`));
  backend.on("error", (error) => console.error("No se pudo iniciar el motor local:", error));
  backend.on("exit", (code, signal) => { backend = undefined; if (!quitting) { console.error(`El motor local terminó (código ${code}, señal ${signal}).`); app.quit(); } });
}
function stopBackend() {
  if (!backend || backend.exitCode !== null) return Promise.resolve();
  const child = backend;
  if (process.platform === "win32") {
    return new Promise((resolve) => {
      const killer = spawn("taskkill", ["/pid", String(child.pid), "/t", "/f"], { windowsHide: true, stdio: "ignore" });
      killer.once("error", () => { if (child.exitCode === null) child.kill(); resolve(); });
      killer.once("exit", resolve);
    });
  }
  child.kill("SIGTERM");
  return new Promise((resolve) => {
    const timer = setTimeout(() => { if (child.exitCode === null) child.kill("SIGKILL"); resolve(); }, 4000);
    timer.unref();
    child.once("exit", () => { clearTimeout(timer); resolve(); });
  });
}
async function waitForBackend() {
  const deadline = Date.now() + 30000;
  while (Date.now() < deadline) {
    if (!backend || backend.exitCode !== null) throw new Error("El motor local terminó antes de iniciar.");
    try { const response = await fetch(`${API}/api/v1/health/ready`); if (response.ok) return; } catch { /* El backend todavía está iniciando. */ }
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
  throw new Error("El motor local no respondió en 30 segundos.");
}
function registerAppProtocol() {
  const dist = path.join(__dirname, "../dist");
  protocol.handle("lllm", (request) => {
    const url = new URL(request.url);
    if (url.host !== "bundle") return new Response("Not found", { status: 404 });
    const requested = decodeURIComponent(url.pathname === "/" ? "/index.html" : url.pathname);
    const asset = path.resolve(dist, `.${requested}`);
    const relative = path.relative(dist, asset);
    if (!relative || relative.startsWith("..") || path.isAbsolute(relative)) return new Response("Bad path", { status: 400 });
    return net.fetch(pathToFileURL(asset).toString());
  });
}
async function createWindow() {
  mainWindow = new BrowserWindow({ title: "LLLM", width: 1180, height: 760, minWidth: 720, minHeight: 520, autoHideMenuBar: true, webPreferences: { contextIsolation: true, nodeIntegration: false, sandbox: true } });
  mainWindow.webContents.setWindowOpenHandler(({ url }) => { if (url.startsWith("https://")) void shell.openExternal(url); return { action: "deny" }; });
  mainWindow.webContents.on("will-navigate", (event, url) => {
    const allowed = app.isPackaged ? url.startsWith("lllm://bundle/") : url.startsWith("http://127.0.0.1:1420/");
    if (!allowed) event.preventDefault();
  });
  if (app.isPackaged) await mainWindow.loadURL("lllm://bundle/");
  else await mainWindow.loadURL(process.env.LLLM_DEV_URL || "http://127.0.0.1:1420");
}
if (!app.requestSingleInstanceLock()) app.quit();
else {
  app.on("second-instance", () => { if (mainWindow) { if (mainWindow.isMinimized()) mainWindow.restore(); mainWindow.focus(); } });
  app.whenReady().then(async () => {
    if (app.isPackaged) registerAppProtocol();
    startBackend(); await waitForBackend(); await createWindow();
    if (app.isPackaged) {
      const { autoUpdater } = require("electron-updater");
      autoUpdater.on("error", (error) => console.warn("Actualización no disponible:", error.message));
      setTimeout(() => void autoUpdater.checkForUpdatesAndNotify().catch((error) => console.warn(error.message)), 10000).unref();
    }
  }).catch((error) => { console.error("No se pudo iniciar LLLM:", error); app.quit(); });
}
app.on("window-all-closed", () => app.quit());
app.on("before-quit", (event) => {
  if (quitting) return;
  if (!backend || backend.exitCode !== null) { quitting = true; return; }
  event.preventDefault();
  quitting = true;
  void stopBackend().finally(() => app.quit());
});



