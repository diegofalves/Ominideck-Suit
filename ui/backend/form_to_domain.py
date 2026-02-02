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
                    "identifiers": {},
                    "data": {}
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
            
            else:
                # Campos genéricos do objeto
                obj[parts[4]] = value

    # Normaliza para lista ordenada
    domain["groups"] = [
        {
            "label": g.get("label"),
            "sequence": g.get("sequence"),
            "objects": g.get("objects", [])
        }
        for _, g in sorted(groups.items())
    ]

    return domain
