# main.py
import sys
import os
from pathlib import Path

# ── Forzar CWD al directorio del ejecutable ───────────────
if getattr(sys, "frozen", False):
    os.chdir(Path(sys.executable).parent)

# ── Diagnóstico ───────────────────────────────────────────
from debug_startup import log_entorno

log_entorno()
# ─────────────────────────────────────────────────────────


import uvicorn
from fastapi import FastAPI
from nicegui import app, ui

import config

from api import (
    api_db,
    api_nomina,
    api_general,
    api_almacen,
    api_productos,
    api_costo,
    api_cp,
    api_activos_fijos,
    api_cuentas,
)

# from middleware.auth_middleware import AuthMiddleware
from ui.pages import login, main_page

# from db.db_manager import AppState
# store = AppState()

# from state.store import store

# Configuración FastAPI
fastapi_app = FastAPI(title=config.APP_TITLE)

# Montar APIs antes de la integracion de NiceGUI con FastAPI
# porque sino no reconoce swagguer para los endpoints
# y muestra html en lugar de formatos JSON
fastapi_app.include_router(api_db.router, prefix="/api")
fastapi_app.include_router(api_nomina.router, prefix="/api/nomina")
fastapi_app.include_router(api_general.router, prefix="/api/general")
fastapi_app.include_router(api_almacen.router, prefix="/api/almacen")
fastapi_app.include_router(api_productos.router, prefix="/api/producto")
fastapi_app.include_router(api_costo.router, prefix="/api/costo")
fastapi_app.include_router(api_cp.router, prefix="/api/cp")
fastapi_app.include_router(api_cuentas.router, prefix="/api/cuentas")
fastapi_app.include_router(api_activos_fijos.router, prefix="/api/activos_fijos")


# ⛔ Agregar middleware de autenticación
# fastapi_app.add_middleware(AuthMiddleware)

# Integración NiceGUI con FastAPI pero no se inicia el servidor
ui.run_with(
    fastapi_app,
    storage_secret=config.STORAGE_SECRET,
    title=config.APP_TITLE,
    dark=False,
    language="es",
    mount_path="/",
)


# Configurar rutas UI
@ui.page("/")
async def index(client):
    # Asegurar que usamos el contexto del cliente explícitamente
    with client:
        if not app.storage.user.get("connected"):
            login.connection_form()
        else:
            main_page.show()


# Iniciar con: uvicorn main:fastapi_app --reload
# Punto de entrada que inicial el proyecto combinando FastAPI con NiceGui
# if __name__ == "__main__":
#     settings = config.get_settings()
#     uvicorn.run(fastapi_app, host="0.0.0.0", port=settings.PORT, reload=False)

# Modificando para que levante el browser automaticamente

if __name__ == "__main__":
    # 1. Primero cargamos las configuraciones para saber qué puerto usar
    settings = config.get_settings()
    puerto = settings.PORT

    # 2. Creamos la función que abrirá el navegador con el puerto dinámico
    def abrir_navegador():
        import time
        import webbrowser

        time.sleep(1.5)  # Espera a que Uvicorn levante
        webbrowser.open(f"http://localhost:{puerto}")

    # 3. Lanzamos el hilo en segundo plano
    import threading

    threading.Thread(target=abrir_navegador, daemon=True).start()

    # 4. Tu Uvicorn de siempre, iniciando el servidor FastAPI
    uvicorn.run(fastapi_app, host="0.0.0.0", port=puerto, reload=False)