#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import re

from bs4 import BeautifulSoup
from typing import Optional


# Helper functions to generate governance files for Agent Pack v2
def write_sql_rules_file(base_dir: Path):
    rules_path = base_dir / "metadata/otm/agent_sql/catalog_output/sql_rules.md"
    rules_path.parent.mkdir(parents=True, exist_ok=True)
    rules_path.write_text(
        """
# Oracle OTM SQL Rules (Agent Pack v2)

## Join Style
- ALWAYS use implicit joins
- NEVER use explicit JOIN syntax

Correct:
SELECT a.col1,
       b.col2
  FROM table_a a,
       table_b b
 WHERE a.id = b.id

Forbidden:
SELECT * FROM table_a a JOIN table_b b ON a.id = b.id

## Safety Rules
- SELECT * is forbidden
- Always prefer bind variables (:domain, :gid, :xid)
- Always filter by DOMAIN_NAME when applicable
- Limit exploratory queries with FETCH FIRST 200 ROWS ONLY
""".strip(),
        encoding="utf-8",
    )


def write_system_prompt_file(base_dir: Path):
    prompt_path = base_dir / "metadata/otm/agent_sql/catalog_output/agent_behavior.md"
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(
        """
# OTM SQL Agent – GitHub Actions Governance

## Tool Priority
GitHub Actions are the ONLY source of structural truth.
Never confirm tables or columns without repository navigation.

## Evidence Gate
Every structural confirmation must include:
- Repo
- Path
- Branch
- SHA
- Real content snippet

If evidence is missing → answer FAIL.
""".strip(),
        encoding="utf-8",
    )


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


# ==============================
# OTM HELP ENRICHED INDEX BUILD
# ==============================

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s_]", "", text)
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"_+", "_", text)
    return text.strip("_")


def extract_text_from_html(html_path: Path) -> str:
    try:
        raw = html_path.read_text(encoding="utf-8", errors="ignore")
        soup = BeautifulSoup(raw, "html.parser")

        for tag in soup(["script", "style", "header", "footer", "nav", "aside"]):
            tag.decompose()

        text = soup.get_text(separator="\n")
        text = re.sub(r"\s+", " ", text)
        return text.strip()
    except Exception as e:
        print(f"[WARN] Failed to read HTML: {html_path} -> {e}")
        return ""


def compute_doc_metrics(text: str):
    char_count = len(text)
    word_count = len(text.split())
    estimated_tokens = int(word_count * 1.3)
    return char_count, word_count, estimated_tokens


def build_doc_id(topic: str, subtopic: str, title: str) -> str:
    version = subtopic.split("/")[-1] if subtopic else ""
    return f"{topic}_{version}_{slugify(title)}".strip("_")


