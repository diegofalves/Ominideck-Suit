from flask import Flask, render_template, request, redirect, jsonify
import json
import os
import subprocess
import sys

from pathlib import Path

from ui.backend.loaders import load_all
from ui.backend.form_to_domain import form_to_domain
from ui.backend.validators import validate_project, DomainValidationError
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

PROJECT_ROOT = Path(__file__).resolve().parents[2]
GROUP_ZERO_ID = "SEM_GRUPO"
LEGACY_GROUP_ZERO_IDS = {"GROUP_0", GROUP_ZERO_ID}
IGNORED_GROUP_ID = "IGNORADOS"
PROTECTED_GROUP_IDS = set(LEGACY_GROUP_ZERO_IDS) | {IGNORED_GROUP_ID}

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


@app.after_request
def disable_cache_for_dynamic_routes(response):
    path = request.path or ""
    if path == "/projeto-migracao" or path.startswith("/api/"):
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


# ===== MAIN ROUTES =====

@app.route("/projeto-migracao", methods=["GET", "POST"])
def projeto_migracao():
    data = load_all()
    project = load_project()

    if request.method == "POST":
        action = _get_form_value(request.form, "action", "")
        reset_edit_mode = _get_form_value(request.form, "reset_edit_mode", "0")
        
        # ===== REMOVER OBJETO =====
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
                                print(f"✅ Objeto removido: {removed_obj.get('name', 'Sem nome')}")
                                
                                # Limpar estado de edição
                                if project.get("state"):
                                    project["state"]["last_edit_object_index"] = None
                                
                                save_project(project)
                            break
                
                return redirect("/projeto-migracao")
            except (ValueError, KeyError) as e:
                print(f"⚠️ Erro ao remover objeto: {e}")
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
        
        # ===== MOVER OBJETO PARA OUTRO GRUPO =====
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
                        
                        print(f"✅ Objeto '{moved_obj.get('name', 'Sem nome')}' movido de '{source_group.get('label')}' para '{target_group.get('label')}'")
                        
                        # Limpar estado de edição
                        if project.get("state"):
                            project["state"]["last_edit_object_index"] = None
                        
                        save_project(project)
                
                return redirect("/projeto-migracao")
            except (ValueError, KeyError) as e:
                print(f"⚠️ Erro ao mover objeto: {e}")
                return redirect("/projeto-migracao")
        
        # Se reset_edit_mode está ativo (mudança de grupo), limpar estado de edição
        if reset_edit_mode == "1":
            active_group_id = _get_form_value(request.form, "active_group_id", "")
            if project.get("state") is None:
                project["state"] = {}
            project["state"]["last_edit_object_index"] = None
            project["active_group_id"] = active_group_id
            save_project(project)
            return redirect("/projeto-migracao")
        
        # Se ação é apenas carregar objeto, salvar apenas o state sem validar
        if action == "load_object":
            edit_index = _get_form_value(request.form, "edit_object_index", "")
            requested_group_id = _get_form_value(request.form, "active_group_id", "")
            if edit_index != "":
                if project.get("state") is None:
                    project["state"] = {}
                project["state"]["last_edit_object_index"] = int(edit_index)
                if requested_group_id:
                    project["active_group_id"] = requested_group_id
                save_project(project)
            return redirect("/projeto-migracao#object-edit-panel")

        # Salvar apenas o objeto em edição (sem bloquear por validações globais do projeto).
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

            updated_object = source_group["objects"][resolved_source_idx]
            is_ignored = _is_truthy(updated_object.get("ignore_table"))
            if projected_domain.get("state") is None:
                projected_domain["state"] = {}
            if is_ignored:
                # Após salvar com ignore=true, o objeto migra para o grupo IGNORADOS.
                # Selecionamos esse grupo para refletir imediatamente no painel.
                projected_domain["active_group_id"] = IGNORED_GROUP_ID
                projected_domain["state"]["last_edit_object_index"] = None
            else:
                # Se estiver editando dentro de IGNORADOS e remover o ignore,
                # o objeto volta para SEM_GRUPO no save normalizado.
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
                schema=data["schema"],
                enums=data["enums"],
                ui=data["ui"],
                groups_catalog=data.get("groups_catalog", {}),
                project=domain_data,
                errors=e.args[0]
            )

        save_project(domain_data)
        return redirect("/projeto-migracao")

    return render_template(
        "projeto_migracao.html",
        schema=data["schema"],
        enums=data["enums"],
        ui=data["ui"],
        groups_catalog=data.get("groups_catalog", {}),
        project=project,
        errors=[]
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
