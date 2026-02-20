import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from objective_utils import normalize_render_data, validate_object_status

BASE_DIR = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = BASE_DIR / "rendering" / "md"
DEFAULT_JSON = BASE_DIR / "domain" / "projeto_migracao" / "projeto_migracao.json"
OUTPUT_FILE = BASE_DIR / "rendering" / "md" / "projeto_migracao.md"
SPECIAL_GROUP_IDS = {"SEM_GRUPO", "GROUP_0", "IGNORADOS"}

def render(json_path: Path):
    with open(json_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    try:
        data = normalize_render_data(raw)
        validate_object_status(data)

        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=False)
        template = env.get_template("projeto_migracao.md.tpl")

        output = template.render(data=data)

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_FILE.write_text(output, encoding="utf-8")
        print(f"Markdown gerado em: {OUTPUT_FILE}")
    except Exception as e:
        import traceback
        print("\n[ERRO] Falha ao gerar o Markdown do projeto de migração:")
        print(str(e))
        traceback.print_exc()
        raise

if __name__ == "__main__":
    import sys

    json_input = Path(sys.argv[1]) if len(sys.argv) == 2 else DEFAULT_JSON
    render(json_input)
