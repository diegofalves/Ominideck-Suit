from flask import Flask, render_template, request, redirect, jsonify, session
import json
import os
import subprocess
import sys

from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from ui.backend.loaders import load_all
from ui.backend.form_to_domain import form_to_domain
from ui.backend.validators import (
    validate_project,
    validate_subtable_constraints_for_object,
    DomainValidationError,
)
from ui.backend.writers import load_project, save_project
from ui.backend.schema_repository import SchemaRepository


# -------------------------------------------------
# App
# -------------------------------------------------
app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)
app.secret_key = os.environ.get("OMNIDECK_SECRET_KEY", "omnideck-internal-secret")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
GROUP_ZERO_ID = "SEM_GRUPO"
LEGACY_GROUP_ZERO_IDS = {"GROUP_0", GROUP_ZERO_ID}
IGNORED_GROUP_ID = "IGNORADOS"
PROTECTED_GROUP_IDS = set(LEGACY_GROUP_ZERO_IDS) | {IGNORED_GROUP_ID}
CADASTROS_PATH = PROJECT_ROOT / "domain" / "consultoria" / "cadastros.json"

# -------------------------------------------------
# Rotas
# -------------------------------------------------


def _is_truthy(value):
    return str(value or "").strip().lower() in {"1", "true", "on", "yes", "y"}


def _resolve_object_index(group, requested_index, object_name, object_type):
    objects = group.get("objects", []) if isinstance(group, dict) else []
    if not isinstance(objects, list):
        return None

    try:
        idx = int(requested_index)
    except (TypeError, ValueError):
        idx = None

    normalized_name = str(object_name or "").strip()
    normalized_type = str(object_type or "").strip().upper()

    if idx is not None and 0 <= idx < len(objects):
        candidate = objects[idx] if isinstance(objects[idx], dict) else {}
        cand_name = str(candidate.get("name") or "").strip()
        cand_type = str(candidate.get("object_type") or "").strip().upper()
        if (
            not normalized_name
            or not normalized_type
            or (cand_name == normalized_name and cand_type == normalized_type)
        ):
            return idx

    if normalized_name and normalized_type:
        for pos, obj in enumerate(objects):
            if not isinstance(obj, dict):
                continue
            cand_name = str(obj.get("name") or "").strip()
            cand_type = str(obj.get("object_type") or "").strip().upper()
            if cand_name == normalized_name and cand_type == normalized_type:
                return pos

    if idx is not None and 0 <= idx < len(objects):
        return idx

    return None


def _get_form_value(form, key, default=""):
    """
    Retorna o ultimo valor nao vazio para uma chave do form.
    Evita inconsistencias quando ha campos duplicados com mesmo name.
    """
    values = form.getlist(key)
    if not values:
        return default

    for raw in reversed(values):
        if raw is None:
            continue
        value = str(raw)
        if value != "":
            return value

    last = values[-1]
    if last is None:
        return default
    return str(last)


def _apply_no_cache_headers(response):
    """
    Evita cache em navegador/proxy para garantir que o painel
    sempre reflita o estado mais recente salvo em disco.
    """
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


