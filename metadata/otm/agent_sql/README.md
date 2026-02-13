# OTM SQL Agent Pack

This folder is the GitHub-native package for ChatGPT Agent query support.
It is designed to keep JSON metadata as source of truth and provide smaller
artifacts optimized for retrieval.

## Folder structure

- `catalog/`: table schema records in JSONL (one table per line)
- `join_hints/`: curated join patterns and caveats
- `business_rules/`: SQL standards and domain constraints
- `examples/`: approved query patterns for common use cases
- `prompts/`: ready-to-use system prompt for SQL assistant behavior

## Build the schema catalog

Generate catalog from existing `metadata/otm/tables/*.json` files:

```bash
python3 scripts/build_agent_sql_catalog.py
```

Generate with all available tables:

```bash
python3 scripts/build_agent_sql_catalog.py \
  --mode all \
  --output metadata/otm/agent_sql/catalog/schema_catalog_all_tables.jsonl
```

## Why JSONL

- Stable and append-friendly
- Easy retrieval (one object per table)
- Better chunking behavior for large repositories
- Works well with Agent over GitHub connectors

## Recommended GitHub flow

1. Update table metadata in `metadata/otm/tables/`
2. Rebuild catalog JSONL
3. Update join hints and rules only when needed
4. Commit with clear message (what changed and why)
