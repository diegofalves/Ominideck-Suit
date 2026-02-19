from typing import Iterable, List, Dict, Any, Optional


SPECIAL_GROUP_IDS = {"SEM_GRUPO", "GROUP_0", "IGNORADOS"}
REQUIRED_STATUS_KEYS = {"documentation", "migration_project", "export", "deploy", "validation"}

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

    # Centraliza textos da UI/documento para fácil customização
    ui_texts = project_metadata.setdefault("ui_texts", {})
    ui_texts.setdefault("project_information_title", "Informações do Projeto")
    ui_texts.setdefault("version_control_title", "Controle de Versão")
    ui_texts.setdefault("change_history_title", "Histórico de Alterações")
    ui_texts.setdefault("migration_groups_title", "Grupos e Objetos de Migração OTM")

    return project_metadata


def normalize_render_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normaliza a estrutura de dados completa para ser usada nos templates de renderização.
    Esta função é a fonte única da verdade para a preparação de dados para MD e HTML.
    """
    project = dict(data.get("project", {}))
    project.setdefault("code", "")
    project.setdefault("name", "")
    project.setdefault("version", "")
    project.setdefault("consultant", "")
    project.setdefault("environment", {})
    project["environment"].setdefault("source", "")
    project["environment"].setdefault("target", "")

    groups = []
    for group in data.get("groups", []):
        group_id = str(group.get("group_id") or "").strip().upper()
        if group_id in SPECIAL_GROUP_IDS:
            continue

        objects = []
        for obj in group.get("objects", []):
            obj = dict(obj)
            obj.setdefault("identifiers", {})
            obj.setdefault("object_extraction_query", {})
            obj.setdefault("technical_content", {})
            obj.setdefault("status", {})
            obj.setdefault("otm_table", "")
            obj.setdefault("otm_subtables", [])
            obj.setdefault("migration_type", "")
            obj.setdefault("description", "")
            obj.setdefault("responsible", "")
            obj.setdefault("deployment_type", "")
            obj.setdefault("object_type", "")
            obj.setdefault("notes", "")
            obj.setdefault("sequence", "")
            obj.setdefault("name", "")

            extraction_query = obj.get("object_extraction_query", {})
            if not isinstance(extraction_query, dict):
                extraction_query = {}

            if (
                not extraction_query.get("content")
                and isinstance(obj.get("saved_query"), dict)
                and obj["saved_query"].get("sql")
            ):
                extraction_query = {
                    "language": "SQL",
                    "content": str(obj["saved_query"].get("sql") or ""),
                }

            extraction_language = str(extraction_query.get("language") or "SQL").upper()
            extraction_content = str(extraction_query.get("content") or "")
            obj["object_extraction_query"] = {
                "language": extraction_language,
                "content": extraction_content,
            }
            technical_content = obj.get("technical_content", {})
            if not isinstance(technical_content, dict):
                technical_content = {}
            obj["technical_content"] = {
                "type": str(technical_content.get("type") or "NONE").upper(),
                "content": str(technical_content.get("content") or ""),
            }

            if extraction_content and extraction_language == "SQL":
                obj["saved_query"] = {"sql": extraction_content, "type": "extraction"}
            else:
                obj.setdefault("saved_query", None)

            objects.append(obj)

        group = dict(group)
        label = group.get("label") or group.get("group_name") or group.get("name", "")
        group["label"] = label
        group["name"] = label
        group.setdefault("description", "")
        group["objects"] = objects
        groups.append(group)

    project_metadata = extract_project_metadata(data)

    def split_paragraphs(text: str):
        return [p.strip() for p in (text or "").split("\n\n") if p.strip()]

    for g in groups:
        g["description_paragraphs"] = split_paragraphs(g.get("description", ""))

    return {"project": project, "groups": groups, "project_metadata": project_metadata}


def validate_object_status(data: Dict[str, Any]) -> None:
    """
    Valida se cada objeto de migração possui todas as chaves de status requeridas.
    """
    for group in data.get("groups", []):
        for obj in group.get("objects", []):
            status_keys = (obj.get("status") or {}).keys()
            if not REQUIRED_STATUS_KEYS.issubset(status_keys):
                missing = sorted(REQUIRED_STATUS_KEYS - set(status_keys))
                raise ValueError(f"Status incompleto no objeto '{obj.get('name', '')}' (Grupo: '{group.get('label', '')}'): faltando {missing}")
