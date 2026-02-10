import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Set

BASE_DIR = Path(__file__).resolve().parents[2]
ELIGIBILITY_PATH = (
    BASE_DIR / "metadata" / "otm" / "migration_project_eligible_tables.json"
)
DEFAULT_DEPLOYMENT_TYPE = ""


def _normalize(value: Any) -> str:
    return str(value or "").strip().upper()


def _load_payload() -> Dict[str, Any]:
    try:
        return json.loads(ELIGIBILITY_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


@lru_cache(maxsize=1)
def _catalog() -> Dict[str, Any]:
    payload = _load_payload()
    default_type = (
        _normalize(payload.get("defaultDeploymentType"))
        or DEFAULT_DEPLOYMENT_TYPE
    )
    table_rules: Dict[str, Dict[str, Any]] = {}

    for item in payload.get("tables", []):
        if not isinstance(item, dict):
            continue

        table_name = _normalize(item.get("tableName"))
        deployment_type = _normalize(item.get("deploymentType")) or default_type
        if not table_name:
            continue

        allowed_domains_raw = item.get("allowedDomains")
        allowed_domains: Set[str] = set()
        if isinstance(allowed_domains_raw, list):
            allowed_domains = {
                _normalize(domain)
                for domain in allowed_domains_raw
                if _normalize(domain)
            }

        table_rules[table_name] = {
            "deploymentType": deployment_type,
            "allowedDomains": allowed_domains,
        }

    return {
        "defaultDeploymentType": default_type,
        "tableRules": table_rules,
    }


def deployment_type_for_table(table_name: str, domain_name: str = "") -> str:
    normalized_table = _normalize(table_name)
    normalized_domain = _normalize(domain_name)
    catalog = _catalog()
    default_type = (
        _normalize(catalog.get("defaultDeploymentType"))
        or DEFAULT_DEPLOYMENT_TYPE
    )
    table_rules = catalog.get("tableRules", {})
    rule = table_rules.get(normalized_table)
    if not isinstance(rule, dict):
        return default_type

    deployment_type = _normalize(rule.get("deploymentType")) or default_type
    allowed_domains = rule.get("allowedDomains")
    if isinstance(allowed_domains, set) and allowed_domains:
        if not normalized_domain or normalized_domain not in allowed_domains:
            return default_type

    return deployment_type


def clear_deployment_policy_cache() -> None:
    _catalog.cache_clear()
