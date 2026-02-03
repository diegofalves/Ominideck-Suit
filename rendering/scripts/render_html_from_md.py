import json
from pathlib import Path
from jinja2 import Environment, select_autoescape

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_JSON = BASE_DIR / "domain" / "projeto_migracao" / "projeto_migracao.json"
OUTPUT_FILE = BASE_DIR / "rendering" / "html" / "projeto_migracao.html"

REQUIRED_STATUS = {"documentation", "migration_project", "export", "deploy", "validation"}

TEMPLATE_HTML = r"""
<!doctype html>
<html lang="pt-br">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>PROJETO_MIGRACAO</title>
    <link rel="stylesheet" href="../assets/style.css" />
</head>
<body>
    <section class="project-header">
        <h1>{{ data.project.name }}</h1>
        <table class="meta-table">
            <tr><th>Código</th><td>{{ data.project.code }}</td></tr>
            <tr><th>Versão</th><td>{{ data.project.version }}</td></tr>
            <tr><th>Consultor</th><td>{{ data.project.consultant }}</td></tr>
            <tr><th>Ambiente Origem</th><td>{{ data.project.environment.source }}</td></tr>
            <tr><th>Ambiente Destino</th><td>{{ data.project.environment.target }}</td></tr>
        </table>
    </section>
    {% for group in data.groups %}
    <section class="group-block">
        <h2>{{ group.name }}</h2>

        {% for object in group.objects %}
        <section class="object-block">
            <h3>{{ object.name }}</h3>
            <p>{{ object.description }}</p>

            <table class="meta-table">
                <tr><th>Sequência</th><td>{{ object.sequence }}</td></tr>
                <tr><th>Object Type</th><td>{{ object.object_type }}</td></tr>
                <tr><th>OTM Table</th><td>{{ object.otm_table }}</td></tr>
                <tr><th>Deployment Type</th><td>{{ object.deployment_type }}</td></tr>
                <tr><th>Responsável</th><td>{{ object.responsible }}</td></tr>
                <tr><th>Tipo de Migração</th><td>{{ object.migration_type }}</td></tr>

                {% for key, value in object.identifiers.items() %}
                <tr><th>{{ key.replace('_', ' ') | title }}</th><td>{{ value }}</td></tr>
                {% endfor %}

                <tr><th>Documentação</th><td>{{ object.status.documentation }}</td></tr>
                <tr><th>Migration Project</th><td>{{ object.status.migration_project }}</td></tr>
                <tr><th>Exportação</th><td>{{ object.status.export }}</td></tr>
                <tr><th>Deploy</th><td>{{ object.status.deploy }}</td></tr>
                <tr><th>Validação</th><td>{{ object.status.validation }}</td></tr>
                {% if object.notes %}
                <tr><th>Notas</th><td>{{ object.notes }}</td></tr>
                {% endif %}
            </table>

            {% if object.technical_content and object.technical_content.content %}
            <pre><code class="language-{{ object.technical_content.type | lower }}">
{{ object.technical_content.content }}
            </code></pre>
            {% endif %}

            {% if object.saved_query %}
            <h4>Query de Extração</h4>
            <pre><code class="language-sql">
{{ object.saved_query.sql }}
            </code></pre>
            {% endif %}
        </section>
        {% endfor %}
    </section>
    {% endfor %}
</body>
</html>
""".lstrip()


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
        raw = json.loads(json_path.read_text(encoding="utf-8"))
        data = _normalize(raw)
        _validate_status(data)

        env = Environment(autoescape=select_autoescape(enabled_extensions=("html", "xml")))
        template = env.from_string(TEMPLATE_HTML)
        html_output = template.render(data=data)

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_FILE.write_text(html_output, encoding="utf-8")
        print(f"HTML gerado em: {OUTPUT_FILE}")

if __name__ == "__main__":
    import sys

    json_input = Path(sys.argv[1]) if len(sys.argv) == 2 else DEFAULT_JSON
    render(json_input)
