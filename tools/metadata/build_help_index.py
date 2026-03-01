# otm_builder/help/scripts/build_help_index.py
import os
import re
import json
from datetime import datetime
from bs4 import BeautifulSoup

# Pastas base do módulo help/
HELP_BASE = os.path.dirname(os.path.dirname(__file__))

BASE_DIR = os.path.join(HELP_BASE, "base")               # Base folder (if needed)
CONVERTED_DIR = os.path.join(HELP_BASE, "convertido")   # Markdown convertido consolidado
MARKDOWN_DIR = os.path.join(HELP_BASE, "markdown")      # Nova pasta markdown para buscar arquivos
META_DIR = os.path.join(HELP_BASE, "meta")              # help_files_list.json
INDEX_DIR = os.path.join(HELP_BASE, "index")            # help_index.json (saída)

HELP_LIST_JSON = os.path.join(META_DIR, "help_files_list.json")
OUTPUT_INDEX = os.path.join(INDEX_DIR, "help_index.json")

# Utilidades
def slugify(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:120] or "item"

def read_file_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def extract_md_meta(path: str):
    """Extrai 'título' (primeiro #), cabeçalhos e texto plano de um Markdown."""
    content = read_file_text(path)

    # Título = primeira linha que comece com '#'
    title = ""
    headings = []
    for line in content.splitlines():
        m = re.match(r"^(#{1,6})\s+(.*)", line.strip())
        if m:
            level = f"h{len(m.group(1))}"
            text = m.group(2).strip()
            headings.append({"level": level, "text": text})
            if not title and level == "h1":
                title = text
    # Se não achou h1, usa a primeira heading que aparecer
    if not title and headings:
        title = headings[0]["text"]

    # Texto “plano” simplificado (remove marcações básicas)
    plain = re.sub(r"`{1,3}.*?`{1,3}", " ", content, flags=re.S)           # code inline
    plain = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", plain)                     # imagens
    plain = re.sub(r"\[[^\]]*\]\([^)]+\)", " ", plain)                      # links
    plain = re.sub(r"[#*_>\-]{1,}", " ", plain)                             # marcadores
    plain = re.sub(r"\s+", " ", plain).strip()

    return title, headings, plain

def load_help_map():
    """Carrega help_files_list.json (se existir) para mapear relative_path→{url,title}."""
    if not os.path.exists(HELP_LIST_JSON):
        return {}
    try:
        data = json.load(open(HELP_LIST_JSON, "r", encoding="utf-8"))
        m = {}
        for item in data:
            rel = item.get("relative_path") or ""
            if rel:
                m[rel] = {"url": item.get("url"), "title": item.get("title")}
        return m
    except Exception:
        return {}

def relative_from_help(path_abs: str):
    """Retorna o caminho relativo a partir de HELP_BASE (para registrar no índice)."""
    try:
        return os.path.relpath(path_abs, HELP_BASE)
    except Exception:
        return os.path.basename(path_abs)

def build_index():
    os.makedirs(INDEX_DIR, exist_ok=True)

    help_map = load_help_map()  # {relative_path: {url,title}}
    items = []

    now = datetime.now().isoformat()

    # Pastas para buscar arquivos .md
    search_dirs = [CONVERTED_DIR, MARKDOWN_DIR]
    total_files_indexed = 0
    for base_dir in search_dirs:
        if not os.path.isdir(base_dir):
            continue
        count_files = 0
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.lower().endswith(".md"):
                    abs_path = os.path.join(root, file)
                    rel_path = relative_from_help(abs_path)

                    title, headings, text_content = extract_md_meta(abs_path)
                    size_bytes = os.path.getsize(abs_path)

                    effective_title = title or os.path.splitext(os.path.basename(abs_path))[0]
                    summary = (text_content[:600] + "…") if len(text_content) > 600 else text_content

                    items.append({
                        "id": slugify(f"{effective_title}-{os.path.basename(abs_path)}"),
                        "source": "md",
                        "path": rel_path,
                        "url": None,
                        "title": effective_title,
                        "headings": headings,
                        "summary": summary,
                        "size_bytes": size_bytes,
                        "updated": now,
                    })
                    count_files += 1
        print(f"📄 Indexados {count_files} arquivos Markdown na pasta: {base_dir}")
        total_files_indexed += count_files

    # Ordenar por título para ter estabilidade
    items.sort(key=lambda x: (x["title"] or "").lower())

    # Montar metadados resumidos
    metadata = {
        "generated_at": now,
        "total_topics": total_files_indexed,
    }

    output_data = {
        "metadata": metadata,
        "items": items,
    }

    with open(OUTPUT_INDEX, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Índice do Oracle OTM Help gerado com sucesso!")
    print(f"📄 Caminho do arquivo: {OUTPUT_INDEX}")
    print(f"📊 Total de tópicos indexados: {total_files_indexed}")

if __name__ == "__main__":
    print("🚀 Construindo índice consolidado do Oracle OTM Help…")
    build_index()