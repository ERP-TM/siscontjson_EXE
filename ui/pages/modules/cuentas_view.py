from .base_view import (
    mostrar_tabla_base,
    procesar_tabla_individual_base,
    procesar_todas_tablas_base,
    render_module_ui,
)


from services.cuentas_client import TABLAS_CUENTAS, obtener_datos_tabla

# 1. Adaptar las funciones base a General
async def mostrar_tabla(nombre_logico: str):
    async def datos_view(nombre):
            return await obtener_datos_tabla(nombre, export=False)

    await mostrar_tabla_base(nombre_logico, datos_view)

async def procesar_tabla_individual(nombre_logico: str):
    async def datos_export(nombre: str):
        return await obtener_datos_tabla(nombre, export=True)

    await procesar_tabla_individual_base(
        nombre_logico, datos_export, TABLAS_CUENTAS
    )

async def procesar_todas_tablas():
    async def datos_export(nombre: str):
        return await obtener_datos_tabla(nombre, export=True)

    await procesar_todas_tablas_base(TABLAS_CUENTAS, datos_export, "Cuentas")

# 2. Reemplazar la función 'show' con el renderizador base
def show():
    render_module_ui(
        titulo="Cuentas",
        subtitulo='Consulta y genera los JSON de las tablas del modulo "Cuentas"',
        tablas_map=TABLAS_CUENTAS,
        mostrar_func=mostrar_tabla,
        exportar_individual_func=procesar_tabla_individual,
        exportar_todas_func=procesar_todas_tablas,
    )
