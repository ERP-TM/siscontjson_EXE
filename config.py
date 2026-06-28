# config.py
# Utilizando pydantic_settings.BaseSettings para cargar .env una sola vez
import os
import sys  # <--- ¡IMPORTANTE!
from functools import lru_cache
from pathlib import Path  # Adicionado para probar el ejecutable nicegui-pack

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# cargando el archivo .env
# load_dotenv()

# =====================================================================
# DETECTOR DE ENTORNO SEGURO PARA DESARROLLO Y PYINSTALLER
# =====================================================================
if getattr(sys, "frozen", False):
    # Si es el ejecutable empaquetado, la raíz es la carpeta del .exe/.binario (dist/)
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    # Si es desarrollo local (python main.py), la raíz es donde está este config.py
    BASE_DIR = Path(__file__).resolve().parent

# Construimos la ruta absoluta al archivo .env
RUTA_ENV = BASE_DIR / ".env"

# Cargamos el archivo .env usando la ruta absoluta calculada
if RUTA_ENV.exists():
    load_dotenv(dotenv_path=RUTA_ENV)
else:
    load_dotenv()  # Fallback por si acaso
# =====================================================================

# App Config
APP_TITLE = "Exportar Siscont"
STORAGE_SECRET = os.getenv("STORAGE_SECRET", "siscont-json")

PAGINATION_THRESHOLD = (
    5000  # Número de registros a partir del cual se activa la paginación
)
DEFAULT_PAGE_SIZE = 1000

# UI Modules Config(modulo:icon)
# Para sub-módulos, usar: "Modulo Padre": {"icon": "icon_name", "children": {"Sub-módulo": "icon"}}
MODULES = {
    "Inicio": "home",
    "General": "dashboard",
    "Cuentas": "account_balance_wallet",
    "Activos Fijos": "precision_manufacturing",
    "Cobros y Pagos": "receipt_long",
    # "Contabilidad General": "account_balance_wallet",
    "Costo": "payments",
    "Ventas": "sell",
    "Compras": "shopping_cart",
    "Inventarios": {
        "icon": "inventory_2",
        "children": {
            "Almacen": "warehouse",
            "Productos": "category",
        },
    },
    "Nómina": "payments",
    # "Recursos Humanos": "people_alt",
}

DEFAULT_MODULE = "Inicio"


class Settings(BaseSettings):
    # ENVIRONMENT: str  # <--- Agrega esta línea para que acepte "local" o "docker"
    # Al ponerle = "local", si la variable no aparece en el .env,
    # Pydantic asumirá automáticamente que estás en local y NO se romperá.
    ENVIRONMENT: str = "local"
    API_BASE_URL: str
    SQL_USER: str
    SQL_PORT: int
    PORT: int
    STORAGE_SECRET: str
    JSON_OUTPUT_DIR: str
    # Nueva variable para manejar el driver dinámicamente
    DB_DRIVER: str = "ODBC Driver 17 for SQL Server"

    class Config:
        # env_file = ".env"
        # Pydantic leerá la variable de entorno ENV_FILE,
        # si no existe, usará ".env.local" por defecto.
        env_file = os.getenv("ENV_FILE", ".env.local")
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()


# Funcion para crear el directorio de los archivos JSON
def get_output_dir():
    # Intenta obtener desde la variable de entorno
    json_dir = os.getenv("JSON_OUTPUT_DIR")

    if json_dir:
        return json_dir

    # Si no está definida, se usa la ruta por defecto relativa al archivo actual
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    default_dir = os.path.join(base_dir, "archivos_json")
    os.makedirs(default_dir, exist_ok=True)
    return default_dir


# funcion utilitaria para obtener la url segun el modulo
def get_module_api_url(module_name: str) -> str:
    settings = get_settings()
    base = settings.API_BASE_URL.rstrip("/")  # viene del .env como API_BASE
    return f"{base}/{module_name.lower()}"