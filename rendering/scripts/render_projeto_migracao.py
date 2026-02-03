import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = BASE_DIR / "rendering" / "md"
DEFAULT_JSON = BASE_DIR / "domain" / "projeto_migracao" / "projeto_migracao.json"
OUTPUT_FILE = BASE_DIR / "rendering" / "md" / "projeto_migracao.md"

REQUIRED_STATUS = {"documentation", "migration_project", "export", "deploy", "validation"}


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
        group["name"] = group.get("label", "")
        group.setdefault("label", "")
        group["objects"] = objects
        groups.append(group)

    return {"project": project, "groups": groups}


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
