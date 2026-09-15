// Arranca el motor local de Python como proceso hijo y abre la ventana.
// El motor solo escucha en 127.0.0.1: nunca queda expuesto a la red.
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::Manager;
use tauri_plugin_shell::process::CommandEvent;
use tauri_plugin_shell::ShellExt;

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            let sidecar = app
                .shell()
                .sidecar("lllm-backend")
                .expect("no se encontro el motor local");

            let (mut rx, _child) = sidecar.spawn().expect("el motor local no arranco");

            tauri::async_runtime::spawn(async move {
                while let Some(event) = rx.recv().await {
                    if let CommandEvent::Stderr(line) = event {
                        eprintln!("[motor] {}", String::from_utf8_lossy(&line));
                    }
                }
            });

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("no se pudo iniciar LLLM");
}
