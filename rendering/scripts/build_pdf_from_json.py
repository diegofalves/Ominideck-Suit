import glob
def get_object_cache_data(domain_name, otm_table, migration_item_name=None):
    """
    Busca o arquivo de cache correto para o objeto/tabela usando o objects_index.json e retorna os dados do cache.
    """
    index_path = os.path.abspath(os.path.join(BASE_DIR, '../../metadata/otm/cache/objects_index.json'))
    if not os.path.exists(index_path):
        return None
    with open(index_path, encoding="utf-8") as f:
        index_data = json.load(f)
    # Busca por todas as chaves que contenham o domínio e a tabela
    results = []
    for key, entries in index_data.get("objectLocatorByKey", {}).items():
        # Busca apenas pela tabela principal definida em otm_table
        if domain_name and otm_table and f"{domain_name}|{otm_table}" in key:
            for entry in entries:
                # Garante que a tabela do cache seja exatamente a principal
                if entry.get("table") != otm_table:
                    continue
                # Se migration_item_name for fornecido, filtra apenas se for MUITO diferente
                if migration_item_name:
                    entry_name = entry.get("migrationItemName")
                    # Permite se for igual, ou se um contém o outro (case-insensitive)
                    if entry_name and migration_item_name:
                        if migration_item_name.lower() != entry_name.lower() and migration_item_name.lower() not in entry_name.lower() and entry_name.lower() not in migration_item_name.lower():
                            continue
                file_path = os.path.abspath(os.path.join(BASE_DIR, '../../', entry["file"]))
                if os.path.exists(file_path):
                    with open(file_path, encoding="utf-8") as cache_file:
                        try:
                            cache_data = json.load(cache_file)
                            # Adiciona referência ao arquivo e info extra
                            results.append({
                                "file": entry["file"],
                                "rowNumber": entry.get("rowNumber"),
                                "tableRowNumber": entry.get("tableRowNumber"),
                                "migrationItemId": entry.get("migrationItemId"),
                                "migrationItemName": entry.get("migrationItemName"),
                                "migrationGroupId": entry.get("migrationGroupId"),
                                "table": entry.get("table"),
                                "domainName": entry.get("domainName"),
                                "cache_data": cache_data
                            })
                        except Exception as e:
                            continue
    return results if results else None
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
OUTPUT_HTML = os.path.join(BASE_DIR, "../pdf/projeto_migracao.debug.html")

def load_data():
    json_path = os.path.join(DOMAIN_DIR, "projeto_migracao.json")
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)

