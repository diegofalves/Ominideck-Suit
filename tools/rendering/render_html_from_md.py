def drop_roadmap_md_block(md_text: str) -> str:
    if not md_text:
        return md_text

    marker = "|#|Grupo|Objeto|Responsável|"
    start = md_text.find(marker)
    if start == -1:
        return md_text

    lines = md_text.splitlines(True)  # mantém \n
    acc = []
    in_table = False

    for line in lines:
        if not in_table:
            if marker in line:
                in_table = True
            else:
                acc.append(line)
        else:
            # estamos dentro da tabela: paramos na primeira linha em branco
            if line.strip() == "":
                in_table = False
    return "".join(acc)
def drop_roadmap_md_block(text: str) -> str:
    """Remove bloco de tabela Markdown do roadmap (|#|Grupo|Objeto|Responsável|...) do texto."""
    if not text:
        return text
    start = text.find("|#|Grupo|Objeto|Responsável|")
    if start == -1:
        return text
    # Corta até a primeira linha em branco após a tabela
    end = text.find("\n\n", start)
    if end == -1:
        end = len(text)
    return text[:start].rstrip() + "\n\n" + text[end:].lstrip()
import markdown
import json
from pathlib import Path
from jinja2 import Environment, select_autoescape, FileSystemLoader
from datetime import datetime

from objective_utils import normalize_render_data, validate_object_status

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_JSON = BASE_DIR / "domain" / "projeto_migracao" / "projeto_migracao.json"
TEMPLATE_DIR = BASE_DIR / "rendering" / "templates"
OUTPUT_FILE = BASE_DIR / "rendering" / "html" / "projeto_migracao.html"


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


def render(json_path: Path):
    raw = json.loads(json_path.read_text(encoding="utf-8"))
    # Normaliza os dados usando a função compartilhada
    data = normalize_render_data(raw)
    # Valida os dados usando a função compartilhada
    validate_object_status(data)

    def md_to_html(text):
        if not text:
            return ""
        return markdown.markdown(text, extensions=["tables", "fenced_code"])

    # Converter descrições de grupos e objetos
    for group in data["groups"]:
        if group.get("description"):
            group["description_html"] = md_to_html(group["description"])
        for obj in group["objects"]:
            if obj.get("description"):
                obj["description_html"] = md_to_html(obj["description"])
            if obj.get("notes"):
                obj["notes_html"] = md_to_html(obj["notes"])

    # Remover tabela Markdown de roadmap de campos de texto longo (exemplo: migration_plan, roadmap_text, etc.)
    # Ajuste aqui se o campo exato for diferente
    roadmap_fields = ["migration_plan", "roadmap_text"]
    if "project_metadata" in data:
        for field in roadmap_fields:
            if field in data["project_metadata"] and isinstance(data["project_metadata"][field], str):
                data["project_metadata"][field] = drop_roadmap_md_block(data["project_metadata"][field])

    # Converter blocos de objetivo do projeto (parágrafos e listas)
    migration_objective = data.get("project_metadata", {}).get("migration_objective", {})
    if migration_objective and "blocks" in migration_objective:
        for block in migration_objective["blocks"]:
            if block["type"] == "paragraph" and block.get("text"):
                block["text"] = md_to_html(block["text"])
            elif block["type"] == "list" and block.get("items"):
                block["items"] = [md_to_html(item) for item in block["items"]]

    template_dirs = [
        str(BASE_DIR / "rendering" / "html"),
        str(BASE_DIR / "rendering" / "templates")
    ]
    env = Environment(
        loader=FileSystemLoader(template_dirs),
        autoescape=select_autoescape(enabled_extensions=("html", "xml"))
    )
    env.filters['format_date_br'] = format_date_br
    template = env.get_template("base.html.tpl")
    # Para compatibilidade, passamos as variáveis principais esperadas pelo novo base.html.tpl
    # Renderiza o conteúdo principal com o contexto 'data' para o template projeto_migracao.html.tpl
    # Renderizar blocos separados para cada seção principal
    # Função auxiliar para extrair apenas o conteúdo de uma seção do template
    # Renderizar blocos separados para cada seção principal usando templates parciais
    overview = env.get_template("overview.html").render(data=data)
    metadata = env.get_template("metadata.html").render(data=data)
    objective = env.get_template("objective.html").render(data=data)
    groups_content = env.get_template("groups_content.html").render(data=data)
    roadmap = env.get_template("roadmap.html").render(data=data)

    # Corrigir ids dos grupos para sidebar
    groups = data.get("groups", [])
    for idx, group in enumerate(groups, 1):
        group["_sidebar_id"] = f"group-{group.get('domain', idx)}"

    html_output = template.render(
        title=data.get("project", {}).get("name", "Projeto de Migração"),
        project_code=data.get("project", {}).get("code", ""),
        groups=groups,
        overview=overview,
        metadata=metadata,
        objective=objective,
        groups_content=groups_content,
        roadmap=roadmap
    )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(html_output, encoding="utf-8")
    print(f"HTML gerado em: {OUTPUT_FILE}")

if __name__ == "__main__":
    import sys

    json_input = Path(sys.argv[1]) if len(sys.argv) == 2 else DEFAULT_JSON
    render(json_input)