def _to_positive_int(value: Any, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def _run_script(script_relative_path: str, args: Optional[List[str]] = None, timeout: int = 600) -> Tuple[int, Dict[str, Any], str]:
    script_path = PROJECT_ROOT / script_relative_path
    if not script_path.exists():
        return (
            404,
            {
                "status": "error",
                "message": f"Script nao encontrado: {script_path}",
                "result": None,
            },
            "",
        )

    command = [sys.executable, str(script_path)]
    if args:
        command.extend(args)

    try:
        completed = subprocess.run(
            command,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return (
            504,
            {
                "status": "error",
                "message": "Tempo limite atingido na execucao do script.",
                "result": None,
            },
            "",
        )
    except Exception as exc:
        return (
            500,
            {
                "status": "error",
                "message": f"Falha ao executar script: {exc}",
                "result": None,
            },
            "",
        )

    stdout = (completed.stdout or "").strip()
    stderr = (completed.stderr or "").strip()

    parsed_result: Optional[Dict[str, Any]] = None
    if stdout:
        try:
            raw = json.loads(stdout)
            parsed_result = raw if isinstance(raw, dict) else {"payload": raw}
        except json.JSONDecodeError:
            parsed_result = {"raw_output": stdout}

    if completed.returncode != 0:
        return (
            500,
            {
                "status": "error",
                "message": "Script retornou erro.",
                "result": parsed_result,
            },
            stderr,
        )

    return (
        200,
        {
            "status": "success",
            "message": "Script executado com sucesso.",
            "result": parsed_result,
        },
        stderr,
    )


def _normalize_status(value: Any) -> str:
    normalized = str(value or "").strip().upper()
    if normalized in {"DONE", "IN_PROGRESS", "PENDING"}:
        return normalized
    return "PENDING"


def _safe_pct(done: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round((done / total) * 100.0, 1)


def _build_migration_dashboard(project: Dict[str, Any]) -> Dict[str, Any]:
    groups = project.get("groups", [])
    if not isinstance(groups, list):
        groups = []

    excluded_ids = {IGNORED_GROUP_ID}
    tracked_objects: List[Dict[str, Any]] = []
    ignored_count = 0
    deployment_type_counter: Dict[str, int] = defaultdict(int)

    for group in groups:
        if not isinstance(group, dict):
            continue
        group_id = str(group.get("group_id") or "").strip().upper()
        group_label = str(group.get("label") or group_id or "Sem nome").strip()
        objects = group.get("objects", [])
        if not isinstance(objects, list):
            continue

        if group_id in excluded_ids:
            ignored_count += len([obj for obj in objects if isinstance(obj, dict)])
            continue

        for idx, obj in enumerate(objects):
            if not isinstance(obj, dict):
                continue
            status = obj.get("status", {})
            status_doc = _normalize_status(
                status.get("documentation") if isinstance(status, dict) else ""
            )
            status_dep = _normalize_status(
                status.get("deployment") if isinstance(status, dict) else ""
            )
            status_mig = _normalize_status(
                status.get("migration_project") if isinstance(status, dict) else ""
            )
            deployment_type = str(obj.get("deployment_type") or "SEM_DEFINICAO").strip() or "SEM_DEFINICAO"
            deployment_type_counter[deployment_type] += 1

            tracked_objects.append(
                {
                    "group_id": group_id,
                    "group_label": group_label,
                    "name": str(obj.get("name") or f"Item #{idx + 1}").strip(),
                    "object_type": str(obj.get("object_type") or "").strip() or "-",
                    "deployment_type": deployment_type,
                    "sequence": int(obj.get("sequence") or 0),
                    "status_documentation": status_doc,
                    "status_deployment": status_dep,
                    "status_migration_project": status_mig,
                }
            )

    total_objects = len(tracked_objects)
    done_doc = len([o for o in tracked_objects if o["status_documentation"] == "DONE"])
    done_dep = len([o for o in tracked_objects if o["status_deployment"] == "DONE"])
    done_mig = len([o for o in tracked_objects if o["status_migration_project"] == "DONE"])

    group_stats_map: Dict[str, Dict[str, Any]] = {}
    for item in tracked_objects:
        group_id = item["group_id"]
        if group_id not in group_stats_map:
            group_stats_map[group_id] = {
                "group_id": group_id,
                "group_label": item["group_label"],
                "total": 0,
                "done_documentation": 0,
                "done_deployment": 0,
                "done_migration_project": 0,
                "in_progress_any": 0,
                "pending_any": 0,
            }
        row = group_stats_map[group_id]
        row["total"] += 1
        if item["status_documentation"] == "DONE":
            row["done_documentation"] += 1
        if item["status_deployment"] == "DONE":
            row["done_deployment"] += 1
        if item["status_migration_project"] == "DONE":
            row["done_migration_project"] += 1
        statuses = [
            item["status_documentation"],
            item["status_deployment"],
            item["status_migration_project"],
        ]
        if "IN_PROGRESS" in statuses:
            row["in_progress_any"] += 1
        if "PENDING" in statuses:
            row["pending_any"] += 1

    groups_stats = sorted(
        group_stats_map.values(),
        key=lambda r: (
            999.0
            - (
                _safe_pct(r["done_documentation"], r["total"])
                + _safe_pct(r["done_deployment"], r["total"])
                + _safe_pct(r["done_migration_project"], r["total"])
            )
            / 3.0,
            r["group_label"],
        ),
    )

    for row in groups_stats:
        avg_done_pct = (
            _safe_pct(row["done_documentation"], row["total"])
            + _safe_pct(row["done_deployment"], row["total"])
            + _safe_pct(row["done_migration_project"], row["total"])
        ) / 3.0
        row["progress_pct"] = round(avg_done_pct, 1)

    critical_items = []
    for item in tracked_objects:
        pending_count = len(
            [
                status
                for status in (
                    item["status_documentation"],
                    item["status_deployment"],
                    item["status_migration_project"],
                )
                if status != "DONE"
            ]
        )
        if pending_count == 0:
            continue
        critical_items.append(
            {
                **item,
                "pending_count": pending_count,
            }
        )

    critical_items.sort(
        key=lambda i: (
            -i["pending_count"],
            0 if i["status_migration_project"] == "PENDING" else 1,
            i["group_label"],
            i["sequence"],
            i["name"],
        )
    )

    deployment_breakdown = sorted(
        [
            {
                "deployment_type": k,
                "count": v,
                "pct": _safe_pct(v, total_objects),
            }
            for k, v in deployment_type_counter.items()
        ],
        key=lambda d: (-d["count"], d["deployment_type"]),
    )

    return {
        "project_name": str(project.get("project", {}).get("name") or "Projeto de Migração").strip(),
        "project_code": str(project.get("project", {}).get("code") or "-").strip(),
        "total_groups": len(groups_stats),
        "total_objects": total_objects,
        "ignored_objects": ignored_count,
        "phases": {
            "documentation": {
                "done": done_doc,
                "total": total_objects,
                "pct": _safe_pct(done_doc, total_objects),
            },
            "deployment": {
                "done": done_dep,
                "total": total_objects,
                "pct": _safe_pct(done_dep, total_objects),
            },
            "migration_project": {
                "done": done_mig,
                "total": total_objects,
                "pct": _safe_pct(done_mig, total_objects),
            },
        },
        "overall_pct": round(
            (
                _safe_pct(done_doc, total_objects)
                + _safe_pct(done_dep, total_objects)
                + _safe_pct(done_mig, total_objects)
            )
            / 3.0,
            1,
        ),
        "groups": groups_stats,
        "critical_items": critical_items[:20],
        "deployment_breakdown": deployment_breakdown,
        "generated_at": str(project.get("project_metadata", {}).get("last_updated_at") or ""),
    }


def _default_cadastros_payload() -> Dict[str, Any]:
    return {
        "consultants": [],
        "clients": [],
        "projects": [],
        "consultancies": [],
    }


def _load_cadastros() -> Dict[str, Any]:
    if not CADASTROS_PATH.exists():
        return _default_cadastros_payload()
    try:
        payload = json.loads(CADASTROS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return _default_cadastros_payload()
    if not isinstance(payload, dict):
        return _default_cadastros_payload()

    normalized = _default_cadastros_payload()
    for key in normalized.keys():
        raw = payload.get(key, [])
        if isinstance(raw, list):
            normalized[key] = [item for item in raw if isinstance(item, dict)]
    return normalized


def _save_cadastros(payload: Dict[str, Any]) -> None:
    CADASTROS_PATH.parent.mkdir(parents=True, exist_ok=True)
    CADASTROS_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:10]}".upper()


@app.after_request
def disable_cache_for_dynamic_routes(response):
    path = request.path or ""
    if path in {"/projeto-migracao", "/execucao-scripts", "/dashboard-migracao", "/cadastros"} or path.startswith("/api/"):
        return _apply_no_cache_headers(response)
    return response

# ===== SCHEMA API ENDPOINTS =====

@app.route("/api/schema/tables", methods=["GET"])
def api_schema_tables():
    """
    Retorna lista de todas as tabelas OTM disponíveis.
    
    Response: {tables: [str]}
    """
    repo = SchemaRepository()
    tables = repo.list_tables()
    return jsonify({"tables": tables})


@app.route("/api/schema/<table_name>/raw", methods=["GET"])
def api_schema_raw(table_name: str):
    """
    Retorna schema completo e bruto de uma tabela.
    
    Response: schema object (columns, foreignKeys, etc)
    """
    repo = SchemaRepository()
    schema = repo.load_table(table_name)
    
    if not schema:
        return jsonify({"error": f"Schema not found: {table_name}"}), 404
    
    return jsonify(schema)


@app.route("/api/schema/<table_name>/fields", methods=["GET"])
def api_schema_fields(table_name: str):
    """
    Retorna FieldDescriptors normalizados com sections.
    Ordena por section, depois por nome de campo.
    
    Response: {
        table: str,
        sections: {
            CORE: [{name, label, type, required, ...}],
            LOCALIZACAO: [...],
            ...
        }
    }
    """
    repo = SchemaRepository()
    descriptors = repo.get_field_descriptors(table_name)
    
    if not descriptors:
        return jsonify({"error": f"Schema not found: {table_name}"}), 404
    
    # Agrupa por section
    by_section = {}
    for desc in descriptors:
        section = desc.section
        if section not in by_section:
            by_section[section] = []
        by_section[section].append({
            "name": desc.name,
            "label": desc.label,
            "type": desc.type,
            "required": desc.required,
            "maxLength": desc.maxLength,
            "defaultValue": desc.defaultValue,
            "constraint": desc.constraint,
            "lookup": desc.lookup,
        })
    
    return jsonify({
        "table": table_name,
        "sections": by_section
    })


@app.route("/api/otm/update-tables", methods=["POST"])
def api_otm_update_tables():
    """
    Executa script CORE de atualizacao das estatisticas de dominio OTM.

    Response:
    {
      status: "success" | "error",
      message: str,
      result: dict | null
    }
    """
    script_path = PROJECT_ROOT / "infra" / "update_otm_tables.py"

    if not script_path.exists():
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Script nao encontrado: {script_path}",
                    "result": None,
                }
            ),
            404,
        )

    try:
        completed = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=600,
        )
    except subprocess.TimeoutExpired:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Tempo limite atingido ao atualizar estatisticas de dominio OTM.",
                    "result": None,
                }
            ),
            504,
        )
    except Exception as exc:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Falha ao executar script de estatisticas OTM: {exc}",
                    "result": None,
                }
            ),
            500,
        )

    stdout = (completed.stdout or "").strip()
    stderr = (completed.stderr or "").strip()

    parsed_result = None
    if stdout:
        try:
            parsed_result = json.loads(stdout)
        except json.JSONDecodeError:
            parsed_result = {"raw_output": stdout}

    if completed.returncode != 0:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Script de estatisticas OTM retornou erro.",
                    "result": parsed_result,
                    "stderr": stderr[-2000:] if stderr else None,
                }
            ),
            500,
        )

    is_valid_contract = (
        isinstance(parsed_result, dict)
        and parsed_result.get("metadataType") == "OTM_DOMAIN_TABLE_STATISTICS"
        and isinstance(parsed_result.get("tables"), list)
    )
    if not is_valid_contract:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Resposta do script em formato inesperado para estatisticas de dominio OTM.",
                    "result": parsed_result,
                    "stderr": stderr[-2000:] if stderr else None,
                }
            ),
            502,
        )

    return jsonify(
        {
            "status": "success",
            "message": "Atualizacao de estatisticas de dominio concluida.",
            "result": parsed_result,
            "stderr": stderr[-2000:] if stderr else None,
        }
    )


