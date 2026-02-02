from collections import defaultdict


# Tipos lógicos (não são tabelas OTM)
LOGICAL_OBJECT_TYPES = {
    "SAVED_QUERY",
    "AGENT",
    "FINDER_SET",
    "RATE",
    "EVENT_GROUP",
}


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
                "source": form.get("environment.source", ""),
                "target": form.get("environment.target", ""),
            },
        },
        "groups": [],
        "state": {
            "overall_status": "PENDING"
        }
    }

    groups = defaultdict(lambda: {"objects": []})

    for key, value in form.items():
        if not key.startswith("groups["):
            continue

        # Ex: groups[0][label]
        parts = key.replace("]", "").split("[")

        group_idx = int(parts[1])

        if parts[2] == "label":
            groups[group_idx]["label"] = value

        elif parts[2] == "sequence":
            groups[group_idx]["sequence"] = int(value)

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
                        "deployment": "PENDING"
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
                # Campo de status documentação
                if "status" not in obj:
                    obj["status"] = {}
                obj["status"]["documentation"] = value
            
            elif parts[4] == "status_deployment":
                # Campo de status deployment
                if "status" not in obj:
                    obj["status"] = {}
                obj["status"]["deployment"] = value
            
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
            "label": g.get("label"),
            "sequence": g.get("sequence"),
            "objects": g.get("objects", [])
        }
        for _, g in sorted(groups.items())
    ]
    
    # Processar saved_query_sql do formulário de edição (não aninhado)
    saved_query_sql = form.get("saved_query_sql", "").strip()
    object_name = form.get("object_name", "").strip()
    
    # Se estamos editando um objeto (campos não-aninhados presentes)
    if object_name:
        # Buscar o último grupo com objetos
        for group in domain["groups"]:
            if group.get("objects"):
                last_obj = group["objects"][-1]
                
                # Atualizar campos do objeto em edição
                if object_name:
                    last_obj["name"] = object_name
                
                object_description = form.get("object_description", "")
                if object_description:
                    last_obj["description"] = object_description
                
                # Status
                status_doc = form.get("status_documentation")
                status_dep = form.get("status_deployment")
                if status_doc or status_dep:
                    if "status" not in last_obj:
                        last_obj["status"] = {}
                    if status_doc:
                        last_obj["status"]["documentation"] = status_doc
                    if status_dep:
                        last_obj["status"]["deployment"] = status_dep
                
                # Saved Query SQL
                if saved_query_sql:
                    if "saved_query" not in last_obj:
                        last_obj["saved_query"] = {}
                    last_obj["saved_query"]["sql"] = saved_query_sql

    return domain
