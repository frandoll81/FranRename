use tauri::{AppHandle, Manager};
use tauri_plugin_shell::ShellExt;
use std::fs;
use std::path::Path;

#[tauri::command]
async fn run_ocr(app: AppHandle, image_path: String, coords: String) -> Result<String, String> {
    let shell = app.shell();
    let sidecar = shell.sidecar("ocr-engine")
        .map_err(|e| e.to_string())?
        .args([image_path, coords]);

    let output = sidecar.output()
        .await
        .map_err(|e| e.to_string())?;

    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    } else {
        Err(String::from_utf8_lossy(&output.stderr).to_string())
    }
}

#[tauri::command]
fn rename_file(old_path: String, new_name: String) -> Result<(), String> {
    let path = Path::new(&old_path);
    let parent = path.parent().ok_or("Invalid path")?;
    let new_path = parent.join(new_name);

    fs::rename(path, new_path).map_err(|e| e.to_string())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_fs::init()) // Initializing the FS plugin for Tauri v2 security
        .invoke_handler(tauri::generate_handler![run_ocr, rename_file])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
