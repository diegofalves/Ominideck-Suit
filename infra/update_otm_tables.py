#!/usr/bin/env python3
"""
CORE SCRIPT - OTM DOMAIN RECORD COUNT

Script canonico e fixo para consulta de contagem de registros
por dominio em tabelas OTM.

Contrato de saida:
- Gera metadata canônica em metadata/otm/domain_table_statistics.json
- Inclui apenas tabelas com domainCountsRaw nao vazio

ATENCAO: QUERY FIXA
ATENCAO: NAO GENERALIZAR
ATENCAO: NAO PARAMETRIZAR
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

try:
    from infra.otm_query_executor import execute_otm_query
except ModuleNotFoundError:
    from otm_query_executor import execute_otm_query  # type: ignore


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_STATISTICS_FILE = BASE_DIR / "metadata" / "otm" / "domain_table_statistics.json"
CORE_SCHEMA_OWNER = "GLOGOWNER"
CORE_QUERY_TIMEOUT_SECONDS = 300
SOURCE_SCRIPT_NAME = "update_otm_tables.py"

CORE_DOMAIN_COUNT_SQL = """
WITH table_columns AS (
  SELECT
    table_name,
    MAX(CASE WHEN column_name = 'DOMAIN_NAME' THEN 1 ELSE 0 END) AS has_domain_name,
    MAX(CASE WHEN column_name = 'UPDATE_DATE' THEN 1 ELSE 0 END) AS has_update_date,
    MAX(CASE WHEN column_name = 'INSERT_DATE' THEN 1 ELSE 0 END) AS has_insert_date
  FROM all_tab_columns
  WHERE owner = 'GLOGOWNER'
    AND table_name NOT LIKE 'BIN$%'
    AND table_name NOT LIKE '%$%'
    AND column_name IN ('DOMAIN_NAME', 'UPDATE_DATE', 'INSERT_DATE')
  GROUP BY table_name
),
candidate_tables AS (
  SELECT
    tc.table_name,
    ats.num_rows,
    ats.stale_stats,
    ats.last_analyzed
  FROM table_columns tc
  LEFT JOIN all_tab_statistics ats
    ON ats.owner = 'GLOGOWNER'
   AND ats.table_name = tc.table_name
   AND ats.partition_name IS NULL
  WHERE tc.has_domain_name = 1
    AND tc.has_update_date = 1
    AND tc.has_insert_date = 1
)
SELECT
  table_name,
  CASE
    WHEN last_analyzed IS NOT NULL
     AND stale_stats = 'NO'
     AND num_rows = 0
    THEN ''
    ELSE dbms_xmlgen.getxmltype(
      'SELECT (SELECT LISTAGG(domain_name || '': '' || cnt, '' | '') WITHIN GROUP (ORDER BY domain_name) ' ||
      'FROM (SELECT t.domain_name, COUNT(*) cnt FROM GLOGOWNER."' || table_name || '" t ' ||
      'LEFT JOIN GLOGOWNER.DOMAIN d ON d.domain_name = t.domain_name ' ||
      'WHERE t.domain_name IS NOT NULL ' ||
      'AND ((t.update_date IS NOT NULL AND (t.domain_name <> ''PUBLIC'' ' ||
      'OR (t.insert_date IS NOT NULL AND t.update_date > (t.insert_date + (1/1440))))) ' ||
      'OR (t.update_date IS NULL AND t.insert_date IS NOT NULL ' ||
      'AND d.insert_date IS NOT NULL AND t.insert_date > (d.insert_date + 1))) ' ||
      'GROUP BY t.domain_name)) c FROM DUAL'
    ).extract('//C/text()').getstringval()
  END AS total_registros_geral
