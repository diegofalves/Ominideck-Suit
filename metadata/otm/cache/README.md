# OTM Object Cache

This directory stores local cache files generated from OTM extraction queries.

Canonical extraction runbook:
- `docs/otm_extraction_runbook.md`

Rules:
- One JSON file per `MIGRATION_ITEM`.
- Extraction query comes from `object_extraction_query.content`.
- `technical_content` remains available in the project model for non-extraction technical notes.
- `ROOT_NAME` is always the `MIGRATION_ITEM` `otm_table`.
- Additional cache sections run only for related tables explicitly marked in `otm_subtables`.
- Queries run only for `MIGRATION_ITEM`s with valid domain (`domainName`/`domain`).
- The same OTM table can exist in multiple `MIGRATION_ITEM`s and in multiple domains.
- The same OTM object must not exist in caches of different `MIGRATION_ITEM`s (validation by PK/GID/XID when available).
- Rows are normalized by the canonical schema in `metadata/otm/tables/<TABLE>.json`.
- Every schema column is always present in each row.
- Missing values are persisted as empty string (`""`).

Current output path:
- `metadata/otm/cache/objects/*.json`
- `metadata/otm/cache/objects_index.json` (index global para localizar objetos por chave)

File naming:
- Compact pattern: `<DOMAIN>_<TABLE>_<MIGRATION_ITEM_NAME_SHORT>_<SEQUENCE>_<MIGRATION_GROUP_SHORT>.json`
- Older long filenames for the same `migrationItemId` are automatically removed on refresh.

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
