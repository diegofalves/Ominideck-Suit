import json
from pathlib import Path
from jinja2 import Environment, select_autoescape, FileSystemLoader
from datetime import datetime

from objective_utils import extract_project_metadata

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_JSON = BASE_DIR / "domain" / "projeto_migracao" / "projeto_migracao.json"
TEMPLATE_DIR = BASE_DIR / "rendering" / "templates"
OUTPUT_FILE = BASE_DIR / "rendering" / "html" / "projeto_migracao.html"

REQUIRED_STATUS = {"documentation", "migration_project", "export", "deploy", "validation"}
SPECIAL_GROUP_IDS = {"SEM_GRUPO", "GROUP_0", "IGNORADOS"}

def format_date_br(date_str):
    """Converte data para formato brasileiro DD/MM/YYYY"""
    if not date_str:
        return date_str
    try:
        # Tenta parsear no formato YYYY-MM-DD
        date_obj = datetime.strptime(str(date_str), "%Y-%m-%d")
        return date_obj.strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        # Se falhar, retorna a string original
        return date_str


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
            obj.setdefault("object_extraction_query", {})
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

            extraction_query = obj.get("object_extraction_query", {})
            if not isinstance(extraction_query, dict):
                extraction_query = {}

            if (
                not extraction_query.get("content")
                and isinstance(obj.get("saved_query"), dict)
                and obj["saved_query"].get("sql")
            ):
                extraction_query = {
                    "language": "SQL",
                    "content": str(obj["saved_query"].get("sql") or ""),
                }

            obj["object_extraction_query"] = {
                "language": str(extraction_query.get("language") or "SQL").upper(),
                "content": str(extraction_query.get("content") or ""),
            }

            technical_content = obj.get("technical_content", {})
            if not isinstance(technical_content, dict):
                technical_content = {}
            obj["technical_content"] = {
                "type": str(technical_content.get("type") or "NONE").upper(),
                "content": str(technical_content.get("content") or ""),
            }

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

    # Defaults e parágrafos para blocos de grupo
    go = project_metadata.get("groups_overview", {}) or {}
    if "title" not in go or not go.get("title"):
        go["title"] = "Grupos e Objetos de Migração OTM"
    if "description" not in go or not go.get("description"):
        go["description"] = "Esta seção apresenta os conjuntos de objetos do Oracle Transportation Management (OTM) contemplados no escopo de migração."

    def split_paragraphs(text: str):
        return [p.strip() for p in (text or "").split("\n\n") if p.strip()]

    go["paragraphs"] = split_paragraphs(go.get("description", ""))
    project_metadata["groups_overview"] = go

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
        raw = json.loads(json_path.read_text(encoding="utf-8"))
        data = _normalize(raw)
        _validate_status(data)

        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=select_autoescape(enabled_extensions=("html", "xml")))
        env.filters['format_date_br'] = format_date_br
        template = env.get_template("projeto_migracao.html.tpl")
        html_output = template.render(data=data)

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_FILE.write_text(html_output, encoding="utf-8")
        print(f"HTML gerado em: {OUTPUT_FILE}")

if __name__ == "__main__":
    import sys

    json_input = Path(sys.argv[1]) if len(sys.argv) == 2 else DEFAULT_JSON
    render(json_input)
