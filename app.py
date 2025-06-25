# app.py

from pathlib import Path
import os
import yaml
from flask import Flask, render_template, request, redirect, url_for

# ————— Carga y expande sites_root —————
with open("config/global_config.yaml") as f:
    GLOBAL_CFG = yaml.safe_load(f)

raw = GLOBAL_CFG.get("sites_root", "")
SITES_ROOT = Path(os.path.expanduser(os.path.expandvars(raw)))
SITES_ROOT.mkdir(parents=True, exist_ok=True)
# ————————————————————————————————

app = Flask(__name__)

@app.route("/")
def index():
    sites_cfg_dir = Path("config/sites")
    sitios = [f.stem for f in sites_cfg_dir.glob("*.yaml")] if sites_cfg_dir.exists() else []
    return render_template("index.html", sitios=sitios)

@app.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    if request.method == "POST":
        # 1) Leer formulario
        dominio     = request.form.get("dominio")
        backup_path = request.form.get("backup_path") or None
        ssh_host    = request.form.get("ssh_host")
        ssh_user    = request.form.get("ssh_user")
        ssh_key     = request.form.get("ssh_key", "")
        remote_www  = request.form.get("remote_www_path")

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
            "dominio":         dominio,
            "root_path":       str(site_dir),
            "ssh_host":        ssh_host,
            "ssh_user":        ssh_user,
            "ssh_key":         ssh_key,
            "remote_www_path": remote_www,
            "db_ssh_host":       request.form["db_ssh_host"],
            "db_ssh_user":       request.form["db_ssh_user"],
            "db_ssh_key":        request.form.get("db_ssh_key", ""),
            "db_name":           request.form["db_name"],
            "db_user":           request.form["db_user"],
            "db_pass":           request.form.get("db_pass", ""),
        }
        yaml_path = Path("config/sites") / f"{dominio}.yaml"
        yaml_path.parent.mkdir(parents=True, exist_ok=True)
        with open(yaml_path, "w") as yf:
            yaml.safe_dump(cfg, yf)

        # 5) Generar el script de backup web
        from managers.generator import generate_www_script
        script_path = generate_www_script(str(yaml_path))
        print(f"Script generado en: {script_path}")

        # 6) Redirigir al listado
        return redirect(url_for("index"))

    # GET → mostrar formulario
    return render_template("nuevo.html")

if __name__ == "__main__":
    app.run(debug=True)
