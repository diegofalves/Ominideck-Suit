"""
Field Descriptor — Normalização de Colunas OTM para UI

Este módulo oferece:
- FieldDescriptor: Dataclass para campo de formulário
- Type Mapping: OTM dataType → UI type
- Constraint Parsing: Extração de validações
- Section Inference: Categorização automática (sem hardcode)
"""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, List, Any
from enum import Enum


# ============================================================
# Enums
# ============================================================

class FieldType(str, Enum):
    """Tipos de input suportados"""
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    BOOLEAN = "boolean"
    SELECT = "select"


class FormSection(str, Enum):
    """Seções lógicas do formulário"""
    CORE = "CORE"
    LOCALIZACAO = "LOCALIZACAO"
    DATAS = "DATAS"
    FINANCEIRO = "FINANCEIRO"
    PLANEJAMENTO = "PLANEJAMENTO"
    FLEXFIELDS = "FLEXFIELDS"
    TECNICO = "TECNICO"
    OUTROS = "OUTROS"


# ============================================================
# FieldDescriptor
# ============================================================

@dataclass
class FieldDescriptor:
    """
    Normalização de uma coluna OTM para campo de formulário.
    
    Atributos:
    - name: Nome técnico da coluna
    - label: Descrição amigável para UI
    - type: Tipo de input (FieldType)
    - required: Campo obrigatório?
    - maxLength: Tamanho máximo (se VARCHAR2)
    - defaultValue: Valor padrão
    - constraint: Restrições (opções, ranges, etc)
    - lookup: Metadados de FK para autocomplete
    - section: Seção lógica do formulário
    """
    
    name: str
    label: str
    type: FieldType
    required: bool
    maxLength: Optional[int] = None
    defaultValue: Optional[str] = None
    constraint: Optional[dict] = None
    lookup: Optional[dict] = None
    section: FormSection = FormSection.OUTROS
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dict (serializable para JSON)"""
        d = asdict(self)
        d["type"] = self.type.value
        d["section"] = self.section.value
        return d
    
    def is_select_field(self) -> bool:
        """Determina se é campo com seleção (dropdown)"""
        return self.type == FieldType.SELECT or self.lookup is not None
    
    def get_options(self) -> List[str]:
        """Retorna opções do campo (se select)"""
        if self.constraint and "options" in self.constraint:
            return self.constraint["options"]
        return []


# ============================================================
# Type Inference
# ============================================================

class TypeMapper:
    """Mapeia OTM dataType para UI FieldType"""
    
    @staticmethod
    def infer_type(
        data_type: str,
        constraint_values: str = "",
        conditional_constraint: str = ""
    ) -> FieldType:
        """
        Infere tipo UI a partir de dataType e restrições.
        
        Estratégia:
        1. Se VARCHAR2 + constraintValues => SELECT
        2. Se VARCHAR2 + Y/N pattern => BOOLEAN
        3. Se VARCHAR2 => TEXT
        4. Se NUMBER => NUMBER
        5. Se DATE => DATE
        6. Default => TEXT
        """
        
        data_type_upper = data_type.upper()
        
        if "VARCHAR2" in data_type_upper:
            # Check Y/N pattern first
            if constraint_values:
                if ("'Y'" in constraint_values and "'N'" in constraint_values) or \
                   ("Y'" in constraint_values and "N'" in constraint_values):
                    return FieldType.BOOLEAN
            
            # Check for other constraints => select
            if constraint_values and constraint_values.strip():
                return FieldType.SELECT
            
            return FieldType.TEXT
        
        elif "NUMBER" in data_type_upper:
            return FieldType.NUMBER
        
        elif "DATE" in data_type_upper:
            return FieldType.DATE
        
        elif "CHAR" in data_type_upper:
            # CHAR(1) commonly used for Y/N flags
            if constraint_values and ("'Y'" in constraint_values or "'N'" in constraint_values):
                return FieldType.BOOLEAN
            return FieldType.TEXT
        
        return FieldType.TEXT


# ============================================================
# Constraint Parsing
# ============================================================

class ConstraintParser:
    """Parser para restrições OTM"""
    
    @staticmethod
    def parse(
        constraint_values: str = "",
        conditional_constraint: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        Parseia constraintValues e conditionalConstraint.
        
        Retorna dict com:
        - options: [str] lista de valores permitidos
        - conditional: str regra condicional
        - ranges: {min, max} para NUMBER
        """
        
        if not constraint_values and not conditional_constraint:
            return None
        
        result = {}
        
        # Parse constraintValues (lista de opções)
        if constraint_values and constraint_values.strip():
            options = ConstraintParser._extract_options(constraint_values)
            if options:
                result["options"] = options
        
        # Parse conditionalConstraint (rules, ranges)
        if conditional_constraint and conditional_constraint.strip():
            result["conditional"] = conditional_constraint
            
            # Try to extract range from BETWEEN expressions
            ranges = ConstraintParser._extract_range(conditional_constraint)
            if ranges:
                result.update(ranges)
        
        return result if result else None
    
    @staticmethod
    def _extract_options(constraint_str: str) -> List[str]:
        """
        Extrai lista de opções de string como: 'Y','N' ou 'A','B','C'
        """
        # Remove aspas simples e split por vírgula
        options_str = constraint_str.replace("'", "").replace('"', '')
        
        if not options_str.strip():
            return []
        
        options = [
            opt.strip()
            for opt in options_str.split(",")
            if opt.strip()
        ]
        
        return options
    
    @staticmethod
    def _extract_range(conditional_str: str) -> Optional[Dict[str, int]]:
        """
        Extrai range de expressões como: 'PRIORITY BETWEEN 1 AND 999'
        """
        upper = conditional_str.upper()
        
        if "BETWEEN" not in upper:
            return None
        
        import re
        
        # Padrão: BETWEEN <num> AND <num>
        match = re.search(r"BETWEEN\s+(\d+)\s+AND\s+(\d+)", upper)
        if match:
            return {
                "min": int(match.group(1)),
                "max": int(match.group(2))
            }
        
        return None