@app.route("/api/otm/update-object-cache", methods=["POST"])
def api_otm_update_object_cache():
    """
    Executa atualizacao de cache de itens por escopo.

    Body JSON:
    {
      scope: "all" | "migration_group" | "migration_item",
      migration_group_id?: str,
      migration_item_name?: str,
      migration_item_id?: str,
      dry_run?: bool
    }
    """
    script_path = PROJECT_ROOT / "infra" / "update_otm_object_cache.py"

    if not script_path.exists():
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Script nao encontrado: {script_path}",
                    "result": None,
                }
            ),
            404,
        )

    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        payload = {}

    raw_scope = str(payload.get("scope") or "").strip().lower()
    scope_aliases = {
        "all": "all",
        "all_migration_items": "all",
        "all_objects": "all",
        "migration_group": "group",
        "group": "group",
        "group_objects": "group",
        "migration_item": "item",
        "object": "item",
        "single_object": "item",
        "single_migration_item": "item",
    }
    scope = scope_aliases.get(raw_scope, "")

    if not scope:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": (
                        "Parametro 'scope' invalido. "
                        "Use: all, migration_group ou migration_item."
                    ),
                    "result": None,
                }
            ),
            400,
        )

    migration_group_id = str(
        payload.get("migration_group_id") or payload.get("group_id") or ""
    ).strip()
    migration_item_name = str(
        payload.get("migration_item_name") or payload.get("object_name") or ""
    ).strip()
    migration_item_id = str(payload.get("migration_item_id") or "").strip()
    dry_run = _is_truthy(payload.get("dry_run"))

    command = [sys.executable, str(script_path)]

    if scope == "all":
        command.append("--all-migration-items")
    elif scope == "group":
        if not migration_group_id:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": (
                            "Parametro 'migration_group_id' e obrigatorio "
                            "para scope=migration_group."
                        ),
                        "result": None,
                    }
                ),
                400,
            )
        command.extend(["--migration-group-id", migration_group_id])
    else:
        # Compatibilidade: scope=object segue equivalente a migration_item.
        if migration_item_id:
            command.extend(["--migration-item-id", migration_item_id])
        elif migration_item_name:
            command.extend(["--migration-item-name", migration_item_name])
            if migration_group_id:
                command.extend(["--migration-group-id", migration_group_id])
        else:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": (
                            "Parametro 'migration_item_name' ou 'migration_item_id' "
                            "e obrigatorio para scope=migration_item."
                        ),
                        "result": None,
                    }
                ),
                400,
            )

    if dry_run:
        command.append("--dry-run")

    try:
        completed = subprocess.run(
            command,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=1800,
        )
    except subprocess.TimeoutExpired:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Tempo limite atingido ao atualizar cache de itens.",
                    "result": None,
                }
            ),
            504,
        )
    except Exception as exc:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Falha ao executar script de cache de itens: {exc}",
                    "result": None,
                }
            ),
            500,
        )

    stdout = (completed.stdout or "").strip()
    stderr = (completed.stderr or "").strip()

    parsed_result = None
    if stdout:
        try:
            parsed_result = json.loads(stdout)
        except json.JSONDecodeError:
            parsed_result = {"raw_output": stdout}

    script_status = ""
    if isinstance(parsed_result, dict):
        script_status = str(parsed_result.get("status") or "").strip().lower()

    if script_status in {"success", "partial_success"}:
        message = (
            "Atualizacao de cache de itens concluida."
            if script_status == "success"
            else "Atualizacao de cache de itens concluida parcialmente."
        )
        return jsonify(
            {
                "status": script_status,
                "message": message,
                "result": parsed_result,
                "stderr": stderr[-2000:] if stderr else None,
            }
        )

    if completed.returncode != 0:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Script de cache de itens retornou erro.",
                    "result": parsed_result,
                    "stderr": stderr[-2000:] if stderr else None,
                }
            ),
            500,
        )

    return (
        jsonify(
            {
                "status": "error",
                "message": "Resposta do script em formato inesperado para cache de itens.",
                "result": parsed_result,
                "stderr": stderr[-2000:] if stderr else None,
            }
        ),
        502,
    )


