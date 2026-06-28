from typing import Any

import httpx

from config import get_module_api_url
from db.db_manager import ConexionParams
from state.store import \
    store  # Importas la instancia ya inicializada y compartida

# Importar la función base y la función de utilidad
from .base_client import get_current_conexion_params


# Lista de endpoints disponibles para iterar si quieres hacer algo dinámico
TABLAS_CUENTAS = {
    "Cuentas": "cuentas",
    # "Relaciones": "relaciones-trabajadores",
    "Elementos de gastos": "elementos_gastos",
    "Asientos Contables": "asientos_contables",
}


## Este helper consulta una tabla segun el endpoint para obtener sus datos
# haciendo uso del diccionario que tiene la relacion de las tablas
async def obtener_datos_tabla(nombre_tabla: str,
                              modulo: str | None = None, export=False) -> Any:
    modulo = modulo or store.selected_module or 'cuentas'
    endpoint = TABLAS_CUENTAS[nombre_tabla]
    base_url = get_module_api_url(modulo)
    url = f"{base_url}/{endpoint}"
   
    conexion_params = get_current_conexion_params()
    payload = conexion_params.model_dump()

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, params={"export": export},)
        response.raise_for_status()
        return response.json()