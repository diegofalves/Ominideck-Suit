from flask import Flask, render_template, request, redirect
import json
import os

from pathlib import Path

from .loaders import load_all


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
    if request.method == "POST":
        payload = request.form.to_dict()
        save_project(payload)
        return redirect("/projeto-migracao")

    data = load_all()
    projeto_existente = load_existing_project()

    return render_template(
        "projeto_migracao.html",
        schema=data["schema"],
        enums=data["enums"],
        ui=data["ui"],
        projeto=projeto_existente
    )


# -------------------------------------------------
# Persistência
# -------------------------------------------------
def save_project(payload):
    path = Path("domain/projeto_migracao/projeto_migracao.json")

    data = {
        "identificacao": payload,
        "grupos": []
    }

    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


import json
import os

def load_existing_project():
    path = "domain/projeto_migracao/projeto_migracao.json"

    if not os.path.exists(path):
        return None

    if os.path.getsize(path) == 0:
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return None



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
