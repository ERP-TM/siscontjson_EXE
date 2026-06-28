import asyncio
import csv
import io
# Manipular texto y asegura que el JSON mantenga un orden specífico de claves
from collections import OrderedDict
import json
from nicegui import ui
from services.cp_client import TABLAS_CP, TABLAS_CP_CSV,obtener_datos_tabla, get_current_conexion_params
from utils.download_manager import save_to_download_cache
# Importar el módulo base
from .base_view import (
    mostrar_tabla_base,
    procesar_tabla_individual_base,
    procesar_todas_tablas_base,
    descargar_csv_js,
    render_module_ui,
)

from api.api_cp import get_factura_compra_csv
from db.db_manager import ConexionParams 
from state.store import \
    store  # Importas la instancia ya inicializada y compartida

# Funcion Helper para generar el string JSON
# definida aqui para que  "obtener_datos_tabla" devuelve los datos puros (list[dict])
def _generate_json_string(data_list: list, doctype: str) -> str:
    """
    Genera el contenido JSON como un string con la estructura de exportacion
    """
    content = OrderedDict()
    content["doctype"] = doctype
    content["data"] = data_list
    return json.dumps(content, indent=4, ensure_ascii=False)

# Muestra ventana modal con los datos de la tabla especificada
async def mostrar_tabla(nombre_logico: str):
    await mostrar_tabla_base(nombre_logico, obtener_datos_tabla)

# funcion que obtiene los datos de la tabla especificada
async def procesar_tabla_individual(nombre_logico: str):
    await procesar_tabla_individual_base(
        nombre_logico, obtener_datos_tabla, TABLAS_CP)

async def procesar_todas_tablas():
    await procesar_todas_tablas_base(TABLAS_CP, procesar_tabla_individual)
#
# async def descargar_csv(nombre_logico: str):
#     await descargar_csv_base(nombre_logico, obtener_datos_tabla, TABLAS_CP)


async def descargar_csv_js_custom(nombre_logico: str):
    await descargar_csv_js(nombre_logico, "cp", TABLAS_CP_CSV)


def show():
    render_module_ui(
        titulo="Cobros y Pagos",
        subtitulo='Consulta y genera los JSON y CSV de las tablas del módulo "Cobros y Pagos"',
        tablas_map=TABLAS_CP,
        tablas_map_csv=TABLAS_CP_CSV,
        mostrar_func=mostrar_tabla,
        exportar_individual_func=procesar_tabla_individual,
        exportar_todas_func=procesar_todas_tablas,
        descargar_csv_func=descargar_csv_js_custom,
    )

