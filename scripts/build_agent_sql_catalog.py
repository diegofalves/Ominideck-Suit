#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_domain_stats_map(stats_path: Path):
    stats = load_json(stats_path)
    table_map = {}
    for item in stats.get("tables", []):
        table_name = (item.get("tableName") or "").upper()
        if not table_name:
            continue
        table_map[table_name] = item.get("parsedCounts", {}) or {}
    return table_map


def load_eligible_table_names(eligible_path: Path):
    eligible = load_json(eligible_path)
    return {
        (entry.get("tableName") or "").upper()
        for entry in eligible.get("tables", [])
        if entry.get("tableName")
    }


def infer_primary_key_candidates(table_name: str, columns):
    names = {col["name"] for col in columns}
    table_upper = table_name.upper()
    candidates = []
    for suffix in ("_GID", "_ID"):
        direct_name = f"{table_upper}{suffix}"
        if direct_name in names:
            candidates.append(direct_name)
    if not candidates:
        for col in columns:
            name = col["name"]
            if name.endswith("_GID") and name.startswith(table_upper[:8]):
                candidates.append(name)
    return candidates[:5]


def extract_columns(raw_columns):
    columns = []
    for col in raw_columns:
        columns.append(
            {
                "name": col.get("name"),
                "type": col.get("dataType"),
                "size": col.get("size"),
                "nullable": bool(col.get("isNull")),
                "default": col.get("defaultValue") or None,
                "description": col.get("description") or "",
            }
        )
    return columns


def build_record(table_json: dict, source_path: Path, domain_counts: dict):
    table_data = table_json.get("table", {})
    table_name = (table_data.get("name") or "").upper()
    schema_name = (table_data.get("schema") or "").upper()
    description = table_data.get("description") or ""

    columns = extract_columns(table_json.get("columns", []))
    join_key_candidates = [
        col["name"]
        for col in columns
        if col["name"] and col["name"].endswith(("_GID", "_ID", "_XID"))
    ][:40]
    required_columns = [col["name"] for col in columns if col["name"] and not col["nullable"]][:40]

    return {
        "table": table_name,
        "schema": schema_name,
        "description": description,
        "column_count": len(columns),
        "primary_key_candidates": infer_primary_key_candidates(table_name, columns),
        "required_columns": required_columns,
        "join_key_candidates": join_key_candidates,
        "domain_counts": domain_counts or {},
        "source_file": str(source_path).replace("\\", "/"),
        "columns": columns,
    }


def parse_args():
    parser = argparse.ArgumentParser(
        description="Build JSONL catalog for SQL agent consumption from OTM table metadata."
    )
    parser.add_argument(
        "--tables-dir",
        default="metadata/otm/tables",
        help="Directory with table JSON files.",
    )
    parser.add_argument(
        "--eligible-file",
        default="metadata/otm/migration_project_eligible_tables.json",
        help="File with eligible migration tables.",
    )
    parser.add_argument(
        "--stats-file",
        default="metadata/otm/domain_table_statistics.json",
        help="File with domain statistics by table.",
    )
    parser.add_argument(
        "--output",
        default="metadata/otm/agent_sql/catalog/schema_catalog_eligible_tables.jsonl",
        help="Output JSONL file path.",
    )
    parser.add_argument(
        "--mode",
        choices=["eligible", "all"],
        default="eligible",
        help="eligible: only migration project eligible tables; all: all tables",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    tables_dir = Path(args.tables_dir)
    eligible_path = Path(args.eligible_file)
    stats_path = Path(args.stats_file)
    output_path = Path(args.output)

    domain_stats_map = build_domain_stats_map(stats_path) if stats_path.exists() else {}
    eligible_tables = load_eligible_table_names(eligible_path) if eligible_path.exists() else set()

    table_files = sorted(
        [
            path
            for path in tables_dir.glob("*.json")
            if path.name.lower() != "index.json"
        ]
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    generated = 0
    skipped = 0

    with output_path.open("w", encoding="utf-8") as out:
        for path in table_files:
            table_json = load_json(path)
            table_name = (table_json.get("table", {}).get("name") or "").upper()
            if not table_name:
                skipped += 1
                continue

            if args.mode == "eligible" and table_name not in eligible_tables:
                skipped += 1
                continue

            record = build_record(
                table_json=table_json,
                source_path=path,
                domain_counts=domain_stats_map.get(table_name, {}),
            )
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            generated += 1

    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": args.mode,
        "tables_generated": generated,
        "tables_skipped": skipped,
        "output_file": str(output_path),
    }
    print(json.dumps(metadata, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