@app.route("/api/scripts/update-translations-cache", methods=["POST"])
def api_scripts_update_translations_cache():
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        payload = {}

    args: List[str] = []
    if _is_truthy(payload.get("incremental")):
        args.append("--incremental")

    timeout_seconds = _to_positive_int(payload.get("timeout"), 1800)
    page_size = _to_positive_int(payload.get("page_size"), 5000)
    args.extend(["--timeout", str(timeout_seconds), "--page-size", str(page_size)])

    status_code, response_body, stderr = _run_script(
        "infra/update_otm_translations_cache.py",
        args=args,
        timeout=max(timeout_seconds + 60, 600),
    )
    if stderr:
        response_body["stderr"] = stderr[-2000:]
    return jsonify(response_body), status_code


@app.route("/api/scripts/update-help-index", methods=["POST"])
def api_scripts_update_help_index():
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        payload = {}

    args: List[str] = []
    doc_version = str(payload.get("doc_version") or "").strip().lower()
    if doc_version:
        args.extend(["--doc-version", doc_version])

    book_key = str(payload.get("book_key") or "").strip().lower()
    if book_key:
        args.extend(["--book", book_key])

    max_pages = _to_positive_int(payload.get("max_pages"), 0)
    if max_pages > 0:
        args.extend(["--max-pages", str(max_pages)])

    if _is_truthy(payload.get("dry_run")):
        args.append("--dry-run")
    if _is_truthy(payload.get("incremental")):
        args.append("--incremental")
    if _is_truthy(payload.get("build_index_only")):
        args.append("--build-index-only")

    status_code, response_body, stderr = _run_script(
        "infra/update_otm_help_index.py",
        args=args,
        timeout=7200,
    )
    if stderr:
        response_body["stderr"] = stderr[-2000:]
    return jsonify(response_body), status_code


@app.route("/api/scripts/validate-eligible-tables", methods=["POST"])
def api_scripts_validate_eligible_tables():
    status_code, response_body, stderr = _run_script(
        "infra/validate_migration_project_eligible_tables.py",
        args=[],
        timeout=120,
    )
    if stderr:
        response_body["stderr"] = stderr[-2000:]
    return jsonify(response_body), status_code


@app.route("/api/scripts/build-agent-sql-catalog", methods=["POST"])
def api_scripts_build_agent_sql_catalog():
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        payload = {}

    mode = str(payload.get("mode") or "eligible").strip().lower()
    if mode not in {"eligible", "all"}:
        mode = "eligible"

    output_file = str(payload.get("output_file") or "").strip()
    if not output_file:
        if mode == "all":
            output_file = "metadata/otm/agent_sql/catalog/schema_catalog_all_tables.jsonl"
        else:
            output_file = "metadata/otm/agent_sql/catalog/schema_catalog_eligible_tables.jsonl"

    args: List[str] = ["--mode", mode, "--output", output_file]
    status_code, response_body, stderr = _run_script(
        "scripts/build_agent_sql_catalog.py",
        args=args,
        timeout=1800,
    )
    if stderr:
        response_body["stderr"] = stderr[-2000:]
    return jsonify(response_body), status_code


