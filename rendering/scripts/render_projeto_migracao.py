import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from objective_utils import extract_project_metadata

BASE_DIR = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = BASE_DIR / "rendering" / "md"
DEFAULT_JSON = BASE_DIR / "domain" / "projeto_migracao" / "projeto_migracao.json"
OUTPUT_FILE = BASE_DIR / "rendering" / "md" / "projeto_migracao.md"

REQUIRED_STATUS = {"documentation", "migration_project", "export", "deploy", "validation"}
SPECIAL_GROUP_IDS = {"SEM_GRUPO", "GROUP_0", "IGNORADOS"}


def _normalize(data: dict) -> dict:
    project = dict(data.get("project", {}))
    project.setdefault("code", "")
    project.setdefault("name", "")
    project.setdefault("version", "")
    project.setdefault("consultant", "")
    project.setdefault("environment", {})
    project["environment"].setdefault("source", "")
    project["environment"].setdefault("target", "")

    groups = []
    for group in data.get("groups", []):
        group_id = str(group.get("group_id") or "").strip().upper()
        if group_id in SPECIAL_GROUP_IDS:
            continue

        objects = []
        for obj in group.get("objects", []):
            obj = dict(obj)
            obj.setdefault("identifiers", {})
            obj.setdefault("technical_content", {})
            obj.setdefault("status", {})
            obj.setdefault("otm_table", "")
            obj.setdefault("migration_type", "")
            obj.setdefault("description", "")
            obj.setdefault("responsible", "")
            obj.setdefault("deployment_type", "")
            obj.setdefault("object_type", "")
            obj.setdefault("notes", "")
            obj.setdefault("sequence", "")
            obj.setdefault("name", "")
            
            # Gerar saved_query canônico a partir de technical_content
            technical_content = obj.get("technical_content", {})
            if technical_content.get("content") and technical_content.get("type") == "SQL":
                obj["saved_query"] = {
                    "sql": technical_content["content"],
                    "type": "extraction"
                }
            else:
                obj.setdefault("saved_query", None)
            
            objects.append(obj)

        group = dict(group)
        label = group.get("label") or group.get("group_name") or group.get("name", "")
        group["label"] = label
        group["name"] = label
        group.setdefault("description", "")
        group["objects"] = objects
        groups.append(group)

    project_metadata = extract_project_metadata(data)
    groups_overview = project_metadata.get("groups_overview", {}) or {}
    project_metadata["groups_overview"] = {
        "title": groups_overview.get("title", "") or "Grupos e Objetos de Migração OTM",
        "description": groups_overview.get("description", "") or "Esta seção apresenta os conjuntos de objetos do Oracle Transportation Management (OTM) contemplados no escopo de migração."
    }

    # Quebra de parágrafos para descrições de grupos e overview
    def split_paragraphs(text: str):
        return [p.strip() for p in (text or "").split("\n\n") if p.strip()]

    project_metadata["groups_overview"]["paragraphs"] = split_paragraphs(project_metadata["groups_overview"]["description"])

    for g in groups:
        g["description_paragraphs"] = split_paragraphs(g.get("description", ""))

    return {"project": project, "groups": groups, "project_metadata": project_metadata}


def _validate_status(data: dict) -> None:
    for group in data.get("groups", []):
        for obj in group.get("objects", []):
            status = obj.get("status", {})
            if not REQUIRED_STATUS.issubset(status.keys()):
                missing = sorted(REQUIRED_STATUS - set(status.keys()))
                raise ValueError(f"Status incompleto em objeto '{obj.get('name', '')}': faltando {missing}")


def render(json_path: Path):
    with open(json_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    data = _normalize(raw)
    _validate_status(data)

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=False)
    template = env.get_template("projeto_migracao.md.tpl")

    output = template.render(data=data)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(output, encoding="utf-8")
    print(f"Markdown gerado em: {OUTPUT_FILE}")

if __name__ == "__main__":
    import sys

    json_input = Path(sys.argv[1]) if len(sys.argv) == 2 else DEFAULT_JSON
    render(json_input)
