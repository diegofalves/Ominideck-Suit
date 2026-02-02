"""
Schema Repository — Foundation para OmniDeck 9.0 (Schema-Driven)

Responsável por:
- Carregar e cachear schemas OTM do disco
- Normalizar metadados em FieldDescriptors
- Fornecer metadados de relacionamentos
- Ser a fonte única de verdade para estrutura de dados
"""

from pathlib import Path
import json
from typing import Dict, List, Optional
from dataclasses import dataclass


# ============================================================
# Data Models
# ============================================================

@dataclass
class FieldDescriptor:
    """Normalização de coluna OTM para campo UI"""
    name: str              # column.name
    label: str             # column.description ou name
    type: str              # "text" | "select" | "number" | "date" | "boolean"
    required: bool         # NOT column.isNull
    maxLength: Optional[int]     # column.size
    defaultValue: Optional[str]  # column.defaultValue
    constraint: Optional[dict]   # parsed constraintValues
    lookup: Optional[dict]       # {table, column} se FK existir
    section: str           # CORE, LOCALIZACAO, DATAS, etc


@dataclass
class ForeignKeyInfo:
    """Metadados de relacionamento (sem carregar dados)"""
    column: str
    parentTable: str
    parentColumn: str
    cascadeDelete: bool


# ============================================================
# Schema Repository (Singleton)
# ============================================================

