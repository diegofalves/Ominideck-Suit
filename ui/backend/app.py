from flask import Flask, render_template, request, redirect, jsonify
import json
import os

from pathlib import Path

from .loaders import load_all
from .form_to_domain import form_to_domain
from .validators import validate_project, DomainValidationError
from .writers import load_project, save_project
from .schema_repository import SchemaRepository


# -------------------------------------------------
# App
# -------------------------------------------------
app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

# -------------------------------------------------
# Rotas
# -------------------------------------------------

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


# ===== MAIN ROUTES =====

@app.route("/projeto-migracao", methods=["GET", "POST"])
def projeto_migracao():
    data = load_all()
    project = load_project()

    if request.method == "POST":
        action = request.form.get("action", "")
        reset_edit_mode = request.form.get("reset_edit_mode", "0")
        
        # ===== REMOVER OBJETO =====
        remove_object_index = request.form.get("remove_object_index")
        if remove_object_index is not None and remove_object_index != "":
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
        remove_group_id = request.form.get("remove_group_id")
        if remove_group_id is not None and remove_group_id != "":
            try:
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
        move_object_index = request.form.get("move_object_index")
        move_to_group_id = request.form.get("move_to_group_id")
        
        if move_object_index is not None and move_object_index != "" and move_to_group_id:
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
            active_group_id = request.form.get("active_group_id", "")
            if project.get("state") is None:
                project["state"] = {}
            project["state"]["last_edit_object_index"] = None
            project["active_group_id"] = active_group_id
            save_project(project)
            return redirect("/projeto-migracao")
        
        # Se ação é apenas carregar objeto, salvar apenas o state sem validar
        if action == "load_object":
            edit_index = request.form.get("edit_object_index")
            if edit_index:
                project["state"]["last_edit_object_index"] = int(edit_index) if edit_index else None
                save_project(project)
            return redirect("/projeto-migracao")
        
        # Caso contrário, validar e salvar normalmente
        domain_data = form_to_domain(request.form)

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
