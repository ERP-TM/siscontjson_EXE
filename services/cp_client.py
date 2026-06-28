from typing import Any

import httpx

from config import get_module_api_url
from db.db_manager import ConexionParams
from state.store import \
    store  # Importas la instancia ya inicializada y compartida

from typing import Any

# Importar la función base y la función de utilidad
from .base_client import obtener_datos_tabla_base, get_current_conexion_params

# Lista de endpoints disponibles para iterar si quieres hacer algo dinámico
TABLAS_CP = {
    "Facturas de Compra": "factura_compra",
    "Facturas de Venta": "factura_venta",
    "Cobros Anticipados": "cobros_anticipados",
    "Pagos Anticipados": "pagos_anticipados",
    "Documentos Crediticios": "doc_crediticios",
    "Tipo de Documentos Bancarios": "tipo_docbancario"
}
# Mapeando con el nombre de las tablas de sqlserver (Datos únicos)
DOCTYPE_NAME_MAP = {
    "Facturas de Compra": "Purchase Invoice",
    "Facturas de Venta": "Sales Invoice",
    "Cobros Anticipados": "Payment Entry",
    "Pagos Anticipados": "Payment Entry",
    "Documentos Crediticios": "Payment Entry",
    "Tipo de Documentos Bancarios": "Mode of Payment"
}


TABLAS_CP_CSV ={
    "Facturas de Compra CSV": "factura_compra_csv",
    "Facturas de Venta CSV": "factura_ventas_csv",
}

get_current_conexion_params = get_current_conexion_params

async def obtener_datos_tabla(nombre_tabla: str, modulo: str | None = None) -> Any:
    """
    Función de fachada para General que llama a la función base.
    """
    return await obtener_datos_tabla_base(
        nombre_tabla=nombre_tabla,
        tablas_map=TABLAS_CP,
        doctype_map=DOCTYPE_NAME_MAP,
        default_module="CP",
        modulo=modulo,
    )
