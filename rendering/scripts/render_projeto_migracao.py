import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = BASE_DIR / "rendering" / "md"
OUTPUT_DIR = BASE_DIR / "rendering" / "md"

def render(json_path: Path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=False
    )

    template = env.get_template("projeto_migracao.md.tpl")

    output = template.render(
        project=data["project"],
        groups=data["groups"]
    )

    output_file = OUTPUT_DIR / "projeto_migracao.md"
    output_file.write_text(output, encoding="utf-8")

    print(f"Markdown gerado em: {output_file}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Uso: python render_projeto_migracao.py <caminho_json>")
        sys.exit(1)

    json_input = Path(sys.argv[1])
    render(json_input)
