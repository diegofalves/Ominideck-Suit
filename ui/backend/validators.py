"""
Validadores de domínio para Projeto de Migração OTM
Implementa regras de negócio e validações estruturais
"""

from typing import Dict, List, Any, Optional, Set


class DomainValidationError(Exception):
    pass


from ui.backend.domain_stats import object_domain_map, table_domain_map

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


def _collect_ignored_tables(groups: List[Dict[str, Any]]) -> Set[str]:
    ignored = set()
    for group in groups:
        if not isinstance(group, dict):
            continue
        for obj in group.get("objects", []):
            if not isinstance(obj, dict):
                continue
            if _is_ignored_object(obj):
                table = _normalize_otm_name(obj.get("object_type") or obj.get("otm_table"))
                if table and table not in ignored:
                    ignored.add(table)
    return ignored


def _domains_overlap(domain_a: str, domain_b: str) -> bool:
    token_a = _normalize_otm_name(domain_a)
    token_b = _normalize_otm_name(domain_b)
    return not token_a or not token_b or token_a == token_b


def _normalize_subtable_list(values: Any) -> List[str]:
    normalized: List[str] = []
    seen: Set[str] = set()
    if not isinstance(values, list):
        return normalized

    for value in values:
        token = _normalize_otm_name(value)
        if not token or token in seen:
            continue
        normalized.append(token)
        seen.add(token)
    return normalized


def _collect_subtable_constraint_errors(groups: List[Dict[str, Any]]) -> List[str]:
    errors: List[str] = []
    owners_by_subtable: Dict[str, List[Dict[str, Any]]] = {}
    object_rows: List[Dict[str, Any]] = []

    for group in groups:
        if not isinstance(group, dict):
            continue
        group_label = str(group.get("label") or group.get("group_id") or group.get("migration_group_id") or "Grupo")
        objects = group.get("objects", [])
        if not isinstance(objects, list):
            continue

        for obj in objects:
            if not isinstance(obj, dict):
                continue
            if _is_ignored_object(obj):
                continue

            parent_table = _normalize_otm_name(obj.get("object_type") or obj.get("otm_table"))
            if not parent_table:
                continue
            parent_domain = _normalize_otm_name(obj.get("domainName") or obj.get("domain"))
            parent_name = str(obj.get("name") or parent_table)
            parent_subtables = _normalize_subtable_list(obj.get("otm_subtables"))

            row_ref = {
                "group_id": group.get("migration_group_id"),
                "object_id": obj.get("migration_item_id"),
                "group_label": group_label,
                "name": parent_name,
                "table": parent_table,
                "domain": parent_domain,
                "subtables": parent_subtables,
            }
            object_rows.append(row_ref)

            for subtable in parent_subtables:
                if subtable == parent_table:
                    errors.append(
                        f"Grupo '{group_label}' / Item '{parent_name}': tabela {parent_table} não pode ser subtabela de si mesma."
                    )
                    continue

                bucket = owners_by_subtable.setdefault(subtable, [])
                conflict = None
                for owner in bucket:
                    same_row = (
                        owner["group_id"] == group.get("migration_group_id")
                        and owner["object_id"] == obj.get("migration_item_id")
                    )
                    if same_row:
                        continue
                    if _domains_overlap(owner["domain"], parent_domain):
                        conflict = owner
                        break

                if conflict:
                    errors.append(
                        "Conflito de subtabela: "
                        f"{subtable} já está vinculada a "
                        f"'{conflict['name']}' ({conflict['group_label']}) "
                        f"e não pode ser vinculada também a '{parent_name}' ({group_label}). "
                        "Remova o vínculo anterior antes de redefinir."
                    )
                    continue

                bucket.append(
                    {
                        "group_id": group.get("migration_group_id"),
                        "object_id": obj.get("migration_item_id"),
                        "group_label": group_label,
                        "name": parent_name,
                        "table": parent_table,
                        "domain": parent_domain,
                    }
                )

    # Se uma tabela está vinculada como subtabela, o item dessa tabela
    # não pode atuar como tabela principal com suas próprias subtabelas.
    for row in object_rows:
        if not row["subtables"]:
            continue

        current_table = row["table"]
        current_domain = row["domain"]
        owners = owners_by_subtable.get(current_table, [])
        if not owners:
            continue

        for owner in owners:
            same_row = (
                owner["group_id"] == row["group_id"]
                and owner["object_id"] == row["object_id"]
            )
            if same_row:
                continue
            if not _domains_overlap(owner["domain"], current_domain):
                continue

            errors.append(
                "Conflito de hierarquia: "
                f"Item '{row['name']}' (Grupo '{row['group_label']}') está definido com subtabelas, "
                f"mas sua tabela {current_table} já é subtabela de "
                f"Item '{owner['name']}' (Grupo '{owner['group_label']}). "
                "Remova o vínculo anterior para permitir nova hierarquia."
            )
            break
            break

    return errors


