import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from ui.backend.deployment_policy import deployment_type_for_table
from ui.backend.domain_stats import object_domain_map, table_domain_map

BASE_DIR = Path(__file__).resolve().parents[2]
PROJECT_PATH = BASE_DIR / "domain/projeto_migracao/projeto_migracao.json"
DOMAIN_TABLE_STATS_PATH = BASE_DIR / "metadata" / "otm" / "domain_table_statistics.json"

GROUP_ZERO_ID = "SEM_GRUPO"
LEGACY_GROUP_ZERO_IDS = {"GROUP_0", GROUP_ZERO_ID}
GROUP_ZERO_LABEL = "Sem Grupo Definido"
GROUP_ZERO_DESCRIPTION = "Objetos sem grupo definido sao agrupados automaticamente aqui."
GROUP_ZERO_SEQUENCE = 0
IGNORED_GROUP_ID = "IGNORADOS"
IGNORED_GROUP_LABEL = "Ignorados"
IGNORED_GROUP_DESCRIPTION = (
    "Objetos marcados para ignorar cobertura automatica de tabela."
)
IGNORED_GROUP_SEQUENCE = 999
MIGRATION_GROUP_ID_KEY = "migration_group_id"
MIGRATION_ITEM_ID_KEY = "migration_item_id"
MIGRATION_ITEM_NAME_KEY = "migration_item_name"
ACTIVE_MIGRATION_GROUP_ID_KEY = "active_migration_group_id"
LOGICAL_REQUIRED_IDENTIFIERS = {
    "SAVED_QUERY": ("query_name",),
    "AGENT": ("agent_gid",),
    "FINDER_SET": ("finder_set_gid",),
    "RATE": ("rate_offering_gid",),
    "EVENT_GROUP": ("event_group_gid",),
}
FROM_CLAUSE_TERMINATORS = {
    "WHERE",
    "GROUP",
    "ORDER",
    "HAVING",
    "CONNECT",
    "START",
    "UNION",
    "MINUS",
    "INTERSECT",
    "MODEL",
}


def _as_object_list(value):
    if not isinstance(value, list):
        return []
    return [obj for obj in value if isinstance(obj, dict)]


def _normalize_name(value: Any) -> str:
    return str(value or "").strip().upper()


def _is_truthy(value: Any) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "on", "yes", "y"}


def _to_int(value: Any) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return 0


def _normalize_table_list(raw_values: Any) -> List[str]:
    values: List[Any] = []
    if isinstance(raw_values, list):
        values = raw_values
    elif isinstance(raw_values, str):
        values = [part.strip() for part in raw_values.split(",")]

    normalized: List[str] = []
    seen: Set[str] = set()
    for value in values:
        table_name = _normalize_name(value)
        if not table_name or table_name in seen:
            continue
        normalized.append(table_name)
        seen.add(table_name)
    return normalized


def _slug_token(value: Any, fallback: str) -> str:
    normalized = _normalize_name(value)
    slug = re.sub(r"[^A-Z0-9]+", "_", normalized).strip("_")
    return slug or fallback


def _build_migration_item_id(group_id: str, item: Dict[str, Any]) -> str:
    group_token = _slug_token(group_id, "NO_GROUP")
    table_token = _slug_token(
        item.get("otm_table") or item.get("object_type"),
        "NO_TABLE",
    )
    name_token = _slug_token(
        item.get("name") or item.get(MIGRATION_ITEM_NAME_KEY),
        "NO_NAME",
    )
    sequence_token = str(max(_to_int(item.get("sequence")), 0))
    return (
        f"MIGRATION_ITEM."
        f"{group_token}.{table_token}.{name_token}.{sequence_token}"
    )