class SchemaRepository:
    """
    Repositório centralizado de schemas OTM.
    Carrega do disco uma única vez e cacheia em memória.
    """
    
    _instance = None
    _cache: Dict[str, dict] = {}
    
    BASE_PATH = Path(__file__).parent.parent.parent / "metadata" / "otm" / "tables"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def load_table(cls, table_name: str) -> Optional[dict]:
        """
        Carrega schema completo de uma tabela.
        Aceita 'ORDER_RELEASE' ou 'order_release'.
        """
        repo = cls()
        
        # Normalize name
        normalized = table_name.upper()
        
        # Check cache first
        if normalized in repo._cache:
            return repo._cache[normalized]
        
        # Try to load from disk
        file_path = repo.BASE_PATH / f"{normalized}.json"
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                schema = json.load(f)
                repo._cache[normalized] = schema
                return schema
        except Exception as e:
            print(f"Erro ao carregar schema {normalized}: {e}")
            return None
    
    @classmethod
    def list_tables(cls) -> List[str]:
        """
        Lista todas as tabelas disponíveis.
        Retorna nomes sem extensão, alfabeticamente ordenados.
        """
        repo = cls()
        
        if not repo.BASE_PATH.exists():
            return []
        
        tables = [
            f.stem  # filename without extension
            for f in repo.BASE_PATH.glob("*.json")
            if f.is_file()
        ]
        
        return sorted(tables)
    
    @classmethod
    def get_field_descriptors(cls, table_name: str) -> List[FieldDescriptor]:
        """
        Retorna descritores normalizados de campos.
        Ordena por section, depois por name.
        """
        schema = cls.load_table(table_name)
        if not schema:
            return []
        
        columns = schema.get("columns", [])
        fk_map = cls._build_fk_map(schema)
        
        descriptors = []
        for col in columns:
            descriptor = cls._column_to_field_descriptor(col, fk_map)
            descriptors.append(descriptor)
        
        # Sort: by section, then by name
        descriptors.sort(key=lambda d: (d.section, d.name))
        
        return descriptors
    
    @classmethod
    def get_foreign_keys(cls, table_name: str) -> List[ForeignKeyInfo]:
        """
        Retorna metadados de relacionamentos (sem carregar dados).
        """
        schema = cls.load_table(table_name)
        if not schema:
            return []
        
        fks = schema.get("foreignKeys", [])
        result = []
        
        for fk in fks:
            # FK pode ter múltiplos relacionamentos de colunas
            relations = fk.get("columnRelation", [])
            for rel in relations:
                info = ForeignKeyInfo(
                    column=rel.get("columnName", ""),
                    parentTable=fk.get("parentTableName", ""),
                    parentColumn=rel.get("parentColumnName", ""),
                    cascadeDelete=fk.get("cascadeDelete", False)
                )
                result.append(info)
        
        return result
    
    @classmethod
    def clear_cache(cls):
        """Limpa cache (útil para testes)"""
        repo = cls()
        repo._cache.clear()
    
    # ============================================================
    # Private Methods
    # ============================================================
    
    @staticmethod
    def _column_to_field_descriptor(col: dict, fk_map: dict) -> FieldDescriptor:
        """Converte um column OTM em FieldDescriptor"""
        
        name = col.get("name", "")
        description = col.get("description", "")
        data_type = col.get("dataType", "VARCHAR2")
        size = col.get("size")
        is_null = col.get("isNull", True)
        default = col.get("defaultValue", "")
        constraint_values = col.get("constraintValues", "")
        conditional_constraint = col.get("conditionalConstraint", "")
        
        # ---- Type inference ----
        ui_type = SchemaRepository._infer_type(
            data_type,
            constraint_values,
            conditional_constraint
        )
        
        # ---- Constraint parsing ----
        constraint = SchemaRepository._parse_constraint(
            constraint_values,
            conditional_constraint,
            ui_type
        )
        
        # ---- Lookup (FK) ----
        lookup = fk_map.get(name)
        
        # ---- Section ----
        section = SchemaRepository._infer_section(name)
        
        # ---- Label ----
        label = description if description else name
        
        # ---- Required ----
        required = not is_null
        
        # ---- Max Length ----
        max_len = int(size) if size else None
        
        return FieldDescriptor(
            name=name,
            label=label,
            type=ui_type,
            required=required,
            maxLength=max_len,
            defaultValue=default if default else None,
            constraint=constraint,
            lookup=lookup,
            section=section
        )
    
    @staticmethod
    def _infer_type(data_type: str, constraint_values: str, conditional: str) -> str:
        """
        Infere tipo UI a partir de dataType e restrições.
        
        Mapeamento:
        - VARCHAR2 + constraintValues => select
        - VARCHAR2 + Y/N pattern => boolean
        - VARCHAR2 => text
        - NUMBER => number
        - DATE => date
        """
        
        if "VARCHAR2" in data_type:
            # Check for Y/N pattern
            if constraint_values and ("'Y'" in constraint_values and "'N'" in constraint_values):
                return "boolean"
            # Check for other constraint values
            if constraint_values and constraint_values.strip():
                return "select"
            return "text"
        
        elif "NUMBER" in data_type:
            return "number"
        
        elif "DATE" in data_type:
            return "date"
        
        return "text"
    
    @staticmethod
    def _parse_constraint(constraint_values: str, conditional: str, ui_type: str) -> Optional[dict]:
        """
        Parseia constraintValues e conditionalConstraint em estrutura dict.
        
        Exemplos:
        - "'Y','N'" => ["Y", "N"]
        - "PRIORITY BETWEEN 1 AND 999" => {type: "range", min: 1, max: 999}
        """
        
        if not constraint_values and not conditional:
            return None
        
        result = {}
        
        # Parse constraintValues (lista de opções)
        if constraint_values and constraint_values.strip():
            # Remove single quotes and split by comma
            options_str = constraint_values.replace("'", "").strip()
            if options_str:
                options = [opt.strip() for opt in options_str.split(",") if opt.strip()]
                if options:
                    result["options"] = options
        
        # Parse conditionalConstraint (ranges, custom rules)
        if conditional and conditional.strip():
            result["conditional"] = conditional
        
        return result if result else None
    
    @staticmethod
    def _infer_section(column_name: str) -> str:
        """
        Infere seção do formulário baseado em padrões de nome.
        Sem hardcode de colunas específicas.
        """
        
        upper_name = column_name.upper()
        
        # CORE: PK, XID, NAME
        if upper_name.endswith("_GID") or "_XID" in upper_name or upper_name.endswith("_NAME"):
            if not any(x in upper_name for x in ["LOCATION", "DATE", "TIME", "COST", "AMOUNT", "RATE", "PLAN", "SCHEDULE", "ATTRIBUTE", "INSERT_", "UPDATE_"]):
                return "CORE"
        
        # LOCALIZACAO
        if "LOCATION" in upper_name or "_LOC_" in upper_name:
            return "LOCALIZACAO"
        
        # DATAS
        if upper_name.endswith("_DATE") or "_TIME" in upper_name:
            return "DATAS"
        
        # FINANCEIRO
        if any(x in upper_name for x in ["_AMOUNT", "_COST", "_RATE"]):
            return "FINANCEIRO"
        
        # PLANEJAMENTO
        if "_PLAN_" in upper_name or "_SCHEDULE_" in upper_name:
            return "PLANEJAMENTO"
        
        # FLEXFIELDS
        if upper_name.startswith("ATTRIBUTE"):
            return "FLEXFIELDS"
        
        # TECNICO
        if upper_name.startswith("INSERT_") or upper_name.startswith("UPDATE_") or upper_name == "DOMAIN_NAME":
            return "TECNICO"
        
        # DEFAULT
        return "OUTROS"
    
    @staticmethod
    def _build_fk_map(schema: dict) -> dict:
        """
        Constrói mapa column_name => lookup info a partir de foreignKeys.
        """
        
        fk_map = {}
        fks = schema.get("foreignKeys", [])
        
        for fk in fks:
            parent_table = fk.get("parentTableName", "")
            relations = fk.get("columnRelation", [])
            
            for rel in relations:
                col_name = rel.get("columnName", "")
                parent_col = rel.get("parentColumnName", "")
                
                if col_name and parent_table and parent_col:
                    fk_map[col_name] = {
                        "table": parent_table,
                        "column": parent_col
                    }
        
        return fk_map
