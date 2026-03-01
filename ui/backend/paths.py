
import sys
import os
from pathlib import Path

def get_project_root() -> Path:
    """
    Determines the project root directory.

    Handles three scenarios:
    1. OMNIDECK_PROJECT_ROOT environment variable is set.
    2. Application is running as a frozen executable (PyInstaller).
    3. Application is running from source.

    Returns:
        Path: The absolute path to the project root.
    """
    env_project_root = os.environ.get("OMNIDECK_PROJECT_ROOT")

    if env_project_root:
        return Path(env_project_root).resolve()
    
    if getattr(sys, "frozen", False):
        # Running in a PyInstaller bundle
        # sys.executable points to the executable inside the .app bundle
        # e.g., /path/to/your.app/Contents/MacOS/omni_launcher
        macos_dir = Path(sys.executable).resolve().parent
        # The 'Resources' directory is where PyInstaller places data files
        # It's at /path/to/your.app/Contents/Resources
        resources_dir = macos_dir.parent / "Resources"
        if resources_dir.exists():
            return resources_dir
        else:
            # Fallback for non-macOS frozen apps if needed
            return Path(sys.executable).resolve().parent

    # Running as a regular Python script
    # This file is in ui/backend/paths.py, so we go up 3 levels
    # ui/ -> backend/ -> paths.py
    return Path(__file__).resolve().parents[2]

PROJECT_ROOT = get_project_root()
