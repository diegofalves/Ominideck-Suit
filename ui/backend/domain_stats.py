import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Set

BASE_DIR = Path(__file__).resolve().parents[2]
DOMAIN_STATS_PATH = BASE_DIR / "metadata" / "otm" / "domain_table_statistics.json"


def _normalize(value: object) -> str:
    return str(value or "").strip().upper()


def _load_payload() -> Dict:
    try:
        return json.loads(DOMAIN_STATS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_domain_statistics() -> Dict:
    return _load_payload()


def table_domain_map() -> Dict[str, List[str]]:
    payload = load_domain_statistics()
    result: Dict[str, List[str]] = {}
    for entry in payload.get("tables", []):
        table_name = _normalize(entry.get("tableName"))
        if not table_name:
            continue
        parsed = entry.get("parsedCounts") or {}
        domains = [ _normalize(domain) for domain in parsed.keys() if _normalize(domain) ]
        result[table_name] = domains
    return result


def unique_domain_names() -> List[str]:
    payload = load_domain_statistics()
    names: Set[str] = set()
    for entry in payload.get("tables", []):
        parsed = entry.get("parsedCounts") or {}
        for domain in parsed:
            normalized = _normalize(domain)
            if normalized:
                names.add(normalized)
    return sorted(names)


def object_domain_map(groups: Iterable[Dict], domain_map: Dict[str, List[str]] = None) -> Dict[str, Set[str]]:
    if domain_map is None:
        domain_map = table_domain_map()

    mapping: Dict[str, Set[str]] = defaultdict(set)
    for group in groups or []:
        if not isinstance(group, dict):
            continue
        for obj in group.get("objects", []) or []:
            if not isinstance(obj, dict):
                continue
            if str(obj.get("ignore_table") or "").strip().lower() in {"1", "true", "on", "yes", "y"}:
                continue
            table_name = _normalize(obj.get("object_type") or obj.get("otm_table"))
            if not table_name:
                continue
            domain_name = _normalize(obj.get("domainName") or obj.get("domain"))
            if not domain_name:
                fallback = domain_map.get(table_name, [])
                if len(fallback) == 1:
                    domain_name = fallback[0]
            if domain_name:
                mapping[table_name].add(domain_name)
    return mapping
