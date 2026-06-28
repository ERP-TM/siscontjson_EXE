from typing import Any

# Importar la función base y la función de utilidad
from .base_client import obtener_datos_tabla_base, get_current_conexion_params

# Lista de endpoints disponibles para iterar si quieres hacer algo dinámico
TABLAS_PRODUCTOS = {
    "Grupo Productos": "grupo_de_productos",
    "Productos y Servicios": "productos",
    "Existencias": "existencias",
    "Lista de precios": "lista_de_precios",
    "Lista de precios por productos y servicios": "precios_productos_lista"
}

# Mapeando con el nombre de las tablas de sqlserver (Datos únicos)
DOCTYPE_NAME_MAP = {
    "Grupo Productos": "Item Group",
    "Productos y Servicios": "Item",
    "Existencias": "Stock Reconciliation",
    "Lista de precios": "Price List",
    "Lista de precios por productos y servicios": "Item Price"
}

TABLAS_PRODUCTOS_CSV ={
    "Existencias CSV": "existencias_csv"
}


# Reemplazar la definición por la importación directa de la base
get_current_conexion_params = get_current_conexion_params


async def obtener_datos_tabla(nombre_tabla: str, modulo: str | None = None, export=False) -> Any:
    """
    Función de fachada para General que llama a la función base.
    """
    return await obtener_datos_tabla_base(
        nombre_tabla=nombre_tabla,
        tablas_map=TABLAS_PRODUCTOS,
        doctype_map=DOCTYPE_NAME_MAP,
        default_module="producto",
        modulo=modulo,
        export=export,
    )
