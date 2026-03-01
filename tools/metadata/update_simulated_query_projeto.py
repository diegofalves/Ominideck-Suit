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


# Carrega o JSON
with PROJETO_PATH.open("r", encoding="utf-8") as f:
    projeto = json.load(f)

# Atualiza/inclui o campo simulatedExtractionQuery para todos os objetos com query válida
alterados = 0
for grupo in projeto.get("groups", []):
    for obj in grupo.get("objects", []):
        query_original = obj.get("object_extraction_query", {}).get("content", "")
        if query_original:
            query_normalizada = _normalize_sql_table_aliases(query_original)
            if obj.get("simulatedExtractionQuery") != query_normalizada:
                obj["simulatedExtractionQuery"] = query_normalizada
                alterados += 1

if alterados > 0:
    with PROJETO_PATH.open("w", encoding="utf-8") as f:
        json.dump(projeto, f, ensure_ascii=False, indent=2)
    print(f"Campo simulatedExtractionQuery atualizado/inserido em {alterados} objeto(s).")
else:
    print("Nenhum objeto elegível encontrado para atualização.")
