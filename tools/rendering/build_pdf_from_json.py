import glob
import sys
import time
import re
from pathlib import Path

# Funções auxiliares para padronizar nomes (slugify, short_slug)
def _slugify(value):
    value = str(value or "").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")

def _short_slug(value, max_len):
    slug = _slugify(value)
    if len(slug) <= max_len:
        return slug
    return slug[:max_len].rstrip("_") or slug[:max_len]

# Função para montar o nome do arquivo de cache
def build_cache_filename(domain_name, table_name, migration_group_id, migration_item_name, sequence):
    domain_token = _slugify(domain_name or "NO_DOMAIN")
    table_token = _slugify(table_name or "NO_TABLE")
    group_token = _short_slug(migration_group_id or "NO_GROUP", 18)
    name_token = _short_slug(migration_item_name or "ITEM", 24)
    sequence_token = re.sub(r"[^0-9]+", "", str(sequence or "").strip()) or "0"
    filename = f"{domain_token}_{table_token}_{name_token}_{sequence_token}_{group_token}.json"
    return filename

def _load_cache_file(file_path):
    try:
        with open(file_path, encoding="utf-8") as f:
            return [{"file": str(file_path), "cache_data": json.load(f)}]
    except Exception:
        return None

def get_object_cache_data(domain_name, otm_table, migration_item_name=None, migration_group_id=None, sequence=None):
    cache_dir = Path(BASE_DIR) / "../../metadata/otm/cache/objects"
    if not cache_dir.is_dir():
        return None

    filename = build_cache_filename(domain_name, otm_table, migration_group_id, migration_item_name, sequence)

    # Camada 1: match exato (esperado em ambientes case-insensitive como macOS)
    exact_path = cache_dir / filename
    if exact_path.exists():
        return _load_cache_file(exact_path)

    # Camada 2: match case-insensitive (Linux com arquivos em UPPERCASE)
    filename_lower = filename.lower()
    for f in cache_dir.iterdir():
        if f.name.lower() == filename_lower:
            return _load_cache_file(f)

    # Camada 3: fallback por domínio + tabela + sequência + grupo (ignora variação no migration_item_name)
    domain_slug = _slugify(domain_name or "")
    table_slug = _slugify(otm_table or "")
    group_slug = _short_slug(migration_group_id or "", 18).lower()
    seq_str = re.sub(r"[^0-9]+", "", str(sequence or "").strip()) or "0"
    prefix = f"{domain_slug}_{table_slug}_"
    suffix = f"_{seq_str}_{group_slug}.json"
    for f in cache_dir.iterdir():
        fname_lower = f.name.lower()
        if fname_lower.startswith(prefix) and fname_lower.endswith(suffix):
            return _load_cache_file(f)

    return None
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

# Helper for SQL keyword highlighting
import re

def highlight_sql(sql_text):
    if not isinstance(sql_text, str):
        return sql_text

    keywords = [
        "SELECT", "FROM", "WHERE", "AND", "OR",
        "ORDER BY", "GROUP BY", "NOT LIKE",
        "INNER JOIN", "LEFT JOIN", "RIGHT JOIN",
        "ON", "IN", "EXISTS"
    ]

    for kw in sorted(keywords, key=len, reverse=True):
        pattern = r"\b" + re.escape(kw) + r"\b"
        sql_text = re.sub(
            pattern,
            f"<span class='sql-keyword'>{kw}</span>",
            sql_text,
            flags=re.IGNORECASE
        )

    return sql_text

def sanitize_text(value):
    if isinstance(value, str):
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
OUTPUT_PDF = os.path.join(BASE_DIR, "../pdf/documento_migracao.pdf")
OUTPUT_HTML = os.path.join(BASE_DIR, "../pdf/documento_migracao.debug.html")

def load_data():
    json_path = os.path.join(DOMAIN_DIR, "documento_migracao.json")
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)