# ============================================================
# Section Inference
# ============================================================

class SectionInferencer:
    """Infere seção lógica baseado em padrões de nome (sem hardcode)"""
    
    # Padrões para cada seção
    SECTION_PATTERNS = {
        FormSection.CORE: [
            r".*_GID$",           # Global ID
            r".*_XID$",           # External ID
            r".*_NAME$",          # Names
            r"^DOMAIN_",          # Domain identifiers
        ],
        
        FormSection.LOCALIZACAO: [
            r".*LOCATION.*",
            r".*_LOC_.*",
            r".*ADDRESS.*",
            r".*WAREHOUSE.*",
            r".*SITE.*",
        ],
        
        FormSection.DATAS: [
            r".*_DATE$",
            r".*_TIME$",
            r".*_DT$",
            r".*_DATETIME$",
            r".*_TS$",            # timestamp
            r"^EFFECTIVE_DATE",
            r"^EXPIRATION_DATE",
        ],
        
        FormSection.FINANCEIRO: [
            r".*_AMOUNT$",
            r".*_COST$",
            r".*_RATE$",
            r".*_PRICE$",
            r".*_FEE$",
            r".*CURRENCY.*",
            r".*FINANCIAL.*",
        ],
        
        FormSection.PLANEJAMENTO: [
            r".*_PLAN_.*",
            r".*_SCHEDULE_.*",
            r".*FORECAST.*",
            r".*CAPACITY.*",
            r".*RESOURCE.*",
        ],
        
        FormSection.FLEXFIELDS: [
            r"^ATTRIBUTE.*",
            r"^FLEX_.*",
            r"^CUSTOM_.*",
        ],
        
        FormSection.TECNICO: [
            r"^INSERT_.*",        # Audit: inserção
            r"^UPDATE_.*",        # Audit: atualização
            r"^DELETE_.*",        # Audit: deleção
            r".*_SEQ$",           # Sequences
            r".*_ID$",            # Generic IDs
            r"^DOMAIN_NAME$",
            r"^STATUS$",
            r"^ENABLED$",
        ],
    }
    
    @staticmethod
    def infer(column_name: str) -> FormSection:
        """
        Infere seção baseado em padrões de nome (case-insensitive).
        
        Usa regex para ser flexível sem hardcode.
        Priority: ordem de verificação na lista SECTION_PATTERNS.
        """
        
        import re
        
        upper_name = column_name.upper()
        
        # Tenta cada seção em ordem de prioridade
        for section, patterns in SectionInferencer.SECTION_PATTERNS.items():
            for pattern in patterns:
                if re.match(pattern, upper_name):
                    return section
        
        # Default
        return FormSection.OUTROS


# ============================================================
# Lookup Builder
# ============================================================

class LookupBuilder:
    """Constrói metadados de lookup para autocomplete em FKs"""
    
    @staticmethod
    def build_from_fk(fk_info: Optional[Dict[str, str]]) -> Optional[Dict[str, str]]:
        """
        Constrói metadados de lookup a partir de ForeignKeyInfo.
        
        Retorna: {table: str, column: str}
        """
        
        if not fk_info:
            return None
        
        return {
            "table": fk_info.get("table"),
            "column": fk_info.get("column"),
        }
