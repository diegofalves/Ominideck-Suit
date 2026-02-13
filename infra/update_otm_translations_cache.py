#!/usr/bin/env python3
"""
Extrai o conjunto completo de traducoes OTM (TRANSLATION + TRANSLATION_D)
e salva em cache local JSON.

Regra principal:
- Nao aplica filtro de dominio (sem LIKE '%BAU%').
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from infra.otm_query_executor import execute_otm_query
except ModuleNotFoundError:
    from otm_query_executor import execute_otm_query  # type: ignore


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    BASE_DIR / "metadata" / "otm" / "cache" / "translations" / "otm_translations.json"
)
DEFAULT_INDEX_OUTPUT_PATH = (
    BASE_DIR / "metadata" / "otm" / "cache" / "translations" / "otm_translations_index.json"
)
SCRIPT_NAME = "update_otm_translations_cache.py"
DEFAULT_ROOT_NAME = "TRANSLATION"
DEFAULT_TIMEOUT_SECONDS = 1800
DEFAULT_PAGE_SIZE = 5000

BASE_TRANSLATION_SELECT_SQL = """
SELECT
  t.TRANSLATION_GID,
  t.TRANSLATION_XID,
  t.TRANSLATION_TYPE,
  t.DOMAIN_NAME,
  td.LANG,
  td.COUNTRY,
  td.VARIANT,
  td.TEXT
FROM
  TRANSLATION t,
  TRANSLATION_D td
WHERE
  t.TRANSLATION_GID = td.TRANSLATION_GID
  AND LOWER(td.LANG) IN ('pt', 'en')
""".strip()

TRANSLATION_ORDER_BY_SQL = """
ORDER BY
  t.TRANSLATION_XID,
  td.LANG,
  td.COUNTRY,
  td.VARIANT
""".strip()

FULL_TRANSLATION_SQL = f"""
{BASE_TRANSLATION_SELECT_SQL}
{TRANSLATION_ORDER_BY_SQL}
""".strip()


def _timestamp_utc_z() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _to_oracle_timestamp(dt_utc: datetime) -> str:
    return dt_utc.strftime("%Y-%m-%d %H:%M:%S")


def _parse_generated_at(value: str) -> Optional[datetime]:
    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


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
        attrs = row.get("@attributes", {})
        if isinstance(attrs, dict):
            extracted.append(attrs)
            continue
        extracted.append({k: v for k, v in row.items() if isinstance(v, (str, int, float, bool))})

    return extracted


def _query_rows(
    sql: str,
    root_name: str,
    timeout_seconds: int,
    context_values: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    context: Dict[str, Any] = {
        "sql_param_name": "sqlQuery",
        "request_params": {"rootName": root_name},
        "timeout": timeout_seconds,
    }
    if context_values:
        context.update(context_values)

    result = execute_otm_query(sql, "SQL", context, "json")
    if result.get("status") != "success":
        raise RuntimeError(result.get("error_message") or "Falha ao consultar OTM.")

    payload = result.get("payload")
    if not isinstance(payload, dict):
        raise RuntimeError("Resposta da consulta sem payload JSON.")

    return _extract_transaction_rows(payload, root_name)


def _query_rows_paginated(
    root_name: str,
    timeout_seconds: int,
    page_size: int,
    base_select_sql: str,
    order_by_columns: List[str],
    context_values: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    if page_size <= 0:
        raise ValueError("page_size deve ser maior que zero.")

    if not order_by_columns:
        raise ValueError("order_by_columns deve conter ao menos uma coluna.")
    order_expr = ",\n      ".join(order_by_columns)

    all_rows: List[Dict[str, Any]] = []
    offset = 0
    page_index = 1

    while True:
        page_sql = f"""
SELECT *
FROM (
  SELECT inner_query.*, ROW_NUMBER() OVER (
    ORDER BY
      {order_expr}
  ) AS RN
  FROM (
    {base_select_sql}
  ) inner_query
)
WHERE RN > {offset}
  AND RN <= {offset + page_size}
