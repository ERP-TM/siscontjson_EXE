import asyncio


# Manipular texto y asegura que el JSON mantenga un orden específico de claves
from collections import OrderedDict
import json

from nicegui import ui

from services.costo_client import TABLAS_COSTO, obtener_datos_tabla
from utils.download_manager import save_to_download_cache
from .base_view import (
    mostrar_tabla_base,
    procesar_tabla_individual_base,
    procesar_todas_tablas_base,
    render_module_ui,
)

# Funcion Helper para generar el string JSON
# definida aqui para que  "obtener_datos_tabla" devuelve los datos puros (list[dict])
def _generate_json_string(data_list: list, doctype: str) -> str:
    """
    Genera el contenido JSON como un string con la estructura de exportacion
    """
    content = OrderedDict()
    content["doctype"] = doctype
    content["data"] = data_list
    return json.dumps(content, indent=4, ensure_ascii=False)    #FIN DEL NUEVO


# Muestra ventana modal con los datos de la tabla especificada
async def mostrar_tabla(nombre_logico: str):
    await mostrar_tabla_base(nombre_logico, obtener_datos_tabla)

# funcion que obtiene los datos de la tabla especificada
async def procesar_tabla_individual(nombre_logico: str):
    await procesar_tabla_individual_base(
        nombre_logico, obtener_datos_tabla, TABLAS_COSTO)

async def procesar_todas_tablas():
    await procesar_todas_tablas_base(TABLAS_COSTO, procesar_tabla_individual)

def show():
    render_module_ui(
        titulo="Cobros y Pagos",
        subtitulo='Consulta y genera los JSON y CSV de las tablas del módulo de "Costo"',
        tablas_map=TABLAS_COSTO,
        mostrar_func=mostrar_tabla,
        exportar_individual_func=procesar_tabla_individual,
        exportar_todas_func=procesar_todas_tablas,
    )

'''    ui.label("Costo").classes("text-2xl font-bold mb-1")
    ui.label("Consulta y genera los JSON de las tablas del modulo "
             "Costo").classes(
        "text-sm mb-4")
    ui.separator()

    # Botón para exportar todas las tablas de NOMINA
    ui.button(
        "Exportar todas las tablas a JSON",
        on_click=lambda: procesar_todas_tablas()
        # ¡Aquí pasas TABLAS_COSTO!
    ).props("color=blue size=md icon=cloud_download").classes("mt-4 mb-6")

    # Display table names and buttons
    with ui.column().classes("mt-6 gap-2 w-full"):  # Use w-full for full width
        for nombre_logico in TABLAS_COSTO.keys():
            with ui.row().classes(
                    "items-center justify-between w-full"):  # Row for table
                # name and buttons
                ui.label(nombre_logico).classes(
                    "text-md font-semibold")  # Display the table name

                with ui.row():  # Group the buttons together
                    ui.button(
                        "Visualizar datos",
                        on_click=lambda n=nombre_logico: mostrar_tabla(n)
                    ).props(
                        "color=primary outline size=sm")  # Added size for
                    # smaller buttons

                    ui.button(
                        "Exportar a JSON",
                        on_click=lambda
                            n=nombre_logico: procesar_tabla_individual(n)
                    ).props(
                        "color=green outline size=sm icon=cloud_download")
'''