import os
import sys
# --- Ajuste automático de variáveis de ambiente para libs do Homebrew (macOS) ---
if sys.platform == "darwin":
    homebrew_lib = "/opt/homebrew/lib"
    homebrew_pkg = "/opt/homebrew/lib/pkgconfig"
    os.environ["DYLD_LIBRARY_PATH"] = f"{homebrew_lib}:" + os.environ.get("DYLD_LIBRARY_PATH", "")
    os.environ["PKG_CONFIG_PATH"] = f"{homebrew_pkg}:" + os.environ.get("PKG_CONFIG_PATH", "")

import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS

def sanitize_text(value):
    if isinstance(value, str):
        # Normaliza hífens
        value = (
            value
            .replace("\u2010", "-")
            .replace("\u2011", "-")
            .replace("\u2012", "-")
            .replace("\u2013", "-")
            .replace("\u2014", "-")
            .replace("\u2212", "-")
        )

        # Remove qualquer caractere invisível ou não imprimível
        value = "".join(
            ch for ch in value
            if ch.isprintable()
        )

        return value
    return value

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

    # DEBUG: confirma qual template está sendo carregado
    try:
        print("TEMPLATE_DIR:", TEMPLATE_DIR)
        print("Template carregado:", template.filename)
    except Exception as e:
        print("Erro ao inspecionar template:", e)

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

    # Histórico de alterações (governança documental)
    change_history = project_metadata.get("change_history") or []

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

    # ================================
    # NORMALIZA ESTRUTURA DE GRUPOS (compatível com JSON real)
    # ================================

    normalized_groups = []
    roadmap_grouped = {}

    for g in groups:
        grupo_nome = g.get("label") or g.get("nome") or g.get("name")
        # Ignora grupos técnicos ou placeholders
        if not grupo_nome:
            continue

        if str(grupo_nome).strip().upper() in [
            "SEM GRUPO DEFINIDO",
            "UNDEFINED",
            "NONE",
            "NULL",
            "IGNORADOS",
            "IGNORED"
        ]:
            continue
        grupo_seq = g.get("sequence")
        objetos = (
            g.get("objects")
            or g.get("objetos")
            or g.get("items")
            or []
        )

        normalized_objetos = []

        for obj in objetos:
            deployment_type = obj.get("deployment_type") or obj.get("tipo")
            if not deployment_type:
                continue
            deployment_type = str(deployment_type).strip().upper()
            codigo = obj.get("code") or obj.get("codigo")
            descricao = obj.get("name") or obj.get("description") or obj.get("descricao")
            object_type = obj.get("object_type")
            otm_table = obj.get("otm_table")
            sequence = obj.get("sequence")
            saved_query_id = obj.get("saved_query_id")
            responsavel = obj.get("owner") or "ITC"

            normalized_obj = {
                "codigo": codigo,
                "name": obj.get("name"),
                "description": obj.get("description"),
                "descricao": descricao,
                "tipo": deployment_type,
                "object_type": object_type,
                "otm_table": otm_table,
                "sequence": sequence,
                "saved_query_id": saved_query_id,
                "responsavel": responsavel
            }

            normalized_objetos.append(normalized_obj)

        # Adiciona grupo normalizado à estrutura final (inclui descrição do grupo)
        grupo_descricao = g.get("description") or g.get("descricao")

        normalized_groups.append({
            "nome": grupo_nome,
            "sequence": grupo_seq,
            "descricao": grupo_descricao,
            "objetos": normalized_objetos
        })

    # ---------------------------------------------------------
    # ROADMAP FIXED DEPLOYMENT TYPES (PADRÃO CORPORATIVO)
    # ---------------------------------------------------------

    ALLOWED_DEPLOYMENT_TYPES = [
        "MANUAL",
        "MIGRATION_PROJECT",
        "CSV",
        "DB_XML",
        "INTEGRATION"
    ]

    roadmap_grouped = {dtype: [] for dtype in ALLOWED_DEPLOYMENT_TYPES}

    for grupo in normalized_groups:
        for obj in grupo.get("objetos", []):

            deployment_type = (obj.get("tipo") or "").strip().upper()

            if deployment_type not in ALLOWED_DEPLOYMENT_TYPES:
                continue

            if deployment_type == "MANUAL":
                roadmap_grouped[deployment_type].append({
                    "responsavel": obj.get("responsavel"),
                    "tipo_migracao": "Técnica",
                    "grupo": grupo.get("nome"),
                    "descricao": obj.get("descricao"),
                    "otm_table": obj.get("otm_table")
                })

            elif deployment_type == "MIGRATION_PROJECT":
                roadmap_grouped[deployment_type].append({
                    "responsavel": obj.get("responsavel"),
                    "tipo_migracao": "Técnica",
                    "seq": obj.get("sequence"),
                    "id_migration_project": obj.get("codigo"),
                    "grupo": grupo.get("nome"),
                    "descricao": obj.get("descricao"),
                    "otm_table": obj.get("otm_table")
                })

            elif deployment_type == "CSV":
                roadmap_grouped[deployment_type].append({
                    "responsavel": obj.get("responsavel"),
                    "tipo_migracao": "Técnica",
                    "seq": obj.get("sequence"),
                    "grupo": grupo.get("nome"),
                    "descricao": obj.get("descricao"),
                    "otm_table": obj.get("otm_table")
                })

            elif deployment_type == "DB_XML":
                roadmap_grouped[deployment_type].append({
                    "responsavel": obj.get("responsavel"),
                    "tipo_migracao": "Técnica",
                    "seq": obj.get("sequence"),
                    "grupo": grupo.get("nome"),
                    "descricao": obj.get("descricao"),
                    "otm_table": obj.get("otm_table")
                })

            elif deployment_type == "INTEGRATION":
                roadmap_grouped[deployment_type].append({
                    "responsavel": obj.get("responsavel"),
                    "tipo_migracao": "Técnica",
                    "seq": obj.get("sequence"),
                    "grupo": grupo.get("nome"),
                    "descricao": obj.get("descricao"),
                    "otm_table": obj.get("otm_table")
                })

    # Remove deployment types vazios
    roadmap_grouped = {k: v for k, v in roadmap_grouped.items() if v}

    # Ordena roadmap por tipo e por sequência interna
    for tipo in roadmap_grouped:
        roadmap_grouped[tipo] = sorted(
            roadmap_grouped[tipo],
            key=lambda x: (
                x.get("grupo") or "",
                x.get("seq") is None,
                x.get("seq")
            )
        )

    roadmap_grouped = dict(sorted(roadmap_grouped.items()))

    # Outros campos que o painel pode usar
    # Exemplo: enums, ui, etc. (adapte conforme necessário)
    enums = data.get("enums", project_metadata.get("enums"))
    ui = data.get("ui", project_metadata.get("ui"))

    # Lookup funcional para status técnico
    STATUS_LOOKUP = {
        "IN_PROGRESS": "Em Andamento",
        "COMPLETED": "Concluído",
        "PENDING": "Pendente",
        "CANCELLED": "Cancelado",
        "FAILED": "Falhou"
    }

    # Monta objeto completo de projeto (fixo + metadata dinâmica)
    projeto_context = {}

    # Campos principais padronizados
    projeto_context.update({
        "nome": project.get("name"),
        "codigo": project.get("code"),
        "versao": project.get("version"),
        "responsavel": project.get("consultant"),
        "data_geracao": project_metadata.get("generated_at") or datetime.now().strftime("%d/%m/%Y"),
        "objetivo": migration_obj[0] if migration_obj else None,
        "escopo": project_metadata.get("scope"),
        "cliente": project_metadata.get("client"),
        # Status com interpretação funcional segura
        "status": (
            (lambda state: (
                STATUS_LOOKUP.get(state.get("overall_status"))
                if isinstance(state, dict)
                else STATUS_LOOKUP.get(state, state)
            ))(project.get("state"))
        ),
        "subtitulo": project_metadata.get("subtitle"),
        "logo_path": project_metadata.get("logo_path"),
        # URLs de ambiente (para renderização como hyperlink no template)
        "environment_source_url": sanitize_text(
            project.get("environment", {}).get("source")
            if isinstance(project.get("environment"), dict)
            else None
        ),
        "environment_target_url": sanitize_text(
            project.get("environment", {}).get("target")
            if isinstance(project.get("environment"), dict)
            else None
        ),
        "grupos": normalized_groups,
        "roadmap_dinamico": roadmap_grouped,
        "change_history": change_history
    })

    # Incorpora TODOS os campos adicionais do project
    for key, value in project.items():
        if key not in projeto_context:
            projeto_context[key] = value

    # Incorpora TODOS os campos adicionais do project_metadata
    for key, value in project_metadata.items():
        if key not in projeto_context:
            projeto_context[key] = value

    html = template.render(projeto=projeto_context)
    return html

def main():
    data = load_data()
    html_string = build_html(data)

    html = HTML(
        string=html_string.encode("utf-8").decode("utf-8"),
        base_url=TEMPLATE_DIR,
        encoding="utf-8"
    )
    css = CSS(filename=os.path.join(TEMPLATE_DIR, "pdf.css"))
    print("Gerando PDF em:", OUTPUT_PDF)
    html.write_pdf(OUTPUT_PDF, stylesheets=[css])
    print("PDF gerado em:", OUTPUT_PDF)

if __name__ == "__main__":
    main()
