#!/usr/bin/env python3
"""
CLI para encaminhar queries ao executor OTM.

Exemplos:
  python3 infra/run_otm_query.py \
    --query "SELECT * FROM SHIPMENT WHERE DOMAIN_NAME = '$DOMAIN_NAME'" \
    --execution-type SQL \
    --context-json '{"DOMAIN_NAME":"BAUDUCCO"}'

  python3 infra/run_otm_query.py \
    --query-file ./minha_query.sql \
    --execution-type SQL \
    --context-file ./context.json \
    --output-format raw
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

try:
    from infra.otm_query_executor import execute_otm_query
except ModuleNotFoundError:
    from otm_query_executor import execute_otm_query  # type: ignore


def _parse_json_string(value: str, source: str) -> Dict[str, Any]:
    """Converte string JSON para dict validando tipo."""
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON invalido em {source}: {exc}") from exc

    if not isinstance(parsed, dict):
        raise ValueError(f"{source} deve representar um objeto JSON (dict).")
    return parsed


def _load_context(context_json: str, context_file: str) -> Dict[str, Any]:
    """Carrega contexto a partir de JSON inline e/ou arquivo."""
    context: Dict[str, Any] = {}

    if context_file:
        file_path = Path(context_file)
        if not file_path.exists():
            raise ValueError(f"Arquivo de contexto nao encontrado: {file_path}")
        context.update(_parse_json_string(file_path.read_text(encoding="utf-8"), str(file_path)))

    if context_json:
        context.update(_parse_json_string(context_json, "--context-json"))

    return context


def _load_query(query: str, query_file: str) -> str:
    """Carrega query diretamente da CLI ou de arquivo."""
    if query:
        return query

    file_path = Path(query_file)
    if not file_path.exists():
        raise ValueError(f"Arquivo de query nao encontrado: {file_path}")
    return file_path.read_text(encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Encaminha uma query para execute_otm_query (OTM)."
    )

    query_group = parser.add_mutually_exclusive_group(required=True)
    query_group.add_argument(
        "--query",
        help="SQL ou nome da saved query.",
    )
    query_group.add_argument(
        "--query-file",
        help="Caminho para arquivo contendo SQL ou nome da saved query.",
    )

    parser.add_argument(
        "--execution-type",
        required=True,
        choices=["SQL", "SAVED_QUERY"],
        help="Tipo de execucao da consulta.",
    )
    parser.add_argument(
        "--output-format",
        default="json",
        choices=["json", "md", "raw"],
        help="Formato de retorno do payload.",
    )

    parser.add_argument(
        "--context-json",
        default="",
        help="Contexto em JSON inline (ex.: '{\"DOMAIN_NAME\":\"BAUDUCCO\"}').",
    )
    parser.add_argument(
        "--context-file",
        default="",
        help="Arquivo JSON com contexto.",
    )

    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    try:
        query_payload = _load_query(args.query, args.query_file)
        context = _load_context(args.context_json, args.context_file)
    except ValueError as exc:
        print(
            json.dumps(
                {
                    "status": "error",
                    "payload": None,
                    "raw": None,
                    "error_message": str(exc),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2

    result = execute_otm_query(
        query_payload=query_payload,
        execution_type=args.execution_type,
        context=context,
        output_format=args.output_format,
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
