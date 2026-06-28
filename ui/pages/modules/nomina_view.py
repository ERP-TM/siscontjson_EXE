# ui/pages/modules/nomina_view.py
import asyncio
from nicegui import ui

# Importar el módulo base
from .base_view import (
    mostrar_tabla_base,
    procesar_tabla_individual_base,
    procesar_todas_tablas_base,
    render_module_ui,
)
from utils.constants import MESES

# Importar solo lo necesario del cliente específico
from services.nomina_client import TABLAS_NOMINA, obtener_datos_tabla

NOMBRE_SUBMAYOR = "Submayor Vacaciones"


# 1. Adaptar las funciones base a Nómina
# La función 'mostrar_tabla' llama a la base con la función específica de Nómina.
async def mostrar_tabla(nombre_logico: str, mes=None, anno=None):
    async def datos_view(nombre):
        return await obtener_datos_tabla(nombre, export=False, grouped=False, mes=mes, anno=anno)

    await mostrar_tabla_base(nombre_logico, datos_view)



async def procesar_tabla_individual(nombre_logico: str, mes=None, anno=None):
    async def datos_export(nombre: str):
        return await obtener_datos_tabla(nombre, export=True)

    await procesar_tabla_individual_base(nombre_logico, datos_export, TABLAS_NOMINA)


# Envolver la función base de 'procesar_todas_tablas'
async def procesar_todas_tablas():
    # Pasa obtener_datos_tabla directamente para que la función base maneje la exportación
    async def datos_export(nombre: str):
        return await obtener_datos_tabla(nombre, export=True)

    await procesar_todas_tablas_base(TABLAS_NOMINA, datos_export, "Nomina")


# 2. Reemplazar la función 'show' con el renderizador base
def _render_submayor_vacaciones():
    """Fila especial con selectores de mes/año que habilitan los botones."""

    estado = {"mes": None, "anno": None}

    with ui.row().classes(
        "items-center justify-between w-full px-3 py-2 rounded "
        "transition-all duration-200 hover:bg-blue-200"
    ):
        ui.label(NOMBRE_SUBMAYOR).classes("text-md font-semibold")

        with ui.row().classes("items-center gap-3"):

            ui.select(
                options=MESES,
                label="Mes",
                on_change=lambda e: _on_change(estado, "mes", e.value, botones),
            ).classes("w-32")

            ui.number(
                label="Año",
                min=2000,
                max=2100,
                precision=0,
                on_change=lambda e: _on_change(
                    estado, "anno", int(e.value) if e.value else None, botones
                ),
            ).classes("w-24")

            botones = ui.row().classes("gap-2")
            botones.set_visibility(False)

            with botones:
                ui.button(
                    "Visualizar datos",
                    on_click=lambda: mostrar_tabla(
                        NOMBRE_SUBMAYOR, mes=estado["mes"], anno=estado["anno"]
                    ),
                ).props("color=primary outline size=sm")

                ui.button(
                    "Exportar a JSON",
                    on_click=lambda: procesar_tabla_individual(
                        NOMBRE_SUBMAYOR, mes=estado["mes"], anno=estado["anno"]
                    ),
                ).props("color=green outline size=sm icon=cloud_download")


def _on_change(estado, clave, valor, botones):
    estado[clave] = valor
    botones.set_visibility(
        estado["mes"] is not None and estado["anno"] is not None
    )


def show():
    # Excluir Submayor Vacaciones del render genérico
    tablas_sin_submayor = {k: v for k, v in TABLAS_NOMINA.items()
                           if k != NOMBRE_SUBMAYOR}

    render_module_ui(
        titulo="Nómina",
        subtitulo="Consulta y genera los JSON de las tablas de Nomina",
        tablas_map=tablas_sin_submayor,
        mostrar_func=mostrar_tabla,
        exportar_individual_func=procesar_tabla_individual,
        exportar_todas_func=procesar_todas_tablas,
    )

    _render_submayor_vacaciones()
