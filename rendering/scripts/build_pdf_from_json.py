import os
import sys
# --- Ajuste automático de variáveis de ambiente para libs do Homebrew (macOS) ---
if sys.platform == "darwin":
    homebrew_lib = "/opt/homebrew/lib"
    homebrew_pkg = "/opt/homebrew/lib/pkgconfig"
    os.environ["DYLD_LIBRARY_PATH"] = f"{homebrew_lib}:" + os.environ.get("DYLD_LIBRARY_PATH", "")
    os.environ["PKG_CONFIG_PATH"] = f"{homebrew_pkg}:" + os.environ.get("PKG_CONFIG_PATH", "")

import json
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS

BASE_DIR = os.path.dirname(__file__)
TEMPLATE_DIR = os.path.join(BASE_DIR, "../pdf/templates")
DOMAIN_DIR = os.path.join(BASE_DIR, "../../domain/projeto_migracao")
OUTPUT_PDF = os.path.join(BASE_DIR, "../pdf/projeto_migracao.pdf")

def load_data():
    json_path = os.path.join(DOMAIN_DIR, "projeto_migracao.json")
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)

def build_html(data):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("projeto_migracao.html")

    project = data.get("project", {})
    groups = data.get("groups", [])
    roadmap = data.get("roadmap", [])

    migration_obj = None
    meta = data.get("project_metadata", {})
    if "migration_objective" in meta:
        content = meta["migration_objective"].get("content")
        if isinstance(content, list):
            migration_obj = content
        elif isinstance(content, str):
            migration_obj = [content]

    html = template.render(
        project=project,
        migration_objective=migration_obj,
        groups=groups,
        roadmap=roadmap,
    )
    return html

def main():
    data = load_data()
    html_string = build_html(data)

    html = HTML(string=html_string, base_url=TEMPLATE_DIR)
    css = CSS(filename=os.path.join(TEMPLATE_DIR, "pdf.css"))
    html.write_pdf(OUTPUT_PDF, stylesheets=[css])
    print("PDF gerado em:", OUTPUT_PDF)

if __name__ == "__main__":
    main()