# ===== MAIN ROUTES =====

@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")


@app.route("/execucao-scripts", methods=["GET"])
def execucao_scripts():
    return render_template("execucao_scripts.html")


@app.route("/cadastros", methods=["GET", "POST"])
def cadastros():
    payload = _load_cadastros()
    error_message = ""
    success_message = ""

    if request.method == "POST":
        entity = str(request.form.get("entity") or "").strip().lower()

        if entity == "consultant":
            name = str(request.form.get("consultant_name") or "").strip()
            email = str(request.form.get("consultant_email") or "").strip()
            role = str(request.form.get("consultant_role") or "").strip()
            status = str(request.form.get("consultant_status") or "ACTIVE").strip().upper()
            phone = str(request.form.get("consultant_phone") or "").strip()
            seniority = str(request.form.get("consultant_seniority") or "").strip()
            specialty = str(request.form.get("consultant_specialty") or "").strip()
            city_state = str(request.form.get("consultant_city_state") or "").strip()
            document = str(request.form.get("consultant_document") or "").strip()
            availability_pct = str(request.form.get("consultant_availability_pct") or "").strip()

            if not name:
                error_message = "Informe o nome do consultor."
            else:
                payload["consultants"].append(
                    {
                        "consultant_id": _new_id("CONSULTANT"),
                        "name": name,
                        "email": email,
                        "role": role,
                        "phone": phone,
                        "seniority": seniority,
                        "specialty": specialty,
                        "city_state": city_state,
                        "document": document,
                        "availability_pct": availability_pct,
                        "status": status or "ACTIVE",
                    }
                )
                _save_cadastros(payload)
                return redirect("/cadastros?ok=consultor")

        elif entity == "client":
            name = str(request.form.get("client_name") or "").strip()
            segment = str(request.form.get("client_segment") or "").strip()
            contact_name = str(request.form.get("client_contact_name") or "").strip()
            contact_email = str(request.form.get("client_contact_email") or "").strip()
            legal_name = str(request.form.get("client_legal_name") or "").strip()
            cnpj = str(request.form.get("client_cnpj") or "").strip()
            size = str(request.form.get("client_size") or "").strip()
            country = str(request.form.get("client_country") or "").strip()
            state = str(request.form.get("client_state") or "").strip()
            city = str(request.form.get("client_city") or "").strip()
            billing_email = str(request.form.get("client_billing_email") or "").strip()
            account_manager = str(request.form.get("client_account_manager") or "").strip()

            if not name:
                error_message = "Informe o nome do cliente."
            else:
                payload["clients"].append(
                    {
                        "client_id": _new_id("CLIENT"),
                        "name": name,
                        "legal_name": legal_name,
                        "cnpj": cnpj,
                        "segment": segment,
                        "size": size,
                        "country": country,
                        "state": state,
                        "city": city,
                        "contact_name": contact_name,
                        "contact_email": contact_email,
                        "billing_email": billing_email,
                        "account_manager": account_manager,
                    }
                )
                _save_cadastros(payload)
                return redirect("/cadastros?ok=cliente")

        elif entity == "project":
            code = str(request.form.get("project_code") or "").strip().upper()
            name = str(request.form.get("project_name") or "").strip()
            client_id = str(request.form.get("project_client_id") or "").strip()
            consultant_id = str(request.form.get("project_consultant_id") or "").strip()
            consultancy_id = str(request.form.get("project_consultancy_id") or "").strip()
            status = str(request.form.get("project_status") or "PLANNING").strip().upper()
            start_date = str(request.form.get("project_start_date") or "").strip()
            end_date = str(request.form.get("project_end_date") or "").strip()
            env_dev_url = str(request.form.get("project_env_dev_url") or "").strip()
            env_test_url = str(request.form.get("project_env_test_url") or "").strip()
            env_prod_url = str(request.form.get("project_env_prod_url") or "").strip()
            integration_user = str(request.form.get("project_integration_user") or "").strip()
            integration_password = str(request.form.get("project_integration_password") or "").strip()

            if not code or not name:
                error_message = "Informe código e nome do projeto."
            elif not client_id:
                error_message = "Selecione o cliente do projeto."
            else:
                payload["projects"].append(
                    {
                        "project_id": _new_id("PROJECT"),
                        "code": code,
                        "name": name,
                        "client_id": client_id,
                        "consultant_id": consultant_id,
                        "consultancy_id": consultancy_id,
                        "status": status or "PLANNING",
                        "start_date": start_date,
                        "end_date": end_date,
                        "environments": {
                            "dev_url": env_dev_url,
                            "test_url": env_test_url,
                            "prod_url": env_prod_url,
                        },
                        "integration": {
                            "user": integration_user,
                            "password": integration_password,
                        },
                    }
                )
                _save_cadastros(payload)
                return redirect("/cadastros?ok=projeto")

        elif entity == "consultancy":
            consultant_id = str(request.form.get("consultancy_consultant_id") or "").strip()
            client_id = str(request.form.get("consultancy_client_id") or "").strip()
            project_id = str(request.form.get("consultancy_project_id") or "").strip()
            service_name = str(request.form.get("consultancy_service_name") or "").strip()
            hourly_rate = str(request.form.get("consultancy_hourly_rate") or "").strip()
            status = str(request.form.get("consultancy_status") or "PLANNED").strip().upper()
            contract_type = str(request.form.get("consultancy_contract_type") or "").strip().upper()
            taxes_payload: Dict[str, str] = {}

            if contract_type == "PJ":
                taxes_payload = {
                    "tax_regime": str(request.form.get("consultancy_pj_tax_regime") or "").strip(),
                    "iss_rate": str(request.form.get("consultancy_pj_iss_rate") or "").strip(),
                    "service_tax_rate": str(request.form.get("consultancy_pj_service_tax_rate") or "").strip(),
                    "management_fee_rate": str(request.form.get("consultancy_pj_management_fee_rate") or "").strip(),
                }
            elif contract_type == "CLT":
                taxes_payload = {
                    "inss_rate": str(request.form.get("consultancy_clt_inss_rate") or "").strip(),
                    "fgts_rate": str(request.form.get("consultancy_clt_fgts_rate") or "").strip(),
                    "benefits_rate": str(request.form.get("consultancy_clt_benefits_rate") or "").strip(),
                    "thirteenth_salary_rate": str(request.form.get("consultancy_clt_thirteenth_salary_rate") or "").strip(),
                }
            elif contract_type == "COOPERATIVA":
                taxes_payload = {
                    "cooperative_fee_rate": str(request.form.get("consultancy_coop_fee_rate") or "").strip(),
                    "admin_fee_rate": str(request.form.get("consultancy_coop_admin_rate") or "").strip(),
                    "inss_rate": str(request.form.get("consultancy_coop_inss_rate") or "").strip(),
                    "taxes_rate": str(request.form.get("consultancy_coop_taxes_rate") or "").strip(),
                }

            if not consultant_id or not client_id or not project_id:
                error_message = "Selecione consultor, cliente e projeto para cadastrar a consultoria."
            elif not service_name:
                error_message = "Informe o tipo de consultoria/serviço."
            elif contract_type not in {"PJ", "CLT", "COOPERATIVA"}:
                error_message = "Selecione o tipo de contratação."
            else:
                payload["consultancies"].append(
                    {
                        "consultancy_id": _new_id("CONSULTANCY"),
                        "consultant_id": consultant_id,
                        "client_id": client_id,
                        "project_id": project_id,
                        "service_name": service_name,
                        "hourly_rate": hourly_rate,
                        "status": status or "PLANNED",
                        "contract_type": contract_type,
                        "taxes": taxes_payload,
                    }
                )
                _save_cadastros(payload)
                return redirect("/cadastros?ok=consultoria")

        else:
            error_message = "Tipo de cadastro inválido."

    ok_param = str(request.args.get("ok") or "").strip().lower()
    if ok_param:
        success_message = f"Cadastro de {ok_param} realizado com sucesso."

    return render_template(
        "cadastros.html",
        cadastros=payload,
        success_message=success_message,
        error_message=error_message,
    )