ORDER BY RN
""".strip()

        rows = _query_rows(page_sql, root_name, timeout_seconds, context_values=context_values)
        if not rows:
            break

        for row in rows:
            if "RN" in row:
                row.pop("RN", None)
        all_rows.extend(rows)

        print(f"[INFO] Pagina {page_index}: +{len(rows)} linhas (acumulado={len(all_rows)})")
        if len(rows) < page_size:
            break

        offset += page_size
        page_index += 1

    return all_rows


def _escape_sql_literal(value: str) -> str:
    return value.replace("'", "''")


def _build_select_by_gid_list(gid_list: List[str]) -> str:
    quoted = ", ".join(f"'{_escape_sql_literal(gid)}'" for gid in gid_list)
    return f"""
SELECT
  t.TRANSLATION_GID,
  t.TRANSLATION_XID,
  t.TRANSLATION_TYPE,
  t.DOMAIN_NAME,
  td.LANG,
  td.COUNTRY,
  td.VARIANT,
  td.TEXT
FROM
  TRANSLATION t,
  TRANSLATION_D td
WHERE
  t.TRANSLATION_GID = td.TRANSLATION_GID
  AND LOWER(td.LANG) IN ('pt', 'en')
  AND t.TRANSLATION_GID IN ({quoted})
""".strip()


def _load_existing_payload(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return payload if isinstance(payload, dict) else None


def _extract_changed_gids_since(
    root_name: str,
    timeout_seconds: int,
    page_size: int,
    since_ts: str,
) -> List[str]:
    changed_gid_sql = """
SELECT
  t.TRANSLATION_GID
FROM
  TRANSLATION t,
  TRANSLATION_D td
WHERE
  t.TRANSLATION_GID = td.TRANSLATION_GID
  AND LOWER(td.LANG) IN ('pt', 'en')
  AND (
    NVL(td.UPDATE_DATE, td.INSERT_DATE) >= TO_DATE('$SINCE_TS', 'YYYY-MM-DD HH24:MI:SS')
    OR NVL(t.UPDATE_DATE, t.INSERT_DATE) >= TO_DATE('$SINCE_TS', 'YYYY-MM-DD HH24:MI:SS')
  )
GROUP BY
  t.TRANSLATION_GID
