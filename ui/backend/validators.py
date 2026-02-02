"""
Validadores de domínio para Projeto de Migração OTM
Implementa regras de negócio e validações estruturais
"""

from typing import Dict, List, Any, Optional


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


# ============================================================
# Schema-Aware Validation (Fase 5)
# ============================================================

def validate_form_data_against_schema(
    table_name: str,
    form_data: Dict[str, Any],
    repo=None  # Injected SchemaRepository
) -> List[str]:
    """
    Valida dados de formulário contra schema OTM da tabela.
    
    Verifica:
    1. Coluna existe no schema
    2. Campo obrigatório está preenchido
    3. Tipo de dado é compatível
    4. Constraint é respeitado (range, opções)
    5. Tamanho máximo respeitado
    
    Retorna: Lista de erros (vazia se tudo OK)
    """
    
    errors = []
    
    if repo is None:
        from .schema_repository import SchemaRepository
        repo = SchemaRepository()
    
    # Carrega descriptores
    descriptors = repo.get_field_descriptors(table_name)
    
    if not descriptors:
        errors.append(f"Schema não encontrado para tabela: {table_name}")
        return errors
    
    # Cria mapa nome_coluna => descriptor
    desc_map = {d.name: d for d in descriptors}
    
    # Valida cada campo do formulário
    for field_name, field_value in form_data.items():
        if field_name not in desc_map:
            # Campo não existe no schema? Pode ser um campo técnico/meta
            # Silenciamos este erro por enquanto
            continue
        
        descriptor = desc_map[field_name]
        
        # Validação 1: Campo obrigatório
        if descriptor.required and not field_value:
            errors.append(f"Campo obrigatório: {descriptor.label}")
            continue
        
        # Skip se vazio e não obrigatório
        if not field_value:
            continue
        
        # Validação 2: Tipo de dado
        type_error = _validate_field_type(
            field_name,
            field_value,
            descriptor.type
        )
        if type_error:
            errors.append(type_error)
            continue
        
        # Validação 3: Tamanho máximo
        if descriptor.maxLength and isinstance(field_value, str):
            if len(field_value) > descriptor.maxLength:
                errors.append(
                    f"{descriptor.label}: máximo {descriptor.maxLength} caracteres"
                )
        
        # Validação 4: Constraint (opções, range)
        constraint_error = _validate_constraint(
            field_name,
            field_value,
            descriptor.constraint,
            descriptor.type
        )
        if constraint_error:
            errors.append(constraint_error)
    
    return errors


def _validate_field_type(
    field_name: str,
    field_value: Any,
    expected_type: str
) -> Optional[str]:
    """
    Valida tipo de campo.
    Retorna mensagem de erro ou None se OK.
    """
    
    if expected_type == "number":
        try:
            float(field_value)
        except (ValueError, TypeError):
            return f"{field_name}: deve ser um número"
    
    elif expected_type == "date":
        # Aceita qualquer formato, Flask/HTML5 encarrega de parsear
        if not field_value:
            return None
        # Validação básica: yyyy-mm-dd
        if isinstance(field_value, str) and len(field_value) > 0:
            if not _is_valid_date_format(field_value):
                return f"{field_name}: formato de data inválido"
    
    elif expected_type == "boolean":
        if field_value not in ["Y", "N", "y", "n", True, False]:
            return f"{field_name}: deve ser Y ou N"
    
    return None


def _validate_constraint(
    field_name: str,
    field_value: Any,
    constraint: Optional[Dict[str, Any]],
    field_type: str
) -> Optional[str]:
    """
    Valida constraints (opções, range).
    Retorna mensagem de erro ou None.
    """
    
    if not constraint:
        return None
    
    # Constraint: options (select)
    if "options" in constraint:
        options = constraint["options"]
        if field_value not in options:
            return f"{field_name}: valor deve estar em {', '.join(options)}"
    
    # Constraint: range (number)
    if field_type == "number" and ("min" in constraint or "max" in constraint):
        try:
            num_value = float(field_value)
            
            if "min" in constraint and num_value < constraint["min"]:
                return f"{field_name}: mínimo é {constraint['min']}"
            
            if "max" in constraint and num_value > constraint["max"]:
                return f"{field_name}: máximo é {constraint['max']}"
        except (ValueError, TypeError):
            pass
    
    return None


def _is_valid_date_format(date_str: str) -> bool:
    """Validação simples de formato de data (yyyy-mm-dd)"""
    import re
    return bool(re.match(r'^\d{4}-\d{2}-\d{2}$', date_str))

    if errors:
        raise DomainValidationError(errors)
