from collections import defaultdict
from datetime import datetime


# Tipos lógicos (não são tabelas OTM)
LOGICAL_OBJECT_TYPES = {
    "SAVED_QUERY",
    "AGENT",
    "FINDER_SET",
    "RATE",
    "EVENT_GROUP",
}


def _parse_history_date(raw_date):
    if not raw_date:
        return None

    value = str(raw_date).strip()
    if not value:
        return None

    for date_format in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, date_format)
        except ValueError:
            continue

    return None


def _latest_history_entry(change_history):
    latest_entry = None
    latest_date = None

    for entry in change_history:
        if not any(entry.values()):
            continue

        entry_date = _parse_history_date(entry.get("date", ""))

        if latest_entry is None:
            latest_entry = entry
            latest_date = entry_date
            continue

        if entry_date and latest_date:
            if entry_date > latest_date:
                latest_entry = entry
                latest_date = entry_date
            continue

        if entry_date and not latest_date:
            latest_entry = entry
            latest_date = entry_date
            continue

        if not entry_date and not latest_date:
            # Sem data válida: mantém a última entrada preenchida.
            latest_entry = entry

    return latest_entry


def form_to_domain(form):
    """
    Converte request.form (flat) em estrutura de domínio canônica.
    
    SE object_type é tipo lógico (AGENT, SAVED_QUERY, etc):
        → salvar em identifiers (modelo antigo)
    
    SE object_type é tabela OTM (ORDER_RELEASE, SHIPMENT, etc):
        → salvar em data (schema-driven)
    """

    domain = {
        "project": {
            "code": form.get("code", ""),
            "name": form.get("name", ""),
            "version": form.get("version", ""),
            "consultant": form.get("consultant", ""),
            "environment": {
                "source": form.get("environment.source") or form.get("environment_source", ""),
                "target": form.get("environment.target") or form.get("environment_target", ""),
            },
        },
        "groups": [],
        "state": {
            "overall_status": form.get("overall_status") or "PENDING",
            "last_edit_object_index": form.get("edit_object_index") or None
        },
        "active_group_id": form.get("active_group_id") or None
    }

    groups = defaultdict(lambda: {"objects": []})

    for key, value in form.items():
        if not key.startswith("groups["):
            continue

        # Ex: groups[0][label]
        parts = key.replace("]", "").split("[")

        group_idx = int(parts[1])

        if parts[2] == "group_id":
            groups[group_idx]["group_id"] = value

        elif parts[2] == "label":
            groups[group_idx]["label"] = value

        elif parts[2] == "sequence":
            groups[group_idx]["sequence"] = int(value)

        elif parts[2] == "description":
            groups[group_idx]["description"] = value

        elif parts[2] == "objects":
            obj_idx = int(parts[3])

            while len(groups[group_idx]["objects"]) <= obj_idx:
                groups[group_idx]["objects"].append({
                    "name": "",  # Nome funcional obrigatório
                    "description": "",  # Descrição funcional opcional
                    "identifiers": {},
                    "data": {},
                    "status": {
                        "documentation": "PENDING",
                        "migration_project": "PENDING",
                        "export": "PENDING",
                        "deploy": "PENDING",
                        "validation": "PENDING"
                    },
                    "saved_query": {"sql": ""}  # Inicializar vazio
                })

            obj = groups[group_idx]["objects"][obj_idx]
            
            # Determinar se é tipo lógico ou tabela OTM
            obj_type = obj.get("object_type") or form.get(f"groups[{group_idx}][objects][{obj_idx}][object_type]", "")

            if parts[4] == "identifiers":
                # Tipo lógico: usar identifiers
                identifier_key = parts[5]
                obj["identifiers"][identifier_key] = value
            
            elif parts[4] == "data":
                # Tabela OTM: usar data
                data_key = parts[5]
                obj["data"][data_key] = value
            
            elif parts[4] == "status_documentation":
                if "status" not in obj:
                    obj["status"] = {}
                obj["status"]["documentation"] = value
            
            elif parts[4] == "status_migration_project":
                if "status" not in obj:
                    obj["status"] = {}
                obj["status"]["migration_project"] = value
            
            elif parts[4] == "status_export":
                if "status" not in obj:
                    obj["status"] = {}
                obj["status"]["export"] = value
            
            elif parts[4] == "status_deploy":
                if "status" not in obj:
                    obj["status"] = {}
                obj["status"]["deploy"] = value
            
            elif parts[4] == "status_validation":
                if "status" not in obj:
                    obj["status"] = {}
                obj["status"]["validation"] = value
            
            else:
                # Campos genéricos do objeto
                obj[parts[4]] = value
    
    # Processar campos não aninhados (saved_query_sql, etc)
    for key, value in form.items():
        if key == "saved_query_sql":
            # Encontrar qual objeto está sendo editado (buscar no form)
            # Como é um campo do formulário de edição, aplicar no objeto sendo editado
            pass  # Será tratado abaixo na normalização
    
    # Normaliza para lista ordenada
    domain["groups"] = [
        {
            "group_id": g.get("group_id"),
            "label": g.get("label"),
            "sequence": g.get("sequence"),
            "objects": g.get("objects", [])
        }
        for _, g in sorted(groups.items())
    ]
    
    # Processar saved_query_sql do formulário de edição (não aninhado)
    saved_query_sql = form.get("saved_query_sql", "").strip()
    object_name = form.get("object_name", "").strip()

    def _coerce_index(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    active_group_index = _coerce_index(form.get("active_group_index"))
    edit_object_index = _coerce_index(form.get("edit_object_index"))

    # Se estamos editando/criando um objeto (campos não-aninhados presentes)
    if object_name or saved_query_sql or form.get("object_description") or form.get("object_responsible") or form.get("object_deployment_type"):
        if active_group_index is not None:
            # Garantir grupo ativo existe
            while len(domain["groups"]) <= active_group_index:
                domain["groups"].append({"label": "", "sequence": None, "objects": []})
            target_group = domain["groups"][active_group_index]

            # Definir índice do objeto (editar ou criar novo no fim)
            target_obj_index = edit_object_index if edit_object_index is not None else len(target_group["objects"])

            while len(target_group["objects"]) <= target_obj_index:
                target_group["objects"].append({
                    "name": "",
                    "description": "",
                    "identifiers": {},
                    "data": {},
                    "status": {
                        "documentation": "PENDING",
                        "migration_project": "PENDING",
                        "export": "PENDING",
                        "deploy": "PENDING",
                        "validation": "PENDING"
                    },
                    "saved_query": {"sql": ""}
                })

            target_obj = target_group["objects"][target_obj_index]

            # Campos básicos
            if object_name:
                target_obj["name"] = object_name
            object_description = form.get("object_description", "")
            if object_description:
                target_obj["description"] = object_description
            object_type = form.get("object_type")
            if object_type:
                target_obj["object_type"] = object_type
            object_deployment_type = form.get("object_deployment_type")
            if object_deployment_type:
                target_obj["deployment_type"] = object_deployment_type
            object_responsible = form.get("object_responsible")
            if object_responsible:
                target_obj["responsible"] = object_responsible
            object_notes = form.get("object_notes")
            if object_notes:
                target_obj["notes"] = object_notes
            object_otm_table = form.get("object_otm_table")
            if object_otm_table:
                target_obj["otm_table"] = object_otm_table

            # Status (5 campos)
            if "status" not in target_obj:
                target_obj["status"] = {}
            
            status_doc = form.get("status_documentation")
            if status_doc:
                target_obj["status"]["documentation"] = status_doc
            
            status_mig = form.get("status_migration_project")
            if status_mig:
                target_obj["status"]["migration_project"] = status_mig
            
            status_exp = form.get("status_export")
            if status_exp:
                target_obj["status"]["export"] = status_exp
            
            status_dep = form.get("status_deploy")
            if status_dep:
                target_obj["status"]["deploy"] = status_dep
            
            status_val = form.get("status_validation")
            if status_val:
                target_obj["status"]["validation"] = status_val

            # Saved Query SQL (legado - será migrado para technical_content)
            if saved_query_sql:
                if "saved_query" not in target_obj:
                    target_obj["saved_query"] = {}
                target_obj["saved_query"]["sql"] = saved_query_sql

            # Technical Content (novo modelo canônico v1.1)
            technical_content_type = form.get("technical_content_type", "NONE")
            technical_content_content = form.get("technical_content_content", "").strip()
            
            if "technical_content" not in target_obj:
                target_obj["technical_content"] = {"type": "NONE", "content": ""}
            
            target_obj["technical_content"]["type"] = technical_content_type
            target_obj["technical_content"]["content"] = technical_content_content

            # Identifiers (não aninhados)
            for key, value in form.items():
                if key.startswith("identifiers[") and key.endswith("]"):
                    identifier_key = key[len("identifiers["):-1]
                    target_obj.setdefault("identifiers", {})[identifier_key] = value

            # Data (schema-driven não aninhado)
            for key, value in form.items():
                if key.startswith("data[") and key.endswith("]"):
                    data_key = key[len("data["):-1]
                    target_obj.setdefault("data", {})[data_key] = value

    migration_objective_title = form.get("migration_objective_title") or "Objetivo do Projeto de Migração"
    migration_objective_content = form.get("migration_objective_content", "")
    content_lines = [
        line.strip()
        for line in migration_objective_content.splitlines()
        if line.strip()
    ]

    # Controle de versão
    version_control = {
        "current_version": form.get("version_control.current_version", ""),
        "last_update": form.get("version_control.last_update", ""),
        "author": form.get("version_control.author", "")
    }

    # Histórico de alterações
    change_history_map = {}
    for key, value in form.items():
        if key.startswith("change_history[") and key.endswith("]"):
            parts = key.replace("]", "").split("[")
            idx = int(parts[1])
            field = parts[2]
            change_history_map.setdefault(idx, {})[field] = value

    change_history = [
        change_history_map[idx] for idx in sorted(change_history_map.keys())
        if any(change_history_map[idx].values())
    ]

    latest_entry = _latest_history_entry(change_history)
    if latest_entry:
        version_control = {
            "current_version": latest_entry.get("version", ""),
            "last_update": latest_entry.get("date", ""),
            "author": latest_entry.get("author", "")
        }

    domain["project_metadata"] = {
        "migration_objective": {
            "title": migration_objective_title,
            "content": content_lines
        },
        "version_control": version_control,
        "change_history": change_history
    }

    return domain
