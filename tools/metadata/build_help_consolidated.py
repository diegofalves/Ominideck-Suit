import os
import json
from datetime import datetime
from tqdm import tqdm

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
JSON_DIR = os.path.join(BASE_DIR, "json")
MD_DIR = os.path.join(BASE_DIR, "markdown")
META_DIR = os.path.join(BASE_DIR, "meta")

OUTPUT_JSON = os.path.join(META_DIR, "help_consolidated.json")
OUTPUT_MD = os.path.join(META_DIR, "help_consolidated.md")
MANIFEST_FILE = os.path.join(META_DIR, "help_manifest.json")

def consolidate_json():
    """Une todos os arquivos JSON individuais em um único JSON consolidado."""
    consolidated = []
    file_paths = []
    for root, _, files in os.walk(JSON_DIR):
        for file in files:
            if file.endswith(".json"):
                file_paths.append(os.path.join(root, file))
    file_paths.sort()  # Ordena alfabeticamente (por caminho relativo)
    for file_path in tqdm(file_paths, desc="Consolidando JSON"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            consolidated.append(data)
        except Exception as e:
            print(f"⚠️ Erro lendo {os.path.relpath(file_path, JSON_DIR)}: {e}")
    print(f"🔢 Total de arquivos JSON consolidados: {len(file_paths)} → {OUTPUT_JSON}")
    return consolidated

def consolidate_markdown():
    """Une todos os arquivos Markdown individuais em um único MD consolidado."""
    consolidated_md = f"# Oracle OTM Help Consolidado\n📘 Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
    file_paths = []
    for root, _, files in os.walk(MD_DIR):
        for file in files:
            if file.endswith(".md"):
                file_paths.append(os.path.join(root, file))
    file_paths.sort()  # Ordena alfabeticamente (por caminho relativo)
    total_files = 0
    for file_path in tqdm(file_paths, desc="Consolidando Markdown"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            rel_path = os.path.relpath(file_path, MD_DIR)
            consolidated_md += f"\n\n---\n\n## 📄 {rel_path}\n\n{content}\n"
            total_files += 1
        except Exception as e:
            print(f"⚠️ Erro lendo {os.path.relpath(file_path, MD_DIR)}: {e}")
    print(f"🔢 Total de arquivos Markdown consolidados: {total_files} → {OUTPUT_MD}")
    return consolidated_md, total_files

def main():
    print("🚀 Iniciando consolidação do Oracle OTM Help...")

    os.makedirs(META_DIR, exist_ok=True)

    # 1️⃣ Consolida JSON
    consolidated_json = consolidate_json()
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(consolidated_json, f, indent=2, ensure_ascii=False)

    # 2️⃣ Consolida Markdown
    consolidated_md, total_files = consolidate_markdown()
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(consolidated_md)

    # 3️⃣ Gera manifesto
    manifest = {
        "versao_otm": "25C",
        "data_geracao": datetime.now().isoformat(),
        "arquivos_md": total_files,
        "arquivos_json": len(consolidated_json),
        "saida_json": OUTPUT_JSON,
        "saida_md": OUTPUT_MD
    }
    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"✅ Consolidação concluída com sucesso!")
    print(f"📘 Markdown consolidado: {OUTPUT_MD}")
    print(f"📄 JSON consolidado: {OUTPUT_JSON}")
    print(f"📊 Manifesto: {MANIFEST_FILE}")

if __name__ == "__main__":
    main()