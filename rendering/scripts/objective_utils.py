from typing import Iterable, List, Dict, Any, Optional


def prepare_objective_blocks(content: Iterable[str]) -> List[Dict[str, Any]]:
    """
    Converte linhas de texto do objetivo em blocos de parágrafo ou lista.

    Cada string que começa com '- ' vira um item de lista. Strings vazias são ignoradas.
    """
    blocks: List[Dict[str, Any]] = []
    current_list: Optional[Dict[str, Any]] = None

    for raw_line in content or ():
        line = (raw_line or "").strip()
        if not line:
            current_list = None
            continue

        if line.startswith("- "):
            item_text = line[2:].strip()
            if current_list is None or current_list.get("type") != "list":
                current_list = {"type": "list", "items": []}
                blocks.append(current_list)
            current_list["items"].append(item_text)
        else:
            current_list = None
            blocks.append({"type": "paragraph", "text": line})

    return blocks


def normalize_migration_objective(project_metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Padroniza o bloco migration_objective a partir do JSON fonte.
    """
    objective = (project_metadata or {}).get("migration_objective", {}) or {}
    title = objective.get("title") or "Objetivo do Projeto de Migração"
    content = objective.get("content") or []

    return {
        "title": title,
        "content": list(content),
        "blocks": prepare_objective_blocks(content),
    }


def extract_project_metadata(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Retorna o bloco project_metadata sem inferir campos, exceto normalização do objetivo.
    """
    project_metadata = dict(data.get("project_metadata", {}) or {})
    project_metadata["migration_objective"] = normalize_migration_objective(project_metadata)
    project_metadata.setdefault("version_control", {})
    project_metadata.setdefault("change_history", [])
    return project_metadata
