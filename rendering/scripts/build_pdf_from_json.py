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
    template = env.get_template("projeto_migracao_pdf_template.html.tpl")

    # Copia profunda para evitar mutações
    import copy
    data = copy.deepcopy(data)

    # Lógica de compatibilidade igual ao painel (backend)
    project = data.get("project", {})
    project_metadata = data.get("project_metadata", {})
    groups = data.get("groups", [])

    # Garante que project_metadata está dentro de project
    project["project_metadata"] = project_metadata

    # Atalhos para campos principais
    # Código, nome, versão, consultor, ambientes
    project.setdefault("code", project_metadata.get("code"))
    project.setdefault("name", project_metadata.get("name"))
    project.setdefault("version", project_metadata.get("version"))
    project.setdefault("consultant", project_metadata.get("consultant"))
    project.setdefault("environment", project_metadata.get("environment"))

    # Estado do projeto
    if "state" in data:
        project["state"] = data["state"]
    elif "state" in project_metadata:
        project["state"] = project_metadata["state"]

    # Roadmap: prioriza raiz, depois project_metadata
    roadmap = data.get("roadmap")
    if not roadmap:
        roadmap = project_metadata.get("roadmap")
    if not roadmap:
        roadmap = []

    # Objetivo de migração
    migration_obj = None
    migration_objective = project_metadata.get("migration_objective")
    if migration_objective:
        content = migration_objective.get("content")
        if isinstance(content, list):
            migration_obj = content
        elif isinstance(content, str):
            migration_obj = [content]

    # Grupos: se não vier na raiz, tenta em project_metadata
    if not groups:
        groups = project_metadata.get("groups", [])

    # Outros campos que o painel pode usar
    # Exemplo: enums, ui, etc. (adapte conforme necessário)
    enums = data.get("enums", project_metadata.get("enums"))
    ui = data.get("ui", project_metadata.get("ui"))

    html = template.render(
        project=project,
        migration_objective=migration_obj,
        groups=groups,
        roadmap=roadmap,
        project_metadata=project_metadata,
        enums=enums,
        ui=ui,
        # Adicione outros campos relevantes aqui se necessário
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
