#!/usr/bin/env python3
"""
Validate metadata/otm/migration_project_eligible_tables.json.

Checks:
- valid JSON shape
- duplicated tableName entries
- deploymentType exists in domain/projeto_migracao/enums/deployment_type.json
- tableName not found locally in metadata/otm/tables (warning only)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

BASE_DIR = Path(__file__).resolve().parents[1]
CATALOG_PATH = BASE_DIR / "metadata" / "otm" / "migration_project_eligible_tables.json"
TABLES_DIR = BASE_DIR / "metadata" / "otm" / "tables"
DEPLOYMENT_ENUM_PATH = BASE_DIR / "domain" / "projeto_migracao" / "enums" / "deployment_type.json"


def _normalize(value: Any) -> str:
    return str(value or "").strip().upper()


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _known_tables() -> Set[str]:
    if not TABLES_DIR.exists():
        return set()
    return {
        path.stem.upper()
        for path in TABLES_DIR.glob("*.json")
        if path.stem.upper() != "INDEX"
    }


def _allowed_deployment_types() -> Set[str]:
    payload = _load_json(DEPLOYMENT_ENUM_PATH)
    if not isinstance(payload, dict):
        return set()
    return {_normalize(k) for k in payload.keys() if _normalize(k)}


def _validate_catalog(payload: Dict[str, Any]) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []

    if _normalize(payload.get("metadataType")) != "OTM_MIGRATION_PROJECT_ELIGIBILITY":
        warnings.append("metadataType diferente de OTM_MIGRATION_PROJECT_ELIGIBILITY.")

    default_type = _normalize(payload.get("defaultDeploymentType"))
    allowed_types = _allowed_deployment_types()
    if default_type and default_type not in allowed_types:
        errors.append(f"defaultDeploymentType invalido: {default_type}")

    tables_raw = payload.get("tables")
    if not isinstance(tables_raw, list):
        errors.append("Campo tables deve ser uma lista.")
        tables_raw = []

    known_tables = _known_tables()
    seen: Set[str] = set()
    duplicates: List[str] = []
    unknown_tables: List[str] = []
    invalid_deployment_types: List[str] = []

    for idx, item in enumerate(tables_raw):
        if not isinstance(item, dict):
            errors.append(f"Entrada tables[{idx}] nao e objeto.")
            continue

        table_name = _normalize(item.get("tableName"))
        deployment_type = _normalize(item.get("deploymentType"))

        if not table_name:
            errors.append(f"Entrada tables[{idx}] sem tableName.")
            continue

        if table_name in seen:
            duplicates.append(table_name)
        seen.add(table_name)

        if known_tables and table_name not in known_tables:
            unknown_tables.append(table_name)

        if deployment_type and deployment_type not in allowed_types:
            invalid_deployment_types.append(
                f"{table_name}:{deployment_type}"
            )

    if duplicates:
        errors.append(f"tableName duplicado: {', '.join(sorted(set(duplicates)))}")
    if unknown_tables:
        warnings.append(
            "tableName inexistente em metadata/otm/tables (warning): "
            + ", ".join(sorted(set(unknown_tables)))
        )
    if invalid_deployment_types:
        errors.append(
            "deploymentType invalido: "
            + ", ".join(sorted(set(invalid_deployment_types)))
        )

    return {
        "status": "ok" if not errors else "error",
        "catalogPath": str(CATALOG_PATH),
        "entries": len(seen),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    try:
        payload = _load_json(CATALOG_PATH)
    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "error",
                    "catalogPath": str(CATALOG_PATH),
                    "errors": [f"Falha ao carregar catalogo: {exc}"],
                    "warnings": [],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    result = _validate_catalog(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
