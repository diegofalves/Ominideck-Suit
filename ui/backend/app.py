from flask import Flask, render_template, request, redirect
import json
import os

from pathlib import Path

from .loaders import load_all
from .form_to_domain import form_to_domain
from .validators import validate_project, DomainValidationError
from .writers import load_project, save_project


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
