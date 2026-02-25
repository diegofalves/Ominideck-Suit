import json
import re
from pathlib import Path

def _normalize_sql_table_aliases(sql_query: str) -> str:
    """
    Substitui aliases customizados na query SQL por aliases padronizados com o nome da tabela.
    Exemplo: 'SELECT t1.col FROM table1 t1' vira 'SELECT table1.col FROM table1 table1'.
    """
    if not isinstance(sql_query, str) or not sql_query.strip():
        return sql_query
    # Mapeia aliases para nomes de tabela
    alias_map = {}
    def alias_replacer(match):
        table = match.group("table")
        alias = match.group("alias")
        alias_map[alias] = table
        return f"{table} {table}"
    pattern = re.compile(r"(?i)(FROM|JOIN)\s+(?P<table>[A-Z0-9_.$\"#@]+)\s+(?P<alias>[A-Z0-9_]+)")
    sql_query = pattern.sub(alias_replacer, sql_query)

    # Substitui todas as referências de alias nos campos e joins
    for alias, table in alias_map.items():
        sql_query = re.sub(rf"\b{alias}\.", f"{table}.", sql_query)
    return sql_query

# Caminho do projeto_migracao.json
PROJETO_PATH = Path("domain/projeto_migracao/projeto_migracao.json")

# Nome do objeto alvo
OBJETO_NOME = "Saved Conditions"
# Query simulada (exemplo, pode ser substituída por lógica dinâmica)
QUERY_SIMULADA = "SELECT * FROM BAU_SAVED_CONDITION t1 JOIN BAU_OTHER_TABLE t2 ON t1.ID = t2.ID"

# Carrega o JSON
with PROJETO_PATH.open("r", encoding="utf-8") as f:
    projeto = json.load(f)

# Busca e atualiza/inclui o campo simulatedExtractionQuery
alterado = False
for grupo in projeto.get("groups", []):
    for obj in grupo.get("objects", []):
        nome = obj.get("name")
        if nome and nome.strip().lower() == OBJETO_NOME.strip().lower():
            # Busca a query original
            query_original = obj.get("object_extraction_query", {}).get("content", "")
            query_normalizada = _normalize_sql_table_aliases(query_original)
            obj["simulatedExtractionQuery"] = query_normalizada
            alterado = True

if alterado:
    with PROJETO_PATH.open("w", encoding="utf-8") as f:
        json.dump(projeto, f, ensure_ascii=False, indent=2)
    print(f"Campo simulatedExtractionQuery atualizado/inserido para '{OBJETO_NOME}'.")
else:
    print(f"Objeto '{OBJETO_NOME}' não encontrado.")
