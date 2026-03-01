import os
import sys
import threading
import time
import webview
from pathlib import Path

APP_CONFIG_DIR = Path.home() / ".omnideck"
PROJECT_ROOT_HINT_FILE = APP_CONFIG_DIR / "project_root.txt"


def _is_valid_project_root(path: Path) -> bool:
    required = [
        path / "ui" / "backend" / "app.py",
        path / "ui" / "frontend" / "templates" / "home.html",
        path / "domain" / "projeto_migracao" / "documento_migracao.json",
    ]
    return all(item.exists() for item in required)


def _persist_project_root(project_root: Path) -> None:
    try:
        APP_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        PROJECT_ROOT_HINT_FILE.write_text(str(project_root), encoding="utf-8")
    except Exception:
        # Persistência é best effort
        pass


def _resolve_project_root() -> Path:
    # 1) Variável de ambiente explícita
    env_root = os.environ.get("OMNIDECK_PROJECT_ROOT", "").strip()
    if env_root:
        env_path = Path(env_root).expanduser().resolve()
        if _is_valid_project_root(env_path):
            return env_path

    # 2) Execução a partir do código-fonte
    source_root = Path(__file__).resolve().parent
    if _is_valid_project_root(source_root):
        return source_root

    # 3) Último root conhecido salvo em ~/.omnideck/project_root.txt
    if PROJECT_ROOT_HINT_FILE.exists():
        try:
            hinted = Path(PROJECT_ROOT_HINT_FILE.read_text(encoding="utf-8").strip()).expanduser().resolve()
            if _is_valid_project_root(hinted):
                return hinted
        except Exception:
            pass

    # 4) CWD atual (útil quando app é aberto via terminal no root do projeto)
    cwd_root = Path.cwd().resolve()
    if _is_valid_project_root(cwd_root):
        return cwd_root

    # 5) Fallback do bundle PyInstaller
    if getattr(sys, "frozen", False):
        macos_dir = Path(sys.executable).resolve().parent
        resources_dir = (macos_dir.parent / "Resources").resolve()
        if _is_valid_project_root(resources_dir):
            return resources_dir

    # 6) Último fallback: diretório do script
    return source_root


PROJECT_ROOT = _resolve_project_root()
BASE_PATH = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else PROJECT_ROOT

# Garantir que backend use sempre o mesmo root em app desktop e navegador/terminal
os.environ["OMNIDECK_PROJECT_ROOT"] = str(PROJECT_ROOT)
_persist_project_root(PROJECT_ROOT)

# Diretório de trabalho alinhado ao projeto real
os.chdir(str(PROJECT_ROOT))

def start_flask():
    log_path = str(BASE_PATH / "omni_debug.log")

    with open(log_path, "w") as f:
        f.write("STARTING FLASK\n")
        f.write(f"base_path: {BASE_PATH}\n")
        f.write(f"project_root: {PROJECT_ROOT}\n")
        f.write(f"cwd: {os.getcwd()}\n")
        f.write(f"OMNIDECK_PROJECT_ROOT: {os.environ.get('OMNIDECK_PROJECT_ROOT')}\n")
        f.write(f"sys.path: {sys.path}\n")

    try:
        from ui.backend.app import app

        with open(log_path, "a") as f:
            f.write("IMPORT OK\n")
            f.write(f"Flask app configured: {app.name}\n")
            f.write(f"Template folder: {app.template_folder}\n")
            f.write(f"Static folder: {app.static_folder}\n")

        # Desativar debug e reloader aqui (já desativado em app.py também)
        app.run(host="127.0.0.1", port=8088, debug=False, use_reloader=False)

    except Exception as e:
        with open(log_path, "a") as f:
            f.write("FLASK START ERROR\n")
            f.write(str(e) + "\n")

        import traceback
        with open(log_path, "a") as f:
            f.write(traceback.format_exc())
        
        # Também imprimir no console para debug
        print("ERROR starting Flask:")
        print(str(e))
        traceback.print_exc()

def main():
    log_path = str(BASE_PATH / "omni_debug.log")
    
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()

    with open(log_path, "a") as f:
        f.write("\nWaiting for Flask to start...\n")
    
    time.sleep(5)
    
    with open(log_path, "a") as f:
        f.write("Creating PyWebView window...\n")

    # Determinar título da janela (dinâmico baseado no projeto ativo)
    try:
        from ui.backend.project_context import get_active_project_context
        context = get_active_project_context()
        if context:
            window_title = f"OmniDeck – {context._project_data.get('name', 'Suite')}"
        else:
            window_title = "OmniDeck Suite"
    except:
        window_title = "OmniDeck Suite"

    # Criar janela abrindo na home
    window = webview.create_window(
        window_title,
        "http://127.0.0.1:8088",
        width=1280,
        height=800
    )

    # Limpar storage ao iniciar para evitar cache de versões antigas
    def clear_storage():
        try:
            with open(log_path, "a") as f:
                f.write("Clearing storage...\n")
            
            window.evaluate_js('''
                localStorage.clear();
                sessionStorage.clear();
            ''')
            
            with open(log_path, "a") as f:
                f.write("Storage cleared successfully\n")
        except Exception as e:
            with open(log_path, "a") as f:
                f.write(f"Could not clear storage: {e}\n")
            print(f"Could not clear storage: {e}")
    
    # Executar limpeza após janela carregar
    window.events.loaded += clear_storage

    with open(log_path, "a") as f:
        f.write("Starting PyWebView...\n")

    webview.start(debug=False)

if __name__ == "__main__":
    main()