def build_otm_help_enriched_index(base_dir: Path, locator_path_override: Optional[Path] = None):
    """Build an enriched index of OTM Help HTML pages for downstream ingestion (RAG).

    IMPORTANT: This function always writes the output JSON file. If the locator index is not found,
    it will write an empty index with a clear warning in the metadata.
    """

    output_path = base_dir / "metadata/otm/agent_sql/catalog_output/otm_help_enriched_index.json"

    # 1) Resolve locator index path
    locator_path: Path | None = None

    # Explicit override (highest priority)
    if locator_path_override is not None:
        if locator_path_override.exists():
            locator_path = locator_path_override
        else:
            print(f"[WARN] Locator override does not exist: {locator_path_override}")

    # Known canonical locations (next priority)
    if locator_path is None:
        canonical_candidates = [
            base_dir / "metadata/otm/book_locator_index.json",
            base_dir / "metadata/book_locator_index.json",
        ]
        for cand in canonical_candidates:
            if cand.exists():
                locator_path = cand
                break

    # Fallback: search anywhere under metadata/**
    if locator_path is None:
        locator_candidates = sorted((base_dir / "metadata").glob("**/book_locator_index.json"))
        if locator_candidates:
            locator_path = locator_candidates[0]

    # 2) If locator still missing, write an empty index and return
    if locator_path is None:
        print("[WARN] No book_locator_index.json found under metadata/**. Writing empty help index.")
        empty_output = {
            "metadata_type": "OTM_HELP_ENRICHED_INDEX",
            "version": "1.1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "locator_path": None,
            "warning": "Locator index not found; help ingestion skipped.",
            "total_documents": 0,
            "total_estimated_tokens": 0,
            "documents": [],
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(empty_output, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[INFO] Output file: {output_path}")
        return

    # 3) Normal path: load locator and process HTML
    try:
        locator = load_json(locator_path)
    except Exception as e:
        print(f"[ERROR] Failed to load locator index JSON: {locator_path} -> {e}")
        error_output = {
            "metadata_type": "OTM_HELP_ENRICHED_INDEX",
            "version": "1.1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "locator_path": str(locator_path).replace("\\", "/"),
            "warning": "Locator index could not be parsed; help ingestion skipped.",
            "error": str(e),
            "total_documents": 0,
            "total_estimated_tokens": 0,
            "documents": [],
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(error_output, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[INFO] Output file: {output_path}")
        return

    print(f"[INFO] Using locator index: {locator_path}")

    documents: list[dict] = []
    total_tokens = 0
    missing_files = 0

    # Support multiple possible locator JSON shapes
    if isinstance(locator, list):
        locator_items = locator
    elif isinstance(locator, dict):
        # The actual documents are the values of the 'by_url' dictionary
        # We add this check to the existing chain for robustness.
        by_url_values = list(locator.get("by_url", {}).values())
        locator_items = (
            by_url_values
            or locator.get("documents")
            or locator.get("items")
            or locator.get("pages")
            or locator.get("files")
            or []
        )
    else:
        locator_items = []

    processed_items = len(locator_items)
    print(f"[INFO] Locator items discovered: {processed_items}")

    for item in locator_items:
        html_rel_path = item.get("local_html_path", "")
        if not html_rel_path:
            continue

        # Primary attempt: path relative to repo root
        html_path = base_dir / html_rel_path

        # Secondary attempt: common Book OTM location (metadata/otm/book otm/25c/html/...)
        if not html_path.exists():
            html_path = base_dir / "metadata/otm/book otm/25c" / html_rel_path

        # Third attempt: search full relative path anywhere in repo
        if not html_path.exists():
            matches = list(base_dir.glob(f"**/{html_rel_path}"))
            if matches:
                html_path = matches[0]

        # Last attempt: search by filename (least precise but safe fallback)
        if not html_path.exists():
            matches = list(base_dir.glob(f"**/{Path(html_rel_path).name}"))
            if matches:
                html_path = matches[0]

        if not html_path.exists():
            missing_files += 1
            print(f"[WARN] Missing HTML file: {html_rel_path}")
            continue

        text = extract_text_from_html(html_path)
        if not text:
            print(f"[WARN] Empty text extracted from: {html_path}")
            continue

        char_count, word_count, token_est = compute_doc_metrics(text)
        total_tokens += token_est

        try:
            doc_id = build_doc_id(item.get("topic", "otm"), item.get("subtopic", ""), item.get("title", ""))
        except Exception:
            doc_id = slugify(f"{item.get('topic','otm')}_{item.get('subtopic','')}_{item.get('title','')}")

        doc = {
            "doc_id": doc_id,
            "title": item.get("title", ""),
            "topic": item.get("topic", ""),
            "subtopic": item.get("subtopic", ""),
            "source_url": item.get("url", ""),
            "local_html_path": html_rel_path,
            "resolved_html_path": str(html_path).replace("\\", "/"),
            "character_count": char_count,
            "word_count": word_count,
            "estimated_tokens": token_est,
            "size_kb": item.get("size_kb", 0),
            "content_preview": text[:500],
        }

        documents.append(doc)

    output = {
        "metadata_type": "OTM_HELP_ENRICHED_INDEX",
        "version": "1.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "locator_path": str(locator_path).replace("\\", "/"),
        "processed_locator_items": processed_items,
        "missing_html_files": missing_files,
        "total_documents": len(documents),
        "total_estimated_tokens": total_tokens,
        "documents": documents,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"[INFO] OTM Help documents processed: {len(documents)}")
    print(f"[INFO] Missing HTML files: {missing_files}")
    print(f"[INFO] Total estimated tokens: {total_tokens}")
    print(f"[INFO] Output file: {output_path}")


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
        default="metadata/otm/agent_sql/catalog_output/schema_catalog_eligible_tables.jsonl",
        help="Output JSONL file path.",
    )
    parser.add_argument(
        "--mode",
        choices=["eligible", "all"],
        default="eligible",
        help="eligible: only migration project eligible tables; all: all tables",
    )
    parser.add_argument(
        "--book-locator-file",
        default=None,
        help="Optional explicit path to book_locator_index.json (overrides auto-discovery).",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Resolve repository root reliably (works when script is executed from any directory)
    repo_root = Path(__file__).resolve().parents[1]
    print(f"[INFO] Repo root resolved to: {repo_root}")
    write_sql_rules_file(repo_root)
    write_system_prompt_file(repo_root)
    tables_dir = repo_root / args.tables_dir
    eligible_path = repo_root / args.eligible_file
    stats_path = repo_root / args.stats_file
    output_path = repo_root / args.output

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

    # Governance files for Agent Pack v2 generated automatically
    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": args.mode,
        "tables_generated": generated,
        "tables_skipped": skipped,
        "output_file": str(output_path),
    }

    # Build OTM Help enriched index for GPT ingestion
    locator_override = (repo_root / args.book_locator_file) if args.book_locator_file else None
    build_otm_help_enriched_index(repo_root, locator_path_override=locator_override)

    # Gerar README.md com instruções de navegação
    readme_path = repo_root / "metadata/otm/agent_sql/catalog_output/README.md"
    readme_content = """# OTM Knowledge Navigator – README\n\nEsta pasta contém todos os arquivos de índice essenciais para navegação, consulta e automação com Oracle OTM.\n\n## 📦 Localização\nTodos os arquivos estão em:\nmetadata/otm/agent_sql/catalog_output/\n\n## 🧠 Arquivos principais\n\n1. **sql_rules.md**\n   - Regras de governança SQL para OTM\n   - Define padrões de joins, filtros obrigatórios, segurança e boas práticas\n\n2. **agent_behavior.md**\n   - Orienta o comportamento do agente (GPT)\n   - Prioriza evidências do GitHub, disciplina técnica e rastreabilidade\n\n3. **schema_catalog_eligible_tables.jsonl**\n   - Catálogo completo das tabelas elegíveis\n   - Inclui colunas, tipos, chaves, joins, contagem por domínio e caminho do JSON fonte\n\n4. **otm_help_enriched_index.json**\n   - Índice navegável da documentação oficial OTM\n   - Tópicos, subtópicos, URLs, previews e métricas de conteúdo\n\n## 🚀 Como usar\n\n- Consulte o **schema_catalog_eligible_tables.jsonl** para navegar pelo banco, entender tabelas, gerar queries e relacionar entidades.\n- Use o **otm_help_enriched_index.json** para buscar tópicos, explicações e caminhos de leitura na documentação oficial.\n- Siga as regras e orientações de **sql_rules.md** e **agent_behavior.md** para garantir queries seguras e navegação disciplinada.\n\n## 💡 Exemplos de perguntas que podem ser respondidas\n- \"Em qual tabela fica o custo do shipment?\"\n- \"Como configurar Rate Offering?\"\n- \"Gere uma query para listar shipments por domínio.\"\n- \"Quais tabelas possuem DOMAIN_NAME?\"\n\n## 🧭 Para IA e humanos\nEste README serve como guia rápido para consultores, engenheiros, squads e para o próprio GPT, facilitando a integração e o uso dos índices.\n\n---\n\nQualquer dúvida, consulte os arquivos desta pasta ou navegue pelo catálogo e índice de documentação.\n"""
    readme_path.parent.mkdir(parents=True, exist_ok=True)
    readme_path.write_text(readme_content, encoding="utf-8")
    print(json.dumps(metadata, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