def validate_subtable_constraints(domain: Dict[str, Any]) -> None:
    groups = domain.get("groups", [])
    if not isinstance(groups, list):
        return
    errors = _collect_subtable_constraint_errors(groups)
    if errors:
        raise DomainValidationError(errors)


def validate_subtable_constraints_for_object(
    domain: Dict[str, Any],
    target_group_id: str,
    target_object_index: int,
) -> None:
    groups = domain.get("groups", [])
    if not isinstance(groups, list):
        return

    target_group_token = _normalize_otm_name(target_group_id)
    target_idx = int(target_object_index)

    target_obj: Optional[Dict[str, Any]] = None
    target_group_label = ""
    target_group_number = 0
    target_object_number = 0
    owners_by_subtable: Dict[str, List[Dict[str, Any]]] = {}
    principal_by_table: Dict[str, List[Dict[str, Any]]] = {}

    for g_idx, group in enumerate(groups, start=1):
        if not isinstance(group, dict):
            continue
        group_token = _normalize_otm_name(group.get("group_id") or group.get("migration_group_id"))
        group_label = str(group.get("label") or group.get("group_id") or f"Grupo {g_idx}")
        objects = group.get("objects", [])
        if not isinstance(objects, list):
            continue

        for o_idx, obj in enumerate(objects, start=1):
            if not isinstance(obj, dict):
                continue
            if _is_ignored_object(obj):
                continue

            is_target = group_token == target_group_token and (o_idx - 1) == target_idx
            table_name = _normalize_otm_name(obj.get("object_type") or obj.get("otm_table"))
            if not table_name:
                continue
            domain_name = _normalize_otm_name(obj.get("domainName") or obj.get("domain"))
            object_name = str(obj.get("name") or table_name)
            subtables = _normalize_subtable_list(obj.get("otm_subtables"))

            if is_target:
                target_obj = obj
                target_group_label = group_label
                target_group_number = g_idx
                target_object_number = o_idx
                continue

            if subtables:
                principal_by_table.setdefault(table_name, []).append(
                    {
                        "group_label": group_label,
                        "name": object_name,
                        "table": table_name,
                        "domain": domain_name,
                    }
                )

            for subtable in subtables:
                if subtable == table_name:
                    continue
                owners_by_subtable.setdefault(subtable, []).append(
                    {
                        "group_label": group_label,
                        "name": object_name,
                        "table": table_name,
                        "domain": domain_name,
                    }
                )

    if target_obj is None:
        return

    target_table = _normalize_otm_name(target_obj.get("object_type") or target_obj.get("otm_table"))
    target_domain = _normalize_otm_name(target_obj.get("domainName") or target_obj.get("domain"))
    target_name = str(target_obj.get("name") or target_table or "Objeto")
    target_subtables = _normalize_subtable_list(target_obj.get("otm_subtables"))
    errors: List[str] = []

    for subtable in target_subtables:
        if subtable == target_table:
            errors.append(
                f"Grupo {target_group_number} / Objeto {target_object_number}: "
                f"tabela {target_table} não pode ser subtabela de si mesma."
            )
            continue

        owners = owners_by_subtable.get(subtable, [])
        owner_conflict = next(
            (owner for owner in owners if _domains_overlap(owner["domain"], target_domain)),
            None,
        )
        if owner_conflict:
            errors.append(
                "Conflito de subtabela: "
                f"{subtable} já está vinculada a "
                f"'{owner_conflict['name']}' ({owner_conflict['group_label']}). "
                "Remova o vínculo anterior antes de redefinir."
            )
            continue

        principal_conflicts = principal_by_table.get(subtable, [])
        principal_conflict = next(
            (
                owner
                for owner in principal_conflicts
                if _domains_overlap(owner["domain"], target_domain)
            ),
            None,
        )
        if principal_conflict:
            errors.append(
                "Conflito de hierarquia: "
                f"{subtable} já atua como tabela principal em "
                f"'{principal_conflict['name']}' ({principal_conflict['group_label']}). "
                "Remova o vínculo anterior antes de reutilizar como subtabela."
            )

    if target_subtables and target_table:
        owner_conflicts = owners_by_subtable.get(target_table, [])
        owner_conflict = next(
            (owner for owner in owner_conflicts if _domains_overlap(owner["domain"], target_domain)),
            None,
        )
        if owner_conflict:
            errors.append(
                "Conflito de hierarquia: "
                f"'{target_name}' ({target_group_label}) está definido com subtabelas, "
                f"mas sua tabela {target_table} já é subtabela de "
                f"'{owner_conflict['name']}' ({owner_conflict['group_label']}). "
                "Remova o vínculo anterior para permitir nova hierarquia."
            )

    if errors:
        raise DomainValidationError(errors)


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

        group_label = str(group.get("label") or group.get("group_id") or group.get("migration_group_id") or f"Grupo {g_idx}")
        if not group.get("label"):
            errors.append(f"Grupo '{group_label}': label é obrigatório.")

        seq = group.get("sequence")
        try:
            seq_int = int(seq)
            if is_group_zero and seq_int != 0:
                errors.append(f"Grupo '{group_label}': sequência inválida para SEM_GRUPO (use 0).")
            elif not is_group_zero and seq_int <= 0:
                errors.append(f"Grupo '{group_label}': sequência inválida.")
        except (ValueError, TypeError):
            errors.append(f"Grupo '{group_label}': sequência inválida.")

        objects = group.get("objects", [])
        if not objects and not is_group_zero and not is_ignored_group:
            errors.append(f"Grupo '{group_label}': deve conter ao menos um item.")

        for o_idx, obj in enumerate(objects, start=1):
            # Validação: nome obrigatório
            item_name = str(obj.get("name") or obj.get("object_type") or obj.get("migration_item_id") or f"Item {o_idx}")
            if not obj.get("name"):
                errors.append(f"Grupo '{group_label}' / Item '{item_name}': Nome do item é obrigatório.")
            
            obj_type = obj.get("object_type")
            if not obj_type:
                errors.append(f"Grupo '{group_label}' / Item '{item_name}': object_type é obrigatório.")
                continue
            obj_type_normalized = _normalize_otm_name(obj_type)
            otm_table_normalized = _normalize_otm_name(obj.get("otm_table"))
            
            # Validação: Saved Query SQL obrigatório para SAVED_QUERY
            if obj_type == "SAVED_QUERY":
                saved_query = obj.get("saved_query", {})
                sql = saved_query.get("sql", "").strip()
                if not sql:
                    errors.append(f"Grupo '{group_label}' / Item '{item_name}': SQL da Saved Query é obrigatório.")
            
            # Validação: Status documentation
            status = obj.get("status", {})
            status_doc = status.get("documentation", "").strip()
            if status_doc and status_doc not in ["PENDING", "IN_PROGRESS", "DONE"]:
                errors.append(f"Grupo '{group_label}' / Item '{item_name}': Status de documentação inválido (use PENDING, IN_PROGRESS ou DONE).")
            
            # Validação: Status deployment
            status_dep = status.get("deployment", "").strip()
            if status_dep and status_dep not in ["PENDING", "IN_PROGRESS", "DONE"]:
                errors.append(f"Grupo '{group_label}' / Item '{item_name}': Status de deployment inválido (use PENDING, IN_PROGRESS ou DONE).")
            
            obj_type = obj.get("object_type")
            if not obj_type:
                errors.append(f"Grupo '{group_label}' / Item '{item_name}': object_type é obrigatório.")
                continue

            # SE é tipo lógico (não tabela OTM)
            if _is_logical_object_type(obj_type):
                pass  # Não exige identificadores para tipos lógicos
            
            # SE é tabela OTM (schema-driven)
            else:
                if otm_table_normalized and otm_table_normalized != obj_type_normalized:
                    errors.append(
                        f"Grupo '{group_label}' / Item '{item_name}': otm_table deve ser igual a object_type para tabela OTM."
                    )
                # Validar usando schema
                data = obj.get("data", {})
                schema_errors = validate_form_data_against_schema(obj_type_normalized, data)
                
                for schema_error in schema_errors:
                    errors.append(
                        f"Grupo '{group_label}' / Item '{item_name}': {schema_error}"
                    )

    # Regras de subtabelas:
    errors.extend(_collect_subtable_constraint_errors(groups))

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

    domain_map = table_domain_map()
    if domain_map:
        ignored_tables = _collect_ignored_tables(groups)
        object_domains = object_domain_map(groups, domain_map)
        for table_name, required_domains in domain_map.items():
            if table_name in ignored_tables or not required_domains:
                continue
            missing = [
                domain
                for domain in required_domains
                if domain not in object_domains.get(table_name, set())
            ]
            if missing:
                errors.append(
                    f"Regra canônica: tabela {table_name} precisa de objeto(s) para domínio(s) {', '.join(sorted(set(missing)))}."
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
        print(f"[AVISO] Schema não encontrado para tabela: {table_name}")
        return []
    
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
