# debug_startup.py
# Diagnóstico de entorno para ejecutables PyInstaller
# Genera startup_debug.log en la carpeta del .exe
# NOTA: Quitar la llamada a log_entorno() en main.py una vez resuelto el problema

import os
import sys
import logging
from pathlib import Path


def log_entorno():
    # ── Determinar carpeta del ejecutable o del script ──────────────
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
    else:
        exe_dir = Path(__file__).resolve().parent

    log_path = exe_dir / "startup_debug.log"

    # ── Configurar logging a consola y archivo ───────────────────────
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(str(log_path), encoding="utf-8", mode="w"),
        ],
    )

    log = logging.getLogger("startup")

    log.info("=" * 60)
    log.info("DIAGNÓSTICO DE ENTORNO — exportJson")
    log.info("=" * 60)

    # ── Modo de ejecución ────────────────────────────────────────────
    log.info(f"Modo frozen (exe)  : {getattr(sys, 'frozen', False)}")
    log.info(f"sys.executable     : {sys.executable}")
    log.info(
        f"sys._MEIPASS       : {getattr(sys, '_MEIPASS', 'N/A (modo desarrollo)')}"
    )
    log.info(f"Python version     : {sys.version}")

    # ── Directorios ──────────────────────────────────────────────────
    cwd = Path.cwd()
    log.info(f"CWD actual         : {cwd}")
    log.info(f"EXE DIR            : {exe_dir}")
    log.info(f"Log generado en    : {log_path}")

    # ── Permisos de escritura ────────────────────────────────────────
    log.info("── Verificando permisos de escritura ──")
    for ruta in [cwd, exe_dir]:
        test_file = ruta / ".write_test_tmp"
        try:
            test_file.write_text("test")
            test_file.unlink()
            log.info(f"  ✔ Escritura OK    : {ruta}")
        except Exception as e:
            log.error(f"  ✘ SIN PERMISOS    : {ruta}  →  {e}")

    # ── Archivos de configuración ────────────────────────────────────
    log.info("── Buscando archivos .env ──")
    for nombre in [".env", ".env.local", ".env.production"]:
        for ruta in [cwd, exe_dir]:
            p = ruta / nombre
            log.info(
                f"  {nombre} en {ruta}: {'✔ EXISTE' if p.exists() else '✘ NO EXISTE'}"
            )

    # ── Variables de entorno relevantes ─────────────────────────────
    log.info("── Variables de entorno ──")
    vars_check = [
        "NO_PROXY",
        "no_proxy",
        "ENV_FILE",
        "JSON_OUTPUT_DIR",
        "API_BASE_URL",
        "PORT",
        "DB_DRIVER",
        "STORAGE_SECRET",
    ]
    for var in vars_check:
        val = os.environ.get(var)
        log.info(f"  {var:<20}: {val if val else '(no definida)'}")

    # ── Carpeta .nicegui ─────────────────────────────────────────────
    log.info("── Verificando carpeta .nicegui ──")
    nicegui_dir = exe_dir / ".nicegui"
    log.info(f"  .nicegui existe   : {nicegui_dir.exists()}")
    if not nicegui_dir.exists():
        try:
            nicegui_dir.mkdir(parents=True, exist_ok=True)
            log.info(f"  .nicegui creada   : {nicegui_dir}")
        except Exception as e:
            log.error(f"  No se pudo crear .nicegui: {e}")
    else:
        # Listar contenido si ya existe
        contenido = list(nicegui_dir.iterdir())
        log.info(f"  .nicegui contenido: {[f.name for f in contenido]}")

    # ── Espacio en disco ─────────────────────────────────────────────
    try:
        import shutil

        total, usado, libre = shutil.disk_usage(exe_dir)
        log.info(f"  Espacio libre     : {libre // (1024**2)} MB")
    except Exception as e:
        log.warning(f"  No se pudo verificar espacio en disco: {e}")

    # ── Plataforma ───────────────────────────────────────────────────
    log.info(f"  OS / Plataforma   : {sys.platform} — {os.name}")

    log.info("=" * 60)
    log.info(f"Log completo guardado en: {log_path}")
    log.info("=" * 60)
