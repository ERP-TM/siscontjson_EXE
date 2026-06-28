from typing import Any

# Importar la función base y la función de utilidad
from .base_client import obtener_datos_tabla_base, get_current_conexion_params

# Lista de endpoints disponibles para iterar si quieres hacer algo dinámico
TABLAS_ALMACEN = {
    "Almacen": "almacen",
}

# Mapeando con el nombre de las tablas de sqlserver (Datos únicos)
DOCTYPE_NAME_MAP = {
    "Almacen": "Warehouse",
}

get_current_conexion_params = get_current_conexion_params

async def obtener_datos_tabla(nombre_tabla: str, modulo: str | None = None,export=False) -> Any:
    """
    Función de fachada para Almacén que llama a la función base.
    """
    return await obtener_datos_tabla_base(
        nombre_tabla=nombre_tabla,
        tablas_map=TABLAS_ALMACEN,
        doctype_map=DOCTYPE_NAME_MAP,
        default_module="almacen",
        modulo=modulo,
        export=export,
    )