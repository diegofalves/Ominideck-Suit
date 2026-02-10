"""
Validadores de domínio para Projeto de Migração OTM
Implementa regras de negócio e validações estruturais
"""

from typing import Dict, List, Any, Optional


class DomainValidationError(Exception):
    pass


GROUP_ZERO_ID = "SEM_GRUPO"
LEGACY_GROUP_ZERO_IDS = {"GROUP_0", GROUP_ZERO_ID}
IGNORED_GROUP_ID = "IGNORADOS"


# Tipos lógicos (não são tabelas OTM)
LOGICAL_OBJECT_TYPES = {
    "SAVED_QUERY": ["query_name"],
    "AGENT": ["agent_gid"],
    "FINDER_SET": ["finder_set_gid"],
    "RATE": ["rate_offering_gid"],
    "EVENT_GROUP": ["event_group_gid"],
}


def _normalize_otm_name(value: Any) -> str:
    return str(value or "").strip().upper()


def _is_logical_object_type(object_type: str) -> bool:
    return _normalize_otm_name(object_type) in LOGICAL_OBJECT_TYPES


def _is_ignored_object(obj: Dict[str, Any]) -> bool:
    return str(obj.get("ignore_table") or "").strip().lower() in {"1", "true", "on", "yes", "y"}


def _collect_otm_table_object_counts(groups: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Regra canônica:
    Toda tabela OTM contida no projeto deve ter ao menos 1 objeto associado.
    """
    counts: Dict[str, int] = {}

    for group in groups:
        if not isinstance(group, dict):
            continue

        objects = group.get("objects", [])
        if not isinstance(objects, list):
            continue

        for obj in objects:
            if not isinstance(obj, dict):
                continue
            if _is_ignored_object(obj):
                continue

            object_type = _normalize_otm_name(obj.get("object_type"))
            if not object_type:
                continue

            if _is_logical_object_type(object_type):
                continue

            # A associação canônica de objeto -> tabela usa object_type.
            counts[object_type] = counts.get(object_type, 0) + 1

    return counts


def _collect_declared_otm_tables(groups: List[Dict[str, Any]]) -> List[str]:
    declared = set()
    for group in groups:
        if not isinstance(group, dict):
            continue

        objects = group.get("objects", [])
        if not isinstance(objects, list):
            continue

        for obj in objects:
            if not isinstance(obj, dict):
                continue
            if _is_ignored_object(obj):
                continue

            otm_table = _normalize_otm_name(obj.get("otm_table"))
            if not otm_table:
                continue
            if _is_logical_object_type(otm_table):
                continue
            declared.add(otm_table)

    return sorted(declared)


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
        group_id = str(group.get("group_id") or "").strip().upper()
        is_group_zero = group_id in LEGACY_GROUP_ZERO_IDS
        is_ignored_group = group_id == IGNORED_GROUP_ID

        if not group.get("label"):
            errors.append(f"Grupo {g_idx}: label é obrigatório.")

        seq = group.get("sequence")
        try:
            seq_int = int(seq)
            if is_group_zero and seq_int != 0:
                errors.append(f"Grupo {g_idx}: sequência inválida para SEM_GRUPO (use 0).")
            elif not is_group_zero and seq_int <= 0:
                errors.append(f"Grupo {g_idx}: sequência inválida.")
        except (ValueError, TypeError):
            errors.append(f"Grupo {g_idx}: sequência inválida.")

        objects = group.get("objects", [])
        if not objects and not is_group_zero and not is_ignored_group:
            errors.append(f"Grupo {g_idx}: deve conter ao menos um objeto.")

        for o_idx, obj in enumerate(objects, start=1):
            # Validação: nome obrigatório
            if not obj.get("name"):
                errors.append(f"Grupo {g_idx} / Objeto {o_idx}: Nome do objeto é obrigatório.")
            
            obj_type = obj.get("object_type")
            if not obj_type:
                errors.append(f"Grupo {g_idx} / Objeto {o_idx}: object_type é obrigatório.")
                continue
            obj_type_normalized = _normalize_otm_name(obj_type)
            otm_table_normalized = _normalize_otm_name(obj.get("otm_table"))
            
            # Validação: Saved Query SQL obrigatório para SAVED_QUERY
            if obj_type == "SAVED_QUERY":
                saved_query = obj.get("saved_query", {})
                sql = saved_query.get("sql", "").strip()
                if not sql:
                    errors.append(f"Grupo {g_idx} / Objeto {o_idx}: SQL da Saved Query é obrigatório.")
            
            # Validação: Status documentation
            status = obj.get("status", {})
            status_doc = status.get("documentation", "").strip()
            if status_doc and status_doc not in ["PENDING", "IN_PROGRESS", "DONE"]:
                errors.append(f"Grupo {g_idx} / Objeto {o_idx}: Status de documentação inválido (use PENDING, IN_PROGRESS ou DONE).")
            
            # Validação: Status deployment
            status_dep = status.get("deployment", "").strip()
            if status_dep and status_dep not in ["PENDING", "IN_PROGRESS", "DONE"]:
                errors.append(f"Grupo {g_idx} / Objeto {o_idx}: Status de deployment inválido (use PENDING, IN_PROGRESS ou DONE).")
            
            obj_type = obj.get("object_type")
            if not obj_type:
                errors.append(f"Grupo {g_idx} / Objeto {o_idx}: object_type é obrigatório.")
                continue

            # SE é tipo lógico (não tabela OTM)
            if _is_logical_object_type(obj_type):
                required_ids = LOGICAL_OBJECT_TYPES[obj_type_normalized]
                identifiers = obj.get("identifiers", {})

                for rid in required_ids:
                    if not identifiers.get(rid):
                        errors.append(
                            f"Grupo {g_idx} / Objeto {o_idx}: {rid} é obrigatório para {obj_type_normalized}."
                        )
            
            # SE é tabela OTM (schema-driven)
            else:
                if otm_table_normalized and otm_table_normalized != obj_type_normalized:
                    errors.append(
                        f"Grupo {g_idx} / Objeto {o_idx}: otm_table deve ser igual a object_type para tabela OTM."
                    )
                # Validar usando schema
                data = obj.get("data", {})
                schema_errors = validate_form_data_against_schema(obj_type_normalized, data)
                
                for schema_error in schema_errors:
                    errors.append(
                        f"Grupo {g_idx} / Objeto {o_idx}: {schema_error}"
                    )

    # Regra canônica de processo:
    # cada tabela OTM presente no projeto deve estar associada a >= 1 objeto.
    # A cardinalidade superior é livre (1..N objetos por tabela).
    declared_otm_tables = _collect_declared_otm_tables(groups)
    otm_table_counts = _collect_otm_table_object_counts(groups)
    for table_name in declared_otm_tables:
        count = otm_table_counts.get(table_name, 0)
        if count < 1:
            errors.append(
                f"Regra canônica: tabela OTM {table_name} sem objeto associado."
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