@app.route("/dashboard-migracao", methods=["GET"])
def dashboard_migracao():
    session["can_access_migration_panel"] = True
    project = load_project() or {}
    dashboard = _build_migration_dashboard(project)
    return render_template("dashboard_migracao.html", dashboard=dashboard)


@app.route("/api/edit-group", methods=["POST"])
def api_edit_group():
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        return jsonify({"status": "error", "message": "Payload inválido."}), 400

    group_id = str(payload.get("group_id") or "").strip()
    if not group_id:
        return jsonify({"status": "error", "message": "group_id é obrigatório."}), 400

    project = load_project()
    if not project or not isinstance(project.get("groups"), list):
        return jsonify({"status": "error", "message": "Projeto não encontrado."}), 404

    target_group = None
    for group in project["groups"]:
        if isinstance(group, dict) and str(group.get("group_id") or "").strip() == group_id:
            target_group = group
            break

    if target_group is None:
        return jsonify({"status": "error", "message": f"Grupo '{group_id}' não encontrado."}), 404

    updated_fields = []

    new_label = payload.get("label")
    if new_label is not None:
        new_label = str(new_label).strip()
        if new_label:
            target_group["label"] = new_label
            updated_fields.append("label")

    new_description = payload.get("description")
    if new_description is not None:
        target_group["description"] = str(new_description).strip()
        updated_fields.append("description")

    new_sequence = payload.get("sequence")
    if new_sequence is not None:
        try:
            seq = int(new_sequence)
            if seq >= 1:
                target_group["sequence"] = seq
                updated_fields.append("sequence")
        except (TypeError, ValueError):
            pass

    if not updated_fields:
        return jsonify({"status": "ok", "message": "Nenhum campo alterado.", "group": target_group})

    save_project(project)

    return jsonify({
        "status": "success",
        "message": f"Grupo '{group_id}' atualizado. Campos: {', '.join(updated_fields)}.",
        "group": target_group,
    })


