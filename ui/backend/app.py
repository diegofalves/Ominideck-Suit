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
        domain_data = form_to_domain(request.form)

        try:
            validate_project(domain_data)
        except DomainValidationError as e:
            return render_template(
                "projeto_migracao.html",
                schema=data["schema"],
                enums=data["enums"],
                ui=data["ui"],
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
