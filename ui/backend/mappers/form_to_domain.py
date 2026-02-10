def map_project(form, groups_catalog=None, existing_project=None):
    groups_catalog = groups_catalog or {}
    existing_project = existing_project or {}

    # Suportar tanto ImmutableMultiDict (form) quanto dict
    if hasattr(form, 'getlist'):
        selected_group_ids = form.getlist("groups")
    else:
        groups_value = form.get("groups", [])
        selected_group_ids = groups_value if isinstance(groups_value, list) else [groups_value] if groups_value else []

    # Construir grupos preservando objetos existentes
    existing_groups = {g["group_id"]: g for g in existing_project.get("groups", [])}
    
    groups = []
    for group_id in selected_group_ids:
        meta = groups_catalog.get(group_id)
        if not meta:
            continue

        # Preservar objetos existentes do grupo
        existing_objects = []
        if group_id in existing_groups:
            existing_objects = existing_groups[group_id].get("objects", [])

        groups.append({
            "group_id": group_id,
            "label": meta["label"],
            "sequence": meta["sequence"],
            "objects": existing_objects.copy()
        })

    active_group_id = form.get("active_group_id")
    edit_object_index_str = form.get("edit_object_index", "").strip()
    
    # Converter edit_object_index para int (-1 se vazio)
    try:
        edit_object_index = int(edit_object_index_str) if edit_object_index_str else -1
    except (ValueError, TypeError):
        edit_object_index = -1

    # Verificar se há solicitação de remoção
    remove_object_index_str = form.get("remove_object_index", "").strip()
    try:
        remove_object_index = int(remove_object_index_str) if remove_object_index_str else -1
    except (ValueError, TypeError):
        remove_object_index = -1

    # PRIMEIRA ETAPA: Processar remoção se solicitado
    if active_group_id and remove_object_index >= 0:
        # Encontrar o grupo ativo para remover
        target_group = None
        for group in groups:
            if group["group_id"] == active_group_id:
                target_group = group
                break
        
        if target_group is not None and remove_object_index < len(target_group["objects"]):
            # Remover objeto no índice especificado
            del target_group["objects"][remove_object_index]
            # Resetar edit_object_index após remoção
            edit_object_index = -1

    # SEGUNDA ETAPA: Processar criação/edição de objeto se houver grupo ativo e campos preenchidos
    if active_group_id:
        object_type = form.get("object_type", "").strip()
        
        if object_type:
            # Status default
            default_status = {
                "documentation": "PENDING",
                "migration_project": "PENDING",
                "export": "PENDING",
                "deploy": "PENDING",
                "validation": "PENDING"
            }

            # Encontrar o grupo ativo
            target_group = None
            for group in groups:
                if group["group_id"] == active_group_id:
                    target_group = group
                    break
            
            if target_group is not None:
                # Construir identifiers baseado no tipo
                identifiers = {}
                if object_type == "SAVED_QUERY":
                    identifiers["query_name"] = form.get("identifiers_query_name", "").strip()
                elif object_type == "AGENT":
                    identifiers["agent_gid"] = form.get("identifiers_agent_gid", "").strip()
                elif object_type == "TABLE":
                    identifiers["table_name"] = form.get("identifiers_table_name", "").strip()
                elif object_type == "FINDER_SET":
                    identifiers["finder_set_gid"] = form.get("identifiers_finder_set_gid", "").strip()
                elif object_type == "RATE":
                    identifiers["rate_offering_gid"] = form.get("identifiers_rate_offering_gid", "").strip()
                elif object_type == "EVENT_GROUP":
                    identifiers["event_group_gid"] = form.get("identifiers_event_group_gid", "").strip()
                
                # Distinguir entre criação e edição
                if edit_object_index >= 0 and edit_object_index < len(target_group["objects"]):
                    # MODO EDIÇÃO: Substituir objeto existente
                    existing_obj = target_group["objects"][edit_object_index]
                    obj = {
                        "type": object_type,
                        "deployment_type": form.get("object_deployment_type", "").strip(),
                        "deployment_type_user_defined": bool(form.get("object_deployment_type", "").strip()),
                        "responsible": form.get("object_responsible", "").strip(),
                        "sequence": existing_obj["sequence"],  # Manter sequence original
                        "notes": form.get("object_notes", "").strip(),
                        "status": existing_obj.get("status", default_status),  # Manter status
                        "identifiers": identifiers
                    }
                    target_group["objects"][edit_object_index] = obj
                else:
                    # MODO CRIAÇÃO: Adicionar novo objeto
                    next_sequence = len(target_group["objects"]) + 1
                    obj = {
                        "type": object_type,
                        "deployment_type": form.get("object_deployment_type", "").strip(),
                        "deployment_type_user_defined": bool(form.get("object_deployment_type", "").strip()),
                        "responsible": form.get("object_responsible", "").strip(),
                        "sequence": next_sequence,
                        "notes": form.get("object_notes", "").strip(),
                        "status": default_status,
                        "identifiers": identifiers
                    }
                    target_group["objects"].append(obj)

    return {
        "project": {
            "code": form.get("code", "").strip(),
            "name": form.get("name", "").strip(),
            "version": form.get("version", "").strip(),
            "consultant": form.get("consultant", "").strip(),
            "environment": {
                "source": form.get("environment_source", "").strip(),
                "target": form.get("environment_target", "").strip(),
            },
        },
        "groups": groups,
        "state": {
            "overall_status": "PENDING",
            "last_edit_object_index": edit_object_index if edit_object_index >= 0 else None
        },
        "active_group_id": active_group_id
    }
