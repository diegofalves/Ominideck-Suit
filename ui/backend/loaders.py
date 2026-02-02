import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

DOMAIN_DIR = BASE_DIR / "domain" / "projeto_migracao"
ENUMS_DIR = DOMAIN_DIR / "enums"
SCHEMA_PATH = DOMAIN_DIR / "schema.json"

UI_CONTRACT_PATH = BASE_DIR / "ui" / "contracts" / "projeto_migracao.ui.json"


def load_schema():
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_enums():
    enums = {}
    for enum_file in ENUMS_DIR.glob("*.json"):
        with open(enum_file, "r", encoding="utf-8") as f:
            enums[enum_file.stem] = json.load(f)
    return enums


def load_ui_contract():
    with open(UI_CONTRACT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_groups():
    path = BASE_DIR / "metadata" / "ui" / "groups.json"
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_all():
    """
    Ponto único de carga para a UI.
    """
    return {
        "schema": load_schema(),
        "enums": load_enums(),
        "ui": load_ui_contract(),
        "groups_catalog": load_groups()
    }
