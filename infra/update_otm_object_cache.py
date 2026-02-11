#!/usr/bin/env python3
"""
Build local OTM object cache files from projeto_migracao migration items.

Core rules:
- Extraction query comes from object_extraction_query.content.
- ROOT_NAME uses migration item otm_table and only user-selected otm_subtables.
- Output rows always contain every column from metadata/otm/tables/<TABLE>.json.
- Missing values in OTM response are filled with empty string.
- INSERT_DATE/UPDATE_DATE are managed as local cache lifecycle fields when present in schema.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

try:
    from infra.otm_query_executor import execute_otm_query
except ModuleNotFoundError:
    from otm_query_executor import execute_otm_query  # type: ignore


BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_PATH = BASE_DIR / "domain" / "projeto_migracao" / "projeto_migracao.json"
TABLES_DIR = BASE_DIR / "metadata" / "otm" / "tables"
CACHE_DIR = BASE_DIR / "metadata" / "otm" / "cache" / "objects"
CACHE_INDEX_PATH = BASE_DIR / "metadata" / "otm" / "cache" / "objects_index.json"
SCRIPT_NAME = "update_otm_object_cache.py"
QUERY_TIMEOUT_SECONDS = 300
MIGRATION_GROUP_ID_KEY = "migration_group_id"
MIGRATION_ITEM_ID_KEY = "migration_item_id"
MIGRATION_ITEM_NAME_KEY = "migration_item_name"
INVALID_DOMAIN_TOKENS = {"", "NO_DOMAIN", "NONE", "NULL"}
LOCAL_INSERT_DATE_COLUMN = "INSERT_DATE"
LOCAL_UPDATE_DATE_COLUMN = "UPDATE_DATE"


def _timestamp_utc_z() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_name(value: Any) -> str:
    return str(value or "").strip().upper()


def _is_truthy(value: Any) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "on", "yes", "y"}


def _slugify(value: Any) -> str:
    raw = str(value or "").strip().upper()
    slug = re.sub(r"[^A-Z0-9]+", "_", raw).strip("_")
    return slug or "OBJECT"


def _short_slug(value: Any, max_len: int) -> str:
    slug = _slugify(value)
    if len(slug) <= max_len:
        return slug
    return slug[:max_len].rstrip("_") or slug[:max_len]


def _build_migration_item_id(group_id: str, item: Dict[str, Any]) -> str:
    group_token = _slugify(group_id or "NO_GROUP")
    table_token = _slugify(item.get("otm_table") or item.get("object_type") or "NO_TABLE")
    name_token = _slugify(item.get("name") or item.get(MIGRATION_ITEM_NAME_KEY) or "NO_NAME")
    sequence = str(item.get("sequence") or "0").strip() or "0"
    return f"MIGRATION_ITEM.{group_token}.{table_token}.{name_token}.{sequence}"


def _resolve_domain_name(item: Dict[str, Any]) -> str:
    domain_name = _normalize_name(item.get("domainName") or item.get("domain"))
    if domain_name in INVALID_DOMAIN_TOKENS:
        return ""
    return domain_name


def _resolve_object_extraction_query(item: Dict[str, Any]) -> Tuple[str, str, str]:
    extraction_query = item.get("object_extraction_query")
    if isinstance(extraction_query, dict):
        language = str(
            extraction_query.get("language") or extraction_query.get("type") or "SQL"
        ).strip().upper() or "SQL"
        content = str(extraction_query.get("content") or "").strip()
        if content:
            return language, content, "object_extraction_query"

    saved_query = item.get("saved_query")
    if isinstance(saved_query, dict):
        content = str(saved_query.get("sql") or "").strip()
        if content:
            return "SQL", content, "saved_query"

    return "SQL", "", "none"


def _normalize_table_identifier(raw_identifier: str) -> str:
    token = str(raw_identifier or "").strip()
    if not token:
        return ""

    token = token.rstrip(")")
    token = token.split("@", 1)[0].strip()
    if token.startswith('"') and token.endswith('"') and len(token) >= 2:
        token = token[1:-1]

    parts = [part.strip() for part in token.split(".") if part.strip()]
    if not parts:
        return ""

    return _normalize_name(parts[-1])


def _split_top_level_commas(text: str) -> List[str]:
    if not isinstance(text, str) or not text.strip():
        return []

    parts: List[str] = []
    current: List[str] = []
    paren_depth = 0
    in_string = False
    idx = 0
    length = len(text)

    while idx < length:
        char = text[idx]
        next_char = text[idx + 1] if idx + 1 < length else ""

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


def _extract_main_from_clause(sql_query: str) -> str:
    if not isinstance(sql_query, str):
        return ""
    match = re.search(
        r"(?is)\bFROM\b(?P<from>.*?)(?:\bWHERE\b|\bGROUP\s+BY\b|\bORDER\s+BY\b|\bHAVING\b|\bCONNECT\s+BY\b|\bSTART\s+WITH\b|\bUNION\b|\bMINUS\b|\bINTERSECT\b|$)",
        sql_query,
    )
    if not match:
        return ""
    return str(match.group("from") or "").strip()


def _extract_tables_from_sql_query(sql_query: str) -> List[str]:
    from_clause = _extract_main_from_clause(sql_query)
    if not from_clause:
        return []

    table_names: List[str] = []
    seen: Set[str] = set()

    segments = _split_top_level_commas(from_clause)
    if not segments:
        segments = [from_clause]

    for segment in segments:
        segment_text = str(segment or "").strip()
        if not segment_text or segment_text.startswith("("):
            continue

        base_match = re.match(
            r"(?is)^\s*(?:ONLY\s*\(\s*)?(?P<table>[A-Z0-9_.$\"#@]+)",
            segment_text,
        )
        if base_match:
            base_table = _normalize_table_identifier(base_match.group("table"))
            if base_table and base_table not in seen:
                table_names.append(base_table)
                seen.add(base_table)

        for join_match in re.finditer(
            r"(?is)\bJOIN\b\s+(?:ONLY\s*\(\s*)?(?P<table>[A-Z0-9_.$\"#@]+)",
            segment_text,
        ):
            join_table = _normalize_table_identifier(join_match.group("table"))
            if join_table and join_table not in seen:
                table_names.append(join_table)
                seen.add(join_table)

    return table_names


def _resolve_item_tables(obj: Dict[str, Any], primary_table: str, _sql_query: str) -> List[str]:
    target_tables: List[str] = []
    seen_tables: Set[str] = set()

    normalized_primary = _normalize_name(primary_table)
    if normalized_primary:
        target_tables.append(normalized_primary)
        seen_tables.add(normalized_primary)

    raw_subtables = obj.get("otm_subtables")
    candidate_values: List[str] = []
    if isinstance(raw_subtables, list):
        candidate_values.extend(str(value or "") for value in raw_subtables)
    elif isinstance(raw_subtables, str):
        candidate_values.extend(part.strip() for part in raw_subtables.split(","))

    for candidate in candidate_values:
        normalized_candidate = _normalize_name(candidate)
        if not normalized_candidate:
            continue
        if normalized_candidate in seen_tables:
            continue
        target_tables.append(normalized_candidate)
        seen_tables.add(normalized_candidate)

    return target_tables


def _find_by_local_name(node: Dict[str, Any], local_name: str) -> Any:
    for key, value in node.items():
        if key.split("}")[-1] == local_name:
            return value
    return None


def _extract_transaction_rows(payload: Dict[str, Any], root_name: str) -> List[Dict[str, Any]]:
    xml2sql = _find_by_local_name(payload, "xml2sql")
    if not isinstance(xml2sql, dict):
        return []

    transaction_set = _find_by_local_name(xml2sql, "TRANSACTION_SET")
    if transaction_set is None or transaction_set == "NO DATA":
        return []
    if not isinstance(transaction_set, dict):
        return []

    rows = transaction_set.get(root_name)
    if rows is None:
        rows = _find_by_local_name(transaction_set, root_name)
    if rows is None:
        return []

    if isinstance(rows, list):
        source_rows = rows
    elif isinstance(rows, dict):
        source_rows = [rows]
    else:
        return []

    extracted: List[Dict[str, Any]] = []
    for row in source_rows:
        if not isinstance(row, dict):
            continue
        attrs = row.get("@attributes")
        if isinstance(attrs, dict):
            extracted.append(attrs)
            continue
        extracted.append(
            {k: v for k, v in row.items() if isinstance(v, (str, int, float, bool, dict, list))}
        )
    return extracted


def _load_project() -> Dict[str, Any]:
    if not PROJECT_PATH.exists():
        raise FileNotFoundError(f"Arquivo de projeto nao encontrado: {PROJECT_PATH}")
    with PROJECT_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _iter_project_objects(project_data: Dict[str, Any]) -> Iterable[Tuple[str, Dict[str, Any]]]:
    groups = project_data.get("groups", [])
    if not isinstance(groups, list):
        return []

    pairs: List[Tuple[str, Dict[str, Any]]] = []
    for group in groups:
        if not isinstance(group, dict):
            continue
        migration_group_id = str(
            group.get(MIGRATION_GROUP_ID_KEY) or group.get("group_id") or ""
        ).strip()
        migration_items = group.get("migration_items")
        if not isinstance(migration_items, list):
            migration_items = group.get("objects", [])
        if not isinstance(migration_items, list):
            continue
        for obj in migration_items:
            if isinstance(obj, dict):
                pairs.append((migration_group_id, obj))
    return pairs


def _select_object(
    project_data: Dict[str, Any],
    migration_item_name: str,
    migration_group_id: str | None,
) -> Tuple[str, Dict[str, Any]]:
    target_name = migration_item_name.strip().lower()
    target_group = _normalize_name(migration_group_id) if migration_group_id else ""

    matches: List[Tuple[str, Dict[str, Any]]] = []
    for current_group_id, item in _iter_project_objects(project_data):
        current_name = str(
            item.get(MIGRATION_ITEM_NAME_KEY) or item.get("name") or ""
        ).strip().lower()
        if current_name != target_name:
            continue
        if target_group and _normalize_name(current_group_id) != target_group:
            continue
        matches.append((current_group_id, item))

    if not matches:
        raise ValueError(
            "MIGRATION_ITEM nao encontrado no projeto. "
            f"name={migration_item_name!r}, migration_group_id={migration_group_id!r}"
        )

    if len(matches) > 1:
        labels = ", ".join(
            f"{str(item.get('name') or '')} [migration_group={gid}]"
            for gid, item in matches
        )
        raise ValueError(
            "Mais de um MIGRATION_ITEM encontrado com esse nome. "
            "Informe --migration-group-id para desambiguar. "
            f"Candidatos: {labels}"
        )

    return matches[0]


def _select_object_by_migration_item_id(
    project_data: Dict[str, Any],
    migration_item_id: str,
) -> Tuple[str, Dict[str, Any]]:
    target_item_id = str(migration_item_id or "").strip()
    if not target_item_id:
        raise ValueError("migration_item_id vazio.")

    matches: List[Tuple[str, Dict[str, Any]]] = []
    for current_group_id, item in _iter_project_objects(project_data):
        current_item_id = str(item.get(MIGRATION_ITEM_ID_KEY) or "").strip()
        if current_item_id == target_item_id:
            matches.append((current_group_id, item))

    if not matches:
        raise ValueError(f"MIGRATION_ITEM nao encontrado para migration_item_id='{target_item_id}'.")

    if len(matches) > 1:
        raise ValueError(
            f"Mais de um MIGRATION_ITEM encontrado para migration_item_id='{target_item_id}'."
        )

    return matches[0]


def _select_group_objects(
    project_data: Dict[str, Any],
    migration_group_id: str,
) -> List[Tuple[str, Dict[str, Any]]]:
    target_group = _normalize_name(migration_group_id)
    if not target_group:
        raise ValueError("migration_group_id vazio.")

    matches: List[Tuple[str, Dict[str, Any]]] = []
    for current_group_id, obj in _iter_project_objects(project_data):
        if _normalize_name(current_group_id) != target_group:
            continue
        matches.append((current_group_id, obj))

    if not matches:
        raise ValueError(f"Nenhum MIGRATION_ITEM encontrado para o MIGRATION_GROUP '{migration_group_id}'.")
    return matches


def _load_table_columns(table_name: str) -> Tuple[List[str], Dict[str, Any]]:
    normalized_table = _normalize_name(table_name)
    if not normalized_table:
        raise ValueError("MIGRATION_ITEM sem otm_table definido.")

    table_path = TABLES_DIR / f"{normalized_table}.json"
    if not table_path.exists():
        raise FileNotFoundError(
            f"Schema da tabela nao encontrado em metadata/otm/tables: {normalized_table}.json"
        )

    with table_path.open("r", encoding="utf-8") as handle:
        schema = json.load(handle)

    columns_raw = schema.get("columns", [])
    if not isinstance(columns_raw, list):
        raise ValueError(f"Schema invalido para tabela {normalized_table}: columns nao e lista.")

    columns: List[str] = []
    for col in columns_raw:
        if not isinstance(col, dict):
            continue
        col_name = _normalize_name(col.get("name"))
        if not col_name:
            continue
        columns.append(col_name)

    if not columns:
        raise ValueError(f"Tabela {normalized_table} sem colunas validas no metadata.")

    return columns, schema


def _extract_primary_key_columns(table_schema: Dict[str, Any]) -> List[str]:
    pk_columns_raw = table_schema.get("primaryKey", [])
    if not isinstance(pk_columns_raw, list):
        return []

    pk_columns: List[str] = []
    for pk in pk_columns_raw:
        if not isinstance(pk, dict):
            continue
        col_name = _normalize_name(pk.get("columnName"))
        if col_name:
            pk_columns.append(col_name)
    return pk_columns


def _build_object_identity_key(
    normalized_row: Dict[str, str],
    table_name: str,
    domain_name: str,
    pk_columns: List[str],
) -> str:
    # Preferência: chave primária declarada no metadata da tabela.
    if pk_columns:
        pk_parts: List[str] = []
        for col in pk_columns:
            value = str(normalized_row.get(col) or "").strip()
            if not value:
                pk_parts = []
                break
            pk_parts.append(f"{col}={value}")
        if pk_parts:
            return f"{domain_name}|{table_name}|PK|{'|'.join(pk_parts)}"

    # Fallback 1: <TABLE>_GID.
    gid_col = f"{table_name}_GID"
    gid_value = str(normalized_row.get(gid_col) or "").strip()
    if gid_value:
        return f"{domain_name}|{table_name}|GID|{gid_value}"

    # Fallback 2: <TABLE>_XID + DOMAIN_NAME.
    xid_col = f"{table_name}_XID"
    xid_value = str(normalized_row.get(xid_col) or "").strip()
    row_domain = str(normalized_row.get("DOMAIN_NAME") or "").strip() or domain_name
    if xid_value and row_domain:
        return f"{row_domain}|{table_name}|XID|{xid_value}"

    return ""


def _stringify_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, dict):
        text = value.get("#text")
        if isinstance(text, (str, int, float, bool)):
            return str(text)
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    if isinstance(value, list):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _normalize_row_by_schema(
    row: Dict[str, Any],
    schema_columns: List[str],
) -> Tuple[Dict[str, str], Set[str]]:
    row_source: Dict[str, str] = {}
    for key, value in row.items():
        normalized_key = key.split("}")[-1].strip().upper()
        if not normalized_key:
            continue
        row_source[normalized_key] = _stringify_value(value)

    normalized_row: Dict[str, str] = {}
    for column in schema_columns:
        normalized_row[column] = row_source.get(column, "")

    extra_fields = {k for k in row_source.keys() if k not in set(schema_columns)}
    return normalized_row, extra_fields


def _row_signature_without_local_dates(row: Dict[str, str]) -> str:
    comparable_row = {
        key: str(value or "")
        for key, value in row.items()
        if key not in {LOCAL_INSERT_DATE_COLUMN, LOCAL_UPDATE_DATE_COLUMN}
    }
    return json.dumps(comparable_row, ensure_ascii=False, sort_keys=True)


def _normalize_existing_row_by_schema(
    row: Dict[str, Any],
    schema_columns: List[str],
) -> Dict[str, str]:
    normalized: Dict[str, str] = {}
    for column in schema_columns:
        normalized[column] = _stringify_value(row.get(column))
    return normalized


def _load_existing_cache_context(
    output_path: Path,
    table_name: str,
) -> Tuple[List[Dict[str, Any]], str]:
    if not output_path.exists():
        return [], ""

    try:
        payload = json.loads(output_path.read_text(encoding="utf-8"))
    except Exception:
        return [], ""

    if not isinstance(payload, dict):
        return [], ""

    normalized_table = _normalize_name(table_name)

    rows: List[Dict[str, Any]] = []
    tables_payload = payload.get("tables")
    if isinstance(tables_payload, dict) and normalized_table:
        table_section = tables_payload.get(normalized_table)
        if not isinstance(table_section, dict):
            for key, candidate in tables_payload.items():
                if _normalize_name(key) == normalized_table and isinstance(candidate, dict):
                    table_section = candidate
                    break
        if isinstance(table_section, dict):
            section_rows = table_section.get("rows", [])
            if isinstance(section_rows, list):
                rows = section_rows

    if not rows:
        migration_item = payload.get("migrationItem")
        legacy_object = payload.get("object")
        schema_meta = payload.get("schema")
        if not isinstance(migration_item, dict):
            migration_item = {}
        if not isinstance(legacy_object, dict):
            legacy_object = {}
        if not isinstance(schema_meta, dict):
            schema_meta = {}

        fallback_primary_table = _normalize_name(
            migration_item.get("otmTable")
            or legacy_object.get("otmTable")
            or schema_meta.get("tableName")
            or ""
        )
        if not fallback_primary_table or fallback_primary_table == normalized_table:
            rows_raw = payload.get("rows", [])
            rows = rows_raw if isinstance(rows_raw, list) else []

    generated_at = str(payload.get("generatedAt") or "").strip()
    return rows, generated_at


def _apply_local_row_lifecycle_dates(
    normalized_rows: List[Dict[str, str]],
    *,
    schema_columns: List[str],
    output_path: Path,
    table_name: str,
    domain_name: str,
    pk_columns: List[str],
) -> None:
    has_insert_date = LOCAL_INSERT_DATE_COLUMN in set(schema_columns)
    has_update_date = LOCAL_UPDATE_DATE_COLUMN in set(schema_columns)
    if not has_insert_date and not has_update_date:
        return

    existing_rows_raw, existing_generated_at = _load_existing_cache_context(
        output_path=output_path,
        table_name=table_name,
    )

    existing_by_identity: Dict[str, List[Dict[str, str]]] = {}
    existing_by_signature: Dict[str, List[Dict[str, str]]] = {}
    for existing_row_raw in existing_rows_raw:
        if not isinstance(existing_row_raw, dict):
            continue

        existing_row = _normalize_existing_row_by_schema(existing_row_raw, schema_columns)
        identity_key = _build_object_identity_key(
            normalized_row=existing_row,
            table_name=table_name,
            domain_name=domain_name,
            pk_columns=pk_columns,
        )
        if identity_key:
            existing_by_identity.setdefault(identity_key, []).append(existing_row)

        signature = _row_signature_without_local_dates(existing_row)
        existing_by_signature.setdefault(signature, []).append(existing_row)

    now_ts = _timestamp_utc_z()
    fallback_insert_ts = existing_generated_at or now_ts

    for row in normalized_rows:
        identity_key = _build_object_identity_key(
            normalized_row=row,
            table_name=table_name,
            domain_name=domain_name,
            pk_columns=pk_columns,
        )

        previous_row: Optional[Dict[str, str]] = None
        if identity_key:
            matches = existing_by_identity.get(identity_key)
            if matches:
                previous_row = matches.pop(0)

        if previous_row is None:
            signature = _row_signature_without_local_dates(row)
            matches = existing_by_signature.get(signature)
            if matches:
                previous_row = matches.pop(0)

        if has_insert_date:
            if previous_row is not None:
                previous_insert = str(previous_row.get(LOCAL_INSERT_DATE_COLUMN) or "").strip()
                row[LOCAL_INSERT_DATE_COLUMN] = previous_insert or fallback_insert_ts
            else:
                row[LOCAL_INSERT_DATE_COLUMN] = now_ts

        if has_update_date:
            if previous_row is not None:
                previous_update = str(previous_row.get(LOCAL_UPDATE_DATE_COLUMN) or "").strip()
                previous_signature = _row_signature_without_local_dates(previous_row)
                current_signature = _row_signature_without_local_dates(row)
                row[LOCAL_UPDATE_DATE_COLUMN] = now_ts if current_signature != previous_signature else previous_update
            else:
                row[LOCAL_UPDATE_DATE_COLUMN] = ""


def _query_rows(sql_query: str, root_name: str) -> List[Dict[str, Any]]:
    context = {
        "sql_param_name": "sqlQuery",
        "request_params": {"rootName": root_name},
        "timeout": QUERY_TIMEOUT_SECONDS,
    }
    result = execute_otm_query(sql_query, "SQL", context, "json")
    if result.get("status") != "success":
        raise RuntimeError(result.get("error_message") or "Falha ao consultar OTM.")

    payload = result.get("payload")
    if not isinstance(payload, dict):
        raise RuntimeError("Resposta OTM sem payload JSON.")
    return _extract_transaction_rows(payload, root_name)


def _build_output_path(
    *,
    domain_name: str,
    table_name: str,
    migration_group_id: str,
    migration_item_id: str,
    migration_item_name: str,
    sequence: Any,
) -> Path:
    domain_token = _slugify(domain_name or "NO_DOMAIN")
    table_token = _slugify(table_name or "NO_TABLE")
    group_token = _short_slug(migration_group_id or "NO_GROUP", 18)
    name_token = _short_slug(migration_item_name or "ITEM", 24)
    sequence_token = re.sub(r"[^0-9]+", "", str(sequence or "").strip()) or "0"

    # Sem hash: nome curto e determinístico.
    filename = f"{domain_token}_{table_token}_{name_token}_{sequence_token}_{group_token}.json"
    return CACHE_DIR / filename


def _remove_stale_cache_files_for_item(
    *,
    migration_item_id: str,
    keep_path: Path,
    dry_run: bool,
) -> int:
    migration_item_id = str(migration_item_id or "").strip()
    if not migration_item_id or not CACHE_DIR.exists():
        return 0

    removed = 0
    for cache_file in CACHE_DIR.glob("*.json"):
        if cache_file.resolve() == keep_path.resolve():
            continue
        if not cache_file.is_file():
            continue

        try:
            payload = json.loads(cache_file.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(payload, dict):
            continue

        migration_item = payload.get("migrationItem", {})
        if not isinstance(migration_item, dict):
            migration_item = {}
        current_item_id = str(migration_item.get("migrationItemId") or "").strip()
        if current_item_id != migration_item_id:
            continue

        removed += 1
        if not dry_run:
            cache_file.unlink(missing_ok=True)

    return removed


def _build_table_cache_section(
    *,
    table_name: str,
    table_schema: Dict[str, Any],
    schema_columns: List[str],
    query_language: str,
    query_source: str,
    sql_query: str,
    normalized_rows: List[Dict[str, str]],
    extra_fields: List[str],
) -> Dict[str, Any]:
    table_meta = table_schema.get("table", {}) if isinstance(table_schema, dict) else {}
    return {
        "tableName": table_name,
        "schema": {
            "owner": str(table_meta.get("schema") or ""),
            "tableName": str(table_meta.get("name") or table_name.lower()),
            "columnCount": len(schema_columns),
            "columns": schema_columns,
        },
        "extraction": {
            "queryLanguage": query_language,
            "querySource": query_source,
            "rootName": table_name,
            "query": sql_query,
            "normalizedRowCount": len(normalized_rows),
            "nonSchemaFieldsDetected": extra_fields,
        },
        "rows": normalized_rows,
    }


def _build_cache_payload(
    group_id: str,
    obj: Dict[str, Any],
    primary_table_name: str,
    sql_query: str,
    query_language: str,
    query_source: str,
    table_sections: Dict[str, Dict[str, Any]],
    skipped_subtables_no_schema: List[str],
) -> Dict[str, Any]:
    primary_table = _normalize_name(primary_table_name)
    if primary_table not in table_sections and table_sections:
        primary_table = next(iter(table_sections.keys()))

    primary_section = table_sections.get(primary_table, {})
    if not isinstance(primary_section, dict):
        primary_section = {}

    primary_schema = primary_section.get("schema", {})
    if not isinstance(primary_schema, dict):
        primary_schema = {}
    primary_extraction = primary_section.get("extraction", {})
    if not isinstance(primary_extraction, dict):
        primary_extraction = {}
    primary_rows_raw = primary_section.get("rows", [])
    primary_rows = primary_rows_raw if isinstance(primary_rows_raw, list) else []

    all_table_names = list(table_sections.keys())
    subtable_names = [table for table in all_table_names if table != primary_table]

    migration_group_id = _normalize_name(
        obj.get(MIGRATION_GROUP_ID_KEY) or group_id
    )
    migration_item_name = str(
        obj.get(MIGRATION_ITEM_NAME_KEY) or obj.get("name") or ""
    ).strip()
    migration_item_id = str(obj.get(MIGRATION_ITEM_ID_KEY) or "").strip()
    if not migration_item_id:
        migration_item_id = _build_migration_item_id(
            migration_group_id,
            {
                **obj,
                "name": migration_item_name,
            },
        )

    migration_item_payload = {
        "migrationItemId": migration_item_id,
        "migrationItemName": migration_item_name,
        "migrationGroupId": migration_group_id,
        "objectType": str(obj.get("object_type") or ""),
        "otmTable": primary_table,
        "otmSubtables": subtable_names,
        "domainName": str(obj.get("domainName") or obj.get("domain") or ""),
        "sequence": obj.get("sequence"),
        "deploymentType": str(obj.get("deployment_type") or ""),
    }

    return {
        "cacheType": "OTM_OBJECT_CACHE",
        "version": "1.0",
        "generatedAt": _timestamp_utc_z(),
        "source": SCRIPT_NAME,
        "migrationItem": migration_item_payload,
        # Compatibilidade retroativa: manter estrutura legado "object"
        "object": {
            "name": migration_item_payload["migrationItemName"],
            "groupId": migration_item_payload["migrationGroupId"],
            "objectType": migration_item_payload["objectType"],
            "otmTable": migration_item_payload["otmTable"],
            "domainName": migration_item_payload["domainName"],
            "sequence": migration_item_payload["sequence"],
            "deploymentType": migration_item_payload["deploymentType"],
        },
        "extraction": {
            "objectExtractionQueryLanguage": query_language,
            "objectExtractionQuerySource": query_source,
            # Compatibilidade retroativa
            "technicalContentType": str(
                obj.get("technical_content", {}).get("type", "")
                if isinstance(obj.get("technical_content"), dict)
                else ""
            ),
            "rootName": primary_table,
            "query": sql_query,
            "normalizedRowCount": int(primary_extraction.get("normalizedRowCount") or len(primary_rows)),
            "nonSchemaFieldsDetected": primary_extraction.get("nonSchemaFieldsDetected", []),
            "tableCount": len(all_table_names),
            "tableNames": all_table_names,
            "skippedSubtablesNoSchema": skipped_subtables_no_schema,
        },
        "tableHierarchy": {
            "primaryTable": primary_table,
            "subtables": subtable_names,
            "allTables": all_table_names,
            "skippedSubtablesNoSchema": skipped_subtables_no_schema,
        },
        "tables": table_sections,
        # Compatibilidade retroativa com leitores que ainda usam formato legado.
        "schema": primary_schema,
        "rows": primary_rows,
    }


def _write_output(path: Path, payload: Dict[str, Any], dry_run: bool) -> None:
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _iter_cache_files() -> List[Path]:
    if not CACHE_DIR.exists():
        return []
    return sorted(path for path in CACHE_DIR.glob("*.json") if path.is_file())


def _build_row_hash(normalized_row: Dict[str, str]) -> str:
    serialized = json.dumps(normalized_row, ensure_ascii=False, sort_keys=True)
    return hashlib.sha1(serialized.encode("utf-8")).hexdigest()


def _iter_payload_table_sections(
    payload: Dict[str, Any],
    fallback_table_name: str,
) -> List[Tuple[str, List[Dict[str, Any]]]]:
    sections: List[Tuple[str, List[Dict[str, Any]]]] = []
    tables_payload = payload.get("tables")
    if isinstance(tables_payload, dict):
        for key, table_payload in tables_payload.items():
            if not isinstance(table_payload, dict):
                continue
            schema_meta = table_payload.get("schema", {})
            if not isinstance(schema_meta, dict):
                schema_meta = {}
            table_name = _normalize_name(
                table_payload.get("tableName") or schema_meta.get("tableName") or key
            )
            if not table_name:
                continue
            rows_raw = table_payload.get("rows", [])
            rows = rows_raw if isinstance(rows_raw, list) else []
            sections.append((table_name, rows))

    if sections:
        return sections

    rows_raw = payload.get("rows", [])
    rows = rows_raw if isinstance(rows_raw, list) else []
    table_name = _normalize_name(fallback_table_name)
    if not table_name:
        return []
    return [(table_name, rows)]


def _collect_substituted_migration_items_from_project() -> Tuple[Dict[str, str], Set[str]]:
    """
    Retorna mapeamento de itens substituídos no índice.

    Regra:
    - quando um MIGRATION_ITEM AUTO tem sua tabela principal marcada como subtabela
      de outro item no mesmo domínio, o item AUTO é suprimido no índice
      para evitar duplicidade com o cache do item "dono".

    Saída:
    - substitution_owner_by_item_id: {child_item_id: owner_item_id}
    - ambiguous_subtable_keys: chaves (DOMAIN|TABLE) onde mais de um dono foi definido.
    """
    try:
        project_data = _load_project()
    except Exception:
        return {}, set()

    items: List[Dict[str, Any]] = []
    for group_id, item in _iter_project_objects(project_data):
        if not isinstance(item, dict):
            continue

        migration_group_id = _normalize_name(item.get(MIGRATION_GROUP_ID_KEY) or group_id)
        migration_item_name = str(
            item.get(MIGRATION_ITEM_NAME_KEY) or item.get("name") or ""
        ).strip()
        migration_item_id = str(item.get(MIGRATION_ITEM_ID_KEY) or "").strip()
        if not migration_item_id:
            migration_item_id = _build_migration_item_id(
                migration_group_id,
                {**item, "name": migration_item_name},
            )

        primary_table = _normalize_name(item.get("otm_table") or item.get("object_type"))
        domain_name = _resolve_domain_name(item)
        if not primary_table or not domain_name:
            continue

        raw_subtables = item.get("otm_subtables")
        subtables: List[str] = []
        seen_subtables: Set[str] = set()
        if isinstance(raw_subtables, list):
            candidates = [str(value or "") for value in raw_subtables]
        elif isinstance(raw_subtables, str):
            candidates = [part.strip() for part in raw_subtables.split(",")]
        else:
            candidates = []
        for candidate in candidates:
            normalized_candidate = _normalize_name(candidate)
            if (
                not normalized_candidate
                or normalized_candidate == primary_table
                or normalized_candidate in seen_subtables
            ):
                continue
            subtables.append(normalized_candidate)
            seen_subtables.add(normalized_candidate)

        items.append(
            {
                "migrationItemId": migration_item_id,
                "migrationItemName": migration_item_name,
                "groupId": migration_group_id,
                "domainName": domain_name,
                "primaryTable": primary_table,
                "subtables": subtables,
                "sequence": int(item.get("sequence") or 0),
                "isAuto": _is_truthy(item.get("auto_generated"))
                or migration_item_name.upper().endswith("(AUTO)"),
            }
        )

    owner_by_key: Dict[str, str] = {}
    ambiguous_keys: Set[str] = set()
    owner_candidates_by_key: Dict[str, List[Dict[str, Any]]] = {}

    owners_sorted = sorted(
        items,
        key=lambda itm: (
            int(itm.get("sequence") or 0),
            str(itm.get("migrationItemId") or ""),
        ),
    )
    for owner in owners_sorted:
        owner_id = str(owner.get("migrationItemId") or "").strip()
        owner_domain = str(owner.get("domainName") or "").strip()
        if not owner_id or not owner_domain:
            continue
        for subtable in owner.get("subtables") or []:
            subtable_name = _normalize_name(subtable)
            if not subtable_name:
                continue
            key = f"{owner_domain}|{subtable_name}"
            owner_candidates_by_key.setdefault(key, []).append(
                {
                    "migrationItemId": owner_id,
                    "sequence": int(owner.get("sequence") or 0),
                    "subtableCount": len(owner.get("subtables") or []),
                }
            )

    for key, candidates in owner_candidates_by_key.items():
        if not candidates:
            continue
        if len(candidates) > 1:
            ambiguous_keys.add(key)
        selected_candidate = sorted(
            candidates,
            key=lambda candidate: (
                int(candidate.get("subtableCount") or 0),
                int(candidate.get("sequence") or 0),
                str(candidate.get("migrationItemId") or ""),
            ),
        )[0]
        selected_owner_id = str(selected_candidate.get("migrationItemId") or "").strip()
        if selected_owner_id:
            owner_by_key[key] = selected_owner_id

    substitution_owner_by_item_id: Dict[str, str] = {}
    for item in items:
        item_id = str(item.get("migrationItemId") or "").strip()
        if not item_id:
            continue
        if not bool(item.get("isAuto")):
            continue
        key = f"{item.get('domainName')}|{item.get('primaryTable')}"
        owner_item_id = owner_by_key.get(key)
        if not owner_item_id or owner_item_id == item_id:
            continue
        substitution_owner_by_item_id[item_id] = owner_item_id

    return substitution_owner_by_item_id, ambiguous_keys


def _build_cache_index_payload() -> Dict[str, Any]:
    cache_files = _iter_cache_files()
    substitution_owner_by_item_id, ambiguous_subtable_keys = (
        _collect_substituted_migration_items_from_project()
    )
    pk_columns_by_table: Dict[str, List[str]] = {}
    files_summary: List[Dict[str, Any]] = []
    malformed_files: List[Dict[str, str]] = []
    excluded_files_by_substitution: List[Dict[str, Any]] = []
    object_locator_by_key: Dict[str, List[Dict[str, Any]]] = {}
    unverifiable_rows: List[Dict[str, Any]] = []

    total_rows = 0
    indexed_rows = 0
    total_unverifiable_rows = 0

    for cache_file in cache_files:
        relative_file = str(cache_file.relative_to(BASE_DIR))
        try:
            payload = json.loads(cache_file.read_text(encoding="utf-8"))
        except Exception as exc:
            malformed_files.append(
                {
                    "file": relative_file,
                    "errorMessage": str(exc),
                }
            )
            continue

        migration_item = payload.get("migrationItem", {})
        legacy_object = payload.get("object", {})
        if not isinstance(migration_item, dict):
            migration_item = {}
        if not isinstance(legacy_object, dict):
            legacy_object = {}
        schema_meta = payload.get("schema", {})
        if not isinstance(schema_meta, dict):
            schema_meta = {}

        migration_group_id = _normalize_name(
            migration_item.get("migrationGroupId") or legacy_object.get("groupId") or ""
        )
        migration_item_name = str(
            migration_item.get("migrationItemName") or legacy_object.get("name") or ""
        ).strip()
        migration_item_id = str(migration_item.get("migrationItemId") or "").strip()
        table_name = _normalize_name(
            migration_item.get("otmTable")
            or legacy_object.get("otmTable")
            or schema_meta.get("tableName")
            or ""
        )
        domain_name = _normalize_name(
            migration_item.get("domainName") or legacy_object.get("domainName") or ""
        )

        if not migration_item_id:
            migration_item_id = f"MIGRATION_ITEM.FILE.{_slugify(cache_file.stem)}"

        owner_item_id = substitution_owner_by_item_id.get(migration_item_id)
        if owner_item_id:
            excluded_files_by_substitution.append(
                {
                    "file": relative_file,
                    "migrationItemId": migration_item_id,
                    "migrationItemName": migration_item_name,
                    "migrationGroupId": migration_group_id,
                    "table": table_name,
                    "domainName": domain_name,
                    "substitutedByMigrationItemId": owner_item_id,
                }
            )
            continue

        table_sections = _iter_payload_table_sections(payload, table_name)
        if not table_name and table_sections:
            table_name = table_sections[0][0]

        file_row_count = 0
        file_indexed_count = 0
        file_unverifiable_count = 0
        file_table_summary: List[Dict[str, Any]] = []

        for section_table_name, section_rows in table_sections:
            if section_table_name not in pk_columns_by_table:
                try:
                    _, table_schema = _load_table_columns(section_table_name)
                    pk_columns_by_table[section_table_name] = _extract_primary_key_columns(table_schema)
                except Exception:
                    pk_columns_by_table[section_table_name] = []
            pk_columns = pk_columns_by_table[section_table_name]

            section_row_count = 0
            for section_row_number, row in enumerate(section_rows, start=1):
                if not isinstance(row, dict):
                    continue

                file_row_count += 1
                section_row_count += 1

                normalized_row: Dict[str, str] = {}
                for key, value in row.items():
                    normalized_key = _normalize_name(key)
                    if not normalized_key:
                        continue
                    normalized_row[normalized_key] = _stringify_value(value)

                identity_key = _build_object_identity_key(
                    normalized_row=normalized_row,
                    table_name=section_table_name,
                    domain_name=domain_name,
                    pk_columns=pk_columns,
                )

                row_locator = {
                    "file": relative_file,
                    "rowNumber": file_row_count,
                    "tableRowNumber": section_row_number,
                    "migrationItemId": migration_item_id,
                    "migrationItemName": migration_item_name,
                    "migrationGroupId": migration_group_id,
                    "table": section_table_name,
                    "domainName": domain_name,
                }

                if identity_key:
                    object_locator_by_key.setdefault(identity_key, []).append(row_locator)
                    file_indexed_count += 1
                else:
                    file_unverifiable_count += 1
                    unverifiable_rows.append(
                        {
                            **row_locator,
                            "rowHash": _build_row_hash(normalized_row),
                        }
                    )

            file_table_summary.append(
                {
                    "table": section_table_name,
                    "rowCount": section_row_count,
                }
            )

        total_rows += file_row_count
        indexed_rows += file_indexed_count
        total_unverifiable_rows += file_unverifiable_count
        files_summary.append(
            {
                "file": relative_file,
                "migrationItemId": migration_item_id,
                "migrationItemName": migration_item_name,
                "migrationGroupId": migration_group_id,
                "table": table_name,
                "domainName": domain_name,
                "rowCount": file_row_count,
                "indexedObjectRows": file_indexed_count,
                "unverifiableRows": file_unverifiable_count,
                "tableCount": len(file_table_summary),
                "tables": file_table_summary,
            }
        )

    sorted_object_locator = {
        key: sorted(
            locations,
            key=lambda loc: (str(loc.get("file") or ""), int(loc.get("rowNumber") or 0)),
        )
        for key, locations in sorted(object_locator_by_key.items())
    }

    duplicate_object_keys: List[Dict[str, Any]] = []
    for object_key, locations in sorted_object_locator.items():
        migration_item_ids = sorted(
            {
                str(loc.get("migrationItemId") or "").strip()
                for loc in locations
                if str(loc.get("migrationItemId") or "").strip()
            }
        )
        if len(migration_item_ids) <= 1:
            continue
        duplicate_object_keys.append(
            {
                "objectKey": object_key,
                "migrationItemIds": migration_item_ids,
                "occurrences": locations,
            }
        )

    return {
        "cacheType": "OTM_OBJECT_CACHE_INDEX",
        "version": "1.0",
        "generatedAt": _timestamp_utc_z(),
        "source": SCRIPT_NAME,
        "objectLocatorByKey": sorted_object_locator,
        "unverifiableRows": sorted(
            unverifiable_rows,
            key=lambda row: (str(row.get("file") or ""), int(row.get("rowNumber") or 0)),
        ),
        "files": sorted(files_summary, key=lambda item: str(item.get("file") or "")),
        "excludedCacheFilesBySubstitution": sorted(
            excluded_files_by_substitution, key=lambda item: str(item.get("file") or "")
        ),
        "substitutionRules": {
            "substitutedMigrationItems": sorted(
                [
                    {
                        "migrationItemId": child_id,
                        "substitutedByMigrationItemId": owner_id,
                    }
                    for child_id, owner_id in substitution_owner_by_item_id.items()
                ],
                key=lambda item: str(item.get("migrationItemId") or ""),
            ),
            "ambiguousSubtableKeys": sorted(ambiguous_subtable_keys),
        },
        "duplicatesAcrossMigrationItems": duplicate_object_keys,
        "malformedCacheFiles": sorted(
            malformed_files, key=lambda item: str(item.get("file") or "")
        ),
        "stats": {
            "cacheFileCount": len(cache_files),
            "validCacheFileCount": len(files_summary),
            "excludedBySubstitutionCacheFileCount": len(excluded_files_by_substitution),
            "malformedCacheFileCount": len(malformed_files),
            "totalRows": total_rows,
            "indexedObjectRows": indexed_rows,
            "unverifiableRows": total_unverifiable_rows,
            "uniqueObjectKeys": len(sorted_object_locator),
            "duplicateObjectKeysAcrossMigrationItems": len(duplicate_object_keys),
        },
    }


def _write_cache_index(dry_run: bool) -> Dict[str, Any]:
    index_payload = _build_cache_index_payload()
    if not dry_run:
        CACHE_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
        CACHE_INDEX_PATH.write_text(
            json.dumps(index_payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return index_payload


def _extract_single_object_cache(
    group_id: str,
    obj: Dict[str, Any],
    dry_run: bool,
    strict_extractability: bool,
) -> Dict[str, Any]:
    migration_group_id = _normalize_name(obj.get(MIGRATION_GROUP_ID_KEY) or group_id)
    migration_item_name = str(
        obj.get(MIGRATION_ITEM_NAME_KEY) or obj.get("name") or ""
    ).strip()
    migration_item_id = str(obj.get(MIGRATION_ITEM_ID_KEY) or "").strip()
    if not migration_item_id:
        migration_item_id = _build_migration_item_id(
            migration_group_id,
            {
                **obj,
                "name": migration_item_name,
            },
        )

    domain_name = _resolve_domain_name(obj)
    if not domain_name:
        if strict_extractability:
            raise ValueError(
                f"MIGRATION_ITEM '{migration_item_name}' sem dominio valido (domainName/domain)."
            )
        return {
            "status": "skipped",
            "migrationGroupId": migration_group_id,
            "migrationItemId": migration_item_id,
            "migrationItem": migration_item_name,
            # Compatibilidade retroativa
            "groupId": migration_group_id,
            "object": migration_item_name,
            "reason": "item sem dominio valido",
        }

    query_language, sql_query, query_source = _resolve_object_extraction_query(obj)
    if _normalize_name(query_language) != "SQL":
        if strict_extractability:
            raise ValueError(
                f"MIGRATION_ITEM '{migration_item_name}' sem object_extraction_query.language=SQL."
            )
        return {
            "status": "skipped",
            "migrationGroupId": migration_group_id,
            "migrationItemId": migration_item_id,
            "migrationItem": migration_item_name,
            # Compatibilidade retroativa
            "groupId": migration_group_id,
            "object": migration_item_name,
            "reason": "object_extraction_query.language diferente de SQL",
        }
    if not sql_query:
        if strict_extractability:
            raise ValueError(f"MIGRATION_ITEM '{migration_item_name}' sem object_extraction_query.content.")
        return {
            "status": "skipped",
            "migrationGroupId": migration_group_id,
            "migrationItemId": migration_item_id,
            "migrationItem": migration_item_name,
            # Compatibilidade retroativa
            "groupId": migration_group_id,
            "object": migration_item_name,
            "reason": "object_extraction_query.content vazio",
        }

    primary_table_name = _normalize_name(obj.get("otm_table"))
    if not primary_table_name:
        raise ValueError(
            f"MIGRATION_ITEM '{migration_item_name}' sem tabela principal definida em otm_table."
        )

    target_tables = _resolve_item_tables(obj, primary_table_name, sql_query)
    output_path = _build_output_path(
        domain_name=domain_name,
        table_name=primary_table_name,
        migration_group_id=migration_group_id,
        migration_item_id=migration_item_id,
        migration_item_name=migration_item_name,
        sequence=obj.get("sequence"),
    )

    table_sections: Dict[str, Dict[str, Any]] = {}
    table_rows_by_name: Dict[str, int] = {}
    table_unverifiable_by_name: Dict[str, int] = {}
    skipped_subtables_no_schema: List[str] = []
    primary_object_identity_keys: Set[str] = set()

    normalized_query_language = _normalize_name(query_language) or "SQL"
    for current_table_name in target_tables:
        try:
            schema_columns, table_schema = _load_table_columns(current_table_name)
        except FileNotFoundError:
            if current_table_name == primary_table_name:
                raise
            skipped_subtables_no_schema.append(current_table_name)
            continue

        pk_columns = _extract_primary_key_columns(table_schema)
        raw_rows = _query_rows(sql_query, root_name=current_table_name)

        normalized_rows: List[Dict[str, str]] = []
        extra_fields_union: Set[str] = set()
        table_unverifiable_count = 0
        for row in raw_rows:
            normalized_row, row_extra_fields = _normalize_row_by_schema(row, schema_columns)
            normalized_rows.append(normalized_row)
            extra_fields_union.update(row_extra_fields)

            identity_key = _build_object_identity_key(
                normalized_row=normalized_row,
                table_name=current_table_name,
                domain_name=domain_name,
                pk_columns=pk_columns,
            )
            if identity_key:
                if current_table_name == primary_table_name:
                    primary_object_identity_keys.add(identity_key)
            else:
                table_unverifiable_count += 1

        _apply_local_row_lifecycle_dates(
            normalized_rows,
            schema_columns=schema_columns,
            output_path=output_path,
            table_name=current_table_name,
            domain_name=domain_name,
            pk_columns=pk_columns,
        )

        table_sections[current_table_name] = _build_table_cache_section(
            table_name=current_table_name,
            table_schema=table_schema,
            schema_columns=schema_columns,
            query_language=normalized_query_language,
            query_source=query_source,
            sql_query=sql_query,
            normalized_rows=normalized_rows,
            extra_fields=sorted(extra_fields_union),
        )
        table_rows_by_name[current_table_name] = len(normalized_rows)
        table_unverifiable_by_name[current_table_name] = table_unverifiable_count

    payload = _build_cache_payload(
        group_id=migration_group_id,
        obj=obj,
        primary_table_name=primary_table_name,
        sql_query=sql_query,
        query_language=normalized_query_language,
        query_source=query_source,
        table_sections=table_sections,
        skipped_subtables_no_schema=sorted(skipped_subtables_no_schema),
    )
    _write_output(output_path, payload, dry_run=dry_run)
    stale_files_removed = _remove_stale_cache_files_for_item(
        migration_item_id=migration_item_id,
        keep_path=output_path,
        dry_run=dry_run,
    )

    primary_rows = int(table_rows_by_name.get(primary_table_name) or 0)
    total_rows = int(sum(table_rows_by_name.values()))
    total_unverifiable_rows = int(sum(table_unverifiable_by_name.values()))
    processed_tables = list(table_sections.keys())
    processed_subtables = [table for table in processed_tables if table != primary_table_name]

    return {
        "status": "success",
        "migrationGroupId": migration_group_id,
        "migrationItemId": migration_item_id,
        "migrationItem": migration_item_name,
        # Compatibilidade retroativa
        "groupId": migration_group_id,
        "object": migration_item_name,
        "table": primary_table_name,
        "rows": primary_rows,
        "unverifiableRows": total_unverifiable_rows,
        "totalRows": total_rows,
        "tableRows": table_rows_by_name,
        "tablesProcessed": processed_tables,
        "subtablesProcessed": processed_subtables,
        "skippedSubtablesNoSchema": sorted(skipped_subtables_no_schema),
        "staleFilesRemoved": stale_files_removed,
        "objectIdentityKeys": sorted(primary_object_identity_keys),
        "file": str(output_path.relative_to(BASE_DIR)),
    }


def _parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extrai MIGRATION_ITEMs do projeto e grava cache local em JSON "
            "(1 arquivo por MIGRATION_ITEM)."
        )
    )
    parser.add_argument(
        "--all-migration-items",
        action="store_true",
        help="Atualiza cache de todos os MIGRATION_ITEMs do projeto.",
    )
    parser.add_argument(
        "--all-objects",
        action="store_true",
        help="Alias legado de --all-migration-items.",
    )
    parser.add_argument(
        "--migration-item-id",
        default="",
        help="ID canônico do MIGRATION_ITEM (migration_item_id).",
    )
    parser.add_argument(
        "--migration-item-name",
        default="",
        help="Nome exato do MIGRATION_ITEM em domain/projeto_migracao/projeto_migracao.json.",
    )
    parser.add_argument(
        "--object-name",
        default="",
        help="Alias legado de --migration-item-name.",
    )
    parser.add_argument(
        "--migration-group-id",
        default="",
        help=(
            "Escopo de MIGRATION_GROUP (quando --migration-item-name nao for informado) "
            "ou desambiguacao de MIGRATION_GROUP para --migration-item-name."
        ),
    )
    parser.add_argument(
        "--group-id",
        default="",
        help="Alias legado de --migration-group-id.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Executa extracao e validacao sem gravar arquivos de cache.",
    )
    args = parser.parse_args(argv)

    args.resolved_all = bool(args.all_migration_items or args.all_objects)
    args.resolved_migration_item_id = str(args.migration_item_id or "").strip()
    args.resolved_migration_item_name = str(
        args.migration_item_name or args.object_name or ""
    ).strip()
    args.resolved_migration_group_id = str(
        args.migration_group_id or args.group_id or ""
    ).strip()

    has_all = bool(args.resolved_all)
    has_item_id = bool(args.resolved_migration_item_id)
    has_item_name = bool(args.resolved_migration_item_name)
    has_group = bool(args.resolved_migration_group_id)

    if sum([has_all, has_item_id, has_item_name, has_group]) == 0:
        parser.error(
            "Informe um escopo: --all-migration-items, "
            "--migration-item-id, --migration-item-name ou --migration-group-id."
        )
    if has_all and (has_item_id or has_item_name or has_group):
        parser.error(
            "--all-migration-items nao pode ser combinado com "
            "--migration-item-id/--migration-item-name/--migration-group-id."
        )
    if has_item_id and (has_item_name or has_group):
        parser.error(
            "--migration-item-id nao pode ser combinado com "
            "--migration-item-name/--migration-group-id."
        )

    return args


def main(argv: List[str]) -> int:
    args = _parse_args(argv)

    try:
        project_data = _load_project()
        mode = ""
        targets: List[Tuple[str, Dict[str, Any]]] = []
        strict_extractability = False

        if args.resolved_all:
            mode = "all_migration_items"
            targets = list(_iter_project_objects(project_data))
            strict_extractability = False
        elif args.resolved_migration_item_id:
            mode = "single_migration_item"
            targets = [
                _select_object_by_migration_item_id(
                    project_data,
                    migration_item_id=args.resolved_migration_item_id,
                )
            ]
            strict_extractability = True
        elif args.resolved_migration_item_name:
            mode = "single_migration_item"
            targets = [
                _select_object(
                    project_data,
                    migration_item_name=args.resolved_migration_item_name,
                    migration_group_id=args.resolved_migration_group_id or None,
                )
            ]
            strict_extractability = True
        else:
            mode = "migration_group_items"
            targets = _select_group_objects(
                project_data,
                migration_group_id=args.resolved_migration_group_id,
            )
            strict_extractability = False

        processed: List[Dict[str, Any]] = []
        errors: List[Dict[str, Any]] = []
        object_key_registry: Dict[str, str] = {}
        duplicate_conflicts = 0

        for group_id, obj in targets:
            try:
                result = _extract_single_object_cache(
                    group_id=group_id,
                    obj=obj,
                    dry_run=bool(args.dry_run),
                    strict_extractability=strict_extractability,
                )
                if result.get("status") == "success":
                    current_item_id = str(result.get("migrationItemId") or "")
                    current_file_rel = str(result.get("file") or "")
                    identity_keys = result.pop("objectIdentityKeys", [])
                    if not isinstance(identity_keys, list):
                        identity_keys = []

                    duplicate_messages: List[str] = []
                    for key in identity_keys:
                        if not isinstance(key, str) or not key:
                            continue
                        owner_item_id = object_key_registry.get(key)
                        if owner_item_id and owner_item_id != current_item_id:
                            duplicate_messages.append(
                                f"Objeto duplicado entre itens: key='{key}' "
                                f"(owner='{owner_item_id}', current='{current_item_id}')."
                            )
                            continue
                        object_key_registry[key] = current_item_id

                    if duplicate_messages:
                        duplicate_conflicts += 1
                        if current_file_rel:
                            output_path = BASE_DIR / current_file_rel
                            if output_path.exists():
                                output_path.unlink()
                        raise ValueError(" ".join(duplicate_messages))

                processed.append(result)
            except Exception as exc:
                current_error = {
                    "status": "error",
                    "migrationGroupId": group_id,
                    "migrationItemId": str(obj.get(MIGRATION_ITEM_ID_KEY) or ""),
                    "migrationItem": str(
                        obj.get(MIGRATION_ITEM_NAME_KEY) or obj.get("name") or ""
                    ),
                    # Compatibilidade retroativa
                    "groupId": group_id,
                    "object": str(obj.get("name") or ""),
                    "error_message": str(exc),
                }
                errors.append(current_error)
                if strict_extractability:
                    raise

        success_count = sum(1 for item in processed if item.get("status") == "success")
        skipped_count = sum(1 for item in processed if item.get("status") == "skipped")
        cache_index_summary: Dict[str, Any] = {
            "updated": False,
            "file": str(CACHE_INDEX_PATH.relative_to(BASE_DIR)),
        }
        if not args.dry_run:
            index_payload = _write_cache_index(dry_run=False)
            stats = index_payload.get("stats", {})
            if not isinstance(stats, dict):
                stats = {}
            cache_index_summary = {
                "updated": True,
                "file": str(CACHE_INDEX_PATH.relative_to(BASE_DIR)),
                "cacheFileCount": int(stats.get("cacheFileCount") or 0),
                "validCacheFileCount": int(stats.get("validCacheFileCount") or 0),
                "indexedObjectRows": int(stats.get("indexedObjectRows") or 0),
                "unverifiableRows": int(stats.get("unverifiableRows") or 0),
                "duplicateObjectKeysAcrossMigrationItems": int(
                    stats.get("duplicateObjectKeysAcrossMigrationItems") or 0
                ),
            }

        summary = {
            "status": "success" if not errors else "partial_success",
            "mode": mode,
            "dryRun": bool(args.dry_run),
            "selectedMigrationItems": len(targets),
            "successMigrationItems": success_count,
            "skippedMigrationItems": skipped_count,
            "errorMigrationItems": len(errors),
            "duplicateObjectConflicts": duplicate_conflicts,
            # Compatibilidade retroativa
            "selectedObjects": len(targets),
            "successCount": success_count,
            "skippedCount": skipped_count,
            "errorCount": len(errors),
            "cacheIndex": cache_index_summary,
            "results": processed,
            "errors": errors,
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))

        return 0 if not errors else 1
    except Exception as exc:
        print(json.dumps({"status": "error", "error_message": str(exc)}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
