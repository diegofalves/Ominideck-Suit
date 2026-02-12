import os
import json
from datetime import datetime
from pathlib import Path
import shutil
from bs4 import BeautifulSoup  # pyright: ignore[reportMissingImports]
from tqdm import tqdm  # pyright: ignore[reportMissingModuleSource]

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "base")
OUTPUT_MD = os.path.join(BASE_DIR, "markdown")
OUTPUT_JSON = os.path.join(BASE_DIR, "json")
LOG_FILE = os.path.join(BASE_DIR, "meta", "help_convert_log.txt")
MANIFEST_FILE = os.path.join(BASE_DIR, "meta", "help_convert_manifest.json")
FIXOS_DIR = Path(__file__).resolve().parents[2] / "01 - master_data" / "02 - dados_fixos"
CONSOLIDATED_DIR = str(FIXOS_DIR)
CONSOLIDATED_PATH = os.path.join(CONSOLIDATED_DIR, "help_completo.md")
CONSOLIDATED_INDEX = os.path.join(CONSOLIDATED_DIR, "help_consolidated_index.json")

def html_to_text(html):
    """Extrai texto e estrutura básica do HTML."""
    soup = BeautifulSoup(html, "lxml")

    # Remove scripts e estilos
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title else "(Sem título)"
    headings = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3"])]
    body_text = "\n".join([p.get_text(" ", strip=True) for p in soup.find_all(["p", "li", "td"])])

    return title, headings, body_text

def convert_html_file(file_path, rel_path):
    """Converte HTML em Markdown e JSON."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    title, headings, text = html_to_text(html)
    markdown = f"# {title}\n\n"
    for h in headings:
        markdown += f"## {h}\n"
    markdown += f"\n{text}\n"

    # Caminhos de saída
    md_path = os.path.join(OUTPUT_MD, rel_path.replace(".htm", ".md").replace(".html", ".md"))
    json_path = os.path.join(OUTPUT_JSON, rel_path.replace(".htm", ".json").replace(".html", ".json"))

    os.makedirs(os.path.dirname(md_path), exist_ok=True)
    os.makedirs(os.path.dirname(json_path), exist_ok=True)

    # Grava os arquivos
    with open(md_path, "w", encoding="utf-8") as f_md:
        f_md.write(markdown)

    json_data = {
        "title": title,
        "path": rel_path,
        "headings": headings,
        "content": text,
        "tokens": len(text.split()),
        "timestamp": datetime.now().isoformat()
    }

    with open(json_path, "w", encoding="utf-8") as f_json:
        json.dump(json_data, f_json, indent=2, ensure_ascii=False)

def main():
    print("⚙️ Iniciando conversão dos HTMLs para Markdown e JSON...")
    start_ts = datetime.now().isoformat()
    total = 0
    errors = []

    with open(LOG_FILE, "w", encoding="utf-8") as log:
        log.write(f"[INICIO] {start_ts}\n")
        log.flush()
        for root, _, files in os.walk(INPUT_DIR):
            for file in tqdm(files, desc="Convertendo"):
                if not file.endswith((".htm", ".html")):
                    continue
                rel_path = os.path.relpath(os.path.join(root, file), INPUT_DIR)
                try:
                    convert_html_file(os.path.join(root, file), rel_path)
                    log.write(f"[OK] {rel_path}\n")
                    total += 1
                except Exception as e:
                    log.write(f"[ERRO] {rel_path} - {e}\n")
                    errors.append({"path": rel_path, "erro": str(e)})
                log.flush()

    manifest = {
        "total_convertidos": total,
        "data_execucao_inicio": start_ts,
        "data_execucao_fim": datetime.now().isoformat(),
        "saida_md": OUTPUT_MD,
        "saida_json": OUTPUT_JSON,
        "erros": errors[:20]  # amostra para rastreabilidade
    }

    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    # Nova etapa: Consolidação dos arquivos Markdown
    os.makedirs(CONSOLIDATED_DIR, exist_ok=True)

    md_files = []
    for root, _, files in os.walk(OUTPUT_MD):
        for file in files:
            if file.endswith(".md"):
                full_path = os.path.join(root, file)
                rel_md_path = os.path.relpath(full_path, OUTPUT_MD)
                md_files.append((full_path, rel_md_path))

    consolidated_index = []
    current_line = 1
    with open(CONSOLIDATED_PATH, "w", encoding="utf-8") as consolidated_file:
        for full_path, rel_md_path in md_files:
            if not os.path.exists(full_path):
                errors.append({"path": rel_md_path, "erro": "arquivo markdown ausente na consolidação"})
                continue
            with open(full_path, "r", encoding="utf-8") as f_md:
                content = f_md.read()
            # Extrai o título do conteúdo markdown (primeira linha que começa com # )
            first_line = content.splitlines()[0] if content else "(Sem conteúdo)"
            title_line = first_line if first_line.startswith("#") else "(Sem título)"
            # Escreve cabeçalho com caminho relativo e título
            header = f"\n\n---\n\n**Arquivo:** `{rel_md_path}`\n\n**Título:** {title_line}\n\n"
            consolidated_file.write(header)
            consolidated_file.write(content)
            consolidated_file.write("\n")
            lines_added = header.count("\n") + content.count("\n") + 1
            consolidated_index.append({
                "path": rel_md_path,
                "title": title_line.lstrip("# ").strip(),
                "start_line": current_line,
                "end_line": current_line + lines_added - 1
            })
            current_line += lines_added

    # Atualiza o manifesto com dados da consolidação
    manifest["consolidado"] = {
        "arquivo": CONSOLIDATED_PATH,
        "total_arquivos_consolidados": len(md_files),
        "index": CONSOLIDATED_INDEX
    }

    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    # Índice separado para acesso rápido ao consolidado
    with open(CONSOLIDATED_INDEX, "w", encoding="utf-8") as f:
        json.dump(consolidated_index, f, indent=2, ensure_ascii=False)

    # Limpeza: remove temporários (HTMLs, Markdown e JSON individuais) mantendo apenas consolidados e manifestos
    cleanup_targets = [INPUT_DIR, OUTPUT_MD, OUTPUT_JSON]
    cleaned = []
    for target in cleanup_targets:
        if os.path.exists(target):
            shutil.rmtree(target, ignore_errors=True)
            cleaned.append(target)
    manifest["limpeza"] = {"removidos": cleaned}
    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"✅ Conversão concluída. Total: {total}")
    print(f"📘 Manifesto: {MANIFEST_FILE}")
    print(f"📄 Arquivo consolidado criado em: {CONSOLIDATED_PATH}")
    print(f"🧭 Índice consolidado: {CONSOLIDATED_INDEX}")
    if cleaned:
        print(f"🧹 Limpeza concluída (removidos): {', '.join(cleaned)}")

if __name__ == "__main__":
    main()
