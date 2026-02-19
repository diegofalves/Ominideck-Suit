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
