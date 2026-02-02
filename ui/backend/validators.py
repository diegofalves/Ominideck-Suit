"""
Validadores de domínio para Projeto de Migração OTM
Implementa regras de negócio e validações estruturais
"""


class DomainValidationError(Exception):
    pass


OBJECT_TYPE_RULES = {
    "SAVED_QUERY": ["query_name"],
    "AGENT": ["agent_gid"],
    "TABLE": ["table_name"],
    "FINDER_SET": ["finder_set_gid"],
    "RATE": ["rate_offering_gid"],
    "EVENT_GROUP": ["event_group_gid"],
}


def validate_project(domain):
    errors = []

    project = domain.get("project", {})
    env = project.get("environment", {})

    if not project.get("code"):
        errors.append("Código do projeto é obrigatório.")

    if not project.get("version"):
        errors.append("Versão do projeto é obrigatória.")

    if env.get("source") == env.get("target"):
        errors.append("Ambiente de origem e destino não podem ser iguais.")

    groups = domain.get("groups", [])
    if not groups:
        errors.append("O projeto deve conter ao menos um grupo.")

    for g_idx, group in enumerate(groups, start=1):
        if not group.get("label"):
            errors.append(f"Grupo {g_idx}: label é obrigatório.")

        seq = group.get("sequence")
        try:
            seq_int = int(seq)
            if seq_int <= 0:
                errors.append(f"Grupo {g_idx}: sequência inválida.")
        except (ValueError, TypeError):
            errors.append(f"Grupo {g_idx}: sequência inválida.")

        objects = group.get("objects", [])
        if not objects:
            errors.append(f"Grupo {g_idx}: deve conter ao menos um objeto.")

        for o_idx, obj in enumerate(objects, start=1):
            obj_type = obj.get("object_type")
            if not obj_type:
                errors.append(f"Grupo {g_idx} / Objeto {o_idx}: object_type é obrigatório.")
                continue

            required_ids = OBJECT_TYPE_RULES.get(obj_type, [])
            identifiers = obj.get("identifiers", {})

            for rid in required_ids:
                if not identifiers.get(rid):
                    errors.append(
                        f"Grupo {g_idx} / Objeto {o_idx}: {rid} é obrigatório para {obj_type}."
                    )

    if errors:
        raise DomainValidationError(errors)