def build_html(data):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), auto_reload=True, cache_size=0)
    template = env.get_template("projeto_migracao_pdf_template.html.tpl")
    # NOTE: cache_size=0 garante reload efetivo do template em cada execução (evita cache de Jinja durante depuração)
    print("Jinja cache_size=0 (template reload forçado)")

    # DEBUG: confirma qual template está sendo carregado
    try:
        print("TEMPLATE_DIR:", TEMPLATE_DIR)
        print("Template carregado:", template.filename)
        try:
            import os
            from datetime import datetime
            mtime = os.path.getmtime(template.filename)
            print("Template mtime:", datetime.fromtimestamp(mtime).isoformat(timespec="seconds"))

            with open(template.filename, encoding="utf-8") as tf:
                tpl_text = tf.read()
            # Sanity check: verify if the moved Navigation block exists near the description area
            desc_pos = tpl_text.find("<!-- Descrição Técnica -->")
            nav_pos = tpl_text.find("Navegação OTM")
            print("Template sanity (Descrição Técnica pos):", desc_pos)
            print("Template sanity (Navegação OTM pos):", nav_pos)
            if desc_pos != -1 and nav_pos != -1:
                print("Template sanity (Nav after Desc):", nav_pos > desc_pos)
        except Exception as e:
            print("Erro ao checar mtime/sanity do template:", e)
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
            # JSON como fonte única de verdade
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

            # Preserva TODOS os campos originais do JSON
            normalized_obj = dict(obj)

            # Aplica highlight apenas no campo content, mantendo a estrutura original
            raw_query = obj.get("object_extraction_query")
            if isinstance(raw_query, dict) and raw_query.get("content"):
                raw_query = dict(raw_query)
                raw_query["content"] = highlight_sql(raw_query.get("content"))

            # Busca dados de cache para o objeto/tabela
            domain_name = obj.get("domainName") or obj.get("domain")
            migration_item_name = obj.get("migration_item_name") or obj.get("name")

            cache_results = None
            if domain_name and otm_table:
                cache_results = get_object_cache_data(domain_name, otm_table, migration_item_name)

                # --- AJUSTE: selected_columns do tipo TABELA.COLUNA ---
                selected_columns = obj.get("selected_columns")
                if cache_results and selected_columns:
                    # Para cada resultado de cache encontrado
                    for cache in cache_results:
                        # Busca as linhas do cache, tentando os caminhos mais comuns
                        rows = None
                        cache_data = cache.get("cache_data", {})
                        if (
                            cache_data.get("data")
                            and cache_data["data"].get("rows")
                        ):
                            rows = cache_data["data"]["rows"]
                        elif (
                            cache_data.get("tables")
                            and otm_table in cache_data["tables"]
                            and cache_data["tables"][otm_table].get("rows")
                        ):
                            rows = cache_data["tables"][otm_table]["rows"]
                        # Se houver linhas, reestrutura para usar apenas o nome da coluna
                        if rows:
                            new_rows = []
                            for row in rows:
                                new_row = {}
                                for col in selected_columns:
                                    # Se col for TABELA.COLUNA, extrai só COLUNA
                                    if "." in col:
                                        _, col_name = col.split(".", 1)
                                    else:
                                        col_name = col
                                    # Busca valor na linha
                                    val = row.get(col_name)
                                    new_row[col_name] = val if val is not None else ""
                                new_rows.append(new_row)
                            # Atualiza as linhas do cache para o template
                            if (
                                cache_data.get("data")
                                and cache_data["data"].get("rows")
                            ):
                                cache_data["data"]["rows"] = new_rows
                            elif (
                                cache_data.get("tables")
                                and otm_table in cache_data["tables"]
                                and cache_data["tables"][otm_table].get("rows")
                            ):
                                cache_data["tables"][otm_table]["rows"] = new_rows

            normalized_obj["object_cache_results"] = cache_results

            # DEBUG: printa se encontrou dados de cache
            if cache_results:
                print(f"[CACHE] Objeto: {normalized_obj.get('name') or normalized_obj.get('migration_item_name')} | Domínio: {domain_name} | Tabela: {otm_table}")
                print(f"[CACHE] Arquivos encontrados: {[c['file'] for c in cache_results]}")
                for c in cache_results:
                    print(f"[CACHE] Exemplo de dados: {str(c.get('cache_data'))[:500]}")

            # Normalizações e aliases padronizados para o template (alinhado 100% com o JSON)
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

    try:
        with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
            f.write(html_string)
        print("HTML debug gerado em:", OUTPUT_HTML)
    except Exception as e:
        print("Falha ao gravar HTML debug:", e)

    print("Base URL (templates):", TEMPLATE_DIR)
    print("CSS:", os.path.join(TEMPLATE_DIR, "pdf.css"))
    print("Gerando PDF em:", OUTPUT_PDF)

    # Garante caminhos absolutos para evitar problemas de resolução no WeasyPrint
    template_base = os.path.abspath(TEMPLATE_DIR)
    css_path = os.path.abspath(os.path.join(TEMPLATE_DIR, "pdf.css"))

    print("Base URL absoluto:", template_base)
    print("CSS absoluto:", css_path)

    html = HTML(
        string=html_string,
        base_url=template_base
    )

    css = CSS(filename=css_path)

    # ---------------------------------------------------------
    # WeasyPrint: overrides pontuais para evitar quebra artificial
    # entre cabeçalho do grupo e primeiro objeto.
    #
    # Sintoma: o título do grupo fica no fim da página anterior
    # e o primeiro objeto é empurrado inteiro para a próxima página,
    # gerando página "quase vazia".
    #
    # Causa típica: algum bloco está sendo tratado como "não quebrável"
    # (break-inside: avoid / page-break-inside: avoid), especialmente
    # quando há <pre> grandes.
    #
    # Estratégia: permitir quebra dentro de .group-item e dentro de <pre>,
    # e impedir quebra imediatamente após .group-head.
    # ---------------------------------------------------------
    weasyprint_fix_css = CSS(
        string="""
/* === WeasyPrint FIX: evitar páginas vazias entre grupo e 1º objeto === */

/* Mantém o cabeçalho do grupo grudado no conteúdo seguinte */
.group-head {
  break-after: avoid-page;
  page-break-after: avoid;
}

/* Permite que o item quebre entre páginas (não pode ser um bloco "inteiro") */
.group-item,
.group-item-first,
.object-status,
.object-extraction,
.object-technical,
.object-relationships {
  break-inside: auto;
  page-break-inside: auto;
}

/* Garante que o primeiro item não force início em nova página */
.group-item-first {
  break-before: auto;
  page-break-before: auto;
}

/* Se a introdução for grande, não trate como bloco indivisível */
.groups-intro,
.no-page-break {
  break-inside: auto;
  page-break-inside: auto;
}

/* Blocos de código precisam quebrar e fazer wrap */
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
    print("PDF gerado em:", OUTPUT_PDF)

if __name__ == "__main__":
    main()
