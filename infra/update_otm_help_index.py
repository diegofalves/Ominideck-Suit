import argparse
import csv
import json
import os
import re
import shutil
import sys
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse

import requests  # type: ignore
from bs4 import BeautifulSoup

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from infra.otm_query_executor import execute_otm_query


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
HELP_ROOT = os.path.join(BASE_DIR, "metadata", "otm", "help otm")
DOC_BASE_TEMPLATE = "https://docs.oracle.com/en/cloud/saas/transportation/{doc_version}/otmol/"
HTML_REF_PATTERN = re.compile(r"""['"]([^'"]+\.(?:htm|html)(?:#[^'"]*)?(?:\?[^'"]*)?)['"]""", re.IGNORECASE)


def _find_by_local_name(node: Dict[str, Any], local_name: str) -> Any:
    for key, value in node.items():
        if key.split("}")[-1] == local_name:
            return value
    return None


def _extract_transaction_rows(payload: Dict[str, Any], root_name: str) -> List[Dict[str, Any]]:
    xml2sql = _find_by_local_name(payload, "xml2sql")
    if not isinstance(xml2sql, dict):
        return []

    transaction_set = _find_by_local_name(xml2sql, "TRANSACTION_SET")
    if transaction_set is None or transaction_set == "NO DATA":
        return []
    if not isinstance(transaction_set, dict):
        return []

    rows = transaction_set.get(root_name)
    if rows is None:
        rows = _find_by_local_name(transaction_set, root_name)
    if rows is None:
        return []

    if isinstance(rows, list):
        source_rows = rows
    elif isinstance(rows, dict):
        source_rows = [rows]
    else:
        return []

    extracted: List[Dict[str, Any]] = []
    for row in source_rows:
        if not isinstance(row, dict):
            continue
        attrs = row.get("@attributes", {})
        if isinstance(attrs, dict):
            extracted.append(attrs)
        else:
            extracted.append({k: v for k, v in row.items() if isinstance(v, (str, int, float, bool))})
    return extracted


def _query_current_release_row() -> Dict[str, Any]:
    sql = """
    SELECT * FROM (
      SELECT
        OTM_RELEASE_XID,
        SORTABLE_VERSION,
        DESCRIPTION,
        DOMAIN_NAME
      FROM OTM_RELEASE
      ORDER BY SORTABLE_VERSION DESC
    )
    WHERE ROWNUM = 1
    """
    context = {
        "sql_param_name": "sqlQuery",
        "request_params": {"rootName": "OTM_RELEASE"},
        "timeout": 30,
    }
    result = execute_otm_query(sql, "SQL", context, "json")
    if result.get("status") != "success":
        raise RuntimeError(result.get("error_message") or "Falha ao consultar OTM_RELEASE.")
    payload = result.get("payload")
    if not isinstance(payload, dict):
        raise RuntimeError("Resposta OTM sem payload JSON.")
    rows = _extract_transaction_rows(payload, "OTM_RELEASE")
    if not rows:
        raise RuntimeError("Consulta OTM_RELEASE retornou vazio (NO DATA).")
    return rows[0]


def _release_row_to_doc_version(release_row: Dict[str, Any]) -> str:
    description = str(release_row.get("DESCRIPTION") or "").strip().upper()
    match_desc = re.search(r"\b(\d{2})([A-Z])\b", description)
    if match_desc:
        return f"{match_desc.group(1)}{match_desc.group(2).lower()}"

    release_xid = str(release_row.get("OTM_RELEASE_XID") or "").strip()
    match_xid = re.match(r"^(\d{2})\.(\d+)\.", release_xid)
    if not match_xid:
        raise RuntimeError(f"Nao foi possivel derivar doc version de OTM_RELEASE_XID={release_xid!r}.")

    year = match_xid.group(1)
    minor = int(match_xid.group(2))
    if minor <= 0 or minor > 26:
        raise RuntimeError(f"Minor release fora do intervalo esperado: {release_xid!r}.")
    letter = chr(ord("a") + minor - 1)
    return f"{year}{letter}"


def _clean_old_versions(help_root: str, current_version: str) -> List[str]:
    removed: List[str] = []
    if not os.path.isdir(help_root):
        return removed

    for entry in os.listdir(help_root):
        full_path = os.path.join(help_root, entry)
        if not os.path.isdir(full_path):
            continue
        if entry == current_version:
            continue
        shutil.rmtree(full_path, ignore_errors=True)
        removed.append(entry)
    return removed


