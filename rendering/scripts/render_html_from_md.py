from pathlib import Path
import markdown
from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).resolve().parents[2]
MD_DIR = BASE_DIR / "rendering" / "md"
HTML_DIR = BASE_DIR / "rendering" / "html"

def render(md_file: Path):
    md_content = md_file.read_text(encoding="utf-8")

    html_body = markdown.markdown(
        md_content,
        extensions=["extra"]
    )

    env = Environment(
        loader=FileSystemLoader(HTML_DIR),
        autoescape=True
    )

    template = env.get_template("base.html.tpl")

    html_output = template.render(
        title="Projeto de Migração OTM",
        content=html_body
    )

    output_file = HTML_DIR / md_file.with_suffix(".html").name
    output_file.write_text(html_output, encoding="utf-8")

    print(f"HTML gerado em: {output_file}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Uso: python render_html_from_md.py <arquivo_md>")
        raise SystemExit(1)

    render(Path(sys.argv[1]))