def print_progress(percent, milestone=None):
    bar_len = 40
    filled_len = int(bar_len * percent // 100)
    bar = '█' * filled_len + '-' * (bar_len - filled_len)
    if milestone:
        sys.stdout.write(f"\r[{bar}] {percent:3d}% - {milestone}   ")
    else:
        sys.stdout.write(f"\r[{bar}] {percent:3d}%   ")
    sys.stdout.flush()
    if percent == 100:
        print()

def build_html(data):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), auto_reload=True, cache_size=0)
    template = env.get_template("documento_migracao_pdf_template.html.tpl")

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
            deployment_type = obj.get("deployment_type")
            if not deployment_type:
                continue
            deployment_type = str(deployment_type).strip().upper()

            codigo = obj.get("migration_item_id")
            descricao = obj.get("description")
            object_type = obj.get("object_type")
            otm_table = obj.get("otm_table")
            sequence = obj.get("sequence")
            saved_query_id = obj.get("saved_query_id")
            responsavel = obj.get("responsible")

            normalized_obj = dict(obj)

            domain_name = obj.get("domainName") or obj.get("domain")
            migration_item_name = obj.get("migration_item_name") or obj.get("name")

            cache_results = None

            selected_columns = obj.get("selected_columns")

            simulated_query = obj.get("simulatedExtractionQuery")
            otm_primary_key = obj.get("otm_primary_key")

            # Se não houver selected_columns, usa a primary key como padrão
            if not selected_columns and otm_primary_key:
                if isinstance(otm_primary_key, list):
                    selected_columns = [col for col in otm_primary_key]
                elif isinstance(otm_primary_key, str):
                    selected_columns = [otm_primary_key]

            # Se ainda não houver selected_columns, tenta pegar todas as colunas do schema do cache
            if not selected_columns:
                # Busca cache para pegar schema
                domain_name_tmp = obj.get("domainName") or obj.get("domain")
                otm_table_tmp = obj.get("otmTable") or obj.get("otm_table")
                migration_item_name_tmp = obj.get("migration_item_name") or obj.get("name")
                migration_group_id_tmp = g.get("group_id") or g.get("nome") or g.get("label")
                sequence_tmp = obj.get("sequence")
                cache_results_tmp = get_object_cache_data(domain_name_tmp, otm_table_tmp, migration_item_name_tmp, migration_group_id_tmp, sequence_tmp)
                if cache_results_tmp and len(cache_results_tmp) > 0:
                    cache_data_tmp = cache_results_tmp[0].get("cache_data", {})
                    # Tenta pegar schema das tabelas
                    schema_cols = []
                    if cache_data_tmp.get("tables") and otm_table_tmp in cache_data_tmp["tables"]:
                        schema = cache_data_tmp["tables"][otm_table_tmp].get("schema", {})
                        schema_cols = schema.get("columns", [])
                    elif cache_data_tmp.get("schema"):
                        schema_cols = cache_data_tmp["schema"].get("columns", [])
                    if schema_cols:
                        selected_columns = schema_cols

            # Sempre exibe object_extraction_query.content no bloco 'QUERY DE EXTRAÇÃO'
            raw_query = obj.get("object_extraction_query")
            if isinstance(raw_query, dict) and raw_query.get("content"):
                raw_query = dict(raw_query)
                raw_query["content"] = highlight_sql(raw_query.get("content"))
            else:
                raw_query = {"language": "SQL", "content": ""}

            # simulatedExtractionQuery será usado apenas para renderizar a tabela de dados (não para exibir no bloco de query)


            # Garante que a tabela de extração será renderizada mesmo se não houver dados, desde que selected_columns esteja presente
            if domain_name and otm_table and selected_columns:
                migration_group_id = g.get("group_id") or g.get("nome") or g.get("label")
                sequence = obj.get("sequence")
                cache_results = get_object_cache_data(domain_name, otm_table, migration_item_name, migration_group_id, sequence)
                # Se não houver cache_results, cria um resultado vazio para garantir renderização da tabela
                if not cache_results:
                    cache_results = [{
                        "file": None,
                        "rowNumber": None,
                        "tableRowNumber": None,
                        "migrationItemId": None,
                        "migrationItemName": migration_item_name,
                        "migrationGroupId": migration_group_id,
                        "table": otm_table,
                        "domainName": domain_name,
                        "cache_data": {
                            "data": {"rows": []},
                            "tables": {otm_table: {"rows": []}}
                        }
                    }]
                # Nova lógica: simula JOINs simples para selected_columns que referenciam subtabelas
                for cache in cache_results or []:
                    cache_data = cache.get("cache_data", {})
                    # Busca linhas da tabela principal
                    rows = None
                    if cache_data.get("data") and cache_data["data"].get("rows"):
                        rows = cache_data["data"]["rows"]
                    elif cache_data.get("tables") and otm_table in cache_data["tables"] and cache_data["tables"][otm_table].get("rows"):
                        rows = cache_data["tables"][otm_table]["rows"]

                    # Indexa subtabelas por nome
                    subtables = {}
                    if cache_data.get("tables"):
                        for tbl_name, tbl_data in cache_data["tables"].items():
                            if tbl_data.get("rows"):
                                subtables[tbl_name] = tbl_data["rows"]

                    filtered_rows = []
                    if rows:
                        for row in rows:
                            filtered_row = {}
                            for col in selected_columns:
                                if "." in col:
                                    tbl, col_name = col.split(".", 1)
                                    if tbl == otm_table:
                                        # Fallback: se col_name não existir, tenta pegar o valor bruto
                                        filtered_row[col] = row.get(col_name, row.get(col, ""))
                                    elif tbl in subtables:
                                        main_keys = [k for k in row.keys() if k.endswith("_GID") or k.endswith("_ID") or k.endswith("_XID")]
                                        match = None
                                        for sub_row in subtables[tbl]:
                                            for key in main_keys:
                                                if key in sub_row and row[key] == sub_row[key]:
                                                    match = sub_row
                                                    break
                                            if match:
                                                break
                                        filtered_row[col] = match.get(col_name, match.get(col, "")) if match else ""
                                    else:
                                        filtered_row[col] = row.get(col, "")
                                else:
                                    filtered_row[col] = row.get(col, "")
                            # Sempre adiciona a linha, mesmo se estiver parcialmente vazia
                            filtered_rows.append(filtered_row)
                        # Atualiza as linhas filtradas no cache_data
                        if cache_data.get("data") and cache_data["data"].get("rows"):
                            cache_data["data"]["rows"] = filtered_rows
                        elif cache_data.get("tables") and otm_table in cache_data["tables"] and cache_data["tables"][otm_table].get("rows"):
                            cache_data["tables"][otm_table]["rows"] = filtered_rows


            # Garante que selected_columns sempre está presente no objeto normalizado
            normalized_obj["selected_columns"] = selected_columns
            normalized_obj["object_cache_results"] = cache_results

            normalized_obj.update({
                "codigo": codigo,
                "name": obj.get("name"),
                "description": descricao,
                "descricao": descricao,
                "deployment_type": deployment_type,
                "tipo": deployment_type,
                "object_type": object_type,
                "otm_table": otm_table,
                "sequence": sequence,
                "saved_query_id": saved_query_id,
                "responsavel": responsavel,
                "domain": obj.get("domain"),
                "domainName": obj.get("domainName"),
                "migration_item_name": obj.get("migration_item_name"),
                "auto_generated": obj.get("auto_generated"),
                "auto_source": obj.get("auto_source"),
                "notes": obj.get("notes"),
                "identifiers": obj.get("identifiers"),
                "data": obj.get("data"),
                "status": obj.get("status"),
                "object_extraction_query": raw_query,
                "technical_content": obj.get("technical_content"),
                "otm_subtables": obj.get("otm_subtables"),
                "otm_related_tables": obj.get("otm_related_tables"),
                "otm_navigation_path_en": obj.get("otm_navigation_path_en"),
                "otm_navigation_source": obj.get("otm_navigation_source"),
                "otm_navigation_equivalent_table": obj.get("otm_navigation_equivalent_table"),
                "otm_navigation_equivalence_confidence": obj.get("otm_navigation_equivalence_confidence")
            })

            # ...removido bloco de debug...
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
        "nome": sanitize_text(project.get("name")),
        "codigo": project.get("code"),  # NÃO sanitizar código
        "versao": project.get("version"),
        "responsavel": sanitize_text(project.get("consultant")),
        "data_geracao": project_metadata.get("generated_at") or datetime.now().strftime("%d/%m/%Y"),
        "objetivo": sanitize_text(migration_obj[0]) if migration_obj else None,
        "escopo": sanitize_text(project_metadata.get("scope")),
        "cliente": sanitize_text(project_metadata.get("client")),
        # Status com interpretação funcional segura
        "status": (
            (lambda state: (
                STATUS_LOOKUP.get(state.get("overall_status"))
                if isinstance(state, dict)
                else STATUS_LOOKUP.get(state, state)
            ))(project.get("state"))
        ),
        "subtitulo": sanitize_text(project_metadata.get("subtitle")),
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

    try:
        with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
            f.write(html_string)
    except Exception as e:
        print(f"⚠️  Falha ao gravar HTML debug: {e}")

    template_base = os.path.abspath(TEMPLATE_DIR)
        css_path = os.path.abspath(os.path.join(TEMPLATE_DIR, "pdf.css"))

        html = HTML(
                string=html_string,
                base_url=template_base
        )

        css = CSS(filename=css_path)

        weasyprint_fix_css = CSS(
                string="""
/* === WeasyPrint FIX: evitar páginas vazias entre grupo e 1º objeto === */

.group-head {
    break-after: avoid-page;
    page-break-after: avoid;
}
.group-item,
.group-item-first,
.object-status,
.object-extraction,
.object-technical,
.object-relationships {
    break-inside: auto;
    page-break-inside: auto;
}
.group-item-first {
    break-before: auto;
    page-break-before: auto;
}
.groups-intro,
.no-page-break {
    break-inside: auto;
    page-break-inside: auto;
}
pre,
code {
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    word-break: break-word;
}
pre {
    max-width: 100%;
}
"""
        )

        html.write_pdf(
                OUTPUT_PDF,
                stylesheets=[css, weasyprint_fix_css]
        )
        print_progress(100, f"PDF gerado: {OUTPUT_PDF}")

if __name__ == "__main__":
        main()
(f"✅ 