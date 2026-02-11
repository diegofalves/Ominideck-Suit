# OTM Object Cache

This directory stores local cache files generated from OTM extraction queries.

Rules:
- One JSON file per `MIGRATION_ITEM`.
- Extraction query comes from `technical_content.content`.
- `ROOT_NAME` is always the `MIGRATION_ITEM` `otm_table`.
- Rows are normalized by the canonical schema in `metadata/otm/tables/<TABLE>.json`.
- Every schema column is always present in each row.
- Missing values are persisted as empty string (`""`).

Current output path:
- `metadata/otm/cache/objects/*.json`

Examples:
```bash
# Atualizar todos os MIGRATION_ITEMs do projeto
python3 infra/update_otm_object_cache.py --all-migration-items

# Atualizar todos os MIGRATION_ITEMs de um MIGRATION_GROUP
python3 infra/update_otm_object_cache.py --migration-group-id "PLANNING"

# Atualizar um MIGRATION_ITEM especifico
python3 infra/update_otm_object_cache.py --migration-item-name "Itineraries"

# MIGRATION_ITEM especifico com desambiguacao de MIGRATION_GROUP
python3 infra/update_otm_object_cache.py --migration-item-name "Itineraries" --migration-group-id "PLANNING"
```
