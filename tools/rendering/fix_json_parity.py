#!/usr/bin/env python3
"""
Script para garantir paridade total entre JSON e templates MD/HTML
Preenche os campos faltantes que são esperados pelos templates
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
JSON_FILE = Path(__file__).resolve().parents[2] / "domain" / "projeto_migracao" / "documento_migracao.json"

# Mapear objeto_type para tabela OTM padrão
OBJECT_TYPE_TO_TABLE = {
    "SAVED_QUERY": "SAVED_QUERY",
    "SAVED_CONDITION": "SAVED_CONDITION",
    "DATA_TYPE_ASSOCIATION": "DATA_TYPE_ASSOCIATION",
    "AGENT_EVENT": "AGENT_EVENT",
    "AGENT": "AGENT",
    "APP_ACTION": "APP_ACTION",
    "ACTION": "ACTION",
    "BATCH_PROCESS": "BATCH_PROCESS",
    "DOMAIN": "DOMAIN",
    "DOMAIN_GRANTS_MADE": "DOMAIN_GRANTS_MADE",
    "DOMAIN_SETTING": "DOMAIN_SETTING",
    "PROP_INSTRUCTION": "PROP_INSTRUCTION",
    "UOM": "UOM",
    "HNAME_COMPONENT": "HNAME_COMPONENT",
    "BRANDING": "BRANDING",
    "BN_RULE": "BN_RULE",
    "REPORT": "REPORT",
    "TRANSPORT_MODE": "TRANSPORT_MODE",
    "BN_NAMED_RANGE": "BN_NAMED_RANGE",
    "COMMODITY": "COMMODITY",
    "CORPORATION": "CORPORATION",
    "SHIP_UNIT_SPEC": "SHIP_UNIT_SPEC",
    "SERVPROV": "SERVPROV",
    "LOCATION": "LOCATION",
    "CONTACT": "CONTACT",
    "EQUIPMENT_GROUP": "EQUIPMENT_GROUP",
    "ITEM": "ITEM",
    "PACKAGED_ITEM": "PACKAGED_ITEM",
    "CONTACT_GROUP": "CONTACT_GROUP",
    "LOCATION_REFNUM_QUAL": "LOCATION_REFNUM_QUAL",
    "ORDER_RELEASE_REFNUM_QUAL": "ORDER_RELEASE_REFNUM_QUAL",
    "ORDER_RELEASE_LINE_REFNUM_QUAL": "ORDER_RELEASE_LINE_REFNUM_QUAL",
    "PACKAGED_ITEM_REFNUM_QUAL": "PACKAGED_ITEM_REFNUM_QUAL",
    "ITEM_REFNUM_QUAL": "ITEM_REFNUM_QUAL",
    "SHIPMENT_REFNUM_QUAL": "SHIPMENT_REFNUM_QUAL",
    "SHIPMENT_STOP_REFNUM_QUAL": "SHIPMENT_STOP_REFNUM_QUAL",
    "RATE_GEO_REFNUM_QUAL": "RATE_GEO_REFNUM_QUAL",
    "ORDER_MOVEMENT_REFNUM_QUAL": "ORDER_MOVEMENT_REFNUM_QUAL",
    "STATUS_TYPES": "STATUS_TYPES",
    "REMARKS_QUALIFIER": "REMARKS_QUALIFIER",
    "AUDIT_TRAIL": "AUDIT_TRAIL",
    "LOGIC_CONFIG": "LOGIC_CONFIG",
    "PARAMETER_SET": "PARAMETER_SET",
    "ACCESSORIAL_CODE": "ACCESSORIAL_CODE",
    "ITINERARY_LEG": "ITINERARY_LEG",
    "ITINERARY": "ITINERARY",
    "ITINERARY_PROFILE": "ITINERARY_PROFILE",
    "LOAD_CONFIG_RULE": "LOAD_CONFIG_RULE",
    "LOAD_CONFIG_SETUP": "LOAD_CONFIG_SETUP",
    "ORDER_RELEASE_TYPE": "ORDER_RELEASE_TYPE",
    "STYLESHEET_CONTENT": "STYLESHEET_CONTENT",
    "STYLESHEET_PROFILE": "STYLESHEET_PROFILE",
    "XML_TEMPLATE": "XML_TEMPLATE",
    "OUT_XML_PROFILE": "OUT_XML_PROFILE",
    "DOCUMENT": "DOCUMENT",
    "WEBSERVICE": "WEBSERVICE",
    "EXTERNAL_SYSTEM": "EXTERNAL_SYSTEM",
    "EXTERNAL_SYSTEM_CONTACT": "EXTERNAL_SYSTEM_CONTACT",
    "MANAGER_LAYOUT": "MANAGER_LAYOUT",
    "FINDER_SET": "FINDER_SET",
    "WORKBENCH": "WORKBENCH",
    "BUSINESS_MONITOR": "BUSINESS_MONITOR",
    "ACL": "ACL",
    "USER_ROLE": "USER_ROLE",
    "USER_MENU": "USER_MENU",
    "USER_PREFERENCE": "USER_PREFERENCE",
    "TRANSLATION": "TRANSLATION",
    "USER_ACCESS": "USER_ACCESS",
    "VPD_PROFILE": "VPD_PROFILE",
    "BI_REPORT": "BI_REPORT",
}

def fill_missing_fields(data):
    """Preenche campos faltantes no JSON"""
    
    for group_idx, group in enumerate(data.get("groups", [])):
        for obj_idx, obj in enumerate(group.get("objects", [])):
            # 1. Preencher otm_table se vazio
            if not obj.get("otm_table"):
                object_type = obj.get("object_type", "")
                obj["otm_table"] = OBJECT_TYPE_TO_TABLE.get(object_type, object_type)
                print(f"✓ Grupo {group['label']} / Objeto {obj['name']}: OTM Table = {obj['otm_table']}")
            
            # 2. Garantir que identifiers existe e tem estrutura correta
            if "identifiers" not in obj:
                obj["identifiers"] = {}
            
            # 3. Garantir migration_type existe
            if "migration_type" not in obj:
                obj["migration_type"] = ""
            
            # 4. Garantir notes existe
            if "notes" not in obj:
                obj["notes"] = ""
            
            # 5. Garantir name existe
            if "name" not in obj:
                obj["name"] = ""
            
            # 6. Garantir description existe
            if "description" not in obj:
                obj["description"] = ""
            
            # 7. Preencher otm_primary_key com a chave primária da tabela equivalente
            otm_table = obj.get("otm_table", "")
            if otm_table:
                tables_dir = Path(__file__).resolve().parents[2] / "metadata" / "otm" / "tables"
                # Busca case-insensitive
                metadata_file = None
                for file in tables_dir.iterdir():
                    if file.is_file() and file.stem.lower() == otm_table.lower():
                        metadata_file = file
                        break
                if metadata_file:
                    try:
                        with open(metadata_file, "r", encoding="utf-8") as meta_file:
                            meta_json = json.load(meta_file)
                        primary_key = meta_json.get("primaryKey", [])
                        obj["otm_primary_key"] = [pk["columnName"] for pk in primary_key if "columnName" in pk]
                        print(f"✓ Grupo {group['label']} / Objeto {obj['name']}: OTM Primary Key preenchida: {obj['otm_primary_key']}")
                    except Exception as e:
                        obj["otm_primary_key"] = []
                        print(f"⚠️ Erro ao ler chave primária de {otm_table}: {e}")
                else:
                    obj["otm_primary_key"] = []
                    print(f"⚠️ Metadata não encontrada para tabela {otm_table}")
    
    return data

def main():
    print("=" * 60)
    print("Preenchendo campos faltantes no JSON...")
    print("=" * 60)
    
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    data = fill_missing_fields(data)
    
    # Fazer backup
    backup_file = JSON_FILE.with_suffix(".json.backup")
    import shutil
    shutil.copy(JSON_FILE, backup_file)
    print(f"\n✓ Backup criado: {backup_file}")
    
    # Salvar JSON atualizado
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ JSON atualizado: {JSON_FILE}")
    print("=" * 60)
    print("✓ Campos faltantes preenchidos com sucesso!")
    print("=" * 60)

if __name__ == "__main__":
    main()
