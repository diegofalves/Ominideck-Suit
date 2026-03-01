import os
import json
import requests
from tqdm import tqdm
from datetime import datetime

USER_AGENT = "OTM-Builder-HelpDownloader/1.0 (+https://docs.oracle.com)"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT})

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
INPUT_JSON = os.path.join(BASE_DIR, "meta", "help_files_list.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "base")
LOG_FILE = os.path.join(BASE_DIR, "meta", "help_download_log.txt")
MANIFEST_FILE = os.path.join(BASE_DIR, "meta", "help_download_manifest.json")

def download_file(url, relative_path):
    """Faz o download e salva o HTML na estrutura local."""
    local_path = os.path.join(OUTPUT_DIR, relative_path)
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    try:
        resp = SESSION.get(url, timeout=15)
        if resp.status_code == 200:
            with open(local_path, "w", encoding="utf-8") as f:
                f.write(resp.text)
            return {"status": "OK", "size_kb": len(resp.content) // 1024}
        else:
            return {"status": f"HTTP {resp.status_code}", "size_kb": 0}
    except Exception as e:
        return {"status": f"ERROR: {e}", "size_kb": 0}

def main():
    print("🚀 Iniciando download dos arquivos do Oracle OTM Help...")
    
    if not os.path.exists(INPUT_JSON):
        print(f"❌ Arquivo não encontrado: {INPUT_JSON}")
        return

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        pages = json.load(f)

    start_ts = datetime.now().isoformat()
    results = []
    with open(LOG_FILE, "w", encoding="utf-8") as log:
        log.write(f"[INICIO] {start_ts} - total previsto: {len(pages)}\n")
        log.flush()
        for page in tqdm(pages, desc="Baixando páginas"):
            url = page["url"]
            relative_path = page["relative_path"]
            result = download_file(url, relative_path)
            results.append({
                "url": url,
                "relative_path": relative_path,
                "status": result["status"],
                "size_kb": result["size_kb"]
            })
            log.write(f"{url} → {result['status']} ({result['size_kb']} KB)\n")
            log.flush()

    total = len(results)
    success = len([r for r in results if r["status"] == "OK"])
    errors = [r for r in results if r["status"] != "OK"]
    end_ts = datetime.now().isoformat()

    manifest = {
        "total": total,
        "baixados_com_sucesso": success,
        "falhas": total - success,
        "data_execucao_inicio": start_ts,
        "data_execucao_fim": end_ts,
        "saida": OUTPUT_DIR,
        "user_agent": USER_AGENT,
        "erros": errors[:20]  # amostra para rastreabilidade rápida
    }

    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"✅ Download concluído: {success}/{total} páginas baixadas.")
    print(f"📄 Log: {LOG_FILE}")
    print(f"📘 Manifesto: {MANIFEST_FILE}")

if __name__ == "__main__":
    main()
