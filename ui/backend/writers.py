import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

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
    """
    Carrega a lista canônica de tabelas OTM do metadata consolidado.
    """
    if not DOMAIN_TABLE_STATS_PATH.exists():
        return []

    try:
        payload = json.loads(DOMAIN_TABLE_STATS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []

    tables = payload.get("tables", [])
    if not isinstance(tables, list):
        return []

    result: Set[str] = set()
    for row in tables:
        if not isinstance(row, dict):
            continue
        table_name = _normalize_name(row.get("tableName"))
        if not table_name:
            continue
        if not re.fullmatch(r"[A-Z0-9_#$]+", table_name):
            continue
        result.add(table_name)

    return sorted(result)


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


def _build_auto_group_zero_object(table_name: str, sequence: int) -> Dict[str, Any]:
    auto_name = f"{table_name} (AUTO)"
    identifiers: Dict[str, str] = {}
    saved_query: Optional[Dict[str, str]] = None

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
        "deployment_type": "MANUAL",
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

    return payload


def _ensure_domain_statistics_coverage(data: Dict[str, Any]) -> None:
    """
    Regra canônica:
    Todas as tabelas existentes em metadata/otm/domain_table_statistics.json
    devem ter ao menos um objeto associado no projeto final.
    As ausentes são criadas automaticamente em SEM_GRUPO.
    """
    required_tables = _load_domain_statistics_tables()
    if not required_tables:
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

    effective_required_tables = [
        table for table in required_tables if table not in ignored_tables
    ]
    existing_tables = _collect_existing_otm_tables(data)
    missing_tables = [
        table for table in effective_required_tables if table not in existing_tables
    ]
    if not missing_tables:
        return

    next_sequence = 1
    for obj in objects:
        if not isinstance(obj, dict):
            continue
        next_sequence = max(next_sequence, _to_int(obj.get("sequence")) + 1)

    for table_name in missing_tables:
        objects.append(_build_auto_group_zero_object(table_name, next_sequence))
        next_sequence += 1


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
    _ensure_domain_statistics_coverage(data)
    normalized_signature = json.dumps(data, ensure_ascii=False, sort_keys=True)
    if normalized_signature != original_signature:
        PROJECT_PATH.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return data


def save_project(domain):
    _normalize_group_zero(domain)
    _ensure_domain_statistics_coverage(domain)
    PROJECT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PROJECT_PATH, "w", encoding="utf-8") as f:
        json.dump(domain, f, indent=2, ensure_ascii=False)