def _canonicalize_doc_url(url: str) -> Optional[str]:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return None
    if "docs.oracle.com" not in parsed.netloc:
        return None
    if "/otmol/" not in parsed.path:
        return None

    clean = url.split("#")[0].split("?")[0].strip()
    if not clean:
        return None

    parsed_clean = urlparse(clean)
    normalized_url = f"{parsed_clean.scheme.lower()}://{parsed_clean.netloc.lower()}{parsed_clean.path}"
    if not normalized_url.endswith((".htm", ".html")):
        return None
    return normalized_url


def _extract_internal_links(base_url: str, html: str) -> Set[str]:
    soup = BeautifulSoup(html, "html.parser")
    links: Set[str] = set()

    href_sources = []
    for tag_name, attr_name in (
        ("a", "href"),
        ("link", "href"),
        ("frame", "src"),
        ("iframe", "src"),
        ("area", "href"),
    ):
        for tag in soup.find_all(tag_name):
            raw = (tag.get(attr_name) or "").strip()
            if raw:
                href_sources.append(raw)

    # Captura refs em meta refresh: <meta http-equiv="refresh" content="0; URL=...">
    for meta in soup.find_all("meta"):
        content = (meta.get("content") or "").strip()
        if not content:
            continue
        lower_content = content.lower()
        if "url=" in lower_content:
            raw = content[lower_content.index("url=") + 4 :].strip()
            if raw:
                href_sources.append(raw)

    # Captura refs em scripts (muitos tópicos são montados dinamicamente).
    for script in soup.find_all("script"):
        text = script.string or script.get_text() or ""
        if not text:
            continue
        for match in HTML_REF_PATTERN.findall(text):
            candidate = (match or "").strip()
            if candidate:
                href_sources.append(candidate)

    for href in href_sources:
        if href.startswith("#"):
            continue
        href_lower = href.lower()
        if href_lower.endswith((".pdf", ".png", ".jpg", ".jpeg", ".zip", ".css", ".js")):
            continue
        full_url = urljoin(base_url, href)
        normalized = _canonicalize_doc_url(full_url)
        if normalized:
            links.add(normalized)
    return links