def _split_ignored_objects(
    objects: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    regular_objects: List[Dict[str, Any]] = []
    ignored_objects: List[Dict[str, Any]] = []
    for obj in objects:
        if not isinstance(obj, dict):
            continue
        if _is_truthy(obj.get("ignore_table")):
            obj["ignore_table"] = True
            ignored_objects.append(obj)
            continue
        regular_objects.append(obj)
    return regular_objects, ignored_objects


def _normalize_migration_group_item_aliases(data: Dict[str, Any]) -> None:
    groups = data.get("groups", [])
    if not isinstance(groups, list):
        return

    valid_group_ids: List[str] = []
    for group in groups:
        if not isinstance(group, dict):
            continue

        normalized_group_id = _normalize_name(
            group.get(MIGRATION_GROUP_ID_KEY) or group.get("group_id")
        )
        if not normalized_group_id:
            continue

        group["group_id"] = normalized_group_id
        group[MIGRATION_GROUP_ID_KEY] = normalized_group_id
        valid_group_ids.append(normalized_group_id)

        migration_items = _as_object_list(group.get("objects"))
        group["objects"] = migration_items

        for item in migration_items:
            if not isinstance(item, dict):
                continue

            current_item_id = str(item.get(MIGRATION_ITEM_ID_KEY) or "").strip()
            if current_item_id:
                item[MIGRATION_ITEM_ID_KEY] = current_item_id
            else:
                item[MIGRATION_ITEM_ID_KEY] = _build_migration_item_id(
                    normalized_group_id, item
                )

            migration_item_name = str(
                item.get("name") or item.get(MIGRATION_ITEM_NAME_KEY) or ""
            ).strip()
            if migration_item_name:
                item["name"] = migration_item_name
                item[MIGRATION_ITEM_NAME_KEY] = migration_item_name

    normalized_active_group_id = _normalize_name(
        data.get(ACTIVE_MIGRATION_GROUP_ID_KEY) or data.get("active_group_id")
    )
    if normalized_active_group_id and normalized_active_group_id in set(valid_group_ids):
        data["active_group_id"] = normalized_active_group_id
        data[ACTIVE_MIGRATION_GROUP_ID_KEY] = normalized_active_group_id
        return

    fallback_active_group_id = _normalize_name(data.get("active_group_id"))
    if fallback_active_group_id and fallback_active_group_id in set(valid_group_ids):
        data[ACTIVE_MIGRATION_GROUP_ID_KEY] = fallback_active_group_id
        return

    if valid_group_ids:
        data[ACTIVE_MIGRATION_GROUP_ID_KEY] = valid_group_ids[0]


def _load_domain_statistics_tables() -> List[str]:
    return sorted(table_domain_map().keys())


def _collect_existing_otm_tables(data: Dict[str, Any]) -> Set[str]:
    existing: Set[str] = set()
    groups = data.get("groups", [])
    if not isinstance(groups, list):
        return existing

    for group in groups:
        if not isinstance(group, dict):
            continue
        objects = group.get("objects", [])
        if not isinstance(objects, list):
            continue

        for obj in objects:
            if not isinstance(obj, dict):
                continue
            if _is_truthy(obj.get("ignore_table")):
                continue
            object_type = _normalize_name(obj.get("object_type"))
            otm_table = _normalize_name(obj.get("otm_table"))
            if object_type:
                existing.add(object_type)
            if otm_table:
                existing.add(otm_table)

    return existing


def _collect_ignored_otm_tables(data: Dict[str, Any]) -> Set[str]:
    ignored: Set[str] = set()
    groups = data.get("groups", [])
    if not isinstance(groups, list):
        return ignored

    for group in groups:
        if not isinstance(group, dict):
            continue
        objects = group.get("objects", [])
        if not isinstance(objects, list):
            continue

        for obj in objects:
            if not isinstance(obj, dict):
                continue
            if not _is_truthy(obj.get("ignore_table")):
                continue
            table_name = _normalize_name(obj.get("object_type")) or _normalize_name(
                obj.get("otm_table")
            )
            if table_name:
                ignored.add(table_name)

    return ignored


def _build_auto_group_zero_object(table_name: str, sequence: int, domain_name: Optional[str] = None) -> Dict[str, Any]:
    auto_name = f"{table_name} (AUTO)"
    identifiers: Dict[str, str] = {}
    saved_query: Optional[Dict[str, str]] = None
    normalized_domain = _normalize_name(domain_name)
    deployment_type = deployment_type_for_table(table_name, normalized_domain)

    if table_name in LOGICAL_REQUIRED_IDENTIFIERS:
        for identifier in LOGICAL_REQUIRED_IDENTIFIERS[table_name]:
            identifiers[identifier] = f"AUTO_{table_name}"
    if table_name == "SAVED_QUERY":
        saved_query = {"sql": "SELECT 1 FROM DUAL"}

    payload: Dict[str, Any] = {
        "name": auto_name,
        "description": (
            "Objeto adicionado automaticamente para garantir cobertura canônica "
            "das tabelas presentes em domain_table_statistics.json."
        ),
        "object_type": table_name,
        "otm_table": table_name,
        "otm_related_tables": [],
        "otm_subtables": [],
        "deployment_type": deployment_type,
        "deployment_type_user_defined": False,
        "sequence": sequence,
        "responsible": "",
        "status": {
            "documentation": "PENDING",
            "migration_project": "PENDING",
            "export": "PENDING",
            "deploy": "PENDING",
            "validation": "PENDING",
            "deployment": "PENDING",
        },
        "object_extraction_query": {"language": "SQL", "content": ""},
        "technical_content": {"type": "NONE", "content": ""},
        "identifiers": identifiers,
        "data": {},
        "notes": "",
        "auto_generated": True,
        "auto_source": "domain_table_statistics.json",
    }
    if saved_query is not None:
        payload["saved_query"] = saved_query
    if normalized_domain:
        payload["domainName"] = normalized_domain
        payload["domain"] = normalized_domain
        payload["name"] = f"{table_name} ({normalized_domain} - AUTO)"

    return payload


def _resolve_object_extraction_query(obj: Dict[str, Any]) -> Dict[str, str]:
    if not isinstance(obj, dict):
        return {"language": "SQL", "content": ""}

    extraction_query = obj.get("object_extraction_query")
    if isinstance(extraction_query, dict):
        language = str(
            extraction_query.get("language") or extraction_query.get("type") or "SQL"
        ).strip().upper() or "SQL"
        content = str(extraction_query.get("content") or "").strip()
        if content:
            return {"language": language, "content": content}

    saved_query = obj.get("saved_query")
    if isinstance(saved_query, dict):
        sql = str(saved_query.get("sql") or "").strip()
        if sql:
            return {"language": "SQL", "content": sql}

    return {"language": "SQL", "content": ""}


def _iter_top_level_word_tokens(sql: str):
    """
    Itera tokens de palavra no nível top-level do SQL (fora de strings, comentários e parênteses).
    """
    if not isinstance(sql, str):
        return

    length = len(sql)
    idx = 0
    paren_depth = 0
    in_string = False
    in_line_comment = False
    in_block_comment = False

    while idx < length:
        char = sql[idx]
        next_char = sql[idx + 1] if idx + 1 < length else ""

        if in_line_comment:
            if char in {"\n", "\r"}:
                in_line_comment = False
            idx += 1
            continue

        if in_block_comment:
            if char == "*" and next_char == "/":
                in_block_comment = False
                idx += 2
                continue
            idx += 1
            continue

        if in_string:
            if char == "'" and next_char == "'":
                idx += 2
                continue
            if char == "'":
                in_string = False
            idx += 1
            continue

        if char == "-" and next_char == "-":
            in_line_comment = True
            idx += 2
            continue

        if char == "/" and next_char == "*":
            in_block_comment = True
            idx += 2
            continue

        if char == "'":
            in_string = True
            idx += 1
            continue

        if char == "(":
            paren_depth += 1
            idx += 1
            continue

        if char == ")":
            paren_depth = max(paren_depth - 1, 0)
            idx += 1
            continue

        if paren_depth == 0 and (char.isalpha() or char == "_"):
            start = idx
            idx += 1
            while idx < length:
                current = sql[idx]
                if current.isalnum() or current in {"_", "$", "#"}:
                    idx += 1
                    continue
                break
            yield sql[start:idx].upper(), start, idx
            continue

        idx += 1


def _extract_main_from_clause(sql: str) -> str:
    if not isinstance(sql, str):
        return ""

    tokens = list(_iter_top_level_word_tokens(sql))
    from_end = -1
    for token, _start, end in tokens:
        if token == "FROM":
            from_end = end
            break

    if from_end < 0:
        return ""

    end_pos = len(sql)
    for token, start, _end in tokens:
        if start <= from_end:
            continue
        if token in FROM_CLAUSE_TERMINATORS:
            end_pos = start
            break

    return sql[from_end:end_pos]


def _split_top_level_commas(text: str) -> List[str]:
    if not isinstance(text, str) or not text.strip():
        return []

    parts: List[str] = []
    current: List[str] = []
    paren_depth = 0
    in_string = False
    in_line_comment = False
    in_block_comment = False
    idx = 0
    length = len(text)

    while idx < length:
        char = text[idx]
        next_char = text[idx + 1] if idx + 1 < length else ""

        if in_line_comment:
            current.append(char)
            if char in {"\n", "\r"}:
                in_line_comment = False
            idx += 1
            continue

        if in_block_comment:
            current.append(char)
            if char == "*" and next_char == "/":
                current.append(next_char)
                in_block_comment = False
                idx += 2
                continue
            idx += 1
            continue

        if in_string:
            current.append(char)
            if char == "'" and next_char == "'":
                current.append(next_char)
                idx += 2
                continue
            if char == "'":
                in_string = False
            idx += 1
            continue

        if char == "-" and next_char == "-":
            current.append(char)
            current.append(next_char)
            in_line_comment = True
            idx += 2
            continue

        if char == "/" and next_char == "*":
            current.append(char)
            current.append(next_char)
            in_block_comment = True
            idx += 2
            continue

        if char == "'":
            current.append(char)
            in_string = True
            idx += 1
            continue

        if char == "(":
            current.append(char)
            paren_depth += 1
            idx += 1
            continue

        if char == ")":
            current.append(char)
            paren_depth = max(paren_depth - 1, 0)
            idx += 1
            continue

        if char == "," and paren_depth == 0:
            segment = "".join(current).strip()
            if segment:
                parts.append(segment)
            current = []
            idx += 1
            continue

        current.append(char)
        idx += 1

    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return parts


def _skip_parenthesized_expression(text: str, start: int) -> int:
    length = len(text)
    if start >= length or text[start] != "(":
        return start

    idx = start
    depth = 0
    in_string = False
    while idx < length:
        char = text[idx]
        next_char = text[idx + 1] if idx + 1 < length else ""

        if in_string:
            if char == "'" and next_char == "'":
                idx += 2
                continue
            if char == "'":
                in_string = False
            idx += 1
            continue

        if char == "'":
            in_string = True
            idx += 1
            continue

        if char == "(":
            depth += 1
            idx += 1
            continue

        if char == ")":
            depth -= 1
            idx += 1
            if depth <= 0:
                return idx
            continue

        idx += 1

    return idx


def _normalize_table_identifier(identifier: str) -> str:
    token = str(identifier or "").strip()
    if not token:
        return ""

    token = token.split("@", 1)[0]
    token = token.strip()
    if not token:
        return ""

    parts = [part.strip() for part in token.split(".") if part.strip()]
    if not parts:
        return ""

    table_part = parts[-1]
    if table_part.startswith('"') and table_part.endswith('"') and len(table_part) >= 2:
        table_part = table_part[1:-1]
    table_part = table_part.strip()
    return _normalize_name(table_part)


def _read_identifier(text: str, start: int) -> Tuple[str, int]:
    length = len(text)
    idx = start
    while idx < length and text[idx].isspace():
        idx += 1
    if idx >= length:
        return "", idx

    if text[idx] == '"':
        end = idx + 1
        while end < length and text[end] != '"':
            end += 1
        if end < length:
            return text[idx : end + 1], end + 1
        return text[idx:], length

    ident_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_$.#@")
    end = idx
    while end < length and text[end] in ident_chars:
        end += 1

    if end == idx:
        return "", idx
    return text[idx:end], end


def _read_table_after_position(text: str, start: int) -> Tuple[str, int]:
    length = len(text)
    idx = start
    while idx < length and text[idx].isspace():
        idx += 1
    if idx >= length:
        return "", idx

    if text[idx] == "(":
        return "", _skip_parenthesized_expression(text, idx)

    identifier, next_idx = _read_identifier(text, idx)
    if not identifier:
        return "", idx

    if _normalize_name(identifier) == "ONLY":
        return _read_table_after_position(text, next_idx)

    return _normalize_table_identifier(identifier), next_idx


def _extract_table_names_from_from_clause(from_clause: str) -> List[str]:
    segments = _split_top_level_commas(from_clause)
    if not segments:
        return []

    tables: List[str] = []
    seen: Set[str] = set()

    for segment in segments:
        base_table, _ = _read_table_after_position(segment, 0)
        if base_table and base_table not in seen:
            tables.append(base_table)
            seen.add(base_table)

        for token, _start, end in _iter_top_level_word_tokens(segment):
            if token != "JOIN":
                continue
            join_table, _ = _read_table_after_position(segment, end)
            if join_table and join_table not in seen:
                tables.append(join_table)
                seen.add(join_table)

    return tables


def _extract_sql_tables(sql: str) -> List[str]:
    from_clause = _extract_main_from_clause(sql)
    if not from_clause:
        return []
    return _extract_table_names_from_from_clause(from_clause)


def _normalize_object_extraction_queries(data: Dict[str, Any]) -> None:
    groups = data.get("groups", [])
    if not isinstance(groups, list):
        return

    for group in groups:
        if not isinstance(group, dict):
            continue
        objects = group.get("objects", [])
        if not isinstance(objects, list):
            continue

        for obj in objects:
            if not isinstance(obj, dict):
                continue
            obj["object_extraction_query"] = _resolve_object_extraction_query(obj)


def _normalize_otm_table_hierarchy(data: Dict[str, Any]) -> None:
    groups = data.get("groups", [])
    if not isinstance(groups, list):
        return

    for group in groups:
        if not isinstance(group, dict):
            continue
        objects = group.get("objects", [])
        if not isinstance(objects, list):
            continue

        for obj in objects:
            if not isinstance(obj, dict):
                continue

            primary_table = _normalize_name(obj.get("object_type") or obj.get("otm_table"))
            if primary_table:
                obj["otm_table"] = primary_table

            extraction_query = _resolve_object_extraction_query(obj)
            sql = extraction_query.get("content", "")
            tables_in_from = _extract_sql_tables(sql) if sql else []

            related_tables: List[str] = []
            seen_related: Set[str] = set()
            for table_name in tables_in_from:
                normalized_table = _normalize_name(table_name)
                if not normalized_table or normalized_table == primary_table:
                    continue
                if normalized_table in seen_related:
                    continue
                related_tables.append(normalized_table)
                seen_related.add(normalized_table)

            if not related_tables:
                # Fallback: preserva estrutura já existente quando o parser não
                # consegue extrair tabelas da query.
                related_tables = [
                    table_name
                    for table_name in _normalize_table_list(obj.get("otm_related_tables"))
                    if table_name != primary_table
                ]

            raw_subtables = _normalize_table_list(obj.get("otm_subtables"))
            if related_tables:
                related_lookup = set(related_tables)
                subtables = [table for table in raw_subtables if table in related_lookup]
            else:
                subtables = [table for table in raw_subtables if table != primary_table]

            obj["otm_related_tables"] = related_tables
            obj["otm_subtables"] = subtables


def _normalize_technical_content(data: Dict[str, Any]) -> None:
    groups = data.get("groups", [])
    if not isinstance(groups, list):
        return

    for group in groups:
        if not isinstance(group, dict):
            continue
        objects = group.get("objects", [])
        if not isinstance(objects, list):
            continue

        for obj in objects:
            if not isinstance(obj, dict):
                continue
            technical = obj.get("technical_content")
            if not isinstance(technical, dict):
                technical = {}
            obj["technical_content"] = {
                "type": str(technical.get("type") or "NONE").strip().upper() or "NONE",
                "content": str(technical.get("content") or "").strip(),
            }


def _normalize_object_domain_aliases(data: Dict[str, Any]) -> None:
    domain_map = table_domain_map()
    groups = data.get("groups", [])
    if not isinstance(groups, list):
        return

    for group in groups:
        if not isinstance(group, dict):
            continue
        objects = group.get("objects", [])
        if not isinstance(objects, list):
            continue

        for obj in objects:
            if not isinstance(obj, dict):
                continue

            domain_name = _normalize_name(obj.get("domainName"))
            domain_alias = _normalize_name(obj.get("domain"))
            table_name = _normalize_name(obj.get("object_type") or obj.get("otm_table"))

            if domain_name:
                obj["domainName"] = domain_name
                obj["domain"] = domain_name
                continue

            if domain_alias:
                obj["domain"] = domain_alias
                obj["domainName"] = domain_alias
                continue

            if not table_name:
                continue

            table_domains = [d for d in domain_map.get(table_name, []) if d]

            # Se houver apenas um dominio para a tabela, preenche automaticamente.
            if len(table_domains) == 1:
                only_domain = _normalize_name(table_domains[0])
                if only_domain:
                    obj["domainName"] = only_domain
                    obj["domain"] = only_domain
                continue

            # Compatibilidade: objetos auto antigos podem ter dominio no nome.
            if _is_truthy(obj.get("auto_generated")):
                name = str(obj.get("name") or "")
                match = re.search(r"\(([A-Z0-9_]+)\s*-\s*AUTO\)", name.upper())
                if match:
                    inferred_domain = _normalize_name(match.group(1))
                    if inferred_domain:
                        obj["domainName"] = inferred_domain
                        obj["domain"] = inferred_domain


def _inherit_subtable_item_from_primary(
    primary_obj: Dict[str, Any],
    subtable_obj: Dict[str, Any],
    subtable_name: str,
) -> None:
    if not isinstance(primary_obj, dict) or not isinstance(subtable_obj, dict):
        return

    normalized_subtable = _normalize_name(subtable_name)
    if normalized_subtable:
        subtable_obj["object_type"] = normalized_subtable
        subtable_obj["otm_table"] = normalized_subtable

    primary_domain = _normalize_name(primary_obj.get("domainName") or primary_obj.get("domain"))
    subtable_obj["domainName"] = primary_domain
    subtable_obj["domain"] = primary_domain

    primary_extraction = _resolve_object_extraction_query(primary_obj)
    subtable_obj["object_extraction_query"] = {
        "language": str(primary_extraction.get("language") or "SQL").strip().upper() or "SQL",
        "content": str(primary_extraction.get("content") or "").strip(),
    }

    is_auto_generated = _is_truthy(subtable_obj.get("auto_generated"))
    primary_deployment = str(primary_obj.get("deployment_type") or "").strip()
    subtable_obj["deployment_type"] = primary_deployment
    subtable_obj["deployment_type_user_defined"] = bool(primary_deployment)

    primary_responsible = str(primary_obj.get("responsible") or "").strip()
    subtable_obj["responsible"] = primary_responsible

    primary_identifiers = primary_obj.get("identifiers")
    if isinstance(primary_identifiers, dict):
        subtable_obj["identifiers"] = json.loads(
            json.dumps(primary_identifiers, ensure_ascii=False)
        )
    else:
        subtable_obj["identifiers"] = {}

    primary_related_tables = _normalize_table_list(primary_obj.get("otm_related_tables"))
    subtable_obj["otm_related_tables"] = json.loads(
        json.dumps(primary_related_tables, ensure_ascii=False)
    )
    subtable_obj["otm_subtables"] = []

    primary_notes = str(primary_obj.get("notes") or "").strip()
    if primary_notes and (is_auto_generated or not str(subtable_obj.get("notes") or "").strip()):
        subtable_obj["notes"] = primary_notes

    primary_status = primary_obj.get("status")
    if isinstance(primary_status, dict):
        # Regra canônica: status de subtabela sempre acompanha o item principal.
        subtable_obj["status"] = json.loads(json.dumps(primary_status, ensure_ascii=False))

    primary_technical = primary_obj.get("technical_content")
    if isinstance(primary_technical, dict):
        normalized_technical = {
            "type": str(primary_technical.get("type") or "NONE").strip().upper() or "NONE",
            "content": str(primary_technical.get("content") or "").strip(),
        }
        current_technical = subtable_obj.get("technical_content")
        if not isinstance(current_technical, dict):
            current_technical = {"type": "NONE", "content": ""}
        if is_auto_generated:
            subtable_obj["technical_content"] = normalized_technical
        else:
            if normalized_technical["type"] != "NONE" and (
                str(current_technical.get("type") or "").strip().upper() in {"", "NONE"}
            ):
                current_technical["type"] = normalized_technical["type"]
            if normalized_technical["content"] and not str(current_technical.get("content") or "").strip():
                current_technical["content"] = normalized_technical["content"]
            subtable_obj["technical_content"] = current_technical

    subtable_obj["otm_related_tables"] = _normalize_table_list(subtable_obj.get("otm_related_tables"))
    subtable_obj["otm_subtables"] = _normalize_table_list(subtable_obj.get("otm_subtables"))


def _relocate_group_zero_subtables(data: Dict[str, Any]) -> None:
    groups = data.get("groups", [])
    if not isinstance(groups, list):
        return

    group_zero: Optional[Dict[str, Any]] = None
    manual_groups: List[Dict[str, Any]] = []
    for group in groups:
        if not isinstance(group, dict):
            continue
        normalized_group_id = _normalize_name(group.get("group_id"))
        if normalized_group_id == GROUP_ZERO_ID:
            group_zero = group
            continue
        if normalized_group_id in {IGNORED_GROUP_ID, ""}:
            continue
        manual_groups.append(group)

    if group_zero is None:
        return

    group_zero_objects = _as_object_list(group_zero.get("objects"))
    group_zero["objects"] = group_zero_objects
    if not group_zero_objects:
        return

    consumed_group_zero_indexes: Set[int] = set()

    def _find_candidate_index(table_name: str, domain_name: str) -> Optional[int]:
        table_token = _normalize_name(table_name)
        domain_token = _normalize_name(domain_name)
        if not table_token:
            return None

        def _matches(idx: int, require_domain: Optional[bool]) -> bool:
            if idx in consumed_group_zero_indexes:
                return False
            candidate = group_zero_objects[idx]
            if not isinstance(candidate, dict):
                return False
            if _is_truthy(candidate.get("ignore_table")):
                return False
            candidate_table = _normalize_name(candidate.get("object_type") or candidate.get("otm_table"))
            if candidate_table != table_token:
                return False
            candidate_domain = _normalize_name(candidate.get("domainName") or candidate.get("domain"))
            if require_domain is True:
                return bool(domain_token) and candidate_domain == domain_token
            if require_domain is False:
                return candidate_domain == ""
            return True

        if domain_token:
            for idx in range(len(group_zero_objects)):
                if _matches(idx, True):
                    return idx
            for idx in range(len(group_zero_objects)):
                if _matches(idx, False):
                    return idx

        for idx in range(len(group_zero_objects)):
            if _matches(idx, None):
                return idx
        return None

    def _find_target_object(
        target_objects: List[Dict[str, Any]],
        table_name: str,
        domain_name: str,
    ) -> Optional[Dict[str, Any]]:
        table_token = _normalize_name(table_name)
        domain_token = _normalize_name(domain_name)
        if not table_token:
            return None
        for candidate in target_objects:
            if not isinstance(candidate, dict):
                continue
            if _is_truthy(candidate.get("ignore_table")):
                continue
            candidate_table = _normalize_name(candidate.get("object_type") or candidate.get("otm_table"))
            if candidate_table != table_token:
                continue
            candidate_domain = _normalize_name(candidate.get("domainName") or candidate.get("domain"))
            if domain_token and candidate_domain and candidate_domain != domain_token:
                continue
            return candidate
        return None

    for group in manual_groups:
        target_objects = _as_object_list(group.get("objects"))
        group["objects"] = target_objects
        if not target_objects:
            continue

        primary_items = list(target_objects)
        for primary_obj in primary_items:
            if not isinstance(primary_obj, dict):
                continue

            primary_table = _normalize_name(primary_obj.get("object_type") or primary_obj.get("otm_table"))
            if not primary_table:
                continue

            selected_subtables = _normalize_table_list(primary_obj.get("otm_subtables"))
            if not selected_subtables:
                continue

            primary_domain = _normalize_name(primary_obj.get("domainName") or primary_obj.get("domain"))
            for subtable_name in selected_subtables:
                if subtable_name == primary_table:
                    continue

                existing_target = _find_target_object(target_objects, subtable_name, primary_domain)
                if existing_target is not None:
                    _inherit_subtable_item_from_primary(primary_obj, existing_target, subtable_name)

                candidate_idx = _find_candidate_index(subtable_name, primary_domain)
                if candidate_idx is None:
                    continue

                candidate_obj = group_zero_objects[candidate_idx]
                if not isinstance(candidate_obj, dict):
                    consumed_group_zero_indexes.add(candidate_idx)
                    continue

                if existing_target is None:
                    _inherit_subtable_item_from_primary(primary_obj, candidate_obj, subtable_name)
                    candidate_obj[MIGRATION_ITEM_ID_KEY] = ""
                    target_objects.append(candidate_obj)

                consumed_group_zero_indexes.add(candidate_idx)

    if consumed_group_zero_indexes:
        group_zero["objects"] = [
            obj
            for idx, obj in enumerate(group_zero_objects)
            if idx not in consumed_group_zero_indexes
        ]


def _normalize_auto_generated_deployment_types(data: Dict[str, Any]) -> None:
    groups = data.get("groups", [])
    if not isinstance(groups, list):
        return

    for group in groups:
        if not isinstance(group, dict):
            continue
        objects = group.get("objects", [])
        if not isinstance(objects, list):
            continue

        for obj in objects:
            if not isinstance(obj, dict):
                continue
            if not _is_truthy(obj.get("auto_generated")):
                continue
            if _is_truthy(obj.get("deployment_type_user_defined")):
                continue

            table_name = _normalize_name(obj.get("object_type") or obj.get("otm_table"))
            if not table_name:
                continue

            domain_name = _normalize_name(obj.get("domainName") or obj.get("domain"))
            target_type = deployment_type_for_table(table_name, domain_name)
            obj["deployment_type"] = target_type


def _ensure_domain_statistics_coverage(data: Dict[str, Any]) -> None:
    required_map = table_domain_map()
    if not required_map:
        return
    ignored_tables = _collect_ignored_otm_tables(data)

    groups = data.get("groups", [])
    if not isinstance(groups, list):
        return

    group_zero = None
    for group in groups:
        if not isinstance(group, dict):
            continue
        if _normalize_name(group.get("group_id")) == GROUP_ZERO_ID:
            group_zero = group
            break
    if group_zero is None:
        return

    objects = _as_object_list(group_zero.get("objects"))
    group_zero["objects"] = objects

    existing_domains = object_domain_map(data.get("groups", []), required_map)
    for table_name, domains in required_map.items():
        if table_name in ignored_tables:
            continue
        if not domains:
            continue
        required_domains = [d for d in domains if d]
        missing = [
            domain for domain in required_domains
            if domain not in existing_domains.get(table_name, set())
        ]
        if not missing:
            continue

        next_sequence = 1
        for obj in objects:
            if not isinstance(obj, dict):
                continue
            next_sequence = max(next_sequence, _to_int(obj.get("sequence")) + 1)

        for domain_name in missing:
            objects.append(
                _build_auto_group_zero_object(table_name, next_sequence, domain_name)
            )
            next_sequence += 1


def _cleanup_group_zero_legacy_generic_autos(data: Dict[str, Any]) -> None:
    """
    Remove autos legados genéricos em SEM_GRUPO quando a cobertura por domínio
    já existe para tabelas multi-domínio.
    """
    required_map = table_domain_map()
    if not required_map:
        return

    groups = data.get("groups", [])
    if not isinstance(groups, list):
        return

    group_zero = None
    for group in groups:
        if not isinstance(group, dict):
            continue
        if _normalize_name(group.get("group_id")) == GROUP_ZERO_ID:
            group_zero = group
            break

    if group_zero is None:
        return

    objects = _as_object_list(group_zero.get("objects"))
    group_zero["objects"] = objects
    if not objects:
        return

    coverage = object_domain_map(data.get("groups", []), required_map)
    filtered: List[Dict[str, Any]] = []

    for obj in objects:
        table_name = _normalize_name(obj.get("object_type") or obj.get("otm_table"))
        if not table_name:
            filtered.append(obj)
            continue

        table_domains = [d for d in required_map.get(table_name, []) if d]
        if len(table_domains) <= 1:
            filtered.append(obj)
            continue

        is_auto = _is_truthy(obj.get("auto_generated"))
        has_domain = bool(_normalize_name(obj.get("domainName") or obj.get("domain")))
        generic_name = f"{table_name} (AUTO)"
        is_generic_legacy = _normalize_name(obj.get("name")) == generic_name
        has_full_coverage = all(
            domain in coverage.get(table_name, set()) for domain in table_domains
        )

        if is_auto and is_generic_legacy and not has_domain and has_full_coverage:
            continue

        filtered.append(obj)

    group_zero["objects"] = filtered


def _deduplicate_group_zero_auto_objects(data: Dict[str, Any]) -> None:
    """
    Garante apenas 1 objeto auto por combinacao (tabela, dominio) no SEM_GRUPO.
    """
    groups = data.get("groups", [])
    if not isinstance(groups, list):
        return

    group_zero = None
    for group in groups:
        if not isinstance(group, dict):
            continue
        if _normalize_name(group.get("group_id")) == GROUP_ZERO_ID:
            group_zero = group
            break
    if group_zero is None:
        return

    objects = _as_object_list(group_zero.get("objects"))
    if not objects:
        group_zero["objects"] = objects
        return

    deduped: List[Dict[str, Any]] = []
    seen_auto_keys: Set[Tuple[str, str]] = set()

    for obj in objects:
        table_name = _normalize_name(obj.get("object_type") or obj.get("otm_table"))
        domain_name = _normalize_name(obj.get("domainName") or obj.get("domain"))
        is_auto = _is_truthy(obj.get("auto_generated"))

        if is_auto and table_name:
            auto_key = (table_name, domain_name)
            if auto_key in seen_auto_keys:
                continue
            seen_auto_keys.add(auto_key)

        deduped.append(obj)

    group_zero["objects"] = deduped


def _normalize_group_zero(data):
    """
    Garante o Grupo 0 e centraliza objetos sem grupo definido.

    Fontes de objetos sem grupo:
    - data['objects'] legado (top-level)
    - grupos sem group_id
    """
    groups = data.get("groups")
    if not isinstance(groups, list):
        groups = []

    group_zero = None
    ignored_group = None
    normalized_groups = []
    manual_groups_with_order: List[Tuple[int, int, Dict[str, Any]]] = []
    ungrouped_objects = []
    ignored_objects = []

    top_level_objects = _as_object_list(data.get("objects"))
    if top_level_objects:
        top_level_regular, top_level_ignored = _split_ignored_objects(top_level_objects)
        ungrouped_objects.extend(top_level_regular)
        ignored_objects.extend(top_level_ignored)
    data.pop("objects", None)

    for idx, group in enumerate(groups):
        if not isinstance(group, dict):
            continue

        group_id = str(group.get("group_id") or "").strip().upper()
        source_objects = _as_object_list(group.get("objects"))
        regular_objects, group_ignored_objects = _split_ignored_objects(source_objects)
        ignored_objects.extend(group_ignored_objects)

        if group_id in LEGACY_GROUP_ZERO_IDS:
            group_zero = group
            group_zero["group_id"] = GROUP_ZERO_ID
            group_zero["label"] = str(group_zero.get("label") or GROUP_ZERO_LABEL)
            group_zero["description"] = str(
                group_zero.get("description") or GROUP_ZERO_DESCRIPTION
            )
            group_zero["sequence"] = GROUP_ZERO_SEQUENCE
            group_zero["objects"] = regular_objects
            continue

        if group_id == IGNORED_GROUP_ID:
            ignored_group = group
            ignored_group["group_id"] = IGNORED_GROUP_ID
            ignored_group["label"] = str(ignored_group.get("label") or IGNORED_GROUP_LABEL)
            ignored_group["description"] = str(
                ignored_group.get("description") or IGNORED_GROUP_DESCRIPTION
            )
            ignored_group["sequence"] = IGNORED_GROUP_SEQUENCE
            # Será preenchido no final com o consolidado de ignorados.
            ignored_group["objects"] = []
            # Objetos não ignorados não devem permanecer no grupo de ignorados.
            if regular_objects:
                ungrouped_objects.extend(regular_objects)
            continue

        if not group_id:
            ungrouped_objects.extend(regular_objects)
            continue

        group["group_id"] = group_id
        group["objects"] = regular_objects
        seq_hint = _to_int(group.get("sequence"))
        if seq_hint <= 0:
            seq_hint = 10_000 + idx
        manual_groups_with_order.append((seq_hint, idx, group))

    if group_zero is None:
        group_zero = {
            "group_id": GROUP_ZERO_ID,
            "label": GROUP_ZERO_LABEL,
            "sequence": GROUP_ZERO_SEQUENCE,
            "description": GROUP_ZERO_DESCRIPTION,
            "objects": [],
        }
    if ignored_group is None:
        ignored_group = {
            "group_id": IGNORED_GROUP_ID,
            "label": IGNORED_GROUP_LABEL,
            "sequence": IGNORED_GROUP_SEQUENCE,
            "description": IGNORED_GROUP_DESCRIPTION,
            "objects": [],
        }

    # Sequência canônica dos grupos manuais:
    # SEM_GRUPO e IGNORADOS não contam; manuais iniciam em 1.
    manual_groups_with_order.sort(key=lambda item: (item[0], item[1]))
    for manual_seq, (_, _, group) in enumerate(manual_groups_with_order, start=1):
        group["sequence"] = manual_seq
        normalized_groups.append(group)

    if ungrouped_objects:
        group_zero["objects"].extend(ungrouped_objects)
    group_zero["objects"] = _as_object_list(group_zero.get("objects"))
    ignored_group["objects"] = _as_object_list(ignored_objects)
    data["groups"] = [group_zero, ignored_group] + normalized_groups

    active_group_id = str(data.get("active_group_id") or "").strip().upper()
    valid_group_ids = [
        str(group.get("group_id") or "").strip().upper()
        for group in data.get("groups", [])
        if isinstance(group, dict)
    ]

    if active_group_id in LEGACY_GROUP_ZERO_IDS:
        data["active_group_id"] = GROUP_ZERO_ID
        return

    if active_group_id and active_group_id in valid_group_ids:
        data["active_group_id"] = active_group_id
        return

    if GROUP_ZERO_ID in valid_group_ids:
        data["active_group_id"] = GROUP_ZERO_ID
        return

    data["active_group_id"] = valid_group_ids[0] if valid_group_ids else None


def load_project():
    if not PROJECT_PATH.exists():
        return None

    if PROJECT_PATH.stat().st_size == 0:
        return None

    with open(PROJECT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    original_signature = json.dumps(data, ensure_ascii=False, sort_keys=True)

    project_metadata = data.setdefault("project_metadata", {})
    migration_objective = project_metadata.setdefault("migration_objective", {})
    migration_objective.setdefault("title", "Objetivo do Projeto de Migração")
    migration_objective.setdefault("content", [])
    project_metadata.setdefault("version_control", {})
    project_metadata.setdefault("change_history", [])

    # Compatibilidade retroativa: adicionar 'name' e 'description' se não existirem
    if data.get("groups"):
        for group_idx, group in enumerate(data["groups"]):
            if "description" not in group:
                group["description"] = ""
            if group.get("objects"):
                for obj_idx, obj in enumerate(group["objects"]):
                    if "name" not in obj:
                        # Gerar fallback: TYPE #index
                        obj_type = obj.get("object_type") or obj.get("type", "OBJETO")
                        obj["name"] = f"{obj_type} #{obj_idx + 1}"
                    if "description" not in obj:
                        obj["description"] = ""
                    if "otm_related_tables" not in obj:
                        obj["otm_related_tables"] = []
                    if "otm_subtables" not in obj:
                        obj["otm_subtables"] = []
                    # Garantir status existe
                    if "status" not in obj:
                        obj["status"] = {
                            "documentation": "PENDING",
                            "deployment": "PENDING"
                        }
                    else:
                        # Garantir campos de status existem
                        if "documentation" not in obj["status"]:
                            obj["status"]["documentation"] = "PENDING"
                        if "deployment" not in obj["status"]:
                            obj["status"]["deployment"] = "PENDING"
                    # Garantir saved_query existe para SAVED_QUERY
                    obj_type = obj.get("object_type") or obj.get("type")
                    if obj_type == "SAVED_QUERY" and "saved_query" not in obj:
                        obj["saved_query"] = {"sql": ""}

    _normalize_group_zero(data)
    _normalize_object_extraction_queries(data)
    _normalize_otm_table_hierarchy(data)
    _normalize_technical_content(data)
    # Primeiro normaliza aliases de dominio para evitar duplicacao por cobertura.
    _normalize_object_domain_aliases(data)
    _relocate_group_zero_subtables(data)
    _ensure_domain_statistics_coverage(data)
    _normalize_object_domain_aliases(data)
    _normalize_auto_generated_deployment_types(data)
    _deduplicate_group_zero_auto_objects(data)
    _cleanup_group_zero_legacy_generic_autos(data)
    _normalize_migration_group_item_aliases(data)
    normalized_signature = json.dumps(data, ensure_ascii=False, sort_keys=True)
    if normalized_signature != original_signature:
        PROJECT_PATH.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return data


def save_project(domain):
    _normalize_group_zero(domain)
    _normalize_object_extraction_queries(domain)
    _normalize_otm_table_hierarchy(domain)
    _normalize_technical_content(domain)
    _normalize_object_domain_aliases(domain)
    _relocate_group_zero_subtables(domain)
    _ensure_domain_statistics_coverage(domain)
    _normalize_object_domain_aliases(domain)
    _normalize_auto_generated_deployment_types(domain)
    _deduplicate_group_zero_auto_objects(domain)
    _cleanup_group_zero_legacy_generic_autos(domain)
    _normalize_migration_group_item_aliases(domain)
    PROJECT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PROJECT_PATH, "w", encoding="utf-8") as f:
        json.dump(domain, f, indent=2, ensure_ascii=False)
