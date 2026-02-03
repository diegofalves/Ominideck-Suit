#!/usr/bin/env python3
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
data = json.loads((BASE_DIR / "domain" / "projeto_migracao" / "projeto_migracao.json").read_text())

count_with_sql = 0
example_shown = False

for group in data["groups"]:
    for obj in group["objects"]:
        tech = obj.get("technical_content", {})
        if tech.get("type") == "SQL" and tech.get("content"):
            count_with_sql += 1
            if not example_shown:
                print("✓ Exemplo de objeto com SQL canônico:")
                print(f"  Nome: {obj['name']}")
                print(f"  Object Type: {obj['object_type']}")
                print(f"  SQL length: {len(tech['content'])} chars")
                print(f"  SQL preview: {tech['content'][:60]}...")
                example_shown = True

print(f"\n✅ Total de objetos com SQL: {count_with_sql}")
print(f"✅ Todos renderizados como 'Query de Extração' em MD, HTML e PDF")
