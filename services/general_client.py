# services/general_client.py
from typing import Any

# Importar la función base y la función de utilidad
from .base_client import obtener_datos_tabla_base, get_current_conexion_params

# Lista de endpoints disponibles (Datos únicos)
TABLAS_GENERAL = {
    "Unidad Medida": "unidad_medida",
    "Clientes": "clientes",
    "Proveedores": "proveedores",
    "Contactos": "contactos",
    "Bancos": "bancos",
    "Tipos Bancos": "tipos_bancos",
    "Cuentas Bancarias": "cuentas_bancarias",
    "Direcciones": "direcciones",
}

# Mapeando con el nombre de las tablas de sqlserver (Datos únicos)
DOCTYPE_NAME_MAP = {
    "Unidad Medida": "UOM",
    "Clientes": "Customer",
    "Proveedores": "Supplier",
    "Contactos": "Contact",
    "Bancos": "Bank",
    "Tipos Bancos": "Bank Type",
    "Cuentas Bancarias": "Bank Account",
    "Direcciones": "Address",
}


# **********************************************
# * Aquí se mantiene get_current_conexion_params *
# * si se desea que las funciones de base_client *
# * no sean visibles desde fuera del paquete.     *
# * Si no, se puede importar directamente         *
# * desde base_client si base_client es un módulo*
# * aparte. Lo mantendremos aquí por ahora.      *
# **********************************************
# Reemplazar la definición por la importación directa de la base
get_current_conexion_params = get_current_conexion_params


async def obtener_datos_tabla(
    nombre_tabla: str,
    modulo: str | None = None,
    export: bool = False,
    grouped: bool = False,
) -> Any:
    """
    Función de fachada para General que llama a la función base.
    """
    return await obtener_datos_tabla_base(
        nombre_tabla=nombre_tabla,
        tablas_map=TABLAS_GENERAL,
        doctype_map=DOCTYPE_NAME_MAP,
        default_module="general",
        modulo=modulo,
        export=export,
        grouped=grouped,
    )
