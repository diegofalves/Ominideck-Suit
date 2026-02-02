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
        data = json.load(f)

    # Compatibilidade retroativa: adicionar 'name' e 'description' se não existirem
    if data.get("groups"):
        for group_idx, group in enumerate(data["groups"]):
            if group.get("objects"):
                for obj_idx, obj in enumerate(group["objects"]):
                    if "name" not in obj:
                        # Gerar fallback: TYPE #index
                        obj_type = obj.get("object_type") or obj.get("type", "OBJETO")
                        obj["name"] = f"{obj_type} #{obj_idx + 1}"
                    if "description" not in obj:
                        obj["description"] = ""
                    
                    # Garantir status existe
                    if "status" not in obj:
                        obj["status"] = {
                            "documentation": "PENDING",
                            "deployment": "PENDING"
                        }
                    else:
                        # Garantir campos de status existem
                        if "documentation" not in obj["status"]:
                            obj["status"]["documentation"] = "PENDING"
                        if "deployment" not in obj["status"]:
                            obj["status"]["deployment"] = "PENDING"
                    
                    # Garantir saved_query existe para SAVED_QUERY
                    obj_type = obj.get("object_type") or obj.get("type")
                    if obj_type == "SAVED_QUERY" and "saved_query" not in obj:
                        obj["saved_query"] = {"sql": ""}

    return data


def save_project(domain):
    PROJECT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PROJECT_PATH, "w", encoding="utf-8") as f:
        json.dump(domain, f, indent=2, ensure_ascii=False)