FROM candidate_tables
ORDER BY table_name
"""


def _safe_table_name(value: str) -> str:
    name = value.strip().upper()
    if not name:
        raise ValueError("Nome de tabela vazio.")
    if not re.fullmatch(r"[A-Z0-9_#$]+", name):
        raise ValueError(f"Nome de tabela invalido: {value}")
    return name


def _timestamp_utc_z() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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
        extracted.append(
            {k: v for k, v in row.items() if isinstance(v, (str, int, float, bool))}
        )

    return extracted


def _query_rows(sql_template: str, root_name: str, context_vars: Dict[str, Any]) -> List[Dict[str, Any]]:
    context = dict(context_vars)
    context["sql_param_name"] = "sqlQuery"
    context["request_params"] = {"rootName": root_name}
    context["timeout"] = CORE_QUERY_TIMEOUT_SECONDS

    result = execute_otm_query(sql_template, "SQL", context, "json")
    if result.get("status") != "success":
        raise RuntimeError(result.get("error_message") or "Falha ao consultar OTM.")

    payload = result.get("payload")
    if not isinstance(payload, dict):
        raise RuntimeError("Resposta da consulta sem payload JSON.")

    return _extract_transaction_rows(payload, root_name)


def _parse_domain_counts(domain_counts_raw: str) -> Dict[str, int]:
    parsed: Dict[str, int] = {}
    if not domain_counts_raw:
        return parsed

    for item in domain_counts_raw.split(" | "):
        item = item.strip()
        if not item or ": " not in item:
            continue

        domain_name, count_text = item.split(": ", 1)
        domain_name = domain_name.strip()
        count_text = count_text.strip().replace(",", "")

        if not domain_name or not count_text:
            continue

        try:
            parsed[domain_name] = int(count_text)
        except ValueError:
            continue

    return parsed


def _normalize_core_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []

    for row in rows:
        table_name_raw = str(row.get("TABLE_NAME", "")).strip().upper()
        if not table_name_raw:
            continue

        try:
            table_name = _safe_table_name(table_name_raw)
        except ValueError:
            continue

        domain_counts_raw_value = row.get("TOTAL_REGISTROS_GERAL")
        if domain_counts_raw_value is None:
            domain_counts_raw_value = row.get("total_registros_geral")

        domain_counts_raw = ""
        if domain_counts_raw_value is not None:
            domain_counts_raw = str(domain_counts_raw_value).strip()
        if not domain_counts_raw:
            # Regra CORE: tabelas sem retorno de contagem nao entram no JSON final.
            continue

        normalized.append(
            {
                "tableName": table_name,
                "domainCountsRaw": domain_counts_raw,
                "parsedCounts": _parse_domain_counts(domain_counts_raw),
            }
        )

    return normalized


def _build_statistics_payload(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "metadataType": "OTM_DOMAIN_TABLE_STATISTICS",
        "schemaOwner": CORE_SCHEMA_OWNER,
        "generatedAt": _timestamp_utc_z(),
        "source": SOURCE_SCRIPT_NAME,
        "tables": _normalize_core_rows(rows),
    }


def _write_statistics_file(payload: Dict[str, Any], dry_run: bool) -> None:
    if dry_run:
        return
    DEFAULT_STATISTICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_STATISTICS_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CORE: persiste estatisticas de contagem por dominio em JSON canônico.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Executa consulta e imprime JSON sem gravar arquivo.",
    )
    parser.add_argument(
        "--skip-report",
        action="store_true",
        help="Mantido por compatibilidade. Ignorado no modo CORE atual.",
    )
    return parser.parse_args(argv)


def main(argv: List[str]) -> int:
    args = _parse_args(argv)
    _ = args.skip_report  # flag legada, intencionalmente ignorada

    try:
        rows = _query_rows(
            CORE_DOMAIN_COUNT_SQL,
            root_name="TABLE_DOMAIN_COUNT",
            context_vars={},
        )
        payload = _build_statistics_payload(rows)
        _write_statistics_file(payload, dry_run=bool(args.dry_run))
    except Exception as exc:
        error_payload = {
            "status": "error",
            "error_message": str(exc),
            "generatedAt": _timestamp_utc_z(),
            "source": SOURCE_SCRIPT_NAME,
        }
        print(json.dumps(error_payload, ensure_ascii=False, indent=2))
        return 1

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
