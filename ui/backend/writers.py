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
LOGICAL_REQUIRED_IDENTIFIERS = {
    "SAVED_QUERY": ("query_name",),
    "AGENT": ("agent_gid",),
    "FINDER_SET": ("finder_set_gid",),
    "RATE": ("rate_offering_gid",),
    "EVENT_GROUP": ("event_group_gid",),
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
    # Primeiro normaliza aliases de dominio para evitar duplicacao por cobertura.
    _normalize_object_domain_aliases(data)
    _ensure_domain_statistics_coverage(data)
    _normalize_object_domain_aliases(data)
    _normalize_auto_generated_deployment_types(data)
    _deduplicate_group_zero_auto_objects(data)
    _cleanup_group_zero_legacy_generic_autos(data)
    normalized_signature = json.dumps(data, ensure_ascii=False, sort_keys=True)
    if normalized_signature != original_signature:
        PROJECT_PATH.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return data


def save_project(domain):
    _normalize_group_zero(domain)
    _normalize_object_domain_aliases(domain)
    _ensure_domain_statistics_coverage(domain)
    _normalize_object_domain_aliases(domain)
    _normalize_auto_generated_deployment_types(domain)
    _deduplicate_group_zero_auto_objects(domain)
    _cleanup_group_zero_legacy_generic_autos(domain)
    PROJECT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PROJECT_PATH, "w", encoding="utf-8") as f:
        json.dump(domain, f, indent=2, ensure_ascii=False)