""".strip()

    rows = _query_rows_paginated(
        root_name,
        timeout_seconds,
        page_size,
        changed_gid_sql,
        ["inner_query.TRANSLATION_GID"],
        context_values={"SINCE_TS": since_ts},
    )

    gids = sorted({str(row.get("TRANSLATION_GID") or "").strip() for row in rows if row.get("TRANSLATION_GID")})
    return gids


def _fetch_rows_for_gid_chunks(
    root_name: str,
    timeout_seconds: int,
    gid_list: List[str],
    chunk_size: int = 500,
) -> List[Dict[str, Any]]:
    all_rows: List[Dict[str, Any]] = []
    if not gid_list:
        return all_rows

    for chunk_start in range(0, len(gid_list), chunk_size):
        chunk = gid_list[chunk_start : chunk_start + chunk_size]
        select_sql = _build_select_by_gid_list(chunk)
        rows = _query_rows(select_sql, root_name, timeout_seconds)
        all_rows.extend(rows)
        print(
            f"[INFO] Incremental chunk {chunk_start // chunk_size + 1}: "
            f"{len(chunk)} GIDs, +{len(rows)} linhas"
        )

    return all_rows


def _group_rows_by_gid(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped: Dict[str, Dict[str, Any]] = {}

    for row in rows:
        gid = str(row.get("TRANSLATION_GID") or "").strip()
        if not gid:
            continue

        bucket = grouped.get(gid)
        if bucket is None:
            bucket = {
                "TRANSLATION_GID": gid,
                "TRANSLATION_XID": row.get("TRANSLATION_XID", ""),
                "TRANSLATION_TYPE": row.get("TRANSLATION_TYPE", ""),
                "DOMAIN_NAME": row.get("DOMAIN_NAME", ""),
                "translations": [],
            }
            grouped[gid] = bucket

        bucket["translations"].append(
            {
                "LANG": row.get("LANG", ""),
                "COUNTRY": row.get("COUNTRY", ""),
                "VARIANT": row.get("VARIANT", ""),
                "TEXT": row.get("TEXT", ""),
            }
        )

    result = list(grouped.values())
    result.sort(key=lambda item: str(item.get("TRANSLATION_XID") or item.get("TRANSLATION_GID") or ""))
    return result


def _build_output_payload(rows: List[Dict[str, Any]], root_name: str, timeout_seconds: int) -> Dict[str, Any]:
    grouped_gids = _group_rows_by_gid(rows)
    return {
        "metadata": {
            "generatedAt": _timestamp_utc_z(),
            "sourceScript": SCRIPT_NAME,
            "rootName": root_name,
            "queryTimeoutSeconds": timeout_seconds,
            "translationRowCount": len(rows),
            "gidCount": len(grouped_gids),
            "query": FULL_TRANSLATION_SQL,
        },
        "gids": grouped_gids,
    }


def _build_index_payload(gids: List[Dict[str, Any]], source_file: Path) -> Dict[str, Any]:
    by_gid: Dict[str, Dict[str, Any]] = {}

    for position, item in enumerate(gids):
        gid = str(item.get("TRANSLATION_GID") or "").strip()
        if not gid:
            continue

        translations = item.get("translations", [])
        if not isinstance(translations, list):
            translations = []

        langs = sorted(
            {
                str(entry.get("LANG") or "").strip().lower()
                for entry in translations
                if isinstance(entry, dict) and str(entry.get("LANG") or "").strip()
            }
        )

        by_gid[gid] = {
            "position": position,
            "translation_xid": item.get("TRANSLATION_XID", ""),
            "translation_type": item.get("TRANSLATION_TYPE", ""),
            "domain_name": item.get("DOMAIN_NAME", ""),
            "languages": langs,
            "translation_count": len(translations),
        }

    return {
        "metadata": {
            "generatedAt": _timestamp_utc_z(),
            "sourceScript": SCRIPT_NAME,
            "sourceFile": str(source_file),
            "gidCount": len(by_gid),
        },
        "by_gid": by_gid,
    }


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Atualiza cache local completo de traducoes OTM (TRANSLATION + TRANSLATION_D)."
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help=f"Arquivo de saida JSON (padrao: {DEFAULT_OUTPUT_PATH})",
    )
    parser.add_argument(
        "--index-output",
        default=str(DEFAULT_INDEX_OUTPUT_PATH),
        help=f"Arquivo de indice JSON (padrao: {DEFAULT_INDEX_OUTPUT_PATH})",
    )
    parser.add_argument(
        "--root-name",
        default=DEFAULT_ROOT_NAME,
        help=f"Valor de rootName para DBXMLServlet (padrao: {DEFAULT_ROOT_NAME})",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"Timeout da consulta OTM em segundos (padrao: {DEFAULT_TIMEOUT_SECONDS})",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=DEFAULT_PAGE_SIZE,
        help=f"Tamanho do lote por pagina da extracao (padrao: {DEFAULT_PAGE_SIZE})",
    )
    parser.add_argument(
        "--incremental",
        action="store_true",
        help="Atualiza apenas GIDs alterados desde a ultima geracao do arquivo de saida.",
    )
    return parser.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)

    output_path = Path(args.output).expanduser().resolve()
    index_output_path = Path(args.index_output).expanduser().resolve()
    root_name = str(args.root_name).strip().upper() or DEFAULT_ROOT_NAME
    timeout_seconds = int(args.timeout)
    page_size = int(args.page_size)

    if timeout_seconds <= 0 or page_size <= 0:
        print("[ERRO] --timeout e --page-size devem ser maiores que zero.")
        return 2

    rows: List[Dict[str, Any]]
    if args.incremental:
        existing_payload = _load_existing_payload(output_path)
        if not existing_payload:
            print("[INFO] Modo incremental sem base existente. Executando carga completa.")
            rows = _query_rows_paginated(
                root_name,
                timeout_seconds,
                page_size,
                BASE_TRANSLATION_SELECT_SQL,
                [
                    "inner_query.TRANSLATION_XID",
                    "inner_query.LANG",
                    "inner_query.COUNTRY",
                    "inner_query.VARIANT",
                ],
            )
        else:
            existing_generated_at = (
                existing_payload.get("metadata", {}).get("generatedAt")
                if isinstance(existing_payload.get("metadata"), dict)
                else None
            )
            generated_at_dt = _parse_generated_at(str(existing_generated_at or ""))
            if generated_at_dt is None:
                print("[INFO] Nao foi possivel ler generatedAt da base. Executando carga completa.")
                rows = _query_rows_paginated(
                    root_name,
                    timeout_seconds,
                    page_size,
                    BASE_TRANSLATION_SELECT_SQL,
                    [
                        "inner_query.TRANSLATION_XID",
                        "inner_query.LANG",
                        "inner_query.COUNTRY",
                        "inner_query.VARIANT",
                    ],
                )
            else:
                since_ts = _to_oracle_timestamp(generated_at_dt)
                print(
                    f"[INFO] Executando extracao incremental de traducoes OTM "
                    f"(rootName={root_name}, since={since_ts})..."
                )
                changed_gids = _extract_changed_gids_since(
                    root_name, timeout_seconds, page_size, since_ts
                )
                print(f"[INFO] GIDs alterados identificados: {len(changed_gids)}")

                if not changed_gids:
                    print("[INFO] Nenhuma alteracao detectada desde a ultima geracao.")
                    rows = []
                    payload = existing_payload
                    payload["metadata"]["generatedAt"] = _timestamp_utc_z()
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_text(
                        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
                    )

                    index_payload = _build_index_payload(payload.get("gids", []), output_path)
                    index_output_path.parent.mkdir(parents=True, exist_ok=True)
                    index_output_path.write_text(
                        json.dumps(index_payload, ensure_ascii=False, indent=2), encoding="utf-8"
                    )
                    print(f"[OK] Cache de traducoes atualizado: {output_path}")
                    print(f"[OK] Indice de traducoes atualizado: {index_output_path}")
                    print("[OK] Total de linhas: 0 (incremental sem alteracoes)")
                    return 0

                changed_rows = _fetch_rows_for_gid_chunks(
                    root_name, timeout_seconds, changed_gids, chunk_size=500
                )
                changed_grouped = _group_rows_by_gid(changed_rows)
                changed_by_gid = {
                    str(item.get("TRANSLATION_GID") or "").strip(): item
                    for item in changed_grouped
                    if str(item.get("TRANSLATION_GID") or "").strip()
                }

                existing_gids = existing_payload.get("gids", [])
                if not isinstance(existing_gids, list):
                    existing_gids = []
                existing_by_gid: Dict[str, Dict[str, Any]] = {
                    str(item.get("TRANSLATION_GID") or "").strip(): item
                    for item in existing_gids
                    if isinstance(item, dict) and str(item.get("TRANSLATION_GID") or "").strip()
                }

                for gid in changed_gids:
                    normalized_gid = str(gid).strip()
                    replacement = changed_by_gid.get(normalized_gid)
                    if replacement is None:
                        # Se nao retornou mais dados para o GID, remove do cache consolidado.
                        existing_by_gid.pop(normalized_gid, None)
                    else:
                        existing_by_gid[normalized_gid] = replacement

                merged_gids = list(existing_by_gid.values())
                merged_gids.sort(
                    key=lambda item: str(
                        item.get("TRANSLATION_XID") or item.get("TRANSLATION_GID") or ""
                    )
                )

                merged_row_count = sum(
                    len(item.get("translations", []))
                    for item in merged_gids
                    if isinstance(item, dict) and isinstance(item.get("translations", []), list)
                )
                payload = {
                    "metadata": {
                        "generatedAt": _timestamp_utc_z(),
                        "sourceScript": SCRIPT_NAME,
                        "rootName": root_name,
                        "queryTimeoutSeconds": timeout_seconds,
                        "translationRowCount": merged_row_count,
                        "gidCount": len(merged_gids),
                        "query": FULL_TRANSLATION_SQL,
                    },
                    "gids": merged_gids,
                }
                rows = changed_rows
    else:
        print(f"[INFO] Executando extracao completa de traducoes OTM (rootName={root_name})...")
        rows = _query_rows_paginated(
            root_name,
            timeout_seconds,
            page_size,
            BASE_TRANSLATION_SELECT_SQL,
            [
                "inner_query.TRANSLATION_XID",
                "inner_query.LANG",
                "inner_query.COUNTRY",
                "inner_query.VARIANT",
            ],
        )
        payload = _build_output_payload(rows, root_name, timeout_seconds)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    index_payload = _build_index_payload(payload.get("gids", []), output_path)
    index_output_path.parent.mkdir(parents=True, exist_ok=True)
    index_output_path.write_text(
        json.dumps(index_payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"[OK] Cache de traducoes atualizado: {output_path}")
    print(f"[OK] Indice de traducoes atualizado: {index_output_path}")
    print(f"[OK] Total de linhas: {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
