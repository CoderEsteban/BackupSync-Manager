import yaml
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

# Directorio donde están las plantillas Jinja2
TEMPLATE_DIR = Path(__file__).parent.parent / "scripts"
# Carpeta donde se escribirán los scripts generados
OUTPUT_DIR   = Path(__file__).parent.parent / "generated"

def generate_www_script(site_config_path):
    # 1) Leer la configuración YAML
    with open(site_config_path) as f:
        cfg = yaml.safe_load(f)
    # 2) Cargar la plantilla desde scripts/backup_www.sh.j2
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    tmpl = env.get_template("backup_www.sh.j2")
    # 3) Renderizar pasando todas las claves del YAML
    rendered = tmpl.render(**cfg)
    # 4) Escribir el resultado en generated/{sitio}/backup_www.sh
    site = Path(site_config_path).stem
    out_path = OUTPUT_DIR / site / "backup_www.sh"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        f.write(rendered)
    # 5) Hacerlo ejecutable
    out_path.chmod(0o750)
    return out_path

def generate_db_script(site_config_path):
    with open(site_config_path) as f:
        cfg = yaml.safe_load(f)
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    tmpl = env.get_template("backup_db.sh.j2")
    rendered = tmpl.render(**cfg)
    site = Path(site_config_path).stem
    out_dir = OUTPUT_DIR / site
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "backup_db.sh"
    with open(out_path, "w") as f:
        f.write(rendered)
    out_path.chmod(0o750)
    return out_path


