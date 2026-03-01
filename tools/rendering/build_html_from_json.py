#!/usr/bin/env python3
"""
OmniDeck - Build HTML from JSON
Gera visualização HTML rápida do documento de migração
Idêntico ao PDF mas para navegador
"""

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

    # Camada 3: fallback por domínio + tabela + sequência + grupo
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
import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

# Helper for SQL keyword highlighting
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
TEMPLATE_DIR = os.path.join(BASE_DIR, "../../rendering/html/templates")
DOMAIN_DIR = os.path.join(BASE_DIR, "../../domain/projeto_migracao")
OUTPUT_HTML = os.path.join(BASE_DIR, "../../rendering/html/documento_migracao_standalone.html")

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
    template = env.get_template("documento_migracao_html_template.html.tpl")
    print_progress(10, "Carregando template HTML")
    print_progress(20, "Template carregado")

    # Copia profunda para evitar mutações
    import copy
    data = copy.deepcopy(data)

    # Lógica de compatibilidade igual ao painel (backend) e ao PDF
    project = data.get("project", {})
    project_metadata = data.get("project_metadata", {})
    groups = data.get("groups", [])

    # Garante que project_metadata está dentro de project
    project["project_metadata"] = project_metadata

    # Atalhos para campos principais
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

    # NORMALIZA ESTRUTURA DE GRUPOS
    normalized_groups = []
    roadmap_grouped = {}

    for g in groups:
        grupo_nome = g.get("label") or g.get("nome") or g.get("name")
        if not grupo_nome:
            continue

        if str(grupo_nome).strip().upper() in [
            "SEM GRUPO DEFINIDO", "UNDEFINED", "NONE",
            "NULL", "IGNORADOS", "IGNORED"
        ]:
            continue

        grupo_seq = g.get("sequence")
        objetos = (g.get("objects") or g.get("objetos") or g.get("items") or [])
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
            otm_primary_key = obj.get("otm_primary_key")

            if not selected_columns and otm_primary_key:
                if isinstance(otm_primary_key, list):
                    selected_columns = [col for col in otm_primary_key]
                elif isinstance(otm_primary_key, str):
                    selected_columns = [otm_primary_key]

            # Busca cache para schema
            if not selected_columns:
                domain_name_tmp = obj.get("domainName") or obj.get("domain")
                otm_table_tmp = obj.get("otmTable") or obj.get("otm_table")
                migration_item_name_tmp = obj.get("migration_item_name") or obj.get("name")
                migration_group_id_tmp = g.get("group_id") or g.get("nome") or g.get("label")
                sequence_tmp = obj.get("sequence")
                cache_results_tmp = get_object_cache_data(domain_name_tmp, otm_table_tmp, migration_item_name_tmp, migration_group_id_tmp, sequence_tmp)
                if cache_results_tmp and len(cache_results_tmp) > 0:
                    cache_data_tmp = cache_results_tmp[0].get("cache_data", {})
                    schema_cols = []
                    if cache_data_tmp.get("tables") and otm_table_tmp in cache_data_tmp["tables"]:
                        schema = cache_data_tmp["tables"][otm_table_tmp].get("schema", {})
                        schema_cols = schema.get("columns", [])
                    elif cache_data_tmp.get("schema"):
                        schema_cols = cache_data_tmp["schema"].get("columns", [])
                    if schema_cols:
                        selected_columns = schema_cols

            # Query de extração
            raw_query = obj.get("object_extraction_query")
            if isinstance(raw_query, dict) and raw_query.get("content"):
                raw_query = dict(raw_query)
                raw_query["content"] = highlight_sql(raw_query.get("content"))
            else:
                raw_query = {"language": "SQL", "content": ""}

            # Cache de dados
            if domain_name and otm_table and selected_columns:
                migration_group_id = g.get("group_id") or g.get("nome") or g.get("label")
                sequence = obj.get("sequence")
                cache_results = get_object_cache_data(domain_name, otm_table, migration_item_name, migration_group_id, sequence)
                if not cache_results:
                    cache_results = [{
                        "file": None,
                        "cache_data": {
                            "data": {"rows": []},
                            "tables": {otm_table: {"rows": []}}
                        }
                    }]
                
                # Filtragem de colunas
                for cache in cache_results or []:
                    cache_data = cache.get("cache_data", {})
                    rows = None
                    if cache_data.get("data") and cache_data["data"].get("rows"):
                        rows = cache_data["data"]["rows"]
                    elif cache_data.get("tables") and otm_table in cache_data["tables"] and cache_data["tables"][otm_table].get("rows"):
                        rows = cache_data["tables"][otm_table]["rows"]

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
                            filtered_rows.append(filtered_row)
                        
                        if cache_data.get("data") and cache_data["data"].get("rows"):
                            cache_data["data"]["rows"] = filtered_rows
                        elif cache_data.get("tables") and otm_table in cache_data["tables"] and cache_data["tables"][otm_table].get("rows"):
                            cache_data["tables"][otm_table]["rows"] = filtered_rows

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

            normalized_objetos.append(normalized_obj)

        grupo_descricao = g.get("description") or g.get("descricao")
        normalized_groups.append({
            "nome": grupo_nome,
            "sequence": grupo_seq,
            "descricao": grupo_descricao,
            "objetos": normalized_objetos
        })

    # ROADMAP
    ALLOWED_DEPLOYMENT_TYPES = ["MANUAL", "MIGRATION_PROJECT", "CSV", "DB_XML", "INTEGRATION"]
    roadmap_grouped = {dtype: [] for dtype in ALLOWED_DEPLOYMENT_TYPES}

    for grupo in normalized_groups:
        for obj in grupo.get("objetos", []):
            deployment_type = (obj.get("tipo") or "").strip().upper()
            if deployment_type not in ALLOWED_DEPLOYMENT_TYPES:
                continue

            roadmap_grouped[deployment_type].append({
                "responsavel": obj.get("responsavel"),
                "tipo_migracao": "Técnica",
                "seq": obj.get("sequence"),
                "grupo": grupo.get("nome"),
                "descricao": obj.get("descricao"),
                "otm_table": obj.get("otm_table")
            })

    roadmap_grouped = {k: v for k, v in roadmap_grouped.items() if v}

    for tipo in roadmap_grouped:
        roadmap_grouped[tipo] = sorted(
            roadmap_grouped[tipo],
            key=lambda x: (x.get("grupo") or "", x.get("seq") is None, x.get("seq"))
        )

    roadmap_grouped = dict(sorted(roadmap_grouped.items()))

    STATUS_LOOKUP = {
        "IN_PROGRESS": "Em Andamento",
        "COMPLETED": "Concluído",
        "PENDING": "Pendente",
        "CANCELLED": "Cancelado",
        "FAILED": "Falhou"
    }

    projeto_context = {}
    projeto_context.update({
        "nome": sanitize_text(project.get("name")),
        "codigo": project.get("code"),
        "versao": project.get("version"),
        "responsavel": sanitize_text(project.get("consultant")),
        "data_geracao": project_metadata.get("generated_at") or datetime.now().strftime("%d/%m/%Y"),
        "objetivo": sanitize_text(migration_obj[0]) if migration_obj else None,
        "escopo": sanitize_text(project_metadata.get("scope")),
        "cliente": sanitize_text(project_metadata.get("client")),
        "status": (
            (lambda state: (
                STATUS_LOOKUP.get(state.get("overall_status"))
                if isinstance(state, dict)
                else STATUS_LOOKUP.get(state, state)
            ))(project.get("state"))
        ),
        "subtitulo": sanitize_text(project_metadata.get("subtitle")),
        "logo_path": project_metadata.get("logo_path"),
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

    for key, value in project.items():
        if key not in projeto_context:
            projeto_context[key] = value

    for key, value in project_metadata.items():
        if key not in projeto_context:
            projeto_context[key] = value

    print_progress(60, "Renderizando HTML")
    html = template.render(projeto=projeto_context)
    print_progress(70, "HTML renderizado")
    return html

def main():
    print_progress(0, "Iniciando geração HTML")
    data = load_data()
    print_progress(30, "Dados carregados")
    html_string = build_html(data)

    # Inline o CSS no HTML para visualização standalone
    css_path = os.path.join(TEMPLATE_DIR, "html.css")
    with open(css_path, "r", encoding="utf-8") as f:
        css_content = f.read()
    
    # Injeta CSS inline
    html_string = html_string.replace(
        '<link rel="stylesheet" href="html.css">',
        f'<style>{css_content}</style>'
    )

    print_progress(80, "Salvando HTML")
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_string)
    
    print_progress(100, f"HTML gerado: {OUTPUT_HTML}")
    print(f"\n✅ Arquivo pronto para visualização: {OUTPUT_HTML}")
    print(f"💡 Abra no navegador ou use: open '{OUTPUT_HTML}'")

if __name__ == "__main__":
    main()
