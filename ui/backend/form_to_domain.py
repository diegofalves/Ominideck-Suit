from collections import defaultdict


def form_to_domain(form):
    """
    Converte request.form (flat) em estrutura de domínio canônica
    compatível com schema.json
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
                    "identifiers": {}
                })

            obj = groups[group_idx]["objects"][obj_idx]

            if parts[4] == "identifiers":
                identifier_key = parts[5]
                obj["identifiers"][identifier_key] = value
            else:
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
