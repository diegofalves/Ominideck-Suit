# OTM Object Cache

This directory stores local cache files generated from OTM extraction queries.

Rules:
- One JSON file per migration object.
- Extraction query comes from `technical_content.content`.
- `ROOT_NAME` is always the object `otm_table`.
- Rows are normalized by the canonical schema in `metadata/otm/tables/<TABLE>.json`.
- Every schema column is always present in each row.
- Missing values are persisted as empty string (`""`).

Current output path:
- `metadata/otm/cache/objects/*.json`

Examples:
```bash
# Atualizar todos os objetos do projeto
python3 infra/update_otm_object_cache.py --all-objects

# Atualizar todos os objetos de um grupo
python3 infra/update_otm_object_cache.py --group-id "PLANNING"

# Atualizar um objeto especifico
python3 infra/update_otm_object_cache.py --object-name "Itineraries"

# Objeto especifico com desambiguacao de grupo
python3 infra/update_otm_object_cache.py --object-name "Itineraries" --group-id "PLANNING"
```