def _get_page_title(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    return "(sem titulo)"


def _relative_path_from_url(url: str) -> str:
    parsed = urlparse(url)
    marker = "/otmol/"
    path = parsed.path
    idx = path.find(marker)
    if idx >= 0:
        rel = path[idx + len(marker) :]
    else:
        rel = path.lstrip("/")
    return rel or "index.html"


def _normalize_relative_path(relative_path: str) -> str:
    cleaned = relative_path.replace("\\", "/").strip().lstrip("/")
    normalized = os.path.normpath(cleaned)
    if normalized in {"", "."}:
        return "index.html"
    if normalized.startswith(".."):
        raise ValueError(f"Caminho relativo invalido: {relative_path!r}")
    return normalized.replace("\\", "/")


def _derive_topic_labels(relative_path: str) -> Tuple[str, str]:
    parts = [part for part in relative_path.split("/") if part]
    dir_parts = parts[:-1]
    if not dir_parts:
        return "_root", "_root"

    topic = dir_parts[0]
    subtopic = "/".join(dir_parts[:2]) if len(dir_parts) >= 2 else topic
    return topic, subtopic


def _load_existing_pages(output_json: str, version_dir: str) -> Dict[str, Dict[str, Any]]:
    if not os.path.exists(output_json):
        return {}
    try:
        with open(output_json, "r", encoding="utf-8") as file_json:
            rows = json.load(file_json)
    except Exception:
        return {}
    if not isinstance(rows, list):
        return {}

    existing: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        url = str(row.get("url") or "").strip()
        local_html_path = str(row.get("local_html_path") or "").strip()
        if not url or not local_html_path:
            continue
        html_abs = os.path.join(version_dir, local_html_path)
        if not os.path.isfile(html_abs):
            continue
        existing[url] = row
    return existing


def _write_html_snapshot(version_dir: str, relative_path: str, html: str) -> str:
    safe_relative = _normalize_relative_path(relative_path)
    local_path = os.path.join("html", safe_relative).replace("\\", "/")
    output_path = os.path.join(version_dir, local_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as html_file:
        html_file.write(html)
    return local_path


def _build_topics_index(found_pages: List[Dict[str, Any]]) -> Dict[str, Any]:
    topics: Dict[str, Dict[str, Any]] = {}
    for page in found_pages:
        topic = str(page.get("topic") or "_root")
        subtopic = str(page.get("subtopic") or topic)

        topic_entry = topics.setdefault(
            topic,
            {"topic": topic, "total_pages": 0, "subtopics": {}},
        )
        topic_entry["total_pages"] += 1

        subtopics = topic_entry["subtopics"]
        subtopic_entry = subtopics.setdefault(subtopic, {"subtopic": subtopic, "total_pages": 0})
        subtopic_entry["total_pages"] += 1

    topic_rows: List[Dict[str, Any]] = []
    for topic in sorted(topics.keys()):
        topic_entry = topics[topic]
        subtopic_rows = sorted(
            topic_entry["subtopics"].values(),
            key=lambda row: (0 if row["subtopic"] == topic else 1, row["subtopic"]),
        )
        topic_rows.append(
            {
                "topic": topic,
                "total_pages": topic_entry["total_pages"],
                "subtopics": subtopic_rows,
            }
        )

    return {
        "generated_at": datetime.now().isoformat(),
        "total_pages": len(found_pages),
        "total_topics": len(topic_rows),
        "topics": topic_rows,
    }


def _build_help_locator_index(found_pages: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_url: Dict[str, Dict[str, Any]] = {}
    by_relative_path: Dict[str, Dict[str, Any]] = {}
    by_topic: Dict[str, Dict[str, Any]] = {}

    for page in found_pages:
        url = str(page.get("url") or "").strip()
        relative_path = str(page.get("relative_path") or "").strip()
        local_html_path = str(page.get("local_html_path") or "").strip()
        topic = str(page.get("topic") or "_root")
        subtopic = str(page.get("subtopic") or topic)
        title = str(page.get("title") or "").strip()

        base_entry = {
            "url": url,
            "relative_path": relative_path,
            "local_html_path": local_html_path,
            "topic": topic,
            "subtopic": subtopic,
            "title": title,
            "size_kb": page.get("size_kb"),
            "status": page.get("status"),
            "timestamp": page.get("timestamp"),
        }

        if url:
            by_url[url] = base_entry
        if relative_path:
            by_relative_path[relative_path] = base_entry

        topic_entry = by_topic.setdefault(
            topic,
            {"total_pages": 0, "subtopics": {}},
        )
        topic_entry["total_pages"] += 1
        subtopic_entry = topic_entry["subtopics"].setdefault(
            subtopic,
            {"total_pages": 0, "relative_paths": []},
        )
        subtopic_entry["total_pages"] += 1
        if relative_path:
            subtopic_entry["relative_paths"].append(relative_path)

    # Ordena listas para estabilidade de diff.
    for topic_entry in by_topic.values():
        for subtopic_entry in topic_entry["subtopics"].values():
            subtopic_entry["relative_paths"] = sorted(
                set(subtopic_entry.get("relative_paths", []))
            )

    return {
        "index_type": "OTM_HELP_LOCATOR_INDEX",
        "version": "1.0",
        "generated_at": datetime.now().isoformat(),
        "total_pages": len(found_pages),
        "total_topics": len(by_topic),
        "by_url": by_url,
        "by_relative_path": by_relative_path,
        "by_topic": by_topic,
    }


def _crawl_help_docs(
    start_urls: Iterable[str],
    log_file: str,
    max_pages: Optional[int],
    version_dir: str,
    use_incremental_cache: bool,
    existing_pages_by_url: Dict[str, Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    queue: List[str] = []
    queued: Set[str] = set()

    for raw_url in start_urls:
        normalized = _canonicalize_doc_url(str(raw_url).strip())
        if not normalized or normalized in queued:
            continue
        queue.append(normalized)
        queued.add(normalized)

    visited: Set[str] = set()
    found_pages: List[Dict[str, Any]] = []
    download_errors: List[Dict[str, Any]] = []
    session = requests.Session()
    session.headers.update({"User-Agent": "OTM-Builder-HelpScanner/2.0"})

    with open(log_file, "w", encoding="utf-8") as log:
        log.write(f"[START] {datetime.now().isoformat()} seeds={len(queue)}\n")
        for seed in queue:
            log.write(f"[SEED] {seed}\n")
        log.flush()

        while queue:
            if max_pages is not None and len(found_pages) >= max_pages:
                break

            url = queue.pop(0)
            queued.discard(url)
            if url in visited:
                continue
            visited.add(url)

            if use_incremental_cache:
                cached = existing_pages_by_url.get(url)
                if isinstance(cached, dict):
                    cached_local = str(cached.get("local_html_path") or "").strip()
                    cached_abs = os.path.join(version_dir, cached_local)
                    if cached_local and os.path.isfile(cached_abs):
                        try:
                            with open(cached_abs, "r", encoding="utf-8", errors="ignore") as html_file:
                                html = html_file.read()
                            rel_path = _normalize_relative_path(_relative_path_from_url(url))
                            topic, subtopic = _derive_topic_labels(rel_path)
                            title = _get_page_title(html)
                            size_kb = len(html.encode("utf-8")) // 1024
                            found_pages.append(
                                {
                                    "url": url,
                                    "relative_path": rel_path,
                                    "local_html_path": cached_local.replace("\\", "/"),
                                    "topic": topic,
                                    "subtopic": subtopic,
                                    "title": title,
                                    "size_kb": size_kb,
                                    "status": 200,
                                    "timestamp": datetime.now().isoformat(),
                                }
                            )

                            new_links = _extract_internal_links(url, html)
                            new_links_added = 0
                            for link in new_links:
                                if link not in visited and link not in queued:
                                    queue.append(link)
                                    queued.add(link)
                                    new_links_added += 1

                            print(
                                f"[{len(found_pages)}] CACHE {rel_path} (+{new_links_added} links)",
                                flush=True,
                            )
                            log.write(
                                f"[CACHE] {url} discovered={len(new_links)} new={new_links_added} "
                                f"visited={len(visited)} queued={len(queue)}\n"
                            )
                            log.flush()
                            continue
                        except Exception as cache_exc:
                            log.write(f"[CACHE_READ_ERROR] {url} - {cache_exc}\n")
                            log.flush()

            try:
                response = session.get(url, timeout=15)
                status = response.status_code
                if status != 200:
                    log.write(f"[HTTP_{status}] {url}\n")
                    download_errors.append(
                        {
                            "url": url,
                            "stage": "http_status",
                            "status": status,
                            "error": f"HTTP {status}",
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                    continue

                html = response.text
                title = _get_page_title(html)
                rel_path = _normalize_relative_path(_relative_path_from_url(url))
                topic, subtopic = _derive_topic_labels(rel_path)
                size_kb = len(html.encode("utf-8")) // 1024
                local_html_path = ""
                try:
                    local_html_path = _write_html_snapshot(version_dir, rel_path, html)
                except Exception as write_exc:
                    download_errors.append(
                        {
                            "url": url,
                            "relative_path": rel_path,
                            "stage": "save_html",
                            "status": status,
                            "error": str(write_exc),
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                    log.write(f"[SAVE_HTML_ERROR] {url} - {write_exc}\n")

                found_pages.append(
                    {
                        "url": url,
                        "relative_path": rel_path,
                        "local_html_path": local_html_path,
                        "topic": topic,
                        "subtopic": subtopic,
                        "title": title,
                        "size_kb": size_kb,
                        "status": status,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

                new_links = _extract_internal_links(url, html)
                new_links_added = 0
                for link in new_links:
                    if link not in visited and link not in queued:
                        queue.append(link)
                        queued.add(link)
                        new_links_added += 1

                print(f"[{len(found_pages)}] OK {rel_path} (+{new_links_added} links)", flush=True)
                log.write(
                    f"[OK] {url} discovered={len(new_links)} new={new_links_added} "
                    f"visited={len(visited)} queued={len(queue)}\n"
                )
                log.flush()

            except Exception as exc:
                log.write(f"[EXCEPTION] {url} - {exc}\n")
                log.flush()
                print(f"[ERRO] {url} -> {exc}", flush=True)
                download_errors.append(
                    {
                        "url": url,
                        "stage": "request_exception",
                        "status": None,
                        "error": str(exc),
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        log.write(
            f"[END] {datetime.now().isoformat()} total_found={len(found_pages)} "
            f"visited={len(visited)} queued_remaining={len(queue)}\n"
        )
        log.flush()

    return found_pages, download_errors


def _save_results(
    found_pages: List[Dict[str, Any]],
    output_json: str,
    output_csv: str,
    output_topics_json: str,
    output_locator_json: str,
    output_errors_json: str,
    download_errors: List[Dict[str, Any]],
) -> None:
    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as file_json:
        json.dump(found_pages, file_json, indent=2, ensure_ascii=False)

    with open(output_csv, "w", newline="", encoding="utf-8") as file_csv:
        writer = csv.writer(file_csv)
        writer.writerow(
            [
                "url",
                "relative_path",
                "local_html_path",
                "topic",
                "subtopic",
                "title",
                "size_kb",
                "status",
                "timestamp",
            ]
        )
        for page in found_pages:
            writer.writerow(
                [
                    page.get("url"),
                    page.get("relative_path"),
                    page.get("local_html_path"),
                    page.get("topic"),
                    page.get("subtopic"),
                    page.get("title"),
                    page.get("size_kb"),
                    page.get("status"),
                    page.get("timestamp"),
                ]
            )

    topics_index = _build_topics_index(found_pages)
    with open(output_topics_json, "w", encoding="utf-8") as file_topics:
        json.dump(topics_index, file_topics, indent=2, ensure_ascii=False)

    locator_index = _build_help_locator_index(found_pages)
    with open(output_locator_json, "w", encoding="utf-8") as file_locator:
        json.dump(locator_index, file_locator, indent=2, ensure_ascii=False)

    with open(output_errors_json, "w", encoding="utf-8") as file_errors:
        json.dump(
            {
                "generated_at": datetime.now().isoformat(),
                "total_errors": len(download_errors),
                "errors": download_errors,
            },
            file_errors,
            indent=2,
            ensure_ascii=False,
        )


def _write_version_manifest(
    version_dir: str,
    doc_version: str,
    release_row: Dict[str, Any],
    total_pages: int,
    total_download_errors: int,
    removed_versions: List[str],
    start_urls: List[str],
) -> str:
    manifest_path = os.path.join(version_dir, "meta", "help_scan_manifest.json")
    manifest = {
        "generated_at": datetime.now().isoformat(),
        "doc_version": doc_version,
        "start_urls": start_urls,
        "otm_release": {
            "otm_release_xid": release_row.get("OTM_RELEASE_XID"),
            "sortable_version": release_row.get("SORTABLE_VERSION"),
            "description": release_row.get("DESCRIPTION"),
            "domain_name": release_row.get("DOMAIN_NAME"),
        },
        "total_pages": total_pages,
        "total_download_errors": total_download_errors,
        "html_root": os.path.join(version_dir, "html"),
        "removed_versions": removed_versions,
    }
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as file_manifest:
        json.dump(manifest, file_manifest, indent=2, ensure_ascii=False)
    return manifest_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Varre links do Oracle OTM Help com versao dinamica derivada do ambiente "
            "OTM, baixa os HTMLs localmente e salva metadados em "
            "metadata/otm/help otm/<versao>/meta."
        )
    )
    parser.add_argument(
        "--doc-version",
        default="",
        help="Override manual da versao da documentacao (ex.: 25c, 26a).",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=0,
        help="Limita quantidade de paginas para varredura (0 = sem limite).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Apenas resolve versao e paths, sem executar a varredura.",
    )
    parser.add_argument(
        "--incremental",
        action="store_true",
        help=(
            "Reutiliza HTMLs locais existentes para URLs ja conhecidas e baixa "
            "somente paginas novas."
        ),
    )
    parser.add_argument(
        "--build-index-only",
        action="store_true",
        help=(
            "Nao faz varredura/download. Apenas recria os indices JSON a partir de "
            "help_files_list.json ja existente."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    os.makedirs(HELP_ROOT, exist_ok=True)

    release_row = _query_current_release_row()
    detected_doc_version = _release_row_to_doc_version(release_row)
    doc_version = (args.doc_version or detected_doc_version).strip().lower()
    if not re.fullmatch(r"\d{2}[a-z]", doc_version):
        raise RuntimeError(f"doc_version invalida: {doc_version!r}")

    base_url = DOC_BASE_TEMPLATE.format(doc_version=doc_version)
    start_urls = [
        urljoin(base_url, "index.html"),
        urljoin(base_url, "general/about_doc.htm"),
    ]
    normalized_starts: List[str] = []
    seen_start: Set[str] = set()
    for raw_start in start_urls:
        normalized = _canonicalize_doc_url(raw_start)
        if not normalized or normalized in seen_start:
            continue
        normalized_starts.append(normalized)
        seen_start.add(normalized)

    version_dir = os.path.join(HELP_ROOT, doc_version)
    meta_dir = os.path.join(version_dir, "meta")
    output_json = os.path.join(meta_dir, "help_files_list.json")
    output_csv = os.path.join(meta_dir, "help_files_list.csv")
    output_topics_json = os.path.join(meta_dir, "help_topics_index.json")
    output_locator_json = os.path.join(meta_dir, "help_locator_index.json")
    output_errors_json = os.path.join(meta_dir, "help_download_errors.json")
    log_file = os.path.join(meta_dir, "help_scan_log.txt")
    html_dir = os.path.join(version_dir, "html")

    removed_versions = _clean_old_versions(HELP_ROOT, doc_version)
    os.makedirs(meta_dir, exist_ok=True)

    # build-index-only deve apenas recalcular indices: nunca apagar HTML local.
    if not args.build_index_only:
        if not args.incremental:
            if os.path.isdir(html_dir):
                shutil.rmtree(html_dir, ignore_errors=True)
            os.makedirs(html_dir, exist_ok=True)
        else:
            os.makedirs(html_dir, exist_ok=True)

    print("Iniciando varredura do Oracle OTM Help (modo leitura)...")
    print(f"Versao detectada no ambiente: {detected_doc_version}")
    print(f"Versao utilizada para docs: {doc_version}")
    print(f"Base URL: {base_url}")
    print("Start URLs:")
    for start in normalized_starts:
        print(f" - {start}")
    if removed_versions:
        print(f"Versoes removidas da pasta help: {', '.join(sorted(removed_versions))}")
    if args.incremental:
        print("Modo incremental: ativo (download apenas de HTML novo).")

    if args.dry_run:
        manifest_path = _write_version_manifest(
            version_dir,
            doc_version,
            release_row,
            0,
            0,
            removed_versions,
            normalized_starts,
        )
        print(f"Dry-run concluido. Manifesto: {manifest_path}")
        return

    if args.build_index_only:
        if not os.path.exists(output_json):
            raise RuntimeError(
                f"Arquivo base nao encontrado para gerar indice: {output_json}"
            )
        with open(output_json, "r", encoding="utf-8") as file_json:
            pages = json.load(file_json)
        if not isinstance(pages, list):
            raise RuntimeError(f"Conteudo invalido em {output_json}: esperado lista JSON.")
        _save_results(
            pages,
            output_json=output_json,
            output_csv=output_csv,
            output_topics_json=output_topics_json,
            output_locator_json=output_locator_json,
            output_errors_json=output_errors_json,
            download_errors=[],
        )
        print(f"Rebuild de indices concluido. Total de paginas indexadas: {len(pages)}")
        print(f"Indice por topicos: {output_topics_json}")
        print(f"Indice localizador: {output_locator_json}")
        return

    max_pages = args.max_pages if args.max_pages and args.max_pages > 0 else None
    existing_pages_by_url = _load_existing_pages(output_json, version_dir) if args.incremental else {}
    if args.incremental:
        print(f"Entradas reaproveitaveis do cache local: {len(existing_pages_by_url)}")
    pages, download_errors = _crawl_help_docs(
        start_urls=normalized_starts,
        log_file=log_file,
        max_pages=max_pages,
        version_dir=version_dir,
        use_incremental_cache=args.incremental,
        existing_pages_by_url=existing_pages_by_url,
    )
    _save_results(
        pages,
        output_json=output_json,
        output_csv=output_csv,
        output_topics_json=output_topics_json,
        output_locator_json=output_locator_json,
        output_errors_json=output_errors_json,
        download_errors=download_errors,
    )
    manifest_path = _write_version_manifest(
        version_dir=version_dir,
        doc_version=doc_version,
        release_row=release_row,
        total_pages=len(pages),
        total_download_errors=len(download_errors),
        removed_versions=removed_versions,
        start_urls=normalized_starts,
    )

    current_version_file = os.path.join(HELP_ROOT, "current_version.json")
    with open(current_version_file, "w", encoding="utf-8") as file_current:
        json.dump(
            {
                "doc_version": doc_version,
                "detected_doc_version": detected_doc_version,
                "updated_at": datetime.now().isoformat(),
                "version_dir": version_dir,
                "html_dir": html_dir,
                "manifest": manifest_path,
            },
            file_current,
            indent=2,
            ensure_ascii=False,
        )

    print(f"Varredura concluida. Total de paginas mapeadas: {len(pages)}")
    print(f"Total de erros de download/salvamento: {len(download_errors)}")
    print(f"Resultados JSON: {output_json}")
    print(f"Resultados CSV: {output_csv}")
    print(f"Indice por topicos: {output_topics_json}")
    print(f"Indice localizador: {output_locator_json}")
    print(f"Erros de download: {output_errors_json}")
    print(f"HTML local: {html_dir}")
    print(f"Manifesto: {manifest_path}")
    print(f"Versao atual: {current_version_file}")


if __name__ == "__main__":
    main()
