#!/usr/bin/env python3
import sys
from pathlib import Path

# Add ui/backend to path
backend_path = Path(__file__).parent / "ui" / "backend"
sys.path.insert(0, str(backend_path.parent))

from ui.backend.app import app

if __name__ == "__main__":
    app.run(debug=False, port=8088, use_reloader=False)
