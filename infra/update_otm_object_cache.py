#!/usr/bin/env python3
"""
Build local OTM object cache files from projeto_migracao objects.

Core rules:
- Extraction query comes from technical_content.content.
- ROOT_NAME always matches object otm_table.
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


def _timestamp_utc_z() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_name(value: Any) -> str:
    return str(value or "").strip().upper()


def _slugify(value: Any) -> str:
    raw = str(value or "").strip().upper()
    slug = re.sub(r"[^A-Z0-9]+", "_", raw).strip("_")
    return slug or "OBJECT"


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
        group_id = str(group.get("group_id") or "")
        objects = group.get("objects", [])
        if not isinstance(objects, list):
            continue
        for obj in objects:
            if isinstance(obj, dict):
                pairs.append((group_id, obj))
    return pairs


def _select_object(
    project_data: Dict[str, Any],
    object_name: str,
    group_id: str | None,
) -> Tuple[str, Dict[str, Any]]:
    target_name = object_name.strip().lower()
    target_group = _normalize_name(group_id) if group_id else ""

    matches: List[Tuple[str, Dict[str, Any]]] = []
    for current_group_id, obj in _iter_project_objects(project_data):
        current_name = str(obj.get("name") or "").strip().lower()
        if current_name != target_name:
            continue
        if target_group and _normalize_name(current_group_id) != target_group:
            continue
        matches.append((current_group_id, obj))

    if not matches:
        raise ValueError(
            "Objeto nao encontrado no projeto. "
            f"name={object_name!r}, group_id={group_id!r}"
        )

    if len(matches) > 1:
        labels = ", ".join(
            f"{str(obj.get('name') or '')} [group={gid}]"
            for gid, obj in matches
        )
        raise ValueError(
            "Mais de um objeto encontrado com esse nome. "
            "Informe --group-id para desambiguar. "
            f"Candidatos: {labels}"
        )

    return matches[0]


def _select_group_objects(
    project_data: Dict[str, Any],
    group_id: str,
) -> List[Tuple[str, Dict[str, Any]]]:
    target_group = _normalize_name(group_id)
    if not target_group:
        raise ValueError("group_id vazio.")

    matches: List[Tuple[str, Dict[str, Any]]] = []
    for current_group_id, obj in _iter_project_objects(project_data):
        if _normalize_name(current_group_id) != target_group:
            continue
        matches.append((current_group_id, obj))

    if not matches:
        raise ValueError(f"Nenhum objeto encontrado para o grupo '{group_id}'.")
    return matches


def _load_table_columns(table_name: str) -> Tuple[List[str], Dict[str, Any]]:
    normalized_table = _normalize_name(table_name)
    if not normalized_table:
        raise ValueError("Objeto sem otm_table definido.")

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
    filename = "__".join(
        [
            _slugify(domain_name),
            _slugify(table_name),
            _slugify(obj.get("name") or obj.get("object_type") or "OBJECT"),
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
    return {
        "cacheType": "OTM_OBJECT_CACHE",
        "version": "1.0",
        "generatedAt": _timestamp_utc_z(),
        "source": SCRIPT_NAME,
        "object": {
            "name": str(obj.get("name") or ""),
            "groupId": group_id,
            "objectType": str(obj.get("object_type") or ""),
            "otmTable": table_name,
            "domainName": str(obj.get("domainName") or obj.get("domain") or ""),
            "sequence": obj.get("sequence"),
            "deploymentType": str(obj.get("deployment_type") or ""),
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
    object_name = str(obj.get("name") or "")
    technical_content = obj.get("technical_content", {})
    if not isinstance(technical_content, dict):
        if strict_extractability:
            raise ValueError(f"Objeto '{object_name}' sem technical_content valido.")
        return {
            "status": "skipped",
            "groupId": group_id,
            "object": object_name,
            "reason": "technical_content invalido",
        }

    technical_type = _normalize_name(technical_content.get("type"))
    sql_query = str(technical_content.get("content") or "").strip()
    if technical_type != "SQL":
        if strict_extractability:
            raise ValueError(
                f"Objeto '{object_name}' nao possui technical_content.type=SQL."
            )
        return {
            "status": "skipped",
            "groupId": group_id,
            "object": object_name,
            "reason": "technical_content.type diferente de SQL",
        }
    if not sql_query:
        if strict_extractability:
            raise ValueError(f"Objeto '{object_name}' sem technical_content.content.")
        return {
            "status": "skipped",
            "groupId": group_id,
            "object": object_name,
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
        group_id=group_id,
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
        "groupId": group_id,
        "object": object_name,
        "table": table_name,
        "rows": len(normalized_rows),
        "file": str(output_path.relative_to(BASE_DIR)),
    }


def _parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extrai objetos do projeto e grava cache local em JSON "
            "(1 arquivo por objeto)."
        )
    )
    parser.add_argument(
        "--all-objects",
        action="store_true",
        help="Atualiza cache de todos os objetos do projeto.",
    )
    parser.add_argument(
        "--object-name",
        default="",
        help="Nome exato do objeto em domain/projeto_migracao/projeto_migracao.json",
    )
    parser.add_argument(
        "--group-id",
        default="",
        help=(
            "Escopo de grupo (quando --object-name nao for informado) "
            "ou desambiguacao de grupo para --object-name."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Executa extracao e validacao sem gravar arquivos de cache.",
    )
    args = parser.parse_args(argv)

    has_all = bool(args.all_objects)
    has_object = bool(str(args.object_name).strip())
    has_group = bool(str(args.group_id).strip())

    if sum([has_all, has_object, has_group]) == 0:
        parser.error("Informe um escopo: --all-objects, --group-id ou --object-name.")
    if has_all and (has_object or has_group):
        parser.error("--all-objects nao pode ser combinado com --group-id/--object-name.")

    return args


def main(argv: List[str]) -> int:
    args = _parse_args(argv)

    try:
        project_data = _load_project()
        mode = ""
        targets: List[Tuple[str, Dict[str, Any]]] = []
        strict_extractability = False

        if args.all_objects:
            mode = "all_objects"
            targets = list(_iter_project_objects(project_data))
            strict_extractability = False
        elif str(args.object_name).strip():
            mode = "single_object"
            targets = [
                _select_object(
                    project_data,
                    object_name=args.object_name,
                    group_id=args.group_id or None,
                )
            ]
            strict_extractability = True
        else:
            mode = "group_objects"
            targets = _select_group_objects(project_data, group_id=args.group_id)
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
