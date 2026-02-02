import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
PROJECT_PATH = BASE_DIR / "domain/projeto_migracao/projeto_migracao.json"


def load_project():
    if not PROJECT_PATH.exists():
        return None

    if PROJECT_PATH.stat().st_size == 0:
        return None

    with open(PROJECT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_project(domain):
    PROJECT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PROJECT_PATH, "w", encoding="utf-8") as f:
        json.dump(domain, f, indent=2, ensure_ascii=False)