@app.route("/projeto-migracao", methods=["GET", "POST"])
def projeto_migracao():
    if not session.get("can_access_migration_panel"):
        return redirect("/dashboard-migracao")

    data = load_all()
    project = load_project()

    if request.method == "POST":
        action = _get_form_value(request.form, "action", "")
        reset_edit_mode = _get_form_value(request.form, "reset_edit_mode", "0")

        # Atualizar grupo ativo (somente quando reset_edit_mode=1)
        if reset_edit_mode == "1":
            active_group_id = _get_form_value(request.form, "active_group_id", "")
            if project.get("state") is None:
                project["state"] = {}
            project["state"]["last_edit_object_index"] = None
            if active_group_id:
                project["active_group_id"] = active_group_id
                project["active_migration_group_id"] = active_group_id
            save_project(project)
            return redirect("/projeto-migracao")

        # ===== REMOVER ITEM =====
        remove_object_index = _get_form_value(request.form, "remove_object_index", "")
        if remove_object_index != "":
            try:
                remove_idx = int(remove_object_index)
                active_group_id = project.get("active_group_id")
                
                if active_group_id and project.get("groups"):
                    for group in project["groups"]:
                        if group.get("group_id") == active_group_id:
                            if 0 <= remove_idx < len(group.get("objects", [])):
                                removed_obj = group["objects"].pop(remove_idx)
                                print(f"✅ Item removido: {removed_obj.get('name', 'Sem nome')}")
                                
                                # Limpar estado de edição
                                if project.get("state"):
                                    project["state"]["last_edit_object_index"] = None
                                
                                save_project(project)
                            break
                
                return redirect("/projeto-migracao")
            except (ValueError, KeyError) as e:
                print(f"⚠️ Erro ao remover item: {e}")
                return redirect("/projeto-migracao")
        
        # ===== REMOVER GRUPO =====
        remove_group_id = _get_form_value(request.form, "remove_group_id", "")
        if remove_group_id != "":
            try:
                if str(remove_group_id).strip().upper() in PROTECTED_GROUP_IDS:
                    return redirect("/projeto-migracao")

                if project.get("groups"):
                    # Encontrar e remover o grupo
                    for i, group in enumerate(project["groups"]):
                        if group.get("group_id") == remove_group_id:
                            removed_group = project["groups"].pop(i)
                            print(f"✅ Grupo removido: {removed_group.get('label', 'Sem nome')}")
                            
                            # Se era o grupo ativo, desativar
                            if project.get("active_group_id") == remove_group_id:
                                project["active_group_id"] = None
                            
                            save_project(project)
                            break
                
                return redirect("/projeto-migracao")
            except (ValueError, KeyError) as e:
                print(f"⚠️ Erro ao remover grupo: {e}")
                return redirect("/projeto-migracao")
        
        # ===== MOVER ITEM PARA OUTRO GRUPO =====
        move_object_index = _get_form_value(request.form, "move_object_index", "")
        move_to_group_id = _get_form_value(request.form, "move_to_group_id", "")
        
        if move_object_index != "" and move_to_group_id:
            try:
                move_idx = int(move_object_index)
                active_group_id = project.get("active_group_id")
                
                if active_group_id and project.get("groups"):
                    # Encontrar grupo de origem
                    source_group = None
                    target_group = None
                    
                    for group in project["groups"]:
                        if group.get("group_id") == active_group_id:
                            source_group = group
                        if group.get("group_id") == move_to_group_id:
                            target_group = group
                    
                    if source_group and target_group and 0 <= move_idx < len(source_group.get("objects", [])):
                        # Remover do grupo de origem
                        moved_obj = source_group["objects"].pop(move_idx)
                        
                        # Adicionar ao grupo de destino
                        if "objects" not in target_group:
                            target_group["objects"] = []
                        target_group["objects"].append(moved_obj)
                        
                        print(f"✅ Item '{moved_obj.get('name', 'Sem nome')}' movido de '{source_group.get('label')}' para '{target_group.get('label')}'")
                        
                        # Limpar estado de edição
                        if project.get("state"):
                            project["state"]["last_edit_object_index"] = None
                        
                        save_project(project)
                
                return redirect("/projeto-migracao")
            except (ValueError, KeyError) as e:
                print(f"⚠️ Erro ao mover item: {e}")
                return redirect("/projeto-migracao")
        
        # Se reset_edit_mode esta ativo (mudanca de grupo), limpar estado de edicao
        if reset_edit_mode == "1":
            active_group_id = _get_form_value(request.form, "active_group_id", "")
            if project.get("state") is None:
                project["state"] = {}
            project["state"]["last_edit_object_index"] = None
            project["active_group_id"] = active_group_id
            save_project(project)
            return redirect("/projeto-migracao")
        
        # Se acao for carregar grupo para edição
        if action == "load_group":
            edit_group_index = _get_form_value(request.form, "edit_group_index", "")
            requested_group_id = _get_form_value(request.form, "active_group_id", "")
            if edit_group_index != "":
                if project.get("state") is None:
                    project["state"] = {}
                project["state"]["last_edit_group_index"] = int(edit_group_index)
                # Limpa edição de item
                project["state"]["last_edit_object_index"] = None
                if requested_group_id:
                    project["active_group_id"] = requested_group_id
                save_project(project)
            return redirect("/projeto-migracao#group-edit-panel")

        # Se acao e apenas carregar item, salvar apenas o state sem validar
        if action == "load_object":
            edit_index = _get_form_value(request.form, "edit_object_index", "")
            requested_group_id = _get_form_value(request.form, "active_group_id", "")
            if edit_index != "":
                if project.get("state") is None:
                    project["state"] = {}
                project["state"]["last_edit_object_index"] = int(edit_index)
                # Limpa edição de grupo
                project["state"]["last_edit_group_index"] = None
                if requested_group_id:
                    project["active_group_id"] = requested_group_id
                save_project(project)
            return redirect("/projeto-migracao#object-edit-panel")

        # Salvar apenas o item em edicao (sem bloquear por validacoes globais do projeto).
        # Também entra aqui quando a flag de ignore foi alterada no formulário.
        should_save_object_partial = action == "save_object"
        if not should_save_object_partial and request.form.get("object_ignore_table_present") is not None:
            try:
                group_id_probe = str(_get_form_value(request.form, "active_group_id", "") or "").strip()
                idx_probe = _get_form_value(request.form, "edit_object_index", "")
                name_probe = _get_form_value(request.form, "object_name", "")
                type_probe = _get_form_value(request.form, "object_type", "") or _get_form_value(request.form, "object_otm_table", "")
                if group_id_probe:
                    for group in project.get("groups", []):
                        if str(group.get("group_id") or "").strip().upper() != group_id_probe.upper():
                            continue
                        resolved_idx = _resolve_object_index(group, idx_probe, name_probe, type_probe)
                        if resolved_idx is None:
                            break
                        objects = group.get("objects", []) or []
                        current_ignore = _is_truthy(objects[resolved_idx].get("ignore_table"))
                        requested_ignore = _is_truthy(_get_form_value(request.form, "object_ignore_table", ""))
                        if current_ignore != requested_ignore:
                            should_save_object_partial = True
                        break
            except Exception:
                pass

        if should_save_object_partial:
            def _to_int_or_none(value):
                try:
                    return int(value)
                except (TypeError, ValueError):
                    return None

            active_group_id = str(_get_form_value(request.form, "active_group_id", "") or "").strip()
            edit_object_index = _to_int_or_none(_get_form_value(request.form, "edit_object_index", ""))
            object_name = _get_form_value(request.form, "object_name", "")
            object_type = _get_form_value(request.form, "object_type", "") or _get_form_value(request.form, "object_otm_table", "")

            if not active_group_id:
                return redirect("/projeto-migracao")

            projected_domain = form_to_domain(request.form, existing_project=project)
            source_group = None
            for group in projected_domain.get("groups", []):
                if str(group.get("group_id") or "").strip().upper() == active_group_id.upper():
                    source_group = group
                    break

            if not isinstance(source_group, dict):
                return redirect("/projeto-migracao")

            resolved_source_idx = _resolve_object_index(
                source_group,
                edit_object_index,
                object_name,
                object_type,
            )
            if resolved_source_idx is None:
                return redirect("/projeto-migracao")

            try:
                validate_subtable_constraints_for_object(
                    projected_domain,
                    active_group_id,
                    resolved_source_idx,
                )
            except DomainValidationError as e:
                return render_template(
                    "projeto_migracao.html",
                    data=data,
                    schema=data["schema"],
                    enums=data["enums"],
                    ui=data["ui"],
                    groups_catalog=data.get("groups_catalog", {}),
                    project=projected_domain,
                    errors=e.args[0],
                )

            updated_object = source_group["objects"][resolved_source_idx]
            is_ignored = _is_truthy(updated_object.get("ignore_table"))
            if projected_domain.get("state") is None:
                projected_domain["state"] = {}
            if is_ignored:
                # Apos salvar com ignore=true, o item migra para o grupo IGNORADOS.
                # Selecionamos esse grupo para refletir imediatamente no painel.
                projected_domain["active_group_id"] = IGNORED_GROUP_ID
                projected_domain["state"]["last_edit_object_index"] = None
            else:
                # Se estiver editando dentro de IGNORADOS e remover o ignore,
                # o item volta para SEM_GRUPO no save normalizado.
                if active_group_id.upper() == IGNORED_GROUP_ID:
                    projected_domain["active_group_id"] = GROUP_ZERO_ID
                    projected_domain["state"]["last_edit_object_index"] = None
                else:
                    projected_domain["active_group_id"] = active_group_id
                    projected_domain["state"]["last_edit_object_index"] = resolved_source_idx
            save_project(projected_domain)
            return redirect("/projeto-migracao")
        
        # Caso contrário, validar e salvar normalmente
        domain_data = form_to_domain(request.form, existing_project=project)

        try:
            validate_project(domain_data)
        except DomainValidationError as e:
            return render_template(
                "projeto_migracao.html",
                data=data,
                schema=data["schema"],
                enums=data["enums"],
                ui=data["ui"],
                groups_catalog=data.get("groups_catalog", {}),
                project=domain_data,
                errors=e.args[0]
            )

        save_project(domain_data)
        return redirect("/projeto-migracao")

    # Montar columns_catalog: dicionário {tabela: [colunas]}
    from ui.backend.schema_repository import SchemaRepository

    def get_all_tables_from_project(proj):
        tables = set()
        if not proj:
            return tables
        for group in proj.get("groups", []):
            for obj in group.get("objects", []):
                t = obj.get("otm_table") or obj.get("object_type")
                if t:
                    tables.add(str(t).upper())
                for sub in obj.get("otm_subtables", []):
                    tables.add(str(sub).upper())
        return tables


    import glob
    cache_dir = PROJECT_ROOT / "metadata" / "otm" / "cache" / "objects"

    def get_cache_file_for_table(table):
        # Busca arquivo de cache que contenha o nome da tabela (exato, upper)
        pattern = f"*{table.upper()}*.json"
        files = list(cache_dir.glob(pattern))
        return files[0] if files else None

    def get_nonempty_columns(table):
        schema = SchemaRepository.load_table(table)
        if not (schema and "columns" in schema):
            return []
        cache_file = get_cache_file_for_table(table)
        if not cache_file:
            # Se não houver cache, retorna todas as colunas
            return [col["name"] for col in schema["columns"]]
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
            # Estrutura esperada: cache_data["tables"][table]["rows"]
            rows = cache_data.get("tables", {}).get(table, {}).get("rows", [])
            if not rows:
                return []
            result = []
            for col in schema["columns"]:
                col_name = col["name"]
                # Se pelo menos um valor não for vazio/nulo, inclui
                if any(row.get(col_name) not in (None, "") for row in rows):
                    result.append(col_name)
            return result
        except Exception as e:
            print(f"Erro lendo cache para tabela {table}: {e}")
            return [col["name"] for col in schema["columns"]]

    all_tables = get_all_tables_from_project(project)
    columns_catalog = {}
    for table in all_tables:
        columns_catalog[table] = get_nonempty_columns(table)

    return render_template(
        "projeto_migracao.html",
        data=data,
        schema=data["schema"],
        enums=data["enums"],
        ui=data["ui"],
        groups_catalog=data.get("groups_catalog", {}),
        project=project,
        errors=[],
        columns_catalog=columns_catalog
    )


# -------------------------------------------------
# Bootstrap
# -------------------------------------------------
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8088,
        debug=False,
        use_reloader=False
    )
