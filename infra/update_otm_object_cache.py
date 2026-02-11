#!/usr/bin/env python3
"""
Build local OTM object cache files from projeto_migracao migration items.

Core rules:
- Extraction query comes from technical_content.content.
- ROOT_NAME always matches migration item otm_table.
- Output rows always contain every column from metadata/otm/tables/<TABLE>.json.
- Missing values in OTM response are filled with empty string.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set, Tuple

try:
    from infra.otm_query_executor import execute_otm_query
except ModuleNotFoundError:
    from otm_query_executor import execute_otm_query  # type: ignore


BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_PATH = BASE_DIR / "domain" / "projeto_migracao" / "projeto_migracao.json"
TABLES_DIR = BASE_DIR / "metadata" / "otm" / "tables"
CACHE_DIR = BASE_DIR / "metadata" / "otm" / "cache" / "objects"
SCRIPT_NAME = "update_otm_object_cache.py"
QUERY_TIMEOUT_SECONDS = 300
MIGRATION_GROUP_ID_KEY = "migration_group_id"
MIGRATION_ITEM_ID_KEY = "migration_item_id"
MIGRATION_ITEM_NAME_KEY = "migration_item_name"


def _timestamp_utc_z() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_name(value: Any) -> str:
    return str(value or "").strip().upper()


def _slugify(value: Any) -> str:
    raw = str(value or "").strip().upper()
    slug = re.sub(r"[^A-Z0-9]+", "_", raw).strip("_")
    return slug or "OBJECT"


def _build_migration_item_id(group_id: str, item: Dict[str, Any]) -> str:
    group_token = _slugify(group_id or "NO_GROUP")
    table_token = _slugify(item.get("otm_table") or item.get("object_type") or "NO_TABLE")
    name_token = _slugify(item.get("name") or item.get(MIGRATION_ITEM_NAME_KEY) or "NO_NAME")
    sequence = str(item.get("sequence") or "0").strip() or "0"
    return f"MIGRATION_ITEM.{group_token}.{table_token}.{name_token}.{sequence}"


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


def _build_output_path(obj: Dict[str, Any], table_name: str) -> Path:
    domain_name = str(obj.get("domainName") or obj.get("domain") or "NO_DOMAIN")
    migration_item_token = _slugify(
        obj.get(MIGRATION_ITEM_ID_KEY)
        or obj.get(MIGRATION_ITEM_NAME_KEY)
        or obj.get("name")
        or obj.get("object_type")
        or "MIGRATION_ITEM"
    )
    filename = "__".join(
        [
            _slugify(domain_name),
            _slugify(table_name),
            migration_item_token,
        ]
    ) + ".json"
    return CACHE_DIR / filename


def _build_cache_payload(
    group_id: str,
    obj: Dict[str, Any],
    table_name: str,
    table_schema: Dict[str, Any],
    schema_columns: List[str],
    sql_query: str,
    normalized_rows: List[Dict[str, str]],
    extra_fields: List[str],
) -> Dict[str, Any]:
    table_meta = table_schema.get("table", {}) if isinstance(table_schema, dict) else {}
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
        "otmTable": table_name,
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
            "technicalContentType": str(obj.get("technical_content", {}).get("type", "")),
            "rootName": table_name,
            "query": sql_query,
            "normalizedRowCount": len(normalized_rows),
            "nonSchemaFieldsDetected": extra_fields,
        },
        "schema": {
            "owner": str(table_meta.get("schema") or ""),
            "tableName": str(table_meta.get("name") or table_name.lower()),
            "columnCount": len(schema_columns),
            "columns": schema_columns,
        },
        "rows": normalized_rows,
    }


def _write_output(path: Path, payload: Dict[str, Any], dry_run: bool) -> None:
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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

    technical_content = obj.get("technical_content", {})
    if not isinstance(technical_content, dict):
        if strict_extractability:
            raise ValueError(f"MIGRATION_ITEM '{migration_item_name}' sem technical_content valido.")
        return {
            "status": "skipped",
            "migrationGroupId": migration_group_id,
            "migrationItemId": migration_item_id,
            "migrationItem": migration_item_name,
            # Compatibilidade retroativa
            "groupId": migration_group_id,
            "object": migration_item_name,
            "reason": "technical_content invalido",
        }

    technical_type = _normalize_name(technical_content.get("type"))
    sql_query = str(technical_content.get("content") or "").strip()
    if technical_type != "SQL":
        if strict_extractability:
            raise ValueError(
                f"MIGRATION_ITEM '{migration_item_name}' nao possui technical_content.type=SQL."
            )
        return {
            "status": "skipped",
            "migrationGroupId": migration_group_id,
            "migrationItemId": migration_item_id,
            "migrationItem": migration_item_name,
            # Compatibilidade retroativa
            "groupId": migration_group_id,
            "object": migration_item_name,
            "reason": "technical_content.type diferente de SQL",
        }
    if not sql_query:
        if strict_extractability:
            raise ValueError(f"MIGRATION_ITEM '{migration_item_name}' sem technical_content.content.")
        return {
            "status": "skipped",
            "migrationGroupId": migration_group_id,
            "migrationItemId": migration_item_id,
            "migrationItem": migration_item_name,
            # Compatibilidade retroativa
            "groupId": migration_group_id,
            "object": migration_item_name,
            "reason": "technical_content.content vazio",
        }

    table_name = _normalize_name(obj.get("otm_table"))
    schema_columns, table_schema = _load_table_columns(table_name)

    raw_rows = _query_rows(sql_query, root_name=table_name)

    normalized_rows: List[Dict[str, str]] = []
    extra_fields_union: Set[str] = set()
    for row in raw_rows:
        normalized_row, row_extra_fields = _normalize_row_by_schema(row, schema_columns)
        normalized_rows.append(normalized_row)
        extra_fields_union.update(row_extra_fields)

    payload = _build_cache_payload(
        group_id=migration_group_id,
        obj=obj,
        table_name=table_name,
        table_schema=table_schema,
        schema_columns=schema_columns,
        sql_query=sql_query,
        normalized_rows=normalized_rows,
        extra_fields=sorted(extra_fields_union),
    )
    output_path = _build_output_path(obj, table_name)
    _write_output(output_path, payload, dry_run=dry_run)

    return {
        "status": "success",
        "migrationGroupId": migration_group_id,
        "migrationItemId": migration_item_id,
        "migrationItem": migration_item_name,
        # Compatibilidade retroativa
        "groupId": migration_group_id,
        "object": migration_item_name,
        "table": table_name,
        "rows": len(normalized_rows),
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

        for group_id, obj in targets:
            try:
                result = _extract_single_object_cache(
                    group_id=group_id,
                    obj=obj,
                    dry_run=bool(args.dry_run),
                    strict_extractability=strict_extractability,
                )
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

        summary = {
            "status": "success" if not errors else "partial_success",
            "mode": mode,
            "dryRun": bool(args.dry_run),
            "selectedMigrationItems": len(targets),
            "successMigrationItems": success_count,
            "skippedMigrationItems": skipped_count,
            "errorMigrationItems": len(errors),
            # Compatibilidade retroativa
            "selectedObjects": len(targets),
            "successCount": success_count,
            "skippedCount": skipped_count,
            "errorCount": len(errors),
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
