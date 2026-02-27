import os
import sys
import threading
import time
import webview

# --- Fix working directory when running inside PyInstaller bundle ---
if getattr(sys, 'frozen', False):
    # When bundled (onedir mode), use executable directory
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.abspath(".")

os.chdir(base_path)
# ---------------------------------------------------------------

def start_flask():
    log_path = os.path.join(base_path, "omni_debug.log")

    with open(log_path, "w") as f:
        f.write("STARTING FLASK\n")
        f.write(f"base_path: {base_path}\n")
        f.write(f"cwd: {os.getcwd()}\n")
        f.write(f"sys.path: {sys.path}\n")

    try:
        from ui.backend.app import app

        with open(log_path, "a") as f:
            f.write("IMPORT OK\n")

        app.run(host="127.0.0.1", port=8088, debug=True, use_reloader=False)

    except Exception as e:
        with open(log_path, "a") as f:
            f.write("FLASK START ERROR\n")
            f.write(str(e) + "\n")

        import traceback
        with open(log_path, "a") as f:
            f.write(traceback.format_exc())

def main():
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()

    time.sleep(5)

    webview.create_window(
        "OmniDeck – Bauducco",
        "http://127.0.0.1:8088",
        width=1280,
        height=800
    )

    webview.start(debug=False)

if __name__ == "__main__":
    main()