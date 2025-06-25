# app.py

import os
from pathlib import Path
import yaml
from flask import Flask, render_template, request, redirect, url_for

# ————— Ya deberías tener aquí tu bloque de carga de config global —————
with open("config/global_config.yaml") as f:
    GLOBAL_CFG = yaml.safe_load(f)

raw = GLOBAL_CFG.get("sites_root", "")    # por ejemplo "~/"
SITES_ROOT = Path(os.path.expanduser(os.path.expandvars(raw)))
SITES_ROOT.mkdir(parents=True, exist_ok=True)
# ————————————————————————————————————————————————————————————————

app = Flask(__name__)


@app.route("/")
def index():
    # Directorio donde guardas los YAML de cada sitio
    sites_cfg_dir = Path("config/sites")
    sitios = []
    if sites_cfg_dir.exists():
        # Cada fichero .yaml → nombre del sitio
        sitios = [f.stem for f in sites_cfg_dir.glob("*.yaml")]
    return render_template("index.html", sitios=sitios)



# ——————— Vista para crear un sitio nuevo actualizada ———————
@app.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    if request.method == "POST":
        # 1) Leer formulario
        dominio     = request.form.get("dominio")
        backup_path = request.form.get("backup_path") or None

        # 2) Calcular carpeta destino
        if backup_path:
            site_dir = Path(os.path.expanduser(os.path.expandvars(backup_path)))
        else:
            site_dir = SITES_ROOT / dominio

        # 3) Crear estructura de carpetas
        (site_dir / "backup_db").mkdir(parents=True, exist_ok=True)
        (site_dir / "backup_www").mkdir(parents=True, exist_ok=True)

        # 4) Guardar la configuración en YAML
        cfg = {
            "dominio":   dominio,
            "root_path": str(site_dir),
            # más campos (SSH, credenciales…) luego aquí
        }
        yaml_path = Path("config/sites") / f"{dominio}.yaml"
        yaml_path.parent.mkdir(parents=True, exist_ok=True)
        with open(yaml_path, "w") as yf:
            yaml.safe_dump(cfg, yf)

        # 5) Redirigir al listado
        return redirect(url_for("index"))

    # GET → mostrar formulario
    return render_template("nuevo.html")
# ————————————————————————————————————————————————————————————————

if __name__ == "__main__":
    app.run(debug=True)



