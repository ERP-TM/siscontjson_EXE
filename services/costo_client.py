from typing import Any
from .base_client import obtener_datos_tabla_base, get_current_conexion_params

import httpx

from config import get_module_api_url
from db.db_manager import ConexionParams
from state.store import \
    store  # Importas la instancia ya inicializada y compartida

# Lista de endpoints disponibles para iterar si quieres hacer algo dinámico
TABLAS_COSTO = {
    "Centros de Costo": "centro_costo",
}

# Mapeando con el nombre de las tablas de sqlserver (Datos únicos)
DOCTYPE_NAME_MAP = {
    "Centros de Costo": "Cost Center",
}

get_current_conexion_params = get_current_conexion_params

## Este helper consulta una tabla segun el endpoint para obtener sus datos
# haciendo uso del diccionario que tiene la relacion de las tablas
async def obtener_datos_tabla(nombre_tabla: str,
                              modulo: str | None = None) -> Any:
    return await obtener_datos_tabla_base(
        nombre_tabla=nombre_tabla,
        tablas_map=TABLAS_COSTO,
        doctype_map=DOCTYPE_NAME_MAP,
        default_module="costo",
        modulo=modulo,
    )
